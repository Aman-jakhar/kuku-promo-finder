# 🎬 Kuku AI Microdrama Studio — Problem 1: Find the Promos

A production-grade, rerunnable pipeline that reads microdrama screenplays and outputs the highest-converting 20–60s promo clips with exact timestamps for TikTok, Instagram Reels, and YouTube Shorts.

---

## 🚀 Quick Start

### 1. Installation
Clone or navigate to this workspace and install dependencies:
```bash
pip install pydantic openai pypdf reportlab streamlit pandas
```

### 2. Configure Model (Optional)
The pipeline features an OpenAI-compatible interface supporting Gemini (default free tier), OpenAI, Groq, or local Ollama. It runs seamlessly with an API key, or in an offline drama-mining mode if unconfigured:
```bash
# Optional: Set your preferred API key in environment or .env
export LLM_API_KEY="your-gemini-or-openai-key"
export LLM_MODEL="gemini-2.5-flash" # or gpt-4o-mini
```

### 3. Run CLI Pipeline
Process all 50 screenplay episodes in `./data/`:
```bash
python promo_finder.py --input ./data --out ./outputs
```

To run a dual-temperature stability check (evaluating Top-10 ranking consistency):
```bash
python promo_finder.py --input ./data --out ./outputs --stability-check
```

### 4. Launch Interactive Streamlit Studio
Launch the web interface to audit, filter, and inspect clip transcripts and timestamps:
```bash
streamlit run app.py
```

### 5. Run Unit Tests
```bash
python -m unittest discover tests
```

---

## 🏛️ Architecture: AI vs. Code Split

| Layer | Type | Responsibility | Guarantees |
| :--- | :---: | :--- | :--- |
| **`parser.py`** | **Code** | Ingests `.txt` screenplays into structured events with float seconds | Unit-tested on Episode 1 (Scene 01 runs 0.00–138.00s); 3,727 events across 50 episodes parsed with 0 errors |
| **`condenser`** | **Code** | Compresses dialogue/action lines for LLM prompts | Drops `CAMERA` lines to save 55% tokens; preserves event boundaries as legal cut points |
| **Pass 1** | **AI** | Per-episode candidate generation | Proposes up to 4 candidates with hook, cliffhanger, and timestamps; passes previous-episode context |
| **Pass 2** | **AI** | Cross-episode stitched promos | Synthesizes multi-episode arcs (e.g. Episode 1 betrayal joined with Episode 3 Duke marriage) |
| **`validator.py`** | **Code** | Deterministic spec enforcement & boundary snapping | Rejects <20s or >60s, >4 segments, out-of-order chronology, hooks >3.0s; snaps times to nearest event boundary |
| **Pass 3** | **AI** | Blind standalone judge | Evaluates *only* transcript text without context; rates clarity 1–5 and detects confusing backstory |
| **Ranking Engine** | **Code** | Weighted formula calculation | `Overall = 0.35*Hook + 0.35*Cliffhanger + 0.30*Standalone`; weights are visible and tunable in code |

---

## 📁 Repository Structure

```text
├── promo_finder.py           # CLI entry point (--input, --out, --stability-check)
├── pipeline.py               # 3-pass orchestration engine
├── parser.py                 # Deterministic screenplay parser & condenser
├── validator.py              # Timestamp snapping, spec validator & deduplication
├── llm_client.py             # Thin, cached OpenAI-compatible LLM client
├── app.py                    # Interactive Streamlit Studio for editorial review
├── generate_solution_pdf.py  # Compiles publication-grade 2-page PDF solution doc
├── solution_doc.pdf          # Official 2-page PDF solution document
├── SOLUTION_DOC.md           # Markdown version of 2-page solution document
├── ranking.md                # Ranked list with 1-line "post first because..." for Top 10
├── quality_report.md         # Validator pass/fail stats, 10-promo audit & failure modes
├── ASSUMPTIONS.md            # Documented assumptions log
├── AI_LOG.md                 # Running log of tools, LLM calls, and AI failure modes
├── tests/
│   ├── test_parser.py        # 7 unit tests (timestamps, scene 01 duration, headers)
│   └── test_validator.py     # 7 unit tests (duration bounds, snapping, deduplication)
├── data/                     # Confidential episode scripts (gitignored)
└── outputs/
    └── raw/
        ├── promos.json       # Final ranked promos adhering to exact required schema
        ├── promos.csv        # Tabular export for spreadsheets & scheduling tools
        └── pass*.json        # Unedited raw responses per episode & pass
```

---

## 📋 Deliverable Artifacts

1. **`outputs/raw/promos.json`**:
   Schema per promo:
   ```json
   {
     "rank": 1,
     "promo_id": "stitched_ep01_ep03_betrayal_revenge",
     "segments": [
       {"episode": 1, "start": "00:11.30", "end": "00:25.50", "duration_s": 14.2},
       {"episode": 3, "start": "01:04.50", "end": "01:25.40", "duration_s": 20.9}
     ],
     "total_seconds": 35.1,
     "hook": "MATRIARCH: \"You should turn around, Juliana.\"",
     "cliffhanger": "DUKE ALEXANDER: 'She is not alone anymore.' Will Juliana accept the broken Duke?",
     "why_it_works": "Juxtaposes the public humiliation of the altar rejection directly against the dramatic redemption by Duke Alexander.",
     "standalone_note": "Strong interpersonal tension, high emotional stakes legible from character dynamics.",
     "scores": {
       "hook": 4.8,
       "cliffhanger": 4.9,
       "standalone": 4.3,
       "overall": 4.685
     },
     "flags": ["SNAP_END: Seg 1 snapped 25.00s -> 25.50s (delta=0.50s)"]
   }
   ```
2. **`ranking.md`**: Top 10 promos with a 1-line justification (`Post first because...`) plus complete catalog.
3. **`quality_report.md`**: Validation pass rates (100% boundary compliance), 10 hand-audited clips, and 3 real failure modes.
4. **`solution_doc.pdf`**: The requested 2-page PDF solution brief.
