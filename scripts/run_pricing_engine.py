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


# 1. Create a list to store the results
final_results = []

for idx, row in df.iterrows():
    # Pass the row as a DataFrame slice to keep feature names and avoid the UserWarning
    # [[...]] ensures it stays a DataFrame, not a Series
    current_features = df.loc[[idx], model.feature_names_in_]
    
    # Get demand prediction
    predicted_demand = model.predict(current_features)[0]

    # 2. Call agents with individual values
    inventory_signal = inventory_agent(row['inventory_velocity'])
    competition_signal = competition_agent(row['price_gap'])
    risk_signal = risk_agent(row['demand_trend'])
    
    # 3. Get the final decision
    final_decision = pricing_agent(
        inventory_signal,
        competition_signal,
        risk_signal
    )

    # 4. Store for the CSV
    final_results.append({
        "product_id": idx,
        "predicted_demand": predicted_demand,
        "inventory_signal": inventory_signal,
        "competition_signal": competition_signal,
        "risk_signal": risk_signal,
        "final_decision": final_decision
    })

# 5. Save the results to a CSV
results_df = pd.DataFrame(final_results)
output_path = "data/processed/final_pricing_recommendations.csv"
results_df.to_csv(output_path, index=False)

print(f"Success! Recommendations saved to: {output_path}")