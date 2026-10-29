#!/usr/bin/env python3
"""Generate a small, content-validated native game slice from private inputs.

Uses the pinned framework's static-overlay emitter and residency gate. No game
instructions or generated bodies belong in this repository or a source package.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

from build_recompiler import verify_framework
from n2o_disc import ROOT, digest, exe_header


def write_text(path: Path, text: str):
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8", newline="\n")


def capture(data: bytes, base: int, entries: list[int]) -> dict:
    if not data or len(data) % 4 or base % 4 or not entries or len(entries) != len(set(entries)):
        raise ValueError("Invalid native slice geometry")
    if any(e % 4 or not base <= e < base + len(data) for e in entries):
        raise ValueError("Native entry outside slice")
    pcs = [f"0x{e:08X}" for e in entries]
    return dict(schema="psxrecomp overlay capture v2", load_addr=f"0x{base:08X}",
                size=len(data), guard_bytes=0, bytes_b64=base64.b64encode(data).decode(),
                dispatch_entry_pcs=pcs, static_dispatch_entry_pcs=pcs,
                function_entry_pcs=pcs)


def add_resumes(compiler, part: dict) -> list[dict]:
    """Expose compiled block resumptions through the same residency gate.

    Use the pinned emitter's continuation ownership and resume-arm helper,
    as its static CLI does. An alias is not an additional translated function.
    """
    owners = {}
    for entry, owner in sorted(part["continuation_owners"].items()):
        if entry in part["func_addrs"]:
            continue
        identities = part["ids_by_addr"].get(owner, [])
        if not identities or not all(any(lo <= entry < lo + size for lo, size in ranges)
                                    for _, ranges in identities):
            raise ValueError("Native continuation has no guarded owner range")
        owners.setdefault(owner, []).append(entry)
    requests = [(part["symbols"][owner], owner, entries) for owner, entries in owners.items()]
    part["src"], accepted = compiler.add_cps_resume_cases(part["src"], requests)
    resumes = []
    for owner, entries in owners.items():
        host = part["symbols"][owner]
        for entry in entries:
            if entry not in accepted.get(host, ()):
                raise ValueError("Pinned emitter could not bind a native continuation")
            symbol = f"{part['namespace']}_resume_{entry:08X}"
            part["src"] += (f"\nvoid {symbol}(CPUState *cpu)\n{{\n"
                            f"    cpu->pc = 0x{entry:08X}u;\n    {host}(cpu);\n}}\n")
            for crc, ranges in part["ids_by_addr"][owner]:
                part["variants"].append(dict(addr=entry, symbol=symbol, crc=crc, ranges=ranges))
            resumes.append(dict(entry=entry, owner=owner))
    return resumes


def emit(records: list[tuple[str, dict]], framework: Path, recompiler: Path,
         game_toml: Path, output: Path, cmake="cmake") -> Path:
    """Shared production/synthetic path; return a metadata-only private receipt."""
    verify_framework(framework)
    try:
        import tomllib
    except ImportError:
        try:
            import tomli  # noqa: F401
        except ImportError as e:
            raise ValueError("Python 3.10 native builds need: python -m pip install tomli") from e
    sys.path.insert(0, str(framework / "tools"))
    compiler = importlib.import_module("compile_overlays")
    subprocess.run([cmake, f"-DPSXRECOMP_CODEGEN_HASH_ROOT={framework.as_posix()}",
                    f"-DOUT={(framework / 'runtime/include/overlay_codegen_hash.h').as_posix()}",
                    "-P", str(framework / "runtime/hash_codegen.cmake")], check=True)
    expected = compiler.codegen_hash(str(framework / "runtime/include"))
    actual = int(subprocess.check_output([str(recompiler), "--codegen-hash"], text=True).strip(), 16)
    if not expected or expected != actual:
        raise ValueError("Native slice emitter/runtime codegen identities differ")
    output.mkdir(parents=True, exist_ok=True)
    main = output / "overlays_static.c"
    args = argparse.Namespace(recompiler=str(recompiler), game_toml=str(game_toml),
                              project_root=str(framework), runtime_include=str(framework / "runtime/include"),
                              cps=True, root_enrichment=False)
    config = compiler.tomllib.loads(game_toml.read_text(encoding="utf-8"))
    parts, variants, inventories, manifests = [], [], [], []
    logs = []
    for index, (executable, record) in enumerate(records):
        result = compiler.static_capture_job(record, args, config, set(), str(main))
        logs.append(result["log"])
        write_text(output / "generation.log", "\n".join(logs))
        if result["outcome"] != "ok":
            raise ValueError(f"Native slice generation failed: {result['fail']}; see {output / 'generation.log'}")
        part = result["part"]
        entries = {int(e, 16) for e in record["dispatch_entry_pcs"]}
        if set(part["func_addrs"]) != entries or len(part["variants"]) != len(entries):
            raise ValueError("Native slice emitted unexpected functions or variants")
        base, end = int(record["load_addr"], 16), int(record["load_addr"], 16) + record["size"]
        text = "# Private linked native slice ranges; no instruction bytes\n"
        for v in part["variants"]:
            text += f"F {v['addr']:08X}\n"
            for lo, size in v["ranges"]:
                if lo % 4 or size <= 0 or size % 4 or not base <= lo < lo + size <= end:
                    raise ValueError("Emitted native range escapes its verified input")
                text += f"R {lo:08X} {size:X}\n"
        manifest = output / f"slice-{index}.ranges"
        write_text(manifest, text)
        manifests.append(manifest)
        # Metadata only: distinguish overlapping executable occupants during
        # private qualification without publishing instruction bytes.
        source_bytes = base64.b64decode(record["bytes_b64"], validate=True)
        identities = []
        for v in part["variants"]:
            covered = b"".join(source_bytes[lo-base:lo-base+length]
                               for lo, length in v["ranges"])
            identities.append(dict(owner=v["addr"], crc=v["crc"],
                                   code_sha256=hashlib.sha256(covered).hexdigest(),
                                   ranges=[list(r) for r in v["ranges"]]))
        resumes = add_resumes(compiler, part)
        inventories.append(dict(executable=executable, ranges=manifest.name, entries=sorted(entries),
                                resume_entries=resumes, identities=identities))
        parts.append(part)
        variants.extend(part["variants"])
    files = compiler.write_static_outputs(str(main), parts, variants,
                                          compiler.generate_overlay_dispatch(variants))
    paths = [Path(p) for p in files] + manifests
    receipt = dict(schema=1, codegen_hash=f"{expected:08x}", slices=inventories,
                   files={p.name: digest(p) for p in paths})
    receipt_path = output / "game-slices.json"
    write_text(receipt_path, json.dumps(receipt, indent=2) + "\n")
    return receipt_path


def prepare_native(installation: Path, framework: Path, recompiler: Path,
                   game_toml: Path, output: Path, cmake="cmake") -> Path:
    identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
    specs = json.loads((ROOT / "configs/native_usa.json").read_text())
    records = []
    for spec in specs:
        expected = next(e for e in identity["executables"] if e["path"] == spec["executable"])
        path = installation / "executables" / spec["executable"]
        if path.stat().st_size != expected["size"] or digest(path) != expected["sha256"]:
            raise ValueError(f"Native slice executable changed: {path.name}")
        data = path.read_bytes()
        header = exe_header(data)
        start, size = int(spec["start"], 16), spec["size"]
        offset = start - header["load_address"]
        if offset < 0 or size <= 0 or offset + size > header["text_size"]:
            raise ValueError("Native slice outside verified executable payload")
        body = data[2048 + offset:2048 + offset + size]
        records.append((path.name, capture(body, start, [int(e, 16) for e in spec["entries"]])))
    return emit(records, framework, recompiler, game_toml, output, cmake)
