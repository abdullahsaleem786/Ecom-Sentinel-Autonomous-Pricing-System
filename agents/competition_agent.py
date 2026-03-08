def competition_agent(price_gap):

    if price_gap > 3:
        return "decrease_price"

    elif price_gap < -3:
        return "increase_price"

    else:
        return "hold_price"