# engine/run_optimizer.py
import numpy as np

MULTIPLIERS    = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]
MIN_MARGIN     = 0.08
MAX_DISCOUNT   = 0.10   # never drop more than 10% in one cycle
MAX_INCREASE   = 0.20   # never raise more than 20% in one cycle


def predict_demand(curves: dict, product_id: str, price: float) -> float:
    if product_id not in curves:
        return 0.0
    c = curves[product_id]
    return max(0.0, c["a"] * (price ** c["b"]))


def optimize_price(row, model, cost_price: float, multiplier_range: tuple = None):
    product_id  = row["product_id"]
    base_price  = float(row["price"])
    floor_price = max(
        cost_price * (1 + MIN_MARGIN),
        base_price * (1 - MAX_DISCOUNT)   # never drop more than 10%
    )
    ceiling_price = base_price * (1 + MAX_INCREASE)

    multipliers = MULTIPLIERS
    if multiplier_range:
        lo, hi      = multiplier_range
        multipliers = [m for m in MULTIPLIERS if lo <= m <= hi] or [1.0]

    # Current revenue is the floor — only move if it genuinely improves
    current_weekly_demand = predict_demand(model, product_id, base_price) * 7
    current_revenue       = base_price * current_weekly_demand

    best_price   = base_price
    best_revenue = current_revenue
    best_demand  = current_weekly_demand

    for mult in multipliers:
        candidate_price = round(base_price * mult, 2)

        # Apply hard bounds
        if candidate_price < floor_price:
            continue
        if candidate_price > ceiling_price:
            continue

        weekly_demand = predict_demand(model, product_id, candidate_price) * 7
        revenue       = candidate_price * weekly_demand

        if revenue > best_revenue:
            best_revenue = revenue
            best_price   = candidate_price
            best_demand  = weekly_demand

    decision = (
        "increase" if best_price > base_price
        else "decrease" if best_price < base_price
        else "hold"
    )

    return (
        round(best_price, 2),
        round(best_revenue, 2),
        round(best_demand, 2),
        decision,
    )