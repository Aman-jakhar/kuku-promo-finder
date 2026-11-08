"""edl_exporter.py

Generates industry-standard CMX 3600 Edit Decision Lists (EDL) and SRT subtitles
for candidate promos, allowing studio editors to import cuts directly into
Adobe Premiere Pro, DaVinci Resolve, or Final Cut Pro.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Dict, Any


def seconds_to_timecode(seconds: float, fps: float = 24.0) -> str:
    """Convert float seconds to SMPTE timecode HH:MM:SS:FF."""
    total_frames = int(round(seconds * fps))
    frames = total_frames % int(fps)
    total_seconds = total_frames // int(fps)
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hrs = total_minutes // 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}:{frames:02d}"


def seconds_to_srt_time(seconds: float) -> str:
    """Convert float seconds to SRT timestamp HH:MM:SS,mmm."""
    millis = int(round((seconds - int(seconds)) * 1000))
    total_secs = int(seconds)
    secs = total_secs % 60
    total_mins = total_secs // 60
    mins = total_mins % 60
    hrs = total_mins // 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_cmx3600_edl(promo: Dict[str, Any], fps: float = 24.0) -> str:
    """Generate CMX 3600 EDL for a single promo candidate."""
    promo_id = promo.get("promo_id", "promo")
    lines = [
        f"TITLE: KUKU_PROMO_{promo_id.upper()}",
        "FCM: NON-DROP FRAME",
        ""
    ]

    record_in = 0.0
    for idx, seg in enumerate(promo.get("segments", []), 1):
        start_s = seg.get("start_s", 0.0)
        end_s = seg.get("end_s", 0.0)
        dur = end_s - start_s
        record_out = record_in + dur

        src_in_tc = seconds_to_timecode(start_s, fps)
        src_out_tc = seconds_to_timecode(end_s, fps)
        rec_in_tc = seconds_to_timecode(record_in, fps)
        rec_out_tc = seconds_to_timecode(record_out, fps)

        # CMX 3600 event line: Event# Reel Track Trans SrcIn SrcOut RecIn RecOut
        reel_name = f"EP{seg.get('episode', 1):03d}"
        lines.append(f"{idx:03d}  {reel_name:<8} V     C        {src_in_tc} {src_out_tc} {rec_in_tc} {rec_out_tc}")
        lines.append(f"* FROM CLIP: Episode {seg.get('episode', 1)} [{seg.get('start')} - {seg.get('end')}]")
        if idx == 1:
            lines.append(f"* HOOK: {promo.get('hook', '')[:70]}")
        if idx == len(promo.get("segments", [])):
            lines.append(f"* CLIFFHANGER: {promo.get('cliffhanger', '')[:70]}")
        lines.append("")

        record_in = record_out

    return "\n".join(lines)


def generate_srt(promo: Dict[str, Any]) -> str:
    """Generate an SRT subtitle track for the promo marking Hook, Body, and Cliffhanger."""
    segments = promo.get("segments", [])
    if not segments:
        return ""

    entries = []
    current_time = 0.0

    # 1. Hook entry (first 3 seconds)
    hook_end = min(3.0, promo.get("total_seconds", 3.0))
    entries.append(
        f"1\n{seconds_to_srt_time(0.0)} --> {seconds_to_srt_time(hook_end)}\n[HOOK] {promo.get('hook', '')}"
    )

    # 2. Body entry
    cliff_start = max(hook_end, promo.get("total_seconds", 25.0) - 4.0)
    if cliff_start > hook_end:
        entries.append(
            f"2\n{seconds_to_srt_time(hook_end)} --> {seconds_to_srt_time(cliff_start)}\n[PROMO BODY] {promo.get('why_it_works', '')}"
        )

    # 3. Cliffhanger entry
    entries.append(
        f"3\n{seconds_to_srt_time(cliff_start)} --> {seconds_to_srt_time(promo.get('total_seconds', 30.0))}\n[CLIFFHANGER CUT] {promo.get('cliffhanger', '')}"
    )

    return "\n\n".join(entries)


def export_edl_and_srt_for_top_promos(promos: List[Dict[str, Any]], out_dir: str = "outputs/edl") -> None:
    """Export EDL and SRT files for top candidate promos."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for p in promos[:15]:
        pid = p.get("promo_id", "promo")
        edl_text = generate_cmx3600_edl(p)
        srt_text = generate_srt(p)

        (out_path / f"{pid}.edl").write_text(edl_text, encoding="utf-8")
        (out_path / f"{pid}.srt").write_text(srt_text, encoding="utf-8")

    print(f"Exported EDL & SRT files for top {min(15, len(promos))} promos to {out_dir}/")
