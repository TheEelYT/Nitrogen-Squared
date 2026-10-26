import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_disc import fixture
from n2o_disc import DiscError, prepare
import build_runtime
import run_runtime


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

    def test_runtime_config_explicitly_routes_first_gamepad(self):
        manifest = json.loads((self.installation / "installation.json").read_text())
        manifest["executables"][0]["path"] = "SLUS_006.37"
        text = build_runtime.runtime_config(manifest, self.installation, self.root / "generated")
        controller = text.split("[controller]\n", 1)[1]
        self.assertIn('p1_device = "auto"', controller)
        self.assertIn('p2_device = "none"', controller)
        self.assertIn('default_mode = "analog"', controller)
        digital = build_runtime.runtime_config(manifest, self.installation, self.root / "generated", "digital")
        self.assertIn('default_mode = "digital"', digital)
        with self.assertRaises(ValueError):
            build_runtime.runtime_config(manifest, self.installation, self.root / "generated", "invalid")

    def test_play_environment_disables_frame_history_without_changing_parent(self):
        with patch.dict(run_runtime.os.environ, {"PSX_DISPLAY_RING": "1"}):
            env = run_runtime.runtime_environment(self.root)
            self.assertEqual(env["PSX_DISPLAY_RING"], "0")
            self.assertEqual(env["PSX_OVERLAY_AUTOCOMPILE_OFF"], "1")
            self.assertEqual(Path(env["PSX_OVERLAY_CAPTURES"]), self.root / "overlay_captures.json")
            self.assertEqual(run_runtime.os.environ["PSX_DISPLAY_RING"], "1")
            self.assertEqual(run_runtime.runtime_environment(self.root, True)["PSX_DISPLAY_RING"], "1")
            self.assertEqual(run_runtime.runtime_environment(self.root, show_fps=True)["PSX_FPS_TELEMETRY"], "1")

    def test_render_worker_defaults_and_explicit_comparison(self):
        with patch.dict(run_runtime.os.environ, {}, clear=True):
            env = run_runtime.runtime_environment(self.root)
            self.assertEqual(env["PSX_RENDER_THREAD"], "1")
            self.assertEqual(env["PSX_RENDER_THREAD_FRAMES"], "1")
            self.assertNotIn("PSX_RENDER_THREAD", run_runtime.os.environ)
        with patch.dict(run_runtime.os.environ, {"PSX_RENDER_THREAD": "0", "PSX_RENDER_THREAD_FRAMES": "2"}):
            self.assertEqual(run_runtime.runtime_environment(self.root)["PSX_RENDER_THREAD"], "0")
            self.assertEqual(run_runtime.runtime_environment(self.root, render_worker=True)["PSX_RENDER_THREAD"], "1")
            self.assertEqual(run_runtime.runtime_environment(self.root, render_worker=False)["PSX_RENDER_THREAD"], "0")
            self.assertEqual(run_runtime.runtime_environment(self.root)["PSX_RENDER_THREAD_FRAMES"], "2")


if __name__ == "__main__":
    unittest.main()
