"""Generates test_cases.json and verifies every gold query against the real DB."""
import json, sqlite3

DB = "../data/product_metrics.db"

CASES = [
 # ---- easy: single table, simple aggregate / filter ----
 ("easy", "How many users are in the database?",
  "SELECT COUNT(*) FROM users"),
 ("easy", "How many users are on each device type?",
  "SELECT device, COUNT(*) FROM users GROUP BY device"),
 ("easy", "How many users are on each plan?",
  "SELECT plan, COUNT(*) FROM users GROUP BY plan"),
 ("easy", "How many users are on the Enterprise plan?",
  "SELECT COUNT(*) FROM users WHERE plan = 'Enterprise'"),
 ("easy", "How many total orders were placed?",
  "SELECT COUNT(*) FROM orders"),
 ("easy", "What is the total revenue across all orders?",
  "SELECT ROUND(SUM(amount), 2) FROM orders"),
 ("easy", "What is the average order amount?",
  "SELECT ROUND(AVG(amount), 2) FROM orders"),
 ("easy", "What is the largest single order amount?",
  "SELECT MAX(amount) FROM orders"),
 ("easy", "How many events are recorded for each event name?",
  "SELECT event_name, COUNT(*) FROM events GROUP BY event_name"),
 ("easy", "What is the earliest and latest signup date?",
  "SELECT MIN(signup_date), MAX(signup_date) FROM users"),
 ("easy", "How many iOS users are there?",
  "SELECT COUNT(*) FROM users WHERE device = 'iOS'"),
 ("easy", "How many distinct users have placed at least one order?",
  "SELECT COUNT(DISTINCT user_id) FROM orders"),

 # ---- medium: joins, grouping, date logic ----
 ("medium", "What is the total revenue by device type?",
  "SELECT u.device, ROUND(SUM(o.amount), 2) FROM orders o JOIN users u ON o.user_id = u.user_id GROUP BY u.device"),
 ("medium", "What is the average order amount by plan?",
  "SELECT u.plan, ROUND(AVG(o.amount), 2) FROM orders o JOIN users u ON o.user_id = u.user_id GROUP BY u.plan"),
 ("medium", "How many orders were placed in August 2026?",
  "SELECT COUNT(*) FROM orders WHERE strftime('%Y-%m', order_date) = '2026-08'"),
 ("medium", "How many users signed up in each month?",
  "SELECT strftime('%Y-%m', signup_date), COUNT(*) FROM users GROUP BY 1"),
 ("medium", "How many orders per day were placed between 2026-09-01 and 2026-09-05 inclusive?",
  "SELECT order_date, COUNT(*) FROM orders WHERE order_date BETWEEN '2026-09-01' AND '2026-09-05' GROUP BY order_date"),
 ("medium", "Which 5 users have spent the most in total? Show user_id and total spend.",
  "SELECT user_id, ROUND(SUM(amount), 2) FROM orders GROUP BY user_id ORDER BY SUM(amount) DESC LIMIT 5"),
 ("medium", "How many users have never placed an order?",
  "SELECT COUNT(*) FROM users WHERE user_id NOT IN (SELECT DISTINCT user_id FROM orders)"),
 ("medium", "How many page_view events were there on each device type?",
  "SELECT u.device, COUNT(*) FROM events e JOIN users u ON e.user_id = u.user_id WHERE e.event_name = 'page_view' GROUP BY u.device"),
 ("medium", "What is the total revenue per month?",
  "SELECT strftime('%Y-%m', order_date), ROUND(SUM(amount), 2) FROM orders GROUP BY 1"),
 ("medium", "Which plan has the highest number of orders?",
  "SELECT u.plan FROM orders o JOIN users u ON o.user_id = u.user_id GROUP BY u.plan ORDER BY COUNT(*) DESC LIMIT 1"),
 ("medium", "How many checkout events happened on each device type?",
  "SELECT u.device, COUNT(*) FROM events e JOIN users u ON e.user_id = u.user_id WHERE e.event_name = 'checkout' GROUP BY u.device"),
 ("medium", "How many orders had an amount above 100?",
  "SELECT COUNT(*) FROM orders WHERE amount > 100"),

 # ---- hard: ratios, funnels, CTEs, subqueries, windows ----
 ("hard", "What is the overall add_to_cart to checkout conversion rate as a percentage? Count events, not unique users.",
  "SELECT ROUND(100.0 * SUM(event_name = 'checkout') / SUM(event_name = 'add_to_cart'), 2) FROM events"),
 ("hard", "What is the checkout event count divided by add_to_cart event count, per device type, as a percentage?",
  "SELECT u.device, ROUND(100.0 * SUM(e.event_name = 'checkout') / SUM(e.event_name = 'add_to_cart'), 2) FROM events e JOIN users u ON e.user_id = u.user_id GROUP BY u.device"),
 ("hard", "For each day from 2026-09-03 to 2026-09-08 inclusive, how many checkout events were there?",
  "SELECT event_date, COUNT(*) FROM events WHERE event_name = 'checkout' AND event_date BETWEEN '2026-09-03' AND '2026-09-08' GROUP BY event_date"),
 ("hard", "Compare checkout-to-add_to_cart event ratio on iOS and Android users before 2026-08-31 versus on or after 2026-08-31. Show period and ratio as a percentage.",
  "SELECT CASE WHEN e.event_date < '2026-08-31' THEN 'before' ELSE 'after' END AS period, ROUND(100.0 * SUM(e.event_name = 'checkout') / SUM(e.event_name = 'add_to_cart'), 2) FROM events e JOIN users u ON e.user_id = u.user_id WHERE u.device IN ('iOS', 'Android') GROUP BY period"),
 ("hard", "What is the average number of orders per user among users who placed at least one order?",
  "SELECT ROUND(1.0 * COUNT(*) / COUNT(DISTINCT user_id), 2) FROM orders"),
 ("hard", "What percentage of users have placed at least one order?",
  "SELECT ROUND(100.0 * COUNT(DISTINCT o.user_id) / (SELECT COUNT(*) FROM users), 2) FROM orders o"),
 ("hard", "Which device type has the highest average order amount, and what is that average?",
  "SELECT u.device, ROUND(AVG(o.amount), 2) FROM orders o JOIN users u ON o.user_id = u.user_id GROUP BY u.device ORDER BY AVG(o.amount) DESC LIMIT 1"),
 ("hard", "List users who have more than 10 orders, with their order counts.",
  "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id HAVING COUNT(*) > 10"),
 ("hard", "What is the daily revenue for the 3 days with the highest revenue? Show date and revenue.",
  "SELECT order_date, ROUND(SUM(amount), 2) FROM orders GROUP BY order_date ORDER BY SUM(amount) DESC LIMIT 3"),
 ("hard", "What is the cumulative number of orders by date for 2026-09-01 to 2026-09-03?",
  "SELECT order_date, SUM(COUNT(*)) OVER (ORDER BY order_date) FROM orders WHERE order_date BETWEEN '2026-09-01' AND '2026-09-03' GROUP BY order_date"),
 ("hard", "How many users signed up each week? Use strftime('%W') as the week number.",
  "SELECT strftime('%W', signup_date), COUNT(*) FROM users GROUP BY 1"),
 ("hard", "What share of total revenue comes from each plan, as a percentage?",
  "SELECT u.plan, ROUND(100.0 * SUM(o.amount) / (SELECT SUM(amount) FROM orders), 2) FROM orders o JOIN users u ON o.user_id = u.user_id GROUP BY u.plan"),

 # ---- ambiguous / tricky wording (expected to fail sometimes: honest limits) ----
 ("tricky", "How many users converted?",
  "SELECT COUNT(DISTINCT user_id) FROM orders"),
 ("tricky", "Which day had the most activity?",
  "SELECT event_date FROM events GROUP BY event_date ORDER BY COUNT(*) DESC LIMIT 1"),
 ("tricky", "How many people bought something on mobile?",
  "SELECT COUNT(DISTINCT o.user_id) FROM orders o JOIN users u ON o.user_id = u.user_id WHERE u.device IN ('iOS', 'Android')"),
]

def main():
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    out, bad = [], 0
    for i, (cat, q, sql) in enumerate(CASES, 1):
        try:
            rows = conn.execute(sql).fetchall()
            ok = len(rows) > 0 and len(rows) < 500
        except Exception as e:
            rows, ok = [], False
            print(f"[ERROR] #{i}: {e}")
        if not ok:
            bad += 1
            print(f"[CHECK] #{i} returned {len(rows)} rows: {q}")
        out.append({"id": i, "category": cat, "question": q, "gold_sql": sql})
    json.dump(out, open("test_cases.json", "w"), indent=2)
    print(f"Wrote {len(out)} cases, {bad} need attention")

if __name__ == "__main__":
    main()
