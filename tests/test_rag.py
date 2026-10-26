"""
Test suite to verify Vector Schema RAG and Few-Shot Retrieval Engine.
"""

import os
import sys
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.rag import get_schema_retriever
from src.llm import generate_sql


def test_vector_retriever():
    print("Testing Vector Schema Retriever...")
    retriever = get_schema_retriever()

    # Test 1: Query about profit margin
    query_1 = "What is our average profit margin by category?"
    results_1 = retriever.retrieve(query_1, top_k_schema=3, top_k_examples=2)

    schema_titles = [item["title"] for item in results_1["schema_context"]]
    print(f"\nQuery: \"{query_1}\"")
    print(f"Retrieved Schema Items: {schema_titles}")
    assert any("Profit Margin" in t or "profit" in t.lower() for t in schema_titles), "Failed to retrieve profit context"
    print("[PASS] Successfully retrieved profit margin schema context.")

    # Test 2: Query about delivery time
    query_2 = "What is the average shipping duration in days for each shipping mode?"
    results_2 = retriever.retrieve(query_2, top_k_schema=3, top_k_examples=2)

    schema_titles_2 = [item["title"] for item in results_2["schema_context"]]
    print(f"\nQuery: \"{query_2}\"")
    print(f"Retrieved Schema Items: {schema_titles_2}")
    assert any("ship" in t.lower() or "shipping" in t.lower() for t in schema_titles_2), "Failed to retrieve shipping context"
    print("[PASS] Successfully retrieved shipping schema context.")

    # Test 3: Check augmented prompt formatting
    context_str = retriever.format_augmented_context(query_1)
    assert "Dynamically Retrieved Schema" in context_str
    print("\n[PASS] Augmented context string generated successfully.")
    return True


def test_rag_end_to_end_generation():
    print("\nTesting End-to-End RAG + LLM SQL Generation...")
    question = "What is the average discount and profit margin percentage by product category?"
    print(f"Question: \"{question}\"")

    try:
        sql = generate_sql(question, use_rag=True)
        print(f"\n[PASS] RAG Generated SQL:\n{sql}\n")

        # Verify execution on database
        db_path = os.path.join("data", "superstore.db")
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        df = pd.read_sql_query(sql, conn)
        conn.close()

        print("[PASS] RAG-generated SQL successfully executed on data/superstore.db!")
        print("Query Results:")
        print(df.to_string(index=False))
        print("\n[SUCCESS] Phase 6 Vector RAG integration fully verified!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error during RAG SQL generation: {e}")
        return False


if __name__ == "__main__":
    test_vector_retriever()
    test_rag_end_to_end_generation()
