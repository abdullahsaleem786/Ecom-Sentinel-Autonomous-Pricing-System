# scripts/seed_data.py
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DB_PATH    = "market_data.db"
np.random.seed(42)

N_PRODUCTS = 30
N_DAYS     = 365
START_DATE = datetime(2023, 1, 1)

PRODUCTS = []
for i in range(N_PRODUCTS):
    base_price  = round(np.random.uniform(20, 100), 2)
    base_demand = np.random.randint(40, 120)
    elasticity  = round(np.random.uniform(-2.0, -0.8), 2)
    PRODUCTS.append({
        "product_id": f"P{i+1:03d}",
        "base_price":  base_price,
        "base_demand": base_demand,
        "elasticity":  elasticity,
        "cost_ratio":  round(np.random.uniform(0.45, 0.60), 2),
        "stock":       np.random.randint(300, 1500),
    })


def generate_sales(products, n_days, start_date):
    rows = []
    for p in products:
        for d in range(n_days):
            date = start_date + timedelta(days=d)

            # Price varies around base — no promotions, pure price signal
            price_mult = np.random.choice(
                [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15],
                p=[0.05, 0.15, 0.25, 0.20, 0.20, 0.10, 0.05]
            )
            price = round(p["base_price"] * price_mult, 2)

            # Demand responds ONLY to price via elasticity — no promotion noise
            price_change_pct  = (price - p["base_price"]) / p["base_price"]
            demand_change_pct = p["elasticity"] * price_change_pct
            expected_demand   = p["base_demand"] * (1 + demand_change_pct)

            # Very tight noise — 3% only
            units_sold = max(1, int(np.random.normal(expected_demand, expected_demand * 0.03)))

            rows.append({
                "date":             date.strftime("%Y-%m-%d"),
                "product_id":       p["product_id"],
                "units_sold":       units_sold,
                "price":            price,
                "promotion_status": "no",   # no promotions — clean signal
            })
    return pd.DataFrame(rows)


def generate_competitor_intelligence(products, n_days, start_date):
    rows = []
    for p in products:
        for d in range(0, n_days, 7):
            date = start_date + timedelta(days=d)
            for comp in ["CompA", "CompB", "CompC"]:
                rows.append({
                    "product_id":       p["product_id"],
                    "competitor_price": round(p["base_price"] * np.random.uniform(0.88, 1.12), 2),
                    "timestamp":        date.strftime("%Y-%m-%d %H:%M:%S"),
                })
    return pd.DataFrame(rows)


def generate_inventory_cost(products):
    return pd.DataFrame([{
        "product_id":    p["product_id"],
        "current_stock": p["stock"],
        "base_cost":     round(p["base_price"] * p["cost_ratio"], 2),
    } for p in products])


def seed(db_path):
    conn = sqlite3.connect(db_path)
    conn.cursor().executescript("""
        DROP TABLE IF EXISTS sales_history;
        DROP TABLE IF EXISTS competitor_intelligence;
        DROP TABLE IF EXISTS inventory_cost;

        CREATE TABLE sales_history (
            sale_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date             DATE,
            product_id       TEXT,
            units_sold       INTEGER,
            price            REAL,
            promotion_status TEXT
        );
        CREATE TABLE competitor_intelligence (
            intel_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id       TEXT,
            competitor_price REAL,
            timestamp        DATETIME
        );
        CREATE TABLE inventory_cost (
            product_id    TEXT PRIMARY KEY,
            current_stock INTEGER,
            base_cost     REAL
        );
    """)

    sales_df = generate_sales(PRODUCTS, N_DAYS, START_DATE)
    sales_df.to_sql("sales_history", conn, if_exists="append", index=False)

    comp_df = generate_competitor_intelligence(PRODUCTS, N_DAYS, START_DATE)
    comp_df.to_sql("competitor_intelligence", conn, if_exists="append", index=False)

    inv_df = generate_inventory_cost(PRODUCTS)
    inv_df.to_sql("inventory_cost", conn, if_exists="append", index=False)

    conn.commit()

    df = pd.read_sql("SELECT price, units_sold FROM sales_history", conn)
    corr = df.corr()["units_sold"]["price"]
    print(f"Rows inserted:            {len(sales_df)}")
    print(f"Unique products:          {sales_df['product_id'].nunique()}")
    print(f"Price-demand correlation: {corr:.4f}  (target: below -0.6)")
    conn.close()


if __name__ == "__main__":
    seed(DB_PATH)
    print("Done. Run scripts/retrain_demand_model.py next.")