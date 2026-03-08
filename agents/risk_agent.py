def risk_agent(price_elasticity, demand_trend):

    if price_elasticity < -2:
        return "high_risk"

    elif demand_trend < -0.03:
        return "falling_demand"

    else:
        return "stable"