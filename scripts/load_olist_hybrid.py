# scripts/load_olist_hybrid.py
"""
Phase 7 Day 1 — Hybrid Data Integration
Uses real Olist product IDs and price ranges.
Generates realistic price-elastic demand calibrated to real prices.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

ARCHIVE      = "archive (6)"
ITEMS_CSV    = f"{ARCHIVE}/olist_order_items_dataset.csv"
ORDERS_CSV   = f"{ARCHIVE}/olist_orders_dataset.csv"
PRODUCTS_CSV = f"{ARCHIVE}/olist_products_dataset.csv"
CATEGORY_CSV = f"{ARCHIVE}/product_category_name_translation.csv"
DB_PATH      = "market_data.db"

np.random.seed(42)

N_DAYS     = 365
START_DATE = datetime(2017, 1, 1)


def extract_real_product_profiles():
    """
    Extract real product IDs and their actual price distributions from Olist.
    Keep top 30 products by order volume — enough history, enough variety.
    """
    print("Extracting real product profiles from Olist...")

    items   = pd.read_csv(ITEMS_CSV)
    orders  = pd.read_csv(ORDERS_CSV)
    products= pd.read_csv(PRODUCTS_CSV)
    cats    = pd.read_csv(CATEGORY_CSV)

    # Merge order dates
    orders["date"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    ).dt.date.astype(str)

    df = items.merge(orders[["order_id", "date"]], on="order_id")
    df = df.merge(products[["product_id", "product_category_name"]], on="product_id")
    df = df.merge(cats, on="product_category_name", how="left")

    # Get product stats from real data
    stats = df.groupby("product_id").agg(
        real_avg_price   =("price", "mean"),
        real_price_std   =("price", "std"),
        real_min_price   =("price", "min"),
        real_max_price   =("price", "max"),
        total_orders     =("order_id", "count"),
        category         =("product_category_name_english", "first"),
    ).reset_index()

    # Keep top 30 by order volume — enough data to be meaningful
    stats = stats.nlargest(30, "total_orders").reset_index(drop=True)
    stats["real_price_std"] = stats["real_price_std"].fillna(
        stats["real_avg_price"] * 0.10
    )

    print(f"  Products selected: {len(stats)}")
    print(f"  Price range: ${stats['real_avg_price'].min():.2f} "
          f"– ${stats['real_avg_price'].max():.2f}")
    print(f"  Categories: {stats['category'].nunique()}")

    return stats


def generate_hybrid_sales(product_profiles):
    """
    Generate daily sales using:
    - Real product IDs from Olist
    - Real price levels and ranges from Olist
    - Synthetic but realistic demand curve per product
    """
    print("\nGenerating hybrid sales history...")
    rows = []

    for _, p in product_profiles.iterrows():
        # Assign realistic demand based on real order volume
        # Scale total_orders to daily units (365 days)
        avg_daily = max(5, int(p["total_orders"] / 365 * 3))
        base_demand = np.random.randint(
            max(5, avg_daily - 2),
            avg_daily + 10
        )

        # Elasticity calibrated to price level
        # Higher priced products tend to be more elastic
        if p["real_avg_price"] > 100:
            elasticity = round(np.random.uniform(-2.0, -1.2), 2)
        elif p["real_avg_price"] > 50:
            elasticity = round(np.random.uniform(-1.8, -0.9), 2)
        else:
            elasticity = round(np.random.uniform(-1.5, -0.7), 2)

        # Price variation based on real std from Olist
        price_variation = min(0.20, p["real_price_std"] / p["real_avg_price"])
        price_variation = max(0.05, price_variation)

        for d in range(N_DAYS):
            date = START_DATE + timedelta(days=d)

            # Price varies around real average
            price_mult = np.random.choice(
                [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15],
                p=[0.05, 0.10, 0.20, 0.30, 0.20, 0.10, 0.05]
            )
            price = round(p["real_avg_price"] * price_mult, 2)

            # Clamp to real observed price range with 10% buffer
            price = max(p["real_min_price"] * 0.90,
                       min(p["real_max_price"] * 1.10, price))

            # Demand responds to price via elasticity
            price_change_pct  = (price - p["real_avg_price"]) / p["real_avg_price"]
            demand_change_pct = elasticity * price_change_pct
            expected_demand   = base_demand * (1 + demand_change_pct)

            # Tight noise — 4%
            units_sold = max(1, int(
                np.random.normal(expected_demand, expected_demand * 0.04)
            ))

            rows.append({
                "date":             date.strftime("%Y-%m-%d"),
                "product_id":       p["product_id"],
                "units_sold":       units_sold,
                "price":            price,
                "promotion_status": "no",
            })

    df = pd.DataFrame(rows)
    print(f"  Rows generated: {len(df):,}")
    print(f"  Products: {df['product_id'].nunique()}")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Price range: ${df['price'].min():.2f} – ${df['price'].max():.2f}")
    print(f"  Units/day range: {df['units_sold'].min()} – {df['units_sold'].max()}")

    # Verify correlation
    corr = df.groupby("product_id").apply(
        lambda x: x["price"].corr(x["units_sold"]),
        include_groups=False
    ).mean()
    print(f"  Avg price-demand correlation: {corr:.4f}  (target: below -0.4)")

    return df


def generate_competitor_intelligence(sales_df, product_profiles):
    print("\nGenerating competitor intelligence...")
    rows  = []
    dates = pd.date_range(start=START_DATE, periods=N_DAYS // 7, freq="7D")

    price_map = dict(zip(
        product_profiles["product_id"],
        product_profiles["real_avg_price"]
    ))

    for product_id, avg_price in price_map.items():
        for date in dates:
            for comp in ["CompA", "CompB", "CompC"]:
                rows.append({
                    "product_id":       product_id,
                    "competitor_price": round(
                        avg_price * np.random.uniform(0.88, 1.12), 2
                    ),
                    "timestamp": date.strftime("%Y-%m-%d %H:%M:%S"),
                })

    df = pd.DataFrame(rows)
    print(f"  Rows: {len(df):,}")
    return df


def generate_inventory_cost(sales_df, product_profiles):
    print("\nGenerating inventory & cost...")
    rows = []

    avg_sales = sales_df.groupby("product_id")["units_sold"].mean()

    for _, p in product_profiles.iterrows():
        pid        = p["product_id"]
        avg_daily  = avg_sales.get(pid, 10)
        rows.append({
            "product_id":    pid,
            "current_stock": int(avg_daily * np.random.randint(30, 90)),
            "base_cost":     round(
                p["real_avg_price"] * np.random.uniform(0.50, 0.65), 2
            ),
        })

    df = pd.DataFrame(rows)
    print(f"  Products: {len(df)}")
    return df


def seed_db(sales_df, competitor_df, inventory_df):
    print("\nSeeding database...")
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.executescript("""
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

    sales_df[["date", "product_id", "units_sold",
              "price", "promotion_status"]].to_sql(
        "sales_history", conn, if_exists="append", index=False
    )
    competitor_df.to_sql(
        "competitor_intelligence", conn, if_exists="append", index=False
    )
    inventory_df.to_sql(
        "inventory_cost", conn, if_exists="append", index=False
    )
    conn.commit()

    print("\nVerification:")
    for table in ["sales_history", "competitor_intelligence", "inventory_cost"]:
        n = pd.read_sql(
            f"SELECT COUNT(*) as n FROM {table}", conn
        ).iloc[0, 0]
        print(f"  {table}: {n:,} rows")

    conn.close()


if __name__ == "__main__":
    print("=" * 55)
    print("Phase 7 Day 1 — Hybrid Olist Data Integration")
    print("=" * 55)

    profiles      = extract_real_product_profiles()
    sales_df      = generate_hybrid_sales(profiles)
    competitor_df = generate_competitor_intelligence(sales_df, profiles)
    inventory_df  = generate_inventory_cost(sales_df, profiles)
    seed_db(sales_df, competitor_df, inventory_df)

    print("\nDone. Run scripts/retrain_demand_model.py next.")