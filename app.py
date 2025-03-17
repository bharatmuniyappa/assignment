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
        df.columns = df.columns.str.strip().str.lower()  # Standardize column names
        df["order date"] = pd.to_datetime(df["order date"], errors="coerce")

        if "region" not in df.columns:
            st.error(f"⚠️ 'Region' column not found! Available columns: {', '.join(df.columns)}")
            return pd.DataFrame()

        return df
    except FileNotFoundError:
        st.error("⚠️ Dataset not found. Please upload 'Sample - Superstore.xlsx'.")
        return pd.DataFrame()

df_original = load_data()

# ---- Debugging: Check Available Columns ----
st.write("Available columns in dataset:", df_original.columns.tolist())

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

# Persistent Filter State
def filter_selection(key, options):
    if key not in st.session_state:
        st.session_state[key] = "All"
    return st.sidebar.selectbox(f"Select {key}", options=["All"] + options, index=options.index(st.session_state[key]) if st.session_state[key] in options else 0)

# Region Filter (Using Lowercase Column Name)
all_regions = sorted(df_original["region"].dropna().unique())
selected_region = filter_selection("Region", all_regions)

df_filtered = df_original if selected_region == "All" else df_original[df_original["region"] == selected_region]

# State Filter
all_states = sorted(df_filtered["state"].dropna().unique())
selected_state = filter_selection("State", all_states)

df_filtered = df_filtered if selected_state == "All" else df_filtered[df_filtered["state"] == selected_state]

# Category Filter
all_categories = sorted(df_filtered["category"].dropna().unique())
selected_category = filter_selection("Category", all_categories)

df_filtered = df_filtered if selected_category == "All" else df_filtered[df_filtered["category"] == selected_category]

# Sub-Category Filter
all_subcats = sorted(df_filtered["sub-category"].dropna().unique())
selected_subcat = filter_selection("Sub-Category", all_subcats)

df_filtered = df_filtered if selected_subcat == "All" else df_filtered[df_filtered["sub-category"] == selected_subcat]

# ---- Date Range Filter ----
if df_filtered.empty:
    min_date, max_date = df_original["order date"].min(), df_original["order date"].max()
else:
    min_date, max_date = df_filtered["order date"].min(), df_filtered["order date"].max()

from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

df_filtered = df_filtered[(df_filtered["order date"] >= pd.to_datetime(from_date)) & (df_filtered["order date"] <= pd.to_datetime(to_date))]

# ---- Title ----
st.title("SuperStore KPI Dashboard")

# ---- KPI Section ----
st.subheader("Key Performance Indicators")

total_sales = df_filtered["sales"].sum() if not df_filtered.empty else 0
total_quantity = df_filtered["quantity"].sum() if not df_filtered.empty else 0
total_profit = df_filtered["profit"].sum() if not df_filtered.empty else 0
margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

st.metric("Total Sales", f"${total_sales:,.2f}")
st.metric("Total Quantity Sold", f"{total_quantity:,}")
st.metric("Total Profit", f"${total_profit:,.2f}")
st.metric("Margin Rate", f"{margin_rate * 100:.2f}%")

# ---- KPI Selection ----
st.subheader("Visualize KPI Trends & Insights")
kpi_options = ["sales", "quantity", "profit", "margin rate"]
selected_kpi = st.radio("Select KPI to display:", options=kpi_options, horizontal=True)

# ---- Visualizations ----
if not df_filtered.empty:
    daily_grouped = df_filtered.groupby("order date").agg({"sales": "sum", "quantity": "sum", "profit": "sum"}).reset_index()
    daily_grouped["margin rate"] = daily_grouped["profit"] / daily_grouped["sales"].replace(0, 1)

    product_grouped = df_filtered.groupby("product name").agg({"sales": "sum", "quantity": "sum", "profit": "sum"}).reset_index()
    product_grouped["margin rate"] = product_grouped["profit"] / product_grouped["sales"].replace(0, 1)

    product_grouped.sort_values(by=selected_kpi, ascending=False, inplace=True)
    top_10 = product_grouped.head(10)

    col1, col2 = st.columns(2)

    with col1:
        fig_line = px.line(daily_grouped, x="order date", y=selected_kpi, title=f"{selected_kpi} Over Time", labels={"order date": "Date", selected_kpi: selected_kpi})
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        fig_bar = px.bar(top_10, x=selected_kpi, y="product name", orientation="h", title=f"Top 10 Products by {selected_kpi}")
        st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.warning("No data available for the selected filters and date range.")
