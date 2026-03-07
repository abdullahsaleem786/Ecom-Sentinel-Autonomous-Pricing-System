from agents.inventory_agent import inventory_agent

print(inventory_agent(0.40))  # expected: increase_price
print(inventory_agent(0.05))  # expected: decrease_price
print(inventory_agent(0.20))  # expected: hold_price