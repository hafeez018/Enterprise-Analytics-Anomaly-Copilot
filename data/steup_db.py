import sqlite3
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/product_metrics.db")
cursor = conn.cursor()

cursor.executescript("""
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS orders;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    signup_date DATE,
    device TEXT,
    plan TEXT
);

CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_name TEXT,
    event_date DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_date DATE,
    amount REAL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
""")

# Seed 500 users
np.random.seed(42)
num_users = 500
start_date = datetime.now() - timedelta(days=60)

devices = np.random.choice(
    ["iOS", "Android", "Web"], size=num_users, p=[0.45, 0.35, 0.20]
)
plans = np.random.choice(
    ["Free", "Pro", "Enterprise"], size=num_users, p=[0.7, 0.25, 0.05]
)
signup_dates = [
    start_date + timedelta(days=int(d))
    for d in np.random.randint(0, 50, size=num_users)
]

users_df = pd.DataFrame(
    {
        "user_id": range(1, num_users + 1),
        "signup_date": [d.strftime("%Y-%m-%d") for d in signup_dates],
        "device": devices,
        "plan": plans,
    }
)
users_df.to_sql("users", conn, if_exists="append", index=False)

# Seed 60 days of activity
events_list = []
orders_list = []

for day in range(60):
    current_date = start_date + timedelta(days=day)
    date_str = current_date.strftime("%Y-%m-%d")
    active_users = np.random.choice(
        users_df["user_id"], size=int(num_users * 0.4), replace=False
    )

    # Simulate a bug in the last 7 days that halved mobile checkouts
    is_recent_anomaly = day >= 53

    for u_id in active_users:
        user_device = users_df.loc[users_df["user_id"] == u_id, "device"].values[0]
        events_list.append((u_id, "page_view", date_str))

        if np.random.rand() > 0.3:
            events_list.append((u_id, "add_to_cart", date_str))

            # Conversion probability
            conv_prob = 0.5
            if is_recent_anomaly and user_device in ["iOS", "Android"]:
                conv_prob = 0.15  # Injected drop

            if np.random.rand() < conv_prob:
                events_list.append((u_id, "checkout", date_str))
                orders_list.append(
                    (u_id, date_str, round(np.random.exponential(45) + 10, 2))
                )

pd.DataFrame(events_list, columns=["user_id", "event_name", "event_date"]).to_sql(
    "events", conn, if_exists="append", index=False
)
pd.DataFrame(orders_list, columns=["user_id", "order_date", "amount"]).to_sql(
    "orders", conn, if_exists="append", index=False
)

conn.commit()
conn.close()
print("Database initialized at data/product_metrics.db")
