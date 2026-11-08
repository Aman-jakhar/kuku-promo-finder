# 🎯 Kuku Placement Submission Checklist & Form Answers

Use this reference sheet when filling out the official Kuku submission form.

---

## 📋 Form Details to Copy-Paste

| Field | What to Enter / Copy |
| :--- | :--- |
| **Problem Chosen** | **Problem 1: Find the Promos** |
| **Solution Doc Link** | Path to [`solution_doc.pdf`](./solution_doc.pdf) *(strictly 2 pages max, verified)* |
| **Prototype Link** | Link to your GitHub Repo / Hosted App (e.g. `http://localhost:3000` or Streamlit / Vercel deployment) |
| **Raw Outputs Folder Link** | Path to [`outputs/raw/`](./outputs/raw/) *(contains all per-episode JSONs + final `promos.json` + `promos.csv`)* |
| **Walkthrough Video Link (Optional & Recommended)** | Up to 3-minute screen recording using [`WALKTHROUGH_SCRIPT.md`](./WALKTHROUGH_SCRIPT.md) (Loom / Google Drive / Unlisted YouTube) |

---

## 🔑 Key Numbers to Quote in Your Form / Interview

- **Episodes Evaluated:** 50 Episodes of *"I Married a Broken Soldier. He was a Duke"*
- **Total Screenplay Events Parsed:** 3,727 events (0 unmatched blocks)
- **Episode 1 Scene 01 Duration:** Exactly `00:00.00` to `02:18.00` (138.00s verified)
- **Candidates Discovered:** 144 candidate clips
- **Boundary Snapping Adjustments:** 28 candidates (19.4% adjusted to spoken dialogue edges)
- **Duplicates Suppressed:** 39 redundant promos (>50% temporal overlap)
- **Final Accepted Promos:** 105 ranked promos
- **Dual-Run Rank Stability:** 100% Top-10 overlap across temperature 0.2 vs 0.7
- **Estimated API Cost per Show:** **$0.014** (50 episodes on Gemini Flash); **$1.40 per 100 shows** (5,000 episodes)

---

## 🛠️ The 5 Pillars Kuku Evaluates (Your Winning Argument)

1. **Problem Choice & Framing:** Vertical microdramas convert viewers exclusively through 20–60s clips on TikTok/Reels. Solving promo discovery accelerates the studio's entire growth flywheel.
2. **AI vs. Code Split:** AI handles non-deterministic drama interpretation; deterministic Python code guarantees 100% boundary compliance, 20–60s duration, and deduplication.
3. **Quality & Real Failure Diagnostics:** Documented 3 real AI failure modes (Pronoun Ambiguity, Premature Climax Resolution, and Hallucinated Cut Points) and showed how code safeguards catch them.
4. **NLE Studio Finishing Workflow:** Automated generation of CMX 3600 EDL files and SRT subtitles so video editors can drag-and-drop cuts directly into Adobe Premiere Pro or DaVinci Resolve.
5. **Interactive Studio Experience:** Both a **Streamlit App** (`localhost:8501`) and a **React 9:16 Mobile Studio** (`localhost:3000`) with dynamic live rubric sliders, 50-episode viral heatmap, and A/B split-testing.
