# agents/inventory_agent.py

def inventory_agent(price_ratio):
    """
    price_ratio = current_price / avg_price for this product.
    > 1.0 means we are currently priced above our own average.
    < 1.0 means we are currently priced below our own average.
    
    High price ratio = stock likely moving slowly = consider discounting.
    Low price ratio = stock moving fast = safe to increase.
    """
    if price_ratio < 0.93:
        return "increase_price"   # priced below average — room to raise
    elif price_ratio > 1.07:
        return "lower_price"      # priced above average — stock may pile up
    else:
        return "hold_price"       # near average — neutral