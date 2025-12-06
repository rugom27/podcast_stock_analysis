import streamlit as st
import os
import json
from pathlib import Path

# === CONFIGURATION ===
st.set_page_config(page_title="Hedge Fund Tips Reports", page_icon="📈", layout="wide")

# Define the base directory where outputs are stored
OUTPUTS_DIR = Path("outputs")

# === HELPER FUNCTIONS ===


def get_available_episodes():
    """
    Scans the outputs directory for folders matching 'episode_{num}'
    and checks if a report exists inside them.
    Returns a sorted list of episode numbers (descending).
    """
    episodes = []

    if not OUTPUTS_DIR.exists():
        return []

    for item in OUTPUTS_DIR.iterdir():
        if item.is_dir() and item.name.startswith("episode_"):
            try:
                ep_num = item.name.split("_")[1]
                # Check for either the text report OR the visual analysis
                report_path = (
                    item / "transcripts" / f"hedge_fund_tips_episode_{ep_num}_report.md"
                )
                visual_path = item / "step5_visual_analysis_complete.json"

                if report_path.exists() or visual_path.exists():
                    episodes.append(ep_num)
            except IndexError:
                continue

    # Sort episodes numerically descending
    try:
        episodes.sort(key=lambda x: int(x), reverse=True)
    except ValueError:
        episodes.sort(reverse=True)

    return episodes


def load_report(episode_number):
    """Reads the markdown content for a specific episode."""
    path = (
        OUTPUTS_DIR
        / f"episode_{episode_number}"
        / "transcripts"
        / f"hedge_fund_tips_episode_{episode_number}_report.md"
    )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def load_visual_analysis(episode_number):
    """Reads the Visual Analysis JSON (Step 5 output)."""
    path = (
        OUTPUTS_DIR
        / f"episode_{episode_number}"
        / "step5_visual_analysis_complete.json"
    )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# === MAIN UI ===

# Sidebar
with st.sidebar:
    st.header("🗂️ Library")
    available_episodes = get_available_episodes()

    if not available_episodes:
        st.warning("No reports found in `outputs/`.")
        st.info("Run the notebook pipeline first to generate reports.")
        selected_episode = None
    else:
        selected_episode = st.selectbox("Select Episode:", available_episodes, index=0)
        st.markdown("---")
        st.caption(f"Found {len(available_episodes)} episodes.")

# Main Content Area
st.title(f"📈 Hedge Fund Tips Analysis")

if selected_episode:
    # 1. LOAD DATA
    text_content = load_report(selected_episode)
    visual_data = load_visual_analysis(selected_episode)

    # 2. RENDER TABS
    # We use tabs to keep the interface clean
    tab1, tab2 = st.tabs(["📄 Executive Report", "📊 Visual Intelligence"])

    # --- TAB 1: TEXT REPORT ---
    with tab1:
        if text_content:
            st.markdown(text_content, unsafe_allow_html=True)
        else:
            st.warning("Text report not found for this episode.")

    # --- TAB 2: VISUAL GALLERY ---
    with tab2:
        if visual_data:
            st.info(f"AI analyzed {len(visual_data)} visual artifacts from the video.")

            for item in visual_data:
                # Layout: Image (Left) | Analysis (Right)
                with st.container():
                    col1, col2 = st.columns([1, 1.5], gap="large")

                    with col1:
                        # Construct image path
                        img_path = (
                            OUTPUTS_DIR
                            / f"episode_{selected_episode}"
                            / "images"
                            / item["original_filename"]
                        )
                        if img_path.exists():
                            st.image(str(img_path), use_container_width=True)

                            # Timestamp and filename details
                            minutes = item["timestamp_seconds"] // 60
                            seconds = item["timestamp_seconds"] % 60
                            st.caption(
                                f"⏱️ **Timestamp:** {minutes}m {seconds}s | 📂 {item['original_filename']}"
                            )
                        else:
                            st.error(f"Image not found: {item['original_filename']}")

                    with col2:
                        # Title and Sentiment Badge
                        st.subheader(item.get("chart_title", "Untitled Chart"))

                        sentiment = item.get("sentiment", "NEUTRAL").upper()
                        if sentiment == "BULLISH":
                            st.success(f"**SENTIMENT:** {sentiment}")
                        elif sentiment == "BEARISH":
                            st.error(f"**SENTIMENT:** {sentiment}")
                        else:
                            st.info(f"**SENTIMENT:** {sentiment}")

                        # Analysis Body
                        st.markdown(
                            f"**🧠 Analysis:** {item.get('analysis_summary', 'No summary available.')}"
                        )

                        # Key Data Points
                        if item.get("key_data_points"):
                            st.markdown("**Key Levels:**")
                            for kp in item["key_data_points"]:
                                st.markdown(f"- {kp}")

                        # Confirmation status
                        confirm = item.get("visual_confirmation", "UNCLEAR")
                        if confirm == "CONFIRMED":
                            st.caption("✅ Image visually confirms transcript")
                        elif confirm == "CONTRADICTED":
                            st.caption("⚠️ Image appears to contradict transcript")

                        # Context Quote
                        with st.expander("🗣️ Transcript Context"):
                            st.markdown(
                                f"*{item.get('transcript_context', 'No text context matched.')}*"
                            )

                    st.divider()
        else:
            st.info("No visual analysis found. Ask the owner to get to work.")

else:
    st.info("👈 Please select an episode from the sidebar to view the analysis.")

# Footer
st.markdown("---")
st.caption("De nada, powered by Streamlit 🚀")
