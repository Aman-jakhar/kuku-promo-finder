# Assumptions Log

Documenting all design decisions and sensible assumptions made during implementation.

## 1. Input & Parsing
- Scripts are organized with headers (`EPISODE NUMBER`, `EPISODE LOGLINE`, `CONTINUITY NOTES`, `--- SCRIPT START ---`, `--- SCRIPT END ---`).
- Filenames may vary across shows, so parsing is content-driven and folder-agnostic (does not rely on a hardcoded show title or rigid filename pattern, but accepts any `.txt` scripts in the target directory).
- Timestamp format is `MM:SS.ss` (or `MM:SS`) and converted to float seconds from episode start `0.0`.
- Event boundaries: `LABEL (optional emotion):` followed by `Start: (MM:SS.ss) | End: (MM:SS.ss)` and content text.
- Legal cut points: Start must snap to an event start; end must snap to an event end. `CAMERA` lines are dropped from compact LLM context to save tokens, but their start/end timestamps are retained in the event boundary index as legal cut points.

## 2. Snapping & Validation
- Snapping threshold: LLM-proposed timestamps are snapped to the closest parsed event start/end boundary within a ±2.5s tolerance window. If snapping results in <20s or >60s total duration, the candidate is flagged or rejected.
- Hook window: The hook event must begin within the first 3.0 seconds of the promo start.
- Max segments: Up to 4 segments per promo.
- Segment ordering: Segments must be strictly chronological within an episode, or ordered across episodes. No internal overlaps.
- De-duplication: Promos overlapping by more than 50% in time are deduplicated, keeping the higher-scoring promo.

## 3. Scoring & Ranking
- Deterministic formula: `Overall Score = 0.35 * hook + 0.35 * cliffhanger + 0.30 * standalone`.
- Hook score (1-5): punchiness and shock value within first 3s.
- Cliffhanger score (1-5): unresolved dramatic tension at cutoff.
- Standalone score (1-5): evaluated by Pass 3 (judge LLM) seeing only clip text without context.
