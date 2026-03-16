import pandas as pd

def optimize_price(row, model, feature_cols):

    base_price = row["price"]

    # candidate prices
    multipliers = [0.8, 0.9, 1.0, 1.1, 1.2]

    best_price = base_price
    best_revenue = 0

    candidate_rows = []
    candidate_prices = []

    for m in multipliers:
        new_price = base_price * m

        features = row.copy()
        features["price"] = new_price

        candidate_rows.append(features[feature_cols])
        candidate_prices.append(new_price)

    # Build a DataFrame so sklearn receives named columns in training order.
    X_candidates = pd.DataFrame(candidate_rows, columns=feature_cols)
    predicted_demands = model.predict(X_candidates)

    for new_price, predicted_demand in zip(candidate_prices, predicted_demands):
        revenue = new_price * predicted_demand

        if revenue > best_revenue:
            best_revenue = revenue
            best_price = new_price

    return best_price, best_revenue