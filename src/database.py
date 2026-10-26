"""
Safe Read-Only SQLite Database Connection and Query Execution Engine.

Provides secure database interaction:
- Validates all queries through AST guardrails before execution.
- Connects exclusively in read-only URI mode ('mode=ro') to physically prevent disk writes.
- Enforces execution limits and returns structured Pandas DataFrames.
"""

import os
import sqlite3
from typing import Tuple, Optional, Dict, Any, List
import pandas as pd
from src.sql_validator import validate_and_sanitize_sql


DEFAULT_DB_PATH = os.path.join("data", "superstore.db")


def get_readonly_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Opens a SQLite connection in immutable read-only mode via URI.
    Physical writes (INSERT, UPDATE, DROP) are rejected by SQLite at the OS level.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}. Run 'src/data_loader.py' first.")

    abs_path = os.path.abspath(db_path)
    # Windows paths need forward slashes for SQLite URI format
    uri_path = abs_path.replace("\\", "/")
    connection_uri = f"file:///{uri_path}?mode=ro"

    return sqlite3.connect(connection_uri, uri=True, timeout=10.0)


def execute_safe_query(
    sql: str,
    db_path: str = DEFAULT_DB_PATH,
) -> Tuple[Optional[pd.DataFrame], Optional[str], str]:
    """
    Validates, sanitizes, and safely executes an untrusted SQL query.

    Returns:
        (df: Optional[pd.DataFrame], error_message: Optional[str], executed_sql: str)
    """
    # 1. Security & AST Validation Layer
    is_valid, validation_error, safe_sql = validate_and_sanitize_sql(sql)
    if not is_valid:
        return None, validation_error, ""

    # 2. Database Execution Layer
    try:
        conn = get_readonly_connection(db_path)
        df = pd.read_sql_query(safe_sql, conn)
        conn.close()

        # Handle empty results
        if df.empty:
            return df, "Query executed successfully, but returned 0 rows.", safe_sql

        return df, None, safe_sql

    except sqlite3.OperationalError as e:
        return None, f"Database Operational Error: {e}", safe_sql
    except Exception as e:
        return None, f"Unexpected Execution Error: {e}", safe_sql


def get_table_info(table_name: str = "superstore", db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Retrieves row count and column metadata for the specified table.
    """
    conn = get_readonly_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [{"cid": row[0], "name": row[1], "type": row[2], "pk": row[5]} for row in cursor.fetchall()]

    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]

    conn.close()
    return {"table_name": table_name, "row_count": row_count, "columns": columns}
