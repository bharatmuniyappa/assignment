import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---- Set page layout ----
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

# ---- Load Data with Column Standardization ----
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        df["order date"] = pd.to_datetime(df["order date"], errors="coerce")
        return df
    except FileNotFoundError:
        st.error("⚠️ Dataset not found. Please upload 'Sample - Superstore.xlsx'.")
        return pd.DataFrame()

df_original = load_data()

# ---- Sidebar Filters ----
st.sidebar.title("Advanced Filters")

# Multi-Select Filters with Search
selected_regions = st.sidebar.multiselect("Select Region(s)", sorted(df_original["region"].dropna().unique()))
selected_states = st.sidebar.multiselect("Select State(s)", sorted(df_original["state"].dropna().unique()))
selected_categories = st.sidebar.multiselect("Select Category(s)", sorted(df_original["category"].dropna().unique()))
selected_segments = st.sidebar.multiselect("Select Segment(s)", sorted(df_original["segment"].dropna().unique()))
selected_ship_modes = st.sidebar.multiselect("Select Ship Mode(s)", sorted(df_original["ship mode"].dropna().unique()))
selected_customers = st.sidebar.multiselect("Select Customer(s)", sorted(df_original["customer name"].dropna().unique()))
selected_products = st.sidebar.multiselect("Select Product(s)", sorted(df_original["product name"].dropna().unique()))
selected_discounts = st.sidebar.slider("Select Discount Range", 0.0, df_original["discount"].max(), (0.0, df_original["discount"].max()))
selected_shipping_cost = st.sidebar.slider("Select Shipping Cost Range", df_original["shipping cost"].min(), df_original["shipping cost"].max(), (df_original["shipping cost"].min(), df_original["shipping cost"].max()))

# Apply Filters
df_filtered = df_original.copy()
if selected_regions:
    df_filtered = df_filtered[df_filtered["region"].isin(selected_regions)]
if selected_states:
    df_filtered = df_filtered[df_filtered["state"].isin(selected_states)]
if selected_categories:
    df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]
if selected_segments:
    df_filtered = df_filtered[df_filtered["segment"].isin(selected_segments)]
if selected_ship_modes:
    df_filtered = df_filtered[df_filtered["ship mode"].isin(selected_ship_modes)]
if selected_customers:
    df_filtered = df_filtered[df_filtered["customer name"].isin(selected_customers)]
if selected_products:
    df_filtered = df_filtered[df_filtered["product name"].isin(selected_products)]
df_filtered = df_filtered[(df_filtered["discount"] >= selected_discounts[0]) & (df_filtered["discount"] <= selected_discounts[1])]
df_filtered = df_filtered[(df_filtered["shipping cost"] >= selected_shipping_cost[0]) & (df_filtered["shipping cost"] <= selected_shipping_cost[1])]

# Date Range Filter
min_date, max_date = df_filtered["order date"].min(), df_filtered["order date"].max()
from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)
df_filtered = df_filtered[(df_filtered["order date"] >= pd.to_datetime(from_date)) & (df_filtered["order date"] <= pd.to_datetime(to_date))]

# ---- KPI Section ----
st.title("SuperStore KPI Dashboard")

col1, col2, col3, col4 = st.columns(4)
total_sales = df_filtered["sales"].sum()
total_quantity = df_filtered["quantity"].sum()
total_profit = df_filtered["profit"].sum()
margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Quantity Sold", f"{total_quantity:,}")
col3.metric("Total Profit", f"${total_profit:,.2f}")
col4.metric("Margin Rate", f"{margin_rate * 100:.2f}%")

# ---- KPI Selection ----
kpi_options = ["sales", "quantity", "profit", "margin rate"]
selected_kpi = st.radio("Select KPI to display:", options=kpi_options, horizontal=True)

# ---- CSV Export ----
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("Download Filtered Data", csv, "filtered_data.csv", "text/csv")

st.success("Dashboard updated with advanced filters and enhancements!")
