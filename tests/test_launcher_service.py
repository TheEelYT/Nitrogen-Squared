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


class LaunchProgressRegressionTests(unittest.TestCase):
    setUp=LauncherServiceTests.setUp
    tearDown=LauncherServiceTests.tearDown
    def test_fast_progress_never_drops_startup_verification_or_running_transition(self):
        self.service.busy=True;self.service.phase='starting'
        with patch('launcher_service.time.monotonic',return_value=100):
            self.service.notify('progress','Using your existing compatible game build.')
            self.service.notify('progress','Verifying the complete disc, including audio tracks…')
            self.service.notify('progress','Runtime started (PID 42). Log: local/runtime.log')
        states=[e['payload'] for e in self.events if e.get('event')=='state']
        self.assertEqual([s['title'] for s in states],['Starting game','Verifying your disc','Game running'])
        self.assertEqual(states[-1]['phase'],'running')
        self.assertEqual(states[1]['phase'],'starting')
        with self.assertRaises(ValueError):self.service.handle('stop',{})

    def test_one_play_request_launches_while_protocol_input_remains_open(self):
        from portable_support import write_json
        # Original subprocess fixture: attempts to read stdin before announcing
        # launch. A worker must see EOF, never inherit the UI command pipe.
        marker=self.root/'launched.txt';release=self.root/'exit.txt'
        child=self.root/'original-launch-fixture.py'
        child.write_text('''import pathlib,sys,time
print('Verifying the complete disc, including audio tracks…',flush=True)
assert sys.stdin.read(1)=='', 'worker inherited launcher protocol input'
pathlib.Path(sys.argv[1]).write_text('launched')
print('Runtime started (PID 42). Log: original fixture',flush=True)
while not pathlib.Path(sys.argv[2]).exists():time.sleep(.01)
''',encoding='utf-8')
        write_json(self.layout.state_path,dict(schema=1,disc='original-fixture.cue',prepared_version='0.2.0',root=str(self.root),prepared_tools=self.layout.tool_fingerprint()))
        entry=self.root/'service-entry.py'
        entry.write_text('''import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
from linux_support import LinuxLayout
from launcher_service import serve
from portable_support import run as real_run
layout=LinuxLayout(Path(sys.argv[2]));layout.app=Path(sys.argv[3])
def launch(command,cwd,env,progress):
    assert '-u' in command
    real_run([sys.executable,'-u',sys.argv[4],sys.argv[5],sys.argv[6]],cwd,env,progress)
with patch('portable_launcher.reusable_runtime',return_value=True),patch('portable_launcher.repair_portable_saves'),patch('portable_launcher.run',side_effect=launch):
    serve(layout,testing=True)
''',encoding='utf-8')
        proc=subprocess.Popen([sys.executable,'-I',str(entry),str(ROOT/'tools'),str(self.root),str(ROOT),str(child),str(marker),str(release)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        import queue,time
        messages=queue.Queue()
        reader=threading.Thread(target=lambda:[messages.put(json.loads(line)) for line in proc.stdout],daemon=True);reader.start()
        seen=[]
        try:
            proc.stdin.write(json.dumps(dict(id=1,command='play'))+'\n');proc.stdin.flush()
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                try:value=messages.get(timeout=.1)
                except queue.Empty:continue
                seen.append(value)
                if value.get('event')=='state' and value['payload']['phase']=='running':break
            self.assertTrue(marker.exists(),'Play waited for another UI command instead of starting the child')
            self.assertTrue(any(v.get('event')=='state' and v['payload']['phase']=='running' for v in seen),seen)
            self.assertTrue(any(v.get('event')=='state' and v['payload']['title']=='Verifying your disc' for v in seen),seen)
        finally:
            release.write_text('close fixture')
            if proc.poll() is None:
                proc.stdin.close()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            reader.join(timeout=2);proc.stdout.close();proc.stderr.close()

if __name__=='__main__':unittest.main()
