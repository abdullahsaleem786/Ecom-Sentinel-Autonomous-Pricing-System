def demand_agent(predicted_demand):

    if predicted_demand > 80:
        return "high_demand"

    elif predicted_demand < 30:
        return "low_demand"

    else:
        return "normal_demand"