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

# Dashboard About Section
st.sidebar.markdown(
    """
    ### About This Dashboard
    Welcome to the SuperStore KPI Dashboard! 
    This tool allows you to analyze sales data across different dimensions such as region, state, and product category. 
    Utilize the sidebar filters to view specific metrics and identify trends through interactive charts. 
    Enhance your decision-making with insights on sales, profits, and more.
    """
)

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

# ---- Sidebar Date Range (From and To) ----
if df.empty:
    # If there's no data after filters, default to overall min/max
    min_date = df_original["Order Date"].min()
    max_date = df_original["Order Date"].max()
else:
    min_date = df["Order Date"].min()
    max_date = df["Order Date"].max()

from_date = st.sidebar.date_input(
    "From Date", value=min_date, min_value=min_date, max_value=max_date
)
to_date = st.sidebar.date_input(
    "To Date", value=max_date, min_value=min_date, max_value=max_date
)

# Ensure from_date <= to_date
if from_date > to_date:
    st.sidebar.error("From Date must be earlier than To Date.")

# Apply date range filter
df = df[
    (df["Order Date"] >= pd.to_datetime(from_date))
    & (df["Order Date"] <= pd.to_datetime(to_date))
]

# Function to convert DataFrame to CSV (for download)
def convert_df_to_csv(df):
    # Convert DataFrame to CSV and then encode it into bytes and base64 string for the download link.
    return df.to_csv(index=False).encode('utf-8')

# Check if data is available for download and place the download button
if not df.empty:
    csv = convert_df_to_csv(df)
    st.sidebar.download_button(
        label="Download filtered data (CSV)",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
        help="Click to download the currently filtered data."
    )
else:
    st.sidebar.error("No data available to download. Please adjust your filters.")

# ---- Page Title ----
st.title("SuperStore KPI Dashboard")

# ---- Custom CSS for KPI Tiles ----
st.markdown(
    """
    <style>
    .kpi-box {
        background-color: #FFFFFF;
        border: 2px solid #EAEAEA;
        border-radius: 8px;
        padding: 16px;
        margin: 8px;
        text-align: center;
    }
    .kpi-title {
        font-weight: 600;
        color: #333333;
        font-size: 16px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-weight: 700;
        font-size: 24px;
        color: #1E90FF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to format numbers with 'K' for thousands, 'M' for millions
def format_number(num):
    if num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    elif num >= 1000:
        return f"${num / 1000:.1f}K"
    else:
        return f"${num:.2f}"

# Calculate KPIs
if df.empty:
    total_sales = format_number(0)
    total_quantity = '0'
    total_profit = format_number(0)
    margin_rate = "0.00%"
else:
    total_sales = format_number(df["Sales"].sum())
    total_quantity = f"{df['Quantity'].sum()/1000:.1f}K"  # Assuming large numbers for quantities
    total_profit = format_number(df["Profit"].sum())
    margin_rate = f"{(df['Profit'].sum() / df['Sales'].sum() * 100) if df['Sales'].sum() != 0 else 0:.2f}%"

# Display KPIs in columns
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Sales</div>
            <div class='kpi-value'>{total_sales}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col2:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Quantity Sold</div>
            <div class='kpi-value'>{total_quantity}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col3:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Profit</div>
            <div class='kpi-value'>{total_profit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col4:
    st.markdown(
        f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Margin Rate</div>
            <div class='kpi-value'>{margin_rate}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---- Line Separator ----
st.markdown('---')

# ---- KPI Selection (Affects Both Charts) ----
st.subheader("Visualize KPI through interactive charts")

if df.empty:
    st.warning("No data available for the selected filters and date range.")
else:
    # Radio button above both charts
    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to display:", options=kpi_options, horizontal=True)

# ---- Prepare Data for Charts ----
# After applying all filters and setting the date range
df['MonthYear'] = df['Order Date'].dt.to_period('M')
df['MonthYear'] = df['MonthYear'].astype(str)  # Convert MonthYear from Period to String

# Group data by Month and Year after conversion to string
monthly_grouped = df.groupby('MonthYear').agg({
    "Sales": "sum",
    "Quantity": "sum",
    "Profit": "sum"
}).reset_index()
monthly_grouped["Margin Rate"] = monthly_grouped["Profit"] / monthly_grouped["Sales"].replace(0, 1)  # Handling division by zero

# Product grouping for top 10 chart
product_grouped = df.groupby("Product Name").agg({
    "Sales": "sum",
    "Quantity": "sum",
    "Profit": "sum"
}).reset_index()
product_grouped["Margin Rate"] = product_grouped["Profit"] / product_grouped["Sales"].replace(0, 1)

# Sort for top 10 by selected KPI
product_grouped.sort_values(by=selected_kpi, ascending=False, inplace=True)
top_10 = product_grouped.head(10)

# ---- Side-by-Side Layout for Charts ----
col_left, col_right = st.columns(2)

with col_left:
# Line Chart
    fig_line = px.line(
        monthly_grouped,
        x="MonthYear",
        y=selected_kpi,
        title=f"{selected_kpi} Over Time",
        labels={"MonthYear": "Month/Year", selected_kpi: selected_kpi},
        template="plotly_white",
    )
# Update layout to remove grid lines
    fig_line.update_layout(
        xaxis_showgrid=False,  # Remove grid lines along x-axis
        yaxis_showgrid=False,  # Remove grid lines along y-axis
        plot_bgcolor='rgba(0,0,0,0)'  # Optional: makes background transparent
    )
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    # Horizontal Bar Chart
    fig_bar = px.bar(
        top_10,
        x=selected_kpi,
        y="Product Name",
        orientation="h",
        title=f"Top 10 Products by {selected_kpi}",
        labels={selected_kpi: selected_kpi, "Product Name": "Product"},
        color=selected_kpi,
        color_continuous_scale="Blues",
        template="plotly_white",
    )
    fig_bar.update_layout(
        height=400,
        yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Setup columns for side-by-side chart display
col1, col2 = st.columns(2)

# Using first column for Donut Chart
with col1:
    # Custom colors for category
    colors = {
        "Furniture": "#0d47a1",
        "Office Supplies": "#1e88e5",
        "Technology": "#90caf9"
    }

    # ---- Prepare Data for Donut Chart ----
    category_grouped = df.groupby("Category").agg({
        "Sales": "sum",
        "Quantity": "sum",
        "Profit": "sum"
    }).reset_index()

    # Avoid division by zero in Margin Rate calculation
    category_grouped["Margin Rate"] = (category_grouped["Profit"] / category_grouped["Sales"].replace(0, 1)) * 100

    # ---- Create Donut Chart ----
    fig_donut = px.pie(
        category_grouped,
        values=selected_kpi,
        names='Category',
        title=f"Distribution of {selected_kpi} by Category",
        hole=0.4,
        color='Category',
        color_discrete_map=colors  # Apply custom colors
    )

    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(
        legend_title="Category",
        showlegend=True,  # Remove the legend
        legend=dict(
            x=0,  # x=0 positions the legend at the left
            y=1,  # y=1 positions the legend at the top
            xanchor='left',  # Anchor point of the legend is set to the left
            yanchor='top'    # Anchor point of the legend is set to the top
        )
    )

    # Display Donut Chart in Streamlit
    st.plotly_chart(fig_donut, use_container_width=True)

# Using second column for Bar Chart
with col2:
    # Custom colors for segments
    colors = {
        "Consumer": "#0d47a1",
        "Corporate": "#1e88e5",
        "Home Office": "#90caf9"
    }

    # ---- Prepare Data for Bar Chart ----
    segment_grouped = df.groupby("Segment").agg({
        "Sales": "sum",
        "Quantity": "sum",
        "Profit": "sum"
    }).reset_index()

    # Calculate Margin Rate if not already included
    segment_grouped["Margin Rate"] = (segment_grouped["Profit"] / segment_grouped["Sales"].replace(0, 1)) * 100

    # ---- Create Bar Chart ----
    fig_segment = px.bar(
        segment_grouped,
        x='Segment',
        y=selected_kpi,
        title=f"{selected_kpi} by Segment",
        labels={'Segment': "Segment", selected_kpi: selected_kpi},
        color='Segment',
        text=selected_kpi,  # display the KPI value on top of each bar for clarity
        template="plotly_white",
        color_discrete_map=colors  # Use custom colors
    )

    # Update layout to remove grid lines and update axis titles
    fig_segment.update_layout(
        yaxis_title=selected_kpi,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',  # Makes background transparent
        xaxis={'categoryorder':'total descending', 'showgrid': False},  # Remove x-axis grid lines
        yaxis={'showgrid': False}  # Remove y-axis grid lines
    )

    # Display Bar Chart in Streamlit
    st.plotly_chart(fig_segment, use_container_width=True)

# ---- Line Separator ----
st.markdown('---')

# ---- KPI Selection (Affects Both Charts) ----
st.subheader("Month wise Sub-Category Summary")

# Ensure 'Order Date' is in datetime format
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Extract Year and Month for easier filtering
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.strftime('%Y-%m')  # Keeping it as 'YYYY-MM' for uniformity

# Calculate Margin Rate here assuming 'Profit' and 'Sales' columns exist
if 'Profit' in df.columns and 'Sales' in df.columns and 'Sales' != 0:
    df['Margin Rate'] = (df['Profit'] / df['Sales']) * 100

# Create filters for Year and Month
year_filter = st.selectbox('Select Year', options=sorted(df['Year'].unique(), reverse=True))
month_filter = st.selectbox('Select Month', options=sorted(df[df['Year'] == year_filter]['Month'].unique()))

# Filter the monthly data based on selected year and month
filtered_data = df[(df['Year'] == year_filter) & (df['Month'] == month_filter)]

# Check if the selected KPI is available in the DataFrame
if selected_kpi in df.columns:
    # Group by month and subcategory
    monthly_data = filtered_data.groupby(['Month', 'Sub-Category'])[selected_kpi].sum().reset_index()
    st.write("Monthly Data by Sub-Category")
    st.dataframe(monthly_data[['Month', 'Sub-Category', selected_kpi]])

    # Function to convert DataFrame to CSV
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    # Continue with the rest of your code...
else:
    st.error(f"The selected KPI '{selected_kpi}' is not calculated or does not exist in the DataFrame.")


