# agents/pricing_agent.py

def pricing_agent(demand_signal, inventory_signal, competition_signal, risk_signal):
    """
    Combines agent signals into a (min_multiplier, max_multiplier) range.
    Optimizer searches within this range for revenue-maximising price.
    """
    lo, hi = 0.80, 1.20

    # Demand signal
    if demand_signal == "high_demand":
        lo = max(lo, 0.95)    # strong demand — don't discount
    elif demand_signal == "low_demand":
        hi = min(hi, 1.05)    # weak demand — don't raise aggressively

    # Inventory signal
    if inventory_signal == "increase_price":
        lo = max(lo, 0.95)    # moving fast — safe to hold or raise
    elif inventory_signal == "lower_price":
        hi = min(hi, 1.00)    # moving slow — don't raise further

    # Competition signal
    if competition_signal == "raise_price":
        lo = max(lo, 0.95)    # we're cheaper than market — safe to raise
    elif competition_signal == "lower_price":
        hi = min(hi, 1.00)    # we're more expensive — don't raise further

    # Risk signal — controls how wide the search range can be
    if risk_signal == "high_risk":
        lo = max(lo, 0.90)
        hi = min(hi, 1.10)    # elastic product — limit price movement
    elif risk_signal == "medium_risk":
        lo = max(lo, 0.85)
        hi = min(hi, 1.15)
    # low_risk — full range allowed

    # Agents fully conflicted — hold tight
    if lo >= hi:
        return (0.97, 1.03)

    return (round(lo, 2), round(hi, 2))