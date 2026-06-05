from __future__ import annotations

import pandas as pd


SURFACE = "#111827"
SURFACE_SOFT = "#172033"
SURFACE_RAISED = "#1f2937"
BORDER = "#334155"
TEXT = "#f8fafc"
MUTED = "#a7b0c0"
ACCENT = "#ff4b4b"


def get_app_styles() -> str:
    return f"""
        <style>
        :root {{
            color-scheme: dark;
        }}
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"] {{
            background: #0b1020;
            color: {TEXT};
        }}
        [data-testid="stHeader"] {{
            background: rgba(11, 16, 32, 0.88);
        }}
        [data-testid="stSidebar"] > div {{
            background: #161b29;
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }}
        h1, h2, h3 {{
            letter-spacing: 0;
            color: {TEXT};
        }}
        .kpi-card,
        [data-testid="stMetric"] {{
            background: linear-gradient(180deg, {SURFACE_RAISED}, {SURFACE});
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 0.9rem 1rem;
            min-height: 104px;
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.22);
            color: {TEXT};
        }}
        .kpi-label,
        [data-testid="stMetricLabel"] {{
            color: {MUTED};
            font-size: 0.82rem;
            line-height: 1.2;
        }}
        .kpi-value,
        [data-testid="stMetricValue"] {{
            color: {TEXT};
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.1;
            margin-top: 0.72rem;
        }}
        [data-testid="stSidebar"] {{
            border-right: 1px solid {BORDER};
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {{
            color: {TEXT};
        }}
        [data-testid="stSidebar"] button,
        [data-baseweb="select"] > div,
        [data-testid="stTextInput"] input {{
            background: {SURFACE};
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 8px;
        }}
        [data-testid="stSidebar"] button:hover,
        [data-baseweb="select"] > div:hover,
        [data-testid="stTextInput"] input:focus {{
            border-color: {ACCENT};
        }}
        [data-baseweb="select"] span,
        [data-testid="stTextInput"] input::placeholder {{
            color: {MUTED};
        }}
        .dark-table-wrap,
        [data-testid="stDataFrame"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 8px;
            overflow: hidden;
            color: {TEXT};
        }}
        .dark-table-wrap {{
            max-height: 520px;
            overflow: auto;
            box-shadow: 0 12px 28px rgba(2, 6, 23, 0.2);
        }}
        .dark-table-wrap table {{
            width: max-content;
            min-width: 100%;
            border-collapse: collapse;
            background: {SURFACE};
            color: {TEXT};
            font-size: 0.84rem;
        }}
        .dark-table-wrap th {{
            position: sticky;
            top: 0;
            z-index: 2;
            background: {SURFACE_RAISED};
            color: {TEXT};
            border-bottom: 1px solid {BORDER};
            border-right: 1px solid {BORDER};
            padding: 0.72rem 0.8rem;
            text-align: left;
            white-space: nowrap;
        }}
        .dark-table-wrap td {{
            background: {SURFACE};
            color: {TEXT};
            border-bottom: 1px solid rgba(51, 65, 85, 0.62);
            border-right: 1px solid rgba(51, 65, 85, 0.45);
            padding: 0.64rem 0.8rem;
            white-space: nowrap;
        }}
        .dark-table-wrap tbody tr:nth-child(even) td {{
            background: {SURFACE_SOFT};
        }}
        .dark-table-wrap tbody tr:hover td {{
            background: #243044;
        }}
        [data-testid="stDataFrame"] div,
        [data-testid="stDataFrame"] canvas {{
            color-scheme: dark;
        }}
        [data-testid="stDataFrame"] [role="grid"],
        [data-testid="stDataFrame"] [role="row"],
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="gridcell"] {{
            background-color: {SURFACE};
            color: {TEXT};
            border-color: {BORDER};
        }}
        [data-testid="stDataFrame"] button {{
            color: {TEXT};
        }}
        .stAlert {{
            border-radius: 8px;
        }}
        </style>
    """


def dark_table_html(frame: pd.DataFrame, max_height: int = 520) -> str:
    table_html = frame.to_html(
        index=False,
        border=0,
        classes="dark-table",
        escape=True,
    )
    return f'<div class="dark-table-wrap" style="max-height: {max_height}px;">{table_html}</div>'
