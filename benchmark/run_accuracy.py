"""
SQL accuracy benchmark for the Analytics Copilot.

Run from the PROJECT ROOT (the folder that contains app.py):
    python benchmark/run_accuracy.py                  # full run
    python benchmark/run_accuracy.py --limit 5        # quick dry run
    python benchmark/run_accuracy.py --rerun-errors   # redo only API-error cases + case 28, keep the rest
Needs GEMINI_API_KEY in your .env (same as the app).
Writes benchmark/results_accuracy.json

Rate limits: API errors (429 quota) are retried with a wait and are reported as
"api_error", NOT as wrong answers. Only completed questions count toward accuracy.
"""
import argparse, json, os, sqlite3, statistics, sys, time
from collections import defaultdict

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.getcwd())
load_dotenv()

from core.database import DatabaseManager
from core.gemini_agent import GeminiAnalyticsAgent

DB_PATH = "data/product_metrics.db"
CASES_PATH = "benchmark/test_cases.json"
RESULTS_PATH = "benchmark/results_accuracy.json"


def norm(v):
    """Normalise a cell so 12, 12.0 and 12.004 compare equal."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "NULL"
    try:
        return f"{float(v):.2f}"
    except (TypeError, ValueError):
        return str(v).strip()


def results_match(got: pd.DataFrame, gold: pd.DataFrame) -> bool:
    """
    Order-insensitive, column-name-insensitive comparison.
    Every gold column must be found among the model's columns; extra columns are allowed.
    """
    if len(got) != len(gold):
        return False
    gold_cols = [[norm(v) for v in gold.iloc[:, i]] for i in range(gold.shape[1])]
    got_cols = [[norm(v) for v in got.iloc[:, j]] for j in range(got.shape[1])]
    used, mapping = set(), []
    for gc in gold_cols:
        found = None
        for j, cc in enumerate(got_cols):
            if j not in used and sorted(cc) == sorted(gc):
                found = j
                break
        if found is None:
            return False
        used.add(found)
        mapping.append(found)
    gold_rows = sorted(zip(*gold_cols))
    got_rows = sorted(tuple(got_cols[j][r] for j in mapping) for r in range(len(got)))
    return gold_rows == got_rows


def is_quota_error(e: Exception) -> bool:
    t = str(e)
    return "429" in t or "RESOURCE_EXHAUSTED" in t


def is_daily_quota(e: Exception) -> bool:
    t = str(e)
    return "PerDay" in t or "per day" in t.lower()


def run_case(agent, schema, db, case, max_api_tries=4):
    """Runs one question. Retries only on rate-limit errors; other errors are real results."""
    for api_try in range(1, max_api_tries + 1):
        t0 = time.perf_counter()
        try:
            df, sql, logs = agent.execute_with_self_healing(
                user_question=case["question"], schema=schema,
                db_path=db.db_path, max_retries=3)
            elapsed = time.perf_counter() - t0
            with sqlite3.connect(f"file:{db.db_path}?mode=ro", uri=True) as c:
                gold = pd.read_sql_query(case["gold_sql"], c)
            status = "correct" if results_match(df, gold) else "wrong_result"
            return {**case, "status": status, "attempts": len(logs),
                    "latency_s": round(elapsed, 2), "generated_sql": sql, "error": None}
        except Exception as e:
            elapsed = time.perf_counter() - t0
            if is_quota_error(e):
                if is_daily_quota(e):
                    return {**case, "status": "api_error", "attempts": None,
                            "latency_s": None, "generated_sql": None,
                            "error": "DAILY QUOTA EXHAUSTED: " + str(e)[:150]}
                wait = 20 * api_try
                print(f"    rate limited, waiting {wait}s (try {api_try}/{max_api_tries})")
                time.sleep(wait)
                continue
            # real failure of the copilot itself (e.g. 3 failed SQL repairs)
            return {**case, "status": "error", "attempts": None,
                    "latency_s": round(elapsed, 2), "generated_sql": None,
                    "error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {**case, "status": "api_error", "attempts": None, "latency_s": None,
            "generated_sql": None, "error": "rate limit persisted after retries"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=5.0, help="seconds between questions")
    ap.add_argument("--rerun-errors", action="store_true",
                    help="re-run only api_error/error cases (and any case whose question changed)")
    args = ap.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY missing. Put it in .env")

    db = DatabaseManager(db_path=DB_PATH)
    schema = db.get_schema()
    agent = GeminiAnalyticsAgent(api_key=api_key)
    print("Model:", agent.model)

    cases = json.load(open(CASES_PATH))
    if args.limit:
        cases = cases[: args.limit]

    previous = {}
    if args.rerun_errors and os.path.exists(RESULTS_PATH):
        for r in json.load(open(RESULTS_PATH)):
            previous[r["id"]] = r

    rows = []
    for i, case in enumerate(cases, 1):
        old = previous.get(case["id"])
        # keep finished results (correct / real copilot failures) whose question is unchanged;
        # re-run api_error and wrong_result cases (the latter picks up fixed test cases)
        # (old result files from the first version stored 429 quota errors as "error", so check the text)
        quota_in_old = bool(old and ("429" in (old.get("error") or "")
                                     or "RESOURCE_EXHAUSTED" in (old.get("error") or "")))
        keep = bool(old and old["status"] in ("correct", "error") and not quota_in_old
                    and old["question"] == case["question"])
        if keep:
            rows.append(old)
            print(f"[{i}/{len(cases)}] kept previous result ({old['status']})")
            continue
        row = run_case(agent, schema, db, case)
        rows.append(row)
        print(f"[{i}/{len(cases)}] {row['status']:<12} attempts={row['attempts']} "
              f"{row['latency_s']}s  {case['question'][:60]}")
        if row["status"] == "api_error" and "DAILY" in (row["error"] or ""):
            print("\nDaily quota exhausted. Stop here, re-run with --rerun-errors tomorrow "
                  "or switch GEMINI_MODEL / enable billing.")
            rows.extend({**c, "status": "api_error", "attempts": None, "latency_s": None,
                         "generated_sql": None, "error": "not run (daily quota)"}
                        for c in cases[i:])
            break
        time.sleep(args.sleep)

    completed = [r for r in rows if r["status"] in ("correct", "wrong_result", "error")]
    api_err = [r for r in rows if r["status"] == "api_error"]
    correct = [r for r in rows if r["status"] == "correct"]
    first_try = [r for r in correct if r["attempts"] == 1]
    rescued = [r for r in correct if (r["attempts"] or 0) > 1]
    wrong = [r for r in rows if r["status"] == "wrong_result"]
    failed = [r for r in rows if r["status"] == "error"]
    lat = [r["latency_s"] for r in rows if r["status"] in ("correct", "wrong_result")]

    n = len(completed)
    print("\n================ SUMMARY ================")
    print(f"Questions in test set:        {len(rows)}")
    print(f"API errors (not counted):     {len(api_err)}   <- re-run with --rerun-errors if > 0")
    print(f"Questions evaluated:          {n}")
    if n:
        print(f"Correct:                      {len(correct)}/{n} = {len(correct)/n:.0%}")
        print(f"  correct on first attempt:   {len(first_try)}/{n}")
        print(f"  rescued by retry loop:      {len(rescued)}")
        print(f"Wrong but ran fine:           {len(wrong)}   <- the limitation retries cannot catch")
        print(f"Failed after 3 SQL repairs:   {len(failed)}")
    if lat:
        print(f"Median latency (answered):    {statistics.median(lat):.2f}s")
        if len(lat) >= 20:
            print(f"p95 latency (answered):       {statistics.quantiles(lat, n=20)[18]:.2f}s")
    by_cat = defaultdict(lambda: [0, 0])
    for r in completed:
        by_cat[r["category"]][1] += 1
        by_cat[r["category"]][0] += r["status"] == "correct"
    print("\nBy difficulty:")
    for cat, (ok, tot) in by_cat.items():
        print(f"  {cat:<8} {ok}/{tot}")
    print("\nFailures (read these, they are your interview talking points):")
    for r in wrong + failed:
        print(f"- [{r['category']}] {r['question']}\n    generated: {r['generated_sql']}\n    {r['error'] or ''}")
    for r in api_err:
        print(f"- [API ERROR] {r['question']}")

    json.dump(rows, open(RESULTS_PATH, "w"), indent=2)
    print(f"\nSaved {RESULTS_PATH}")


if __name__ == "__main__":
    main()
