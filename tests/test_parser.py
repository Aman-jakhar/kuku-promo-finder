"""tests/test_parser.py

Unit tests for parser.py, verifying deterministic screenplay parsing.
Specifically tests Episode 1 (Scene 01 running 0.00 to 138.00s).
"""

import unittest
from pathlib import Path

from parser import (
    parse_timestamp,
    format_timestamp,
    parse_label,
    parse_episode_file,
    condense_episode
)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path("data")
        self.ep1_files = list(self.data_dir.glob("episode-001*.txt"))
        if not self.ep1_files:
            self.skipTest("Episode 1 script not found in ./data/")
        self.ep1_path = self.ep1_files[0]
        self.ep1 = parse_episode_file(self.ep1_path)

    def test_timestamp_conversions(self):
        """Test timestamp string to float seconds and formatting."""
        self.assertEqual(parse_timestamp("00:00.00"), 0.0)
        self.assertEqual(parse_timestamp("02:18.00"), 138.0)
        self.assertEqual(parse_timestamp("01:14.50"), 74.5)
        self.assertEqual(parse_timestamp("(00:11.30)"), 11.3)

        self.assertEqual(format_timestamp(0.0), "00:00.00")
        self.assertEqual(format_timestamp(138.0), "02:18.00")
        self.assertEqual(format_timestamp(74.5), "01:14.50")

    def test_label_parsing(self):
        """Test parsing label strings into kind, speaker, and emotion."""
        kind, spk, emo = parse_label("CAMERA:")
        self.assertEqual(kind, "CAMERA")
        self.assertIsNone(spk)

        kind, spk, emo = parse_label("ACTION:")
        self.assertEqual(kind, "ACTION")
        self.assertIsNone(spk)

        kind, spk, emo = parse_label("SOUND FX:")
        self.assertEqual(kind, "SOUND FX")
        self.assertIsNone(spk)

        kind, spk, emo = parse_label("MATRIARCH (Cold, Commanding):")
        self.assertEqual(kind, "DIALOGUE")
        self.assertEqual(spk, "MATRIARCH")
        self.assertEqual(emo, "Cold, Commanding")

        kind, spk, emo = parse_label("LADY JULIANA (Confused, Breathless):")
        self.assertEqual(kind, "DIALOGUE")
        self.assertEqual(spk, "LADY JULIANA")
        self.assertEqual(emo, "Confused, Breathless")

        kind, spk, emo = parse_label("ALEXANDER:")
        self.assertEqual(kind, "DIALOGUE")
        self.assertEqual(spk, "ALEXANDER")
        self.assertIsNone(emo)

    def test_episode_1_scene_01_duration(self):
        """VERIFIED HARD SPEC: Episode 1 Scene 01 should run exactly 0.00 to 138.00s."""
        self.assertEqual(self.ep1.ep_num, 1)
        self.assertGreaterEqual(len(self.ep1.scenes), 1)

        scene_01 = self.ep1.scenes[0]
        self.assertEqual(scene_01.scene_id, "SCENE 01")
        self.assertAlmostEqual(scene_01.start_s, 0.00, places=2)
        self.assertAlmostEqual(scene_01.end_s, 138.00, places=2)
        self.assertAlmostEqual(scene_01.end_s - scene_01.start_s, 138.00, places=2)

    def test_episode_1_metadata(self):
        """Test logline and continuity extraction for Episode 1."""
        self.assertIn("Juliana", self.ep1.logline)
        self.assertIn("cathedral", self.ep1.logline.lower())
        self.assertIn("Gerald", self.ep1.logline)
        self.assertIn("betrayal", self.ep1.logline.lower())

        self.assertIn("First episode of the series", self.ep1.continuity_notes)

    def test_episode_1_events_count_and_types(self):
        """Test that events are parsed with proper types and non-empty text."""
        self.assertGreater(len(self.ep1.events), 50)
        kinds = {e.kind for e in self.ep1.events}
        self.assertIn("CAMERA", kinds)
        self.assertIn("ACTION", kinds)
        self.assertIn("DIALOGUE", kinds)
        self.assertIn("SOUND FX", kinds)

        # Check dialogue events have non-empty speakers and texts
        dialogue_events = [e for e in self.ep1.events if e.kind == "DIALOGUE"]
        self.assertGreater(len(dialogue_events), 20)
        for d in dialogue_events:
            self.assertIsNotNone(d.speaker)
            self.assertGreater(len(d.text), 0)

    def test_legal_boundaries(self):
        """Test extraction of legal cut start and end boundaries."""
        starts = self.ep1.get_legal_start_boundaries()
        ends = self.ep1.get_legal_end_boundaries()

        self.assertIn(0.0, starts)
        self.assertIn(138.0, ends)
        # Every boundary should be non-negative and <= 138.0s
        self.assertTrue(all(s >= 0.0 and s <= 138.0 for s in starts))
        self.assertTrue(all(e >= 0.0 and e <= 138.0 for e in ends))

    def test_condenser_output(self):
        """Test condensed representation drops CAMERA lines and includes logline."""
        condensed = condense_episode(self.ep1, include_camera=False)
        self.assertIn("EPISODE 1 LOGLINE:", condensed)
        self.assertIn("CONTINUITY:", condensed)
        self.assertIn("MATRIARCH", condensed)
        self.assertIn("LADY JULIANA", condensed)
        # Verify CAMERA lines are omitted from condensed text
        self.assertNotIn("CAMERA:", condensed)


if __name__ == "__main__":
    unittest.main()
