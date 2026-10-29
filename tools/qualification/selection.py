#!/usr/bin/env python3
"""Build private, identity-qualified selectors from verified metadata receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from n2o_disc import digest
from route import private_output


def build_selection(receipt, specs):
    wanted = {}
    for spec in specs:
        for entry in spec["entries"]:
            key = (spec["executable"], int(entry, 16))
            if key in wanted:
                raise ValueError("Duplicate selected image/owner")
            wanted[key] = spec
    if not wanted:
        raise ValueError("Empty selection")
    groups, crc_occupants, found = {}, {}, set()
    for item in receipt["slices"]:
        image = item["executable"]
        for identity in item.get("identities", []):
            owner = identity["owner"]
            key = (image, owner)
            if key not in wanted:
                continue
            spec = wanted[key]
            start, size = int(spec["start"], 16), spec["size"]
            if owner not in item["entries"] or not start <= owner < start+size:
                raise ValueError("Identity has no selected root")
            ranges = identity["ranges"]
            if not ranges or len(ranges) > 4096 or any(
                lo % 4 or length <= 0 or length % 4 or not start <= lo < lo+length <= start+size
                for lo, length in ranges
            ):
                raise ValueError("Identity range outside selected input")
            crc, sha = identity["crc"], identity["code_sha256"]
            if not isinstance(crc, int) or not 0 <= crc <= 0xffffffff or len(sha) != 64:
                raise ValueError("Invalid code identity")
            try:
                bytes.fromhex(sha)
            except ValueError as exc:
                raise ValueError("Invalid code identity") from exc
            pcs = sorted({owner} | {r["entry"] for r in item["resume_entries"] if r["owner"] == owner})
            if any(pc % 4 or not any(lo <= pc < lo+length for lo, length in ranges) for pc in pcs):
                raise ValueError("PC lacks guarded owner range")
            gate_key = json.dumps([owner, crc, ranges], separators=(",", ":"))
            if gate_key in crc_occupants and crc_occupants[gate_key] != sha:
                raise ValueError("Ambiguous CRC occupants require separate qualification")
            crc_occupants[gate_key] = sha
            canonical = json.dumps([owner, crc, sha, ranges, pcs], separators=(",", ":"))
            token = hashlib.sha256(canonical.encode()).hexdigest()[:16].upper()
            if token == "0000000000000000":
                raise ValueError("Reserved identity token")
            if token not in groups:
                groups[token] = dict(id=token, start=start, size=size, owner=owner, crc=crc,
                                     code_sha256=sha, ranges=ranges, pcs=pcs, images=[])
            group = groups[token]
            if (group["owner"], group["crc"], group["code_sha256"], group["ranges"], group["pcs"]) != (owner, crc, sha, ranges, pcs):
                raise ValueError("Identity token collision")
            end = max(group["start"]+group["size"], start+size)
            group["start"] = min(group["start"], start)
            group["size"] = end-group["start"]
            group["images"].append(dict(executable=image, owner=owner))
            found.add(key)
    if found != set(wanted):
        raise ValueError("Missing selected identities; rebuild with the current prepare_native.py")
    return sorted(groups.values(), key=lambda row: row["id"])


def selection_text(rows):
    lines = ["v2"]
    for row in rows:
        values = [int(row["id"], 16), row["start"], row["size"], row["crc"],
                  len(row["ranges"]), len(row["pcs"])]
        values += [v for pair in row["ranges"] for v in pair]
        values += row["pcs"]
        lines.append(" ".join(f"{value:X}" for value in values))
    return "\n".join(lines)+"\n"


def read_selection(path):
    lines = [line.split() for line in Path(path).read_text().splitlines() if line.strip()]
    if not lines:
        raise ValueError("Empty selection")
    v2 = lines[0] == ["v2"]
    rows = []
    for fields in lines[1:] if v2 else lines:
        values = [int(value, 16) for value in fields]
        if not v2:
            if len(values) != 2:
                raise ValueError("Invalid legacy selector")
            rows.append(dict(id="0000000000000000", start=values[0], size=values[1], pcs=None))
        else:
            if len(values) < 6:
                raise ValueError("Truncated identity selector")
            token, start, size, crc, nr, np = values[:6]
            if not token or token > 0xffffffffffffffff or not 0 < nr <= 4096 or not 0 < np <= 0x80000 or len(values) != 6+2*nr+np:
                raise ValueError("Invalid identity selector")
            if any(v > 0xffffffff for v in values[1:]):
                raise ValueError("Oversized identity selector word")
            rows.append(dict(id=f"{token:016X}", start=start, size=size, crc=crc,
                             ranges=[values[i:i+2] for i in range(6, 6+2*nr, 2)],
                             pcs=values[6+2*nr:]))
    if not rows:
        raise ValueError("Empty selection")
    seen = set()
    for row in rows:
        start, size = row["start"], row["size"]
        if start % 4 or size <= 0 or size % 4 or not 0x80010000 <= start < start+size <= 0x80200000:
            raise ValueError("Invalid selector geometry")
        if row["pcs"] is not None:
            if row["id"] in seen:
                raise ValueError("Duplicate identity selector")
            seen.add(row["id"])
            if any(lo % 4 or length <= 0 or length % 4 or not start <= lo < lo+length <= start+size
                   for lo, length in row["ranges"]):
                raise ValueError("Invalid selector code range")
            pcs = row["pcs"]
            if pcs != sorted(set(pcs)) or start not in pcs or any(
                pc % 4 or not any(lo <= pc < lo+length for lo, length in row["ranges"]) for pc in pcs
            ):
                raise ValueError("Invalid selector PC ownership")
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--roots", required=True, type=Path)
    p.add_argument("--output", required=True, type=private_output)
    args = p.parse_args()
    receipt = json.loads(args.manifest.read_text())
    for name, expected in receipt["files"].items():
        if Path(name).name != name or digest(args.manifest.parent/name) != expected:
            raise ValueError("Private generated receipt changed")
    rows = build_selection(receipt, json.loads(args.roots.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(selection_text(rows))
    args.output.with_suffix(".json").write_text(json.dumps(rows, indent=2)+"\n")
    print(f"Private selector: {len(rows)} code identities for {sum(len(r['images']) for r in rows)} image/owners")


if __name__ == "__main__":
    main()
