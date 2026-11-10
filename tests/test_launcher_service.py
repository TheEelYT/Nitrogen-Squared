"""Portable service protocol and lifecycle checks; no game or graphical session."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from launcher_service import Service
from linux_support import LinuxLayout
from portable_launcher import instance_lock

class LauncherServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.layout=LinuxLayout(self.root);self.layout.app=ROOT;self.layout.writable()
        self.events=[];self.service=Service(self.layout,self.events.append,testing=True)
    def tearDown(self):self.temp.cleanup()
    def test_existing_preferences_and_readiness_are_read_without_preparing(self):
        (self.layout.local/'nitrogen-options.ini').write_text('master_volume 17\n# custom\n')
        with patch.object(self.service.backend,'prepare') as prepare:
            state=self.service.handle('state',{})
        prepare.assert_not_called();self.assertFalse(state['prepared']);self.assertEqual(state['options']['master_volume'],17)
        self.service.handle('save_option',dict(key='hud_scale',value=3))
        self.assertIn('# custom',(self.layout.local/'nitrogen-options.ini').read_text())
    def test_busy_task_survives_reads_and_refuses_conflicting_actions_and_close(self):
        started=threading.Event();finish=threading.Event()
        def work():started.set();finish.wait(10);self.service.notify('done','Ready')
        self.service.begin('Compiling',work);self.assertTrue(started.wait(2))
        try:
            for cmd,args in [('play',{}),('choose',{'path':'fixture.cue'}),('save_option',{'key':'hud_scale','value':3}),('close',{})]:
                with self.subTest(cmd=cmd),self.assertRaises(ValueError):self.service.handle(cmd,args)
            self.service.notify('progress','[ 42%] Building fixture')
            for _ in range(4):self.assertTrue(self.service.handle('state',{})['busy'])
            self.assertEqual(self.service.snapshot()['percent'],42)
        finally:finish.set()
    def test_backend_commands_and_open_destinations_are_limited(self):
        for cmd,args in [('shell',{'command':'anything'}),('open',{'target':'../saves'}),('save_option',{'key':'master_volume','value':101}),('install_update',{})]:
            with self.subTest(cmd=cmd),self.assertRaises(ValueError):self.service.handle(cmd,args)
        self.service.busy=True;self.service.phase='running'
        with self.assertRaises(ValueError):self.service.handle('stop',{})
        self.service.busy=False
    def test_installer_finalization_uses_only_backend_staged_package(self):
        with self.assertRaises(ValueError):self.service.handle('finalize_update',{'path':'untrusted'})
        self.service.phase='restart';self.service.staged=self.layout.local/'updates/verified'
        with patch('launcher_service.start_updater') as updater:
            self.service.handle('finalize_update',{'path':'untrusted'})
        updater.assert_called_once_with(self.layout,self.service.staged,0)
    def test_real_stdio_responses_keep_unicode_paths_and_emit_valid_json(self):
        # Run the same packaged Python entry point in an isolated portable folder.
        shutil.copytree(ROOT/'tools',self.root/'app/tools',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT/'configs',self.root/'app/configs');shutil.copy2(ROOT/'VERSION',self.root/'app/VERSION')
        report=self.layout.local/'actual-ui-report.json'
        proc=subprocess.Popen([sys.executable,'-I','-X','utf8','-B',str(self.root/'app/tools/launcher_service.py'),'--root',str(self.root),'--self-test','--report',str(report)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        requests=[dict(id=1,command='state'),dict(id=2,command='save_option',args=dict(key='master_volume',value=23)),dict(id=3,command='unsupported'),dict(id=4,command='self_test',args=dict(ui=dict(artwork=True,layout=False,navigation=['home'],progress=True))),dict(id=5,command='self_test',args=dict(ui=dict(artwork=True,layout=True,navigation=['home','news','settings'],progress=True)))]
        output,error=proc.communicate('\n'.join(json.dumps(r) for r in requests)+'\n',timeout=15)
        self.assertEqual(proc.returncode,0,error)
        messages=[json.loads(line) for line in output.splitlines()];replies={r['id']:r for r in messages if 'id' in r}
        self.assertEqual(replies[2]['result']['options']['master_volume'],23)
        self.assertIn('error',replies[3]);self.assertIn('error',replies[4]);self.assertTrue(replies[5]['result'])
        self.assertEqual(json.loads(report.read_text())['frontend'],'tauri')
        lock=instance_lock(self.layout);lock.close()

if __name__=='__main__':unittest.main()
