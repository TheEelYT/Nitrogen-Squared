"""Launcher presentation data; game preferences retain the native file format."""
from __future__ import annotations
import json
import re
from pathlib import Path
from portable_support import write_json
from portable_update import api_json, version_tuple
from portable_support import REPOSITORY

DEFAULT_OPTIONS = dict(video_mode=0, hud_scale=0, render_percent=100, master_volume=100)
KEYBOARD = [("Move / navigate", "W A S D"), ("Select / main weapon", "Enter"),
            ("Back / shield", "Backspace"), ("Secondary weapon", "Right Shift"),
            ("Switch secondary", "W"), ("Firewall", "E"), ("Brake", "S"),
            ("Jump", "Space"), ("Pause / resume", "P"), ("Pause menu", "O"),
            ("Zoom out / in", "− / =")]


def valid_option(name, value):
    if type(value) is not int:return False
    return (name == "video_mode" and value in (0,1,2)
            or name == "hud_scale" and value in (0,2,3,4,6)
            or name == "render_percent" and 25 <= value <= 200 and value % 5 == 0
            or name == "master_volume" and 0 <= value <= 100)


def read_options(local: Path):
    values = dict(DEFAULT_OPTIONS)
    path = local / "nitrogen-options.ini"
    if path.is_file():
        for line in path.read_text(encoding="utf-8",errors="replace").splitlines():
            fields = line.split()
            if len(fields) == 2 and re.fullmatch(r"[+-]?[0-9]+",fields[1]):
                try:value = int(fields[1])
                except ValueError:continue
                if valid_option(fields[0],value):values[fields[0]]=value
    return values


def save_option(local: Path, name, value):
    if not valid_option(name,value):raise ValueError("Unsupported game preference")
    path = local / "nitrogen-options.ini"
    if path.is_symlink():raise ValueError("The preferences file is a symbolic link; it was preserved")
    values=read_options(local);values[name]=value
    previous=path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    # Preserve comments and unknown future fields; normalize known native keys.
    extra=[line for line in previous if not line.split() or line.split()[0] not in DEFAULT_OPTIONS]
    content="\n".join([*(f"{k} {v}" for k,v in values.items()),*extra])+"\n"
    if path.exists() and path.read_text(encoding="utf-8")==content:return
    local.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name("nitrogen-options.launcher.tmp")
    if temporary.exists() or temporary.is_symlink():raise ValueError("A previous preferences write is still present")
    try:
        with temporary.open("x",encoding="utf-8",newline="\n") as stream:stream.write(content)
        temporary.replace(path)
    finally:temporary.unlink(missing_ok=True)


def read_launcher_preferences(local):
    try:
        data=json.loads((local/"launcher-preferences.json").read_text(encoding="utf-8"))
        return dict(accent=data.get("accent") if data.get("accent") in ("Cyan","Violet","Amber") else "Cyan")
    except (OSError,ValueError,AttributeError):return dict(accent="Cyan")


def set_accent(local, name):
    if name not in ("Cyan","Violet","Amber"):raise ValueError("Unknown accent colour")
    write_json(local/"launcher-preferences.json",dict(accent=name))


def bundled_release(layout):
    data=json.loads((layout.app/"configs/launcher_notes.json").read_text(encoding="utf-8"))
    return dict(version=layout.version,title="Nitrogen Squared "+layout.version,date=data["date"],
                summary=data["summary"],body=data["body"],url="https://github.com/"+REPOSITORY,
                current=True)


def clean_release(value):
    if not isinstance(value,dict) or value.get("draft") or value.get("prerelease"):return None
    version=str(value.get("tag_name","")).removeprefix("v")
    try:version_tuple(version)
    except ValueError:return None
    body=str(value.get("body") or "")[:64000]
    title=str(value.get("name") or "Nitrogen Squared "+version)[:180]
    summary=next((line.strip() for line in body.splitlines() if version in line),body[:160])
    summary=re.sub(r"[*`#]","",summary)
    summary=re.sub(r"^"+re.escape(version)+r"\s*:\s*","",summary)[:130]
    return dict(version=version,title=title,date=str(value.get("published_at") or "")[:10],
                summary=summary or "Release notes and improvements.",body=body,
                url=f"https://github.com/{REPOSITORY}/releases/tag/v{version}",current=False)


def read_release_cache(local):
    try:
        data=json.loads((local/"launcher-releases.json").read_text(encoding="utf-8"))
        if not isinstance(data,list):return []
        return [r for value in data[:20] if (r:=clean_release(value))]
    except (OSError,ValueError):return []


def fetch_release_history(local):
    values=api_json(f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=15")
    if not isinstance(values,list):raise ValueError("Unsupported release history")
    releases=[r for value in values if (r:=clean_release(value))]
    write_json(local/"launcher-releases.json",values)
    return releases


def release_list(layout, published):
    current=bundled_release(layout)
    items=[dict(r,current=r["version"]==layout.version) for r in published]
    if not any(r["current"] for r in items):items.append(current)
    return sorted(items,key=lambda r:version_tuple(r["version"]),reverse=True)


BUILD_STAGES = frozenset(('Verifying your disc', 'Configuring build tools', 'Building tools',
    'Preparing firmware', 'Generating game code', 'Checking generated code', 'Preparing game assets',
    'Preparing native game code', 'Configuring game', 'Building game', 'Finishing setup'))


def progress_summary(line, current_stage=''):
    marker=re.fullmatch(r'Stage: ([^|]+) \| (.+)',line)
    if marker and marker[1].strip() in BUILD_STAGES:return marker[1].strip(),marker[2],None
    if line.startswith("Runtime started (PID "):return "Game running", "Close the game window to return here.", None
    if line.startswith("Starting game."):return "Starting game", "Verifying your disc before launch…", None
    if line.startswith("Using your existing"):return "Starting game", "Using your existing compatible game build.", None
    if line.startswith("Downloaded "):return "Downloading tools", line[-180:], None
    if line.startswith("Checking SDL source"):return "Checking SDL", "Checking a required setup component…", None
    if line.startswith("Checking framework source"):return "Checking framework", "Checking the game preparation framework…", None
    if line.startswith("Downloading SDL source"):return "Downloading SDL", "Downloading a required setup component…", None
    if line.startswith("Downloading framework source"):return "Downloading framework", "Downloading the game preparation framework…", None
    git_progress=re.search(r"(?:Receiving objects|Resolving deltas):\s*(\d+)%",line)
    if git_progress:return "Downloading setup components", line[-180:], min(100,int(git_progress[1]))
    if line.startswith("Verifying the complete disc"):return "Verifying your disc", "Checking the game and its audio tracks…", None
    if line.startswith("Extracting "):return "Extracting assets", "Saving original assets and music locally…", None
    if 'Re-running CMake' in line:return 'Configuring game' if current_stage!='Building tools' else 'Configuring build tools','Refreshing the build configuration…',None
    if 'Re-checking globbed directories' in line:return current_stage or 'Checking build inputs','Checking source file lists…',None
    stage=re.match(r"\[\s*(\d+)%\]\s*(.*)",line)
    if stage:return current_stage or 'Building game',stage[2][-180:] or 'Compiling game code…',min(100,int(stage[1]))
    step=re.match(r"\[(\d+)/(\d+)\]\s*(.*)",line)
    if step and int(step[2]):return current_stage or 'Building game',f'{step[1]} of {step[2]} · {step[3][-160:]}',min(100,int(step[1])*100//int(step[2]))
    if current_stage.startswith('Configuring') and line.startswith('-- '):return current_stage,line[3:][-180:],None
    if line.startswith("Preparing "):return "Setting up", "Preparing your game and local tools…",None
    if line.startswith("Existing saves"):return "Keeping your saves",line[-180:],None
    return None
