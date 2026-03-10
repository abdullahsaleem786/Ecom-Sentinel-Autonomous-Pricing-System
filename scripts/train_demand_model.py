import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import joblib

# Load dataset
df = pd.read_csv("data/processed/training_dataset.csv")

features = [
    "price",
    "units_sold",
    "price_elasticity",
    "inventory_velocity",
    "price_gap",
    "demand_trend"
]

X = df[features]
y = df["units_sold_next_7_days"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)
print("Model R2:", r2_score(y_test, pred))

# Save model
joblib.dump(model, "models/demand_model.pkl")

print("Model saved successfully.")