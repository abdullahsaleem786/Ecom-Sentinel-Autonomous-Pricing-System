# scripts/debug_agents.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from agents.demand_agent import demand_agent
from agents.inventory_agent import inventory_agent
from agents.competition_agent import competition_agent
from agents.risk_agent import risk_agent
from agents.pricing_agent import pricing_agent

features = pd.read_csv("data/processed/pricing_features.csv")
latest   = (
    features.sort_values("date")
    .groupby("product_id")
    .last()
    .reset_index()
)

print(f"{'Product':<10} {'base_demand':>12} {'price_ratio':>12} "
      f"{'price_gap':>10} {'elasticity':>11} "
      f"{'d_sig':<14} {'i_sig':<16} {'c_sig':<16} {'r_sig':<12} {'range'}")
print("-" * 130)

for _, row in latest.iterrows():
    d_sig = demand_agent(row["base_demand"])
    i_sig = inventory_agent(row["price_ratio"])
    c_sig = competition_agent(row["price_gap"])
    r_sig = risk_agent(row["price_elasticity"])
    rng   = pricing_agent(d_sig, i_sig, c_sig, r_sig)
    print(
        f"{row['product_id']:<10} {row['base_demand']:>12.2f} "
        f"{row['price_ratio']:>12.3f} {row['price_gap']:>10.2f} "
        f"{row['price_elasticity']:>11.3f} "
        f"{d_sig:<14} {i_sig:<16} {c_sig:<16} {r_sig:<12} {rng}"
    )