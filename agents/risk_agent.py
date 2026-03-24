# agents/risk_agent.py

def risk_agent(price_elasticity):
    """
    price_elasticity is negative for normal goods (demand falls as price rises).
    More negative = more elastic = more risky to raise price.
    
    b < -1.5 : highly elastic — customers very sensitive to price changes
    b > -0.8 : inelastic — customers less sensitive, safer to adjust price
    """
    if price_elasticity < -1.5:
        return "high_risk"     # elastic — large demand drop if price raised
    elif price_elasticity < -0.8:
        return "medium_risk"   # moderate sensitivity
    else:
        return "low_risk"      # inelastic — safe to move price