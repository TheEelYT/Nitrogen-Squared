"""Build budgets, archive dates and a real Ninja regeneration regression."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_policy import available_threads, build_jobs, normalize_build_timestamps
from portable_support import Layout, run
from linux_support import LinuxLayout
from package_source import archive_file


class BuildPolicyTests(unittest.TestCase):
    def test_desktop_budget_floors_eighty_percent_with_one_worker_minimum(self):
        for count,expected in [(1,1),(2,1),(4,3),(8,6),(12,9),(16,12),(32,25)]:
            with self.subTest(count=count),patch('build_policy.available_threads',return_value=count):
                self.assertEqual(build_jobs({}),expected)
                self.assertEqual(build_jobs({},target='vita'),min(count,2))

    def test_smaller_override_is_respected_and_larger_invalid_or_unlimited_is_capped(self):
        with patch('build_policy.available_threads',return_value=16):
            for value,expected in [('2',2),('4',4),('200',12),('0',12),('-1',12),('bad',12),('',12)]:
                with self.subTest(value=value):self.assertEqual(build_jobs({'CMAKE_BUILD_PARALLEL_LEVEL':value}),expected)
            self.assertEqual(build_jobs({'NITROGEN_BUILD_TARGET':'vita','CMAKE_BUILD_PARALLEL_LEVEL':'12'}),2)

    def test_available_count_uses_process_affinity_and_safe_fallback(self):
        with patch('build_policy.os.process_cpu_count',return_value=6,create=True):self.assertEqual(available_threads(),6)
        with patch('build_policy.os.process_cpu_count',return_value=None,create=True),patch('build_policy.os.sched_getaffinity',return_value={0,1,2},create=True):
            self.assertEqual(available_threads(),3)
        with patch('build_policy.os.process_cpu_count',return_value=None,create=True),patch('build_policy.os.sched_getaffinity',side_effect=OSError,create=True),patch('build_policy.os.cpu_count',return_value=None):
            self.assertEqual(available_threads(),1)

    def test_both_launcher_environments_forward_the_budget(self):
        with tempfile.TemporaryDirectory() as t,patch('build_policy.available_threads',return_value=16),patch.dict(os.environ,{'CMAKE_BUILD_PARALLEL_LEVEL':'100'}):
            for kind in (Layout,LinuxLayout):
                self.assertEqual(kind(Path(t)).environment()['CMAKE_BUILD_PARALLEL_LEVEL'],'12')

    def fixture(self,root):
        (root/'configs').mkdir()
        (root/'configs/runtime_inputs.json').write_text(json.dumps(dict(files=['CMakeLists.txt'],trees=[])))
        (root/'VERSION').write_text('0.2.2\n')
        source=root/'CMakeLists.txt'
        source.write_text('cmake_minimum_required(VERSION 3.20)\nproject(OriginalFixture NONE)\n'
            'add_custom_target(fixture ALL COMMAND "${CMAKE_COMMAND}" -E echo "Compiled original fixture")\n')
        return source

    def test_only_future_reviewed_input_dates_change_and_content_stays_identical(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=self.fixture(root);private=root/'user-save';private.write_bytes(b'keep')
            future=(int(time.time())+6*3600)*10**9
            for p in (source,private):os.utime(p,ns=(future,future))
            before=hashlib.sha256(source.read_bytes()).hexdigest();version_time=(root/'VERSION').stat().st_mtime_ns
            self.assertEqual(normalize_build_timestamps(root,lambda _:None),1)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
            self.assertLess(source.stat().st_mtime_ns,time.time_ns())
            self.assertEqual((root/'VERSION').stat().st_mtime_ns,version_time)
            self.assertEqual(private.stat().st_mtime_ns,future)
            self.assertEqual(normalize_build_timestamps(root,lambda _:None),0)

    def test_archive_date_is_safe_and_executable_permissions_survive(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=root/'launcher';source.write_bytes(b'original fixture');source.chmod(0o755)
            with zipfile.ZipFile(root/'package.zip','w') as archive:archive_file(archive,source,'Nitrogen-Squared/launcher')
            with zipfile.ZipFile(root/'package.zip') as archive:
                info=archive.infolist()[0]
                self.assertEqual(info.date_time,(1980,1,1,0,0,0))
                self.assertEqual(archive.read(info),source.read_bytes())
                if os.name!='nt':self.assertTrue(info.external_attr>>16 & 0o111)

    @unittest.skipUnless(shutil.which('cmake') and shutil.which('ninja'),'CMake and Ninja required')
    def test_real_ninja_future_source_loops_then_same_build_completes_after_repair(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=self.fixture(root);build=root/'build'
            subprocess.run(['cmake','-S',str(root),'-B',str(build),'-G','Ninja'],check=True,capture_output=True)
            future=time.time_ns()+6*3600*10**9;os.utime(source,ns=(future,future))
            lines=[]
            with self.assertRaisesRegex(RuntimeError,'repeated three times'):
                run(['ninja','-C',str(build),'-d','explain'],root,os.environ.copy(),lines.append)
            self.assertEqual(sum('Re-running CMake' in l for l in lines),3)
            self.assertTrue(any('CMakeLists.txt' in l and 'older than' in l for l in lines))
            normalize_build_timestamps(root,lines.append)
            run(['ninja','-C',str(build),'-d','explain'],root,os.environ.copy(),lines.append)
            self.assertIn('Compiled original fixture',lines)
