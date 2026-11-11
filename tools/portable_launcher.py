"""Original portable launcher; all writable state is beside launcher.exe."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from portable_support import Layout, beneath, bootstrap, ensure_git_origin, probe, run, sha256, stop_process, write_json
from portable_update import latest_release, stage_release, start_updater
from runtime_paths import repair_portable_saves
from runtime_compatibility import build_options, reusable_runtime


def select_cue(selected: Path) -> Path:
    from n2o_disc import parse_cue
    selected=selected.resolve(strict=True)
    if selected.suffix.lower()==".cue":
        return selected
    if selected.suffix.lower()!=".bin":
        raise ValueError("Select the CUE sheet for the supported USA disc")
    matches=[]
    for cue in selected.parent.iterdir():
        if cue.suffix.lower()==".cue" and cue.is_file():
            try:
                image,_=parse_cue(cue)
                if image.resolve()==selected:
                    matches.append(cue)
            except (OSError,ValueError):
                continue
    if len(matches)!=1:
        raise ValueError("Choose the CUE sheet that belongs to this BIN. Keep both files together.")
    return matches[0]


class Backend:
    def __init__(self,layout: Layout,notify=lambda kind,text: None):
        self.layout=layout
        self.notify=notify
        self.cancel=threading.Event()
        self.process=None
        self.log=None

    def __call__(self,text):
        if self.cancel.is_set():
            raise RuntimeError("Stopped. Existing saves and completed preparation files were kept.")
        if self.log:
            self.log.write(text+"\n");self.log.flush()
        self.notify("progress",text)

    def set_process(self,process):
        self.process=process
        if process and self.cancel.is_set():
            self.stop()

    def stop(self):
        self.cancel.set()
        process=self.process
        if process:
            stop_process(process)

    def import_disc(self,selected):
        from n2o_disc import inspect,prepare,digest
        cue=select_cue(selected)
        identity=json.loads((self.layout.app/"configs/disc_usa.json").read_text())
        if self.layout.installation.exists():
            current=inspect(cue,identity,self)
            old=json.loads((self.layout.installation/"installation.json").read_text())
            if old.get("game_id")!=current["game_id"] or old.get("bin_sha256")!=current["bin_sha256"]:
                raise ValueError("The existing portable import has a different identity and was preserved")
            for item in identity["executables"]:
                path=self.layout.installation/"executables"/item["path"]
                if not path.is_file() or path.stat().st_size!=item["size"] or digest(path)!=item["sha256"]:
                    raise ValueError("An extracted input changed; the existing import was preserved")
            write_json(self.layout.installation/"installation.json",current)
        else:
            prepare(cue,self.layout.installation,identity,self)
        state=self.layout.state()
        state.update(schema=1,disc=str(cue),prepared_version=None)
        write_json(self.layout.state_path,state)

    def ensure_framework(self,env):
        from build_recompiler import FRAMEWORK_REV,FRAMEWORK_URL
        target=self.layout.framework
        git=self.layout.git
        if not target.exists() or (target.is_dir() and not any(target.iterdir())):
            run([git,"init",str(target)],self.layout.root,env,self)
        self("Checking framework source revision…")
        result=probe([git,"-C",str(target),"rev-parse","HEAD"],self.layout.root,env,self)
        if result.returncode:
            ensure_git_origin(git,target,FRAMEWORK_URL,self.layout.root,env,self)
            run([git,"-C",str(target),"config","core.longpaths","true"],self.layout.root,env,self)
            self("Downloading framework source…")
            run([git,"-C",str(target),"fetch","--progress","--depth","1","origin",FRAMEWORK_REV],self.layout.root,env,self)
            self("Preparing framework source checkout…")
            run([git,"-C",str(target),"checkout","--detach",FRAMEWORK_REV],self.layout.root,env,self)
        elif result.stdout.strip()!=FRAMEWORK_REV:
            raise ValueError("The preparation framework has another revision and was preserved")

    def align_cache(self,state):
        saves=self.layout.local/"saves"
        legacy=self.layout.work/"saves"
        if legacy.is_dir() and not saves.exists():
            shutil.copytree(legacy,saves)
            self("Existing saves were copied into the portable save folder.")
        cache=self.layout.work/"build/CMakeCache.txt"
        moved=bool(state.get("root") and state["root"]!=str(self.layout.root))
        changed_tools=bool(state.get("prepared_tools") and state["prepared_tools"]!=self.layout.tool_fingerprint())
        incompatible=False
        escaped_compiler=False
        if cache.is_file():
            values=dict(line.split("=",1) for line in cache.read_text(errors="replace").splitlines() if "=" in line and not line.startswith(("#","//")))
            source=values.get("CMAKE_HOME_DIRECTORY:INTERNAL")
            generator=values.get("CMAKE_GENERATOR:INTERNAL")
            incompatible=not source or Path(source).resolve()!=self.layout.app or generator!=("Unix Makefiles" if self.layout.platform=="linux-x86_64" else "Ninja")
            escaped_compiler=any(key.startswith("CMAKE_RC_COMPILER:") and "\\" in value for key,value in values.items())
        for compiler in (self.layout.work/"build/CMakeFiles").glob("*/CMakeRCCompiler.cmake"):
            escaped_compiler |= any(line.startswith("set(CMAKE_RC_COMPILER ") and "\\" in line
                                    for line in compiler.read_text(errors="replace").splitlines())
        if moved or changed_tools or incompatible:
            backup=beneath(self.layout.root,".local/relocated/"+str(time.time_ns()))
            backup.mkdir(parents=True)
            for name in ("runtime-dev","build-recompiler"):
                source=self.layout.local/name
                if source.exists():os.replace(source,backup/name)
            self.retain_runtime_preferences(backup/"runtime-dev/build")
            self("Preparing a fresh compatible build cache; previous files and saves are preserved.")
        elif escaped_compiler:
            # 0.0.17 could leave CMakeRCCompiler.cmake with invalid backslash
            # escapes. Archive only this configuration, keeping completed tools
            # and generated inputs so repair does not repeat their compilation.
            backup=beneath(self.layout.root,".local/relocated/"+str(time.time_ns()))
            backup.mkdir(parents=True)
            os.replace(self.layout.work/"build",backup/"runtime-build")
            self.retain_runtime_preferences(backup/"runtime-build")
            self("Refreshing Windows compiler configuration; completed preparation and saves are preserved.")

    def retain_runtime_preferences(self,build):
        for name in ("settings.toml","keybinds.ini","input.ini"):
            for directory in (build/"Release",build):
                old=directory/name
                if old.is_file():
                    shutil.copy2(old,self.layout.local/("retained-"+name));break

    def restore_runtime_preferences(self,executable):
        for name in ("settings.toml","keybinds.ini","input.ini"):
            retained=self.layout.local/("retained-"+name)
            target=executable.parent/name
            if retained.is_file() and not target.exists():shutil.copy2(retained,target)

    def prepare(self):
        state=self.layout.state()
        if not (self.layout.installation/"installation.json").is_file():
            raise ValueError("Choose your disc before preparing the game")
        env=bootstrap(self.layout,self)
        self.ensure_framework(env)
        self.align_cache(state)
        self("Preparing the game. First compilation can take several minutes…")
        cmake=self.layout.cmake
        command=self.layout.command("build_runtime.py","--installation",self.layout.installation,
                                    "--framework",self.layout.framework,"--recompiler-build",self.layout.local/"build-recompiler",
                                    "--work-dir",self.layout.work,"--save-dir",self.layout.local/"saves","--cmake",cmake,
                                    *("--cmake-arg="+arg for arg in self.layout.runtime_cmake_args()))
        run(command,self.layout.root,env,self)
        receipt=json.loads((self.layout.work/"runtime-build.json").read_text())
        self.restore_runtime_preferences(Path(receipt["executable"]))
        state.update(schema=1,prepared_version=self.layout.version,root=str(self.layout.root),
                     prepared_tools=self.layout.tool_fingerprint())
        write_json(self.layout.state_path,state)
        repair_portable_saves(self.layout)
        return env

    def play(self):
        state=self.layout.state()
        env = self.layout.environment()
        options = build_options(cmake_args=self.layout.runtime_cmake_args(),environment=env)
        if (state.get("prepared_version") is None or state.get("root")!=str(self.layout.root) or state.get("prepared_tools")!=self.layout.tool_fingerprint()
                or not reusable_runtime(self.layout.app,self.layout.work,self.layout.platform,options)):
            env=self.prepare()
        else:
            self("Using your existing compatible game build.")
        repair_portable_saves(self.layout)
        self("Starting game. Verifying your disc before launch…")
        # The child verifies the disc before it creates a game process. Relay
        # those lines immediately; only its actual PID receipt means Running.
        command=self.layout.command("run_runtime.py","--work-dir",self.layout.work,
                                    "--save-dir",self.layout.local/"saves")
        command.insert(1,"-u")
        run(command,self.layout.root,env,self)

    def action(self,selected=None,play=True,assets=False,import_only=False):
        self.layout.writable()
        with (self.layout.local/"setup.log").open("a",encoding="utf-8") as self.log:
            self.log.write("\nSetup session: "+time.strftime("%Y-%m-%d %H:%M:%S %z")+"\n")
            self.log.flush()
            try:
                if selected:
                    self.import_disc(selected)
                message="Ready to play."
                if import_only:
                    message="Game disc verified. Ready to prepare."
                elif assets:
                    from extract_assets import extract
                    extract(self.layout.installation,self.layout.local/"game",progress=self)
                    message="Assets extracted to .local/game. Use Asset folders to open them."
                elif play:
                    self.play()
                else:
                    bootstrap(self.layout,self)
                self.notify("done",message)
            except Exception as e:
                self.log.write("ERROR: "+str(e)+"\n");self.log.flush()
                self.notify("error",str(e))
            finally:
                self.log=None


def instance_lock(layout):
    layout.writable()
    handle=(layout.local/"launcher.lock").open("a+b")
    handle.seek(0);handle.write(b"0");handle.flush();handle.seek(0)
    try:
        if os.name=="nt":
            import msvcrt
            msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except OSError:
        handle.close();raise RuntimeError("Nitrogen Squared is already running from this folder")
    return handle


def main():
    for stream in (sys.stdout,sys.stderr):
        if stream is not None and hasattr(stream,"reconfigure"):
            stream.reconfigure(encoding="utf-8",errors="replace")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--launcher-pid",type=int,default=0)
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--report",type=Path)
    p.add_argument("--bootstrap-tools",action="store_true")
    p.add_argument("--runtime-fixture",action="store_true")
    args=p.parse_args()
    if os.name=="nt": layout=Layout(args.root)
    else:
        from linux_support import LinuxLayout
        layout=LinuxLayout(args.root)
    lock=instance_lock(layout)
    # Repair prepared configurations even when the user only opens the launcher
    # to update, then starts the existing EXE/shortcut directly. No compilation.
    repair_portable_saves(layout)
    if args.bootstrap_tools or args.runtime_fixture:
        backend=Backend(layout,lambda kind,text:print(text,flush=True))
        env=bootstrap(layout,backend)
        backend.ensure_framework(env)
        if args.runtime_fixture:
            run(layout.command("ci_runtime_build.py","--framework",layout.framework,
                               "--work-dir",layout.local/"portable-runtime-fixture",
                               *("--cmake-arg="+arg for arg in layout.runtime_cmake_args())),layout.root,env,backend)
        lock.close();return
    lock.close()
    native=layout.root/("launcher.exe" if os.name=="nt" else "launcher")
    if not native.is_file():raise RuntimeError("Build the Tauri launcher first (see launcher/README.md).")
    command=[str(native)]
    if args.self_test:command += ["--self-test","--report",str(args.report)]
    raise SystemExit(subprocess.call(command,cwd=layout.root))



if __name__=="__main__":
    try:main()
    except Exception as e:
        if os.name=="nt" and not any(flag in sys.argv for flag in ("--self-test","--runtime-fixture","--bootstrap-tools")):
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,str(e),"Nitrogen Squared",0x10)
        else:
            if "--root" in sys.argv:
                try:
                    root=Path(sys.argv[sys.argv.index("--root")+1]).resolve()
                    error=beneath(root,".local/launcher-error.log")
                    error.parent.mkdir(parents=True,exist_ok=True)
                    error.write_text(str(e)+"\n",encoding="utf-8")
                except Exception:pass
            print(str(e),file=sys.stderr)
        raise SystemExit(1)
