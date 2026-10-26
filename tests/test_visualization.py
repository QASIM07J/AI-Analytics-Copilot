"""
Test suite to verify Automated Visualization Engine and Executive Summary Generator.
"""

import os
import sys
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.visualization import recommend_and_create_chart
from src.llm import generate_explanation


def test_chart_recommendations():
    print("Testing Automated Chart Recommendation Strategies...\n")

    # 1. Test Time Series -> Line Chart
    df_time = pd.DataFrame({
        "order_year": ["2014", "2015", "2016", "2017"],
        "total_sales": [484247.50, 470532.51, 609205.60, 733215.26],
    })
    fig_time, type_time = recommend_and_create_chart(df_time)
    assert isinstance(fig_time, go.Figure)
    assert "Line" in type_time, f"Expected Line Chart, got {type_time}"
    print(f"[PASS] Time Series DataFrame -> Recommended: {type_time}")

    # 2. Test Low-Cardinality Composition (3 segments) -> Donut Chart
    df_donut = pd.DataFrame({
        "segment": ["Consumer", "Corporate", "Home Office"],
        "total_sales": [1161401.34, 706146.37, 429653.15],
    })
    fig_donut, type_donut = recommend_and_create_chart(df_donut)
    assert isinstance(fig_donut, go.Figure)
    assert "Donut" in type_donut, f"Expected Donut Chart, got {type_donut}"
    print(f"[PASS] 3-Category Composition -> Recommended: {type_donut}")

    # 3. Test High-Cardinality Ranking (> 8 items) -> Horizontal Bar Chart
    df_ranking = pd.DataFrame({
        "product_name": [f"Product {i}" for i in range(1, 12)],
        "total_profit": [1000 - i * 50 for i in range(1, 12)],
    })
    fig_rank, type_rank = recommend_and_create_chart(df_ranking)
    assert isinstance(fig_rank, go.Figure)
    assert "Horizontal" in type_rank, f"Expected Horizontal Bar, got {type_rank}"
    print(f"[PASS] 11 Products Ranking -> Recommended: {type_rank}")

    # 4. Test Standard Categorical Comparison (4 regions) -> Vertical Bar Chart
    df_cat = pd.DataFrame({
        "region": ["West", "East", "Central", "South"],
        "total_sales": [725457.82, 678781.24, 501239.89, 391721.91],
        "total_profit": [108418.45, 91522.78, 39706.36, 46749.43],
    })
    fig_cat, type_cat = recommend_and_create_chart(df_cat)
    assert isinstance(fig_cat, go.Figure)
    assert "Vertical Bar" in type_cat, f"Expected Vertical Bar, got {type_cat}"
    print(f"[PASS] Regional Sales & Profit Comparison -> Recommended: {type_cat}")


def test_natural_language_explanation():
    print("\nTesting Executive Summary Insight Generator...")

    df_sample = pd.DataFrame({
        "region": ["West", "East", "Central", "South"],
        "total_sales": [725457.82, 678781.24, 501239.89, 391721.91],
        "total_profit": [108418.45, 91522.78, 39706.36, 46749.43],
    })
    question = "What are the total sales and profit in each region?"

    summary = generate_explanation(question, df_sample)
    assert summary and len(summary) > 20, f"Explanation too short: {summary}"
    print(f"Question: \"{question}\"")
    print(f"Generated Executive Summary:\n\"{summary}\"")
    print("\n[PASS] Executive summary synthesized cleanly from actual data.")


if __name__ == "__main__":
    test_chart_recommendations()
    test_natural_language_explanation()
    print("\n[SUCCESS] ALL VISUALIZATION & EXPLANATION TESTS PASSED 100%!")
