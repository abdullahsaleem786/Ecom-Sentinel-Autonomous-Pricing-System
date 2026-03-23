# scripts/run_pricing_engine.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import joblib
from agents.demand_agent import demand_agent
from agents.inventory_agent import inventory_agent
from agents.competition_agent import competition_agent
from agents.risk_agent import risk_agent
from agents.pricing_agent import pricing_agent
from engine.run_optimizer import optimize_price

print("Loading pricing features dataset...")
df = pd.read_csv("data/processed/pricing_features.csv")

print("Loading trained ML model...")
model = joblib.load("models/demand_model.pkl")

# No units_sold — model was retrained without it
FEATURE_COLS = list(model.feature_names_in_)
print(f"Model features: {FEATURE_COLS}")

# cost_price column comes from retrain script — verify it exists
if "cost_price" not in df.columns:
    df["cost_price"] = df["price"] * 0.60
    print("WARNING: cost_price missing. Estimating as 60% of price.")

# Get one row per product — most recent date
latest = (
    df.sort_values("date")
    .groupby("product_id")
    .last()
    .reset_index()
)

print(f"\nOptimizing prices for {len(latest)} products...\n")

final_results = []

for _, row in latest.iterrows():
    # Agent signals
    d_signal = demand_agent(row["demand_trend"])
    i_signal = inventory_agent(row["inventory_velocity"])
    c_signal = competition_agent(row["price_gap"])
    r_signal = risk_agent(row["demand_trend"])

    # Agents return multiplier range
    mult_range = pricing_agent(d_signal, i_signal, c_signal, r_signal)

    # Optimizer finds best price within that range
    best_price, best_revenue, best_demand, decision = optimize_price(
        row=row,
        model=model,
        cost_price=float(row["cost_price"]),
        multiplier_range=mult_range,
    )

    final_results.append({
        "product_id":         row["product_id"],
        "current_price":      round(float(row["price"]), 2),
        "optimal_price":      best_price,
        "predicted_demand":   best_demand,
        "optimal_revenue":    best_revenue,
        "decision":           decision,
        "demand_signal":      d_signal,
        "inventory_signal":   i_signal,
        "competition_signal": c_signal,
        "risk_signal":        r_signal,
    })

results_df = pd.DataFrame(final_results)

print("Decision distribution:")
print(results_df["decision"].value_counts().to_string())
print(f"\nAvg price change: {((results_df['optimal_price'] - results_df['current_price']) / results_df['current_price'] * 100).mean():.2f}%")

results_df.to_csv("data/processed/final_pricing_recommendations.csv", index=False)
print("\nSaved → data/processed/final_pricing_recommendations.csv")