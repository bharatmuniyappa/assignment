import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# ---- Set page layout ----
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    return df

df_original = load_data()

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

# Advanced Multi-Select Filters
all_regions = sorted(df_original["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect("Select Region(s)", all_regions, default=all_regions)

df_filtered = df_original[df_original["Region"].isin(selected_regions)]

all_states = sorted(df_filtered["State"].dropna().unique())
selected_states = st.sidebar.multiselect("Select State(s)", all_states, default=all_states)

df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

all_categories = sorted(df_filtered["Category"].dropna().unique())
selected_categories = st.sidebar.multiselect("Select Category(s)", all_categories, default=all_categories)

df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

all_subcats = sorted(df_filtered["Sub-Category"].dropna().unique())
selected_subcats = st.sidebar.multiselect("Select Sub-Category(s)", all_subcats, default=all_subcats)

df_filtered = df_filtered[df_filtered["Sub-Category"].isin(selected_subcats)]

all_ship_modes = sorted(df_filtered["Ship Mode"].dropna().unique())
selected_ship_modes = st.sidebar.multiselect("Select Ship Mode(s)", all_ship_modes, default=all_ship_modes)

df_filtered = df_filtered[df_filtered["Ship Mode"].isin(selected_ship_modes)]

# Customer Segment Filter
all_segments = sorted(df_filtered["Segment"].dropna().unique())
selected_segments = st.sidebar.multiselect("Select Customer Segment(s)", all_segments, default=all_segments)

df_filtered = df_filtered[df_filtered["Segment"].isin(selected_segments)]

# Payment Method Filter
if "Payment Method" in df_filtered.columns:
    all_payment_methods = sorted(df_filtered["Payment Method"].dropna().unique())
    selected_payment_methods = st.sidebar.multiselect("Select Payment Method(s)", all_payment_methods, default=all_payment_methods)
    df_filtered = df_filtered[df_filtered["Payment Method"].isin(selected_payment_methods)]

# Date Range Filter
min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date, key="from_date")
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date, key="to_date")

# Ensure date conversion before filtering
df_filtered = df_filtered[(df_filtered["Order Date"].dt.date >= from_date) & (df_filtered["Order Date"].dt.date <= to_date)]

# ---- KPI Section ----
st.title("SuperStore KPI Dashboard")
st.subheader("Key Performance Indicators")

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
else:
    total_sales = df_filtered["Sales"].sum()
    total_quantity = df_filtered["Quantity"].sum()
    total_profit = df_filtered["Profit"].sum()
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total Sales", f"${total_sales:,.2f}")
    kpi_col2.metric("Total Quantity Sold", f"{total_quantity:,}")
    kpi_col3.metric("Total Profit", f"${total_profit:,.2f}")
    kpi_col4.metric("Margin Rate", f"{margin_rate * 100:.2f}%")

    # ---- Multi-Dashboard Views ----
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Regional Analysis", "Forecasting", "Product Insights", "Customer Segmentation", "Profitability Analysis"])
    
    with tab1:
        st.subheader("Overall Performance")
        fig_overall = px.line(df_filtered, x="Order Date", y="Sales", title="Sales Trend Over Time")
        st.plotly_chart(fig_overall, use_container_width=True)
    
    with tab2:
        st.subheader("Regional Performance")
        fig_region = px.bar(df_filtered, x="Region", y="Sales", color="Region", title="Sales by Region")
        st.plotly_chart(fig_region, use_container_width=True)
    
    with tab3:
        st.subheader("Sales Forecast")
        df_filtered["Sales Forecast"] = df_filtered["Sales"].rolling(window=7).mean()
        fig_forecast = px.line(df_filtered, x="Order Date", y="Sales Forecast", title="7-Day Moving Average Sales Forecast")
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    with tab4:
        st.subheader("Product Performance")
        top_products = df_filtered.groupby("Product Name")["Sales"].sum().nlargest(10).reset_index()
        fig_product = px.bar(top_products, x="Sales", y="Product Name", orientation="h", title="Top 10 Products by Sales")
        st.plotly_chart(fig_product, use_container_width=True)
    
    with tab5:
        st.subheader("Customer Segmentation")
        fig_segment = px.pie(df_filtered, names="Segment", values="Sales", title="Sales Distribution by Customer Segment")
        st.plotly_chart(fig_segment, use_container_width=True)
    
    with tab6:
        st.subheader("Profitability Analysis")
        fig_profit = px.bar(df_filtered, x="Product Name", y="Profit", title="Profit by Product")
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # ---- Additional Enhancements ----
    st.sidebar.download_button("Download Filtered Data", df_filtered.to_csv(index=False).encode("utf-8"), "filtered_data.csv", "text/csv")
    
st.success("Dashboard loaded successfully!")
