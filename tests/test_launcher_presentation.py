"""Launcher preferences, offline notes and distribution boundary contracts."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from launcher_presentation import (DEFAULT_OPTIONS,valid_option,read_options,save_option,
    read_release_cache,fetch_release_history,release_list,clean_release,progress_summary,
    read_launcher_preferences,set_accent)
from package_source import launcher_assets,collect,collect_package,audit_staging
from portable_launcher import Backend
from linux_support import LinuxLayout
from runtime_compatibility import input_fingerprint


class LauncherPresentationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()

    def test_opening_preferences_is_read_only_and_invalid_fields_are_ignored(self):
        self.assertEqual(read_options(self.root),DEFAULT_OPTIONS)
        self.assertEqual(list(self.root.iterdir()),[])
        path=self.root/'nitrogen-options.ini'
        content='video_mode 2\nhud_scale 1\nrender_percent 70\nmaster_volume 50 trailing\nfuture 8\n'
        path.write_text(content)
        self.assertEqual(read_options(self.root),dict(video_mode=2,hud_scale=0,render_percent=70,master_volume=100))
        self.assertEqual(path.read_text(),content)

    def test_preferences_preserve_other_settings_comments_and_unknown_fields(self):
        path=self.root/'nitrogen-options.ini';path.write_text('video_mode 1\nmaster_volume 26\n# keep me\nfuture 8\n')
        save_option(self.root,'hud_scale',3)
        self.assertEqual(read_options(self.root),dict(video_mode=1,hud_scale=3,render_percent=100,master_volume=26))
        self.assertIn('# keep me\nfuture 8\n',path.read_text())
        before=path.stat().st_mtime_ns;save_option(self.root,'hud_scale',3)
        self.assertEqual(path.stat().st_mtime_ns,before)
        for key,value in [('hud_scale',1),('video_mode',3),('render_percent',99),('master_volume',101),('master_volume',True),('master_volume','10')]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):save_option(self.root,key,value)

    def test_preferences_preserve_symlink_targets_and_interrupted_write(self):
        target=self.root/'original';target.write_text('original')
        path=self.root/'nitrogen-options.ini'
        try:path.symlink_to(target)
        except OSError:self.skipTest('Symbolic links unavailable')
        with self.assertRaises(ValueError):save_option(self.root,'master_volume',10)
        self.assertEqual(target.read_text(),'original');path.unlink()
        tmp=self.root/'nitrogen-options.launcher.tmp';tmp.write_text('interrupted')
        with self.assertRaises(ValueError):save_option(self.root,'master_volume',10)
        self.assertEqual(tmp.read_text(),'interrupted');self.assertFalse(path.exists())

    def test_native_option_ranges(self):
        for key,values in [('video_mode',range(3)),('hud_scale',[0,2,3,4,6]),('render_percent',range(25,201,5)),('master_volume',range(101))]:
            self.assertTrue(all(valid_option(key,v) for v in values))
        self.assertFalse(valid_option('other',0));self.assertFalse(valid_option('master_volume',-1))

    def test_accent_roundtrip_and_invalid_cache_fallback(self):
        self.assertEqual(read_launcher_preferences(self.root),dict(accent='Cyan'))
        set_accent(self.root,'Violet');self.assertEqual(read_launcher_preferences(self.root)['accent'],'Violet')
        with self.assertRaises(ValueError):set_accent(self.root,'Unknown')
        (self.root/'launcher-preferences.json').write_text('null')
        self.assertEqual(read_launcher_preferences(self.root)['accent'],'Cyan')

    def test_notes_use_bundled_current_and_actual_published_history_offline(self):
        layout=SimpleNamespace(app=ROOT,local=self.root,version='0.2.1')
        self.assertEqual(read_release_cache(self.root),[])
        notes=release_list(layout,[]);self.assertEqual([n['version'] for n in notes],['0.2.1'])
        actual=dict(tag_name='v0.1.3',name='0.1.3',body='PC controls',published_at='2026-11-08T00:00:00Z',html_url='https://untrusted.invalid')
        with patch('launcher_presentation.api_json',return_value=[actual,dict(actual,prerelease=True),dict(tag_name='bad')]) as fetch:
            online=fetch_release_history(self.root)
        self.assertEqual(online,read_release_cache(self.root));self.assertEqual(len(online),1)
        self.assertTrue(online[0]['url'].startswith('https://github.com/TheEelYT/Nitrogen-Squared/'))
        self.assertEqual([n['version'] for n in release_list(layout,online)],['0.2.1','0.1.3'])
        with patch('launcher_presentation.api_json',side_effect=OSError('offline')):
            with self.assertRaises(OSError):fetch_release_history(self.root)
        self.assertEqual(online,read_release_cache(self.root))
        self.assertIsNone(clean_release(dict(actual,draft=True)))

    def test_progress_is_current_stage_only_and_unknown_does_not_invent_percent(self):
        self.assertEqual(progress_summary('[ 42%] Building CXX object')[2],42)
        self.assertEqual(progress_summary('[12/24] Compiling original fixture')[2],50)
        self.assertEqual(progress_summary('[999%] stage')[2],100)
        self.assertIsNone(progress_summary('[12/0] invalid'))
        for line in ['Preparing game','Downloaded compiler','Verifying the complete disc','Extracting assets','Game running. Close window']:
            with self.subTest(line=line):self.assertIsNone(progress_summary(line)[2])
        self.assertIsNone(progress_summary('unstructured tool output'))

    def test_choose_disc_only_never_bootstraps_or_compiles(self):
        layout=LinuxLayout(self.root);layout.app=ROOT;events=[];backend=Backend(layout,lambda *args:events.append(args))
        with patch.object(backend,'import_disc') as imported,patch.object(backend,'play') as play,patch('portable_launcher.bootstrap') as bootstrap:
            backend.action(Path('fixture.cue'),play=False,import_only=True)
        imported.assert_called_once();play.assert_not_called();bootstrap.assert_not_called()
        self.assertEqual(events[-1],('done','Game disc verified. Ready to prepare.'))

    def test_launcher_only_candidate_retains_verified_game_fingerprint(self):
        self.assertEqual(input_fingerprint(ROOT),'4ab9bc7e2cf8067a308fa329692040366619bfd9000b020368832efe70a156af')

    def test_original_artwork_separate_from_text_and_complete_package(self):
        assets=launcher_assets(ROOT);text=collect(ROOT)
        self.assertEqual(set(assets),{'launcher/assets/logo.png','launcher/assets/tunnel.png'})
        self.assertFalse(set(assets)&set(text));self.assertEqual(collect_package(ROOT),text|assets)
        self.assertEqual(assets['launcher/assets/logo.png'],(ROOT/'docs/images/logo.png').read_bytes())
        for name,data in assets.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        (self.root/'configs').mkdir();manifest=self.root/'configs/launcher_assets.json'
        manifest.write_bytes((ROOT/'configs/launcher_assets.json').read_bytes())
        audit_staging(self.root,set(assets)|{'configs/launcher_assets.json'})
        tunnel=self.root/'launcher/assets/tunnel.png';tunnel.write_bytes(tunnel.read_bytes()+b'tamper')
        with self.assertRaisesRegex(ValueError,'Unreviewed'):launcher_assets(self.root)
        manifest.write_text(json.dumps({'../unreviewed.png':'0'*64}))
        with self.assertRaisesRegex(ValueError,'Unsupported'):launcher_assets(self.root)
