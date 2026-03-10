def inventory_agent(velocity):
    # REMOVE the line: velocity = row['inventory_velocity']
    # Just use the variable 'velocity' passed into the function
    if velocity > 0.35:
        return 'increase_price'
    elif velocity < 0.10:
        return 'decrease_price'
    else:
        return 'hold_price'