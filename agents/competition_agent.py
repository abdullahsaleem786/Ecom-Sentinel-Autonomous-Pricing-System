# agents/competition_agent.py

def competition_agent(price_gap):
    """
    price_gap = our_price - competitor_price.
    Positive = we are more expensive than competitor.
    Negative = we are cheaper than competitor.
    Calibrated to actual data range: -4.58 to +9.07.
    """
    if price_gap > 3:
        return "lower_price"   # we are significantly more expensive
    elif price_gap < -3:
        return "raise_price"   # we are significantly cheaper — room to raise
    else:
        return "maintain"      # competitive parity