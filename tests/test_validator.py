"""tests/test_validator.py

Unit tests for validator.py, verifying hard spec checks, boundary snapping,
and candidate deduplication.
"""

import unittest
from pathlib import Path

from parser import parse_episode_file
from validator import (
    Segment,
    PromoCandidate,
    PromoScores,
    snap_and_validate,
    deduplicate_promos
)


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path("data")
        ep1_files = list(self.data_dir.glob("episode-001*.txt"))
        if not ep1_files:
            self.skipTest("Episode 1 script not found in ./data/")
        self.ep1 = parse_episode_file(ep1_files[0])
        self.episodes = {1: self.ep1}

    def test_valid_hand_written_candidate(self):
        """A valid 25.5s promo from Episode 1 (11.30s to 36.80s)."""
        # 11.30s: MATRIARCH: "You should turn around, Juliana."
        # 36.80s: Ends on dramatic confrontation
        candidate = PromoCandidate(
            promo_id="promo_ep1_valid",
            segments=[
                Segment(episode=1, start_s=11.30, end_s=36.80)
            ],
            hook='MATRIARCH: "You should turn around, Juliana."',
            cliffhanger='GERALD: "She is your sister, but she is my true bride now."',
            why_it_works="Immediate emotional gut-punch in the cathedral with shocking betrayal at the altar.",
            standalone_note="Clear bride-groom betrayal instantly legible to any viewer.",
            scores=PromoScores(hook=4.8, cliffhanger=4.7, standalone=4.5)
        )
        candidate.scores.compute_overall()

        res = snap_and_validate(candidate, self.episodes, snap=True)
        self.assertTrue(res.is_valid, f"Validation failed with errors: {res.errors}")
        self.assertGreaterEqual(res.post_snap_duration, 20.0)
        self.assertLessEqual(res.post_snap_duration, 60.0)
        self.assertEqual(len(res.errors), 0)

    def test_reject_duration_too_short(self):
        """Total duration < 20.0s must be rejected."""
        candidate = PromoCandidate(
            promo_id="promo_too_short",
            segments=[
                Segment(episode=1, start_s=11.30, end_s=25.00)  # 13.7s
            ],
            hook='MATRIARCH: "You should turn around, Juliana."',
            cliffhanger="Juliana in shock.",
            why_it_works="Too short test."
        )
        res = snap_and_validate(candidate, self.episodes, snap=True)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("DURATION_TOO_SHORT" in err for err in res.errors))

    def test_reject_duration_too_long(self):
        """Total duration > 60.0s must be rejected."""
        candidate = PromoCandidate(
            promo_id="promo_too_long",
            segments=[
                Segment(episode=1, start_s=11.30, end_s=85.00)  # 73.7s
            ],
            hook='MATRIARCH: "You should turn around, Juliana."',
            cliffhanger="Distant confrontation.",
            why_it_works="Too long test."
        )
        res = snap_and_validate(candidate, self.episodes, snap=True)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("DURATION_TOO_LONG" in err for err in res.errors))

    def test_reject_too_many_segments(self):
        """More than 4 segments must be rejected."""
        candidate = PromoCandidate(
            promo_id="promo_5_segments",
            segments=[
                Segment(episode=1, start_s=11.30, end_s=16.00),
                Segment(episode=1, start_s=18.00, end_s=23.00),
                Segment(episode=1, start_s=25.00, end_s=30.00),
                Segment(episode=1, start_s=32.00, end_s=37.00),
                Segment(episode=1, start_s=40.00, end_s=46.00),
            ],
            hook="Hook line",
            cliffhanger="Ending",
            why_it_works="Fragmented promo."
        )
        res = snap_and_validate(candidate, self.episodes, snap=True)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("TOO_MANY_SEGMENTS" in err for err in res.errors))

    def test_reject_overlapping_segments(self):
        """Segments within same episode that overlap must be rejected."""
        candidate = PromoCandidate(
            promo_id="promo_overlap",
            segments=[
                Segment(episode=1, start_s=11.30, end_s=30.00),
                Segment(episode=1, start_s=25.00, end_s=45.00),  # starts before seg 1 ends
            ],
            hook="Hook line",
            cliffhanger="Ending",
            why_it_works="Overlapping segments."
        )
        res = snap_and_validate(candidate, self.episodes, snap=True)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("SEGMENTS_OVERLAP" in err for err in res.errors))

    def test_snapping_to_nearest_event_boundary(self):
        """Proposed timestamps slightly off-boundary should snap cleanly."""
        # Exact start in Ep 1 is 11.30 (Matriarch dialogue)
        # Exact end is 36.80
        candidate = PromoCandidate(
            promo_id="promo_needs_snap",
            segments=[
                Segment(episode=1, start_s=11.50, end_s=36.50)  # slightly off
            ],
            hook="Hook",
            cliffhanger="Cliffhanger",
            why_it_works="Test boundary snapping."
        )
        res = snap_and_validate(candidate, self.episodes, snap=True)
        snapped_seg = res.snapped_promo.segments[0]
        # Snapped start should land exactly on 11.30s
        self.assertAlmostEqual(snapped_seg.start_s, 11.30, places=2)
        # Snapped end should land on nearest event end
        self.assertIn(snapped_seg.end_s, self.ep1.get_legal_end_boundaries())

    def test_deduplication_keeps_higher_scoring(self):
        """Two overlapping promos: higher scoring must be accepted, other dropped."""
        promo_a = PromoCandidate(
            promo_id="promo_A_high_score",
            segments=[Segment(episode=1, start_s=11.30, end_s=36.80)],
            hook="Hook A", cliffhanger="Cliff A", why_it_works="Why A",
            scores=PromoScores(hook=4.8, cliffhanger=4.8, standalone=4.5)
        )
        promo_a.scores.compute_overall()  # ~4.71

        promo_b = PromoCandidate(
            promo_id="promo_B_lower_score",
            segments=[Segment(episode=1, start_s=13.50, end_s=38.00)],  # heavily overlaps promo A
            hook="Hook B", cliffhanger="Cliff B", why_it_works="Why B",
            scores=PromoScores(hook=3.0, cliffhanger=3.0, standalone=3.0)
        )
        promo_b.scores.compute_overall()  # ~3.0

        accepted, dropped = deduplicate_promos([promo_b, promo_a], overlap_threshold=0.50)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0].promo_id, "promo_A_high_score")
        self.assertEqual(len(dropped), 1)
        self.assertEqual(dropped[0].promo_id, "promo_B_lower_score")


if __name__ == "__main__":
    unittest.main()
