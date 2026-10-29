#!/usr/bin/env python3
"""Replay captured segments with original GTE boundary inputs; no game data ships."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from route import ROOT, private_output
from selection import read_selection


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
    selection = read_selection(args.selection)
    args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for option in ("N2O_COLLECT_FAILURES", "N2O_BLOCKED_IDS", "N2O_TRACE_MISSES"):
        env.pop(option, None)
    env.update(N2O_COMPARE="1", N2O_REPLAY="1", N2O_SELECTION=str(args.selection.resolve()))
    results = []
    failures = []
    for witness in sorted(args.source.glob("call-*.bin")):
        fields = witness.stem.split("-")[1:]
        if len(fields) not in (1, 2):
            raise ValueError("Invalid witness filename")
        token = f"{int(fields[0],16):016X}" if len(fields) == 2 else "0000000000000000"
        pc = int(fields[-1], 16)
        if not any(row["id"] == token and
                   (pc in row["pcs"] if row["pcs"] is not None else row["start"] <= pc < row["start"]+row["size"])
                   for row in selection):
            continue
        label = f"{token}-{pc:08X}" if int(token, 16) else f"{pc:08X}"
        out = args.output / label
        out.mkdir(exist_ok=True)
        env["N2O_REPLAY_ID"] = token
        command = [str(args.binary.resolve()), str(witness.resolve()), str(args.bios.resolve()), hex(pc)]
        try:
            result = subprocess.run(command, cwd=out, env=env, capture_output=True, text=True, timeout=40)
            code, log = result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired as exc:
            code, log = -99, str(exc.stdout) + "\nTIMEOUT"
        (out / "runtime.log").write_text(log)
        summary = (out / "qualification-summary.txt").read_text().splitlines()[0] if (out / "qualification-summary.txt").exists() else ""
        results.append(dict(identity=token, pc=f"{pc:08X}", returncode=code, summary=summary))
        (args.output / "results.json").write_text(json.dumps(results, indent=2))
        if code or "comparisons=25 failures=0" not in summary:
            message = f"Replay failed: {label}: {code}: {summary}\n{log[-2000:]}"
            if not args.keep_going:
                raise RuntimeError(message)
            failures.append(label)
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
