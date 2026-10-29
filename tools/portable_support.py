"""Original portable setup helpers; downloaded tools and game files stay local."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import time
import urllib.request
import zipfile

REPOSITORY = "TheEelYT/Nitrogen-Squared"
ASSET_NAME = "Nitrogen-Squared-Windows-x64.zip"
MAX_ARCHIVE_BYTES = 2 * 1024**3
MAX_EXPANDED_BYTES = 5 * 1024**3


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def relative_path(name: str) -> str:
    """A portable, non-special relative filename; Windows rules apply everywhere."""
    if not name or "\\" in name or "\x00" in name or ":" in name:
        raise ValueError("Unsafe archive filename")
    path = PurePosixPath(name)
    parts = name.split("/")
    if path.is_absolute() or any(p in ("", ".", "..") or p.endswith((" ", ".")) for p in parts):
        raise ValueError("Unsafe archive filename")
    if any(re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", p, re.I) for p in parts):
        raise ValueError("Reserved Windows filename")
    if any(any(ord(c)<32 for c in p) or any(c in '<>"|?*' for c in p) for p in parts):
        raise ValueError("Unsafe Windows filename")
    return path.as_posix()


def beneath(root: Path, name: str) -> Path:
    result = root / relative_path(name)
    result.resolve().relative_to(root.resolve())
    # Reject links/junctions even when they currently point inside the folder.
    for path in [result, *result.parents]:
        if path == root.parent:
            break
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("Portable files cannot pass through links or junctions")
        if path == root:
            break
    return result


def extract_zip(archive: Path, destination: Path, *, strip_root: bool = False):
    """Validate the whole ZIP before creating any output files."""
    with zipfile.ZipFile(archive) as z:
        members, seen, roots, total = [], set(), set(), 0
        for info in z.infolist():
            name = info.orig_filename.rstrip("/") if info.is_dir() else info.orig_filename
            name = relative_path(name)
            if stat.S_IFMT(info.external_attr >> 16) not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError("Archive contains a link or special file")
            key = name.casefold()
            if key in seen:
                raise ValueError("Archive contains duplicate filenames")
            seen.add(key)
            roots.add(name.split("/")[0])
            total += info.file_size
            if total > MAX_EXPANDED_BYTES or len(seen)>100000:
                raise ValueError("Archive exceeds extraction limits")
            members.append((info, name))
        if strip_root and (len(roots)!=1 or any("/" not in name and not info.is_dir() for info,name in members)):
            raise ValueError("Expected a single archive directory")
        for info, name in members:
            if strip_root:
                if "/" not in name:
                    continue
                name = name.split("/", 1)[1]
            target = beneath(destination, name)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as source, target.open("wb") as out:
                    shutil.copyfileobj(source, out, 1024*1024)


def download(url: str, path: Path, expected_sha: str, progress=print, *, maximum=MAX_ARCHIVE_BYTES):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha) or not url.startswith("https://"):
        raise ValueError("A pinned HTTPS download is required")
    if path.is_file() and sha256(path)==expected_sha:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name+".part")
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent":"Nitrogen-Squared-portable"})
            with urllib.request.urlopen(request, timeout=45) as response, partial.open("wb") as out:
                size, h, reported = 0, hashlib.sha256(), 0
                while chunk := response.read(1024*1024):
                    size += len(chunk)
                    if size>maximum:
                        raise ValueError("Download exceeds its size limit")
                    h.update(chunk); out.write(chunk)
                    if size-reported>=16*1024*1024:
                        progress(f"Downloaded {size//(1024*1024)} MiB…"); reported=size
            if h.hexdigest()!=expected_sha:
                raise ValueError("Download checksum did not match; nothing was installed")
            os.replace(partial, path)
            return path
        except (OSError, TimeoutError):
            if attempt==2:
                raise
            time.sleep(1)
        finally:
            partial.unlink(missing_ok=True)
    raise RuntimeError("Download failed")


class Layout:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.app = beneath(self.root, "app")
        self.local = beneath(self.root, ".local")
        self.python = beneath(self.root, "support/python/python.exe")
        self.tools = beneath(self.root, ".local/tools")
        self.work = beneath(self.root, ".local/runtime-dev")
        self.installation = beneath(self.root, ".local/installation")
        self.framework = beneath(self.root, ".local/psxrecomp")
        self.state_path = beneath(self.root, ".local/launcher-state.json")

    @property
    def version(self):
        return (self.app/"VERSION").read_text(encoding="utf-8").strip()

    def state(self):
        if not self.state_path.exists():
            return {}
        result = json.loads(self.state_path.read_text(encoding="utf-8"))
        if result.get("schema")!=1:
            raise ValueError("Unsupported local launcher state")
        return result

    def writable(self):
        self.local.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=self.local):
            pass

    def environment(self):
        env = os.environ.copy()
        llvm = self.tools/"llvm-mingw"
        bins = [self.python.parent, self.tools/"cmake/bin", self.tools/"ninja",
                self.tools/"git/cmd", llvm/"bin", llvm/"x86_64-w64-mingw32/bin"]
        env["PATH"] = os.pathsep.join(map(str,bins))+os.pathsep+env.get("PATH", "")
        env.update(CC="x86_64-w64-mingw32-clang.exe",
                   CXX="x86_64-w64-mingw32-clang++.exe",
                   CMAKE_GENERATOR="Ninja", CMAKE_BUILD_PARALLEL_LEVEL="2",
                   CXXFLAGS="-include cstdlib -include exception",
                   PSX_SDL3_SOURCE_DIR=str(self.local/"SDL3-source"),
                   PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
        temp = beneath(self.root, ".local/tmp")
        temp.mkdir(parents=True, exist_ok=True)
        env.update(TEMP=str(temp), TMP=str(temp))
        env.pop("PYTHONHOME", None); env.pop("PYTHONPATH", None)
        return env

    def command(self, script: str, *args):
        return [str(self.python), "-E", "-s", "-B", str(self.app/"tools"/script), *map(str,args)]


def run(command, cwd: Path, env: dict, progress=print):
    flags = subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0
    with subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                          errors="replace", creationflags=flags) as proc:
        tracker=getattr(progress,"set_process",None)
        if tracker:
            tracker(proc)
        try:
            for line in proc.stdout:
                progress(line.rstrip())
            if proc.wait():
                raise RuntimeError(f"Preparation command failed ({proc.returncode}); see the setup log")
        finally:
            if tracker:
                tracker(None)


def bootstrap(layout: Layout, progress=print):
    layout.writable()
    pins=json.loads((layout.app/"configs/portable_tools.json").read_text())
    if pins.get("schema")!=1 or pins.get("platform")!="windows-x86_64":
        raise ValueError("Unsupported preparation tools")
    for pin in pins["tools"]:
        relative_path(pin["name"])
        relative_path(pin["executable"])
        target=beneath(layout.tools,pin["name"])
        marker=target/"nitrogen-tool.json"
        if marker.is_file() and json.loads(marker.read_text()).get("sha256")==pin["sha256"] and (target/pin["executable"]).is_file():
            continue
        progress(f"Preparing {pin['name']} (first setup only)…")
        archive=beneath(layout.local,"downloads/"+pin["name"]+"-"+pin["sha256"][:16]+".zip")
        download(pin["url"],archive,pin["sha256"],progress,maximum=pin["size"])
        staging=Path(tempfile.mkdtemp(prefix=".tool-",dir=layout.tools if layout.tools.exists() else layout.local))
        try:
            extract_zip(archive,staging,strip_root=pin["strip_root"])
            if not (staging/pin["executable"]).is_file():
                raise ValueError("Preparation tool archive has an unexpected layout")
            write_json(staging/"nitrogen-tool.json",dict(sha256=pin["sha256"],version=pin["version"]))
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                old=target.with_name(target.name+".previous-"+str(time.time_ns()))
                if old.exists():
                    raise ValueError("Previous tool backup exists; retain it and retry from a clean tools directory")
                os.replace(target,old)
            os.replace(staging,target)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    env=layout.environment()
    # Keep SDL preparation deterministic and avoid the release-archive fallback.
    sdl=layout.local/"SDL3-source"
    if not sdl.exists():
        git=str(layout.tools/"git/cmd/git.exe")
        run([git,"init",str(sdl)],layout.root,env,progress)
        run([git,"-C",str(sdl),"remote","add","origin","https://github.com/libsdl-org/SDL.git"],layout.root,env,progress)
    git=str(layout.tools/"git/cmd/git.exe")
    sdl_pin="8e37db5e797b6167f3a00d697d816a684bd259c7"
    current=subprocess.run([git,"-C",str(sdl),"rev-parse","HEAD"],env=env,capture_output=True,text=True,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
    if current.returncode or current.stdout.strip()!=sdl_pin:
        if not current.returncode:
            raise ValueError("The private SDL checkout has another revision; it was preserved")
        run([git,"-C",str(sdl),"fetch","--depth","1","origin",sdl_pin],layout.root,env,progress)
        run([git,"-C",str(sdl),"checkout","--detach",sdl_pin],layout.root,env,progress)
    return env
