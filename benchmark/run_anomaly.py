"""
Anomaly-detection benchmark: Modified Z-score (MAD) vs standard Z-score on data with
injected anomalies. Run from the PROJECT ROOT:
    python benchmark/run_anomaly.py
No API key needed. Writes benchmark/results_anomaly.json
"""
import json, os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.getcwd())
from core.stats_engine import StatisticalAnalyzer as SA

def one_run(seed, n=200, k=20):
    rng = np.random.default_rng(seed)
    values = rng.normal(100, 5, n)
    idx = rng.choice(n, k, replace=False)
    values[idx] = rng.choice([30, 40, 170, 180, 250], k)   # drops and spikes
    df = pd.DataFrame({"metric": values})
    truth = np.zeros(n, bool); truth[idx] = True
    res = {}
    for name, flags in {
        "zscore_3.0": SA.detect_anomalies_zscore(df, "metric", 3.0)["is_anomaly"].to_numpy(),
        "zscore_2.0": SA.detect_anomalies_zscore(df, "metric", 2.0)["is_anomaly"].to_numpy(),
        "mad_3.5":    SA.detect_anomalies_mad(df, "metric", 3.5)["is_anomaly"].to_numpy(),
    }.items():
        tp = int((flags & truth).sum()); fp = int((flags & ~truth).sum()); fn = int((~flags & truth).sum())
        res[name] = {"tp": tp, "fp": fp, "fn": fn,
                     "precision": tp / (tp + fp) if tp + fp else 0.0,
                     "recall": tp / (tp + fn) if tp + fn else 0.0}
    return res

runs = [one_run(s) for s in range(20)]          # 20 random datasets
summary = {}
for name in runs[0]:
    summary[name] = {m: float(np.mean([r[name][m] for r in runs])) for m in ("tp", "fp", "fn", "precision", "recall")}

print("200 points, 20 injected anomalies (10%), averaged over 20 random datasets")
print(f"{'method':<12} {'found':>6} {'missed':>7} {'false alarms':>13} {'precision':>10} {'recall':>8}")
for name, s in summary.items():
    print(f"{name:<12} {s['tp']:>6.1f} {s['fn']:>7.1f} {s['fp']:>13.1f} {s['precision']:>10.2f} {s['recall']:>8.2f}")
json.dump(summary, open("benchmark/results_anomaly.json", "w"), indent=2)
print("\nSaved benchmark/results_anomaly.json")
