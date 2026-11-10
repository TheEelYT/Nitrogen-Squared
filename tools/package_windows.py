"""Stage only original launcher/source files and a clean CPython distribution."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile

from n2o_disc import ROOT
from package_source import collect_package,audit_staging
from portable_support import ASSET_NAME,sha256,write_json
from portable_update import owned_path,verify_package

FIRST_RUN="""Nitrogen Squared — Windows x64

1. Extract the entire Nitrogen-Squared folder somewhere you can write to.
2. Run launcher.exe and select your supported USA N2O CUE sheet.
   Keep the matching BIN beside its CUE. ZIPs must be extracted first.
3. Let the launcher verify the disc, download preparation tools, and compile
   your private game. First setup needs internet access and can take a while.
4. Use the launcher to play and check for updates.

No separate Python, Node.js, Rust or Visual Studio installation is required.
Windows uses Microsoft Edge WebView2 (normally present on Windows 10/11).
If missing, install the Evergreen Runtime from https://developer.microsoft.com/microsoft-edge/webview2/.
All downloaded tools, extracted/generated game files and saves are kept under
this folder's .local directory. Original disc files remain where you selected them.
The release contains no game data or game-derived executable.

Open the updated launcher once to repair existing direct-EXE save paths.
Launcher and direct execution then share .local/saves; old runtime-dev/saves
are preserved if present. The configuration repair needs no recompilation.

Updates preserve .local. Never delete it to update; it includes your saves.
Keep the source disc available for original assets, audio and verification.
If the prepared folder moves, its build cache is rebuilt locally. Saves are kept.
See app/LICENSE, app/COPYRIGHT, app/THIRD_PARTY.md and support/python/LICENSE.txt for third-party notices.
"""


def copy_python(source: Path, destination: Path):
    if sys.version_info[:2]!=(3,13) or os.name!="nt" or struct.calcsize("P")!=8:
        raise ValueError("Package with official 64-bit CPython 3.13 on Windows")
    destination.mkdir(parents=True)
    for path in source.iterdir():
        if path.is_file() and (path.name in ("python.exe","pythonw.exe","LICENSE.txt") or
                               path.suffix.lower()==".dll"):
            shutil.copy2(path,destination/path.name)
    excluded=shutil.ignore_patterns("site-packages","__pycache__","*.pyc","test","tests",
                                   "idlelib","ensurepip","_test*","__phello__","__hello__.*")
    for name in ("Lib","DLLs","tcl"):
        if not (source/name).is_dir():
            raise ValueError("The CPython distribution lacks "+name)
        shutil.copytree(source/name,destination/name,ignore=excluded)
    shutil.copy2(destination/"python.exe",destination/"python3.exe")
    for name in ("python.exe","python3.exe","pythonw.exe","LICENSE.txt","Lib/os.py","Lib/tkinter/__init__.py"):
        if not (destination/name).is_file():
            raise ValueError("Incomplete portable CPython runtime")


def stage(output: Path, *, launcher_bundle=None):
    files=collect_package(ROOT)
    with tempfile.TemporaryDirectory(prefix="nitrogen-release-",dir=output.parent) as temporary:
        root=Path(temporary)/"Nitrogen-Squared"
        app=root/"app"
        app.mkdir(parents=True)
        for name,data in files.items():
            path=app/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
        audit_staging(app,set(files))
        copy_python(Path(sys.base_prefix),root/"support/python")
        bundle=Path(launcher_bundle) if launcher_bundle else ROOT/"dist/launcher-windows"
        if not (bundle/"launcher.exe").is_file() or not (bundle/"licenses/DEPENDENCIES.json").is_file():
            raise ValueError("Build the Tauri launcher first: python tools/build_launcher.py")
        shutil.copy2(bundle/"launcher.exe",root/"launcher.exe")
        shutil.copytree(bundle/"licenses",root/"support/launcher/licenses")
        (root/"README-FIRST.txt").write_text(FIRST_RUN,encoding="utf-8")
        inventory={}
        for path in sorted(root.rglob("*")):
            if not path.is_file():continue
            name=path.relative_to(root).as_posix()
            owned_path(name)
            inventory[name]=dict(sha256=sha256(path),size=path.stat().st_size)
        manifest=dict(schema=1,platform="windows-x86_64",version=(ROOT/"VERSION").read_text().strip(),
                      python_version=sys.version.split()[0],files=inventory)
        write_json(root/"release-manifest.json",manifest)
        verify_package(root)
        with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as archive:
            for path in sorted(root.rglob("*")):
                if path.is_file():archive.write(path,"Nitrogen-Squared/"+path.relative_to(root).as_posix())
        # Read the finished archive into a fresh directory and audit its exact inventory.
        check=Path(temporary)/"verified"
        from portable_support import extract_zip
        extract_zip(output,check)
        verify_package(check/"Nitrogen-Squared")
    digest=sha256(output)
    output.with_name(output.name+".sha256").write_text(digest+"  "+output.name+"\n",encoding="ascii")
    print(f"Portable package verified: {len(inventory)} files; {output.stat().st_size} bytes; SHA256 {digest}",flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"dist"/ASSET_NAME)
    args=p.parse_args()
    output=args.output.resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    stage(output)


if __name__=="__main__":main()
