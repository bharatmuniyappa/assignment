import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import base64

# Configure Streamlit page layout
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# ---- Load Data Function ----
@st.cache_data
def fetch_dataset():
    dataset = pd.read_excel("Retail_Data.xlsx", engine="openpyxl")
    if not pd.api.types.is_datetime64_any_dtype(dataset["Purchase Date"]):
        dataset["Purchase Date"] = pd.to_datetime(dataset["Purchase Date"])
    return dataset

raw_data = fetch_dataset()

# Sidebar Information Section
st.sidebar.markdown(
    """
    ### About This Dashboard
    Welcome to the Retail Insights Dashboard! 
    Analyze transaction data across various dimensions including location, product type, and customer segment. 
    Use the filters to explore trends in revenue, profits, and more.
    """
)

# ---- Sidebar Filters ----
st.sidebar.title("Data Filters")

# Region Selection
regions = sorted(raw_data["Region"].dropna().unique())
selected_region = st.sidebar.selectbox("Choose Region", options=["All"] + regions)

data_filtered = raw_data.copy()
if selected_region != "All":
    data_filtered = data_filtered[data_filtered["Region"] == selected_region]

# State Selection
states = sorted(data_filtered["State"].dropna().unique())
selected_state = st.sidebar.selectbox("Choose State", options=["All"] + states)
if selected_state != "All":
    data_filtered = data_filtered[data_filtered["State"] == selected_state]

# Category Selection
categories = sorted(data_filtered["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Choose Category", options=["All"] + categories)
if selected_category != "All":
    data_filtered = data_filtered[data_filtered["Category"] == selected_category]

# Date Range Selection
min_date = data_filtered["Purchase Date"].min()
max_date = data_filtered["Purchase Date"].max()
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("Start Date cannot be later than End Date.")

data_filtered = data_filtered[(data_filtered["Purchase Date"] >= pd.to_datetime(start_date)) &
                              (data_filtered["Purchase Date"] <= pd.to_datetime(end_date))]

# Download Filtered Data
if not data_filtered.empty:
    csv_data = data_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Data (CSV)",
        data=csv_data,
        file_name='filtered_retail_data.csv',
        mime='text/csv'
    )
else:
    st.sidebar.error("No data available. Adjust filters.")

# ---- Dashboard Title ----
st.title("Retail Insights Dashboard")

# ---- KPI Calculations ----
def format_currency(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:.2f}"

total_revenue = format_currency(data_filtered["Revenue"].sum())
total_units = f"{data_filtered['Units Sold'].sum()/1000:.1f}K"
total_profit = format_currency(data_filtered["Profit"].sum())
profit_margin = f"{(data_filtered['Profit'].sum() / data_filtered['Revenue'].sum() * 100) if data_filtered['Revenue'].sum() != 0 else 0:.2f}%"

# Display KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Total Revenue", value=total_revenue)
kpi2.metric(label="Units Sold", value=total_units)
kpi3.metric(label="Total Profit", value=total_profit)
kpi4.metric(label="Profit Margin", value=profit_margin)

st.markdown("---")

# ---- KPI Trends Visualization ----
st.subheader("KPI Trends Analysis")

data_filtered['YearMonth'] = data_filtered['Purchase Date'].dt.to_period('M').astype(str)
monthly_summary = data_filtered.groupby('YearMonth').agg({
    "Revenue": "sum",
    "Units Sold": "sum",
    "Profit": "sum"
}).reset_index()
monthly_summary["Profit Margin"] = (monthly_summary["Profit"] / monthly_summary["Revenue"]).replace([np.inf, -np.inf], 0) * 100

# Line Chart
fig_trend = px.line(
    monthly_summary,
    x="YearMonth",
    y="Revenue",
    title="Monthly Revenue Trend",
    labels={"YearMonth": "Month-Year", "Revenue": "Revenue ($)"},
    template="plotly_white"
)
st.plotly_chart(fig_trend, use_container_width=True)

# ---- Category Breakdown ----
st.subheader("Category Performance")
category_summary = data_filtered.groupby("Category").agg({
    "Revenue": "sum",
    "Units Sold": "sum",
    "Profit": "sum"
}).reset_index()
category_summary["Profit Margin"] = (category_summary["Profit"] / category_summary["Revenue"]).replace([np.inf, -np.inf], 0) * 100

fig_category = px.pie(
    category_summary,
    values="Revenue",
    names="Category",
    title="Revenue Distribution by Category",
    hole=0.4,
    template="plotly_white"
)
st.plotly_chart(fig_category, use_container_width=True)

# ---- Segment Performance ----
st.subheader("Customer Segment Performance")
segment_summary = data_filtered.groupby("Customer Segment").agg({
    "Revenue": "sum",
    "Units Sold": "sum",
    "Profit": "sum"
}).reset_index()
segment_summary["Profit Margin"] = (segment_summary["Profit"] / segment_summary["Revenue"]).replace([np.inf, -np.inf], 0) * 100

fig_segment = px.bar(
    segment_summary,
    x="Customer Segment",
    y="Revenue",
    title="Revenue by Customer Segment",
    text_auto=True,
    template="plotly_white"
)
st.plotly_chart(fig_segment, use_container_width=True)

st.markdown("---")
st.subheader("Explore Monthly Product Performance")
selected_year = st.selectbox("Choose Year", sorted(data_filtered["Purchase Date"].dt.year.unique(), reverse=True))
selected_month = st.selectbox("Choose Month", sorted(data_filtered[data_filtered["Purchase Date"].dt.year == selected_year]['YearMonth'].unique()))
monthly_data = data_filtered[(data_filtered["YearMonth"] == selected_month)]

if not monthly_data.empty:
    st.dataframe(monthly_data[["YearMonth", "Product Name", "Revenue"]])
else:
    st.warning("No data available for selected month.")
