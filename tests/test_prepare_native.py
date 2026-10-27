import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from prepare_native import capture, add_resumes


class NativeSliceInputTests(unittest.TestCase):
    def test_resume_requires_a_guarded_owner(self):
        part = dict(func_addrs={0x80010000}, continuation_owners={0x80010020: 0x80010000},
                    ids_by_addr={0x80010000: [(123, [(0x80010000, 16)])]})
        with self.assertRaisesRegex(ValueError, "guarded owner"):
            add_resumes(object(), part)

    def test_unknown_resume_owner_is_rejected(self):
        part = dict(func_addrs={0x80010000}, continuation_owners={0x80010004: 0x80020000},
                    ids_by_addr={0x80010000: [(123, [(0x80010000, 16)])]})
        with self.assertRaisesRegex(ValueError, "guarded owner"):
            add_resumes(object(), part)

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
