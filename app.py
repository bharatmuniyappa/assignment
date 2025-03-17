import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import base64

# ---- Set page layout ----
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df_original = load_data()

# ---- Sidebar Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["📊 Business Overview", "📈 Advanced Analytics", "📌 Customer Insights", "📅 Month-wise Summary"])

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

def multiselect_with_all(label, options, default_options):
    selected_options = st.sidebar.multiselect(label, ["All"] + options, default=["All"] if set(default_options) == set(options) else default_options)
    if "All" in selected_options and len(selected_options) > 1:
        selected_options.remove("All")
    elif len(selected_options) == 0:
        st.sidebar.warning(f"At least one {label.lower()} must be selected.")
        selected_options = ["All"]
    return options if "All" in selected_options else selected_options

selected_regions = multiselect_with_all("Select Region(s)", sorted(df_original["Region"].dropna().unique()), df_original["Region"].unique())
df_filtered = df_original[df_original["Region"].isin(selected_regions)]

selected_states = multiselect_with_all("Select State(s)", sorted(df_filtered["State"].dropna().unique()), df_filtered["State"].unique())
df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

selected_categories = multiselect_with_all("Select Category(s)", sorted(df_filtered["Category"].dropna().unique()), df_filtered["Category"].unique())
df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

selected_subcategories = multiselect_with_all("Select Sub-Category(s)", sorted(df_filtered["Sub-Category"].dropna().unique()), df_filtered["Sub-Category"].unique())
df_filtered = df_filtered[df_filtered["Sub-Category"].isin(selected_subcategories)]

selected_products = multiselect_with_all("Select Product(s)", sorted(df_filtered["Product Name"].dropna().unique()), df_filtered["Product Name"].unique())
df_filtered = df_filtered[df_filtered["Product Name"].isin(selected_products)]

# Date Range Filter
min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)
df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

# ---- KPI Metrics ----
if df_filtered.empty:
    total_sales, total_profit, margin_rate, total_quantity = 0, 0, 0, 0
else:
    total_sales = df_filtered["Sales"].sum()
    total_profit = df_filtered["Profit"].sum()
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0
    total_quantity = df_filtered["Quantity"].sum()

# ---- Display KPI Metrics ----
st.title("📊 Business Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Margin Rate", f"{(margin_rate * 100):.2f}%")

# ---- Charts ----
if page == "📊 Business Overview":
    st.subheader("Sales Breakdown by Category & Sub-Category")
    treemap_fig = px.treemap(df_filtered, path=["Category", "Sub-Category"], values="Sales", title="Category Sales Breakdown")
    st.plotly_chart(treemap_fig, use_container_width=True)

    st.subheader("Top 10 Products by Sales")
    top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum"}).reset_index()
    top_products = top_products.sort_values(by="Sales", ascending=False).head(10)
    fig_bar = px.bar(top_products, x="Sales", y="Product Name", orientation="h", title="Top Products")
    st.plotly_chart(fig_bar, use_container_width=True)

elif page == "📈 Advanced Analytics":
    st.subheader("Profit vs. Sales")
    fig_scatter = px.scatter(df_filtered, x="Sales", y="Profit", color="Category", size="Quantity", title="Profitability vs Sales")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("KPI Trends Over Time")
    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to visualize:", options=kpi_options, horizontal=True)
    df_grouped = df_filtered.groupby("Order Date").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    df_grouped["Margin Rate"] = df_grouped["Profit"] / df_grouped["Sales"].replace(0, 1)
    fig_line = px.line(df_grouped, x="Order Date", y=selected_kpi, title=f"{selected_kpi} Over Time")
    st.plotly_chart(fig_line, use_container_width=True)

elif page == "📌 Customer Insights":
    st.subheader("Customer Segmentation")
    fig_segment = px.pie(df_filtered, names="Segment", values="Sales", title="Sales Distribution by Customer Segment")
    st.plotly_chart(fig_segment, use_container_width=True)

elif page == "📅 Month-wise Summary":
    st.subheader("Month-wise Sales Analysis")
    df_filtered["MonthYear"] = df_filtered["Order Date"].dt.to_period("M").astype(str)
    monthly_sales = df_filtered.groupby("MonthYear")["Sales"].sum().reset_index()
    fig_monthly = px.bar(monthly_sales, x="MonthYear", y="Sales", title="Monthly Sales Trend")
    st.plotly_chart(fig_monthly, use_container_width=True)

st.success("Dashboard updated successfully! 🚀")
