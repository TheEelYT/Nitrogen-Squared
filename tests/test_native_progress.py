import sys
import unittest
import json
import struct
import tempfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from native_progress import covered_ranges, report
from n2o_disc import digest


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

    def test_linked_slice_union_reference_omission_and_changed_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "configs").mkdir()
            (root / "executables").mkdir()
            (root / "generated/TEST").mkdir(parents=True)
            exe = root / "executables/TEST"
            program = bytearray(2048 + 64)
            program[:8] = b"PS-X EXE"
            for offset, value in [(16, 0x80001000), (24, 0x80001000), (28, 64), (48, 0x801FFF00)]:
                struct.pack_into("<I", program, offset, value)
            exe.write_bytes(program)
            (root / "configs/disc_usa.json").write_text(json.dumps(dict(executables=[
                dict(path="TEST", size=len(program), sha256=digest(exe))])))
            (root / "generated/TEST/TEST_full.ranges").write_text("F 80001000\nR 80001000 10\n")
            source = root / "original.c"
            source.write_text("/* Original synthetic fixture. */\n")
            ranges = root / "slice.ranges"
            ranges.write_text("F 80001008\nR 80001008 10\n")
            inventory = root / "game-slices.json"
            inventory.write_text(json.dumps(dict(schema=1,
                files={source.name: digest(source), ranges.name: digest(ranges)},
                slices=[dict(executable="TEST", ranges=ranges.name)])))
            receipt = dict(build_succeeded=True, generated_dir=str(root / "generated"),
                           installation=str(root), linked_executables=["TEST"],
                           native_slices=[dict(manifest=str(inventory), sha256=digest(inventory))])
            build = root / "runtime-build.json"
            build.write_text(json.dumps(receipt))
            with patch("native_progress.ROOT", root):
                self.assertEqual(report(root)["native_range_bytes"], 24)
                source.write_text("/* Changed after linking. */\n")
                with self.assertRaisesRegex(ValueError, "source/ranges changed"):
                    report(root)
                receipt["native_slices"] = []
                build.write_text(json.dumps(receipt))
                self.assertEqual(report(root)["native_range_bytes"], 16)
