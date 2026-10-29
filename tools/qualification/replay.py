#!/usr/bin/env python3
"""Replay captured segments with original GTE boundary inputs; no game data ships."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from route import ROOT, private_output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--output", required=True, type=private_output)
    p.add_argument("--selection", required=True, type=Path)
    p.add_argument("--binary", type=Path, default=ROOT / ".local/runtime-dev/build/NitrogenSquared-dev")
    p.add_argument("--bios", type=Path, default=ROOT / ".local/runtime-dev/build/bios/openbios.bin")
    p.add_argument("--keep-going", action="store_true",
                   help="Collect isolated replay failures; still exit unsuccessfully if any fail")
    args = p.parse_args()
    selection = [tuple(int(x, 16) for x in line.split()) for line in args.selection.read_text().splitlines()]
    if not selection or any(len(row) != 2 for row in selection):
        raise ValueError("Invalid selection metadata")
    args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(N2O_COMPARE="1", N2O_REPLAY="1", N2O_SELECTION=str(args.selection.resolve()))
    results = []
    failures = []
    for witness in sorted(args.source.glob("call-*.bin")):
        pc = int(witness.stem.split("-")[1], 16)
        if not any(lo <= pc < lo + size for lo, size in selection):
            continue
        out = args.output / f"{pc:08X}"
        out.mkdir(exist_ok=True)
        command = [str(args.binary.resolve()), str(witness.resolve()), str(args.bios.resolve()), hex(pc)]
        try:
            result = subprocess.run(command, cwd=out, env=env, capture_output=True, text=True, timeout=40)
            code, log = result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired as exc:
            code, log = -99, str(exc.stdout) + "\nTIMEOUT"
        (out / "runtime.log").write_text(log)
        summary = (out / "qualification-summary.txt").read_text().splitlines()[0] if (out / "qualification-summary.txt").exists() else ""
        results.append(dict(pc=f"{pc:08X}", returncode=code, summary=summary))
        (args.output / "results.json").write_text(json.dumps(results, indent=2))
        if code or "comparisons=25 failures=0" not in summary:
            message = f"Replay failed: {pc:08X}: {code}: {summary}\n{log[-2000:]}"
            if not args.keep_going:
                raise RuntimeError(message)
            failures.append(f"{pc:08X}")
            print(message, flush=True)
        if len(results) % 25 == 0:
            print(len(results), f"{pc:08X}", summary, flush=True)
    if not results:
        raise RuntimeError("No selected witnesses")
    if failures:
        raise RuntimeError("Unqualified replay PCs: " + ", ".join(failures))
    print("ALL_SEGMENT_REPLAYS_PASS", len(results), flush=True)


if __name__ == "__main__":
    main()
