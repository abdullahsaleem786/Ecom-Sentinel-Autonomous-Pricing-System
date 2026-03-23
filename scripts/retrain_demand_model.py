# scripts/retrain_demand_model.py
"""
Per-product demand curve fitting.
For each product, fit: units_sold = a * price^b
where b is the price elasticity exponent.
This guarantees demand responds to price correctly.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
import numpy as np
import pandas as pd
import joblib
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

DB_PATH   = "market_data.db"
MODEL_OUT = "models/demand_model.pkl"
DATA_OUT  = "data/processed/pricing_features.csv"


def load_raw(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT
            s.product_id, s.date, s.price, s.units_sold,
            COALESCE(c.competitor_price, s.price) AS competitor_price,
            COALESCE(i.base_cost, s.price * 0.6)  AS cost_price
        FROM sales_history s
        LEFT JOIN (
            SELECT product_id, AVG(competitor_price) AS competitor_price
            FROM competitor_intelligence
            GROUP BY product_id
        ) c ON s.product_id = c.product_id
        LEFT JOIN inventory_cost i ON s.product_id = i.product_id
        ORDER BY s.product_id, s.date
    """, conn)
    conn.close()
    return df


def demand_curve(price, a, b):
    """Power-law demand curve: demand = a * price^b  (b should be negative)"""
    return a * np.power(price, b)


def fit_product_curves(df):
    """
    Fit a demand curve for each product.
    Returns dict: {product_id: {"a": float, "b": float, "r2": float}}
    """
    curves = {}
    failed = []

    for product_id, group in df.groupby("product_id"):
        prices  = group["price"].values
        demands = group["units_sold"].values.astype(float)

        try:
            # Initial guess: a=base_demand at avg price, b=-1.0 (unit elastic)
            a0 = demands.mean()
            b0 = -1.0
            popt, _ = curve_fit(
                demand_curve, prices, demands,
                p0=[a0, b0],
                bounds=([0, -5], [np.inf, -0.01]),  # b must be negative
                maxfev=5000,
            )
            a, b = popt

            # Evaluate fit
            preds = demand_curve(prices, a, b)
            r2    = r2_score(demands, preds)

            curves[product_id] = {
                "a": round(float(a), 4),
                "b": round(float(b), 4),
                "r2": round(float(r2), 4),
                "avg_price":   round(float(prices.mean()), 4),
                "base_demand": round(float(demands.mean()), 4),
            }

        except Exception as e:
            failed.append(product_id)
            # Fallback: use average demand, flat curve
            curves[product_id] = {
                "a": float(demands.mean() * (prices.mean() ** 1.0)),
                "b": -1.0,
                "r2": 0.0,
                "avg_price":   float(prices.mean()),
                "base_demand": float(demands.mean()),
            }

    # Summary
    r2_vals = [v["r2"] for v in curves.values()]
    b_vals  = [v["b"] for v in curves.values()]
    print(f"Products fitted:  {len(curves)}")
    print(f"Failed fits:      {len(failed)}")
    print(f"Avg R²:           {np.mean(r2_vals):.3f}")
    print(f"R² range:         {min(r2_vals):.3f} – {max(r2_vals):.3f}")
    print(f"Avg elasticity b: {np.mean(b_vals):.3f}")
    print(f"b range:          {min(b_vals):.3f} – {max(b_vals):.3f}")

    return curves


def engineer_context_features(df):
    """
    Engineer context features for each row:
    price_elasticity, price_gap — used by agents for signal generation.
    These are NOT used by the demand model anymore.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)
    g  = df.groupby("product_id")

    stats = df.groupby("product_id").agg(
        base_demand=("units_sold", "mean"),
        avg_price=("price", "mean"),
    ).reset_index()
    df = df.merge(stats, on="product_id")

    df["price_ratio"] = df["price"] / df["avg_price"]

    df["prev_price"] = g["price"].shift(1)
    df["prev_units"] = g["units_sold"].shift(1)
    pct_d = (df["units_sold"] - df["prev_units"]) / df["prev_units"].replace(0, np.nan)
    pct_p = (df["price"] - df["prev_price"])      / df["prev_price"].replace(0, np.nan)
    df["price_elasticity"] = (pct_d / pct_p.replace(0, np.nan)).clip(-10, 10)
    df["price_gap"]        = df["price"] - df["competitor_price"]

    return df


if __name__ == "__main__":
    print("Step 1: Loading raw data...")
    raw = load_raw(DB_PATH)
    print(f"Raw rows: {len(raw)}")

    print("\nStep 2: Fitting per-product demand curves...")
    curves = fit_product_curves(raw)

    print("\nStep 3: Saving model (curves dict)...")
    joblib.dump(curves, MODEL_OUT)
    print(f"Saved → {MODEL_OUT}")

    print("\nStep 4: Engineering context features...")
    df = engineer_context_features(raw)
    df = df.dropna(subset=["price_elasticity", "price_gap"])

    out_cols = ["product_id", "date", "cost_price", "price",
                "avg_price", "base_demand", "price_ratio",
                "price_elasticity", "price_gap"]
    df[out_cols].to_csv(DATA_OUT, index=False)
    print(f"Saved features → {DATA_OUT}  ({len(df)} rows)")

    print("\nSample curves:")
    sample = pd.DataFrame(curves).T.head(5)
    print(sample.to_string())
    print("\nDone.")