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
min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
from_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

if page == "📌 Customer Insights":
    st.title("📌 Customer Insights")
    st.subheader("Top Customers by Sales")
    top_customers = df_filtered.groupby("Customer Name")["Sales"].sum().reset_index().nlargest(10, "Sales")
    fig_customers = px.bar(top_customers, x="Sales", y="Customer Name", orientation="h", color="Sales", title="Top 10 Customers by Sales")
    st.plotly_chart(fig_customers, use_container_width=True)

elif page == "📦 Product Analysis":
    st.title("📦 Product Analysis")
    st.subheader("Most Profitable Products")
    profitable_products = df_filtered.groupby("Product Name")["Profit"].sum().reset_index().nlargest(10, "Profit")
    fig_product = px.bar(profitable_products, x="Profit", y="Product Name", orientation="h", color="Profit", title="Top 10 Profitable Products")
    st.plotly_chart(fig_product, use_container_width=True)

# ---- Data Export ----
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="Download Data", data=csv, file_name='filtered_data.csv', mime='text/csv')

st.success("Dashboard updated with enhanced features and layout! 🚀")
