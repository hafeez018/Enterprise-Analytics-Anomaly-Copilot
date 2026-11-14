"""
Guardrail benchmark. Run from the PROJECT ROOT:
    python benchmark/run_guardrails.py
No API key needed. Writes benchmark/results_guardrails.json
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from core.security import SQLSecurityError, SQLSecurityGuard

SHOULD_BLOCK = [
    # mutations / DDL
    "DROP TABLE users;", "DELETE FROM orders;", "DELETE FROM orders WHERE user_id = 1;",
    "UPDATE users SET plan = 'Pro';", "INSERT INTO users VALUES (1,'2026-09-01','iOS','Free');",
    "ALTER TABLE events ADD COLUMN test TEXT;", "CREATE TABLE x (a INT);",
    "REPLACE INTO users VALUES (1,'2026-09-01','iOS','Free');",
    "TRUNCATE TABLE users;",
    # stacked / piggy-backed
    "SELECT * FROM users; DROP TABLE orders;", "SELECT 1; SELECT 2;",
    "SELECT 1; DELETE FROM users;",
    # obfuscation
    "dRoP TaBlE users;", "SELECT * FROM users; /* harmless */ DROP TABLE users;",
    "WITH d AS (SELECT 1) DELETE FROM users;",
    # system catalog
    "SELECT * FROM sqlite_master;", "SELECT * FROM SQLITE_MASTER;",
    "SELECT sql FROM sqlite_schema WHERE type='table';", "SELECT * FROM sqlite_temp_master;",
    "SELECT * FROM main.sqlite_master;", "SELECT * FROM sqlite_sequence;",
    "SELECT name FROM pragma_table_info('users');",
    # other SQLite-specific risks
    "PRAGMA table_info(users);", "ATTACH DATABASE 'x.db' AS x;",
    "SELECT load_extension('x');", "VACUUM;",
]

SHOULD_PASS = [
    "SELECT user_id AS drop_rate FROM users;",   # keyword inside an alias
    "SELECT device, COUNT(*) FROM users GROUP BY device;",
    "SELECT * FROM events WHERE event_name = 'drop_pin';",
    "SELECT * FROM events WHERE event_name = 'checkout';",
    "SELECT 'Please delete my account' AS message;",
    "SELECT 'UPDATE users SET x=1' AS note;",
    "SELECT plan, COUNT(*) AS update_count FROM users GROUP BY plan;",
    "SELECT COUNT(*) AS deleted_rows FROM orders;",
    "SELECT user_id FROM users WHERE plan = 'Free' ORDER BY user_id;",
    "SELECT strftime('%Y-%m', signup_date), COUNT(*) FROM users GROUP BY 1;",
    "SELECT u.user_id FROM users u JOIN orders o ON u.user_id = o.user_id;",
    "WITH t AS (SELECT user_id FROM users) SELECT COUNT(*) FROM t;",
    "SELECT user_id FROM users UNION SELECT user_id FROM orders;",
    "SELECT * FROM (SELECT * FROM users LIMIT 5) t;",
    "SELECT order_date, SUM(amount) OVER (ORDER BY order_date) FROM orders;",
    "SELECT * FROM users LIMIT 5;",
]

def check(sql):
    try:
        out = SQLSecurityGuard.validate_query(sql)
        return "allowed", out
    except SQLSecurityError as e:
        return "blocked", str(e)
    except Exception as e:                     # parser / unexpected errors
        return "blocked_other", f"{type(e).__name__}: {e}"

slipped, wrongly_blocked, log = [], [], []
blocked = 0
for q in SHOULD_BLOCK:
    r, detail = check(q)
    log.append({"type": "malicious", "sql": q, "result": r, "detail": detail})
    if r == "allowed":
        slipped.append(q)
    else:
        blocked += 1
allowed = 0
for q in SHOULD_PASS:
    r, detail = check(q)
    log.append({"type": "legitimate", "sql": q, "result": r, "detail": detail})
    if r == "allowed":
        allowed += 1
    else:
        wrongly_blocked.append((q, detail))

print(f"Malicious queries blocked:   {blocked}/{len(SHOULD_BLOCK)}")
print(f"Legitimate queries allowed:  {allowed}/{len(SHOULD_PASS)}")
print("\nSLIPPED THROUGH (fix these in core/security.py):")
for q in slipped: print("  -", q)
print("\nWRONGLY BLOCKED:")
for q, d in wrongly_blocked: print("  -", q, "->", d)
json.dump(log, open("benchmark/results_guardrails.json", "w"), indent=2)
print("\nSaved benchmark/results_guardrails.json")
