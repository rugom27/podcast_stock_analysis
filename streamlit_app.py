"""
Hedge Fund Tips Analysis Dashboard v2
A Bloomberg Terminal-inspired interface for tracking Tom Hayes' stock recommendations.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

# === CONFIGURATION ===
st.set_page_config(
    page_title="HedgeFund Tips Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

OUTPUTS_DIR = Path("outputs")
GLOBAL_DIR = OUTPUTS_DIR / "global_audit"


# === INJECT CUSTOM CSS ===
st.markdown(
    """
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
    
    /* === ROOT VARIABLES === */
    :root {
        --bg-primary: #0a0a0f;
        --bg-surface: #12121a;
        --bg-elevated: #1a1a24;
        --accent-cyan: #00d4ff;
        --accent-green: #00ff88;
        --accent-red: #ff3366;
        --accent-amber: #ffc107;
        --text-primary: #e8e8e8;
        --text-muted: #8888aa;
        --border-subtle: #2a2a3a;
    }
    
    /* === GLOBAL OVERRIDES === */
    .stApp {
        background: linear-gradient(180deg, var(--bg-primary) 0%, #0d0d14 100%);
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* === TYPOGRAPHY === */
    h1, h2, h3 {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-size: 1.4rem !important;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.5rem;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: var(--accent-cyan) !important;
        font-size: 1.1rem !important;
    }
    
    p, li, span, div {
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--text-primary);
    }
    
    /* === METRIC CARDS === */
    [data-testid="stMetric"] {
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: var(--accent-cyan);
        box-shadow: 0 4px 30px rgba(0,212,255,0.15);
        transform: translateY(-2px);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--accent-cyan) !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }
    
    /* === SELECTBOX === */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--bg-surface);
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        color: var(--text-muted) !important;
        background: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-elevated) !important;
        color: var(--accent-cyan) !important;
        border: 1px solid var(--accent-cyan) !important;
    }
    
    /* === DATAFRAME === */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] th {
        background: var(--bg-elevated) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--accent-cyan) !important;
    }
    
    [data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    
    /* === MARKDOWN CONTENT === */
    .markdown-content {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 2rem;
        line-height: 1.8;
    }
    
    .markdown-content h1 {
        font-size: 1.8rem !important;
        margin-bottom: 1rem !important;
    }
    
    .markdown-content h2 {
        font-size: 1.3rem !important;
        color: var(--accent-cyan) !important;
        border-bottom: none !important;
        margin-top: 1.5rem !important;
    }
    
    .markdown-content h3 {
        font-size: 1.1rem !important;
        color: var(--accent-green) !important;
    }
    
    .markdown-content blockquote {
        border-left: 3px solid var(--accent-amber);
        padding-left: 1rem;
        margin: 1rem 0;
        font-style: italic;
        color: var(--text-muted);
    }
    
    /* === CONVICTION GAUGE === */
    .conviction-gauge {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
    }
    
    .conviction-score {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .conviction-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
    }
    
    /* === IMAGE GRID === */
    .chart-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .chart-card:hover {
        border-color: var(--accent-cyan);
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,212,255,0.2);
    }
    
    /* === STATUS BADGES === */
    .badge-bullish {
        background: rgba(0, 255, 136, 0.15);
        color: var(--accent-green);
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .badge-bearish {
        background: rgba(255, 51, 102, 0.15);
        color: var(--accent-red);
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* === DIVIDER === */
    hr {
        border: none;
        border-top: 1px solid var(--border-subtle);
        margin: 2rem 0;
    }
    
    /* === EXPANDER === */
    [data-testid="stExpander"] {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
    }
    
    [data-testid="stExpander"] summary {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stMetric, .stTabs, [data-testid="stDataFrame"] {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* === INFO/WARNING BOXES === */
    [data-testid="stAlert"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# === DATA HELPERS ===
def get_available_episodes():
    """Scan outputs dir for episode folders."""
    episodes = []
    if not OUTPUTS_DIR.exists():
        return []
    for item in OUTPUTS_DIR.iterdir():
        if item.is_dir() and item.name.startswith("episode_"):
            try:
                episodes.append(item.name.split("_")[1])
            except IndexError:
                continue
    try:
        episodes.sort(key=lambda x: int(x), reverse=True)
    except ValueError:
        episodes.sort(reverse=True)
    return episodes


def load_episode_data(ep_num):
    """Load all assets for a specific episode."""
    base = OUTPUTS_DIR / f"episode_{ep_num}"

    # Markdown Report
    report_content = None
    report_path = base / "transcripts" / f"hedge_fund_tips_episode_{ep_num}_report.md"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

    # Visual Analysis
    visual_data = None
    visual_path = base / "step5_visual_analysis_complete.json"
    if visual_path.exists():
        with open(visual_path, "r", encoding="utf-8") as f:
            visual_data = json.load(f)

    # Signals Audit
    audit_df = None
    audit_path = base / "episode_signals_audit.csv"
    if audit_path.exists():
        audit_df = pd.read_csv(audit_path)

    # Step 2 JSON (for conviction score)
    step2_data = None
    step2_path = base / "transcripts" / f"step2_master_analysis_episode_{ep_num}.json"
    if step2_path.exists():
        with open(step2_path, "r", encoding="utf-8") as f:
            step2_data = json.load(f)

    return report_content, visual_data, audit_df, step2_data


def load_global_data():
    """Load global audit data."""
    scorecard = None
    signals = None

    scorecard_path = GLOBAL_DIR / "master_ticker_scorecard.csv"
    signals_path = GLOBAL_DIR / "master_signals_audit.csv"

    if scorecard_path.exists():
        scorecard = pd.read_csv(scorecard_path)
    if signals_path.exists():
        signals = pd.read_csv(signals_path)

    return scorecard, signals


def style_returns_df(df):
    """Apply color styling to returns dataframe."""

    def color_return(val):
        if pd.isna(val):
            return ""
        try:
            v = float(val)
            if v > 10:
                return "color: #00ff88; font-weight: 600;"
            elif v > 0:
                return "color: #00d4ff;"
            elif v < -10:
                return "color: #ff3366; font-weight: 600;"
            elif v < 0:
                return "color: #ff6b6b;"
            return ""
        except:
            return ""

    return_cols = [c for c in df.columns if "return" in c.lower() or c.startswith("T+")]
    return df.style.applymap(color_return, subset=return_cols)


# === SIDEBAR ===
with st.sidebar:
    st.markdown("## 📊 TERMINAL")
    st.markdown("---")

    available_eps = get_available_episodes()
    options = ["🌐  Global Dashboard"] + [f"EP {ep}" for ep in available_eps]

    selected = st.selectbox(
        "SELECT VIEW",
        options,
        index=0,
        label_visibility="visible",
    )

    st.markdown("---")

    # Stats
    st.markdown("### SYSTEM STATUS")
    st.markdown(f"**Episodes Tracked:** `{len(available_eps)}`")

    global_scorecard, _ = load_global_data()
    if global_scorecard is not None:
        avg_win = global_scorecard["Win_Rate"].mean()
        st.markdown(f"**Avg Win Rate:** `{avg_win:.1f}%`")


# === MAIN CONTENT ===

if selected == "🌐  Global Dashboard":
    # =====================
    # GLOBAL DASHBOARD VIEW
    # =====================

    st.markdown("# GLOBAL PERFORMANCE")
    st.markdown("*Aggregated analysis across all tracked episodes*")

    scorecard, signals = load_global_data()

    # === TOP METRICS ===
    if scorecard is not None and not scorecard.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="TOTAL TICKERS",
                value=len(scorecard),
            )

        with col2:
            avg_win = scorecard["Win_Rate"].mean()
            st.metric(
                label="AVG WIN RATE",
                value=f"{avg_win:.1f}%",
            )

        with col3:
            avg_1m = scorecard["Avg_Return_1Mo"].mean()
            st.metric(
                label="AVG 1M RETURN",
                value=f"{avg_1m:+.1f}%",
            )

        with col4:
            avg_6m = scorecard["Avg_Return_6Mo"].mean()
            st.metric(
                label="AVG 6M RETURN",
                value=f"{avg_6m:+.1f}%" if pd.notna(avg_6m) else "N/A",
            )

    st.markdown("---")

    # === TABS ===
    tab1, tab2 = st.tabs(["🏆 TICKER SCORECARD", "📡 ALL SIGNALS"])

    with tab1:
        st.markdown("### Top Performing Tickers")
        if scorecard is not None and not scorecard.empty:
            st.dataframe(
                scorecard.head(20),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ticker": st.column_config.TextColumn("TICKER", width="small"),
                    "Total_Signals": st.column_config.NumberColumn(
                        "SIGNALS", width="small"
                    ),
                    "Win_Rate": st.column_config.ProgressColumn(
                        "WIN RATE",
                        format="%.0f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Avg_Return_1Mo": st.column_config.NumberColumn(
                        "1M AVG",
                        format="%.1f%%",
                    ),
                    "Avg_Return_6Mo": st.column_config.NumberColumn(
                        "6M AVG",
                        format="%.1f%%",
                    ),
                },
            )
        else:
            st.warning("No scorecard data. Run global audit first.")

    with tab2:
        st.markdown("### Complete Signals Log")
        if signals is not None and not signals.empty:
            st.dataframe(
                signals,
                use_container_width=True,
                hide_index=True,
                height=500,
            )
        else:
            st.warning("No signals data available.")

else:
    # =====================
    # EPISODE ANALYSIS VIEW
    # =====================

    ep_num = selected.replace("EP ", "")
    report, visuals, audit_df, step2_data = load_episode_data(ep_num)

    st.markdown(f"# EPISODE {ep_num}")

    # === CONVICTION GAUGE ===
    if step2_data:
        conviction = step2_data.get("tom_current_conviction", {})
        score = conviction.get("score_1_to_10", "?")
        market_view = conviction.get("overall_market", "N/A")

        st.markdown(
            f"""
        <div class="conviction-gauge">
            <div>
                <div class="conviction-score">{score}/10</div>
                <div class="conviction-label">Conviction Score</div>
            </div>
            <div style="flex: 1; padding-left: 2rem; border-left: 1px solid #2a2a3a;">
                <div style="font-size: 0.8rem; color: #8888aa; text-transform: uppercase; letter-spacing: 0.1em;">Market Outlook</div>
                <div style="font-size: 1.2rem; color: #e8e8e8; margin-top: 0.25rem;">{market_view}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # === TABS ===
    tab1, tab2, tab3 = st.tabs(["📄 REPORT", "🖼️ VISUALS", "📊 PERFORMANCE"])

    with tab1:
        if report:
            st.markdown(
                f'<div class="markdown-content">{report}</div>', unsafe_allow_html=True
            )
        else:
            st.info("No report available for this episode.")

    with tab2:
        if visuals:
            st.markdown("### Chart Analysis Gallery")

            # Grid layout: 2 columns
            cols = st.columns(2)
            for i, item in enumerate(visuals):
                with cols[i % 2]:
                    img_path = (
                        OUTPUTS_DIR
                        / f"episode_{ep_num}"
                        / "images"
                        / item.get("original_filename", "")
                    )

                    with st.container():
                        if img_path.exists():
                            st.image(str(img_path), use_container_width=True)

                        title = item.get("chart_title", "Chart")
                        sentiment = item.get("sentiment", "NEUTRAL")

                        sentiment_class = (
                            "badge-bullish"
                            if sentiment == "BULLISH"
                            else "badge-bearish" if sentiment == "BEARISH" else ""
                        )

                        st.markdown(f"**{title}**")
                        if sentiment_class:
                            st.markdown(
                                f'<span class="{sentiment_class}">{sentiment}</span>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(f"`{sentiment}`")

                        st.markdown(
                            item.get("analysis_summary", ""), unsafe_allow_html=True
                        )
                        st.markdown("---")
        else:
            st.info("No visual analysis available. Run the video pipeline first.")

    with tab3:
        st.markdown("### Signal Performance Tracker")

        if audit_df is not None and not audit_df.empty:
            # Rename columns for display
            display_df = audit_df.rename(
                columns={
                    "ticker": "TICKER",
                    "action": "ACTION",
                    "conviction_score": "CONVICTION",
                    "entry_price": "ENTRY",
                    "return_1m": "T+1M",
                    "return_3m": "T+3M",
                    "return_6m": "T+6M",
                    "status": "STATUS",
                }
            )

            # Filter to relevant columns
            show_cols = [
                "TICKER",
                "ACTION",
                "CONVICTION",
                "ENTRY",
                "T+1M",
                "T+3M",
                "T+6M",
                "STATUS",
            ]
            show_cols = [c for c in show_cols if c in display_df.columns]

            st.dataframe(
                display_df[show_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "TICKER": st.column_config.TextColumn("TICKER", width="medium"),
                    "ACTION": st.column_config.TextColumn("ACTION", width="small"),
                    "CONVICTION": st.column_config.NumberColumn(
                        "CONVICTION", format="%d ⭐"
                    ),
                    "ENTRY": st.column_config.NumberColumn("ENTRY", format="$%.2f"),
                    "T+1M": st.column_config.NumberColumn("T+1M", format="%.1f%%"),
                    "T+3M": st.column_config.NumberColumn("T+3M", format="%.1f%%"),
                    "T+6M": st.column_config.NumberColumn("T+6M", format="%.1f%%"),
                },
            )
        else:
            st.info("No performance data available. Run the audit pipeline.")
