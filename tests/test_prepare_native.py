import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from prepare_native import capture


class NativeSliceInputTests(unittest.TestCase):
    def test_rejects_unaligned_outside_duplicate_or_empty_entries(self):
        for data, base, entries in [(b"", 0x80010000, [0x80010000]),
                                    (b"abc", 0x80010000, [0x80010000]),
                                    (b"1234", 0x80010001, [0x80010001]),
                                    (b"1234", 0x80010000, []),
                                    (b"1234", 0x80010000, [0x80010004]),
                                    (b"1234", 0x80010000, [0x80010002]),
                                    (b"1234", 0x80010000, [0x80010000, 0x80010000])]:
            with self.subTest(base=base, entries=entries), self.assertRaises(ValueError):
                capture(data, base, entries)
