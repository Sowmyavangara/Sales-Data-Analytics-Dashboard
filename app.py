
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import subprocess
import sys

# Page setup
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "sales.db"

st.title("📊 Sales Data Analysis & Insights")
st.caption("Explore sales performance by date, category, and region.")

# Load data from SQLite

@st.cache_data
def load_data():
    # Create the database automatically if it does not exist
    if not DB_FILE.exists():
        pipeline = BASE_DIR / "process_sales.py"

        if not pipeline.exists():
            raise FileNotFoundError(
                "process_sales.py was not found."
            )

        subprocess.run(
            [sys.executable, str(pipeline)],
            cwd=BASE_DIR,
            check=True
        )

    # Read sales data from SQLite
    with sqlite3.connect(DB_FILE) as connection:
        data = pd.read_sql_query(
            "SELECT * FROM sales",
            connection
        )

    data["OrderDate"] = pd.to_datetime(
        data["OrderDate"],
        errors="coerce"
    )

    data = data.dropna(subset=["OrderDate"])

    return data

# Load sales data before using it in the dashboard
try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load sales data: {error}")
    st.info("Check data/sales.csv and process_sales.py.")
    st.stop()

if df.empty:
    st.warning("No sales records found.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Sales")

categories = st.sidebar.multiselect(
    "Select categories",
    sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

regions = st.sidebar.multiselect(
    "Select regions",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

min_date = df["OrderDate"].min().date()
max_date = df["OrderDate"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered = df[
    df["Category"].isin(categories) &
    df["Region"].isin(regions)
].copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["OrderDate"].dt.date.between(start_date, end_date)
    ]

if filtered.empty:
    st.warning("No sales match these filters.")
    st.stop()

# Key performance indicators
total_revenue = filtered["Revenue"].sum()
total_orders = len(filtered)
units_sold = filtered["Quantity"].sum()
average_order_value = total_revenue / total_orders

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{units_sold:,}")
col4.metric("Avg. Revenue / Order", f"₹{average_order_value:,.0f}")

st.divider()

# Prepare monthly data
monthly = filtered.copy()
monthly["Month"] = monthly["OrderDate"].dt.to_period("M").astype(str)
monthly_sales = (
    monthly.groupby("Month", as_index=False)["Revenue"]
    .sum()
    .sort_values("Month")
)

# Prepare category and region data
category_sales = (
    filtered.groupby("Category", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)

region_sales = (
    filtered.groupby("Region", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Monthly Revenue")
    fig_monthly = px.line(
        monthly_sales,
        x="Month",
        y="Revenue",
        markers=True,
        title="Revenue Trend"
    )
    fig_monthly.update_layout(yaxis_title="Revenue (₹)")
    st.plotly_chart(fig_monthly, use_container_width=True)

with right:
    st.subheader("Revenue by Category")
    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Revenue",
        color="Category",
        title="Category Performance"
    )
    fig_category.update_layout(yaxis_title="Revenue (₹)")
    st.plotly_chart(fig_category, use_container_width=True)

st.subheader("Revenue by Region")
fig_region = px.pie(
    region_sales,
    names="Region",
    values="Revenue",
    hole=0.4
)
st.plotly_chart(fig_region, use_container_width=True)

# Data table
st.subheader("Filtered Sales Records")
st.dataframe(
    filtered.sort_values("OrderDate", ascending=False),
    use_container_width=True,
    hide_index=True
)

# Download filtered records
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Sales as CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.caption("Data source: cleaned sales records stored in SQLite.")
