# Ask Your Data: AI Analytics Copilot

An enterprise-grade, end-to-end Text-to-SQL AI analytics system built with Python, SQLite, OpenRouter LLM, LangChain FastEmbed Schema RAG, Abstract Syntax Tree (AST) SQL guardrails, Plotly dynamic charting, and a Streamlit SaaS interface.

The application translates complex natural-language business questions into verified, read-only SQL queries, executes them safely against an indexed relational database, renders context-aware interactive visualizations, and synthesizes executive business takeaways.

---

## Architectural Overview

The system uses a defense-in-depth architecture that decouples semantic query formulation, schema retrieval, security verification, and analytical presentation.

```
+-------------------------------------------------------------------+
|                        User Interface                             |
|        Streamlit Web Application (Modern SaaS Light Theme)        |
+---------------------------------+---------------------------------+
                                  | Natural Language Question
                                  v
+-------------------------------------------------------------------+
|                   Schema RAG Retrieval Engine                     |
|    FastEmbed (bge-small-en-v1.5) Dense Vector Search (384-d)      |
|    Selects relevant columns, KPI definitions, and few-shot pairs  |
+---------------------------------+---------------------------------+
                                  | Retrieved Context + Question
                                  v
+-------------------------------------------------------------------+
|                    Text-to-SQL LLM Engine                         |
|     OpenRouter Client (Deterministic Coding LLM, Temp = 0.0)      |
|     Synthesizes clean ANSI/SQLite SELECT statements               |
+---------------------------------+---------------------------------+
                                  | Raw SQL String
                                  v
+-------------------------------------------------------------------+
|                 AST Security & Guardrail Engine                   |
|        sqlglot Abstract Syntax Tree Parser & Validator            |
|  - Blocks DDL/DML mutations (INSERT, UPDATE, DELETE, DROP, ALTER) |
|  - Prohibits stacked multi-statements, comments, and attachments  |
|  - Injects safety constraints (automatic LIMIT 1000)              |
+---------------------------------+---------------------------------+
                                  | Validated AST-Verified SQL
                                  v
+-------------------------------------------------------------------+
|                Database Query Execution Layer                     |
|           SQLite Database (Sample Superstore, Indexed)            |
|          Enforces filesystem read-only mode (?mode=ro)            |
+---------------------------------+---------------------------------+
                                  | Result DataFrame
                                  v
+-------------------------------------------------------------------+
|               Executive Insights & Visualization                  |
|  - Automated Plotly Chart Recommendation (Line, Donut, Bar)       |
|  - Natural-language business takeaway generation                  |
|  - Tabular data export (CSV) and full SQL audit telemetry         |
+-------------------------------------------------------------------+
```

---

## Benchmark Performance and Verification

The system was evaluated against a verified 10-query Golden Benchmark dataset reflecting production retail analytics scenarios (multi-table aggregations, date filtering, ranked groupings, and negative margin detection).

### Evaluation Metrics

| Metric | Result | Description |
| :--- | :--- | :--- |
| Execution Accuracy (EX) | 100.0% (10/10 Passed) | Generated SQL executed cleanly and matched ground-truth data structures |
| Adversarial Security Resilience | 100.0% (8/8 Blocked) | Zero malicious injection attacks penetrated the AST security engine |
| Mean Query Latency | 3.69 seconds | Average end-to-end latency across semantic search, generation, and query execution |
| Table Record Count | 9,994 rows | Normalized, cleaned, and indexed retail transactions |

### Adversarial Stress Testing Results

The AST guardrail engine was subjected to targeted adversarial SQL attack vectors:

- Stacked query injection (`SELECT 1; DROP TABLE superstore;`): Blocked
- Table drop attempts (`DROP TABLE superstore;`): Blocked
- Data mutation (`DELETE FROM superstore WHERE row_id = 1;`): Blocked
- Data insertion (`INSERT INTO superstore VALUES (...);`): Blocked
- Schema modification (`ALTER TABLE superstore ADD COLUMN pwned TEXT;`): Blocked
- Database attachment (`ATTACH DATABASE ':memory:' AS hack;`): Blocked
- Pragma inspection (`PRAGMA table_info(superstore);`): Blocked
- String preservation test (`SELECT * FROM superstore WHERE product_name LIKE '%Drop-Leaf%';`): Allowed safely

---

## Key Engineering Features

### 1. Schema Vector RAG via FastEmbed
Instead of stuffing the full database schema into the LLM system prompt, the system indexes 21 column definitions, business KPI formulas (such as Profit Margin % and Shipping Duration), and verified few-shot benchmarks using `fastembed` (`bge-small-en-v1.5`, 384-dimensional dense vectors). FastEmbed operates directly on CPU RAM via ONNX Runtime without large deep learning framework dependencies.

### 2. Abstract Syntax Tree (AST) Security Guardrails
Text-to-SQL agents cannot rely on basic regex filtering. Regex fails to differentiate between a destructive command and a product description such as `'Drop-Leaf Table'`. This engine uses `sqlglot` to parse generated SQL into an Abstract Syntax Tree:
- Verifies that the root node is strictly `exp.Select`.
- Traverses all child nodes to ensure absence of mutations (`exp.Drop`, `exp.Delete`, `exp.Update`, `exp.Insert`, `exp.Alter`).
- Restricts statement count to exactly 1 to eliminate stacked SQL injection.
- Dynamically appends a `LIMIT 1000` clause to unbounded queries.

### 3. Read-Only Storage Engine
The database execution layer connects to SQLite using URI read-only parameters:
```python
sqlite3.connect("file:data/superstore.db?mode=ro", uri=True)
```
Even in the theoretical event that malicious SQL bypassed the AST parser, the operating system kernel and SQLite engine refuse write operations at the file level.

### 4. Automated Visualization Recommendation
The visualization module inspects query return schemas to automatically select the optimal chart:
- Time-series data: Multi-line trend charts with hover tooltips.
- Categorical comparisons (up to 4 items): Composition donut charts.
- High-cardinality rankings (more than 8 items): Horizontal bar charts with sorted axes.
- Standard categorical metrics: Grouped vertical bar charts.
- Custom modern SaaS light aesthetic with clean transparent backgrounds, soft gridlines, and high-contrast typography.

### 5. Interactive Web Interface
Built with Streamlit and styled with a modern light design system:
- Zero black or dark backgrounds for seamless legibility in all lighting conditions.
- Integrated LatticeLoader displaying live execution time and completion state.
- Expandable Executive Business Insights card presenting key numerical takeaways.
- Full transparency SQL and performance audit drawer showing executed statements and latency.

---

## Technology Stack

- Language: Python 3.11
- Relational Database: SQLite with composite performance indexes
- Vector Embeddings: FastEmbed (`bge-small-en-v1.5` dense ONNX embeddings)
- LLM Provider: OpenRouter API (`https://openrouter.ai/api/v1`)
- SQL Parser & Security: `sqlglot` AST engine
- Interactive Visualizations: Plotly Express and Graph Objects
- Web Framework: Streamlit
- Data Manipulation: Pandas and NumPy
- Quality Assurance: Pytest and automated evaluation runners

---

## Repository Structure

```
.
|-- .env.example              # Sanitized environment template
|-- .gitignore                # Protects secrets, local notes, and databases
|-- README.md                 # Production documentation
|-- requirements.txt          # Pinned production dependencies
|-- app.py                    # Streamlit web application
|-- Sample - Superstore.csv   # Raw benchmark dataset (9,994 rows)
|-- data/
|   |-- golden_benchmarks.json  # 10 ground-truth query benchmarks
|   |-- schema_metadata.json    # Column definitions and KPI formulas
|   `-- evaluation_report.json  # Automated benchmark test results
|-- notebooks/
|   |-- 01_data_exploration.ipynb  # Exploratory Data Analysis (EDA)
|   `-- 02_sql_benchmarks.ipynb    # SQL verification benchmarks
|-- src/
|   |-- __init__.py
|   |-- data_loader.py        # Ingestion and SQLite ETL pipeline
|   |-- database.py           # Read-only database query execution
|   |-- llm.py                # OpenRouter Text-to-SQL and takeaway client
|   |-- rag.py                # FastEmbed dense vector retrieval
|   |-- sql_validator.py      # sqlglot AST security parser
|   `-- visualization.py      # Automated Plotly chart generator
`-- tests/
    |-- __init__.py
    |-- test_benchmarks.py    # Unit tests for golden benchmark queries
    |-- test_copilot.py       # End-to-end evaluation & adversarial stress tests
    |-- test_database.py      # Database schema and index validation
    |-- test_llm.py           # Text-to-SQL generation integration test
    |-- test_rag.py           # Semantic schema retrieval unit test
    |-- test_security.py      # AST guardrail and injection defense tests
    `-- test_visualization.py # Plotly visualization recommendation tests
```

---

## Getting Started

### 1. Prerequisites
- Python 3.11 installed.
- Git installed.
- An OpenRouter API key (free tier available at [OpenRouter](https://openrouter.ai/)).

### 2. Clone the Repository
```bash
git clone https://github.com/QASIM07J/AI-Analytics-Copilot.git
cd AI-Analytics-Copilot
```

### 3. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and insert your OpenRouter API key:
```ini
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=cohere/north-mini-code:free
DATABASE_PATH=data/superstore.db
```

### 6. Run the ETL Pipeline
Ingest and index `Sample - Superstore.csv` into SQLite:
```bash
python -m src.data_loader
```
Output:
```
Ingestion successful: 9,994 rows loaded into data/superstore.db
Indexes verified: order_date, region, category, sub_category, customer_id
```

### 7. Launch the Web Application
```bash
streamlit run app.py
```
Open your web browser and navigate to `http://localhost:8501`.

---

## Running the Automated Test and Evaluation Suite

Run all unit and integration tests:
```bash
pytest tests/ -v
```

Execute the full 10-benchmark evaluation and adversarial attack stress test:
```bash
python tests/test_copilot.py
```

Expected output:
```
Golden Benchmark Evaluation: 10/10 Passed (100.0% Execution Accuracy)
Adversarial Security Stress Test: 8/8 Attacks Blocked (100.0% Security Resilience)
Evaluation report saved to data/evaluation_report.json
```

---

## Author and Profile

Developed by **Muhammad Qasim**
- GitHub: [https://github.com/QASIM07J](https://github.com/QASIM07J)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
