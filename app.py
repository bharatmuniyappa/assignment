import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Set Streamlit page configuration
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    file_path = "/mnt/data/Sample - Superstore.xlsx"
    if not os.path.exists(file_path):
        st.error("File not found. Please upload the correct file.")
        return pd.DataFrame()  # Return an empty dataframe to prevent errors
    df = pd.read_excel(file_path, engine="openpyxl")
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df = load_data()

# Sidebar Navigation
st.sidebar.title("Dashboard Sections")
page = st.sidebar.radio("Select a section:", ["📊 Sales Overview", "📈 Performance Trends", "📌 Customer Behavior", "📅 Monthly Analysis"])

# Sidebar Filters
st.sidebar.header("Data Filters")

def multiselect_with_all(label, options, default_options):
    selected_options = st.sidebar.multiselect(label, ["All"] + options, default=["All"] if set(default_options) == set(options) else default_options)
    if "All" in selected_options and len(selected_options) > 1:
        selected_options.remove("All")
    elif len(selected_options) == 0:
        st.sidebar.warning(f"At least one {label.lower()} must be selected.")
        selected_options = ["All"]
    return options if "All" in selected_options else selected_options

if not df.empty:
    selected_regions = multiselect_with_all("Select Region(s)", sorted(df["Region"].dropna().unique()), df["Region"].unique())
    df_filtered = df[df["Region"].isin(selected_regions)]

    selected_states = multiselect_with_all("Select State(s)", sorted(df_filtered["State"].dropna().unique()), df_filtered["State"].unique())
    df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

    selected_categories = multiselect_with_all("Select Category(s)", sorted(df_filtered["Category"].dropna().unique()), df_filtered["Category"].unique())
    df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

    # Date Range Filter
    min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
    from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
    to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)
    df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

    # KPI Metrics
    total_sales = df_filtered["Sales"].sum()
    total_profit = df_filtered["Profit"].sum()
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0
    total_orders = df_filtered["Order ID"].nunique()

    # Display KPI Metrics
    st.title("📊 Retail Insights Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Total Orders", total_orders)

    # Charts
    if page == "📊 Sales Overview":
        st.subheader("Category-Wise Sales Distribution")
        fig_category = px.treemap(df_filtered, path=["Category", "Sub-Category"], values="Sales", title="Sales by Product Category")
        st.plotly_chart(fig_category, use_container_width=True)

        st.subheader("Top Performing Products")
        top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum"}).reset_index()
        top_products = top_products.sort_values(by="Sales", ascending=False).head(10)
        fig_bar = px.bar(top_products, x="Sales", y="Product Name", orientation="h", title="Best-Selling Products")
        st.plotly_chart(fig_bar, use_container_width=True)

    elif page == "📈 Performance Trends":
        st.subheader("Sales vs Profitability")
        fig_scatter = px.scatter(df_filtered, x="Sales", y="Profit", color="Category", size="Quantity", title="Revenue vs Profit")
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader("Sales Growth Over Time")
        df_time_series = df_filtered.groupby(df_filtered["Order Date"].dt.to_period("M")).sum().reset_index()
        fig_trend = px.line(df_time_series, x="Order Date", y="Sales", markers=True, title="Monthly Sales Performance")
        st.plotly_chart(fig_trend, use_container_width=True)

    elif page == "📌 Customer Behavior":
        st.subheader("Customer Segments and Sales")
        fig_segment = px.pie(df_filtered, names="Segment", values="Sales", title="Sales Breakdown by Customer Segment")
        st.plotly_chart(fig_segment, use_container_width=True)

    elif page == "📅 Monthly Analysis":
        st.subheader("Monthly Revenue Trends")
        df_filtered["MonthYear"] = df_filtered["Order Date"].dt.to_period("M").astype(str)
        monthly_sales = df_filtered.groupby("MonthYear")["Sales"].sum().reset_index()
        fig_monthly = px.bar(monthly_sales, x="MonthYear", y="Sales", title="Revenue Trends per Month")
        st.plotly_chart(fig_monthly, use_container_width=True)

    st.success("Dashboard Successfully Updated! 🚀")
