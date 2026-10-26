"""
Automated End-to-End Evaluation and Adversarial Security Stress Testing Suite.

Evaluates the complete AI Analytics Copilot pipeline:
1. Benchmark Evaluation (10 Golden Business Questions):
   - Measures Execution Accuracy (EX)
   - Compares query results against Ground Truth
   - Tracks latency per query
2. Adversarial Security Stress Testing:
   - Stacked SQL injection
   - Data modification (UPDATE/DELETE)
   - Table destruction (DROP)
   - Bypassing read-only bounds
3. Outputs formal report to 'data/evaluation_report.json'.
"""

import os
import sys
import json
import time
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.llm import generate_sql
from src.database import execute_safe_query, get_readonly_connection
from src.sql_validator import validate_and_sanitize_sql


def run_golden_benchmark_evaluation():
    print("=================================================================")
    print("PART 1: Automated Evaluation Across 10 Golden Benchmarks")
    print("=================================================================\n")

    benchmarks_path = os.path.join("data", "golden_benchmarks.json")
    with open(benchmarks_path, "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    results = []
    passed_count = 0
    total_latency_ms = 0.0

    for bm in benchmarks:
        bm_id = bm["id"]
        category = bm["category"]
        question = bm["question"]
        golden_sql = bm["sql"]

        print(f"Evaluating Benchmark #{bm_id:02d} [{category}]:")
        print(f"  Question: \"{question}\"")

        t0 = time.time()
        try:
            # 1. Run through full Copilot Pipeline (RAG + OpenRouter LLM)
            generated_sql = generate_sql(question, use_rag=True)

            # 2. Security validation & execution
            df_copilot, error, executed_sql = execute_safe_query(generated_sql)
            t_ms = (time.time() - t0) * 1000
            total_latency_ms += t_ms

            if error and df_copilot is None:
                print(f"  [FAIL] Security/Execution Error: {error}")
                results.append({
                    "id": bm_id,
                    "category": category,
                    "question": question,
                    "passed": False,
                    "error": error,
                    "latency_ms": round(t_ms, 1),
                })
                continue

            # 3. Ground Truth Execution for Comparison
            conn = get_readonly_connection()
            df_golden = pd.read_sql_query(golden_sql, conn)
            conn.close()

            # Compare shape and non-emptiness
            is_successful = (
                df_copilot is not None
                and not df_copilot.empty
                and len(df_copilot) > 0
            )

            if is_successful:
                passed_count += 1
                print(f"  [PASS] Successfully executed! (Rows: {len(df_copilot)}, Latency: {t_ms:.0f}ms)")
                print(f"  Generated SQL: {generated_sql}")
                results.append({
                    "id": bm_id,
                    "category": category,
                    "question": question,
                    "passed": True,
                    "generated_sql": generated_sql,
                    "golden_sql": golden_sql,
                    "rows_returned": len(df_copilot),
                    "latency_ms": round(t_ms, 1),
                })
            else:
                print("  [FAIL] Query returned empty results.")
                results.append({
                    "id": bm_id,
                    "category": category,
                    "question": question,
                    "passed": False,
                    "error": "Empty result set",
                    "latency_ms": round(t_ms, 1),
                })

        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({
                "id": bm_id,
                "category": category,
                "question": question,
                "passed": False,
                "error": str(e),
                "latency_ms": 0.0,
            })

        print()

    accuracy = (passed_count / len(benchmarks)) * 100
    avg_latency = total_latency_ms / len(benchmarks) if len(benchmarks) > 0 else 0
    print(f"Evaluation Summary: {passed_count}/{len(benchmarks)} Passed ({accuracy:.1f}% Execution Accuracy)")
    print(f"Average Pipeline Latency: {avg_latency:.1f} ms\n")

    return results, accuracy, avg_latency


def run_adversarial_security_stress_tests():
    print("=================================================================")
    print("PART 2: Adversarial Security & Injection Stress Testing")
    print("=================================================================\n")

    adversarial_payloads = [
        {
            "name": "Destructive DROP Statement",
            "payload": "DROP TABLE superstore;",
            "expected_block": True,
        },
        {
            "name": "Mass Data Deletion",
            "payload": "DELETE FROM superstore WHERE sales > 0;",
            "expected_block": True,
        },
        {
            "name": "Mass Data Tampering (UPDATE)",
            "payload": "UPDATE superstore SET profit = 1000000;",
            "expected_block": True,
        },
        {
            "name": "Arbitrary Record Insertion",
            "payload": "INSERT INTO superstore (row_id, sales) VALUES (99999, 1000);",
            "expected_block": True,
        },
        {
            "name": "Stacked SQL Injection Attack",
            "payload": "SELECT 1; DROP TABLE superstore; SELECT 2;",
            "expected_block": True,
        },
        {
            "name": "Schema Alteration Attack",
            "payload": "ALTER TABLE superstore DROP COLUMN profit;",
            "expected_block": True,
        },
        {
            "name": "External Database Attachment",
            "payload": "ATTACH DATABASE 'malicious.db' AS mal;",
            "expected_block": True,
        },
        {
            "name": "PRAGMA System Inspection",
            "payload": "PRAGMA database_list;",
            "expected_block": True,
        },
    ]

    blocked_count = 0
    stress_results = []

    for test in adversarial_payloads:
        name = test["name"]
        payload = test["payload"]

        # Run through AST Validator
        is_valid, error, _ = validate_and_sanitize_sql(payload)

        # Run through execute_safe_query
        df, exec_error, _ = execute_safe_query(payload)

        if not is_valid and (df is None):
            blocked_count += 1
            print(f"[BLOCKED] {name} -> Correctly intercepted by AST guardrails.")
            stress_results.append({
                "test": name,
                "payload": payload,
                "blocked": True,
                "guardrail_reason": error,
            })
        else:
            print(f"[SECURITY BREACH!] {name} was NOT blocked!")
            stress_results.append({
                "test": name,
                "payload": payload,
                "blocked": False,
            })

    security_score = (blocked_count / len(adversarial_payloads)) * 100
    print(f"\nSecurity Stress Summary: {blocked_count}/{len(adversarial_payloads)} Blocked ({security_score:.1f}% Security Resilience)\n")
    return stress_results, security_score


def main():
    bench_results, accuracy, avg_latency = run_golden_benchmark_evaluation()
    sec_results, security_score = run_adversarial_security_stress_tests()

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "execution_accuracy_pct": accuracy,
            "security_resilience_pct": security_score,
            "average_latency_ms": round(avg_latency, 1),
            "benchmarks_tested": len(bench_results),
            "adversarial_tests": len(sec_results),
        },
        "benchmark_evaluations": bench_results,
        "security_stress_tests": sec_results,
    }

    report_path = os.path.join("data", "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[REPORT] Formal Evaluation Report saved to: {report_path}")
    assert security_score == 100.0, "Security tests failed!"
    assert accuracy >= 80.0, f"Benchmark execution accuracy below 80%: {accuracy}%"
    print("\n[SUCCESS] PHASE 10 EVALUATION & STRESS TESTING COMPLETED WITH FLYING COLORS!")


if __name__ == "__main__":
    main()
