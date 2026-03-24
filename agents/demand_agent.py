# agents/demand_agent.py

def demand_agent(base_demand):
    """
    base_demand = average daily units sold for this product.
    Calibrated to actual data range: 42–118 units/day.
    """
    if base_demand > 90:
        return "high_demand"
    elif base_demand < 55:
        return "low_demand"
    else:
        return "normal_demand"