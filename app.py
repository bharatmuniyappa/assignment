import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import base64


# Set page config for wide layout
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    # Adjust the path if needed, e.g. "data/Sample - Superstore.xlsx"
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    # Convert Order Date to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df_original = load_data()

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

# Region Filter
all_regions = sorted(df_original["Region"].dropna().unique())
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + all_regions)

# Filter data by Region
if selected_region != "All":
    df_filtered_region = df_original[df_original["Region"] == selected_region]
else:
    df_filtered_region = df_original

# State Filter
all_states = sorted(df_filtered_region["State"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", options=["All"] + all_states)

# Filter data by State
if selected_state != "All":
    df_filtered_state = df_filtered_region[df_filtered_region["State"] == selected_state]
else:
    df_filtered_state = df_filtered_region

# Category Filter
all_categories = sorted(df_filtered_state["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Category", options=["All"] + all_categories)

# Filter data by Category
if selected_category != "All":
    df_filtered_category = df_filtered_state[df_filtered_state["Category"] == selected_category]
else:
    df_filtered_category = df_filtered_state

# Sub-Category Filter
all_subcats = sorted(df_filtered_category["Sub-Category"].dropna().unique())
selected_subcat = st.sidebar.selectbox("Select Sub-Category", options=["All"] + all_subcats)

# Final filter by Sub-Category
df = df_filtered_category.copy()
if selected_subcat != "All":
    df = df[df["Sub-Category"] == selected_subcat]

# Payment Method Filter (New Enhancement)
if "Payment Method" in df.columns:
    all_payment_methods = sorted(df["Payment Method"].dropna().unique())
    selected_payment_method = st.sidebar.selectbox("Select Payment Method", options=["All"] + all_payment_methods)
    if selected_payment_method != "All":
        df = df[df["Payment Method"] == selected_payment_method]

# Customer Segment Filter (New Enhancement)
all_segments = sorted(df["Segment"].dropna().unique())
selected_segment = st.sidebar.selectbox("Select Customer Segment", options=["All"] + all_segments)
if selected_segment != "All":
    df = df[df["Segment"] == selected_segment]

# Date Range Filter
if df.empty:
    min_date, max_date = df_original["Order Date"].min(), df_original["Order Date"].max()
else:
    min_date, max_date = df["Order Date"].min(), df["Order Date"].max()

from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

# Ensure from_date <= to_date
if from_date > to_date:
    st.sidebar.error("From Date must be earlier than To Date.")

df = df[(df["Order Date"] >= pd.to_datetime(from_date)) & (df["Order Date"] <= pd.to_datetime(to_date))]

# ---- Additional Enhancements ----
st.sidebar.markdown("### New Insights Added!")
st.sidebar.markdown("- Payment Method Analysis")
st.sidebar.markdown("- Customer Segment Breakdown")

# ---- New KPI: Average Order Value ----
if not df.empty:
    df["Order Value"] = df["Sales"] / df["Quantity"]
    avg_order_value = df["Order Value"].mean()
    st.sidebar.metric("Average Order Value", f"${avg_order_value:,.2f}")

# ---- Tabbed Dashboard ----
tab1, tab2, tab3 = st.tabs(["Overview", "Sales Trends", "Customer Insights"])

with tab1:
    st.subheader("Overall Sales Overview")
    fig_overall = px.bar(df, x="Category", y="Sales", title="Sales by Category", color="Category")
    st.plotly_chart(fig_overall, use_container_width=True)

with tab2:
    st.subheader("Sales Trends Over Time")
    fig_trend = px.line(df, x="Order Date", y="Sales", title="Sales Over Time")
    st.plotly_chart(fig_trend, use_container_width=True)

with tab3:
    st.subheader("Customer Insights")
    fig_segment = px.pie(df, names="Segment", values="Sales", title="Sales Distribution by Customer Segment")
    st.plotly_chart(fig_segment, use_container_width=True)

st.success("Enhanced Dashboard Loaded Successfully!")
