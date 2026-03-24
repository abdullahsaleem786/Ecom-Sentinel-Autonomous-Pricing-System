# scripts/simulate_revenue_impact.py
import pandas as pd
import joblib

print("Loading optimization results...")
results = pd.read_csv("data/processed/final_pricing_recommendations.csv")

print("Loading pricing features and demand curves...")
features = pd.read_csv("data/processed/pricing_features.csv")
curves   = joblib.load("models/demand_model.pkl")

# Get most recent row per product
latest_features = (
    features.sort_values("date")
    .groupby("product_id")
    .last()
    .reset_index()[["product_id", "base_demand"]]
)

df = results.merge(latest_features, on="product_id")

# Baseline revenue — use demand curve at current price, not flat base_demand
# This is the true apples-to-apples comparison
def current_revenue(row):
    pid = row["product_id"]
    if pid not in curves:
        return row["current_price"] * row["base_demand"] * 7
    c = curves[pid]
    daily_demand  = max(0, c["a"] * (row["current_price"] ** c["b"]))
    weekly_demand = daily_demand * 7
    return row["current_price"] * weekly_demand

df["old_revenue"] = df.apply(current_revenue, axis=1)

# New revenue comes directly from optimizer
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

# Sanity check — optimizer should never return worse revenue than holding
losses = df[df["revenue_change"] < -1]
if len(losses) > 0:
    print(f"\nWARNING: {len(losses)} products show revenue loss > $1")
    print(losses[["product_id", "current_price", "optimal_price", "revenue_change"]].to_string(index=False))
else:
    print("\nSanity check passed: all products at or above baseline revenue")

df.to_csv("data/processed/pricing_revenue_simulation.csv", index=False)
print("\nSaved → data/processed/pricing_revenue_simulation.csv")