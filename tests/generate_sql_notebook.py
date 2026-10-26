import os
import nbformat as nbf
from nbclient import NotebookClient

def generate_and_execute_sql_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    # Title & Metadata
    cells.append(nbf.v4.new_markdown_cell("""# Superstore Analytics - SQL Mastery & Ground-Truth Benchmarks
**Project**: Ask Your Data — AI Analytics Copilot  
**Phase**: Phase 4 — SQL Mastery & Verification  
**Database**: `data/superstore.db` (SQLite)

---

## 1. Why SQL Benchmarks Matter
Before deploying an LLM to generate SQL, we must have **ground truth**:
* An exact hand-crafted SQL query for each common business question.
* Verified numerical outputs.
* In Phase 10, we will feed these exact natural language questions to our AI and compare its generated SQL against these benchmarks.
"""))

    # Cell 1: Connect to database
    cells.append(nbf.v4.new_code_cell("""import sqlite3
import pandas as pd

# Connect to our SQLite database in read-only mode
conn = sqlite3.connect("file:../data/superstore.db?mode=ro", uri=True)

# Helper function to run a query and display as a formatted DataFrame
def run_query(sql_query):
    return pd.read_sql_query(sql_query, conn)

print("Connected to data/superstore.db in read-only mode.")
"""))

    # Benchmark 1
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 1: Overall Totals (Simple Aggregation)
**Question**: What are our overall total sales and total profit across all orders?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_1 = \"\"\"
SELECT 
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore;
\"\"\"
run_query(sql_1)
"""))

    # Benchmark 2
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 2: Grouping & Aggregation
**Question**: What are the total sales and profit in each region?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_2 = \"\"\"
SELECT 
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY region
ORDER BY total_sales DESC;
\"\"\"
run_query(sql_2)
"""))

    # Benchmark 3
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 3: Top Ranking (ORDER BY ... LIMIT)
**Question**: Which top 5 products generated the highest profit?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_3 = \"\"\"
SELECT 
    product_name,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY product_name
ORDER BY total_profit DESC
LIMIT 5;
\"\"\"
run_query(sql_3)
"""))

    # Benchmark 4
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 4: Worst Performers (Unprofitable Outliers)
**Question**: Which 5 products had the largest financial loss?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_4 = \"\"\"
SELECT 
    product_name,
    ROUND(SUM(profit), 2) AS total_loss
FROM superstore
GROUP BY product_name
ORDER BY total_loss ASC
LIMIT 5;
\"\"\"
run_query(sql_4)
"""))

    # Benchmark 5
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 5: Business Ratios & Margins
**Question**: What is the average discount and profit margin percentage by product category?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_5 = \"\"\"
SELECT 
    category,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_pct
FROM superstore
GROUP BY category
ORDER BY profit_margin_pct DESC;
\"\"\"
run_query(sql_5)
"""))

    # Benchmark 6
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 6: Time Analysis by Year (strftime)
**Question**: What was the total sales and total profit for each year?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_6 = \"\"\"
SELECT 
    strftime('%Y', order_date) AS order_year,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY order_year
ORDER BY order_year ASC;
\"\"\"
run_query(sql_6)
"""))

    # Benchmark 7
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 7: Multi-Condition Filtering (HAVING clause)
**Question**: Which products generated more than $5,000 in sales but had negative profit?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_7 = \"\"\"
SELECT 
    product_name,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY product_name
HAVING SUM(sales) > 5000 AND SUM(profit) < 0
ORDER BY total_profit ASC;
\"\"\"
run_query(sql_7)
"""))

    # Benchmark 8
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 8: Customer & Order Counts (COUNT DISTINCT)
**Question**: How many unique customers and total orders are there in each customer segment?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_8 = \"\"\"
SELECT 
    segment,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales
FROM superstore
GROUP BY segment
ORDER BY total_sales DESC;
\"\"\"
run_query(sql_8)
"""))

    # Benchmark 9
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 9: Monthly Trend Filtering (BETWEEN dates)
**Question**: What was the monthly sales trend in 2017?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_9 = \"\"\"
SELECT 
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(sales), 2) AS monthly_sales
FROM superstore
WHERE order_date BETWEEN '2017-01-01' AND '2017-12-31'
GROUP BY month
ORDER BY month ASC;
\"\"\"
run_query(sql_9)
"""))

    # Benchmark 10
    cells.append(nbf.v4.new_markdown_cell("""### Benchmark 10: Date Difference Calculation (julianday)
**Question**: What is the average shipping duration in days for each shipping mode?
"""))
    cells.append(nbf.v4.new_code_cell("""sql_10 = \"\"\"
SELECT 
    ship_mode,
    ROUND(AVG(julianday(ship_date) - julianday(order_date)), 2) AS avg_shipping_days
FROM superstore
GROUP BY ship_mode
ORDER BY avg_shipping_days ASC;
\"\"\"
run_query(sql_10)
"""))

    nb['cells'] = cells

    # Execute the notebook
    client = NotebookClient(nb, timeout=60, kernel_name='ai-anaylytics-env', resources={'metadata': {'path': 'notebooks'}})
    print("Executing SQL benchmark notebook cells...")
    client.execute()

    notebook_file = os.path.join("notebooks", "02_sql_benchmarks.ipynb")
    with open(notebook_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[SUCCESS] SQL benchmark notebook generated and executed at {notebook_file}")

if __name__ == "__main__":
    generate_and_execute_sql_notebook()
