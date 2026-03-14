import pandas as pd

print("Loading pricing recommendations...")

df = pd.read_csv("data/processed/final_pricing_recommendations.csv")

print("Loading pricing features...")

features = pd.read_csv("data/processed/pricing_features.csv")

# Merge both datasets
df = df.merge(features, left_on="product_id", right_index=True)

# Old revenue
df["old_revenue"] = df["price"] * df["units_sold"]


def apply_price_change(row):

    if row["final_decision"] == "increase_price":
        return row["price"] * 1.02   # 5% increase

    elif row["final_decision"] == "lower_price":
        return row["price"] * 0.98   # 5% decrease

    else:
        return row["price"]


df["new_price"] = df.apply(apply_price_change, axis=1)

def simulate_demand(row):

    price_change_pct = (row["new_price"] - row["price"]) / row["price"]

    demand_change_pct = row["price_elasticity"] * price_change_pct

    new_demand = row["predicted_demand"] * (1 + demand_change_pct)

    return max(new_demand, 0)


df["new_units_sold"] = df.apply(simulate_demand, axis=1)

# New revenue
df["new_revenue"] = df["new_price"] * df["new_units_sold"]

df["revenue_change"] = df["new_revenue"] - df["old_revenue"]


print("\n===== REVENUE IMPACT SUMMARY =====\n")

print("Total Old Revenue:", round(df["old_revenue"].sum(),2))
print("Total New Revenue:", round(df["new_revenue"].sum(),2))

improvement = df["new_revenue"].sum() - df["old_revenue"].sum()

print("Revenue Change:", round(improvement,2))


print("\nTop Revenue Gains")

print(
    df.sort_values("revenue_change", ascending=False)[
        ["product_id","revenue_change"]
    ].head(5)
)

print("\nTop Revenue Losses")

print(
    df.sort_values("revenue_change")[
        ["product_id","revenue_change"]
    ].head(5)
)

df.to_csv("data/processed/pricing_revenue_simulation.csv", index=False)

print("\nSimulation results saved.")