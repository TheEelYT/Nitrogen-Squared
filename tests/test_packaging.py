from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from package_source import audit_staging, collect, validate_file, ROOT


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_release_stage_rejects_extra_disc_or_capture(self):
        (self.root / "README.md").write_text("Source only")
        for name in ("disc.bin", "overlay_captures.json"):
            extra = self.root / name
            extra.write_bytes(b"unexpected")
            with self.assertRaisesRegex(ValueError, "release files"):
                audit_staging(self.root, {"README.md"})
            extra.unlink()

    def test_renamed_executable_is_rejected(self):
        (self.root / "notes.md").write_bytes(b"PS-X EXE" + bytes(2048))
        with self.assertRaises(ValueError):
            validate_file(self.root, "notes.md")

    def test_renamed_emitter_output_is_rejected(self):
        payload = "void " + "func_" + "80010000(CPUState* cpu) {}"
        (self.root / "notes.md").write_text(payload)
        with self.assertRaisesRegex(ValueError, "Generated game"):
            validate_file(self.root, "notes.md")

    def test_private_cache_cannot_be_allowlisted(self):
        (self.root / "cache").mkdir()
        (self.root / "cache/notes.md").write_text("private")
        with self.assertRaises(ValueError):
            validate_file(self.root, "cache/notes.md")

    def test_source_manifest_can_be_packaged(self):
        files = collect(ROOT)
        self.assertIn("README.md", files)
        self.assertIn("tools/n2o_disc.py", files)

    def test_parent_path_cannot_be_allowlisted(self):
        with self.assertRaises(ValueError):
            validate_file(self.root, "../outside.md")


if __name__ == "__main__":
    unittest.main()
