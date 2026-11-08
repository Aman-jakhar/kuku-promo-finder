# 3-Minute Walkthrough Video Script (Loom / Screen Recording)

Use this word-for-word script to record your 3-minute screen recording. The assignment brief highlights that a short video walkthrough is the quickest way for Kuku evaluators to see your thinking in action.

---

### Timing & Cue Breakdown

| Timestamp | Visual on Screen | Spoken Script (Word-for-Word) |
| :---: | :--- | :--- |
| **0:00 – 0:30** | Show Terminal & run `python promo_finder.py --input ./data --out ./outputs` | *"Hi Kuku team! Today I’m walking you through my solution for Problem 1: Automated Promo Finder. In microdrama, trailers don’t sell shows—20 to 60-second vertical clips with immediate emotional whiplash do. Our goal is to replace manual editor screening with a rerunnable, model-swappable pipeline that outputs exact, production-ready cut timestamps."* |
| **0:30 – 1:05** | Switch to the terminal showing the 3 passes and validator stats | *"Here’s our architecture split. We keep strict boundaries: AI handles semantic drama interpretation, but code deterministically guarantees technical specs. In Pass 1, the LLM analyzes condensed screenplays with previous-episode context to find high-stakes moments. In Pass 2, it stitches cross-episode arcs. In Pass 3, a fresh, blind LLM acts as a first-time viewer seeing only the clip transcript to evaluate standalone clarity."* |
| **1:05 – 1:40** | Show [quality_report.md](file:///c:/Users/jakha/Downloads/KUKU/quality_report.md) or terminal snapping stats | *"Notice our deterministic validator. Raw LLMs hallucinate rounded timestamps that cut actors off mid-syllable. Our parser maps all 3,727 events to float seconds and automatically snaps cuts to spoken dialogue boundaries with 100% precision. It also enforces the hard 3-second hook rule, drops 39 duplicate clips, and ranks candidates using a transparent formula: 35% hook, 35% cliffhanger, and 30% standalone legibility."* |
| **1:40 – 2:25** | Open the React Dashboard at `http://localhost:3000` (or Streamlit at `http://localhost:8501`) | *"Now let’s look at the studio dashboard. Here are our 105 ranked promos. Notice our live Rubric Tuner: if our marketing team wants to prioritize cliffhanger virality over standalone clarity for a revenge drama, we simply drag the slider and the catalog instantly re-ranks in real time! Opening our 9:16 Mobile Studio, editors can preview simulated vertical captions, verify the 0–3 second Hook Zone in red, and inspect the cliffhanger cut point."* |
| **2:25 – 2:50** | Click the 'EDL / Premiere Export' tab in the React app | *"Crucially, this is built for real production finishing. With one click, editors can export industry-standard CMX 3600 EDL files and SRT subtitles directly into Adobe Premiere Pro or DaVinci Resolve, saving hours of manual timeline cutting."* |
| **2:50 – 3:00** | Show [solution_doc.pdf](file:///c:/Users/jakha/Downloads/KUKU/solution_doc.pdf) | *"At scale, caching keeps re-runs free, and full 50-episode runs cost under 2 cents on Gemini Flash. The code is modular, fully unit-tested, and ready to run on any new show in your interview. Thank you!"* |

---

### Tips for Recording
1. **Resolution:** Record in 1080p using Loom or OBS.
2. **Pacing:** Speak clearly and with energy; do not rush.
3. **Tab Layout:** Have terminal on the left, browser with `http://localhost:3000` on the right.
