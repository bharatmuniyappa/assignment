import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configure Streamlit page layout
st.set_page_config(page_title="Retail Performance Dashboard", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
        body { font-family: Arial, sans-serif; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Roboto', sans-serif; color: #333; }
        .stRadio > label { font-size: 16px; font-weight: bold; }
        .stMetric > div { font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---- Load Data Function ----
@st.cache_data
def load_dataset():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

data_original = load_dataset()

# ---- Sidebar Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Navigate to:", ["📊 Business Overview", "📈 Advanced Analytics"])

# ---- Sidebar Filters ----
def multi_select(label, options, default):
    selected = st.sidebar.multiselect(label, ["All"] + options, default=["All"] if set(default) == set(options) else default)
    if "All" in selected and len(selected) > 1:
        selected.remove("All")
    return options if "All" in selected else selected

st.sidebar.title("Filters")
selected_regions = multi_select("Select Region(s)", sorted(data_original["Region"].dropna().unique()), data_original["Region"].unique())
data_filtered = data_original[data_original["Region"].isin(selected_regions)]

selected_states = multi_select("Select State(s)", sorted(data_filtered["State"].dropna().unique()), data_filtered["State"].unique())
data_filtered = data_filtered[data_filtered["State"].isin(selected_states)]

selected_categories = multi_select("Select Category(s)", sorted(data_filtered["Category"].dropna().unique()), data_filtered["Category"].unique())
data_filtered = data_filtered[data_filtered["Category"].isin(selected_categories)]

selected_products = multi_select("Select Product(s)", sorted(data_filtered["Product Name"].dropna().unique()), data_filtered["Product Name"].unique())
data_filtered = data_filtered[data_filtered["Product Name"].isin(selected_products)]

min_date, max_date = data_filtered["Order Date"].min(), data_filtered["Order Date"].max()
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

data_filtered = data_filtered[(data_filtered["Order Date"] >= pd.to_datetime(start_date)) & (data_filtered["Order Date"] <= pd.to_datetime(end_date))]

# ---- KPI Metrics ----
total_sales = data_filtered["Sales"].sum() if not data_filtered.empty else 0
total_profit = data_filtered["Profit"].sum() if not data_filtered.empty else 0
margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

if page == "📊 Business Overview":
    st.title("📊 Business Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
        st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    with col2:
        st.metric(label="Margin Rate", value=f"{(margin_rate * 100):,.2f}%")
    
    st.subheader("Sales Breakdown by Category & Sub-Category")
    treemap = px.treemap(data_filtered, path=["Category", "Sub-Category"], values="Sales", title="Category Sales Breakdown")
    st.plotly_chart(treemap, use_container_width=True)
    
    top_products = data_filtered.groupby("Product Name")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False).head(5)
    top_products["Short Name"] = top_products["Product Name"].str[:15] + "..."
    st.subheader("Top 5 Products by Sales")
    bar_chart = px.bar(top_products, x="Sales", y="Short Name", orientation="h", title="Top Products", color="Sales", color_continuous_scale="Blues")
    bar_chart.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(bar_chart, use_container_width=True)

elif page == "📈 Advanced Analytics":
    st.title("📈 Advanced Analytics")
    st.subheader("Profit vs. Sales")
    scatter_plot = px.scatter(data_filtered, x="Sales", y="Profit", color="Category", size="Quantity", title="Profitability vs Sales")
    st.plotly_chart(scatter_plot, use_container_width=True)
    
    st.subheader("KPI Trend Over Time")
    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to visualize:", options=kpi_options, horizontal=True)
    data_grouped = data_filtered.groupby("Order Date").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    data_grouped["Margin Rate"] = data_grouped["Profit"] / data_grouped["Sales"].replace(0, 1)
    trend_chart = px.line(data_grouped, x="Order Date", y=selected_kpi, title=f"{selected_kpi} Over Time", labels={"Order Date": "Date", selected_kpi: selected_kpi}, template="plotly_white")
    st.plotly_chart(trend_chart, use_container_width=True)

st.success("Dashboard updated with advanced analytics features! 🚀")
