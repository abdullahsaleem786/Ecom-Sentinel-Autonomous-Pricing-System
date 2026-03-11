def pricing_agent(demand_signal, inventory_signal, competition_signal, risk_signal):

    score = 0

    # Demand signal
    if demand_signal == "high_demand":
        score += 2
    elif demand_signal == "low_demand":
        score -= 2

    # Inventory signal
    if inventory_signal == "increase_price":
        score += 1
    elif inventory_signal == "lower_price":
        score -= 1

    # Competition signal
    if competition_signal == "increase_price":
        score += 1
    elif competition_signal == "lower_price":
        score -= 1

    # Risk signal
    if risk_signal == "high_risk":
        score -= 1

    # Final decision
    if score >= 2:
        return "increase_price"
    elif score <= -2:
        return "lower_price"
    else:
        return "hold_price"