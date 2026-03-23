# engine/run_optimizer.py
import pandas as pd
import numpy as np

MULTIPLIERS = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]
MIN_MARGIN  = 0.08


def predict_demand(curves: dict, product_id: str, price: float) -> float:
    """
    Predict demand for a product at a given price using fitted curve.
    demand = a * price^b
    """
    if product_id not in curves:
        return 0.0
    c = curves[product_id]
    return max(0.0, c["a"] * (price ** c["b"]))


def optimize_price(row, model, cost_price: float, multiplier_range: tuple = None):
    """
    model is now a dict of per-product demand curves, not an sklearn model.
    """
    product_id  = row["product_id"]
    base_price  = float(row["price"])
    floor_price = cost_price * (1 + MIN_MARGIN)

    multipliers = MULTIPLIERS
    if multiplier_range:
        lo, hi      = multiplier_range
        multipliers = [m for m in MULTIPLIERS if lo <= m <= hi] or [1.0]

    best_price   = base_price
    best_revenue = -1
    best_demand  = 0

    for mult in multipliers:
        candidate_price = round(base_price * mult, 2)
        if candidate_price < floor_price:
            continue

        # 7-day demand prediction
        daily_demand   = predict_demand(model, product_id, candidate_price)
        weekly_demand  = daily_demand * 7
        revenue        = candidate_price * weekly_demand

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