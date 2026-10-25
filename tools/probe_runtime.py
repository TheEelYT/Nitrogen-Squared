#!/usr/bin/env python3
"""Collect bounded runtime status, excluding RAM, code captures and screenshots."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import socket

FIELDS = {
    "frame": ("frame",),
    "get_registers": ("pc", "frame"),
    "gpu_state": ("width", "height", "depth24", "disabled", "display_x", "display_y", "gp0_draw", "gp0_writes"),
    "cdrom_state": ("has_disc", "reading", "read_msf", "last_sector"),
    "dispatch_stats": ("static_hits", "miss_total", "miss_unique"),
    "overlay_loader_status": ("active", "registered", "dispatch_native", "dispatch_interp_fallback", "stale_blocked"),
    "dirty_ram_stats": ("blocks_run", "insns_run", "aborts", "guard_yields", "native_handoffs"),
}


def request(port: int, command: str) -> dict:
    with socket.create_connection(("127.0.0.1", port), timeout=3) as sock:
        sock.settimeout(5)
        sock.sendall((json.dumps({"id": 1, "cmd": command}) + "\n").encode())
        data = bytearray()
        while len(data) < 2 * 1024 * 1024:
            chunk = sock.recv(65536)
            if not chunk:
                break
            data.extend(chunk)
            try:
                reply = json.loads(data)
            except json.JSONDecodeError:
                continue
            if not isinstance(reply, dict):
                raise ValueError("Unexpected debug reply")
            if not reply.get("ok"):
                raise ValueError(reply.get("error", reply.get("err", "Debug command failed")))
            if reply.get("id") != 1:
                raise ValueError("Unexpected debug response ID")
            return {key: reply[key] for key in FIELDS[command] if key in reply}
        raise ValueError("Incomplete or oversized debug response")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=4370)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    if not 1024 <= args.port <= 65535:
        p.error("Use a port from 1024 through 65535")
    report = {"schema": 1, "runtime_probe": {}}
    failed = False
    for command in FIELDS:
        try:
            report["runtime_probe"][command] = request(args.port, command)
        except (OSError, ValueError) as e:
            failed = True
            report["runtime_probe"][command] = {"error": str(e)}
    text = json.dumps(report, indent=2) + "\n"
    print(text, end="")
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
