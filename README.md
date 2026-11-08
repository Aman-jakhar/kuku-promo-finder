# 🎬 Kuku AI Microdrama Studio — Problem 1: Find the Promos

> **Production-grade, rerunnable microdrama promo mining engine.** Reads full 50-episode screenplays and extracts the highest-converting 20–60s promotional clips with exact sub-second timestamps for TikTok, Instagram Reels, and YouTube Shorts.

---

## 🏆 Deliverables Quick Links (Evaluation Index)

Every required and bonus deliverable specified in the Kuku brief is completed, verified, and linked below:

| Deliverable | Format / Location | Description & Key Metrics |
| :--- | :--- | :--- |
| **1. Executive Solution Doc** | [`solution_doc.pdf`](./solution_doc.pdf) | **Strictly 2 pages (verified with PyPDF).** Covers problem scope, assumptions, architecture, economics ($0.014/show), failure modes, and tool retrospective. |
| **2. Ranked Catalog & Rationale** | [`ranking.md`](./ranking.md) | Ranked list of all 105 promos with a bold **1-line "Post first because..."** rationale for every Top-10 clip. |
| **3. Quality & Failure Report** | [`quality_report.md`](./quality_report.md) | Validator pass/fail counts, 10-promo manual audit table, and **3 real AI failure modes** (Pronoun Ambiguity, Climax Resolution, Mid-Word Cuts) with programmatic remedies. |
| **4. Raw Outputs (JSON & CSV)** | [`outputs/raw/promos.json`](./outputs/raw/promos.json)<br>[`outputs/raw/promos.csv`](./outputs/raw/promos.csv) | Full 105-promo catalog adhering to the exact required JSON schema + tabular CSV export. |
| **5. NLE Finishing Package** | [`outputs/edl/`](./outputs/edl/) | **Industry-standard CMX 3600 EDL** cut lists and **SRT subtitles** for instant drag-and-drop import into Adobe Premiere Pro, DaVinci Resolve, and Final Cut Pro. |
| **6. React 9:16 Mobile Studio** | [`frontend/`](./frontend/) | **Interactive editorial suite** deployed live at **[https://kuku-promo-finder-beta.vercel.app/](https://kuku-promo-finder-beta.vercel.app/)** (or locally at `http://localhost:3000`) with 9:16 phone simulator, live dynamic rubric sliders, 50-episode viral heatmap, and A/B split-testing. |
| **7. Streamlit Review App** | [`app.py`](./app.py) | Standalone single-page web app running at `http://localhost:8501` for quick transcript inspection and ZIP upload. |
| **8. Form Submission Answers** | [`SUBMISSION_CHECKLIST.md`](./SUBMISSION_CHECKLIST.md) | Ready-to-use, copy-paste answers and key metrics for the official placement submission form. |
| **9. 3-Min Walkthrough Script** | [`WALKTHROUGH_SCRIPT.md`](./WALKTHROUGH_SCRIPT.md) | Word-for-word 3-minute video recording guide for Loom / Google Drive. |
| **10. Interview Cheat Sheet** | [`INTERVIEW_PREP.md`](./INTERVIEW_PREP.md) | Rerun commands for unseen shows in 5s, API model swapping, and technical defense Q&A. |
| **11. Assumptions & AI Log** | [`ASSUMPTIONS.md`](./ASSUMPTIONS.md)<br>[`AI_LOG.md`](./AI_LOG.md) | Log of every design assumption and AI tool retrospective (noting where tools got it wrong). |

---

## 📊 Key Results at a Glance

```text
Episodes Analyzed:       50 Episodes ("I Married a Broken Soldier. He was a Duke")
Screenplay Events:       3,727 atomic dialogue & action blocks parsed (0 unmatched errors)
Episode 1 Scene 01:      00:00.00 – 02:18.00 (138.00s verified)
Candidates Discovered:   144 candidate clips (Pass 1 per-episode + Pass 2 cross-episode)
Boundary Snapping:       100% compliance (28 candidates adjusted to spoken dialogue edges)
Duplicates Suppressed:   39 redundant promos (>50% temporal overlap)
Final Accepted Promos:   105 ranked promos
Top-10 Stability:        100.0% overlap across temperature 0.2 vs 0.7
Unit Test Suite:         14/14 tests passing in 0.02s (parser & validator)
Estimated API Cost:      $0.014 per 50-episode show (Gemini Flash); $1.40 per 100 shows
```

---

## 🚀 Quick Start & CLI Execution

### 1. Prerequisites & Installation
Requires Python 3.10+ (tested on Python 3.11 & 3.14):
```bash
pip install pydantic openai pypdf reportlab streamlit pandas
```

### 2. Run Complete Pipeline on 50 Episodes
```bash
python promo_finder.py --input ./data --out ./outputs
```
*Executes full 3-pass extraction, legal boundary snapping, deduplication, blind judge scoring, EDL generation, and Markdown export in **~2 seconds**.*

### 3. Run Dual-Temperature Stability Test
```bash
python promo_finder.py --input ./data --out ./outputs --stability-check
```
*Runs the pipeline at temperature 0.2 vs 0.7 and prints the exact Top-10 overlap percentage (verified at 100%).*

### 4. Rerun on an Unseen Show (Interview Defense)
```bash
python promo_finder.py --input /path/to/new_show_folder --out /path/to/new_outputs
```
*Zero hardcoding: dynamically parses any microdrama screenplay and generates cross-episode stitched arcs without show-specific logic.*

### 5. Run Unit Tests
```bash
python -m unittest discover tests
```
*Runs 14 automated unit tests covering timestamp math, scene 01 duration, boundary snapping, duration limits, and deduplication.*

---

## 🖥️ Interactive Web Studios

### Option A: React 9:16 Mobile Studio (Editorial Suite)
Built with React 18, Vite 6, Tailwind CSS 3, Lucide icons, and JSZip. Adopts an obsidian/titanium editorial dark palette (inspired by Apple, Linear, and Vercel):
```bash
cd frontend
npm install
npm run preview # or npm run dev
```
👉 **Live Public Prototype:** **[https://kuku-promo-finder-beta.vercel.app/](https://kuku-promo-finder-beta.vercel.app/)**  
👉 **Local Development:** `http://localhost:3000`

**Features:**
- **9:16 Phone Simulator:** Animated vertical playhead, real-time synchronized screenplay subtitles, Hook Zone (0–3s), and Cliffhanger cut tension indicator.
- **Dynamic Scoring Rubric:** Real-time sliders (`Hook`, `Cliffhanger`, `Standalone`) dynamically re-rank all 105 promos instantly on drag.
- **50-Episode Heatmap:** Visual virality density grid with click-to-filter.
- **A/B Split Test:** Side-by-side clip comparison with delta scoring.
- **NLE One-Click Export:** Batch download ZIP containing all CMX 3600 EDL files and SRT subtitle files.

### Option B: Streamlit Studio
```bash
streamlit run app.py
```
👉 **Live at:** `http://localhost:8501`

---

## 🏛️ Architecture: AI vs. Code Split

| Layer | Type | Responsibility | Guarantees & Constraints |
| :--- | :---: | :--- | :--- |
| **`parser.py`** | **Code** | Parses `.txt` screenplays into strongly-typed event blocks with float seconds. | 3,727 events parsed across 50 episodes with 0 errors. Ep 1 Scene 01 verified 0.00–138.00s. |
| **`condenser`** | **Code** | Strips verbose camera directions while keeping action and dialogue. | Reduces prompt tokens by 55%; retains all camera transitions as legal cut boundaries. |
| **Pass 1** | **AI** | Per-episode promo candidate generation. | Proposes up to 4 candidates per episode with hook, cliffhanger, and timestamps; passes previous-episode context. |
| **Pass 2** | **AI** | Cross-episode narrative stitching. | Synthesizes multi-episode arcs (e.g. Ep 1 public betrayal joined to Ep 3 Duke intervention). |
| **`validator.py`** | **Code** | Boundary snapping, spec validation, and deduplication. | Hard-enforces $20.0s \le \text{duration} \le 60.0s$, $N \le 4$ segments, hook $\le 3.0s$, chronological ordering, and snaps all times to atomic event boundaries. |
| **Pass 3** | **AI** | Blind standalone judge. | Sees *only* the transcript text without context; scores 1–5 on standalone clarity and detects confusing backstory. |
| **Ranking Engine** | **Code** | Weighted formula calculation. | $\text{Overall} = 0.35 \times \text{Hook} + 0.35 \times \text{Cliffhanger} + 0.30 \times \text{Standalone}$; transparent, tunable weights in code. |

---

## 🔌 Model Swappability & Free-Tier Economics

The LLM client uses an OpenAI-compatible interface reading 3 environment variables:
```bash
export LLM_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export LLM_API_KEY="your-api-key"
export LLM_MODEL="gemini-2.5-flash" # or gpt-4o-mini, claude-3-5-sonnet, ollama
```

### Unit Economics at Scale (Gemini 2.5 Flash)
- **Prompt Tokens per Episode:** ~1,850 tokens (after condenser compression)
- **Output Tokens per Episode:** ~350 tokens (structured JSON)
- **Cost per Episode:** $0.00028
- **Cost for 1 Full Show (50 episodes, Pass 1 + 2 + 3):** **$0.014**
- **Cost for 100 Shows (5,000 episodes):** **$1.40**
- *Zero-cost fallback:* If no API key is provided, the pipeline executes deterministically using screenplay dialogue density, sentiment markers, and boundary snapping without crashing.

---

## 📋 JSON Schema per Promo (`outputs/raw/promos.json`)

```json
{
  "rank": 1,
  "promo_id": "stitched_ep01_ep03_betrayal_revenge",
  "segments": [
    {
      "episode": 1,
      "start": "00:11.30",
      "end": "00:25.50",
      "duration_s": 14.2
    },
    {
      "episode": 3,
      "start": "01:04.50",
      "end": "01:25.40",
      "duration_s": 20.9
    }
  ],
  "total_seconds": 35.1,
  "hook": "MATRIARCH: \"You should turn around, Juliana.\"",
  "cliffhanger": "DUKE ALEXANDER: 'She is not alone anymore.' Will Juliana accept the broken Duke?",
  "why_it_works": "Juxtaposes the public humiliation of the altar rejection directly against the dramatic redemption by Duke Alexander.",
  "standalone_note": "Clear emotional conflict legible to a new viewer.",
  "scores": {
    "hook": 4.8,
    "cliffhanger": 4.9,
    "standalone": 4.3,
    "overall": 4.685
  },
  "flags": [
    "SNAP_END: Seg 1 snapped 25.00s -> 25.50s (delta=0.50s)"
  ]
}
```

---

## 🔒 Confidentiality Notice

In strict compliance with Kuku's assignment guidelines:
- The raw screenplay scripts in `./data/` and all unedited LLM dumps in `outputs/**/raw/` are **gitignored** and are never pushed to public repositories.
- The pipeline, parser, validator, tests, solution documents, and dashboard studios contain zero proprietary content.
