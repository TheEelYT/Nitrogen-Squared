#!/usr/bin/env python3
"""Generate private movie guards/extents from an already verified import."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
from n2o_disc import ROOT, IsoReader, exe_header


def prepare_media(manifest: dict, installation: Path, output: Path) -> Path:
    identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
    expected = next(e for e in identity["executables"] if e["path"] == "NEW.EXE")
    data = (installation / "executables/NEW.EXE").read_bytes()
    if len(data) != expected["size"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
        raise ValueError("Native movie binding requires the verified NEW.EXE")
    header = exe_header(data)
    entry, end, index = 0x80022350, 0x80022688, 0x8005EB8C
    offset = entry - header["load_address"] + 2048
    body = data[offset:offset + end - entry]
    if offset < 2048 or len(body) != end - entry:
        raise ValueError("Native movie function extent changed")
    guard = struct.unpack_from("<4I", body)
    code_hash = 14695981039346656037
    for byte in body:
        code_hash = ((code_hash ^ byte) * 1099511628211) & ((1 << 64) - 1)
    data_end = manifest["tracks"][1]["pregap"] or manifest["tracks"][1]["start"]
    with IsoReader(Path(manifest["bin"]), data_end) as iso:
        _, entries = iso.inventory()
    files = {e.path: e for e in entries}
    rows = []
    for name in ("FOX.SXA", "N2O.SXA", "N2OEND.SXA", "CRYSTAL.SXA"):
        extent = files[name]
        rows.append(f'    {{{json.dumps(name)}, {extent.lba}u, {(extent.size + 2047) // 2048}u}}')
    text = (
        '// Private generated instruction guards. Do not distribute.\n'
        '#pragma once\n#include "media_contract.h"\nnamespace nitrogen::media {\n'
        f'constexpr Binding binding = {{true, 0x{entry:08x}u, 0x{index:08x}u, {len(body)}u,\n'
        '    {' + ', '.join(f'0x{word:08x}u' for word in guard) + '},\n'
        f'    0x{code_hash:016x}ull, {{\n' + ',\n'.join(rows) + '\n}};\n}\n'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists() or output.read_text() != text:
        output.write_text(text, encoding="utf-8")
    return output
