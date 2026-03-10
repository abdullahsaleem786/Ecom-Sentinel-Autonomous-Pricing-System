def competition_agent(price_gap):
    # Use 'price_gap' directly
    if price_gap > 3:
        return 'lower_price'
    elif price_gap < -3:
        return 'raise_price'
    else:
        return 'maintain'