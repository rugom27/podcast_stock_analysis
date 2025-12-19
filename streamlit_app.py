import streamlit as st
import pandas as pd
import json
from pathlib import Path

# === CONFIGURATION ===
st.set_page_config(page_title="Hedge Fund Tips Analysis", page_icon="📈", layout="wide")

OUTPUTS_DIR = Path("outputs")
GLOBAL_DIR = OUTPUTS_DIR / "global_audit"


# === HELPERS ===
def get_available_episodes():
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
    """Loads assets for a specific episode."""
    base = OUTPUTS_DIR / f"episode_{ep_num}"

    # Text
    text_content = None
    r_path = base / "transcripts" / f"hedge_fund_tips_episode_{ep_num}_report.md"
    if r_path.exists():
        with open(r_path, "r", encoding="utf-8") as f:
            text_content = f.read()

    # Visuals
    visual_data = None
    v_path = base / "step5_visual_analysis_complete.json"
    if v_path.exists():
        with open(v_path, "r", encoding="utf-8") as f:
            visual_data = json.load(f)

    # NEW: Signal Audit (Episode Specific)
    audit_df = None
    a_path = base / "episode_signals_audit.csv"
    if a_path.exists():
        audit_df = pd.read_csv(a_path)

    return text_content, visual_data, audit_df


def load_global_data():
    sc = (
        pd.read_csv(GLOBAL_DIR / "master_ticker_scorecard.csv")
        if (GLOBAL_DIR / "master_ticker_scorecard.csv").exists()
        else None
    )
    sig = (
        pd.read_csv(GLOBAL_DIR / "master_signals_audit.csv")
        if (GLOBAL_DIR / "master_signals_audit.csv").exists()
        else None
    )
    return sc, sig


# === SIDEBAR ===
with st.sidebar:
    st.header("🗂️ Library")
    options = ["🌎 Global Performance"] + get_available_episodes()
    selected_option = st.selectbox("Select View:", options, index=0)

# === MAIN LOGIC ===

# --- OPTION A: GLOBAL ---
if selected_option == "🌎 Global Performance":
    st.title("🌎 Global Performance Audit")
    master_scorecard, master_signals = load_global_data()

    tab_g1, tab_g2 = st.tabs(["🏆 Master Scorecard", "📡 All Signals Log"])

    with tab_g1:
        if master_scorecard is not None:
            st.dataframe(
                master_scorecard,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Win_Rate": st.column_config.ProgressColumn(
                        "Win Rate", format="%d%%", min_value=0, max_value=100
                    ),
                    "Avg_Return_1Mo": st.column_config.NumberColumn(
                        "1M Avg", format="%.1f%%"
                    ),
                    "Avg_Return_6Mo": st.column_config.NumberColumn(
                        "6M Avg", format="%.1f%%"
                    ),
                },
            )
        else:
            st.warning("Run global audit script first.")

    with tab_g2:
        if master_signals is not None:
            st.dataframe(master_signals, use_container_width=True, hide_index=True)
        else:
            st.warning("No global signals found.")

# --- OPTION B: EPISODE ---
else:
    ep_num = selected_option
    st.title(f"📈 Episode {ep_num} Analysis")
    text, visuals, audit_df = load_episode_data(ep_num)

    # 3 TABS: Report, Visuals, Performance (Signals)
    tab1, tab2, tab3 = st.tabs(
        ["📄 Executive Report", "📊 Visual Intelligence", "📡 Performance Audit"]
    )

    with tab1:
        if text:
            st.markdown(text, unsafe_allow_html=True)
        else:
            st.info("No report text found.")

    with tab2:
        if visuals:
            for item in visuals:
                with st.container():
                    c1, c2 = st.columns([1, 2])
                    img_path = (
                        OUTPUTS_DIR
                        / f"episode_{ep_num}"
                        / "images"
                        / item["original_filename"]
                    )
                    if img_path.exists():
                        c1.image(str(img_path))
                    c2.subheader(item.get("chart_title", "Chart"))
                    c2.write(item.get("analysis_summary", ""))
                    st.divider()
        else:
            st.info("No visual analysis found.")

    with tab3:
        if audit_df is not None and not audit_df.empty:
            st.markdown("### 📊 Signal Performance vs Current Price")

            # Helper to style the dataframe
            # We want to highlight the Current Return and T+ Returns
            st.dataframe(
                audit_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "Action": st.column_config.TextColumn("Signal", width="small"),
                    "Conviction": st.column_config.NumberColumn(
                        "Conviction", format="%d ⭐"
                    ),
                    "Entry_Price": st.column_config.NumberColumn(
                        "Entry Price", format="$%.2f"
                    ),
                    "Current_Price": st.column_config.NumberColumn(
                        "Current Price", format="$%.2f"
                    ),
                    "Current_Return_Pct": st.column_config.NumberColumn(
                        "⚠️ Total Return",
                        format="%.2f%%",
                        help="Return from Signal Date to Today",
                    ),
                    "T+1m": st.column_config.NumberColumn("T+1M", format="%.2f%%"),
                    "T+3m": st.column_config.NumberColumn("T+3M", format="%.2f%%"),
                    "T+6m": st.column_config.NumberColumn("T+6M", format="%.2f%%"),
                },
            )
        else:
            st.info("No signals audit found. Run the updated notebook script.")
