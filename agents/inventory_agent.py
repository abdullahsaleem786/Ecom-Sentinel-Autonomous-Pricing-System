def inventory_agent(inventory_velocity):
    if inventory_velocity>0.35:
        return 'increase_price'
    elif inventory_velocity<0.10:
        return 'decrease_price'
    else:
        return 'hold_price'