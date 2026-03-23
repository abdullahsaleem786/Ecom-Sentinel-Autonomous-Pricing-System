# scripts/retrain_demand_model.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

DB_PATH    = "market_data.db"
MODEL_OUT  = "models/demand_model.pkl"
DATA_OUT   = "data/processed/pricing_features.csv"

# These are the ONLY legal features — no units_sold
FEATURES = [
    "price",
    "price_elasticity",
    "inventory_velocity",
    "price_gap",
    "demand_trend",
]
TARGET = "units_sold_next_7_days"


def load_raw(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT
            s.product_id,
            s.date,
            s.price,
            s.units_sold,
            COALESCE(c.competitor_price, s.price)  AS competitor_price,
            COALESCE(i.current_stock, 100)          AS current_stock,
            COALESCE(i.base_cost, s.price * 0.6)   AS cost_price
        FROM sales_history s
        LEFT JOIN (
            SELECT product_id, AVG(competitor_price) AS competitor_price
            FROM competitor_intelligence
            GROUP BY product_id
        ) c ON s.product_id = c.product_id
        LEFT JOIN inventory_cost i
            ON s.product_id = i.product_id
        ORDER BY s.product_id, s.date
    """, conn)
    conn.close()
    return df

def engineer_features(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    g = df.groupby("product_id")

    # LAG values — strictly past, no current row bleed
    df["prev_price"] = g["price"].shift(1)
    df["prev_units"] = g["units_sold"].shift(1)

    # Price elasticity = % demand change / % price change (using only past data)
    pct_demand = (df["units_sold"] - df["prev_units"]) / df["prev_units"].replace(0, np.nan)
    pct_price  = (df["price"] - df["prev_price"])      / df["prev_price"].replace(0, np.nan)
    df["price_elasticity"] = pct_demand / pct_price.replace(0, np.nan)

    # Inventory velocity — units sold vs stock on hand
    df["inventory_velocity"] = (
        df["units_sold"] / df["current_stock"].replace(0, np.nan)
    )

    # Competitor price gap — positive means we are more expensive
    df["price_gap"] = df["price"] - df["competitor_price"]

    # Demand trend — rolling 7-day mean of PAST sales only (shift before rolling)
    df["demand_trend"] = (
        g["units_sold"]
        .transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    )

    # Target — next 7 days of sales
    # shift(-1) then rolling(7).sum() then shift(-6) gives the
    # 7-day forward window without including the current row
    df[TARGET] = (
        g["units_sold"]
        .transform(lambda x: x.shift(-1).rolling(7, min_periods=7).sum().shift(-6))
    )

    # Drop rows missing features or target
    df = df.dropna(subset=FEATURES + [TARGET])

    # Clip extreme elasticity values (outliers from near-zero price changes)
    df["price_elasticity"] = df["price_elasticity"].clip(-10, 10)

    return df


def train(df):
    X = df[FEATURES]
    y = df[TARGET]

    print(f"Dataset shape: {X.shape}")
    print(f"Target range: {y.min():.1f} – {y.max():.1f}")

    # Time-aware split — never shuffle time-series data
    split = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    # Try both models — pick the better one
    results = {}
    for name, m in [
        ("LinearRegression",  LinearRegression()),
        ("RandomForest",      RandomForestRegressor(n_estimators=100, random_state=42)),
    ]:
        m.fit(X_train, y_train)
        preds  = m.predict(X_test)
        mse    = mean_squared_error(y_test, preds)
        r2     = r2_score(y_test, preds)
        results[name] = {"model": m, "mse": mse, "r2": r2}
        print(f"{name:22s}  MSE={mse:.3f}  R²={r2:.3f}")

    # Pick winner
    best_name  = max(results, key=lambda k: results[k]["r2"])
    best       = results[best_name]
    best_model = best["model"]

    print(f"\nSelected: {best_name}  (R²={best['r2']:.3f})")

    if best["r2"] < 0.5:
        print("WARNING: R² below 0.5. Check data quality — do not proceed to optimizer.")
    else:
        print("Model quality acceptable. Saving...")
        joblib.dump(best_model, MODEL_OUT)
        print(f"Saved → {MODEL_OUT}")

        # Verify saved model has correct features
        loaded = joblib.load(MODEL_OUT)
        assert "units_sold" not in list(loaded.feature_names_in_), \
            "CRITICAL: units_sold still in saved model features!"
        print(f"Feature check passed: {list(loaded.feature_names_in_)}")

    return best_model, df


def save_features(df):
    """Save the clean feature dataset for the pricing engine to consume."""
    out = df[["product_id", "date", "cost_price"] + FEATURES].copy()
    out.to_csv(DATA_OUT, index=False)
    print(f"Saved features → {DATA_OUT}  ({len(out)} rows)")


if __name__ == "__main__":
    print("Step 1: Loading raw data from SQLite...")
    raw = load_raw(DB_PATH)
    print(f"Raw rows: {len(raw)}")

    print("\nStep 2: Engineering features...")
    df = engineer_features(raw)
    print(f"Clean rows after dropping NaN: {len(df)}")

    print("\nStep 3: Training models...")
    model, df = train(df)

    print("\nStep 4: Saving feature dataset...")
    save_features(df)

    print("\nDone. Run engine/run_pricing_engine.py next.")