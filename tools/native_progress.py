#!/usr/bin/env python3
"""Count linked native translation ranges, never host code or analysis-only output.

The denominator is the three PS-X EXE payload sizes, including embedded data.
This is a conservative translation-coverage metric, not project completion or
the percentage of instructions executed natively during a particular scene.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from n2o_disc import ROOT, digest, exe_header


def covered_ranges(text: str, base: int, size: int) -> tuple[int, int]:
    spans, functions = [], set()
    for line in text.splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "F" and len(fields) == 2:
            functions.add(int(fields[1], 16))
        elif fields[0] == "R" and len(fields) == 3:
            start, length = int(fields[1], 16), int(fields[2], 16)
            if start % 4 or length <= 0 or length % 4 or start < base or start + length > base + size:
                raise ValueError("Translation range is outside the executable or is not instruction-aligned")
            spans.append((start, start + length))
        else:
            raise ValueError("Unsupported native range manifest")
    merged = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return sum(end - start for start, end in merged), len(functions)


def report(work: Path) -> dict:
    receipt = json.loads((work / "runtime-build.json").read_text())
    if not receipt.get("build_succeeded") or "linked_executables" not in receipt:
        raise ValueError("Rebuild with the current build_runtime.py before measuring native coverage")
    identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
    generated = Path(receipt["generated_dir"])
    installation = Path(receipt["installation"])
    linked = set(receipt["linked_executables"])
    known = {e["path"] for e in identity["executables"]}
    if linked - known:
        raise ValueError("Unknown executable in build receipt")
    rows = []
    for expected in identity["executables"]:
        name = expected["path"]
        exe = installation / "executables" / name
        if exe.stat().st_size != expected["size"] or digest(exe) != expected["sha256"]:
            raise ValueError(f"Extracted executable changed: {name}")
        header = exe_header(exe.read_bytes())
        count = functions = 0
        if name in linked:
            ranges = generated / name / (name + "_full.ranges")
            count, functions = covered_ranges(ranges.read_text(), header["load_address"], header["text_size"])
        rows.append(dict(executable=name, linked=name in linked, native_range_bytes=count,
                         payload_bytes=header["text_size"], linked_functions=functions,
                         percent=round(100 * count / header["text_size"], 4)))
    native = sum(row["native_range_bytes"] for row in rows)
    total = sum(row["payload_bytes"] for row in rows)
    return dict(schema=1, metric="linked-native-ranges / original-executable-payload-bytes",
                percent=round(100 * native / total, 4), native_range_bytes=native,
                payload_bytes=total, executables=rows,
                caveat="Payloads include embedded data. Excludes BIOS, host services and analysis-only C. "
                       "Not project completion or scene-weighted native execution.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work-dir", type=Path, default=ROOT / ".local/runtime-dev")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        result = report(args.work_dir.resolve())
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Linked native translation coverage: {result['percent']:.2f}%")
        for row in result["executables"]:
            print(f"  {row['executable']}: {row['percent']:.2f}% ({row['linked_functions']} linked functions)")
        print(result["caveat"])
    except (OSError, ValueError, KeyError) as e:
        p.exit(1, f"Native progress failed: {e}\n")


if __name__ == "__main__":
    main()
