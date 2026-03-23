# scripts/check_optimizer.py
import pandas as pd
import joblib

curves   = joblib.load("models/demand_model.pkl")
features = pd.read_csv("data/processed/pricing_features.csv")

latest = features.sort_values("date").groupby("product_id").last().reset_index()
row    = latest.iloc[0]

product_id  = row["product_id"]
base_price  = float(row["price"])
c           = curves[product_id]

print(f"Product:      {product_id}")
print(f"Current price: {base_price:.2f}")
print(f"Curve a={c['a']:.4f}  b={c['b']:.4f}  R²={c['r2']:.4f}")
print(f"Elasticity b={c['b']:.4f}  (negative = demand falls as price rises)")
print()
print(f"{'Price':>10} {'Pred Demand':>14} {'Revenue':>12}")

for mult in [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]:
    p      = round(base_price * mult, 2)
    demand = max(0, c["a"] * (p ** c["b"])) * 7
    print(f"{p:>10.2f} {demand:>14.2f} {p * demand:>12.2f}")