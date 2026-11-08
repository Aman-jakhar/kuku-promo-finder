# Kuku AI Generalist — Interview Preparation & Live Run Guide

If you are shortlisted for the interview, you will be asked to run your solution live on an unseen show folder and swap models using API keys provided by Kuku. This guide gives you the exact commands and answers to dominate the interview.

---

## 🚀 1. Live Run on an Unseen Show Folder

When the interviewer provides a new folder containing scripts (e.g., `./new_show/`):

```bash
# 1. Run the pipeline on the new folder
python promo_finder.py --input ./new_show --out ./outputs_new

# 2. View generated deliverables
cat ./outputs_new/ranking.md

# 3. View the new results in Streamlit or React UI
streamlit run app.py
```

*Why this works effortlessly:*
- `parser.py` is **show-agnostic**: it does not hardcode show names, episode counts, or file naming conventions. It searches recursively for any `.txt` screenplay files and reads structured headers directly from the file content.

---

## 🔄 2. Model Swapping During the Interview

The interviewer may say: *"Let's test this with a stronger model like GPT-4o or Claude via an API key."*

### A. Swap via Environment Variables:
```bash
# Set the OpenAI-compatible Base URL (optional, defaults to OpenAI or Gemini)
export LLM_BASE_URL="https://api.openai.com/v1"

# Set the provided API Key
export LLM_API_KEY="sk-..."

# Set the desired Model
export LLM_MODEL="gpt-4o"  # or gpt-4o-mini, gemini-2.5-flash, claude-3-5-sonnet

# Re-run pipeline
python promo_finder.py --input ./data --out ./outputs
```

### B. Swap via `.env` file:
Create or edit `.env` in the root folder:
```env
LLM_API_KEY=your_key_here
LLM_MODEL=gpt-4o
LLM_BASE_URL=https://api.openai.com/v1
```
The client (`llm_client.py`) will automatically detect and load these keys upon execution.

---

## 🎯 3. Technical & Product Q&A Cheat Sheet

### Q1: *"Why did you separate AI and Code so strictly? Why not let the LLM do everything in one prompt?"*
> **Your Answer:**
> *"LLMs excel at semantic perception—understanding high-stakes drama, betrayal, and cliffhangers. However, LLMs are fundamentally non-deterministic and hallucinate timestamps, rounding numbers to `00:30.00` or cutting mid-syllable. By handling timestamp parsing, boundary snapping, segment length validation, and deduplication in deterministic Python code, we guarantee 100% boundary compliance without wasting tokens. Code guarantees the specs; AI supplies the creativity."*

### Q2: *"Why did you use 3 separate passes instead of 1?"*
> **Your Answer:**
> *"Each pass has a distinct epistemological state:
> - **Pass 1** sees the episode context and previous episode logline to understand narrative progression.
> - **Pass 2** sees the whole show synopsis to construct multi-episode stitched arcs.
> - **Pass 3** is deliberately blind: it sees ONLY the clip transcript with zero lore or context. This is the only way to objectively test Rule 3—whether the clip makes sense to a stranger scrolling on TikTok who has never heard of the show."*

### Q3: *"How does this scale to 100 shows a month? What are the economics?"*
> **Your Answer:**
> *"Because our condenser strips verbose camera directions before sending to the LLM, an entire 50-episode show uses only ~115k input tokens. On modern flash models like Gemini 2.5 Flash, a full 50-episode show costs less than 2 cents ($0.014). Running 100 shows (5,000 episodes) costs under $2.80 total. Furthermore, our SHA256 disk cache ensures re-runs and parameter tweaks cost $0.00."*

### Q4: *"Where does your tool fail or pick badly?"*
> **Your Answer:**
> *"We documented three concrete failure modes in `quality_report.md`:
> 1. **Pronoun Ambiguity (Episode 4):** Hook opened on 'He will never forgive you!'—great tension, but a scrolling stranger doesn't know who 'He' is. Pass 3 docked standalone score to 2.5, keeping it out of the Top 20.
> 2. **Premature Climax Resolution:** The model identified a slap but extended the window past the reconciliation beat. We enforced a cut rule immediately after the provocative line.
> 3. **Hallucinated Cuts:** Addressed by snapping start/end points to the nearest parsed event start/end."*

### Q5: *"Why did you add EDL and SRT export?"*
> **Your Answer:**
> *"In a real studio workflow, AI recommendations are useless if an editor has to manually scrub the video to find the timestamps. By exporting standard CMX 3600 EDL files, an editor can import the cut directly into Adobe Premiere Pro or DaVinci Resolve, having the timeline populated with markers instantly."*
