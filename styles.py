import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --navy: #1B2A4A;
    --navy-light: #29406e;
    --amber: #E8A33D;
    --amber-dark: #c9861f;
    --bg: #FAF9F6;
    --card-border: #E5E1D8;
    --text-main: #22262B;
    --text-muted: #6B7280;
    --success: #3C8F6D;
    --danger: #C0392B;
}

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}

h1, h2, h3 {
    font-family: 'Lora', serif !important;
    color: var(--navy) !important;
}

.stApp {
    background-color: var(--bg);
}

label, label p, label span, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
    color: var(--text-main) !important;
    opacity: 1 !important;
    font-weight: 500 !important;
}

section[data-testid="stSidebar"] {
    background-color: var(--navy);
}
section[data-testid="stSidebar"] * {
    color: #F2F0EA !important;
}

.stButton > button {
    background-color: var(--navy);
    color: white;
    border-radius: 6px;
    border: none;
    padding: 0.5rem 1.2rem;
    font-weight: 500;
    transition: background-color 0.15s ease;
}
.stButton > button:hover {
    background-color: var(--amber-dark);
    color: white;
}

.stFormSubmitButton > button {
    background-color: var(--amber);
    color: var(--navy);
    font-weight: 600;
}
.stFormSubmitButton > button:hover {
    background-color: var(--amber-dark);
    color: white;
}

.metric-card {
    background: white;
    border: 1px solid var(--card-border);
    border-left: 5px solid var(--amber);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-card .metric-label {
    font-size: 0.82rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.metric-card .metric-value {
    font-family: 'Lora', serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--navy);
    margin-top: 0.15rem;
}

.page-header {
    padding: 0.4rem 0 1.1rem 0;
    border-bottom: 2px solid var(--card-border);
    margin-bottom: 1.4rem;
}
.page-header .eyebrow {
    color: var(--amber-dark);
    font-weight: 600;
    font-size: 0.85rem;
}
.page-header h1 {
    margin: 0.1rem 0 0 0 !important;
    font-size: 2rem !important;
}

.login-wrapper {
    max-width: 420px;
    margin: 3rem auto 0 auto;
    background: white;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 2.2rem 2.2rem 1.4rem 2.2rem;
    box-shadow: 0 4px 18px rgba(27,42,74,0.08);
}
.login-title {
    font-family: 'Lora', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--navy);
    text-align: center;
    margin-bottom: 0.1rem;
}
.login-subtitle {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 1.4rem;
}

.badge-admin {
    background: var(--navy);
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-teacher {
    background: var(--amber);
    color: var(--navy);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-student {
    background: var(--success);
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--card-border);
    border-radius: 8px;
}
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(eyebrow, title):
    st.markdown(
        f"""
        <div class="page-header">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value):
    return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """