import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from native_progress import covered_ranges


class NativeProgressTests(unittest.TestCase):
    def test_overlapping_and_duplicate_ranges_count_once(self):
        text = "# original synthetic ranges\nF 1000\nF 1000\nR 1000 10\nR 1008 10\nR 1020 4\n"
        self.assertEqual(covered_ranges(text, 0x1000, 0x40), (0x1C, 1))

    def test_adjacent_ranges_and_empty_manifest(self):
        self.assertEqual(covered_ranges("R 1000 4\nR 1004 4\n", 0x1000, 8), (8, 0))
        self.assertEqual(covered_ranges("# no linked code\n", 0x1000, 8), (0, 0))

    def test_outside_unaligned_or_unknown_ranges_are_rejected(self):
        for text in ("R ffc 4", "R 1000 24", "R 1001 4", "R 1000 3", "R 1000 0", "B 1000 4"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                covered_ranges(text, 0x1000, 0x20)
