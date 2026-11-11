"""Original Linux launcher/package fixtures, without commercial input."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from linux_support import LinuxLayout
from package_linux import stage
from portable_support import Layout,extract_zip,write_json,sha256
from portable_update import apply_update,read_manifest,verify_package
from check_renderer import sdl_include_dir

class LinuxPackageTests(unittest.TestCase):
    def test_runtime_fixture_uses_configured_sdl_outside_build_with_spaces(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);build=root/'private work';build.mkdir()
            source=root/'pinned SDL source';header=source/'include/SDL3/SDL.h'
            header.parent.mkdir(parents=True);header.write_text('/* original fixture */')
            (build/'CMakeCache.txt').write_text('SDL3_SOURCE_DIR:STATIC='+str(source)+'\n')
            self.assertEqual(sdl_include_dir(build),source/'include')
            header.unlink()
            with self.assertRaisesRegex(ValueError,'Missing configured SDL3 headers'):
                sdl_include_dir(build)

    def test_linux_environment_uses_host_tools_and_local_state(self):
        with tempfile.TemporaryDirectory() as t:
            l=LinuxLayout(Path(t));env=l.environment()
            self.assertEqual(l.python,Path(sys.executable).resolve())
            from build_policy import build_jobs
            self.assertEqual(env['CMAKE_BUILD_PARALLEL_LEVEL'],str(build_jobs()))
            self.assertEqual(env['CMAKE_GENERATOR'],'Unix Makefiles')
            self.assertNotIn('mingw',env.get('CC',''))
            Path(env['TMPDIR']).relative_to(l.root)
            Path(env['PSX_SDL3_SOURCE_DIR']).relative_to(l.root)
            self.assertIn('Linux',l.display_name)
            self.assertNotEqual(l.asset_name,Layout(Path(t)).asset_name)

    def test_linux_package_exact_inventory_and_update_preservation(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);archive=p/'linux.zip'
            bundle=p/'launcher-fixture';(bundle/'licenses').mkdir(parents=True)
            (bundle/'launcher').write_bytes(b'original native host fixture')
            (bundle/'licenses/DEPENDENCIES.json').write_text('[]')
            # Crate/distribution notices can preserve pre-ZIP (1970) timestamps.
            os.utime(bundle/'licenses/DEPENDENCIES.json',(0,0))
            stage(archive,launcher_bundle=bundle);extract_zip(archive,p/'install')
            root=p/'install/Nitrogen-Squared';l=LinuxLayout(root);old=verify_package(root)
            self.assertEqual(old['platform'],'linux-x86_64')
            self.assertFalse((root/'launcher.exe').exists())
            self.assertFalse((root/'support/python').exists())
            self.assertTrue((root/'launcher').is_file())
            self.assertTrue((root/'support/launcher/licenses/DEPENDENCIES.json').is_file())
            if os.name!='nt':self.assertTrue((root/'launcher.sh').stat().st_mode&0o100)
            staged=l.local/'updates/stage';staged.mkdir(parents=True)
            import shutil
            for name in old['files']:
                dst=staged/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,dst)
            v=old['version'].split('.');v[-1]=str(int(v[-1])+1);version='.'.join(v)
            (staged/'app/VERSION').write_text(version+'\n')
            write_json(staged/'release-manifest.json',dict(old,version=version,files={n:dict(size=(staged/n).stat().st_size,sha256=sha256(staged/n)) for n in old['files']}))
            (l.local/'saves').mkdir();(l.local/'saves/sentinel').write_bytes(b'original private fixture')
            apply_update(l,staged)
            self.assertEqual(read_manifest(root)['version'],version)
            self.assertEqual((l.local/'saves/sentinel').read_bytes(),b'original private fixture')
            self.assertFalse((l.local/'update-state.json').exists())

    def test_update_rejects_another_platform(self):
        from test_portable import package
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'Nitrogen-Squared';root.mkdir();package(root,'0.0.1')
            staged=root/'.local/updates/stage';package(staged,'0.0.2')
            with self.assertRaisesRegex(ValueError,'platform'):
                apply_update(LinuxLayout(root),staged)
