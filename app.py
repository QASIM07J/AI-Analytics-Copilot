"""
Ask Your Data — AI Analytics Copilot
Streamlit Web Dashboard

Features:
- Pure professional typography and high-contrast styling (no emojis)
- Custom LatticeLoader (orbit pattern, 3x3 grid, live timer)
- Expandable Executive Business Insights card with legible contrast in both light/dark themes
- Plotly charts with clean, professional palettes
- Full SQL & AST security inspection
"""

import time
import json
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Backend Core Modules
from src.database import execute_safe_query, get_table_info
from src.llm import generate_sql, generate_explanation
from src.visualization import recommend_and_create_chart
from src.sql_validator import validate_and_sanitize_sql

# Page Configuration - Clean without emojis
st.set_page_config(
    page_title="Ask Your Data — AI Analytics Copilot",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Modern SaaS Light Aesthetic (Zero Emojis, Zero Black Backgrounds, Crisp Contrast)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* Main Title & Subtitle */
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #475569;
        font-weight: 400;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    /* Executive Insights Box - Elegant Light SaaS Gradient Card (No Black Background) */
    .insights-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EEF2F6 100%) !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 5px solid #4F46E5 !important;
        border-radius: 10px !important;
        padding: 18px 22px !important;
        margin: 6px 0 14px 0 !important;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04) !important;
    }

    .insights-title {
        display: inline-block !important;
        font-size: 0.74rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #4F46E5 !important;
        background: #EEF2FF !important;
        border: 1px solid #C7D2FE !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        margin-bottom: 10px !important;
    }

    .insights-body {
        font-size: 1.02rem !important;
        color: #1E293B !important;
        line-height: 1.65 !important;
        font-weight: 500 !important;
    }

    /* Status Indicator */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.76rem;
        font-weight: 600;
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }

    /* Interactive Buttons: Refined Modern Light Chips */
    .stButton>button {
        background: #FFFFFF !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.55rem 1.1rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton>button:hover {
        background: #F8FAFC !important;
        border-color: #6366F1 !important;
        color: #4F46E5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12) !important;
    }

    /* Primary Submit Button (Ask Copilot) */
    button[kind="primaryFormSubmit"], form button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #4338CA !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25) !important;
    }

    button[kind="primaryFormSubmit"]:hover, form button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        color: #FFFFFF !important;
    }

    /* Modern Text Input Field */
    .stTextInput>div>div>input {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        font-size: 0.98rem !important;
        padding: 10px 14px !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }

    .stTextInput>div>div>input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #1E293B !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 14px !important;
    }

    /* Tabs Styling - Indigo Active Bar Instead of Red */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        border-bottom: 2px solid #E2E8F0 !important;
        padding-bottom: 2px !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #64748B !important;
        padding: 8px 16px !important;
        border-radius: 6px 6px 0 0 !important;
        background: transparent !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        color: #4F46E5 !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #4F46E5 !important;
        height: 2.5px !important;
        border-radius: 2px !important;
    }

    /* Metric Cards in Audit Tab */
    [data-testid="stMetric"] {
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600 !important;
        color: #64748B !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_lattice_loader_html(status="working", elapsed_sec=0.0):
    """
    Renders the exact LatticeLoader component:
    - 3x3 grid of 6px round cells with 2px gap
    - pattern="orbit"
    - step=90ms
    - idleOpacity=0.15
    - showTimer=True
    - status="working" (Thinking + timer) or status="done" (Done in X.Xs)
    """
    if status == "working":
        return f"""
        <style>body {{ margin: 0; padding: 2px 0; background: transparent; overflow: hidden; }}</style>
        <div id="lattice-root" style="display: inline-flex; align-items: center; gap: 12px; padding: 8px 16px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; font-family: 'Plus Jakarta Sans', sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="display: grid; grid-template-columns: repeat(3, 6px); grid-gap: 2px; width: 22px; height: 22px;">
                <div class="lc" id="dot-0" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-1" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-2" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-7" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-center" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;"></div>
                <div class="lc" id="dot-3" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-6" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-5" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
                <div class="lc" id="dot-4" style="width:6px;height:6px;border-radius:50%;background:#4F46E5;opacity:0.2;transition:opacity 0.08s;"></div>
            </div>
            <div style="font-size: 13.5px; color: #475569; font-weight: 500; display: flex; align-items: center; gap: 8px;">
                <span style="color: #4F46E5; font-weight: 600;">Thinking</span>
                <span id="lattice-clock" style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: #64748B; background: #EEF2F6; padding: 2px 6px; border-radius: 4px;">0.0s</span>
            </div>
        </div>
        <script>
            (function() {{
                const orbit = [0, 1, 2, 3, 4, 5, 6, 7];
                let step = 0;
                let startTime = Date.now();

                const timerInterval = setInterval(() => {{
                    const el = document.getElementById('lattice-clock');
                    if (el) {{
                        const sec = ((Date.now() - startTime) / 1000).toFixed(1);
                        el.textContent = sec + 's';
                    }}
                }}, 100);

                const orbitInterval = setInterval(() => {{
                    for (let i = 0; i < 8; i++) {{
                        const d = document.getElementById('dot-' + i);
                        if (d) d.style.opacity = '0.2';
                    }}
                    const curr = document.getElementById('dot-' + orbit[step % 8]);
                    const prev = document.getElementById('dot-' + orbit[(step + 7) % 8]);
                    if (curr) curr.style.opacity = '1.0';
                    if (prev) prev.style.opacity = '0.5';
                    step++;
                }}, 90);
            }})();
        </script>
        """
    else:
        # Done State with doneColor="#22c55e"
        return f"""
        <style>body {{ margin: 0; padding: 2px 0; background: transparent; overflow: hidden; }}</style>
        <div style="display: inline-flex; align-items: center; gap: 12px; padding: 8px 16px; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; font-family: 'Plus Jakarta Sans', sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="display: grid; grid-template-columns: repeat(3, 6px); grid-gap: 2px; width: 22px; height: 22px;">
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;opacity:0.35;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
                <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
            </div>
            <div style="font-size: 13.5px; color: #15803D; font-weight: 600;">
                Done in {elapsed_sec:.1f}s
            </div>
        </div>
        """


@st.cache_data
def load_sample_questions():
    """Loads benchmark preset questions from golden_benchmarks.json."""
    path = os.path.join("data", "golden_benchmarks.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_data
def load_cached_table_info():
    """Retrieves and caches table statistics."""
    try:
        return get_table_info()
    except Exception:
        return {"table_name": "superstore", "row_count": 9994, "columns": []}


def main():
    # ------------------ SIDEBAR ------------------
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1E293B;">System Telemetry</h3>
                <span class="status-badge">Active</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        table_meta = load_cached_table_info()
        st.markdown(
            f"""
            <div style="font-size: 0.86rem; color: #64748B; line-height: 1.8;">
                • Database: <b>superstore.db</b> (SQLite)<br>
                • Records: <b>{table_meta['row_count']:,}</b> rows<br>
                • Access: <b>Read-Only (mode=ro)</b><br>
                • Schema RAG: <b>Dense Vector (384-d)</b><br>
                • Security: <b>AST sqlglot Guardrails</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### Preset Queries")
        benchmarks = load_sample_questions()

        selected_preset = st.selectbox(
            "Select an analytical question:",
            options=["-- Choose a preset query --"] + [b["question"] for b in benchmarks],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")
        with st.expander("Database Schema Inspector", expanded=False):
            st.markdown(f"**Table**: `{table_meta['table_name']}` ({len(table_meta['columns'])} columns)")
            if table_meta["columns"]:
                cols_df = pd.DataFrame(table_meta["columns"])[["name", "type"]]
                st.dataframe(cols_df, height=280, use_container_width=True)

        st.markdown("---")
        st.caption("Ask Your Data — AI Analytics Copilot")

    # ------------------ MAIN WORKSPACE ------------------
    st.markdown('<div class="hero-title">Ask Your Data — AI Analytics Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Convert plain-English business questions into verified read-only SQL, safe database queries, and interactive visualizations.</div>',
        unsafe_allow_html=True,
    )

    # Quick interactive suggestion chips (Zero Emojis)
    st.markdown("<p style='font-size: 0.85rem; color: #64748B; margin-bottom: 6px; font-weight: 600;'>Sample Queries:</p>", unsafe_allow_html=True)
    col_c1, col_c2, col_c3 = st.columns(3)
    preset_chosen = None

    with col_c1:
        if st.button("Sales and Profit by Region", use_container_width=True):
            preset_chosen = "What are the total sales and profit in each region?"
    with col_c2:
        if st.button("Top 5 Profitable Products", use_container_width=True):
            preset_chosen = "Which top 5 products generated the highest profit?"
    with col_c3:
        if st.button("High Sales with Negative Profit", use_container_width=True):
            preset_chosen = "Which products generated more than 5,000 dollars in sales but had negative profit?"

    # Determine input value
    if preset_chosen:
        initial_val = preset_chosen
    elif selected_preset != "-- Choose a preset query --":
        initial_val = selected_preset
    else:
        initial_val = st.session_state.get("active_question", "")

    # Input Form
    with st.form(key="copilot_form", clear_on_submit=False):
        user_question = st.text_input(
            "Enter your question:",
            value=initial_val,
            placeholder="e.g., What are the total sales and total profit in each region?",
            label_visibility="collapsed",
        )
        col_submit, col_meta = st.columns([1, 4])
        with col_submit:
            submit_clicked = st.form_submit_button("Ask Copilot", use_container_width=True)
        with col_meta:
            st.markdown(
                """
                <div style="font-size: 0.8rem; color: #64748B; padding-top: 8px;">
                    AST security validation active • Read-only connection • Automatic 1000 row safety limit
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Container for LatticeLoader directly below the button
    loader_placeholder = st.empty()

    # ------------------ EXECUTION ENGINE ------------------
    if submit_clicked and user_question.strip():
        st.session_state["active_question"] = user_question

        # Step A: Show LatticeLoader in 'working' status
        t_start = time.time()
        with loader_placeholder.container():
            components.html(get_lattice_loader_html(status="working"), height=50)

        # Step 1: Schema RAG + SQL Generation
        try:
            generated_sql = generate_sql(user_question, use_rag=True)
        except Exception as e:
            loader_placeholder.empty()
            st.error(f"Error during SQL generation: {e}")
            return

        # Step 2: AST Guardrail Validation & Safe SQLite Query
        df, error_msg, executed_sql = execute_safe_query(generated_sql)
        t_total_sec = time.time() - t_start

        if error_msg and df is None:
            loader_placeholder.empty()
            st.error(f"Security Guardrail Violation: {error_msg}")
            with st.expander("Inspect Rejected SQL"):
                st.code(generated_sql, language="sql")
            return

        if df is None or df.empty:
            loader_placeholder.empty()
            st.warning("The query executed safely, but no records matched the given criteria.")
            with st.expander("Inspect Executed SQL"):
                st.code(executed_sql, language="sql")
            return

        # Step 3: Executive Summary
        try:
            executive_summary = generate_explanation(user_question, df)
        except Exception:
            executive_summary = f"The query returned {len(df)} records for '{user_question}'."

        # Step B: Update LatticeLoader to 'done' status
        with loader_placeholder.container():
            components.html(get_lattice_loader_html(status="done", elapsed_sec=t_total_sec), height=45)

        # ------------------ EXPANDABLE EXECUTIVE INSIGHTS ------------------
        # Expandable insights with guaranteed high-contrast readable styling in both light/dark themes
        with st.expander("Executive Business Insights", expanded=True):
            st.markdown(
                f"""
                <div class="insights-card">
                    <div class="insights-title">Key Takeaway</div>
                    <div class="insights-body">{executive_summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Workspace Tabs (Zero Emojis)
        tab_chart, tab_table, tab_audit = st.tabs([
            "Interactive Visualization",
            "Raw Data Table",
            "SQL and Security Audit",
        ])

        # Tab 1: Plotly Visual
        with tab_chart:
            fig, chart_type = recommend_and_create_chart(df, title=f"Analysis: {user_question}")
            if fig is not None:
                st.caption(f"Recommended Chart: {chart_type}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Visual representation: {chart_type}. Viewing as tabular metrics below.")
                st.dataframe(df, use_container_width=True)

        # Tab 2: Raw Data Table
        with tab_table:
            st.markdown(f"**Result Set**: {len(df):,} rows returned")
            st.dataframe(df, use_container_width=True)

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Export Table as CSV",
                data=csv_bytes,
                file_name="analytics_copilot_data.csv",
                mime="text/csv",
            )

        # Tab 3: Security & Performance Audit
        with tab_audit:
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Latency", f"{(t_total_sec * 1000):.1f} ms")
            with col_m2:
                st.metric("Guardrail Status", "AST Verified (Read-Only)")
            with col_m3:
                st.metric("Rows Returned", f"{len(df):,}")

            st.markdown("##### Executed SQL Statement:")
            st.code(executed_sql, language="sql")
            st.markdown(
                """
                <div style="font-size: 0.8rem; color: #64748B;">
                    • AST Checked: Root operation enforced as exp.Select.<br>
                    • Injection Defense: Stacked queries, comments, and DDL/DML tokens blocked.<br>
                    • Storage Security: Connected via SQLite URI mode ?mode=ro.
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
