import pandas as pd
import numpy as np

np.random.seed(42)

rows = 500

data = {
    "units_sold": np.random.randint(30, 120, rows),
    "price": np.random.uniform(20, 50, rows).round(2),
    "price_elasticity": np.random.uniform(-2, -0.5, rows),
    "inventory_velocity": np.random.uniform(0.2, 1.5, rows),
    "price_gap": np.random.uniform(-5, 5, rows),
    "demand_trend": np.random.uniform(-0.3, 0.3, rows),
}

df = pd.DataFrame(data)

df["units_sold_next_7_days"] = (
    df["units_sold"]
    + df["demand_trend"] * 50
    - df["price"] * 0.5
    + np.random.normal(0, 5, rows)
)

df["units_sold_next_7_days"] = df["units_sold_next_7_days"].round().astype(int)

df.to_csv("data/processed/training_dataset.csv", index=False)

print("Training dataset generated.")
print(df.head())