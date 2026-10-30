"""Original portable-package fixtures; no disc or generated game code."""
import hashlib
import io
import json
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from portable_support import Layout,beneath,download,extract_zip,relative_path,sha256,write_json
from portable_update import apply_update,owned_path,read_manifest,rollback,verify_package,version_tuple
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
        self.assertEqual(env["CMAKE_BUILD_PARALLEL_LEVEL"],"2")
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
