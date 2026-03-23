# engine/run_optimizer.py
import pandas as pd

# These are the ONLY features the retrained model will use — no units_sold
OPTIMIZER_FEATURES = [
    "price",
    "price_elasticity",
    "inventory_velocity",
    "price_gap",
    "demand_trend"
]

MULTIPLIERS = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]
MIN_MARGIN_PCT = 0.08


def optimize_price(row, model, cost_price: float, multiplier_range: tuple = None):
    """
    Search candidate prices and return the one that maximises
    revenue = price × predicted_demand.

    Key fix: only 'price' changes per candidate.
    All other features stay fixed — they reflect current market state,
    not the hypothetical price being tested.

    Args:
        row:              pandas Series — current product feature row
        model:            trained demand model (must NOT have units_sold as feature)
        cost_price:       unit cost — enforces hard margin floor
        multiplier_range: (min_mult, max_mult) from pricing_agent, optional

    Returns:
        (best_price, best_revenue, best_demand, decision)
    """
    base_price  = row["price"]
    floor_price = cost_price * (1 + MIN_MARGIN_PCT)

    # Narrow multiplier space if agents provided a range
    if multiplier_range:
        lo, hi = multiplier_range
        multipliers = [m for m in MULTIPLIERS if lo <= m <= hi]
        if not multipliers:
            multipliers = [1.0]  # agents conflicted — hold
    else:
        multipliers = MULTIPLIERS

    # Build all candidate feature vectors in one batch
    candidate_prices = []
    candidate_rows   = []

    for mult in multipliers:
        candidate_price = round(base_price * mult, 2)

        # Hard floor — never price below cost + margin
        if candidate_price < floor_price:
            continue

        # Only price changes — everything else is current market state
        candidate_features = {
            "price":              candidate_price,
            "price_elasticity":   row["price_elasticity"],
            "inventory_velocity": row["inventory_velocity"],
            "price_gap":          row["price_gap"],
            "demand_trend":       row["demand_trend"],
        }
        candidate_rows.append(candidate_features)
        candidate_prices.append(candidate_price)

    # All candidates below floor — hold current price
    if not candidate_rows:
        feat_df = pd.DataFrame([{
            "price":              base_price,
            "price_elasticity":   row["price_elasticity"],
            "inventory_velocity": row["inventory_velocity"],
            "price_gap":          row["price_gap"],
            "demand_trend":       row["demand_trend"],
        }])[OPTIMIZER_FEATURES]
        demand = max(0, model.predict(feat_df)[0])
        return base_price, round(base_price * demand, 2), round(demand, 2), "hold"

    # Batch predict — one call, not N calls in a loop
    X_candidates = pd.DataFrame(candidate_rows)[OPTIMIZER_FEATURES]
    predicted_demands = model.predict(X_candidates)

    # Find the revenue-maximising candidate
    best_price   = base_price
    best_revenue = -1
    best_demand  = 0

    for price, demand in zip(candidate_prices, predicted_demands):
        demand  = max(0, demand)  # no negative demand
        revenue = price * demand
        if revenue > best_revenue:
            best_revenue = revenue
            best_price   = price
            best_demand  = demand

    decision = (
        "increase" if best_price > base_price
        else "decrease" if best_price < base_price
        else "hold"
    )

    return (
        round(best_price, 2),
        round(best_revenue, 2),
        round(best_demand, 2),
        decision
    )