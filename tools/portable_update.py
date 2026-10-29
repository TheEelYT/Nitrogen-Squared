"""Verified portable-package updates; user data is never release-owned."""
from __future__ import annotations
import argparse
import ctypes
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

from portable_support import (ASSET_NAME, REPOSITORY, Layout, beneath, download,
                              extract_zip, relative_path, sha256, write_json)


def version_tuple(value):
    if not re.fullmatch(r"0|[1-9]\d*", str(value).split(".")[0]) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError("Unsupported release version")
    return tuple(map(int,value.split(".")))


def owned_path(name):
    name=relative_path(name)
    if any(p.casefold() in (".local","saves","cache","generated","disc","executables",".git") for p in name.split("/")):
        raise ValueError("A release cannot own private data")
    if name not in ("launcher.exe","README-FIRST.txt") and not name.startswith(("app/","support/python/")):
        raise ValueError("Unexpected release-owned path")
    return name


def read_manifest(root: Path):
    value=json.loads((root/"release-manifest.json").read_text(encoding="utf-8"))
    if value.get("schema")!=1 or value.get("platform")!="windows-x86_64" or not isinstance(value.get("files"),dict):
        raise ValueError("Unsupported release manifest")
    version_tuple(value["version"])
    seen=set()
    for name,info in value["files"].items():
        owned_path(name)
        if name.casefold() in seen or not re.fullmatch(r"[0-9a-f]{64}",info.get("sha256","")) or not isinstance(info.get("size"),int) or not 0<=info["size"]<=2*1024**3:
            raise ValueError("Invalid release file inventory")
        seen.add(name.casefold())
    if "launcher.exe" not in value["files"] or "support/python/python.exe" not in value["files"] or "app/VERSION" not in value["files"]:
        raise ValueError("Incomplete portable package")
    return value


def verify_package(root: Path):
    value=read_manifest(root)
    actual={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() or p.is_symlink()}
    if actual!=set(value["files"])|{"release-manifest.json"}:
        raise ValueError("Package has missing or unexpected files")
    for name,info in value["files"].items():
        path=beneath(root,name)
        if not path.is_file() or path.stat().st_size!=info["size"] or sha256(path)!=info["sha256"]:
            raise ValueError("Package file checksum mismatch: "+name)
    if (root/"app/VERSION").read_text().strip()!=value["version"]:
        raise ValueError("Package version mismatch")
    return value


def api_json(url):
    request=urllib.request.Request(url,headers={"User-Agent":"Nitrogen-Squared-portable","Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(request,timeout=30) as response:
        data=response.read(2*1024*1024+1)
    if len(data)>2*1024*1024:
        raise ValueError("Release metadata is too large")
    return json.loads(data)


def latest_release(current):
    try:
        value=api_json(f"https://api.github.com/repos/{REPOSITORY}/releases/latest")
    except urllib.error.HTTPError as e:
        if e.code==404:
            return None
        raise
    if value.get("draft") or value.get("prerelease"):
        return None
    version=value["tag_name"].removeprefix("v")
    if version_tuple(version)<=version_tuple(current):
        return None
    assets={a["name"]:a for a in value["assets"]}
    asset=assets.get(ASSET_NAME)
    checksum=assets.get(ASSET_NAME+".sha256")
    if not asset or not checksum:
        raise ValueError("The published release has no complete Windows package")
    prefix=f"https://github.com/{REPOSITORY}/releases/download/{value['tag_name']}/"
    if asset["browser_download_url"]!=prefix+ASSET_NAME or checksum["browser_download_url"]!=prefix+ASSET_NAME+".sha256":
        raise ValueError("Unexpected release download location")
    return dict(version=version,url=asset["browser_download_url"],checksum=checksum["browser_download_url"],digest=asset.get("digest"))


def stage_release(layout: Layout, release, progress=print):
    with urllib.request.urlopen(release["checksum"],timeout=30) as response:
        checksum=response.read(513)
    match=re.fullmatch(rb"([0-9a-f]{64})[ \t]+\*?"+re.escape(ASSET_NAME.encode())+rb"\r?\n?",checksum)
    if not match:
        raise ValueError("Invalid release checksum file")
    digest=match[1].decode()
    if release.get("digest") and release["digest"]!="sha256:"+digest:
        raise ValueError("Release checksum disagrees with GitHub's asset digest")
    archive=beneath(layout.root,".local/updates/"+release["version"]+"-"+digest[:16]+".zip")
    download(release["url"],archive,digest,progress)
    staging=beneath(layout.root,".local/updates/package-"+release["version"]+"-"+digest[:16])
    if staging.exists():
        verified=verify_package(staging/"Nitrogen-Squared")
    else:
        extract_zip(archive,staging)
        if {p.name for p in staging.iterdir()}!={"Nitrogen-Squared"}:
            raise ValueError("Expected a Nitrogen-Squared package folder")
        verified=verify_package(staging/"Nitrogen-Squared")
    if verified["version"]!=release["version"]:
        raise ValueError("Downloaded package has another version")
    return staging/"Nitrogen-Squared"


def rollback(layout: Layout):
    journal_path=beneath(layout.root,".local/update-state.json")
    journal=json.loads(journal_path.read_text())
    backup=beneath(layout.root,journal["backup"])
    for name,record in journal["originals"].items():
        if name!="release-manifest.json":
            owned_path(name)
        target=beneath(layout.root,name)
        if record["present"]:
            source=beneath(backup,name)
            if not source.is_file() or sha256(source)!=record["sha256"]:
                raise ValueError("Update backup is incomplete; existing files were preserved")
        if target.exists() and sha256(target) not in (record.get("sha256"),record.get("new_sha256")):
            raise ValueError("A file changed after update staging; it was preserved: "+name)
    for name,record in journal["originals"].items():
        target=beneath(layout.root,name)
        if record["present"]:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(beneath(backup,name),target)
        elif target.is_file():
            target.unlink()
    journal_path.unlink()


def apply_update(layout: Layout, staged: Path):
    staged.resolve().relative_to(beneath(layout.root,".local/updates").resolve())
    new=verify_package(staged)
    old=read_manifest(layout.root)
    if version_tuple(new["version"])<=version_tuple(old["version"]):
        raise ValueError("Update must advance the package version")
    journal_path=beneath(layout.root,".local/update-state.json")
    if journal_path.exists():
        raise ValueError("An interrupted update must be restored first")
    names=sorted(set(old["files"])|set(new["files"]))+["release-manifest.json"]
    backup=beneath(layout.root,".local/updates/backup-"+str(time.time_ns()))
    originals={}
    for name in names:
        target=beneath(layout.root,name)
        if target.exists() and not target.is_file():
            raise ValueError("An update filename is occupied by a directory")
        if name not in old["files"] and name!="release-manifest.json" and target.exists():
            raise ValueError("An unowned file occupies a new package path; it was preserved: "+name)
        originals[name]=dict(present=target.is_file(),sha256=sha256(target) if target.is_file() else None,
                             new_sha256=sha256(staged/name) if name=="release-manifest.json" else new["files"].get(name,{}).get("sha256"))
    for name,record in originals.items():
        if record["present"]:
            dest=beneath(backup,name)
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(beneath(layout.root,name),dest)
    write_json(journal_path,dict(schema=1,backup=backup.relative_to(layout.root).as_posix(),originals=originals))
    try:
        install=backup/"new-files"
        for name in names:
            target=beneath(layout.root,name)
            source=staged/name
            if source.is_file():
                prepared=beneath(install,name)
                prepared.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,prepared)
                target.parent.mkdir(parents=True,exist_ok=True)
                os.replace(prepared,target)
            elif target.exists():
                target.unlink()
        journal_path.unlink()
    except BaseException:
        rollback(layout)
        raise


def start_updater(layout: Layout, staged: Path | None, launcher_pid: int):
    runner=beneath(layout.root,".local/updates/runner-"+str(time.time_ns()))
    shutil.copytree(layout.python.parent,runner/"python")
    scripts=runner/"scripts"
    scripts.mkdir()
    for name in ("portable_update.py","portable_support.py"):
        shutil.copy2(Path(__file__).with_name(name),scripts/name)
    command=[str(runner/"python/python.exe"),"-E","-s","-B",str(scripts/"portable_update.py"),"--root",str(layout.root),"--wait-pid",str(os.getpid())]
    if launcher_pid:
        command += ["--wait-pid",str(launcher_pid)]
    command += ["--stage",str(staged)] if staged else ["--rollback"]
    with (layout.local/"update.log").open("w",encoding="utf-8") as log:
        subprocess.Popen(command,cwd=runner,stdout=log,stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)


def wait_for_processes(pids):
    if os.name!="nt":
        raise RuntimeError("The portable updater requires Windows")
    kernel=ctypes.WinDLL("kernel32",use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handles=[]
    try:
        for pid in pids:
            handle=kernel.OpenProcess(0x00100000,False,pid)
            if handle:
                handles.append(handle)
        for handle in handles:
            if kernel.WaitForSingleObject(handle,120000)!=0:
                raise RuntimeError("Close running Nitrogen-Squared windows before updating")
    finally:
        for handle in handles:
            kernel.CloseHandle(handle)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--stage",type=Path)
    p.add_argument("--rollback",action="store_true")
    p.add_argument("--wait-pid",type=int,action="append",default=[])
    args=p.parse_args()
    wait_for_processes(args.wait_pid)
    layout=Layout(args.root)
    if args.rollback:
        rollback(layout)
    elif args.stage:
        apply_update(layout,args.stage)
    else:
        raise ValueError("No update action selected")
    subprocess.Popen([str(layout.root/"launcher.exe")],cwd=layout.root)


if __name__=="__main__":
    main()
