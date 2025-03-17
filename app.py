import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config for wide layout
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    return df

df_original = load_data()

# ---- Sidebar Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["📊 Sales Overview", "📈 Performance Analytics"])

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

# Multi-Select Filters with "All" Option
def multiselect_with_all(label, options, default_options):
    selected_options = st.sidebar.multiselect(label, ["All"] + options, default=["All"])
    return options if "All" in selected_options else selected_options

selected_regions = multiselect_with_all("Choose Region(s)", sorted(df_original["Region"].dropna().unique()), df_original["Region"].unique())
df_filtered = df_original[df_original["Region"].isin(selected_regions)]

selected_states = multiselect_with_all("Choose State(s)", sorted(df_filtered["State"].dropna().unique()), df_filtered["State"].unique())
df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

selected_categories = multiselect_with_all("Choose Category(s)", sorted(df_filtered["Category"].dropna().unique()), df_filtered["Category"].unique())
df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

selected_subcategories = multiselect_with_all("Choose Sub-Category(s)", sorted(df_filtered["Sub-Category"].dropna().unique()), df_filtered["Sub-Category"].unique())
df_filtered = df_filtered[df_filtered["Sub-Category"].isin(selected_subcategories)]

# Date Filter
min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
from_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

# ---- KPI Calculation ----
total_sales = df_filtered["Sales"].sum() if not df_filtered.empty else 0
total_profit = df_filtered["Profit"].sum() if not df_filtered.empty else 0
margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

# ---- Display KPIs ----
st.title("📊 Sales Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Revenue", value=f"${total_sales:,.2f}")
with col2:
    st.metric(label="Net Profit", value=f"${total_profit:,.2f}")
with col3:
    st.metric(label="Profit Margin", value=f"{(margin_rate * 100):,.2f}%")

# ---- Visualizations ----
st.subheader("Revenue Breakdown by Category & Sub-Category")
treemap_fig = px.treemap(df_filtered, path=["Category", "Sub-Category"], values="Sales", title="Category Revenue Breakdown")
st.plotly_chart(treemap_fig, use_container_width=True)

st.subheader("Top 5 Best-Selling Products")
top_products = df_filtered.groupby("Product Name")["Sales"].sum().reset_index().nlargest(5, "Sales")
fig_bar = px.bar(top_products, x="Sales", y="Product Name", orientation="h", color="Sales", title="Best-Selling Products")
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Profit vs. Revenue")
fig_scatter = px.scatter(df_filtered, x="Sales", y="Profit", color="Category", size="Quantity", title="Profitability vs Revenue")
st.plotly_chart(fig_scatter, use_container_width=True)

# ---- Performance Analytics Page ----
if page == "📈 Performance Analytics":
    st.title("📈 Performance Analytics")
    st.subheader("KPI Trend Over Time")
    df_filtered["MonthYear"] = df_filtered["Order Date"].dt.to_period("M").astype(str)
    df_trend = df_filtered.groupby("MonthYear")[["Sales", "Profit"]].sum().reset_index()
    fig_line = px.line(df_trend, x="MonthYear", y="Sales", title="Revenue Trends Over Time")
    st.plotly_chart(fig_line, use_container_width=True)

# ---- Data Export ----
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="Download Data", data=csv, file_name='filtered_data.csv', mime='text/csv')

st.success("Dashboard")
