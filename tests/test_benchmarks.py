"""
Automated verification test suite for Golden SQL Benchmarks.
Connects to data/superstore.db in read-only mode and executes all 10 benchmarks.
"""

import os
import json
import sqlite3
import pandas as pd


def test_golden_benchmarks():
    db_path = os.path.join("data", "superstore.db")
    benchmarks_path = os.path.join("data", "golden_benchmarks.json")

    assert os.path.exists(db_path), f"Database not found at {db_path}"
    assert os.path.exists(benchmarks_path), f"Benchmarks not found at {benchmarks_path}"

    with open(benchmarks_path, "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    assert len(benchmarks) == 10, f"Expected 10 benchmarks, found {len(benchmarks)}"

    # Connect to SQLite in read-only URI mode
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    print(f"Testing {len(benchmarks)} Golden SQL Benchmarks against {db_path}...\n")

    for bm in benchmarks:
        bm_id = bm["id"]
        category = bm["category"]
        question = bm["question"]
        sql = bm["sql"]

        # Execute query into DataFrame
        try:
            df = pd.read_sql_query(sql, conn)
            assert len(df) > 0, f"Query returned 0 rows for benchmark #{bm_id}"
            first_val = df.iloc[0, 0] if not df.empty else None
            print(f"[PASS] #{bm_id:02d} [{category}]: Success ({len(df)} rows returned). Sample: {first_val}")
        except Exception as e:
            conn.close()
            raise AssertionError(f"Failed benchmark #{bm_id} ({question}): {e}")

    conn.close()
    print("\n[SUCCESS] ALL 10 GOLDEN BENCHMARKS EXECUTED AND VERIFIED!")


if __name__ == "__main__":
    test_golden_benchmarks()
