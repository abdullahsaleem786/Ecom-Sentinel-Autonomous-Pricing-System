def pricing_agent(inventory_decision, competition_decision, risk_status):

    # Risk protection first
    if risk_status == "high_risk":
        return "hold_price"

    # If both agents want increase
    if inventory_decision == "increase_price" and competition_decision == "increase_price":
        return "increase_price"

    # If competition says decrease
    if competition_decision == "decrease_price":
        return "decrease_price"

    # If inventory says decrease
    if inventory_decision == "decrease_price":
        return "decrease_price"

    return "hold_price"