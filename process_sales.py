
import pandas as pd
import sqlite3
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "sales.csv"
OUTPUT_FILE = BASE_DIR / "output" / "cleaned_sales.csv"
DB_FILE = BASE_DIR / "sales.db"

# 1. EXTRACT: Load raw sales data
df = pd.read_csv(INPUT_FILE)

print("Original data:", len(df), "rows")

# 2. TRANSFORM: Clean and validate data
df.columns = df.columns.str.strip()
df = df.drop_duplicates()

required_columns = [
    "OrderID", "OrderDate", "Product", "Category",
    "Region", "Quantity", "UnitPrice"
]

missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Convert columns to appropriate data types
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

# Remove rows with missing or invalid values
df = df.dropna(subset=required_columns)

# Keep only valid sales records
df = df[
    (df["Quantity"] > 0) &
    (df["UnitPrice"] >= 0) &
    (df["Product"].astype(str).str.strip() != "") &
    (df["Category"].astype(str).str.strip() != "") &
    (df["Region"].astype(str).str.strip() != "")
].copy()

# Calculate revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Format dates for export
df["OrderDate"] = df["OrderDate"].dt.strftime("%Y-%m-%d")

# 3. LOAD: Save cleaned data to CSV and SQLite
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

with sqlite3.connect(DB_FILE) as connection:
    df.to_sql("sales", connection, if_exists="replace", index=False)

    # Run SQL analytics
    summary = pd.read_sql_query("""
        SELECT
            COUNT(*) AS total_orders,
            SUM(Quantity) AS units_sold,
            ROUND(SUM(Revenue), 2) AS total_revenue
        FROM sales
    """, connection)

    category_summary = pd.read_sql_query("""
        SELECT Category,
               SUM(Revenue) AS revenue
        FROM sales
        GROUP BY Category
        ORDER BY revenue DESC
    """, connection)

print("\nETL completed successfully!")
print("Clean records:", len(df))
print("Clean CSV:", OUTPUT_FILE)
print("Database:", DB_FILE)

print("\nSALES SUMMARY")
print(summary.to_string(index=False))

print("\nREVENUE BY CATEGORY")
print(category_summary.to_string(index=False))
