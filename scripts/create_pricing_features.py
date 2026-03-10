import pandas as pd

df = pd.read_csv("data/processed/training_dataset.csv")

df.to_csv("data/processed/pricing_features.csv", index=False)

print("Pricing features file created.")