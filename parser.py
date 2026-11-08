"""parser.py

Deterministic parser for microdrama screenplays.
Extracts episode metadata, scenes, and event blocks into structured objects
with timestamps converted to float seconds from episode start (00:00.00 = 0.0s).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


def parse_timestamp(ts: str) -> float:
    """Convert timestamp 'MM:SS.ss' or 'HH:MM:SS.ss' to float seconds.
    
    Examples:
        '00:00.00' -> 0.0
        '02:18.00' -> 138.0
        '01:14.50' -> 74.5
    """
    ts = ts.strip().strip("()")
    parts = ts.split(":")
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = float(parts[1])
        return round(minutes * 60.0 + seconds, 3)
    elif len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return round(hours * 3600.0 + minutes * 60.0 + seconds, 3)
    else:
        return round(float(ts), 3)


def format_timestamp(seconds: float) -> str:
    """Convert float seconds to 'MM:SS.ss' format."""
    if seconds < 0:
        seconds = 0.0
    minutes = int(seconds // 60)
    rem_seconds = seconds - (minutes * 60)
    return f"{minutes:02d}:{rem_seconds:05.2f}"


@dataclass
class Event:
    """A single atomic beat/event in a microdrama screenplay."""
    ep: int
    scene: str
    kind: str  # 'DIALOGUE', 'ACTION', 'SOUND FX', 'CAMERA'
    speaker: Optional[str]
    emotion: Optional[str]
    start_s: float
    end_s: float
    text: str

    @property
    def duration_s(self) -> float:
        return round(self.end_s - self.start_s, 3)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Scene:
    """A scene in a microdrama episode."""
    scene_id: str
    heading: str
    start_s: float
    end_s: float
    events: List[Event]


@dataclass
class Episode:
    """A fully parsed microdrama episode."""
    ep_num: int
    raw_title: str
    logline: str
    continuity_notes: str
    scenes: List[Scene]
    events: List[Event]
    duration_s: float
    file_path: str

    def get_legal_start_boundaries(self) -> List[float]:
        """All valid cut start boundaries (starts of all events including camera)."""
        return sorted(list({e.start_s for e in self.events}))

    def get_legal_end_boundaries(self) -> List[float]:
        """All valid cut end boundaries (ends of all events including camera)."""
        return sorted(list({e.end_s for e in self.events}))

    def get_events_in_range(self, start_s: float, end_s: float) -> List[Event]:
        """Return all events overlapping [start_s, end_s]."""
        return [
            e for e in self.events
            if e.end_s > start_s and e.start_s < end_s
        ]


def parse_label(raw_label: str) -> Tuple[str, Optional[str], Optional[str]]:
    """Parse a label string into (kind, speaker, emotion).
    
    Examples:
        'CAMERA:' -> ('CAMERA', None, None)
        'ACTION:' -> ('ACTION', None, None)
        'SOUND FX:' -> ('SOUND FX', None, None)
        'MATRIARCH (Cold, Commanding):' -> ('DIALOGUE', 'MATRIARCH', 'Cold, Commanding')
        'LADY JULIANA (Confused):' -> ('DIALOGUE', 'LADY JULIANA', 'Confused')
        'ALEXANDER:' -> ('DIALOGUE', 'ALEXANDER', None)
    """
    cleaned = raw_label.strip().rstrip(":")
    upper = cleaned.upper()

    if upper.startswith("CAMERA"):
        return "CAMERA", None, None
    elif upper.startswith("ACTION"):
        return "ACTION", None, None
    elif upper.startswith("SOUND FX") or upper.startswith("SOUND"):
        return "SOUND FX", None, None

    # Dialogue speaker with optional emotion
    if "(" in cleaned and cleaned.endswith(")"):
        idx = cleaned.find("(")
        speaker = cleaned[:idx].strip()
        emotion = cleaned[idx + 1:-1].strip()
        return "DIALOGUE", speaker, emotion
    elif "(" in cleaned:
        # Fallback if malformed trailing parenthesis
        parts = cleaned.split("(", 1)
        speaker = parts[0].strip()
        emotion = parts[1].rstrip(")").strip()
        return "DIALOGUE", speaker, emotion
    else:
        return "DIALOGUE", cleaned.strip(), None


# Regex patterns for screenplay parsing
RE_EP_NUM = re.compile(r"EPISODE\s+NUMBER:\s*(?:Episode\s*)?(\d+)", re.IGNORECASE)
RE_LOGLINE = re.compile(r"EPISODE\s+LOGLINE:\s*(.+?)(?=\nCONTINUITY\s+NOTES:|\n---|\Z)", re.DOTALL | re.IGNORECASE)
RE_CONTINUITY = re.compile(r"CONTINUITY\s+NOTES:\s*(.+?)(?=\n--- SCRIPT START ---|\Z)", re.DOTALL | re.IGNORECASE)

RE_SCENE_HEADER = re.compile(
    r"(SCENE\s+\d+)\s*\n"
    r"Scene heading:\s*(.+?)\n"
    r"Scene start:\s*([0-9:.]+)\n"
    r"Scene end:\s*([0-9:.]+)",
    re.IGNORECASE
)

RE_EVENT_BLOCK = re.compile(
    r"\*\*([^*]+)\*\*\s*\n"
    r"Start:\s*\(([0-9:.]+)\)\s*\|\s*End:\s*\(([0-9:.]+)\)\s*\n"
    r"(.*?)(?=(?:\n\*\*[^*]+\*\*\s*\nStart:|\nSCENE\s+\d+|\n--- SCRIPT END ---|\Z))",
    re.DOTALL
)


def parse_episode_file(file_path: str | Path) -> Episode:
    """Parse a single episode file into an Episode object.
    
    Works independently of filename formatting by reading headers from text content.
    """
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")

    # 1. Parse Header
    ep_num_match = RE_EP_NUM.search(text)
    if ep_num_match:
        ep_num = int(ep_num_match.group(1))
    else:
        # Fallback to extracting digits from filename
        num_m = re.search(r"\d+", file_path.stem)
        ep_num = int(num_m.group(0)) if num_m else 0

    logline_match = RE_LOGLINE.search(text)
    logline = logline_match.group(1).strip() if logline_match else ""

    continuity_match = RE_CONTINUITY.search(text)
    continuity_notes = continuity_match.group(1).strip() if continuity_match else ""

    # 2. Extract Script Body
    script_start_idx = text.find("--- SCRIPT START ---")
    script_end_idx = text.find("--- SCRIPT END ---")
    if script_start_idx != -1 and script_end_idx != -1:
        script_body = text[script_start_idx + len("--- SCRIPT START ---"):script_end_idx]
    elif script_start_idx != -1:
        script_body = text[script_start_idx + len("--- SCRIPT START ---"):]
    else:
        script_body = text

    # 3. Locate Scenes
    scene_matches = list(RE_SCENE_HEADER.finditer(script_body))
    scene_ranges = []
    for i, sm in enumerate(scene_matches):
        s_id = sm.group(1).strip()
        s_heading = sm.group(2).strip()
        s_start = parse_timestamp(sm.group(3))
        s_end = parse_timestamp(sm.group(4))
        content_start = sm.end()
        content_end = scene_matches[i + 1].start() if i + 1 < len(scene_matches) else len(script_body)
        scene_ranges.append({
            "id": s_id,
            "heading": s_heading,
            "start_s": s_start,
            "end_s": s_end,
            "content": script_body[content_start:content_end]
        })

    # If no explicit scene header found, treat whole script body as single scene
    if not scene_ranges:
        scene_ranges.append({
            "id": "SCENE 01",
            "heading": "UNKNOWN",
            "start_s": 0.0,
            "end_s": 0.0,
            "content": script_body
        })

    all_events: List[Event] = []
    scenes: List[Scene] = []

    for sr in scene_ranges:
        scene_events: List[Event] = []
        for em in RE_EVENT_BLOCK.finditer(sr["content"]):
            raw_label = em.group(1).strip()
            start_str = em.group(2).strip()
            end_str = em.group(3).strip()
            content_text = em.group(4).strip()

            kind, speaker, emotion = parse_label(raw_label)
            start_s = parse_timestamp(start_str)
            end_s = parse_timestamp(end_str)

            event = Event(
                ep=ep_num,
                scene=sr["id"],
                kind=kind,
                speaker=speaker,
                emotion=emotion,
                start_s=start_s,
                end_s=end_s,
                text=content_text
            )
            scene_events.append(event)
            all_events.append(event)

        # Fallback for scene end if not set
        if sr["end_s"] == 0.0 and scene_events:
            sr["end_s"] = max(e.end_s for e in scene_events)

        scenes.append(Scene(
            scene_id=sr["id"],
            heading=sr["heading"],
            start_s=sr["start_s"],
            end_s=sr["end_s"],
            events=scene_events
        ))

    # Calculate total episode duration
    if scenes:
        duration_s = max(s.end_s for s in scenes)
    elif all_events:
        duration_s = max(e.end_s for e in all_events)
    else:
        duration_s = 0.0

    return Episode(
        ep_num=ep_num,
        raw_title=file_path.stem,
        logline=logline,
        continuity_notes=continuity_notes,
        scenes=scenes,
        events=all_events,
        duration_s=duration_s,
        file_path=str(file_path)
    )


def parse_all_episodes(dir_path: str | Path) -> Dict[int, Episode]:
    """Parse all episode .txt files in a directory, returning a dict keyed by episode number."""
    dir_path = Path(dir_path)
    txt_files = list(dir_path.glob("*.txt"))
    if not txt_files:
        # Check subdirectories
        txt_files = list(dir_path.glob("**/*.txt"))

    episodes: Dict[int, Episode] = {}
    for f in sorted(txt_files):
        ep = parse_episode_file(f)
        episodes[ep.ep_num] = ep
    return episodes


def condense_episode(
    episode: Episode,
    include_camera: bool = False,
    include_headers: bool = True
) -> str:
    """Render each episode as compact lines for LLM context.
    
    Format:
    [mm:ss.s–mm:ss.s] SPEAKER (emotion): text
    [mm:ss.s–mm:ss.s] ACTION: text
    [mm:ss.s–mm:ss.s] SOUND FX: text
    
    Drops CAMERA lines by default (to save tokens) while their timestamps
    remain indexed as legal cut points.
    """
    lines = []
    if include_headers:
        lines.append(f"EPISODE {episode.ep_num} LOGLINE: {episode.logline}")
        if episode.continuity_notes:
            lines.append(f"CONTINUITY: {episode.continuity_notes}")
        lines.append("--- SCRIPT TIMELINE ---")

    for e in episode.events:
        if e.kind == "CAMERA" and not include_camera:
            continue

        start_str = format_timestamp(e.start_s)
        end_str = format_timestamp(e.end_s)
        time_tag = f"[{start_str} - {end_str}]"

        if e.kind == "DIALOGUE":
            speaker_str = e.speaker or "SPEAKER"
            if e.emotion:
                header = f"{speaker_str} ({e.emotion})"
            else:
                header = speaker_str
            # Clean outer quotes if any
            clean_text = e.text.strip()
            lines.append(f"{time_tag} {header}: {clean_text}")
        elif e.kind == "ACTION":
            lines.append(f"{time_tag} ACTION: {e.text.strip()}")
        elif e.kind == "SOUND FX":
            lines.append(f"{time_tag} SOUND FX: {e.text.strip()}")
        elif e.kind == "CAMERA" and include_camera:
            lines.append(f"{time_tag} CAMERA: {e.text.strip()}")

    return "\n".join(lines)
