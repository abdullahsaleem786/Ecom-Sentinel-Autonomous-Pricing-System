import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ecom Sentinel Dashboard", layout="wide")

st.title("Ecom Sentinel - Autonomous Pricing Intelligence")

df = pd.read_csv("data/processed/pricing_revenue_simulation.csv")

# ---- KPIs ----

old_rev = df["old_revenue"].sum()
new_rev = df["new_revenue"].sum()
rev_change = new_rev - old_rev

c1, c2, c3 = st.columns(3)

c1.metric("Old Revenue", f"${old_rev:,.0f}")
c2.metric("New Revenue", f"${new_rev:,.0f}")
c3.metric("Revenue Change", f"${rev_change:,.0f}")

st.divider()

# ---- Decision Distribution ----

st.subheader("Pricing Decision Distribution")

decision_fig = px.pie(
    df,
    names="final_decision",
    title="Agent Pricing Decisions"
)

st.plotly_chart(decision_fig, use_container_width=True)

st.divider()

# ---- Revenue Change Distribution ----

st.subheader("Revenue Change per Product")

rev_fig = px.histogram(
    df,
    x="revenue_change",
    nbins=40,
    title="Revenue Change Distribution"
)

st.plotly_chart(rev_fig, use_container_width=True)

st.divider()

# ---- Top Gainers ----

st.subheader("Top Revenue Gains")

top_gain = df.sort_values("revenue_change", ascending=False).head(10)

st.dataframe(top_gain[[
    "product_id",
    "price",
    "new_price",
    "revenue_change"
]])

# ---- Top Losses ----

st.subheader("Top Revenue Losses")

top_loss = df.sort_values("revenue_change").head(10)

st.dataframe(top_loss[[
    "product_id",
    "price",
    "new_price",
    "revenue_change"
]])

st.divider()

# ---- Product Explorer ----

st.subheader("Product Explorer")

product = st.selectbox("Select Product ID", df["product_id"])

product_row = df[df["product_id"] == product]

st.write(product_row)