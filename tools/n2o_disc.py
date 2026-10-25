#!/usr/bin/env python3
"""Bounded, read-only N2O disc inspection and local executable preparation.

Python 3.10+, standard library only. No game bytes are embedded in this module.
The verified revision currently supports the supplied merged BIN/CUE layout.
Split BINs/other revisions must be verified separately before being accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import tempfile
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
SYNC = b"\x00" + b"\xff" * 10 + b"\x00"
SECTOR = 2352
USER = 2048
MAX_EXE = 2 * 1024 * 1024


class DiscError(ValueError):
    pass


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Track:
    number: int
    kind: str
    start: int
    pregap: int | None


def frames(s: str) -> int:
    m, sec, frame = map(int, s.split(":"))
    if sec >= 60 or frame >= 75:
        raise DiscError("Invalid CUE timestamp")
    return (m * 60 + sec) * 75 + frame


def parse_cue(cue: Path) -> tuple[Path, list[Track]]:
    files: list[str] = []
    tracks: list[dict] = []
    for raw in cue.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.upper().startswith("REM "):
            continue
        m = re.fullmatch(r'FILE\s+"([^"]+)"\s+BINARY', line, re.I)
        if m:
            files.append(m[1])
            continue
        m = re.fullmatch(r"TRACK\s+(\d+)\s+(MODE2/2352|AUDIO)", line, re.I)
        if m:
            if len(files) != 1:
                raise DiscError("Only a verified single-BIN CUE is supported yet")
            tracks.append(dict(number=int(m[1]), kind=m[2].upper(), start=None, pregap=None))
            continue
        m = re.fullmatch(r"INDEX\s+(00|01)\s+(\d+:\d+:\d+)", line, re.I)
        if m and tracks:
            key = "start" if m[1] == "01" else "pregap"
            if tracks[-1][key] is not None:
                raise DiscError("Duplicate CUE index")
            tracks[-1][key] = frames(m[2])
            continue
        raise DiscError(f"Unsupported CUE directive: {line}")
    if len(files) != 1 or not tracks:
        raise DiscError("Expected a complete merged BIN/CUE image")
    name = files[0]
    wp = PureWindowsPath(name)
    if wp.is_absolute() or wp.drive or "/" in name or "\\" in name or name in (".", ".."):
        raise DiscError("CUE must reference a BIN beside the CUE")
    bin_path = (cue.parent / name).resolve()
    if bin_path.parent != cue.parent.resolve() or not bin_path.is_file():
        raise DiscError("The BIN referenced by the CUE is missing or outside its folder")
    if bin_path.stat().st_size % SECTOR:
        raise DiscError("BIN length is not a whole number of raw sectors")
    total = bin_path.stat().st_size // SECTOR
    previous = -1
    for i, track in enumerate(tracks, 1):
        start, gap = track["start"], track["pregap"]
        if track["number"] != i or start is None or not previous < start < total:
            raise DiscError("Invalid or non-monotonic track layout")
        if gap is not None and not previous < gap <= start:
            raise DiscError("Invalid track pregap")
        previous = start
    if tracks[0]["start"] != 0 or tracks[0]["kind"] != "MODE2/2352":
        raise DiscError("Track 1 must start at sector zero in MODE2/2352")
    if any(t["kind"] != "AUDIO" for t in tracks[1:]):
        raise DiscError("Expected audio tracks after Track 1")
    return bin_path, [Track(**t) for t in tracks]


@dataclass(frozen=True)
class Entry:
    path: str
    lba: int
    size: int
    directory: bool


class IsoReader:
    def __init__(self, bin_path: Path, data_end: int):
        self.file = bin_path.open("rb")
        self.data_end = data_end

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.file.close()

    def sector(self, lba: int) -> bytes:
        if not 0 <= lba < self.data_end:
            raise DiscError("ISO extent exceeds the data track")
        self.file.seek(lba * SECTOR)
        raw = self.file.read(SECTOR)
        if len(raw) != SECTOR or raw[:12] != SYNC or raw[15] != 2:
            raise DiscError(f"Invalid Mode 2 sector at LBA {lba}")
        if raw[18] & 0x20:
            raise DiscError("Form 2 sector used for an ISO file")
        return raw[24:24 + USER]

    def read(self, lba: int, size: int, limit: int = MAX_EXE) -> bytes:
        if size < 0 or size > limit:
            raise DiscError("ISO object exceeds the permitted size")
        return b"".join(self.sector(lba + i) for i in range((size + USER - 1) // USER))[:size]

    def inventory(self) -> tuple[str, list[Entry]]:
        pvd = self.sector(16)
        if pvd[:7] != b"\x01CD001\x01":
            raise DiscError("No ISO9660 primary volume descriptor")
        volume = pvd[40:72].decode("ascii").strip()
        root_lba, root_size = struct.unpack_from("<I", pvd, 158)[0], struct.unpack_from("<I", pvd, 166)[0]
        out: list[Entry] = []
        seen: set[int] = set()

        def walk(lba: int, size: int, prefix: str, depth: int):
            if lba in seen or depth > 8 or len(out) > 4096:
                raise DiscError("Cyclic or excessive ISO directory structure")
            seen.add(lba)
            data = self.read(lba, size, 1024 * 1024)
            pos = 0
            while pos < len(data):
                length = data[pos]
                if not length:
                    pos = (pos // USER + 1) * USER
                    continue
                if length < 34 or pos + length > len(data) or pos % USER + length > USER:
                    raise DiscError("Malformed ISO directory record")
                rec = data[pos:pos + length]
                pos += length
                nlen = rec[32]
                if not nlen or nlen + 33 > len(rec):
                    raise DiscError("Malformed ISO filename")
                name_bytes = rec[33:33 + nlen]
                if name_bytes in (b"\0", b"\1"):
                    continue
                name = name_bytes.decode("ascii").split(";")[0]
                if not name or name in (".", "..") or "/" in name or "\\" in name:
                    raise DiscError("Invalid ISO filename")
                extent, count = struct.unpack_from("<I", rec, 2)[0], struct.unpack_from("<I", rec, 10)[0]
                directory = bool(rec[25] & 2)
                entry = Entry(prefix + name, extent, count, directory)
                if directory:
                    walk(extent, count, entry.path + "/", depth + 1)
                else:
                    out.append(entry)
                    if len(out) > 4096:
                        raise DiscError("Too many ISO files")
        walk(root_lba, root_size, "", 0)
        return volume, out


def exe_header(data: bytes) -> dict:
    if len(data) < 2048 or data[:8] != b"PS-X EXE":
        raise DiscError("Invalid PS-X EXE header")
    entry, load, text = (struct.unpack_from("<I", data, o)[0] for o in (16, 24, 28))
    lo = load & 0x1fffffff
    if not text or text % 4 or text > MAX_EXE or text + 2048 > len(data):
        raise DiscError("Invalid PS-X EXE text size")
    if lo + text > 0x200000 or not load <= entry < load + text or entry % 4 or load % 4:
        raise DiscError("PS-X EXE addresses exceed PS1 RAM")
    return dict(entry_pc=entry, load_address=load, text_size=text,
                stack_base=struct.unpack_from("<I", data, 48)[0])


def seed_candidates(data: bytes) -> list[int]:
    h = exe_header(data)
    lo, size = h["load_address"], h["text_size"]
    seeds = {h["entry_pc"]}
    for off in range(0, size, 4):
        word = struct.unpack_from("<I", data, 2048 + off)[0]
        if word >> 26 == 3:
            target = ((lo + off + 4) & 0xf0000000) | ((word & 0x03ffffff) << 2)
            if lo <= target < lo + size:
                seeds.add(target)
    return sorted(seeds)


def inspect(cue: Path, identity: dict, progress=lambda s: None) -> dict:
    cue = cue.resolve()
    bin_path, tracks = parse_cue(cue)
    actual_layout = [dict(number=t.number, kind=t.kind, start=t.start, pregap=t.pregap) for t in tracks]
    if actual_layout != identity["tracks"]:
        raise DiscError("Unverified CUE track layout; keep every audio track")
    if bin_path.stat().st_size != identity["bin_size"]:
        raise DiscError("Unsupported or incomplete BIN")
    progress("Verifying the complete disc, including audio tracks…")
    if digest(bin_path) != identity["bin_sha256"]:
        raise DiscError("Disc digest differs from the verified USA revision")
    data_end = tracks[1].pregap if len(tracks) > 1 else bin_path.stat().st_size // SECTOR
    if data_end is None:
        data_end = tracks[1].start
    with IsoReader(bin_path, data_end) as iso:
        volume, entries = iso.inventory()
        by_name = {e.path: e for e in entries}
        if len(by_name) != len(entries):
            raise DiscError("Duplicate ISO filenames")
        cnf = by_name.get("SYSTEM.CNF")
        if cnf is None:
            raise DiscError("SYSTEM.CNF is missing")
        text = iso.read(cnf.lba, cnf.size, 8192).decode("ascii")
        m = re.search(r"BOOT\s*=\s*cdrom:\\?([^;\s]+)", text, re.I)
        if not m or m[1].upper() != identity["boot_exe"]:
            raise DiscError("Unexpected boot executable")
        exes = []
        for expected in identity["executables"]:
            e = by_name.get(expected["path"])
            if e is None or e.size != expected["size"]:
                raise DiscError(f"Missing or unexpected executable: {expected['path']}")
            data = iso.read(e.lba, e.size)
            if hashlib.sha256(data).hexdigest() != expected["sha256"]:
                raise DiscError(f"Executable verification failed: {e.path}")
            h = exe_header(data)
            exes.append(dict(path=e.path, size=e.size, sha256=expected["sha256"],
                             **h, seed_candidates=len(seed_candidates(data))))
    return dict(schema=1, game_id=identity["game_id"], cue=str(cue), bin=str(bin_path),
                bin_sha256=identity["bin_sha256"], volume=volume, tracks=actual_layout,
                executables=exes, runtime_ready=False)


def prepare(cue: Path, destination: Path, identity: dict, progress=lambda s: None) -> dict:
    # Verify before creating a destination. Existing installations are never replaced.
    result = inspect(cue, identity, progress)
    destination = destination.resolve()
    if destination.exists():
        raise DiscError(f"Destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".n2o-import-", dir=destination.parent))
    try:
        (staging / "executables").mkdir()
        (staging / "seeds").mkdir()
        progress("Preparing local executable inputs…")
        data_end = result["tracks"][1]["pregap"] or result["tracks"][1]["start"]
        with IsoReader(Path(result["bin"]), data_end) as iso:
            _, entries = iso.inventory()
            files = {e.path: e for e in entries}
            for e in result["executables"]:
                source = files[e["path"]]
                data = iso.read(source.lba, source.size)
                if hashlib.sha256(data).hexdigest() != e["sha256"]:
                    raise DiscError("Disc changed while preparing local files")
                (staging / "executables" / e["path"]).write_bytes(data)
                seeds = seed_candidates(data)
                (staging / "seeds" / (e["path"] + ".txt")).write_text(
                    "".join(f"0x{s:08X}\n" for s in seeds), encoding="utf-8")
        # Only paths/hashes/analysis metadata go in the manifest, never embedded bytes.
        (staging / "installation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if destination.exists():
            raise DiscError("Destination was created during preparation")
        staging.rename(destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return result


def default_data_dir() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "NitrogenSquared"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "nitrogen-squared"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cue", type=Path)
    p.add_argument("--prepare", type=Path, help="New private local data directory; never a release folder")
    args = p.parse_args()
    identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
    try:
        result = prepare(args.cue, args.prepare, identity, print) if args.prepare else inspect(args.cue, identity, print)
    except (DiscError, OSError, UnicodeError) as e:
        p.exit(1, f"Disc preparation failed: {e}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
