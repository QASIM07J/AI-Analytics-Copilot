import os
import nbformat as nbf
from nbclient import NotebookClient

def generate_and_execute_eda_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    # Title & Metadata
    cells.append(nbf.v4.new_markdown_cell("""# Superstore Dataset - Exploratory Data Analysis (EDA)
**Project**: Ask Your Data — AI Analytics Copilot  
**Phase**: Phase 2 — Exploratory Data Analysis  
**Environment**: Python 3.11 (`AI-Anaylytics-env`)

---

## 1. Objective of this Notebook
Before loading data into a SQL database or building an AI copilot, we must thoroughly understand the raw data:
1. **Schema & Column Names**: What business attributes exist?
2. **Data Types**: Are dates, numbers, and categories stored in suitable formats?
3. **Data Quality**: Are there missing values (nulls) or duplicate records?
4. **Distributions & Outliers**: Are profits negative? What is the date range?
5. **Database Normalization Needs**: How should column names and data types be standardized for SQLite?
"""))

    # Cell 1: Environment & Imports
    cells.append(nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np

# Configure Pandas display options for readable outputs
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 1000)

print(f"Pandas Version: {pd.__version__}")
print(f"NumPy Version:  {np.__version__}")
"""))

    # Section 2 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 2. Loading the Raw Dataset
We load `Sample - Superstore.csv` from the project root. Notice that we do not alter or overwrite the original file.
"""))

    # Cell 2: Load data
    cells.append(nbf.v4.new_code_cell("""dataset_path = os.path.join("..", "Sample - Superstore.csv")

# Read CSV with Windows encoding fallback for special characters
df = pd.read_csv(dataset_path, encoding='windows-1252')
print(f"Dataset Dimensions: {df.shape[0]:,} rows x {df.shape[1]} columns")
df.head(5)
"""))

    # Section 3 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 3. Column Data Types & Memory Usage
Pandas assigns a data type (`dtype`) to each column.
* `int64` / `float64`: Numeric values.
* `object`: Text strings or mixed values.
Notice that `Order Date` and `Ship Date` are initially detected as `object` (strings), not timestamps.
"""))

    # Cell 3: Info & dtypes
    cells.append(nbf.v4.new_code_cell("""df.info()
"""))

    # Section 4 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 4. Missing Values & Duplicate Records Check
In data engineering, null values and duplicate rows can cause incorrect SQL aggregations or faulty joins.
"""))

    # Cell 4: Nulls and duplicates
    cells.append(nbf.v4.new_code_cell("""missing_counts = df.isna().sum()
duplicate_rows = df.duplicated().sum()

print("--- Missing Values per Column ---")
if missing_counts.sum() == 0:
    print("No missing values found in any column!")
else:
    print(missing_counts[missing_counts > 0])

print(f"\\nTotal exact duplicate rows: {duplicate_rows}")
"""))

    # Section 5 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 5. Statistical Summary of Numeric Metrics
Let's analyze the business metrics: `Sales`, `Quantity`, `Discount`, and `Profit`.
* Is `Profit` always positive? (Look at `min`)
* What is the range of `Discount`?
"""))

    # Cell 5: Describe numeric
    cells.append(nbf.v4.new_code_cell("""df[['Sales', 'Quantity', 'Discount', 'Profit']].describe().T
"""))

    # Section 6 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 6. Categorical Attributes & Cardinality
Let's check the distinct count (cardinality) of key business dimensions:
* `Category` and `Sub-Category`
* `Segment`
* `Region` and `Ship Mode`
"""))

    # Cell 6: Value counts
    cells.append(nbf.v4.new_code_cell("""categorical_cols = ['Category', 'Sub-Category', 'Segment', 'Region', 'Ship Mode']
for col in categorical_cols:
    print(f"=== {col} (Unique count: {df[col].nunique()}) ===")
    print(df[col].value_counts().to_dict())
    print()
"""))

    # Section 7 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 7. Date Format & Timeline Analysis
In SQL databases (like SQLite), dates are best stored in ISO-8601 standard format (`YYYY-MM-DD`) so they can be filtered, indexed, and sorted lexicographically.
Let's inspect the date range in the Superstore dataset.
"""))

    # Cell 7: Date inspection
    cells.append(nbf.v4.new_code_cell("""order_dates = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
print(f"Earliest Order Date: {order_dates.min().strftime('%Y-%m-%d')}")
print(f"Latest Order Date:   {order_dates.max().strftime('%Y-%m-%d')}")
print(f"Total Date Span:     {(order_dates.max() - order_dates.min()).days} days (~4 years)")
"""))

    # Section 8 Markdown
    cells.append(nbf.v4.new_markdown_cell("""## 8. Summary of Findings & Next Steps (Phase 3 Preparation)

### Key Findings:
1. **Row Count**: Exactly 9,994 transaction records across 21 columns.
2. **Data Cleanliness**: Zero null values across all columns and zero exact duplicate rows.
3. **Negative Profits**: Profits range from -$6,599.98 to +$8,399.98. The AI copilot will need to understand that profit can be negative (losses).
4. **Dates**: Raw format is `M/D/YYYY`. SQLite doesn't have a native `DATE` storage class; it stores dates as ISO text (`YYYY-MM-DD`). We must standardize them during ETL in Phase 3.
5. **Column Names**: Column names have spaces and hyphens (e.g., `Order Date`, `Sub-Category`, `Row ID`). In SQL, spaces require square brackets `[Order Date]` or quotes. In Phase 3, we should convert column names into standard `snake_case` (`order_date`, `sub_category`, `sales`, etc.) for seamless, clean SQL generation.
"""))

    nb['cells'] = cells

    # Execute the notebook using the kernel so outputs are generated and saved
    client = NotebookClient(nb, timeout=60, kernel_name='ai-anaylytics-env', resources={'metadata': {'path': 'notebooks'}})
    print("Executing notebook cells to pre-compute outputs...")
    client.execute()

    # Save notebook
    os.makedirs("notebooks", exist_ok=True)
    notebook_file = os.path.join("notebooks", "01_data_exploration.ipynb")
    with open(notebook_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[SUCCESS] Notebook successfully generated and executed at {notebook_file}")

if __name__ == "__main__":
    generate_and_execute_eda_notebook()
