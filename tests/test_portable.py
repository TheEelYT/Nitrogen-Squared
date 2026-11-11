"""Original portable-package fixtures; no disc or generated game code."""
import hashlib
import io
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from portable_support import ASSET_NAME,LINUX_ASSET_NAME,REPOSITORY,Layout,beneath,download,extract_zip,relative_path,sha256,write_json,probe,run,prepare_sdl
from portable_update import apply_update,latest_release,stage_release,start_updater,owned_path,read_manifest,rollback,verify_package,version_tuple
from portable_launcher import Backend,select_cue
from test_disc import fixture


def package(root,version,extra=None):
    files={"launcher.exe":b"original bootstrap fixture", "support/python/python.exe":b"original interpreter placeholder",
           "app/VERSION":version.encode(),"app/source.py":b"original source"}
    files.update(extra or {})
    for name,data in files.items():
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    write_json(root/"release-manifest.json",dict(schema=1,platform="windows-x86_64",version=version,
               files={name:dict(size=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in files.items()}))
    return files


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=Path(self.temp.name).resolve()
        self.root=self.base/"Nitrogen-Squared"
        self.root.mkdir()
        self.layout=Layout(self.root)

    def tearDown(self):self.temp.cleanup()

    def test_query_timeout_releases_process_and_identifies_the_command(self):
        seen=[];processes=[]
        class Progress:
            def __call__(self,line):seen.append(line)
            def set_process(self,process):processes.append(process)
        command=[sys.executable,'-u','-c','import time; time.sleep(20)']
        with self.assertRaisesRegex(RuntimeError,'Setup query timed out.*time.sleep'):
            probe(command,self.root,os.environ.copy(),Progress(),timeout=.2)
        self.assertIsNone(processes[-1])
        self.assertIsNotNone(processes[0].poll())
        self.assertTrue(any(line.startswith('Command: ') for line in seen))

    def test_stop_cancels_a_tracked_revision_query(self):
        import threading
        ready=threading.Event();errors=[]
        backend=Backend(self.layout)
        original_tracker=backend.set_process
        def tracker(process):
            original_tracker(process)
            if process:ready.set()
        backend.set_process=tracker
        def query():
            try:probe([sys.executable,'-u','-c','import time; time.sleep(20)'],self.root,os.environ.copy(),backend)
            except Exception as error:errors.append(error)
        thread=threading.Thread(target=query,daemon=True);thread.start()
        self.assertTrue(ready.wait(3))
        backend.stop();thread.join(timeout=5)
        self.assertFalse(thread.is_alive(),'Stop left the revision query running')
        self.assertIsNone(backend.process)
        self.assertTrue(any('Stopped.' in str(error) for error in errors))

    def test_sdl_and_framework_revision_checks_use_the_tracked_query(self):
        from build_recompiler import FRAMEWORK_REV
        self.layout.app.mkdir(parents=True)
        (self.layout.app/'configs').mkdir()
        revision='a'*40
        write_json(self.layout.app/'configs/runtime_inputs.json',dict(sdl_revision=revision))
        (self.layout.local/'SDL3-source/.git').mkdir(parents=True)
        (self.layout.framework/'.git').mkdir(parents=True)
        env=self.layout.environment();backend=Backend(self.layout)
        with patch('portable_support.probe',return_value=subprocess.CompletedProcess([],0,revision+'\n','')) as query:
            prepare_sdl(self.layout,env,self.layout.git,backend)
        self.assertEqual(query.call_args.args[0][-2:],['rev-parse','HEAD'])
        self.assertIs(query.call_args.args[3],backend)
        with patch('portable_launcher.probe',return_value=subprocess.CompletedProcess([],0,FRAMEWORK_REV+'\n','')) as query:
            backend.ensure_framework(env)
        self.assertIs(query.call_args.args[3],backend)

    def test_command_failure_names_the_failing_command(self):
        seen=[]
        with self.assertRaisesRegex(RuntimeError,'Preparation command failed.*original fixture'):
            run([sys.executable,'-c','import sys; print("original fixture"); sys.exit(7)'],self.root,os.environ.copy(),seen.append)
        self.assertIn('original fixture',seen)

    def _original_dependency(self):
        git=shutil.which('git');source=self.base/'original dependency';source.mkdir()
        hooks=self.base/'empty hooks';hooks.mkdir()
        def command(*args):
            return subprocess.check_output([git,*map(str,args)],stderr=subprocess.STDOUT,text=True).strip()
        command('init',source)
        (source/'original.txt').write_text('original dependency fixture\n',encoding='utf-8')
        command('-C',source,'add','original.txt')
        command('-C',source,'-c','user.name=Original Fixture','-c','user.email=fixture@example.invalid',
                '-c','commit.gpgsign=false','-c','core.hooksPath='+hooks.as_posix(),'commit','-m','Original fixture')
        revision=command('-C',source,'rev-parse','HEAD')
        return git,source,revision,command

    @unittest.skipUnless(shutil.which('git'),'Git required for dependency setup integration')
    def test_actual_git_dependency_checkout_resumes_and_preserves_other_revisions(self):
        git,source,revision,command=self._original_dependency()
        sdl=self.layout.local/'SDL3-source';command('init',sdl)
        command('-C',sdl,'remote','add','origin',source.as_uri())
        definition=self.layout.app/'configs/runtime_inputs.json'
        write_json(definition,dict(sdl_revision=revision))
        backend=Backend(self.layout);env=self.layout.environment()
        with patch('portable_support.SDL_SOURCE_URL',source.as_uri()):
            prepare_sdl(self.layout,env,git,backend)
        self.assertEqual(command('-C',sdl,'rev-parse','HEAD'),revision)
        self.assertEqual((sdl/'original.txt').read_text(),'original dependency fixture\n')
        # Resume uses the existing pinned HEAD without another fetch/checkout.
        with patch('portable_support.run',side_effect=AssertionError('Unexpected repeat setup command')):
            prepare_sdl(self.layout,env,git,backend)
        write_json(definition,dict(sdl_revision='0'*40))
        with self.assertRaisesRegex(ValueError,'another revision; it was preserved'):
            prepare_sdl(self.layout,env,git,backend)
        self.assertEqual(command('-C',sdl,'rev-parse','HEAD'),revision)

    @unittest.skipUnless(shutil.which('git'),'Git required for dependency setup integration')
    def test_interrupted_sdl_and_framework_setup_repair_missing_origin(self):
        git,source,revision,command=self._original_dependency()
        for component in ('SDL','framework'):
            for interrupted in ('after-init','empty-directory','new-directory'):
                with self.subTest(component=component,interrupted=interrupted):
                    layout=Layout(self.base/(component+' '+interrupted));layout.writable()
                    target=layout.local/'SDL3-source' if component=='SDL' else layout.framework
                    if interrupted=='after-init':command('init',target)
                    elif interrupted=='empty-directory':target.mkdir()
                    write_json(layout.app/'configs/runtime_inputs.json',dict(sdl_revision=revision))
                    private=layout.local/'saves/keep.txt';private.parent.mkdir();private.write_bytes(b'original private fixture')
                    backend=Backend(layout);env=layout.environment()
                    with patch('portable_support.SDL_SOURCE_URL',source.as_uri()),patch('build_recompiler.FRAMEWORK_URL',source.as_uri()),patch('build_recompiler.FRAMEWORK_REV',revision),patch.object(Layout,'git',property(lambda _:git)):
                        if component=='SDL':prepare_sdl(layout,env,git,backend)
                        else:backend.ensure_framework(env)
                        # The recovered source is reusable, with no new mutation.
                        with patch('portable_support.run',side_effect=AssertionError('Repeated source setup')),patch('portable_launcher.run',side_effect=AssertionError('Repeated framework setup')):
                            if component=='SDL':prepare_sdl(layout,env,git,backend)
                            else:backend.ensure_framework(env)
                    self.assertEqual(command('-C',target,'rev-parse','HEAD'),revision)
                    self.assertEqual(command('-C',target,'remote','get-url','origin'),source.as_uri())
                    self.assertEqual(private.read_bytes(),b'original private fixture')
                    if component=='framework':self.assertEqual(command('-C',target,'config','--get','core.longpaths'),'true')

    @unittest.skipUnless(shutil.which('git'),'Git required for dependency setup integration')
    def test_interrupted_setup_preserves_a_different_existing_origin(self):
        git,source,revision,command=self._original_dependency()
        for component in ('SDL','framework'):
            with self.subTest(component=component):
                layout=Layout(self.base/component);layout.writable()
                target=layout.local/'SDL3-source' if component=='SDL' else layout.framework
                command('init',target);other=source.as_uri()+'/different'
                command('-C',target,'remote','add','origin',other)
                private=target/'keep.txt';private.write_bytes(b'existing source fixture')
                write_json(layout.app/'configs/runtime_inputs.json',dict(sdl_revision=revision))
                backend=Backend(layout);env=layout.environment()
                with patch('portable_support.SDL_SOURCE_URL',source.as_uri()),patch('build_recompiler.FRAMEWORK_URL',source.as_uri()),patch('build_recompiler.FRAMEWORK_REV',revision),patch.object(Layout,'git',property(lambda _:git)):
                    with self.assertRaisesRegex(ValueError,'another origin URL; it was preserved'):
                        if component=='SDL':prepare_sdl(layout,env,git,backend)
                        else:backend.ensure_framework(env)
                self.assertEqual(command('-C',target,'remote','get-url','origin'),other)
                self.assertEqual(private.read_bytes(),b'existing source fixture')

    def test_release_discovery_prefers_combined_checksums_and_accepts_legacy(self):
        prefix=f"https://github.com/{REPOSITORY}/releases/download/v0.1.1/"
        for name in [ASSET_NAME,LINUX_ASSET_NAME]:
            for combined in [False,True]:
                names=[name,name+".sha256"]+(["SHA256SUMS.txt"] if combined else [])
                value=dict(tag_name="v0.1.1",assets=[dict(name=n,browser_download_url=prefix+n) for n in names])
                with patch("portable_update.api_json",return_value=value):
                    release=latest_release("0.1.0",name)
                expected="SHA256SUMS.txt" if combined else name+".sha256"
                self.assertEqual(release["checksum"],prefix+expected)
                self.assertEqual(release["checksum_format"],"sums" if combined else "legacy")
                value["assets"][-1]["browser_download_url"]="https://example.invalid/redirect"
                with patch("portable_update.api_json",return_value=value),self.assertRaises(ValueError):
                    latest_release("0.1.0",name)

    def test_checksum_formats_stage_verified_package_without_installing(self):
        old=package(self.root,"0.1.0")
        card=self.root/".local/saves/card.mcd";card.parent.mkdir(parents=True);card.write_bytes(b"preserved card")
        source=self.base/"new/Nitrogen-Squared";package(source,"0.1.1")
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,"w") as archive:
            for path in source.rglob("*"):
                if path.is_file():archive.writestr("Nitrogen-Squared/"+path.relative_to(source).as_posix(),path.read_bytes())
        data=buffer.getvalue();digest=hashlib.sha256(data).hexdigest()
        for fmt in ["legacy","sums"]:
            checksum=(digest+"  "+ASSET_NAME+"\n").encode()
            if fmt=="sums":checksum+=("a"*64+"  "+LINUX_ASSET_NAME+"\n").encode()
            def open_url(url,*args,**kw):
                return io.BytesIO(checksum if url=="checksum" else data)
            release=dict(version="0.1.1",url="https://example.invalid/archive",checksum="checksum",checksum_format=fmt,digest="sha256:"+digest)
            with patch("urllib.request.urlopen",side_effect=open_url):
                staged=stage_release(self.layout,release,lambda _:None)
            self.assertEqual(verify_package(staged)["version"],"0.1.1")
            for name,content in old.items():self.assertEqual((self.root/name).read_bytes(),content)
            self.assertEqual(card.read_bytes(),b"preserved card")

    def test_bad_combined_checksums_stop_before_package_download(self):
        valid=("a"*64+"  "+ASSET_NAME+"\n").encode()
        for checksum,digest in [(valid+valid,None),(b"x"*65537,None),
                                (("b"*64+"  "+LINUX_ASSET_NAME+"\n").encode(),None),
                                (valid,"sha256:"+"b"*64)]:
            release=dict(version="0.1.1",url="https://example.invalid/archive",checksum="checksum",checksum_format="sums",digest=digest)
            with patch("urllib.request.urlopen",return_value=io.BytesIO(checksum)),patch("portable_update.download") as fetch,self.assertRaises(ValueError):
                stage_release(self.layout,release)
            fetch.assert_not_called()

    def test_copied_updaters_import_without_the_application_tree(self):
        from linux_support import LinuxLayout
        package(self.root,"0.1.0")
        for layout in [self.layout,LinuxLayout(self.root)]:
            with self.subTest(platform=layout.platform):
                with patch("subprocess.Popen") as launch:
                    start_updater(layout,None,0)
                command=launch.call_args.args[0]
                script_index=command.index("-B")+1
                # Run the actual copied script with an isolated working folder
                # and no inherited application search path. --help imports the
                # complete runner without applying an update or rollback.
                command=[sys.executable]+command[1:script_index+1]+["--help"]
                env=dict(os.environ)
                env.pop("PYTHONPATH",None);env.pop("PYTHONHOME",None)
                result=subprocess.run(command,cwd=self.base,env=env,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn("--rollback",result.stdout)

    def test_paths_are_contained_and_windows_reserved_names_fail(self):
        for path in ["../saves","/outside","a/../b","a\\b","C:/x","a:b","a//b","a/CON.txt","aux","x.","x ","a/./b","a\x00b","x?y"]:
            with self.subTest(path=path),self.assertRaises(ValueError):relative_path(path)
        self.assertEqual(relative_path("app/configs/source.json"),"app/configs/source.json")
        self.assertEqual(beneath(self.root,".local/saves"),self.root/".local/saves")

    def test_release_cannot_own_user_data_or_arbitrary_executables(self):
        for name in [".local/saves/card.mcd","app/.local/game.c","app/generated/out.c","support/game.exe","other.exe","saves/card.mcd"]:
            with self.subTest(name=name),self.assertRaises(ValueError):owned_path(name)

    def test_zip_preflight_does_not_write_partial_output(self):
        z=self.base/"bad.zip"
        for bad in ["../outside","C:/outside","app/a:b","app/CON","a\\b"]:
            with zipfile.ZipFile(z,"w") as f:
                f.writestr("valid.txt","good")
                info=zipfile.ZipInfo("placeholder");info.filename=bad
                f.writestr(info,"bad")
            out=self.base/"out"
            with self.assertRaises(ValueError):extract_zip(z,out)
            self.assertFalse(out.exists())

    def test_zip_rejects_case_collisions_and_symbolic_links(self):
        z=self.base/"bad.zip"
        with zipfile.ZipFile(z,"w") as f:f.writestr("app/A.txt","a");f.writestr("app/a.txt","b")
        with self.assertRaises(ValueError):extract_zip(z,self.base/"out")
        link=zipfile.ZipInfo("link");link.create_system=3;link.external_attr=0o120777<<16
        with zipfile.ZipFile(z,"w") as f:f.writestr(link,"elsewhere")
        with self.assertRaises(ValueError):extract_zip(z,self.base/"out")

    def test_zip_strip_root_requires_one_directory(self):
        z=self.base/"tools.zip"
        with zipfile.ZipFile(z,"w") as f:f.writestr("tool/bin/compiler.exe",b"original placeholder")
        extract_zip(z,self.base/"tool",strip_root=True)
        self.assertTrue((self.base/"tool/bin/compiler.exe").is_file())
        with zipfile.ZipFile(z,"w") as f:f.writestr("one/file","a");f.writestr("two/file","b")
        with self.assertRaises(ValueError):extract_zip(z,self.base/"bad",strip_root=True)

    def test_zip_expansion_limit_is_enforced_before_output(self):
        z=self.base/"tools.zip"
        with zipfile.ZipFile(z,"w") as f:f.writestr("file","123456")
        with patch("portable_support.MAX_EXPANDED_BYTES",5),self.assertRaises(ValueError):extract_zip(z,self.base/"out")
        self.assertFalse((self.base/"out").exists())

    def test_download_digest_failure_never_installs_bad_content(self):
        path=self.base/"download.zip"
        with patch("urllib.request.urlopen",return_value=io.BytesIO(b"bad")),self.assertRaises(ValueError):
            download("https://example.invalid/original",path,"0"*64,lambda _:None)
        self.assertFalse(path.exists());self.assertFalse(path.with_name(path.name+".part").exists())

    def test_download_pinned_cache_and_size_limit(self):
        path=self.base/"tool.zip";path.write_bytes(b"original")
        with patch("urllib.request.urlopen") as url:
            download("https://example.invalid/original",path,sha256(path));url.assert_not_called()
        path.unlink()
        with patch("urllib.request.urlopen",return_value=io.BytesIO(b"tool")),self.assertRaises(ValueError):
            download("https://example.invalid/original",path,hashlib.sha256(b"tool").hexdigest(),maximum=3)
        self.assertFalse(path.exists())

    def test_complete_package_checks_content_and_exact_inventory(self):
        package(self.root,"0.0.1")
        self.assertEqual(verify_package(self.root)["version"],"0.0.1")
        (self.root/"app/extra.txt").write_text("unreviewed")
        with self.assertRaises(ValueError):verify_package(self.root)
        (self.root/"app/extra.txt").unlink();(self.root/"app/source.py").write_text("changed")
        with self.assertRaises(ValueError):verify_package(self.root)

    def test_manifest_rejects_duplicate_windows_names_and_invalid_hash(self):
        package(self.root,"0.0.1")
        p=self.root/"release-manifest.json";m=json.loads(p.read_text())
        m["files"]["APP/VERSION"]=m["files"]["app/VERSION"]
        write_json(p,m)
        with self.assertRaises(ValueError):read_manifest(self.root)
        package(self.root,"0.0.1")
        m=json.loads(p.read_text());m["files"]["app/VERSION"]["sha256"]="bad";write_json(p,m)
        with self.assertRaises(ValueError):read_manifest(self.root)

    def test_update_preserves_saves_cache_unknown_files_and_changed_owned_backup(self):
        package(self.root,"0.0.1",{"app/obsolete.txt":b"obsolete"})
        (self.root/"app/source.py").write_bytes(b"local edit")
        for name in [".local/saves/card.mcd",".local/runtime-dev/generated.c","notes.txt"]:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"private unchanged")
        stage=self.root/".local/updates/staged"
        new=package(stage,"0.0.2",{"app/new.txt":b"new"})
        apply_update(self.layout,stage)
        self.assertEqual(read_manifest(self.root)["version"],"0.0.2")
        for name,data in new.items():self.assertEqual((self.root/name).read_bytes(),data)
        for name in [".local/saves/card.mcd",".local/runtime-dev/generated.c","notes.txt"]:
            self.assertEqual((self.root/name).read_bytes(),b"private unchanged")
        self.assertFalse((self.root/"app/obsolete.txt").exists())
        backups=list((self.root/".local/updates").glob("backup-*/app/source.py"))
        self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),b"local edit")

    def test_failed_install_restores_the_complete_previous_package(self):
        old=package(self.root,"0.0.1")
        stage=self.root/".local/updates/staged";package(stage,"0.0.2",{"app/new.txt":b"new"})
        import os
        original=os.replace;failed=False
        def replace(source,target):
            nonlocal failed
            if Path(target)==self.root/"launcher.exe" and not failed:
                failed=True;raise OSError("original simulated failure")
            return original(source,target)
        with patch("portable_update.os.replace",side_effect=replace),self.assertRaises(OSError):
            apply_update(self.layout,stage)
        for name,data in old.items():self.assertEqual((self.root/name).read_bytes(),data)
        self.assertEqual(read_manifest(self.root)["version"],"0.0.1")
        self.assertFalse((self.root/"app/new.txt").exists())
        self.assertFalse((self.root/".local/update-state.json").exists())

    def test_update_refuses_collision_downgrade_and_external_staging(self):
        package(self.root,"0.0.2")
        stage=self.root/".local/updates/staged";package(stage,"0.0.3",{"app/new.txt":b"new"})
        (self.root/"app/new.txt").write_bytes(b"unowned")
        with self.assertRaises(ValueError):apply_update(self.layout,stage)
        self.assertEqual((self.root/"app/new.txt").read_bytes(),b"unowned")
        package(stage,"0.0.1")
        (stage/"app/new.txt").unlink()
        with self.assertRaises(ValueError):apply_update(self.layout,stage)
        outside=self.base/"outside";package(outside,"0.0.3")
        with self.assertRaises(ValueError):apply_update(self.layout,outside)
        self.assertEqual(read_manifest(self.root)["version"],"0.0.2")

    def test_environment_keeps_all_preparation_and_runtime_paths_portable(self):
        env=self.layout.environment()
        for name in ("TEMP","TMP","PSX_SDL3_SOURCE_DIR"):
            Path(env[name]).resolve().relative_to(self.root)
        self.assertEqual(env["CC"],"x86_64-w64-mingw32-clang.exe")
        self.assertIn(str(self.layout.tools/"llvm-mingw/bin"),env["PATH"].split(__import__("os").pathsep))
        from build_policy import build_jobs
        self.assertEqual(env["CMAKE_BUILD_PARALLEL_LEVEL"],str(build_jobs()))
        self.assertEqual(self.layout.work,self.root/".local/runtime-dev")
        self.assertNotIn("PYTHONHOME",env);self.assertNotIn("PYTHONPATH",env)

    def test_cue_is_preferred_and_bin_requires_its_matching_sheet(self):
        cue,identity=fixture(self.base)
        self.assertEqual(select_cue(cue),cue.resolve())
        self.assertEqual(select_cue(self.base/"synthetic.bin"),cue.resolve())
        cue.unlink()
        with self.assertRaises(ValueError):select_cue(self.base/"synthetic.bin")

    def test_relocated_import_preserves_extracted_inputs_and_marks_build_stale(self):
        cue,identity=fixture(self.base)
        (self.layout.app/"configs").mkdir(parents=True)
        write_json(self.layout.app/"configs/disc_usa.json",identity)
        backend=Backend(self.layout)
        backend.import_disc(cue)
        manifest=json.loads((self.layout.installation/"installation.json").read_text())
        extracted={p.name:p.read_bytes() for p in (self.layout.installation/"executables").iterdir()}
        write_json(self.layout.state_path,dict(schema=1,disc=str(cue),prepared_version="0.0.1"))
        backend.import_disc(cue)
        self.assertIsNone(self.layout.state()["prepared_version"])
        self.assertEqual(extracted,{p.name:p.read_bytes() for p in (self.layout.installation/"executables").iterdir()})
        self.assertEqual(json.loads((self.layout.installation/"installation.json").read_text()),manifest)

    def test_existing_developer_cache_and_saves_are_preserved_during_portable_migration(self):
        (self.layout.app/"configs").mkdir(parents=True)
        (self.layout.app/"configs/portable_tools.json").write_text('{}')
        (self.layout.work/"build").mkdir(parents=True)
        (self.layout.work/"build/CMakeCache.txt").write_text('CMAKE_HOME_DIRECTORY:INTERNAL=/previous/project\nCMAKE_GENERATOR:INTERNAL=Visual Studio\n')
        (self.layout.work/"saves").mkdir()
        (self.layout.work/"saves/card.mcd").write_bytes(b'original preservation fixture')
        (self.layout.work/"build/settings.toml").write_text('[video]\n')
        Backend(self.layout).align_cache({})
        self.assertEqual((self.layout.local/"saves/card.mcd").read_bytes(),b'original preservation fixture')
        self.assertEqual((self.layout.local/"retained-settings.toml").read_text(),'[video]\n')
        self.assertTrue(list((self.layout.local/"relocated").glob('*/runtime-dev/saves/card.mcd')))
        self.assertFalse(self.layout.work.exists())

    @unittest.skipUnless(shutil.which("cmake"),"CMake required for compiler-path regression")
    def test_windows_compiler_path_survives_generated_cmake_source(self):
        layout=Layout.__new__(Layout)
        layout.tools=PureWindowsPath("B:/Games/Nitrogen-Squared With Spaces/.local/tools")
        layout.python=PureWindowsPath("B:/Games/Nitrogen-Squared With Spaces/support/python/python.exe")
        definitions=dict(arg[2:].split("=",1) for arg in layout.runtime_cmake_args())
        compiler=layout.tools/"llvm-mingw/bin/x86_64-w64-mingw32-windres.exe"
        script=self.base/"CMakeRCCompiler.cmake"
        # Reproduce the compiler-file failure from the user's setup log.
        script.write_text('cmake_minimum_required(VERSION 3.20)\n'
                          'set(CMAKE_RC_COMPILER "'+str(compiler)+'")\n')
        bad=subprocess.run(["cmake","-P",str(script)],capture_output=True,text=True,timeout=10)
        self.assertNotEqual(bad.returncode,0)
        self.assertIn("Invalid character escape",bad.stderr)
        value=definitions["CMAKE_RC_COMPILER"]
        self.assertEqual(value,compiler.as_posix())
        self.assertEqual(definitions["Python3_EXECUTABLE"],layout.python.as_posix())
        script.write_text('cmake_minimum_required(VERSION 3.20)\n'
                          'set(CMAKE_RC_COMPILER "'+value+'")\n'
                          'if(NOT CMAKE_RC_COMPILER STREQUAL "'+compiler.as_posix()+'")\n'
                          '  message(FATAL_ERROR "Compiler path changed")\nendif()\n')
        fixed=subprocess.run(["cmake","-P",str(script)],capture_output=True,text=True,timeout=10)
        self.assertEqual(fixed.returncode,0,fixed.stderr)

    def test_backslash_compiler_cache_repair_keeps_completed_preparation_and_saves(self):
        self.layout.app.mkdir()
        for name in ("runtime-dev/private/prepared.txt","build-recompiler/compiled.txt",
                     "installation/import.txt","saves/card.mcd"):
            p=self.layout.local/name;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(b"original preservation fixture")
        for kind in ("UNINITIALIZED","FILEPATH"):
            with self.subTest(kind=kind):
                build=self.layout.work/"build";build.mkdir()
                (build/"CMakeCache.txt").write_text(
                    'CMAKE_HOME_DIRECTORY:INTERNAL='+self.layout.app.as_posix()+'\n'
                    'CMAKE_GENERATOR:INTERNAL=Ninja\n'
                    'CMAKE_RC_COMPILER:'+kind+'=B:\\Games\\tools\\windres.exe\n')
                (build/"settings.toml").write_text('[video]\n')
                broken=build/"CMakeFiles/4.4.5/CMakeRCCompiler.cmake"
                broken.parent.mkdir(parents=True);broken.write_text('original broken configuration')
                Backend(self.layout).align_cache({})
                self.assertFalse(build.exists())
                self.assertEqual((self.layout.local/"retained-settings.toml").read_text(),'[video]\n')
                for name in ("runtime-dev/private/prepared.txt","build-recompiler/compiled.txt",
                             "installation/import.txt","saves/card.mcd"):
                    self.assertEqual((self.layout.local/name).read_bytes(),b"original preservation fixture")
        self.assertEqual(len(list((self.layout.local/"relocated").glob('*/runtime-build/CMakeCache.txt'))),2)

    def test_forward_slash_compiler_cache_is_reused(self):
        self.layout.app.mkdir()
        build=self.layout.work/"build";build.mkdir(parents=True)
        (build/"CMakeCache.txt").write_text(
            'CMAKE_HOME_DIRECTORY:INTERNAL='+self.layout.app.as_posix()+'\n'
            'CMAKE_GENERATOR:INTERNAL=Ninja\n'
            'CMAKE_RC_COMPILER:FILEPATH=B:/Games/tools/windres.exe\n')
        Backend(self.layout).align_cache({})
        self.assertTrue((build/"CMakeCache.txt").is_file())
        self.assertFalse((self.layout.local/"relocated").exists())

    def test_broken_generated_compiler_file_is_repaired_even_without_bad_cache_value(self):
        self.layout.app.mkdir()
        for has_cache in (False,True):
            with self.subTest(has_cache=has_cache):
                build=self.layout.work/"build";build.mkdir(parents=True)
                if has_cache:
                    (build/"CMakeCache.txt").write_text(
                        'CMAKE_HOME_DIRECTORY:INTERNAL='+self.layout.app.as_posix()+'\n'
                        'CMAKE_GENERATOR:INTERNAL=Ninja\n'
                        'CMAKE_RC_COMPILER:FILEPATH=B:/Games/tools/windres.exe\n')
                compiler=build/"CMakeFiles/4.4.5/CMakeRCCompiler.cmake"
                compiler.parent.mkdir(parents=True)
                compiler.write_text('set(CMAKE_RC_COMPILER "B:\\Games\\tools\\windres.exe")\n')
                Backend(self.layout).align_cache({})
                self.assertFalse(build.exists())
        self.assertEqual(len(list((self.layout.local/"relocated").glob('*/runtime-build/CMakeFiles/*/CMakeRCCompiler.cmake'))),2)

    def test_release_version_comparison_is_numeric(self):
        self.assertGreater(version_tuple("0.0.10"),version_tuple("0.0.9"))
        for version in ["latest","0.0.1-rc1","../1.2.3"]:
            with self.assertRaises(ValueError):version_tuple(version)


if __name__=="__main__":unittest.main()
