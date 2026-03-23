# scripts/simulate_revenue_impact.py
import pandas as pd

print("Loading optimization results...")
results = pd.read_csv("data/processed/final_pricing_recommendations.csv")

print("Loading pricing features for baseline demand...")
features = pd.read_csv("data/processed/pricing_features.csv")

# Get most recent row per product — need demand_trend as baseline demand proxy
latest_features = (
    features.sort_values("date")
    .groupby("product_id")
    .last()
    .reset_index()[["product_id", "demand_trend"]]
)

df = results.merge(latest_features, on="product_id")

# Baseline revenue = current price × baseline demand
df["old_revenue"] = df["current_price"] * df["demand_trend"]

# New revenue = optimizer output directly
df["new_revenue"] = df["optimal_price"] * df["predicted_demand"]

df["revenue_change"] = df["new_revenue"] - df["old_revenue"]
df["revenue_change_pct"] = (
    df["revenue_change"] / df["old_revenue"].replace(0, 1) * 100
).round(2)
df["price_change_pct"] = (
    (df["optimal_price"] - df["current_price"]) / df["current_price"] * 100
).round(2)

print("\n===== REVENUE IMPACT SUMMARY =====\n")
print(f"Products evaluated:   {len(df)}")
print(f"Old total revenue:   ${df['old_revenue'].sum():,.2f}")
print(f"New total revenue:   ${df['new_revenue'].sum():,.2f}")
print(f"Revenue change:      ${df['revenue_change'].sum():,.2f}")
print(f"Revenue lift:        {df['revenue_change'].sum() / df['old_revenue'].sum() * 100:+.2f}%")

print("\nDecision distribution:")
print(df["decision"].value_counts().to_string())

print("\nTop 5 revenue gains:")
print(
    df.sort_values("revenue_change", ascending=False)[
        ["product_id", "current_price", "optimal_price", "price_change_pct", "revenue_change"]
    ].head(5).to_string(index=False)
)

print("\nTop 5 revenue losses:")
print(
    df.sort_values("revenue_change")[
        ["product_id", "current_price", "optimal_price", "price_change_pct", "revenue_change"]
    ].head(5).to_string(index=False)
)

df.to_csv("data/processed/pricing_revenue_simulation.csv", index=False)
print("\nSaved → data/processed/pricing_revenue_simulation.csv")