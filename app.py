import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config for wide layout
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    return df

df_original = load_data()

# ---- Sidebar Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["📊 Sales Overview", "📈 Performance Analytics", "📌 Customer Insights", "📦 Product Analysis"])

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

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
if not df_filtered.empty:
    min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
    from_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    to_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

if page == "📊 Sales Overview":
    st.title("📊 Sales Overview")
    if not df_filtered.empty:
        total_sales = df_filtered["Sales"].sum()
        total_profit = df_filtered["Profit"].sum()
        total_quantity = df_filtered["Quantity"].sum()
        margin_rate = (total_profit / total_sales * 100) if total_sales != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Sales", value=f"${total_sales:,.2f}")
        with col2:
            st.metric(label="Quantity Sold", value=f"{total_quantity:,}")
        with col3:
            st.metric(label="Profit", value=f"${total_profit:,.2f}")
        with col4:
            st.metric(label="Margin Rate", value=f"{margin_rate:.2f}%")
        
        st.subheader("Sales Trend Over Time")
        df_filtered["MonthYear"] = df_filtered["Order Date"].dt.to_period("M").astype(str)
        df_trend = df_filtered.groupby("MonthYear")["Sales"].sum().reset_index()
        fig_trend = px.line(df_trend, x="MonthYear", y="Sales", title="Sales Trend Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

elif page == "📈 Performance Analytics":
    st.title("📈 Performance Analytics")
    if not df_filtered.empty:
        st.subheader("Profit Distribution Across Categories")
        fig_category_profit = px.box(df_filtered, x="Category", y="Profit", color="Category", title="Profit Distribution by Category")
        st.plotly_chart(fig_category_profit, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

elif page == "📌 Customer Insights":
    st.title("📌 Customer Insights")
    if not df_filtered.empty:
        st.subheader("Top Customers by Sales")
        top_customers = df_filtered.groupby("Customer Name")["Sales"].sum().reset_index().nlargest(10, "Sales").sort_values(by="Sales", ascending=True)
        fig_customers = px.bar(top_customers, x="Sales", y="Customer Name", orientation="h", color="Sales", title="Top 10 Customers by Sales")
        st.plotly_chart(fig_customers, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

elif page == "📦 Product Analysis":
    st.title("📦 Product Analysis")
    if not df_filtered.empty:
        st.subheader("Most Profitable Products")
        profitable_products = df_filtered.groupby("Product Name")["Profit"].sum().reset_index().nlargest(10, "Profit").sort_values(by="Profit", ascending=True)
        fig_product = px.bar(profitable_products, x="Profit", y="Product Name", orientation="h", color="Profit", title="Top 10 Profitable Products")
        st.plotly_chart(fig_product, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

# ---- Data Export ----
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="Download Data", data=csv, file_name='filtered_data.csv', mime='text/csv')

