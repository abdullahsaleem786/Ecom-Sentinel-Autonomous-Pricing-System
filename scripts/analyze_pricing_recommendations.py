import pandas as pd

df = pd.read_csv("data/processed/final_pricing_recommendations.csv")

print("\n===== PRICING SUMMARY =====")

print("\nTotal products analyzed:", len(df))

print("\nDecision Distribution:")
print(df["final_decision"].value_counts())

print("\nAverage Predicted Demand:", round(df["predicted_demand"].mean(), 2))

print("\nHigh Demand Products (Top 5):")
print(df.sort_values("predicted_demand", ascending=False)[
    ["product_id", "predicted_demand"]
].head())

print("\nLow Demand Products (Top 5):")
print(df.sort_values("predicted_demand")[
    ["product_id", "predicted_demand"]
].head())