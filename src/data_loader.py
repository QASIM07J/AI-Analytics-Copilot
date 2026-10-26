"""
Data Loader and ETL Pipeline for Superstore Dataset.

Extracts raw records from 'Sample - Superstore.csv',
Transforms columns into snake_case and dates into ISO-8601,
Loads data into an indexed SQLite database at 'data/superstore.db'.
"""

import os
import sqlite3
import pandas as pd


def clean_superstore_data(raw_csv_path: str) -> pd.DataFrame:
    """
    Extracts and transforms the raw Superstore CSV:
    - Normalizes column names to clean snake_case.
    - Parses dates and converts them to ISO-8601 strings (YYYY-MM-DD).
    - Preserves Postal Code as text (for ZIP codes).
    - Ensures numerical metrics are properly typed floats and ints.
    """
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Raw dataset not found at: {raw_csv_path}")

    # Read raw CSV with fallback encoding for special characters
    df = pd.read_csv(raw_csv_path, encoding="windows-1252")

    # Column name mapping dictionary to snake_case
    column_mapping = {
        "Row ID": "row_id",
        "Order ID": "order_id",
        "Order Date": "order_date",
        "Ship Date": "ship_date",
        "Ship Mode": "ship_mode",
        "Customer ID": "customer_id",
        "Customer Name": "customer_name",
        "Segment": "segment",
        "Country": "country",
        "City": "city",
        "State": "state",
        "Postal Code": "postal_code",
        "Region": "region",
        "Product ID": "product_id",
        "Category": "category",
        "Sub-Category": "sub_category",
        "Product Name": "product_name",
        "Sales": "sales",
        "Quantity": "quantity",
        "Discount": "discount",
        "Profit": "profit",
    }

    df = df.rename(columns=column_mapping)

    # Transform dates to ISO-8601 standard format (YYYY-MM-DD)
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")

    # Format postal_code as string without float decimals
    df["postal_code"] = df["postal_code"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)

    # Cast numeric columns explicitly
    df["row_id"] = df["row_id"].astype(int)
    df["quantity"] = df["quantity"].astype(int)
    df["sales"] = df["sales"].astype(float).round(4)
    df["discount"] = df["discount"].astype(float).round(4)
    df["profit"] = df["profit"].astype(float).round(4)

    return df


def create_and_load_database(
    df: pd.DataFrame,
    db_path: str = os.path.join("data", "superstore.db"),
    table_name: str = "superstore",
) -> None:
    """
    Creates SQLite schema with proper data types, primary key,
    inserts records, and builds performance indexes.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # If database file exists, connect and recreate table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # DDL: Define explicit SQL schema
    create_table_sql = f"""
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE {table_name} (
        row_id INTEGER PRIMARY KEY,
        order_id TEXT NOT NULL,
        order_date TEXT NOT NULL,
        ship_date TEXT NOT NULL,
        ship_mode TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        segment TEXT NOT NULL,
        country TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        postal_code TEXT,
        region TEXT NOT NULL,
        product_id TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT NOT NULL,
        product_name TEXT NOT NULL,
        sales REAL NOT NULL,
        quantity INTEGER NOT NULL,
        discount REAL NOT NULL,
        profit REAL NOT NULL
    );
    """
    cursor.executescript(create_table_sql)

    # Load cleaned DataFrame into SQLite table
    df.to_sql(table_name, conn, if_exists="append", index=False)

    # Build performance indexes on frequently filtered / grouped columns
    index_sql = f"""
    CREATE INDEX IF NOT EXISTS idx_{table_name}_order_date ON {table_name}(order_date);
    CREATE INDEX IF NOT EXISTS idx_{table_name}_region ON {table_name}(region);
    CREATE INDEX IF NOT EXISTS idx_{table_name}_category ON {table_name}(category);
    CREATE INDEX IF NOT EXISTS idx_{table_name}_sub_category ON {table_name}(sub_category);
    CREATE INDEX IF NOT EXISTS idx_{table_name}_customer_id ON {table_name}(customer_id);
    """
    cursor.executescript(index_sql)

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Database created and populated at: {db_path}")


def run_etl(
    raw_csv_path: str = "Sample - Superstore.csv",
    db_path: str = os.path.join("data", "superstore.db"),
) -> None:
    """Runs the complete end-to-end ETL process."""
    print(f"Starting ETL from '{raw_csv_path}' -> '{db_path}'...")
    df_clean = clean_superstore_data(raw_csv_path)
    print(f"Extracted and transformed {len(df_clean):,} records.")
    create_and_load_database(df_clean, db_path)
    print("ETL pipeline completed successfully.")


if __name__ == "__main__":
    run_etl()
