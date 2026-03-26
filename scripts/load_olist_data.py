# scripts/load_olist_data.py
"""
Day 1 - Phase 7: Real data integration
Maps Olist Brazilian E-Commerce dataset to Ecom-Sentinel schema.

Source files needed:
- olist_order_items_dataset.csv  (price, product_id, order_id)
- olist_orders_dataset.csv       (order_id, order_date)
- olist_products_dataset.csv     (product_id, category)
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
ARCHIVE     = "archive (6)"
ITEMS_CSV   = f"{ARCHIVE}/olist_order_items_dataset.csv"
ORDERS_CSV  = f"{ARCHIVE}/olist_orders_dataset.csv"
PRODUCTS_CSV= f"{ARCHIVE}/olist_products_dataset.csv"
DB_PATH     = "market_data.db"

np.random.seed(42)


def load_raw():
    print("Loading Olist CSV files...")
    items    = pd.read_csv(ITEMS_CSV)
    orders   = pd.read_csv(ORDERS_CSV)
    products = pd.read_csv(PRODUCTS_CSV)

    print(f"  order_items:  {len(items):,} rows")
    print(f"  orders:       {len(orders):,} rows")
    print(f"  products:     {len(products):,} rows")

    return items, orders, products


def build_sales_history(items, orders, products):
    """
    Map Olist → sales_history schema:
    product_id, date, price, units_sold, promotion_status
    """
    print("\nBuilding sales_history...")

    # Merge order date onto items
    orders["date"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    ).dt.date.astype(str)

    df = items.merge(
        orders[["order_id", "date"]],
        on="order_id",
        how="inner"
    )

    # Aggregate to daily units sold per product
    daily = (
        df.groupby(["product_id", "date"])
        .agg(
            units_sold=("order_item_id", "count"),
            price=("price", "mean"),           # avg price per day
        )
        .reset_index()
    )

    # Filter: keep only products with at least 60 days of sales history
    # Less than 60 days = not enough to fit a reliable demand curve
    product_days = daily.groupby("product_id")["date"].nunique()
    valid_products = product_days[product_days >= 60].index
    daily = daily[daily["product_id"].isin(valid_products)]

    # Keep top 50 products by total sales volume for manageability
    top_products = (
        daily.groupby("product_id")["units_sold"]
        .sum()
        .nlargest(50)
        .index
    )
    daily = daily[daily["product_id"].isin(top_products)]

    daily["promotion_status"] = "no"

    print(f"  Products retained: {daily['product_id'].nunique()}")
    print(f"  Date range: {daily['date'].min()} to {daily['date'].max()}")
    print(f"  Total rows: {len(daily):,}")
    print(f"  Price range: ${daily['price'].min():.2f} – ${daily['price'].max():.2f}")
    print(f"  Units/day range: {daily['units_sold'].min()} – {daily['units_sold'].max()}")

    return daily


def build_competitor_intelligence(sales_df):
    """
    Olist has no competitor data — synthesize realistic competitor prices
    based on real price distributions from the dataset.
    Competitors price within ±15% of actual market price.
    """
    print("\nBuilding competitor_intelligence...")

    product_avg = sales_df.groupby("product_id")["price"].mean()
    rows = []

    # Weekly competitor price updates
    dates = pd.date_range(
        start=sales_df["date"].min(),
        end=sales_df["date"].max(),
        freq="7D"
    )

    for product_id, avg_price in product_avg.items():
        for date in dates:
            for comp in ["CompA", "CompB", "CompC"]:
                rows.append({
                    "product_id":       product_id,
                    "competitor_price": round(
                        avg_price * np.random.uniform(0.85, 1.15), 2
                    ),
                    "timestamp":        date.strftime("%Y-%m-%d %H:%M:%S"),
                })

    df = pd.DataFrame(rows)
    print(f"  Rows: {len(df):,}")
    return df


def build_inventory_cost(sales_df):
    """
    Derive cost from real prices — typical e-commerce margin is 30-50%.
    Stock estimated from sales velocity.
    """
    print("\nBuilding inventory_cost...")

    product_stats = sales_df.groupby("product_id").agg(
        avg_price=("price", "mean"),
        avg_daily_sales=("units_sold", "mean"),
    ).reset_index()

    rows = []
    for _, row in product_stats.iterrows():
        rows.append({
            "product_id":    row["product_id"],
            "current_stock": int(row["avg_daily_sales"] * np.random.randint(30, 90)),
            "base_cost":     round(row["avg_price"] * np.random.uniform(0.50, 0.65), 2),
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

    # Verify
    print("\nVerification:")
    for table in ["sales_history", "competitor_intelligence", "inventory_cost"]:
        n = pd.read_sql(f"SELECT COUNT(*) as n FROM {table}", conn).iloc[0, 0]
        print(f"  {table}: {n:,} rows")

    # Sanity check correlation
    df = pd.read_sql("""
        SELECT s.product_id, s.price, s.units_sold
        FROM sales_history s
    """, conn)
    corr = df.groupby("product_id").apply(
        lambda x: x["price"].corr(x["units_sold"])
    ).mean()
    print(f"\n  Avg price-demand correlation: {corr:.4f}")
    print(f"  (negative = demand falls as price rises — correct)")
    conn.close()


if __name__ == "__main__":
    print("=" * 55)
    print("Phase 7 Day 1 — Olist Real Data Integration")
    print("=" * 55)

    items, orders, products = load_raw()
    sales_df      = build_sales_history(items, orders, products)
    competitor_df = build_competitor_intelligence(sales_df)
    inventory_df  = build_inventory_cost(sales_df)
    seed_db(sales_df, competitor_df, inventory_df)

    print("\nDone. Run scripts/retrain_demand_model.py next.")