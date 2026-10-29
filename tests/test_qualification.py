import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/qualification"))
from selection import build_selection, read_selection, selection_text


class QualificationIdentityTests(unittest.TestCase):
    def fixture(self, image, crc, sha):
        # Original metadata only: no guest instruction words or imported inputs.
        owner = 0x80020000
        item = dict(executable=image, entries=[owner], resume_entries=[dict(owner=owner, entry=owner+4)],
                    identities=[dict(owner=owner, crc=crc, code_sha256=sha, ranges=[[owner, 8]])])
        spec = dict(executable=image, start=hex(owner), size=16, entries=[hex(owner)])
        return item, spec

    def test_overlapping_images_keep_distinct_witness_identities(self):
        a, sa = self.fixture("FIRST", 123, "a"*64)
        b, sb = self.fixture("SECOND", 456, "b"*64)
        rows = build_selection(dict(slices=[a, b]), [sa, sb])
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["id"], rows[1]["id"])
        self.assertEqual(rows[0]["pcs"], rows[1]["pcs"])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"selection.tsv"
            p.write_text(selection_text(rows))
            restored = read_selection(p)
            self.assertEqual([r["id"] for r in restored], [r["id"] for r in rows])

    def test_identical_guarded_code_is_explicitly_shared(self):
        a, sa = self.fixture("FIRST", 123, "a"*64)
        b, sb = self.fixture("SECOND", 123, "a"*64)
        rows = build_selection(dict(slices=[a, b]), [sa, sb])
        self.assertEqual(len(rows), 1)
        self.assertEqual({x["executable"] for x in rows[0]["images"]}, {"FIRST", "SECOND"})

    def test_crc_collision_does_not_merge_different_code(self):
        a, sa = self.fixture("FIRST", 123, "a"*64)
        b, sb = self.fixture("SECOND", 123, "b"*64)
        with self.assertRaisesRegex(ValueError, "Ambiguous CRC"):
            build_selection(dict(slices=[a, b]), [sa, sb])

    def test_missing_or_unguarded_owner_cannot_be_credited(self):
        a, sa = self.fixture("FIRST", 123, "a"*64)
        with self.assertRaisesRegex(ValueError, "Missing selected identities"):
            build_selection(dict(slices=[]), [sa])
        bad = copy.deepcopy(a)
        bad["resume_entries"][0]["entry"] += 20
        with self.assertRaisesRegex(ValueError, "guarded owner"):
            build_selection(dict(slices=[bad]), [sa])

    def test_truncated_legacy_and_tampered_identity_rows_fail_closed(self):
        a, sa = self.fixture("FIRST", 123, "a"*64)
        rows = build_selection(dict(slices=[a]), [sa])
        text = selection_text(rows)
        cases = ["80020000 10\n80020000\n", "v2\n", text+text.splitlines()[1]+"\n",
                 text.rsplit(" ", 1)[0]+"\n"]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"selection.tsv"
            for value in cases:
                p.write_text(value)
                with self.subTest(value=value), self.assertRaises(ValueError):
                    read_selection(p)
