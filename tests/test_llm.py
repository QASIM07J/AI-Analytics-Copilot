"""
Test suite to verify OpenRouter LLM client and Text-to-SQL generation.
"""

import os
import sys
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.llm import generate_sql, clean_sql_output, get_llm_client


def test_clean_sql_output():
    """Verifies that markdown code blocks and conversational fluff are stripped cleanly."""
    raw_markdown = "```sql\nSELECT region, SUM(sales) FROM superstore GROUP BY region;\n```"
    cleaned = clean_sql_output(raw_markdown)
    assert cleaned == "SELECT region, SUM(sales) FROM superstore GROUP BY region;", f"Failed cleaning: {cleaned}"
    print("[PASS] SQL cleaner successfully strips markdown fences.")


def test_openrouter_llm_generation():
    """Tests the live OpenRouter API connection with a business question."""
    key = os.getenv("OPENROUTER_API_KEY")

    if not key or key == "sk-or-v1-your_token_here" or not key.startswith("sk-or-v1-"):
        print("\n[ATTENTION REQUIRED] OPENROUTER_API_KEY is not yet set in .env!")
        print("Please add your key in .env:\nOPENROUTER_API_KEY=sk-or-v1-...\nand re-run.")
        return False

    print("\nConnecting to OpenRouter Free Inference API...")
    question = "What are the total sales and total profit in each region?"
    print(f"Question: \"{question}\"")

    try:
        sql = generate_sql(question)
        print(f"\n[PASS] Model Generated SQL:\n{sql}\n")

        # Verify that the generated SQL executes on our actual SQLite database
        db_path = os.path.join("data", "superstore.db")
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        df = pd.read_sql_query(sql, conn)
        conn.close()

        print("[PASS] Generated SQL successfully executed on data/superstore.db!")
        print("Query Results:")
        print(df.to_string(index=False))
        print("\n[SUCCESS] OpenRouter LLM integration fully verified!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error communicating with OpenRouter API: {e}")
        return False


if __name__ == "__main__":
    test_clean_sql_output()
    test_openrouter_llm_generation()
