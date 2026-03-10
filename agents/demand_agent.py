import joblib
import numpy as np

# Load trained model
model = joblib.load("models/demand_model.pkl")

def demand_agent(features):
    
    prediction = model.predict([features])[0]

    if prediction > 100:
        return "high_demand"
    elif prediction < 50:
        return "low_demand"
    else:
        return "stable_demand"