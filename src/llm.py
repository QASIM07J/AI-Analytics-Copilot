"""
LLM Client and Prompt Engineering for Text-to-SQL Generation.

Communicates with OpenRouter API using active, verified free coding models:
- Primary: 'cohere/north-mini-code:free' (Specialized coding model)
- Fallbacks: 'poolside/laguna-s-2.1:free', 'recursive/flint-v1.0:free'

Constructs schema-grounded system prompts and sanitizes generated SQL queries.
"""

import os
import re
from typing import Optional, List
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv(override=True)

# Active verified free models on OpenRouter
DEFAULT_MODELS: List[str] = [
    "cohere/north-mini-code:free",
    "poolside/laguna-s-2.1:free",
    "recursive/flint-v1.0:free",
]

# Database schema representation for prompt grounding
SUPERSTORE_SCHEMA = """
Table: superstore
Columns:
- row_id (INTEGER PRIMARY KEY)
- order_id (TEXT)
- order_date (TEXT, format 'YYYY-MM-DD')
- ship_date (TEXT, format 'YYYY-MM-DD')
- ship_mode (TEXT: 'Standard Class', 'Second Class', 'First Class', 'Same Day')
- customer_id (TEXT)
- customer_name (TEXT)
- segment (TEXT: 'Consumer', 'Corporate', 'Home Office')
- country (TEXT)
- city (TEXT)
- state (TEXT)
- postal_code (TEXT)
- region (TEXT: 'West', 'East', 'Central', 'South')
- product_id (TEXT)
- category (TEXT: 'Furniture', 'Office Supplies', 'Technology')
- sub_category (TEXT: 'Chairs', 'Tables', 'Binders', 'Phones', etc.)
- product_name (TEXT)
- sales (REAL, currency value)
- quantity (INTEGER, item count)
- discount (REAL, between 0.0 and 0.8)
- profit (REAL, positive for gain, negative for loss)
"""

SYSTEM_PROMPT = f"""You are an expert SQL engineer specializing in SQLite.
Your task is to convert plain-English business questions into accurate, optimized, read-only SQLite queries.

Database Schema:
{SUPERSTORE_SCHEMA}

Strict Rules:
1. Return ONLY the raw SQL query. Do NOT include markdown code blocks, explanations, preambles, or conversational commentary.
2. The query MUST be a read-only SELECT statement. Never use DROP, DELETE, INSERT, UPDATE, or ALTER.
3. Use valid SQLite functions:
   - For year extraction: strftime('%Y', order_date)
   - For month extraction: strftime('%Y-%m', order_date)
   - For date differences in days: (julianday(ship_date) - julianday(order_date))
   - For rounding numbers: ROUND(val, 2)
4. Always aggregate metrics using SUM, AVG, or COUNT when grouping.
5. Profit can be negative (losses). Take this into account when filtering or sorting.
6. Use lowercase snake_case column names as defined in the schema (e.g. region, sales, profit, order_date).
"""


def get_llm_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Initializes and returns an OpenAI client configured for OpenRouter.
    Retrieves key from .env if not explicitly passed.
    """
    key = api_key or os.getenv("OPENROUTER_API_KEY")

    if not key or key == "sk-or-v1-your_token_here" or not key.startswith("sk-or-v1-"):
        raise ValueError(
            "Missing or invalid OpenRouter API key.\n"
            "Please add your free key in the '.env' file:\n"
            "OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here\n"
            "Get a free key at: https://openrouter.ai/settings/keys"
        )

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "AI Analytics Copilot",
        },
    )


def clean_sql_output(raw_output: str) -> str:
    """
    Sanitizes LLM output to ensure clean, executable SQL:
    - Extracts SQL from code blocks if present (```sql ... ```).
    - Removes conversational filler before or after the SQL.
    - Strips semicolons and returns a clean, single-statement SQL string.
    """
    sql = raw_output.strip()

    # If wrapped in markdown code fences, extract the content inside
    fence_match = re.search(r"```(?:sql)?\s*(.*?)\s*```", sql, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        sql = fence_match.group(1).strip()

    # Extract from SELECT statement to semicolon or end
    select_match = re.search(r"(SELECT\s+[^;]+)", sql, flags=re.IGNORECASE | re.DOTALL)
    if select_match:
        sql = select_match.group(1).strip()

    # Clean up excess whitespace/newlines and terminate with single semicolon
    sql = re.sub(r"\s+", " ", sql).strip().rstrip(";") + ";"
    return sql


def generate_sql(
    question: str,
    client: Optional[OpenAI] = None,
    models: Optional[List[str]] = None,
    use_rag: bool = True,
) -> str:
    """
    Generates a SQLite query from a natural-language business question.
    If use_rag is True, retrieves semantically relevant schema context and few-shot examples.
    Automatically tries candidate verified free models.
    """
    if client is None:
        client = get_llm_client()

    # Construct dynamic prompt with RAG if enabled
    system_content = SYSTEM_PROMPT
    if use_rag:
        try:
            from src.rag import get_schema_retriever
            retriever = get_schema_retriever()
            rag_context = retriever.format_augmented_context(question)
            system_content = f"{SYSTEM_PROMPT}\n{rag_context}"
        except Exception as e:
            # Fall back to base prompt if RAG encounter an issue
            pass

    candidate_models = models or DEFAULT_MODELS
    last_error = None

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Generate a SQLite query for this question: {question}"},
    ]

    for model in candidate_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=512,
                temperature=0.1,
            )
            msg = response.choices[0].message
            raw_sql = msg.content or getattr(msg, "reasoning", None)
            if raw_sql:
                return clean_sql_output(raw_sql)
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All free models failed to respond. Last error: {last_error}")


def generate_explanation(
    question: str,
    df: pd.DataFrame,
    client: Optional[OpenAI] = None,
    models: Optional[List[str]] = None,
) -> str:
    """
    Synthesizes a concise, professional executive summary (2-3 sentences)
    explaining the data findings based strictly on the query result table.
    """
    if df is None or df.empty:
        return "No records were found matching your criteria."

    if client is None:
        client = get_llm_client()

    # Format table data (limit to first 10 rows for prompt brevity)
    table_preview = df.head(10).to_markdown(index=False)

    explanation_system_prompt = (
        "You are an executive business analytics assistant. "
        "Your task is to analyze the provided tabular query results and answer the user's business question in 2 concise sentences. "
        "Highlight the key numbers, leaders, or trends. "
        "Strict Rule: Rely strictly on the numbers provided in the table; never invent or extrapolate outside the data."
    )

    user_prompt = f"Question: {question}\n\nQuery Results Table:\n{table_preview}\n\nExecutive Summary:"

    candidate_models = models or DEFAULT_MODELS
    for model in candidate_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": explanation_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=256,
                temperature=0.3,
            )
            msg = response.choices[0].message
            content = msg.content or getattr(msg, "reasoning", None)
            if content:
                # Clean up any residual markdown headers if present
                clean_summary = content.strip().replace("Executive Summary:", "").strip()
                return clean_summary
        except Exception:
            continue

    # Fallback heuristic summary if API call encounters an issue
    return f"The query returned {len(df)} records for '{question}'."
