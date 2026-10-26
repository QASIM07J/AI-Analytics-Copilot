"""
Security and Guardrail Test Suite.
Verifies AST validation, injection prevention, keyword literal preservation,
safety LIMIT injection, and read-only database execution.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sql_validator import validate_and_sanitize_sql
from src.database import execute_safe_query, get_table_info


def test_valid_select_query():
    sql = "SELECT region, ROUND(SUM(sales), 2) AS total_sales FROM superstore GROUP BY region"
    is_valid, error, safe_sql = validate_and_sanitize_sql(sql)
    assert is_valid, f"Valid query failed validation: {error}"
    assert "LIMIT 1000" in safe_sql, "Safety LIMIT not appended"
    print("[PASS] Valid SELECT query passes and gets safety LIMIT appended.")


def test_blocked_destructive_operations():
    destructive_queries = [
        ("DROP TABLE superstore;", "DROP"),
        ("DELETE FROM superstore WHERE row_id = 1;", "DELETE"),
        ("UPDATE superstore SET profit = 9999;", "UPDATE"),
        ("INSERT INTO superstore (row_id) VALUES (99999);", "INSERT"),
        ("ALTER TABLE superstore ADD COLUMN hacker TEXT;", "ALTER"),
    ]

    for sql, op in destructive_queries:
        is_valid, error, _ = validate_and_sanitize_sql(sql)
        assert not is_valid, f"Destructive {op} query was not blocked!"
        print(f"[PASS] Successfully blocked destructive operation: {op}")


def test_blocked_stacked_sql_injection():
    # An attacker tries to run a harmless SELECT, followed by a destructive command
    stacked_sql = "SELECT 1; DROP TABLE superstore;"
    is_valid, error, _ = validate_and_sanitize_sql(stacked_sql)
    assert not is_valid, "Stacked SQL injection attack was not blocked!"
    assert "Multiple stacked SQL statements are forbidden" in error
    print("[PASS] Successfully blocked stacked SQL injection attempt.")


def test_ast_literal_preservation():
    # The word 'Drop' appears inside a string literal, NOT as a SQL command.
    # AST parser must recognize this as a valid SELECT.
    tricky_sql = "SELECT * FROM superstore WHERE product_name = 'Bush Somerset Collection Drop-Leaf Table' LIMIT 5;"
    is_valid, error, safe_sql = validate_and_sanitize_sql(tricky_sql)
    assert is_valid, f"AST falsely blocked keyword inside string literal: {error}"
    assert "LIMIT 5" in safe_sql
    print("[PASS] AST correctly recognizes 'Drop' inside string literal as harmless data.")


def test_safe_execution_against_database():
    query = "SELECT region, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit FROM superstore GROUP BY region ORDER BY sales DESC;"
    df, error, executed_sql = execute_safe_query(query)

    assert error is None, f"Execution failed with error: {error}"
    assert isinstance(df, pd.DataFrame), "Did not return a DataFrame"
    assert len(df) == 4, f"Expected 4 regions, got {len(df)}"
    print("[PASS] Safe query execution executed successfully:")
    print(df.to_string(index=False))


def test_table_info():
    info = get_table_info()
    assert info["row_count"] == 9994, f"Expected 9,994 rows, found {info['row_count']}"
    assert len(info["columns"]) == 21, f"Expected 21 columns, found {len(info['columns'])}"
    print(f"[PASS] Table info verified: {info['table_name']} ({info['row_count']:,} rows, {len(info['columns'])} columns).")


if __name__ == "__main__":
    print("Running Phase 7 Security & Guardrail Test Suite...\n")
    test_valid_select_query()
    test_blocked_destructive_operations()
    test_blocked_stacked_sql_injection()
    test_ast_literal_preservation()
    test_safe_execution_against_database()
    test_table_info()
    print("\n[SUCCESS] ALL SECURITY GUARDRAIL TESTS PASSED 100%!")
