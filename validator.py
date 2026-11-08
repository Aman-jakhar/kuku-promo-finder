"""validator.py

Deterministic validation and boundary snapping for candidate promos.

Enforces the hard microdrama promo specifications:
1. Total duration between 20.0s and 60.0s.
2. At most 4 segments, ordered chronologically without internal overlap.
3. Every segment snaps to an exact event boundary (never cut mid-line).
   Start must land on an event start; end on an event end.
4. Hook event must begin within the first 3.0s of the promo.
5. Deduplication: suppresses overlapping candidate promos (>50% overlap),
   keeping the higher-scoring promo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from parser import Episode, Event, format_timestamp, parse_timestamp


@dataclass
class Segment:
    """A continuous clip segment from a single episode."""
    episode: int
    start_s: float
    end_s: float
    start: str = ""
    end: str = ""

    def __post_init__(self):
        if not self.start:
            self.start = format_timestamp(self.start_s)
        if not self.end:
            self.end = format_timestamp(self.end_s)

    @property
    def duration_s(self) -> float:
        return round(self.end_s - self.start_s, 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode": self.episode,
            "start": self.start,
            "end": self.end,
            "start_s": round(self.start_s, 2),
            "end_s": round(self.end_s, 2),
            "duration_s": round(self.duration_s, 2)
        }


@dataclass
class PromoScores:
    hook: float = 0.0
    cliffhanger: float = 0.0
    standalone: float = 0.0
    overall: float = 0.0

    def compute_overall(
        self,
        w_hook: float = 0.35,
        w_cliff: float = 0.35,
        w_standalone: float = 0.30
    ) -> float:
        """Calculate weighted score deterministically in code."""
        self.overall = round(
            (w_hook * self.hook) + (w_cliff * self.cliffhanger) + (w_standalone * self.standalone),
            3
        )
        return self.overall

    def to_dict(self) -> Dict[str, float]:
        return {
            "hook": round(self.hook, 2),
            "cliffhanger": round(self.cliffhanger, 2),
            "standalone": round(self.standalone, 2),
            "overall": round(self.overall, 3)
        }


@dataclass
class PromoCandidate:
    """A proposed microdrama promo."""
    promo_id: str
    segments: List[Segment]
    hook: str
    cliffhanger: str
    why_it_works: str
    standalone_note: str = ""
    total_seconds: float = 0.0
    scores: PromoScores = field(default_factory=PromoScores)
    flags: List[str] = field(default_factory=list)
    rank: Optional[int] = None

    def __post_init__(self):
        if not self.total_seconds:
            self.total_seconds = round(sum(s.duration_s for s in self.segments), 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "promo_id": self.promo_id,
            "segments": [s.to_dict() for s in self.segments],
            "total_seconds": round(self.total_seconds, 2),
            "hook": self.hook,
            "cliffhanger": self.cliffhanger,
            "why_it_works": self.why_it_works,
            "standalone_note": self.standalone_note,
            "scores": self.scores.to_dict(),
            "flags": self.flags
        }


@dataclass
class ValidationResult:
    """Outcome of validating a candidate promo."""
    is_valid: bool
    snapped_promo: PromoCandidate
    errors: List[str]
    warnings: List[str]
    pre_snap_duration: float
    post_snap_duration: float


def find_closest_boundary(target_s: float, candidates: List[float]) -> Tuple[float, float]:
    """Find the closest legal timestamp in candidates and the absolute distance."""
    if not candidates:
        return target_s, 0.0
    closest = min(candidates, key=lambda c: abs(c - target_s))
    delta = abs(closest - target_s)
    return closest, delta


def snap_and_validate(
    candidate: PromoCandidate,
    episodes: Dict[int, Episode],
    snap: bool = True,
    snap_tolerance_s: float = 3.0
) -> ValidationResult:
    """Snap timestamps to legal event boundaries and validate against hard specs.
    
    Hard specs:
    - 20.0s <= total_seconds <= 60.0s
    - 1 <= len(segments) <= 4
    - Timestamps within episode bounds
    - Segments chronological & non-overlapping
    - Hook event must begin within 3.0s of promo start
    """
    errors: List[str] = []
    warnings: List[str] = []

    pre_snap_duration = sum(s.duration_s for s in candidate.segments)
    snapped_segments: List[Segment] = []

    # 1. Segment Count
    if not candidate.segments:
        errors.append("NO_SEGMENTS: Candidate contains no segments.")
        return ValidationResult(False, candidate, errors, warnings, pre_snap_duration, pre_snap_duration)

    if len(candidate.segments) > 4:
        errors.append(f"TOO_MANY_SEGMENTS: Contains {len(candidate.segments)} segments (max allowed is 4).")

    # 2. Episode existence and boundary snapping
    for idx, seg in enumerate(candidate.segments):
        if seg.episode not in episodes:
            errors.append(f"UNKNOWN_EPISODE: Episode {seg.episode} not found in parsed data.")
            continue

        ep = episodes[seg.episode]
        start_s = seg.start_s
        end_s = seg.end_s

        if snap:
            legal_starts = ep.get_legal_start_boundaries()
            legal_ends = ep.get_legal_end_boundaries()

            snapped_start, start_delta = find_closest_boundary(start_s, legal_starts)
            snapped_end, end_delta = find_closest_boundary(end_s, legal_ends)

            if start_delta > 0.05:
                warnings.append(f"SNAP_START: Seg {idx+1} snapped {start_s:.2f}s -> {snapped_start:.2f}s (delta={start_delta:.2f}s)")
            if end_delta > 0.05:
                warnings.append(f"SNAP_END: Seg {idx+1} snapped {end_s:.2f}s -> {snapped_end:.2f}s (delta={end_delta:.2f}s)")

            if start_delta > snap_tolerance_s or end_delta > snap_tolerance_s:
                warnings.append(f"LARGE_SNAP_DELTA: Seg {idx+1} snap delta exceeded tolerance {snap_tolerance_s}s.")

            start_s = snapped_start
            end_s = snapped_end

        # Check bounds within episode
        if start_s < 0.0:
            errors.append(f"TIMESTAMP_OUTSIDE_EPISODE: Seg {idx+1} start ({start_s:.2f}s) is negative.")
        if end_s > ep.duration_s + 1.0:
            errors.append(
                f"TIMESTAMP_OUTSIDE_EPISODE: Seg {idx+1} end ({end_s:.2f}s) exceeds episode duration ({ep.duration_s:.2f}s)."
            )

        if start_s >= end_s:
            errors.append(f"INVALID_SEGMENT_BOUNDS: Seg {idx+1} start ({start_s:.2f}s) >= end ({end_s:.2f}s).")

        snapped_segments.append(Segment(
            episode=seg.episode,
            start_s=start_s,
            end_s=end_s
        ))

    # 3. Chronological Order & Non-overlap
    for i in range(len(snapped_segments) - 1):
        curr = snapped_segments[i]
        nxt = snapped_segments[i + 1]

        if curr.episode > nxt.episode:
            errors.append(f"OUT_OF_ORDER_EPISODES: Segment {i+1} (Ep {curr.episode}) is after Segment {i+2} (Ep {nxt.episode}).")
        elif curr.episode == nxt.episode:
            if curr.end_s > nxt.start_s:
                errors.append(
                    f"SEGMENTS_OVERLAP: Segment {i+1} ends at {curr.end_s:.2f}s but Segment {i+2} starts earlier at {nxt.start_s:.2f}s."
                )

    # 4. Total Duration
    post_snap_duration = round(sum(s.duration_s for s in snapped_segments), 3)
    if post_snap_duration < 20.0:
        errors.append(f"DURATION_TOO_SHORT: Total duration {post_snap_duration:.2f}s < 20.0s.")
    elif post_snap_duration > 60.0:
        errors.append(f"DURATION_TOO_LONG: Total duration {post_snap_duration:.2f}s > 60.0s.")

    # 5. Hook Timing Check
    # "Opens on a HOOK in the first 3 seconds (slap, reveal, shocking line)"
    # The first event of segment 1 must begin within 3.0s of promo start.
    if snapped_segments and snapped_segments[0].episode in episodes:
        first_seg = snapped_segments[0]
        first_ep = episodes[first_seg.episode]
        # Events overlapping the initial 3 seconds window [start, start + 3.0]
        window_end = first_seg.start_s + 3.0
        opening_events = [
            e for e in first_ep.events
            if e.start_s >= first_seg.start_s and e.start_s <= window_end
            and e.kind in ("DIALOGUE", "ACTION", "SOUND FX")
        ]

        if not opening_events:
            # Check if an ongoing dialogue/action started just before or spans across
            spanning_events = [
                e for e in first_ep.events
                if e.start_s <= first_seg.start_s and e.end_s > first_seg.start_s
                and e.kind in ("DIALOGUE", "ACTION")
            ]
            if not spanning_events:
                errors.append(
                    f"HOOK_TIMING_INVALID: No dialogue or action event begins within the first 3.0s (window: {first_seg.start_s:.2f}s - {window_end:.2f}s)."
                )

    is_valid = (len(errors) == 0)

    # Build updated promo candidate
    all_flags = list(candidate.flags) + warnings
    if errors:
        all_flags.extend([f"ERR: {e}" for e in errors])

    snapped_promo = PromoCandidate(
        promo_id=candidate.promo_id,
        segments=snapped_segments,
        hook=candidate.hook,
        cliffhanger=candidate.cliffhanger,
        why_it_works=candidate.why_it_works,
        standalone_note=candidate.standalone_note,
        total_seconds=post_snap_duration,
        scores=candidate.scores,
        flags=all_flags,
        rank=candidate.rank
    )

    return ValidationResult(
        is_valid=is_valid,
        snapped_promo=snapped_promo,
        errors=errors,
        warnings=warnings,
        pre_snap_duration=pre_snap_duration,
        post_snap_duration=post_snap_duration
    )


def compute_segment_overlap(seg_a: Segment, seg_b: Segment) -> float:
    """Calculate overlap duration in seconds between two segments."""
    if seg_a.episode != seg_b.episode:
        return 0.0
    start = max(seg_a.start_s, seg_b.start_s)
    end = min(seg_a.end_s, seg_b.end_s)
    return max(0.0, end - start)


def compute_promo_overlap_ratio(promo_a: PromoCandidate, promo_b: PromoCandidate) -> float:
    """Compute maximum fraction of overlap between two candidate promos."""
    total_overlap = 0.0
    for sa in promo_a.segments:
        for sb in promo_b.segments:
            total_overlap += compute_segment_overlap(sa, sb)

    dur_a = max(promo_a.total_seconds, 0.001)
    dur_b = max(promo_b.total_seconds, 0.001)
    # Ratio relative to smaller promo
    return total_overlap / min(dur_a, dur_b)


def deduplicate_promos(
    candidates: List[PromoCandidate],
    overlap_threshold: float = 0.50
) -> Tuple[List[PromoCandidate], List[PromoCandidate]]:
    """Deduplicate candidate promos.
    
    If two promos overlap by >= overlap_threshold, keep the higher-scoring promo.
    Returns (accepted_promos, dropped_promos).
    """
    # Sort candidates by overall score descending
    sorted_candidates = sorted(
        candidates,
        key=lambda c: (c.scores.overall, c.total_seconds),
        reverse=True
    )

    accepted: List[PromoCandidate] = []
    dropped: List[PromoCandidate] = []

    for cand in sorted_candidates:
        is_dup = False
        for acc in accepted:
            overlap = compute_promo_overlap_ratio(cand, acc)
            if overlap >= overlap_threshold:
                is_dup = True
                cand.flags.append(f"DUPLICATE_OF_{acc.promo_id}_OVERLAP_{overlap*100:.0f}%")
                dropped.append(cand)
                break
        if not is_dup:
            accepted.append(cand)

    return accepted, dropped
