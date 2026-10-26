"""
Test suite to verify SQLite database integrity and schema correctness.
"""

import os
import sqlite3
import pandas as pd


def test_database_integrity():
    db_path = os.path.join("data", "superstore.db")
    assert os.path.exists(db_path), f"Database file does not exist at {db_path}"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Verify Table Existence
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='superstore';")
    table = cursor.fetchone()
    assert table is not None, "Table 'superstore' does not exist in database"
    print("[PASS] Table 'superstore' exists.")

    # 2. Verify Exact Row Count
    cursor.execute("SELECT COUNT(*) FROM superstore;")
    row_count = cursor.fetchone()[0]
    assert row_count == 9994, f"Expected 9,994 rows, but found {row_count}"
    print(f"[PASS] Exact row count verified: {row_count:,} rows.")

    # 3. Verify Column Schema & Names (snake_case)
    cursor.execute("PRAGMA table_info(superstore);")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]

    expected_columns = [
        "row_id", "order_id", "order_date", "ship_date", "ship_mode",
        "customer_id", "customer_name", "segment", "country", "city",
        "state", "postal_code", "region", "product_id", "category",
        "sub_category", "product_name", "sales", "quantity", "discount", "profit"
    ]
    assert column_names == expected_columns, f"Columns do not match expected snake_case names.\nFound: {column_names}"
    print(f"[PASS] All {len(column_names)} column names verified in snake_case format.")

    # 4. Verify Primary Key
    pk_col = [col[1] for col in columns_info if col[5] == 1]
    assert pk_col == ["row_id"], f"Expected primary key 'row_id', got {pk_col}"
    print("[PASS] Primary key 'row_id' correctly configured.")

    # 5. Verify Date Format (ISO-8601 YYYY-MM-DD)
    cursor.execute("SELECT order_date, ship_date FROM superstore LIMIT 10;")
    sample_dates = cursor.fetchall()
    for o_date, s_date in sample_dates:
        assert len(o_date) == 10 and o_date[4] == '-' and o_date[7] == '-', f"Invalid order_date format: {o_date}"
        assert len(s_date) == 10 and s_date[4] == '-' and s_date[7] == '-', f"Invalid ship_date format: {s_date}"
    print("[PASS] Date fields verified in ISO-8601 format (YYYY-MM-DD).")

    # 6. Verify Indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='superstore';")
    indexes = [idx[0] for idx in cursor.fetchall()]
    expected_indexes = [
        "idx_superstore_order_date",
        "idx_superstore_region",
        "idx_superstore_category",
        "idx_superstore_sub_category",
        "idx_superstore_customer_id"
    ]
    for exp_idx in expected_indexes:
        assert exp_idx in indexes, f"Missing expected index: {exp_idx}"
    print(f"[PASS] All {len(expected_indexes)} performance indexes verified.")

    # 7. Test a Sample SQL Aggregation
    cursor.execute("SELECT region, ROUND(SUM(sales), 2), ROUND(SUM(profit), 2) FROM superstore GROUP BY region ORDER BY SUM(sales) DESC;")
    results = cursor.fetchall()
    assert len(results) == 4, f"Expected 4 regions, got {len(results)}"
    print(f"[PASS] Sample SQL aggregation query executed successfully:")
    for region, sales, profit in results:
        print(f"       Region: {region:<8} | Sales: ${sales:>10,.2f} | Profit: ${profit:>9,.2f}")

    conn.close()
    print("\n[SUCCESS] ALL DATABASE INTEGRITY TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_database_integrity()
