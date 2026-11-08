# AI Log & Tool Usage

This log documents every tool used, LLM calls made, decisions, edge cases encountered, and corrections throughout the development of Problem 1 ("Find the Promos").

## Log Entries

### 1. Setup & Environment
- **Action**: Initialized `.gitignore` covering `data/`, `outputs/raw/`, `.env`, and temporary files to safeguard confidential Kuku scripts.
- **Dependencies**: Checked environment, installed `pydantic`, `openai`, `pypdf`, `reportlab`, `streamlit`, `pandas`.
- **Node.js**: Verified Node v24.14.0 and npm 11.9.0 available for high-tier React development.
- **Data Ingestion**: Unzipped 50 episode script files into `data/`. Verified all 50 files contain consistent header schemas (`EPISODE NUMBER:`, `EPISODE LOGLINE:`, `CONTINUITY NOTES:`, `--- SCRIPT START ---`, `--- SCRIPT END ---`).

### 2. Deterministic Screenplay Parser (`parser.py`)
- **Implementation**:
  - `parse_timestamp()`: Converts `MM:SS.ss` to float seconds from episode start `0.0`.
  - `format_timestamp()`: Converts float seconds to `MM:SS.ss`.
  - `parse_label()`: Accurately segments `CAMERA`, `ACTION`, `SOUND FX`, and character dialogue lines with speaker and optional parenthetical emotion.
  - `parse_episode_file()`: Extracts episode number, logline, continuity notes, scenes, and events into strongly-typed dataclasses.
  - `condense_episode()`: Renders compact dialogue/action lines for LLM context, omitting verbose camera instructions while retaining all event boundaries as legal cut points.
- **Verification on Dataset**:
  - Scanned all 50 episodes: 3,727 total event blocks parsed with zero unmatched blocks.
  - Episode 1 Scene 01 verified: exactly `00:00.00` to `02:18.00` (0.00s to 138.00s).

### 3. Boundary Snapping & Validator (`validator.py`)
- **Implementation**:
  - `snap_and_validate()`: Checks hard specifications:
    1. Duration bounds: strictly $20.0s \le \text{total} \le 60.0s$.
    2. Segment count: $1 \le N \le 4$.
    3. Boundary snapping: LLM-proposed start/end timestamps snap to nearest legal event boundary; flags large shifts ($>3.0s$).
    4. Ordering & non-overlap: chronological sequence within and across episodes.
    5. Hook timing: verifies an action/dialogue event starts within the first 3.0s window.
    6. Deduplication: suppresses duplicate candidate promos sharing $\ge 50\%$ temporal overlap, prioritizing higher overall scores.
- **Testing**:
  - `tests/test_parser.py`: 7/7 tests passed.
  - `tests/test_validator.py`: 7/7 tests passed.
  - Total 14 unit tests passing in 0.016s.

### 4. 3-Pass Architecture & Production Pipeline (`pipeline.py` & `promo_finder.py`)
- **Pass 1 (Per-Episode Mining)**: Evaluated all 50 episodes, producing 143 candidate clips.
- **Pass 2 (Cross-Episode Stitching)**: Synthesized high-impact multi-episode arcs (e.g. Ep 1 betrayal joined with Ep 3 Duke marriage).
- **Pass 3 (Blind Standalone Judge)**: Judged all candidates seeing only clip text without context.
- **Ranking**: Weighted scoring formula: $0.35 \times \text{Hook} + 0.35 \times \text{Cliffhanger} + 0.30 \times \text{Standalone}$.
- **Deliverables**: Generated `outputs/raw/promos.json`, `outputs/raw/promos.csv`, `ranking.md`, `quality_report.md`.
- **Stability Check**: Verified dual-temperature execution (0.2 vs 0.7) with 100% Top-10 overlap.

### 5. Advanced Production Upgrades (Competitive Edge)
- **NLE Direct Export (`edl_exporter.py`)**: Generated industry-standard CMX 3600 EDL files and SRT subtitles for video editors using Adobe Premiere Pro, DaVinci Resolve, or Final Cut Pro.
- **React 9:16 Mobile Studio (`frontend/`)**: Built a modern React + Vite + Tailwind dashboard with:
  - Interactive 9:16 vertical phone mockup showing real-time text playhead, Hook Zone (0–3s in red), Body, and Cliffhanger cut in gold.
  - Real-time dynamic rubric weight tuner (sliders re-calculate ranks instantly on drag).
  - Search, filter by episode, and one-click EDL cut export.
  - Running live on `http://localhost:3000`.
- **Streamlit App (`app.py`)**: Running live on `http://localhost:8501`.
- **Editorial UI/UX Design System Overhaul**:
  - Replaced high-saturation "AI-generated" purple/rose/amber accents with an understated obsidian/titanium editorial design inspired by Apple, Vercel, and Linear.
  - Neutral `#0A0A0A` page canvas with single-tint border ladders (`rgba(255,255,255,0.07)`), Inter typography, and desaturated status dots.
  - Built unified aesthetic across all 6 studio workspaces (Catalog, Heatmap, 9:16 Mobile Studio, A/B Split Test, Quality Center, NLE Finishing).
  - Verified clean `vite build` and active preview daemon serving at `http://localhost:3000`.
- **2-Page Executive Solution Document (`solution_doc.pdf`)**: Compiled using ReportLab with exact 2-page hard constraint verified.
- **Walkthrough Video Script (`WALKTHROUGH_SCRIPT.md`)**: Complete 3-minute, word-for-word Loom recording guide.
- **Interview Prep Guide (`INTERVIEW_PREP.md`)**: Rerun on unseen show folders in 5s, model swapping instructions, and technical Q&A cheat sheet.
