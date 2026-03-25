# dashboard/pricing_dashboard.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np

st.set_page_config(
    page_title="E-Com Sentinel",
    page_icon="sentinel",
    layout="wide"
)

# ── Data loading ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    sim      = pd.read_csv("data/processed/pricing_revenue_simulation.csv")
    features = pd.read_csv("data/processed/pricing_features.csv")
    return sim, features

@st.cache_resource
def load_curves():
    return joblib.load("models/demand_model.pkl")

sim, features = load_data()
curves        = load_curves()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("E-Com Sentinel — Autonomous Pricing Intelligence")
st.caption("Phase 6 — Price Optimization Engine")
st.divider()

# ── KPI Cards ───────────────────────────────────────────────────────────────
old_rev   = sim["old_revenue"].sum()
new_rev   = sim["new_revenue"].sum()
rev_lift  = (new_rev - old_rev) / old_rev * 100
n_dec     = (sim["decision"] == "decrease").sum()
n_inc     = (sim["decision"] == "increase").sum()
n_hold    = (sim["decision"] == "hold").sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Baseline Revenue",  f"${old_rev:,.0f}")
k2.metric("Optimized Revenue", f"${new_rev:,.0f}", f"+${new_rev - old_rev:,.0f}")
k3.metric("Revenue Lift",      f"{rev_lift:+.2f}%")
k4.metric("Products Decreased", str(n_dec))
k5.metric("Products Increased", str(n_inc))

st.divider()

# ── Row 1: Decision distribution + Price change bar ─────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Decision distribution")
    decision_counts = sim["decision"].value_counts().reset_index()
    decision_counts.columns = ["decision", "count"]
    color_map = {"decrease": "#EF9F27", "increase": "#1D9E75", "hold": "#888780"}
    fig_pie = px.pie(
        decision_counts,
        names="decision",
        values="count",
        color="decision",
        color_discrete_map=color_map,
        hole=0.45,
    )
    fig_pie.update_traces(textinfo="label+percent")
    fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Price change per product (%)")
    sim_sorted = sim.sort_values("price_change_pct")
    colors     = [
        "#1D9E75" if x > 0 else "#EF9F27" if x < 0 else "#888780"
        for x in sim_sorted["price_change_pct"]
    ]
    fig_bar = go.Figure(go.Bar(
        x=sim_sorted["product_id"],
        y=sim_sorted["price_change_pct"],
        marker_color=colors,
    ))
    fig_bar.update_layout(
        xaxis_title="Product",
        yaxis_title="Price change (%)",
        margin=dict(t=20, b=40),
        yaxis=dict(zeroline=True, zerolinewidth=1),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Row 2: Revenue change per product ───────────────────────────────────────
st.subheader("Revenue change per product ($)")
sim_rev = sim.sort_values("revenue_change", ascending=False)
colors_rev = [
    "#1D9E75" if x >= 0 else "#E24B4A"
    for x in sim_rev["revenue_change"]
]
fig_rev = go.Figure(go.Bar(
    x=sim_rev["product_id"],
    y=sim_rev["revenue_change"],
    marker_color=colors_rev,
    text=[f"${v:,.0f}" for v in sim_rev["revenue_change"]],
    textposition="outside",
))
fig_rev.update_layout(
    xaxis_title="Product",
    yaxis_title="Revenue change ($)",
    margin=dict(t=20, b=40),
    yaxis=dict(zeroline=True, zerolinewidth=1),
)
st.plotly_chart(fig_rev, use_container_width=True)

st.divider()

# ── Row 3: Product explorer ──────────────────────────────────────────────────
st.subheader("Product explorer")

product_id = st.selectbox(
    "Select product",
    sorted(sim["product_id"].unique())
)

row = sim[sim["product_id"] == product_id].iloc[0]

# Product KPIs
p1, p2, p3, p4, p5 = st.columns(5)
p1.metric("Current price",  f"${row['current_price']:.2f}")
p2.metric("Optimal price",  f"${row['optimal_price']:.2f}",
          f"{row['price_change_pct']:+.1f}%")
p3.metric("Predicted demand", f"{row['predicted_demand']:.0f} units")
p4.metric("Optimized revenue", f"${row['optimal_revenue']:,.0f}")
p5.metric("Revenue change",   f"${row['revenue_change']:,.0f}",
          f"{row['revenue_change_pct']:+.1f}%")

# Agent signals
st.markdown("**Agent signals**")
a1, a2, a3, a4 = st.columns(4)
a1.info(f"Demand: `{row['demand_signal']}`")
a2.info(f"Inventory: `{row['inventory_signal']}`")
a3.info(f"Competition: `{row['competition_signal']}`")
a4.info(f"Risk: `{row['risk_signal']}`")

st.divider()

# ── Demand curve visualization ───────────────────────────────────────────────
st.subheader(f"Demand curve — {product_id}")
st.caption("Shows how predicted demand and revenue respond to price. "
           "The optimizer picks the price that maximises the revenue curve.")

if product_id in curves:
    c       = curves[product_id]
    cur_p   = float(row["current_price"])
    opt_p   = float(row["optimal_price"])

    price_range = np.linspace(cur_p * 0.70, cur_p * 1.30, 200)
    demands     = [max(0, c["a"] * (p ** c["b"])) * 7 for p in price_range]
    revenues    = [p * d for p, d in zip(price_range, demands)]

    fig_curve = go.Figure()

    # Demand line
    fig_curve.add_trace(go.Scatter(
        x=list(price_range), y=demands,
        name="Predicted demand (7-day)",
        line=dict(color="#378ADD", width=2),
        yaxis="y1",
    ))

    # Revenue line
    fig_curve.add_trace(go.Scatter(
        x=list(price_range), y=revenues,
        name="Projected revenue",
        line=dict(color="#1D9E75", width=2),
        yaxis="y2",
    ))

    # Current price marker
    cur_demand  = max(0, c["a"] * (cur_p ** c["b"])) * 7
    cur_revenue = cur_p * cur_demand
    fig_curve.add_trace(go.Scatter(
        x=[cur_p], y=[cur_revenue],
        name="Current price",
        mode="markers",
        marker=dict(color="#888780", size=12, symbol="circle"),
        yaxis="y2",
    ))

    # Optimal price marker
    opt_demand  = max(0, c["a"] * (opt_p ** c["b"])) * 7
    opt_revenue = opt_p * opt_demand
    fig_curve.add_trace(go.Scatter(
        x=[opt_p], y=[opt_revenue],
        name="Optimal price",
        mode="markers",
        marker=dict(color="#EF9F27", size=12, symbol="star"),
        yaxis="y2",
    ))

    fig_curve.update_layout(
        xaxis_title="Price ($)",
        yaxis=dict(title="Demand (units / 7 days)", side="left"),
        yaxis2=dict(title="Revenue ($)", side="right", overlaying="y"),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=20, b=60),
    )
    st.plotly_chart(fig_curve, use_container_width=True)

    st.caption(
        f"Curve fit: demand = {c['a']:.2f} × price^{c['b']:.4f} "
        f"(R²={c['r2']:.3f}, elasticity={c['b']:.3f})"
    )
else:
    st.warning("No demand curve available for this product.")

st.divider()

# ── Full results table ───────────────────────────────────────────────────────
st.subheader("Full optimization results")
st.dataframe(
    sim[[
        "product_id", "current_price", "optimal_price",
        "price_change_pct", "predicted_demand",
        "old_revenue", "new_revenue", "revenue_change",
        "revenue_change_pct", "decision",
        "demand_signal", "inventory_signal",
        "competition_signal", "risk_signal",
    ]].sort_values("revenue_change", ascending=False),
    use_container_width=True,
    hide_index=True,
)