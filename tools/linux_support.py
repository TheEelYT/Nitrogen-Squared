"""Linux launcher integration. Uses system build tools; all project state is local."""
from pathlib import Path
import os
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from portable_support import Layout, LINUX_ASSET_NAME, beneath, prepare_sdl, sha256
from build_policy import build_jobs

class LinuxLayout(Layout):
    platform = "linux-x86_64"
    asset_name = LINUX_ASSET_NAME
    display_name = "Linux x64"

    def __init__(self, root):
        super().__init__(root)
        self.python = Path(sys.executable).resolve()

    @property
    def git(self): return shutil.which("git") or "git"

    @property
    def cmake(self): return shutil.which("cmake") or "cmake"

    def tool_fingerprint(self):
        from runtime_compatibility import build_options
        options=build_options(cmake_args=self.runtime_cmake_args(),environment=self.environment())
        return hashlib.sha256(json.dumps(options,sort_keys=True).encode()).hexdigest()

    def environment(self):
        env=os.environ.copy()
        for key in ("PYTHONHOME","PYTHONPATH","CMAKE_TOOLCHAIN_FILE","CMAKE_GENERATOR_INSTANCE",
                    "CMAKE_GENERATOR_PLATFORM","CMAKE_GENERATOR_TOOLSET","CC","CXX","RC"):
            env.pop(key,None)
        temp=beneath(self.root,".local/tmp");temp.mkdir(parents=True,exist_ok=True)
        env.update(TMPDIR=str(temp),TEMP=str(temp),TMP=str(temp),
                   CMAKE_GENERATOR="Unix Makefiles",CMAKE_BUILD_PARALLEL_LEVEL=str(build_jobs(env)),
                   PYTHONNOUSERSITE="1",PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1",
                   PSX_SDL3_SOURCE_DIR=str(self.local/"SDL3-source"))
        return env

    def runtime_cmake_args(self):
        return ["-DPython3_EXECUTABLE="+self.python.as_posix(),
                "-DSDL_UNIX_CONSOLE_BUILD=ON", "-DCMAKE_EXPORT_PACKAGE_REGISTRY=OFF",
                "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF"]


def bootstrap_linux(layout, progress=print):
    if sys.platform!="linux" or platform.machine().lower() not in ("x86_64","amd64"):
        raise ValueError("This package requires Linux x86_64")
    if sys.version_info < (3,11): raise ValueError("Install Python 3.11 or newer and python3-tk")
    missing=[name for name in ("git","cmake","make","cc","c++","pkg-config") if not shutil.which(name)]
    if missing: raise ValueError("Install Linux build prerequisites (see README-FIRST.txt): "+", ".join(missing))
    layout.writable();env=layout.environment()
    prepare_sdl(layout,env,layout.git,progress)
    return env


def start_linux_updater(layout, staged, launcher_pid, *, restart_report=None):
    runner=beneath(layout.root,".local/updates/runner-"+str(time.time_ns()))
    runner.mkdir(parents=True)
    for name in ("portable_update.py","portable_support.py","release_checksums.py","build_policy.py","linux_support.py"):
        shutil.copy2(Path(__file__).with_name(name),runner/name)
    command=[str(layout.python),"-X","utf8","-E","-s","-B",str(runner/"portable_update.py"),
             "--root",str(layout.root),"--wait-pid",str(os.getpid())]
    if launcher_pid: command += ["--wait-pid",str(launcher_pid)]
    command += ["--stage",str(staged)] if staged else ["--rollback"]
    if restart_report:
        restart_report.resolve().relative_to(layout.local.resolve())
        command += ["--restart-report",str(restart_report)]
    with (layout.local/"update.log").open("w",encoding="utf-8") as log:
        subprocess.Popen(command,cwd=runner,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
