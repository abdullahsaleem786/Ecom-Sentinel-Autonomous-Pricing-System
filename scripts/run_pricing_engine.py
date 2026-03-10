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


print("Loading pricing features dataset...")
df = pd.read_csv("data/processed/pricing_features.csv")


print("Loading trained ML model...")
model = joblib.load("models/demand_model.pkl")


feature_cols = [
    "units_sold",
    "price",
    "price_elasticity",
    "inventory_velocity",
    "price_gap",
    "demand_trend"
]


print("Predicting future demand...")
# Debugging the mismatch
print("Features model expects:", model.feature_names_in_)
print("Features you are providing:", feature_cols)

# Check for differences
missing = set(model.feature_names_in_) - set(feature_cols)
extra = set(feature_cols) - set(model.feature_names_in_)

if missing: print(f"Missing from your list: {missing}")
if extra: print(f"Extra in your list: {extra}")
# Automatically reorder df columns to match the model's training order
df_for_prediction = df[model.feature_names_in_]

# Use the reordered dataframe for prediction
df["predicted_units_next_7_days"] = model.predict(df_for_prediction)


print("\nRunning pricing agents...\n")


print("\nRunning pricing agents...\n")

for idx, row in df.iterrows():
    # 1. Prepare features for the demand agent
    # Using model.feature_names_in_ ensures the order is ALWAYS correct
    features = row[model.feature_names_in_].values
    
    # 2. Get signals by passing individual values from the current 'row'
    demand_signal = demand_agent(features)
    inventory_signal = inventory_agent(row['inventory_velocity'])  # Pass value, not Series
    competition_signal = competition_agent(row['price_gap'])        # Pass value, not Series
    risk_signal = risk_agent(row["demand_trend"])                  # Pass value, not Series

    # 3. Get the final decision from the pricing agent
    final_decision = pricing_agent(
        inventory_signal,
        competition_signal,
        risk_signal
    )

    # 4. Output results
    print(f"Product ID: {idx}")
    print(f"Demand Signal:      {demand_signal}")
    print(f"Inventory Signal:   {inventory_signal}")
    print(f"Competition Signal: {competition_signal}")
    print(f"Risk Signal:        {risk_signal}")
    print(f"Final Decision:     {final_decision}")
    print("-" * 40)