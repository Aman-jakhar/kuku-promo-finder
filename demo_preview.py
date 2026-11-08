"""demo_preview.py

Demonstration script showing:
1. Parsed output of Episode 1 (Scene 01 duration, events, condensed representation).
2. The validator running on a hand-written fake candidate (valid promo).
3. The validator rejecting invalid candidates (duration <20s, duration >60s, out-of-order, snapping).
"""

from pathlib import Path
from parser import parse_episode_file, condense_episode, format_timestamp
from validator import Segment, PromoCandidate, PromoScores, snap_and_validate


def main():
    print("=" * 80)
    print("1. PARSING EPISODE 1")
    print("=" * 80)

    ep_path = Path("data/episode-001-Episode 1671703.txt")
    if not ep_path.exists():
        ep_path = list(Path("data").glob("episode-001*.txt"))[0]

    ep1 = parse_episode_file(ep_path)

    print(f"Episode Number:     {ep1.ep_num}")
    print(f"Logline:            {ep1.logline}")
    print(f"Continuity Notes:   {ep1.continuity_notes}")
    print(f"Total Scenes:       {len(ep1.scenes)}")
    for s in ep1.scenes:
        print(f"  -> {s.scene_id}: '{s.heading}' | Start: {format_timestamp(s.start_s)} ({s.start_s:.2f}s) -> End: {format_timestamp(s.end_s)} ({s.end_s:.2f}s) | Duration: {s.end_s - s.start_s:.2f}s")
    print(f"Total Events:       {len(ep1.events)}")

    # Breakdown by event kind
    kinds = {}
    for e in ep1.events:
        kinds[e.kind] = kinds.get(e.kind, 0) + 1
    print(f"Event Breakdown:    {kinds}")

    print("\nFirst 4 events:")
    for e in ep1.events[:4]:
        spk_emo = f" {e.speaker}" if e.speaker else ""
        if e.emotion:
            spk_emo += f" ({e.emotion})"
        print(f"  [{format_timestamp(e.start_s)} - {format_timestamp(e.end_s)}] {e.kind}{spk_emo}: {e.text[:70]}...")

    print("\nCondensed LLM Context (first 10 lines):")
    condensed_lines = condense_episode(ep1, include_camera=False).split("\n")
    for line in condensed_lines[:10]:
        print(f"  {line}")
    print(f"  ... [Total condensed lines: {len(condensed_lines)}]")

    print("\n" + "=" * 80)
    print("2. VALIDATOR ON HAND-WRITTEN CANDIDATES")
    print("=" * 80)

    episodes = {1: ep1}

    # Case A: Valid Hand-Written Candidate (Cathedral Altar Betrayal: 25.5s)
    # 00:11.30: Matriarch stops Juliana: "You should turn around, Juliana."
    # 00:36.80: Gerald turns around and delivers cold rejection.
    valid_candidate = PromoCandidate(
        promo_id="promo_ep1_altar_betrayal",
        segments=[
            Segment(episode=1, start_s=11.30, end_s=36.80)
        ],
        hook='MATRIARCH: "You should turn around, Juliana."',
        cliffhanger='GERALD: "She is your sister, but she is my true bride now."',
        why_it_works="Opens on instant conflict stopping the bride in the aisle; builds to a shocking betrayal at the altar with zero prior context required.",
        standalone_note="Universal archetype: bride walking to the altar gets dumped for her sister in front of everyone.",
        scores=PromoScores(hook=4.8, cliffhanger=4.9, standalone=4.7)
    )
    valid_candidate.scores.compute_overall()

    print("\n--- CASE A: VALID CANDIDATE ---")
    res_valid = snap_and_validate(valid_candidate, episodes, snap=True)
    print(f"Promo ID:           {valid_candidate.promo_id}")
    print(f"Is Valid:           {res_valid.is_valid}")
    print(f"Segments:           {res_valid.snapped_promo.segments[0].start} -> {res_valid.snapped_promo.segments[0].end} ({res_valid.post_snap_duration:.2f}s)")
    print(f"Hook:               {valid_candidate.hook}")
    print(f"Cliffhanger:        {valid_candidate.cliffhanger}")
    print(f"Scores:             Hook={valid_candidate.scores.hook}, Cliffhanger={valid_candidate.scores.cliffhanger}, Standalone={valid_candidate.scores.standalone} => Overall={valid_candidate.scores.overall}")
    print(f"Errors:             {res_valid.errors}")
    print(f"Warnings/Flags:     {res_valid.warnings}")

    # Case B: Candidate Needing Boundary Snapping (un-snapped start 11.45, end 36.65)
    print("\n--- CASE B: BOUNDARY SNAPPING DEMO ---")
    snap_candidate = PromoCandidate(
        promo_id="promo_ep1_needs_snapping",
        segments=[
            Segment(episode=1, start_s=11.45, end_s=36.65)  # slightly off actual event timestamps
        ],
        hook='MATRIARCH: "You should turn around, Juliana."',
        cliffhanger='GERALD betrayal line',
        why_it_works="Tests automated boundary alignment."
    )
    res_snap = snap_and_validate(snap_candidate, episodes, snap=True)
    print(f"Original Times:     {snap_candidate.segments[0].start_s:.2f}s -> {snap_candidate.segments[0].end_s:.2f}s (Dur: {res_snap.pre_snap_duration:.2f}s)")
    print(f"Snapped Times:      {res_snap.snapped_promo.segments[0].start_s:.2f}s -> {res_snap.snapped_promo.segments[0].end_s:.2f}s (Dur: {res_snap.post_snap_duration:.2f}s)")
    print(f"Is Valid:           {res_snap.is_valid}")
    print(f"Snap Warnings:      {res_snap.warnings}")

    # Case C: Candidate Rejected (Duration Too Short: 13.7s)
    print("\n--- CASE C: REJECTED (DURATION < 20s) ---")
    short_candidate = PromoCandidate(
        promo_id="promo_ep1_too_short",
        segments=[
            Segment(episode=1, start_s=11.30, end_s=25.00)  # 13.70s
        ],
        hook='MATRIARCH: "You should turn around, Juliana."',
        cliffhanger="Juliana confused.",
        why_it_works="Too short test."
    )
    res_short = snap_and_validate(short_candidate, episodes, snap=True)
    print(f"Duration:           {res_short.post_snap_duration:.2f}s")
    print(f"Is Valid:           {res_short.is_valid}")
    print(f"Errors Caught:      {res_short.errors}")

    # Case D: Candidate Rejected (Duration Too Long: 65.5s)
    print("\n--- CASE D: REJECTED (DURATION > 60s) ---")
    long_candidate = PromoCandidate(
        promo_id="promo_ep1_too_long",
        segments=[
            Segment(episode=1, start_s=11.30, end_s=76.80)  # 65.50s
        ],
        hook='MATRIARCH: "You should turn around, Juliana."',
        cliffhanger="Gerald dismissive.",
        why_it_works="Too long test."
    )
    res_long = snap_and_validate(long_candidate, episodes, snap=True)
    print(f"Duration:           {res_long.post_snap_duration:.2f}s")
    print(f"Is Valid:           {res_long.is_valid}")
    print(f"Errors Caught:      {res_long.errors}")


if __name__ == "__main__":
    main()
