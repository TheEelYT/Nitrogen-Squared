"""Verified package updates and real launcher decisions with synthetic builds."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from package_source import collect
from portable_support import Layout, write_json, sha256
from linux_support import LinuxLayout
from portable_launcher import Backend
from portable_update import apply_update
from runtime_compatibility import input_fingerprint, build_identity, build_options, reusable_runtime
import run_runtime


def source_copy(app):
    for name, content in collect(ROOT).items():
        p = app / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)


def compiled_fixture(layout):
    binary = layout.work / "build" / ("game.exe" if layout.platform.startswith("windows") else "game")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"original synthetic compiled program")
    binary.with_suffix(".execution.json").write_text('{"profile":"ENHANCED","identity":"original fixture"}')
    config = layout.work / "game.toml"
    config.write_text('[runtime]\nmemcard_dir="saves"\n')
    options = build_options(cmake_args=layout.runtime_cmake_args(), environment=layout.environment())
    identity = build_identity(layout.app, binary, options)
    identity["platform"] = layout.platform # Model either target with original bytes.
    record = dict(schema=1, build_succeeded=True, public_distribution_allowed=False,
                  executable=str(binary), config=str(config), build_identity=identity)
    write_json(layout.work / "runtime-build.json", record)
    write_json(layout.state_path, dict(schema=1, prepared_version="0.2.0", root=str(layout.root),
                                     prepared_tools=layout.tool_fingerprint()))
    for path in (layout.local / "saves/card1.mcd", binary.parent / "keybinds.ini", layout.local / "nitrogen-options.ini"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"original private preservation sentinel")
    return binary, options, record


def manifest(root, platform, version):
    if platform.startswith("windows"):
        extras = {"launcher.exe":b"original bootstrap", "support/python/python.exe":b"original interpreter"}
    else:
        extras = {"launcher.sh":b"#!/bin/sh\n# original launcher fixture\n"}
    for name, data in extras.items():
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    files={p.relative_to(root).as_posix():dict(size=p.stat().st_size,sha256=sha256(p))
           for p in root.rglob('*') if p.is_file() and '.local' not in p.relative_to(root).parts
           and p.name != 'release-manifest.json'}
    write_json(root/'release-manifest.json',dict(schema=1,platform=platform,version=version,files=files))


class RuntimeCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="Build reuse with spaces ")
        self.root=Path(self.temp.name)/'Nitrogen-Squared'
        self.layout=Layout(self.root)
        source_copy(self.layout.app)
        self.binary,self.options,self.record=compiled_fixture(self.layout)

    def tearDown(self):self.temp.cleanup()

    def reusable(self):
        return reusable_runtime(self.layout.app,self.layout.work,self.layout.platform,self.options)

    def test_complete_build_reuses_without_changing_private_files(self):
        before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.layout.local.rglob('*') if p.is_file()}
        self.assertTrue(self.reusable())
        self.assertEqual(before,{p:(p.read_bytes(),p.stat().st_mtime_ns) for p in before})

    def test_version_docs_launcher_and_ci_edits_do_not_change_inputs(self):
        before=input_fingerprint(self.layout.app)
        for name in ('VERSION','README.md','TESTING.md','AGENTS.md','tools/portable_launcher.py',
                     'tools/portable_support.py','tools/linux_support.py','tools/runtime_compatibility.py','.github/workflows/windows-release.yml'):
            p=self.layout.app/name;p.write_bytes(p.read_bytes()+b'\n# original launcher-only fixture\n')
            self.assertEqual(input_fingerprint(self.layout.app),before,name)
        self.assertTrue(self.reusable())

    def test_all_build_input_classes_and_added_or_removed_source_force_rebuild(self):
        for name in ('CMakeLists.txt','cmake/keyboard_defaults.cmake','compat/keyboard_defaults.c',
                     'native/media.h','configs/native_usa.json','configs/runtime_inputs.json',
                     'tools/build_recompiler.py','tools/generate.py','tools/prepare_options.py','tools/adapt_window_display.py'):
            with self.subTest(path=name):
                p=self.layout.app/name;data=p.read_bytes();p.write_bytes(data+b'\n')
                self.assertFalse(self.reusable());p.write_bytes(data)
        added=self.layout.app/'native/new-original.c';added.write_text('int new_original(void){return 1;}\n')
        self.assertFalse(self.reusable());added.unlink()
        removed=self.layout.app/'native/media.h';data=removed.read_bytes();removed.unlink()
        self.assertFalse(self.reusable());removed.write_bytes(data)
        self.assertTrue(self.reusable())

    def test_git_line_endings_are_equivalent(self):
        p=self.layout.app/'compat/keyboard_defaults.c';p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
        self.assertTrue(self.reusable())

    def test_legacy_bad_receipts_platform_and_flags_cannot_reuse(self):
        changes=[{}, {'build_identity':{}}, {'schema':2}, {'platform':'another-platform'},
                 {'inputs_sha256':'0'*64}, {'options':build_options(diagnostics=True)},
                 {'executable_sha256':'0'*64}, {'execution_sha256':'0'*64}]
        for change in changes:
            record=copy.deepcopy(self.record)
            if change=={}:record.pop('build_identity')
            elif 'build_identity' in change:record.update(change)
            else:record['build_identity'].update(change)
            write_json(self.layout.work/'runtime-build.json',record)
            self.assertFalse(self.reusable(),change)
        (self.layout.work/'runtime-build.json').write_text('{broken')
        self.assertFalse(self.reusable())

    def test_missing_or_changed_outputs_force_rebuild(self):
        for p in (self.binary,self.binary.with_suffix('.execution.json'),Path(self.record['config'])):
            with self.subTest(path=str(p)):
                data=p.read_bytes();p.unlink();self.assertFalse(self.reusable());p.write_bytes(data)
        self.binary.write_bytes(b'changed executable')
        self.assertFalse(self.reusable())

    def test_build_environment_changes_require_rebuild_but_unrelated_env_does_not(self):
        env=self.layout.environment();env['UNRELATED_DISPLAY_PREFERENCE']='new'
        options=build_options(cmake_args=self.layout.runtime_cmake_args(),environment=env)
        self.assertEqual(options,self.options)
        env['CXXFLAGS']=env.get('CXXFLAGS','')+' -DORIGINAL_FIXTURE=1'
        self.assertFalse(reusable_runtime(self.layout.app,self.layout.work,self.layout.platform,
                                         build_options(cmake_args=self.layout.runtime_cmake_args(),environment=env)))

    def test_verified_launcher_only_package_update_does_not_call_prepare_on_either_platform(self):
        for cls in (Layout,LinuxLayout):
            with self.subTest(platform=cls.platform):
                root=Path(self.temp.name)/cls.platform
                layout=cls(root);source_copy(layout.app)
                (layout.app/'VERSION').write_text('0.2.0\n')
                binary,options,record=compiled_fixture(layout)
                manifest(root,layout.platform,'0.2.0')
                stage=layout.local/'updates/candidate';source_copy(stage/'app')
                (stage/'app/VERSION').write_text('0.2.1\n')
                for name in ('tools/portable_launcher.py','tools/linux_support.py'):
                    p=stage/'app'/name;p.write_bytes(p.read_bytes()+b'\n# original launcher-only fixture\n')
                manifest(stage,layout.platform,'0.2.1')
                protected=[binary,binary.parent/'keybinds.ini',layout.local/'saves/card1.mcd',layout.local/'nitrogen-options.ini']
                before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in protected}
                apply_update(layout,stage)
                backend=Backend(layout)
                with patch.object(backend,'prepare',side_effect=AssertionError('launcher-only update compiled')),patch('portable_launcher.run') as run:
                    backend.play()
                self.assertEqual(run.call_count,1)
                self.assertIn('run_runtime.py',str(run.call_args.args[0]))
                self.assertEqual(before,{p:(p.read_bytes(),p.stat().st_mtime_ns) for p in protected})
                self.assertEqual(layout.state()['prepared_version'],'0.2.0')

    def test_changed_input_calls_prepare_and_failed_prepare_never_launches_stale_game(self):
        p=self.layout.app/'compat/keyboard_defaults.c';p.write_bytes(p.read_bytes()+b'\n/* original changed input */\n')
        backend=Backend(self.layout);before=self.binary.read_bytes()
        with patch.object(backend,'prepare',side_effect=RuntimeError('original compile failure')) as prepare,patch('portable_launcher.run') as run:
            with self.assertRaisesRegex(RuntimeError,'compile failure'):backend.play()
        prepare.assert_called_once();run.assert_not_called();self.assertEqual(self.binary.read_bytes(),before)

    def test_direct_python_launch_refuses_legacy_build_before_disc_or_process(self):
        record=dict(self.record);record.pop('build_identity');write_json(self.layout.work/'runtime-build.json',record)
        with patch.object(sys,'argv',['run_runtime.py','--work-dir',str(self.layout.work)]),patch('run_runtime.load_installation') as disc,patch('run_runtime.subprocess.Popen') as start:
            with self.assertRaises(SystemExit):run_runtime.main()
        disc.assert_not_called();start.assert_not_called()

    def test_missing_or_escaping_input_definition_fails_closed(self):
        path=self.layout.app/'configs/runtime_inputs.json';definition=json.loads(path.read_text())
        for name in ('../outside.c','/absolute.c','C:/outside.c','compat//alias.c','missing.c'):
            d=copy.deepcopy(definition);d['files'].append(name);write_json(path,d)
            self.assertFalse(self.reusable(),name)

    def test_cache_replacement_retains_custom_input_and_keeps_existing_new_preferences(self):
        build=self.binary.parent
        (build/'input.ini').write_bytes(b'custom gamepad profile')
        (build/'settings.toml').write_bytes(b'old settings fixture')
        backend=Backend(self.layout);backend.retain_runtime_preferences(build)
        target=self.layout.local/'fresh-build/game.exe';target.parent.mkdir()
        (target.parent/'settings.toml').write_bytes(b'new settings fixture')
        backend.restore_runtime_preferences(target)
        self.assertEqual((target.parent/'keybinds.ini').read_bytes(),b'original private preservation sentinel')
        self.assertEqual((target.parent/'input.ini').read_bytes(),b'custom gamepad profile')
        self.assertEqual((target.parent/'settings.toml').read_bytes(),b'new settings fixture')
