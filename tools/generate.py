#!/usr/bin/env python3
"""Generate private, separate analysis translations; this does not build a game.

Only the EXE header entry is trusted initially. Reachable discovery avoids
treating arbitrary data-table words as MIPS functions. Executables sharing RAM
addresses remain separate until their loader/identity contract is validated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from build_recompiler import FRAMEWORK_REV, verify_framework
from n2o_disc import ROOT, DiscError, exe_header


def generate(installation: Path, framework: Path, recompiler: Path, output: Path) -> dict:
    installation, framework, recompiler, output = (p.resolve() for p in (installation, framework, recompiler, output))
    verify_framework(framework)
    identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
    manifest = json.loads((installation / "installation.json").read_text())
    if manifest.get("game_id") != identity["game_id"] or manifest.get("bin_sha256") != identity["bin_sha256"]:
        raise DiscError("Installation does not match the verified disc")
    # Validate all local inputs before writing output or invoking an external tool.
    inputs = []
    for expected in identity["executables"]:
        path = installation / "executables" / expected["path"]
        data = path.read_bytes()
        if len(data) != expected["size"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise DiscError(f"Local executable has changed: {path.name}")
        inputs.append((path, exe_header(data)))
    if output.exists():
        raise DiscError("Generation destination exists; use a new private output directory")
    output.mkdir(parents=True)
    result = dict(schema=1, framework_revision=FRAMEWORK_REV, runtime_ready=False, executables=[])
    for path, header in inputs:
        dest = output / path.name
        dest.mkdir()
        seed = dest / "entry.txt"
        seed.write_text(f"0x{header['entry_pc']:08X}\n", encoding="utf-8")
        # JSON string quoting is compatible with TOML basic strings for these paths.
        q = lambda v: json.dumps(str(v))
        config = dest / "analysis.toml"
        config.write_text(
            f'[game]\nname = "Nitrogen Squared analysis"\nid = "SLUS-00637"\nexe = {q(path)}\n'
            f'load_address = "0x{header["load_address"]:08X}"\n'
            f'entry_pc = "0x{header["entry_pc"]:08X}"\n'
            f'text_size = "0x{header["text_size"]:X}"\n'
            f'stack_base = "0x{header["stack_base"]:08X}"\n\n'
            f'[recompiler]\nseeds = {q(seed)}\nout_dir = {q(dest)}\nstrict = true\n'
            f'discovery = "reachable"\nbios_config = {q(framework / "bios/OpenBIOS.toml")}\n',
            encoding="utf-8")
        with (dest / "generation.log").open("w", encoding="utf-8") as log:
            proc = subprocess.run([str(recompiler), "--config", str(config), "--project-root", str(framework)],
                                  cwd=dest, stdout=log, stderr=subprocess.STDOUT)
        row = dict(executable=path.name, exit_code=proc.returncode,
                   generated_c_files=len(list(dest.glob("*.c"))), execution_verified=False)
        result["executables"].append(row)
        (output / "generation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if proc.returncode:
            raise RuntimeError(f"Generation failed for {path.name}; see {dest / 'generation.log'}")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--installation", type=Path, required=True)
    p.add_argument("--framework", type=Path, required=True)
    p.add_argument("--recompiler", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        print(json.dumps(generate(args.installation, args.framework, args.recompiler, args.output), indent=2))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
        p.exit(1, f"Generation failed: {e}\n")


if __name__ == "__main__":
    main()
