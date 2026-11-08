import json
from pathlib import Path
import tempfile
import shutil
import subprocess
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
        from runtime_paths import load_toml
        shared = self.root / 'portable folder/.local/saves'
        configured = build_runtime.runtime_config(manifest, self.installation, self.root / 'generated', save_dir=shared)
        self.assertEqual(load_toml(configured)['runtime']['memcard_dir'], shared.resolve().as_posix())

    def test_execution_manifest_matches_cmake_basename_for_both_layouts(self):
        for rel in ("Release/NitrogenSquared-dev.exe", "NitrogenSquared-dev"):
            with self.subTest(binary=rel):
                executable = self.root / rel
                executable.parent.mkdir(parents=True, exist_ok=True)
                executable.write_text("original synthetic placeholder")
                sidecar = executable.parent / "NitrogenSquared-dev.execution.json"
                for profile in ("REFERENCE", "ENHANCED"):
                    expected = dict(schema=1, profile=profile, identity="synthetic")
                    sidecar.write_text(json.dumps(expected))
                    if executable.suffix == ".exe":
                        # A stale file with the old, incorrect name must not win.
                        Path(str(executable) + ".execution.json").write_text('{"profile":"stale"}')
                    self.assertEqual(build_runtime.load_execution_manifest(executable), expected)
                sidecar.unlink()
                with self.assertRaises(FileNotFoundError):
                    build_runtime.load_execution_manifest(executable)

    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler required for hotkey policy')
    def test_tab_cannot_trigger_hold_turbo_and_other_input_survives(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/'psx_sdl.h').write_text('#pragma once\n#define SDL_NUM_SCANCODES 512\n#define SDL_SCANCODE_TAB 43\n')
            (p/'host_keymap.h').write_text('#pragma once\n#include <stdint.h>\nenum HostKeymapAction {HOST_KEYMAP_TURBO,OTHER};\nint host_keymap_down(HostKeymapAction,const uint8_t*,int);\n')
            (p/'fixture.cpp').write_text(r'''
#include "host_hotkeys.h"
#include <cassert>
static const uint8_t *original;
int host_keymap_down(HostKeymapAction a,const uint8_t*k,int mod){
 assert(mod==7);if(!k)return 0;
 if(a==OTHER){assert(k==original);return k[SDL_SCANCODE_TAB];}
 return k[SDL_SCANCODE_TAB] || k[44]; // default/saved Tab and another Turbo binding
}
int main(){
 uint8_t keys[SDL_NUM_SCANCODES]{};original=keys;
 keys[SDL_SCANCODE_TAB]=1;
 assert(!nitrogen_host_keymap_down(HOST_KEYMAP_TURBO,keys,7));
 assert(keys[SDL_SCANCODE_TAB]==1); // never mutate SDL keyboard state
 assert(nitrogen_host_keymap_down(OTHER,keys,7));
 keys[44]=1;assert(nitrogen_host_keymap_down(HOST_KEYMAP_TURBO,keys,7));
 keys[SDL_SCANCODE_TAB]=0;assert(nitrogen_host_keymap_down(HOST_KEYMAP_TURBO,keys,7));
 keys[44]=0;assert(!nitrogen_host_keymap_down(HOST_KEYMAP_TURBO,keys,7));
 assert(!nitrogen_host_keymap_down(HOST_KEYMAP_TURBO,nullptr,7));
}
''')
            root=Path(__file__).resolve().parents[1]
            subprocess.run(['c++','-std=c++17','-I',str(p),'-I',str(root/'compat'),str(p/'fixture.cpp'),'-o',str(p/'fixture')],check=True)
            subprocess.run([str(p/'fixture')],check=True)
            host=(root/'compat/runtime_host.cpp').read_text()
            self.assertLess(host.index('#define host_keymap_down nitrogen_host_keymap_down'),host.index('#include NITROGEN_FRAMEWORK_MAIN'))
            self.assertGreater(host.index('#undef host_keymap_down'),host.index('#include NITROGEN_FRAMEWORK_MAIN'))

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
