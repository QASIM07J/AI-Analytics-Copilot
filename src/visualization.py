"""
Intelligent Automated Data Visualization Engine using Plotly.

Produces ultra-modern, high-impact interactive business charts:
- Deep-slate / glassmorphism dark aesthetic
- Vibrant neon-accent color harmonies (Indigo, Electric Cyan, Fuchsia, Emerald)
- Smooth entry animations and formatted hover tooltips
- Responsive layout with time-series line, donut composition, and ranking bars.
"""

import re
from typing import Optional, Tuple, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Ultra-Modern Vibrant SaaS Color Sequence
COLOR_SEQUENCE = [
    "#4F46E5",  # Vivid Indigo
    "#06B6D4",  # Electric Cyan
    "#10B981",  # Emerald Green
    "#F59E0B",  # Amber / Gold
    "#EC4899",  # Neon Pink / Fuchsia
    "#8B5CF6",  # Violet
    "#3B82F6",  # Sapphire Blue
]

MODERN_THEME_LAYOUT = dict(
    paper_bgcolor="rgba(255, 255, 255, 0.0)",
    plot_bgcolor="rgba(248, 250, 252, 0.6)",
    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#334155"),
    title_font=dict(size=16, color="#0F172A", family="Plus Jakarta Sans, sans-serif"),
    hoverlabel=dict(
        bgcolor="#FFFFFF",
        font_size=13,
        font_family="Plus Jakarta Sans, sans-serif",
        font_color="#0F172A",
        bordercolor="#CBD5E1",
    ),
    xaxis=dict(
        gridcolor="#E2E8F0",
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569", size=12),
        title_font=dict(color="#1E293B", size=13),
    ),
    yaxis=dict(
        gridcolor="#E2E8F0",
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569", size=12),
        title_font=dict(color="#1E293B", size=13),
    ),
)


def _detect_column_types(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    """Categorizes columns into temporal, categorical, and numeric."""
    temporal_cols = []
    categorical_cols = []
    numeric_cols = []

    date_patterns = re.compile(r"(date|year|month|quarter|week|day|time|period)", re.IGNORECASE)

    for col in df.columns:
        col_lower = str(col).lower()
        if pd.api.types.is_numeric_dtype(df[col]):
            if date_patterns.search(col_lower) and df[col].nunique() <= 20:
                temporal_cols.append(col)
            else:
                numeric_cols.append(col)
        else:
            sample_val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else ""
            if date_patterns.search(col_lower) or re.match(r"^\d{4}(-\d{2})?(-\d{2})?$", sample_val):
                temporal_cols.append(col)
            else:
                categorical_cols.append(col)

    return temporal_cols, categorical_cols, numeric_cols


def recommend_and_create_chart(
    df: pd.DataFrame,
    title: Optional[str] = None,
) -> Tuple[Optional[go.Figure], str]:
    """
    Analyzes DataFrame shape and builds a polished Plotly chart
    with glowing accents and hover animations.
    """
    if df is None or df.empty:
        return None, "No Data"

    if len(df) == 1:
        return None, "KPI Metric"

    temporal_cols, categorical_cols, numeric_cols = _detect_column_types(df)

    if not numeric_cols:
        return None, "Tabular Only (No Numeric Metrics)"

    primary_numeric = numeric_cols[0]
    chart_title = title or f"{primary_numeric.replace('_', ' ').title()} Overview"

    # Strategy 1: Time Series -> Glowing Line Chart
    if temporal_cols:
        time_col = temporal_cols[0]
        df_sorted = df.sort_values(by=time_col)

        fig = px.line(
            df_sorted,
            x=time_col,
            y=numeric_cols,
            title=chart_title,
            markers=True,
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(**MODERN_THEME_LAYOUT)
        fig.update_layout(
            hovermode="x unified",
            xaxis_title=time_col.replace("_", " ").title(),
            yaxis_title=primary_numeric.replace("_", " ").title(),
            margin=dict(l=40, r=40, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8, symbol="circle"))
        return fig, "Line Chart (Time Series)"

    # Strategy 2: Proportions (<= 4 categories) -> Glass Donut Chart
    if categorical_cols and len(df) <= 4 and len(numeric_cols) == 1:
        cat_col = categorical_cols[0]
        if (df[primary_numeric] >= 0).all():
            fig = px.pie(
                df,
                names=cat_col,
                values=primary_numeric,
                title=chart_title,
                hole=0.55,
                color_discrete_sequence=COLOR_SEQUENCE,
            )
            fig.update_layout(**MODERN_THEME_LAYOUT)
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color="#FFFFFF", width=2)),
            )
            fig.update_layout(
                margin=dict(l=40, r=40, t=60, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            )
            return fig, "Donut Chart (Composition)"

    # Strategy 3: Rankings / High Cardinality (> 8 items) -> Horizontal Bar Chart
    if categorical_cols and len(df) > 8:
        cat_col = categorical_cols[0]
        df_sorted = df.sort_values(by=primary_numeric, ascending=True)

        fig = px.bar(
            df_sorted,
            x=primary_numeric,
            y=cat_col,
            orientation="h",
            title=chart_title,
            color=primary_numeric,
            color_continuous_scale=["#38BDF8", "#6366F1", "#A855F7"],
        )
        fig.update_layout(**MODERN_THEME_LAYOUT)
        fig.update_layout(
            xaxis_title=primary_numeric.replace("_", " ").title(),
            yaxis_title="",
            margin=dict(l=170, r=40, t=60, b=40),
            coloraxis_showscale=False,
        )
        return fig, "Horizontal Bar Chart (Ranking)"

    # Strategy 4: Standard Categorical Comparison -> Grouped Modern Bar Chart
    if categorical_cols:
        cat_col = categorical_cols[0]
        df_sorted = df.sort_values(by=primary_numeric, ascending=False)

        fig = px.bar(
            df_sorted,
            x=cat_col,
            y=numeric_cols,
            barmode="group",
            title=chart_title,
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(**MODERN_THEME_LAYOUT)
        fig.update_layout(
            xaxis_title=cat_col.replace("_", " ").title(),
            yaxis_title="Value",
            margin=dict(l=40, r=40, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_traces(marker=dict(line=dict(color="rgba(255,255,255,0.1)", width=1)))
        return fig, "Vertical Bar Chart (Comparison)"

    return None, "Tabular View"
