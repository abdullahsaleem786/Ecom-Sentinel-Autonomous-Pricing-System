def risk_agent(demand_trend_value):
    # Use the value directly
    if demand_trend_value < -0.5:
        return "high_risk"
    elif demand_trend_value < 0:
        return "medium_risk"
    else:
        return "low_risk"