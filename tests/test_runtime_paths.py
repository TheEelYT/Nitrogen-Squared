"""Save-path repair uses original synthetic configurations and card sentinels."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from portable_support import Layout, write_json
from portable_launcher import Backend
from runtime_paths import configured_saves, load_toml, repair_portable_saves
import run_runtime


class RuntimeSavePathsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="Save paths with spaces ")
        self.root = Path(self.temp.name) / "Nitrogen Squared"
        self.layout = Layout(self.root)
        self.layout.app.mkdir(parents=True)
        (self.layout.app / "configs").mkdir()
        (self.layout.app / "configs/portable_tools.json").write_text("{}")
        (self.layout.app / "VERSION").write_text("0.1.2\n")
        self.binary = self.layout.work / "build/NitrogenSquared-dev.exe"
        self.binary.parent.mkdir(parents=True)
        self.binary.write_bytes(b"original compiled-program preservation fixture")
        self.config = self.layout.work / "game.toml"
        self.config.write_text('# Keep this comment\n[game]\nname = "original fixture"\n[runtime]\nmemcard_dir = "saves"\noverlay_cache = true\n[video]\nrenderer = "opengl"\n')
        self.record = dict(build_succeeded=True, public_distribution_allowed=False,
                           installation=str(self.layout.installation), disc_sha256="original",
                           executable=str(self.binary), config=str(self.config))
        write_json(self.layout.work / "runtime-build.json", self.record)

    def tearDown(self):
        self.temp.cleanup()

    def test_repair_handles_both_binary_layouts_and_settings_without_recompiling(self):
        before = self.binary.read_bytes(), self.binary.stat().st_mtime_ns
        old = {}
        for subdir in ("build", "build/Release"):
            directory = self.layout.work / subdir
            directory.mkdir(exist_ok=True)
            (directory / "game.toml").write_bytes(self.config.read_bytes())
            settings = directory / "settings.toml"
            settings.write_text('# Retain other preferences\n[video]\nvsync = true\n[memcard]\ndir = "saves"\ncard1 = "old/card1.mcd"\ncard2 = "old/card2.mcd"\nenable2 = false\n')
            old[settings] = settings.read_bytes()
        changes = repair_portable_saves(self.layout)
        self.assertEqual(len(changes), 5)
        for path in [self.config, self.binary.parent / "game.toml", self.binary.parent / "Release/game.toml"]:
            self.assertEqual(configured_saves(path), self.layout.local / "saves")
            self.assertIn('# Keep this comment', path.read_text())
        for settings, original in old.items():
            data = load_toml(settings.read_text())
            self.assertEqual(data['memcard'], dict(dir=(self.layout.local/'saves').as_posix(), card1='', card2='', enable2=False))
            self.assertTrue(data['video']['vsync'])
            backups = list(settings.parent.glob('settings.toml.before-shared-saves-*'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(repair_portable_saves(self.layout), [])
        self.assertEqual((self.binary.read_bytes(), self.binary.stat().st_mtime_ns), before)

    def test_existing_launcher_and_direct_cards_are_never_merged_or_overwritten(self):
        primary = self.layout.local / "saves"
        legacy = self.layout.work / "saves"
        primary.mkdir(); legacy.mkdir()
        (primary / "card1.mcd").write_bytes(b"existing launcher progress")
        (legacy / "card1.mcd").write_bytes(b"different direct-launch progress")
        (legacy / "card2.mcd").write_bytes(b"legacy-only progress")
        repair_portable_saves(self.layout)
        self.assertEqual((primary/'card1.mcd').read_bytes(), b"existing launcher progress")
        self.assertEqual((legacy/'card1.mcd').read_bytes(), b"different direct-launch progress")
        self.assertFalse((primary/'card2.mcd').exists())
        self.assertEqual((legacy/'card2.mcd').read_bytes(), b"legacy-only progress")

    def test_legacy_only_cards_are_copied_without_deleting_the_original(self):
        legacy = self.layout.work / "saves"
        legacy.mkdir(); (legacy / "card1.mcd").write_bytes(b"legacy preservation fixture")
        repair_portable_saves(self.layout)
        self.assertEqual((self.layout.local/'saves/card1.mcd').read_bytes(), (legacy/'card1.mcd').read_bytes())

    def test_failed_legacy_copy_does_not_leave_a_partial_primary_folder(self):
        legacy = self.layout.work / 'saves'
        legacy.mkdir(); (legacy / 'card1.mcd').write_bytes(b'original legacy card')
        with patch('runtime_paths.shutil.copytree', side_effect=OSError('synthetic disk error')):
            with self.assertRaises(OSError): repair_portable_saves(self.layout)
        self.assertFalse((self.layout.local/'saves').exists())
        self.assertEqual((legacy/'card1.mcd').read_bytes(), b'original legacy card')

    def test_malformed_settings_preserve_all_configs_and_cards(self):
        original = self.config.read_bytes()
        (self.binary.parent / "settings.toml").write_text('[memcard]\ndir = "unterminated\n')
        with self.assertRaises(ValueError):
            repair_portable_saves(self.layout)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse((self.layout.local / 'saves').exists())

    def test_unrelated_working_directory_does_not_change_the_configured_path(self):
        repair_portable_saves(self.layout)
        previous = Path.cwd()
        try:
            os.chdir(self.temp.name)
            self.assertEqual(configured_saves(self.config), self.layout.local / "saves")
        finally:
            os.chdir(previous)

    def test_python_launch_uses_the_persisted_folder_or_explicit_override(self):
        repair_portable_saves(self.layout)
        for explicit in (None, self.root / "isolated test cards"):
            argv = ['run_runtime.py', '--work-dir', str(self.layout.work)]
            if explicit: argv += ['--save-dir', str(explicit)]
            child = Mock(); child.wait.return_value = 0
            with patch.object(sys, 'argv', argv), patch.object(run_runtime, 'load_installation', return_value={'bin_sha256':'original','bin':'synthetic-disc.bin'}), patch.object(run_runtime.subprocess, 'Popen', return_value=child) as start:
                self.assertEqual(run_runtime.main(), 0)
            command = start.call_args.args[0]
            self.assertEqual(Path(command[command.index('--memcard-dir')+1]), explicit or self.layout.local/'saves')

    def test_prepared_launcher_repairs_config_without_calling_the_compiler(self):
        write_json(self.layout.state_path, dict(schema=1, prepared_version=self.layout.version,
                   root=str(self.layout.root), prepared_tools=self.layout.tool_fingerprint()))
        backend = Backend(self.layout)
        with patch.object(backend, 'prepare', side_effect=AssertionError('must not compile')), patch('portable_launcher.run') as run:
            backend.play()
        self.assertEqual(configured_saves(self.config), self.layout.local / 'saves')
        self.assertEqual(len(run.call_args_list), 1)
        self.assertIn('run_runtime.py', run.call_args.args[0][6])

    def test_no_prepared_runtime_is_a_noop(self):
        (self.layout.work/'runtime-build.json').unlink()
        self.assertEqual(repair_portable_saves(self.layout), [])
        self.assertFalse((self.layout.local/'saves').exists())

    def test_linked_config_is_preserved(self):
        outside = Path(self.temp.name)/'outside.toml'
        outside.write_bytes(self.config.read_bytes());self.config.unlink()
        try:self.config.symlink_to(outside)
        except OSError:self.skipTest('Symlink creation is unavailable')
        original = outside.read_bytes()
        with self.assertRaises(ValueError):repair_portable_saves(self.layout)
        self.assertEqual(outside.read_bytes(), original)
