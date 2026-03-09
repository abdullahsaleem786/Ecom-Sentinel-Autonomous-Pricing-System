from agents.inventory_agent import inventory_agent
from agents.competition_agent import competition_agent
from agents.risk_agent import risk_agent
from agents.pricing_agent import pricing_agent


inventory = inventory_agent(0.40)
competition = competition_agent(-4)
risk = risk_agent(-1, 0.02)

decision = pricing_agent(inventory, competition, risk)

print("Inventory Agent:", inventory)
print("Competition Agent:", competition)
print("Risk Agent:", risk)
print("Final Decision:", decision)