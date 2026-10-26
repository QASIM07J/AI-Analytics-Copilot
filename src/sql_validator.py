"""
SQL Guardrails and AST (Abstract Syntax Tree) Security Validator.

Validates LLM-generated SQL queries before execution:
- Rejects multiple stacked statements (preventing SQL injection).
- Parses query syntax into an AST to verify the root operation is strictly SELECT.
- Blocks destructive operations (DROP, DELETE, INSERT, UPDATE, ALTER, ATTACH, PRAGMA).
- Automatically appends a safety LIMIT 1000 if no LIMIT is specified.
"""

import re
from typing import Tuple, Optional
import sqlglot
from sqlglot import exp


# Disallowed expression types in AST
FORBIDDEN_AST_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
    exp.Pragma,
)

# Dangerous keyword patterns as a secondary regex safety net
FORBIDDEN_KEYWORDS_PATTERN = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|ATTACH|DETACH|CREATE|PRAGMA|VACUUM|REINDEX|REPLACE)\b",
    re.IGNORECASE,
)


def validate_and_sanitize_sql(
    sql: str,
    default_limit: int = 1000,
) -> Tuple[bool, Optional[str], str]:
    """
    Validates and sanitizes a SQL query for safe read-only execution.

    Returns:
        (is_valid: bool, error_message: Optional[str], safe_sql: str)
    """
    if not sql or not sql.strip():
        return False, "Query is empty.", ""

    clean_sql = sql.strip().rstrip(";")

    # 1. Reject Multiple Statements (prevent stacked SQL injection like: SELECT 1; DROP TABLE superstore;)
    # We parse all statements in the string
    try:
        parsed_statements = sqlglot.parse(clean_sql, read="sqlite")
    except Exception as e:
        return False, f"SQL Syntax Error: Unable to parse query. ({e})", ""

    if len(parsed_statements) == 0:
        return False, "Query contains no valid SQL statements.", ""

    if len(parsed_statements) > 1:
        return False, "Security Violation: Multiple stacked SQL statements are forbidden.", ""

    statement = parsed_statements[0]
    if statement is None:
        return False, "Query parsed as None.", ""

    # 2. Enforce Root Expression Must Be a SELECT statement
    if not isinstance(statement, exp.Select):
        return False, f"Security Violation: Only read-only SELECT queries are allowed. Got: {type(statement).__name__}.", ""

    # 3. Traverse the AST tree to ensure no forbidden nodes exist anywhere in subqueries or CTEs
    for forbidden_type in FORBIDDEN_AST_EXPRESSIONS:
        if statement.find(forbidden_type):
            return False, f"Security Violation: Forbidden operation '{forbidden_type.__name__}' detected.", ""

    # 4. Check that no dangerous SQLite commands exist in raw keywords outside of string literals
    # We strip string literals and inspect remaining tokens
    sql_without_literals = re.sub(r"'[^']*'", "''", clean_sql)
    sql_without_literals = re.sub(r'"[^"]*"', '""', sql_without_literals)
    forbidden_matches = FORBIDDEN_KEYWORDS_PATTERN.findall(sql_without_literals)
    if forbidden_matches:
        return False, f"Security Violation: Disallowed command detected: {', '.join(set(forbidden_matches))}", ""

    # 5. Safety LIMIT Injection: Ensure result size is capped to prevent memory exhaustion
    if statement.args.get("limit") is None:
        statement = statement.limit(default_limit)

    safe_sql = statement.sql(dialect="sqlite") + ";"
    return True, None, safe_sql
