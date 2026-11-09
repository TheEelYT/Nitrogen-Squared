"""Original portable launcher; all writable state is beside launcher.exe."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from portable_support import Layout, beneath, bootstrap, run, sha256, write_json
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
        if process and process.poll() is None:
            if os.name=="nt":
                subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],capture_output=True,
                               creationflags=subprocess.CREATE_NO_WINDOW,timeout=15)
            else:
                import signal
                try: os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError: pass

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
        if not target.exists():
            run([git,"init",str(target)],self.layout.root,env,self)
            run([git,"-C",str(target),"remote","add","origin",FRAMEWORK_URL],self.layout.root,env,self)
            run([git,"-C",str(target),"config","core.longpaths","true"],self.layout.root,env,self)
        result=subprocess.run([git,"-C",str(target),"rev-parse","HEAD"],env=env,capture_output=True,text=True,
                              creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
        if result.returncode:
            run([git,"-C",str(target),"fetch","--depth","1","origin",FRAMEWORK_REV],self.layout.root,env,self)
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
        self("Game running. Close the game window to return here.")
        run(self.layout.command("run_runtime.py","--work-dir",self.layout.work,
                                 "--save-dir",self.layout.local/"saves"),self.layout.root,env,self)

    def action(self,selected=None,play=True,assets=False,import_only=False):
        self.cancel.clear()
        self.layout.writable()
        with (self.layout.local/"setup.log").open("a",encoding="utf-8") as self.log:
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


class Application:
    def __init__(self,layout,launcher_pid=0,*,testing=False):
        import tkinter as tk
        from tkinter import ttk
        self.tk=tk
        self.layout=layout
        self.launcher_pid=launcher_pid
        self.events=queue.Queue()
        self.backend=Backend(layout,lambda kind,text:self.events.put((kind,text)))
        self.busy=False
        self.recovery=(layout.local/"update-state.json").exists()
        result_path=layout.local/"last-update-result.json"
        update_result=json.loads(result_path.read_text()) if result_path.is_file() else None
        if result_path.is_file():result_path.unlink()
        from launcher_presentation import read_release_cache, release_list
        from launcher_ui import LauncherView
        self.window=tk.Tk()
        self.window.title("Nitrogen Squared")
        width=min(1180,max(960,self.window.winfo_screenwidth()-100))
        height=min(720,max(620,self.window.winfo_screenheight()-100))
        self.window.geometry(f"{width}x{height}")
        self.window.minsize(960,620)
        self.stage_percent=None
        self.status=tk.StringVar(value="Ready to play" if layout.state().get("disc") else "Choose your game disc")
        self.detail=tk.StringVar(value="Your game, settings and saves stay in this folder." if layout.state().get("disc") else "Select your supported USA CUE/BIN to get started.")
        self.releases=release_list(layout,read_release_cache(layout.local))
        self.view=LauncherView(self)
        self.window.protocol("WM_DELETE_WINDOW",self.close)
        self.window.after(100,self.poll)
        if self.recovery:
            self.status.set("Update recovery")
            self.detail.set("Restore the previous launcher version before playing. Your game files and saves are kept.")
        elif update_result and not update_result.get("success"):
            self.status.set("Previous version restored")
            self.detail.set(update_result.get("error","Details are in .local/update.log"))
        if not testing and not self.recovery:self.window.after(300,self.load_history)

    def activity(self,value):
        self.busy=value
        self.stage_percent=None
        self.view.set_busy(value)

    def play(self):
        if not self.layout.state().get("disc"):
            self.choose();return
        self.activity(True);self.status.set("Starting game…")
        threading.Thread(target=self.backend.action,daemon=False).start()

    def choose(self,play=True):
        from tkinter import filedialog
        selected=filedialog.askopenfilename(parent=self.window,title="Select your N2O CUE sheet",filetypes=[("CUE sheet (recommended)","*.cue"),("BIN image with matching CUE","*.bin")])
        if selected:
            self.activity(True);self.status.set("Verifying and preparing your game…" if play else "Verifying your disc…")
            threading.Thread(target=self.backend.action,args=(Path(selected),),kwargs=dict(play=play,import_only=not play),daemon=False).start()

    def assets(self):
        folder=self.layout.local/"game"
        if folder.is_dir():

            if os.name=="nt": os.startfile(str(folder))
            else: subprocess.Popen(["xdg-open",str(folder)])
            return
        self.activity(True);self.status.set("Extracting asset folders…")
        self.detail.set("Original assets and music will be saved in .local/game. The game still uses the original disc.")
        threading.Thread(target=self.backend.action,kwargs=dict(assets=True),daemon=False).start()

    def stop(self):
        self.stop_button.configure(state="disabled")
        self.status.set("Stopping; completed files and saves will be kept…")
        threading.Thread(target=self.backend.stop,daemon=True).start()

    def check_update(self):
        self.backend.cancel.clear()
        self.activity(True);self.status.set("Checking for updates…")
        def check():
            try:
                release=latest_release(self.layout.version,self.layout.asset_name)
                if self.backend.cancel.is_set():raise RuntimeError("Update check stopped")
                self.events.put(("update",release))
            except Exception as e:self.events.put(("update-error",str(e)))
        threading.Thread(target=check,daemon=False).start()

    def restore(self):
        from tkinter import messagebox
        if messagebox.askyesno("Restore previous version","Restore the previous launcher files? Your game files and saves will be kept.",parent=self.window):
            start_updater(self.layout,None,self.launcher_pid)
            self.window.destroy()

    def poll(self):
        from tkinter import messagebox
        try:
            while True:
                kind,text=self.events.get_nowait()
                if kind=="progress":
                    from launcher_presentation import progress_summary
                    summary=progress_summary(text)
                    if summary:
                        title,detail,self.stage_percent=summary
                        self.status.set(title);self.detail.set(detail)
                        self.view.refresh_status()
                        if title=="Game running":self.stop_button.configure(state="disabled")
                elif kind in ("done","error"):
                    self.activity(False)
                    self.status.set(text if kind=="done" else "Setup stopped" if self.backend.cancel.is_set() else "Something went wrong")
                    if kind=="error":self.detail.set(text);self.show_error(text)
                    self.view.reload_options();self.view.refresh_status()
                elif kind=="history":
                    from launcher_presentation import release_list
                    self.releases=release_list(self.layout,text);self.view.update_releases()
                elif kind=="history-error":
                    pass # Cached/bundled notes remain usable offline.
                elif kind=="update-error":
                    self.activity(False);self.status.set("Could not check for updates. You can still play.")
                    self.detail.set(text)
                elif kind=="update":
                    self.activity(False)
                    if not text:self.status.set("You have the latest release.")
                    elif messagebox.askyesno("Update available","Install Nitrogen Squared "+text["version"]+"? The launcher will restart. Your local game files and saves will be kept.",parent=self.window):
                        self.activity(True);self.status.set("Downloading update…")
                        def stage(release=text):
                            try:
                                staged=stage_release(self.layout,release,self.backend)
                                if self.backend.cancel.is_set():raise RuntimeError("Update stopped. Downloaded files were kept.")
                                self.events.put(("staged",staged))
                            except Exception as e:self.events.put(("error",str(e)))
                        self.backend.cancel.clear()
                        threading.Thread(target=stage,daemon=False).start()
                    else:self.status.set("Ready to play.")
                elif kind=="staged":
                    start_updater(self.layout,text,self.launcher_pid)
                    self.window.destroy();return
        except queue.Empty:pass
        self.window.after(100,self.poll)

    def load_history(self):
        def fetch():
            from launcher_presentation import fetch_release_history
            try:self.events.put(("history",fetch_release_history(self.layout.local)))
            except (OSError,ValueError) as e:self.events.put(("history-error",str(e)))
        threading.Thread(target=fetch,daemon=True).start()

    def show_error(self,text):
        from tkinter import messagebox
        messagebox.showerror("Nitrogen Squared",text+"\n\nDetails: .local/setup.log",parent=self.window)

    def open_path(self,path):
        if os.name=="nt":os.startfile(str(path))
        else:subprocess.Popen(["xdg-open",str(path)])

    def open_folder(self,name):
        if name not in ("saves","game"):raise ValueError("Unsupported launcher folder")
        path=self.layout.local/name;path.mkdir(parents=True,exist_ok=True);self.open_path(path)

    def open_local_file(self,name):
        if name not in ("setup.log","update.log"):raise ValueError("Unsupported launcher log")
        path=self.layout.local/name
        if path.is_file():self.open_path(path)
        else:self.status.set("No log yet");self.detail.set("A log will appear after setup or an update.")

    def open_runtime_file(self,name):
        from tkinter import messagebox
        if name not in ("keybinds.ini","input.ini"):raise ValueError("Unsupported input profile")
        try:
            record=json.loads((self.layout.work/"runtime-build.json").read_text(encoding="utf-8"))
            path=Path(record["executable"]).resolve().parent/name
            if not path.is_relative_to(self.layout.work.resolve()) or not path.is_file():raise ValueError("No input profile")
            self.open_path(path)
        except (OSError,ValueError,KeyError):
            messagebox.showinfo("Controls","Launch the game once to create its input profiles. Existing custom bindings are kept.",parent=self.window)

    def open_url(self,url):
        import webbrowser
        allowed=("https://github.com/TheEelYT/Nitrogen-Squared", "https://github.com/TheEelYT/Nitrogen-Squared/releases")
        if url not in allowed:raise ValueError("Unsupported project link")
        webbrowser.open(url)

    def change_accent(self,name):
        if self.busy or self.recovery:return
        from launcher_presentation import set_accent
        from launcher_ui import LauncherView
        page,tab=self.view.page,self.view.tab
        set_accent(self.layout.local,name)
        self.view.destroy();self.view=LauncherView(self)
        self.view.open_settings(tab,show=False);self.view.show_page(page)

    def close(self):
        from tkinter import messagebox
        if self.busy:
            messagebox.showinfo("Nitrogen Squared","Stop the current operation, or close the game, before closing the launcher.",parent=self.window)
        else:self.window.destroy()


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
    for key,pattern in ((("TCL_LIBRARY","tcl8.*"),("TK_LIBRARY","tk8.*")) if os.name=="nt" else ()):
        candidates=sorted((layout.python.parent/"tcl").glob(pattern))
        if len(candidates)!=1:raise RuntimeError("The bundled Tcl/Tk runtime is incomplete")
        os.environ[key]=str(candidates[0])
    app=Application(layout,args.launcher_pid,testing=args.self_test)
    if args.self_test:
        app.window.update()
        ui_report=app.view.smoke()
        if os.name=="nt": Path(sys.executable).resolve().relative_to((layout.root/"support/python").resolve())
        report=dict(version=layout.version,python=str(sys.executable),storage=str(layout.local),
                    tkinter=True,asset_tools=bool(app.assets_button.winfo_exists()),
                    first_run=not bool(layout.state().get("disc")),status=app.status.get(),launcher_ui=ui_report)
        if not args.report:raise ValueError("Self-test needs a report path")
        args.report.resolve().relative_to(layout.local.resolve())
        write_json(args.report,report)
        app.window.destroy()
    else:app.window.mainloop()
    lock.close()


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
