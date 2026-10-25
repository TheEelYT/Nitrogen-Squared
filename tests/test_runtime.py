import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_disc import fixture
from n2o_disc import DiscError, prepare
import build_runtime


class RuntimePreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cue, self.identity = fixture(self.root)
        (self.root / "configs").mkdir()
        (self.root / "configs/disc_usa.json").write_text(json.dumps(self.identity))
        self.installation = self.root / "installation"
        prepare(self.cue, self.installation, self.identity)
        self.patch = patch.object(build_runtime, "ROOT", self.root)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_previously_imported_disc_is_revalidated(self):
        result = build_runtime.load_installation(self.installation)
        self.assertEqual(result["game_id"], "TEST")
        image = self.root / "synthetic.bin"
        data = bytearray(image.read_bytes())
        data[-1] ^= 1
        image.write_bytes(data)
        with self.assertRaisesRegex(DiscError, "digest"):
            build_runtime.load_installation(self.installation)

    def test_local_executable_change_is_rejected(self):
        exe = self.installation / "executables/MAIN.EXE"
        data = bytearray(exe.read_bytes())
        data[-1] ^= 1
        exe.write_bytes(data)
        with self.assertRaisesRegex(DiscError, "executable changed"):
            build_runtime.load_installation(self.installation)

    def test_find_binary_supports_multiconfig_and_single_config_builds(self):
        build = self.root / "build"
        (build / "Release").mkdir(parents=True)
        binary = build / "Release/test-emitter.exe"
        binary.write_text("synthetic placeholder")
        self.assertEqual(build_runtime.find_binary(build, "test-emitter"), binary.resolve())
        binary.unlink()
        binary = build / "test-emitter"
        binary.write_text("synthetic placeholder")
        self.assertEqual(build_runtime.find_binary(build, "test-emitter"), binary.resolve())
        binary.unlink()
        with self.assertRaises(FileNotFoundError):
            build_runtime.find_binary(build, "test-emitter")


if __name__ == "__main__":
    unittest.main()
