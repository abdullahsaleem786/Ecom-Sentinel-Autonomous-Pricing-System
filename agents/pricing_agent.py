# agents/pricing_agent.py

def pricing_agent(demand_signal, inventory_signal, competition_signal, risk_signal):
    """
    Combines agent signals into a (min_multiplier, max_multiplier) range.
    The optimizer searches within this range for the best price.
    Agents constrain the search — they do NOT make the final call.
    """
    lo, hi = 0.80, 1.20

    # Demand signal
    if demand_signal == "high_demand":
        lo = max(lo, 0.95)
    elif demand_signal == "low_demand":
        hi = min(hi, 1.05)

    # Inventory signal
    if inventory_signal == "increase_price":
        lo = max(lo, 1.00)
    elif inventory_signal == "lower_price":
        hi = min(hi, 1.00)

    # Competition signal
    if competition_signal == "increase_price":
        lo = max(lo, 0.95)
    elif competition_signal == "lower_price":
        hi = min(hi, 1.00)

    # Risk signal — tighten range
    if risk_signal == "high_risk":
        lo = max(lo, 0.92)
        hi = min(hi, 1.08)

    # Agents conflicted — hold tight
    if lo >= hi:
        return (0.97, 1.03)

    return (round(lo, 2), round(hi, 2))