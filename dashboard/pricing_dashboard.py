import streamlit as st
import pandas as pd

st.title("Ecom Sentinel Pricing Intelligence Dashboard")

st.write("Multi-Agent Pricing System Overview")

# Load data
df = pd.read_csv("data/processed/pricing_revenue_simulation.csv")


# Summary metrics
total_old_revenue = df["old_revenue"].sum()
total_new_revenue = df["new_revenue"].sum()
revenue_change = total_new_revenue - total_old_revenue

col1, col2, col3 = st.columns(3)

col1.metric("Old Revenue", f"{total_old_revenue:,.2f}")
col2.metric("New Revenue", f"{total_new_revenue:,.2f}")
col3.metric("Revenue Change", f"{revenue_change:,.2f}")

st.divider()

# Pricing decisions
st.subheader("Pricing Decisions Distribution")

decision_counts = df["final_decision"].value_counts()

st.bar_chart(decision_counts)

st.divider()

# Top price increases
st.subheader("Top Products to Increase Price")

increase_df = df[df["final_decision"] == "increase_price"]

st.dataframe(
    increase_df.sort_values("revenue_change", ascending=False)[
        ["product_id","price","new_price","revenue_change"]
    ].head(10)
)

st.divider()

# Top price decreases
st.subheader("Top Products to Lower Price")

lower_df = df[df["final_decision"] == "lower_price"]

st.dataframe(
    lower_df.sort_values("revenue_change")[
        ["product_id","price","new_price","revenue_change"]
    ].head(10)
)

st.divider()

st.subheader("Full Pricing Table")

st.dataframe(df)