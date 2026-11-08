"""app.py

Streamlit Web Application for Kuku Microdrama Promo Finder.
Interactive interface to browse, audit, filter, and inspect extracted promos.

Features:
- View ranked promos from outputs/raw/promos.json or run pipeline on uploaded zip/folder
- Filter by episode, duration, minimum score
- Expandable clip details with exact timestamps, hook/cliffhanger cards, and full screenplay transcript
- Visual score badges and boundary snap audit
- Download filtered promos as JSON or CSV
"""

import io
import json
import os
import zipfile
from pathlib import Path
import streamlit as st
import pandas as pd

from parser import parse_all_episodes, parse_episode_file, condense_episode, format_timestamp
from pipeline import extract_episode_clip_text

st.set_page_config(
    page_title="Kuku Microdrama Promo Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎬 Kuku Microdrama Promo Studio")
st.caption("AI-Powered Promo Finder: Extracting high-conversion 20–60s vertical clips with exact timestamps")

# ---------------------------------------------------------
# Sidebar: Configuration & Data Source
# ---------------------------------------------------------
st.sidebar.header("📁 Data Source & Pipeline")

data_source = st.sidebar.radio(
    "Select Source",
    ["Use Existing Outputs (./outputs/raw/)", "Upload Script Zip (.zip)", "Inspect ./data/ Directory"]
)

promos_data = []
episodes_dict = {}

# Load pre-parsed episodes if available in ./data/
if Path("data").exists():
    try:
        episodes_dict = parse_all_episodes("data")
    except Exception:
        pass

if data_source == "Use Existing Outputs (./outputs/raw/)":
    promos_file = Path("outputs/raw/promos.json")
    if promos_file.exists():
        try:
            promos_data = json.loads(promos_file.read_text(encoding="utf-8"))
            st.sidebar.success(f"Loaded {len(promos_data)} promos from `{promos_file}`")
        except Exception as e:
            st.sidebar.error(f"Error loading promos.json: {e}")
    else:
        st.sidebar.warning("`outputs/raw/promos.json` not found. Please run the CLI pipeline first.")

elif data_source == "Upload Script Zip (.zip)":
    uploaded_zip = st.sidebar.file_uploader("Upload microdrama scripts (.zip)", type=["zip"])
    if uploaded_zip is not None:
        with zipfile.ZipFile(uploaded_zip, "r") as z:
            txt_files = [n for n in z.namelist() if n.endswith(".txt") and not n.startswith("__MACOSX")]
            st.sidebar.info(f"Found {len(txt_files)} screenplay files in archive.")
            if st.sidebar.button("Process Scripts"):
                temp_dir = Path("./outputs/uploaded_data")
                temp_dir.mkdir(parents=True, exist_ok=True)
                for f in txt_files:
                    target = temp_dir / Path(f).name
                    target.write_bytes(z.read(f))
                episodes_dict = parse_all_episodes(temp_dir)
                st.sidebar.success(f"Parsed {len(episodes_dict)} episodes.")

# ---------------------------------------------------------
# Metrics Dashboard
# ---------------------------------------------------------
if promos_data:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Promos Extracted", len(promos_data))
    with col2:
        top_score = max(p["scores"]["overall"] for p in promos_data)
        st.metric("Top Overall Score", f"{top_score:.3f}")
    with col3:
        avg_dur = sum(p["total_seconds"] for p in promos_data) / len(promos_data)
        st.metric("Avg Duration", f"{avg_dur:.1f}s")
    with col4:
        multi_seg = sum(1 for p in promos_data if len(p["segments"]) > 1)
        st.metric("Multi-Segment / Stitched", multi_seg)

    st.markdown("---")

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------
    st.sidebar.subheader("🔍 Filters")
    min_score = st.sidebar.slider("Min Overall Score", 1.0, 5.0, 3.5, 0.1)
    dur_range = st.sidebar.slider("Duration Range (seconds)", 20.0, 60.0, (20.0, 60.0), 1.0)
    
    # Filter
    filtered = [
        p for p in promos_data
        if p["scores"]["overall"] >= min_score and dur_range[0] <= p["total_seconds"] <= dur_range[1]
    ]

    st.write(f"Showing **{len(filtered)}** promos matching criteria:")

    # ---------------------------------------------------------
    # Promos Table & Detail View
    # ---------------------------------------------------------
    table_rows = []
    for p in filtered:
        episodes_str = ", ".join(str(s["episode"]) for s in p["segments"])
        timestamps_str = " + ".join(f"[{s['start']}–{s['end']}]" for s in p["segments"])
        table_rows.append({
            "Rank": f"#{p.get('rank', '-')}",
            "Promo ID": p["promo_id"],
            "Episodes": episodes_str,
            "Duration": f"{p['total_seconds']:.1f}s",
            "Hook Score": f"{p['scores']['hook']:.2f}",
            "Cliffhanger": f"{p['scores']['cliffhanger']:.2f}",
            "Standalone": f"{p['scores']['standalone']:.2f}",
            "Overall Score": f"{p['scores']['overall']:.3f}",
            "Timestamps": timestamps_str
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # Detailed Inspector per Promo
    # ---------------------------------------------------------
    st.subheader("🧐 Deep Clip Inspector")
    selected_promo_id = st.selectbox(
        "Select a Promo to Inspect",
        options=[p["promo_id"] for p in filtered],
        format_func=lambda x: f"Rank #{next(p['rank'] for p in filtered if p['promo_id'] == x)}: {x}"
    )

    if selected_promo_id:
        p = next(item for item in filtered if item["promo_id"] == selected_promo_id)

        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"### `#{p.get('rank', '-')}` — {p['promo_id']}")
            st.markdown(f"**Why it works:** {p['why_it_works']}")
            st.markdown(f"**Standalone Note:** {p['standalone_note']}")

            # Hook and Cliffhanger callout cards
            st.info(f"**🎣 Hook (First 3s):** {p['hook']}")
            st.warning(f"**⚡ Cliffhanger Cut:** {p['cliffhanger']}")

        with c2:
            st.markdown("#### 📊 Score Breakdown")
            st.write(f"- **Hook Punch:** `{p['scores']['hook']:.2f} / 5.0`")
            st.write(f"- **Cliffhanger Tension:** `{p['scores']['cliffhanger']:.2f} / 5.0`")
            st.write(f"- **Standalone Clarity:** `{p['scores']['standalone']:.2f} / 5.0`")
            st.markdown(f"### **Overall: `{p['scores']['overall']:.3f}`**")

            if p.get("flags"):
                st.markdown("#### 🏷️ Validator Flags / Snaps")
                for flg in p["flags"]:
                    st.caption(f"• `{flg}`")

        # Full screenplay clip transcript
        st.markdown("#### 📜 Script Transcript for Clip")
        for seg in p["segments"]:
            ep_num = seg["episode"]
            st.markdown(f"**Segment: Episode {ep_num} [{seg['start']} - {seg['end']}] (Duration: {seg.get('duration_s', 0):.1f}s)**")
            
            if ep_num in episodes_dict:
                ep = episodes_dict[ep_num]
                s_float = seg.get("start_s", 0.0)
                e_float = seg.get("end_s", 0.0)
                if not s_float and "start" in seg:
                    from parser import parse_timestamp
                    s_float = parse_timestamp(seg["start"])
                    e_float = parse_timestamp(seg["end"])
                clip_text = extract_episode_clip_text(ep, s_float, e_float)
                st.text_area(f"Ep {ep_num} Text", clip_text, height=180)
            else:
                st.caption(f"(Screenplay file for Episode {ep_num} not loaded in memory)")

    # ---------------------------------------------------------
    # Downloads
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📥 Export Filtered Promos")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(
            label="Download Filtered promos.json",
            data=json.dumps(filtered, indent=2),
            file_name="filtered_promos.json",
            mime="application/json"
        )
    with d_col2:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Filtered promos.csv",
            data=csv_buffer.getvalue(),
            file_name="filtered_promos.csv",
            mime="text/csv"
        )
else:
    st.info("Run the CLI (`python promo_finder.py --input ./data --out ./outputs`) to generate promo data.")
