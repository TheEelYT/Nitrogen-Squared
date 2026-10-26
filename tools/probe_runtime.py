#!/usr/bin/env python3
"""Collect bounded runtime status, excluding RAM, code captures and screenshots."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import socket
import time

FIELDS = {
    "frame": ("frame",),
    "get_registers": ("pc", "frame"),
    "gpu_state": ("width", "height", "depth24", "disabled", "display_x", "display_y", "gp0_draw", "gp0_writes",
                  "h_display", "v_display", "hres1", "hres2", "draw_area"),
    "cdrom_state": ("has_disc", "reading", "read_msf", "last_sector"),
    "dispatch_stats": ("static_hits", "miss_total", "miss_unique"),
    "overlay_loader_status": ("active", "registered", "dispatch_native", "dispatch_interp_fallback", "stale_blocked"),
    "dirty_ram_stats": ("blocks_run", "insns_run", "aborts", "guard_yields", "native_handoffs"),
    "perf": ("valid", "measurement", "fps", "swaps", "span_ms", "mean_us", "p95_us", "p99_us", "hitches"),
    "audio_stats": ("pump_calls", "pump_skips", "underruns", "out.active", "out.mode", "out.host_rate",
                    "out.fill_ms", "out.target_ms", "out.underruns", "out.overflow_drops"),
    "pad_status": ("slot0.buttons", "slot0.connected", "slot0.type", "slot0.sticks", "slot1.connected"),
}


def select_fields(reply: dict, fields: tuple[str, ...]) -> dict:
    selected = {}
    for field in fields:
        keys = field.split(".")
        source, target = reply, selected
        for key in keys[:-1]:
            source = source.get(key)
            if not isinstance(source, dict):
                break
            target = target.setdefault(key, {})
        else:
            if keys[-1] in source:
                target[keys[-1]] = source[keys[-1]]
    return selected


def request(port: int, command: str) -> dict:
    if command not in FIELDS:
        raise ValueError("Command is outside the status allowlist")
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
            return select_fields(reply, FIELDS[command])
        raise ValueError("Incomplete or oversized debug response")


def sample_speed(port: int, seconds: int) -> dict:
    start = request(port, "frame")["frame"]
    before = time.monotonic()
    time.sleep(seconds)
    end = request(port, "frame")["frame"]
    elapsed = time.monotonic() - before
    if elapsed <= 0 or end < start:
        raise ValueError("Runtime frame counter restarted during the sample")
    rate = (end - start) / elapsed
    return {"elapsed_seconds": round(elapsed, 3), "guest_frames": end - start,
            "guest_frames_per_second": round(rate, 2),
            "ntsc_speed_percent": round(rate / (60000 / 1001) * 100, 1)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=4370)
    p.add_argument("--output", type=Path)
    p.add_argument("--seconds", type=int, default=0,
                   help="Sample guest frame speed for 1–60 seconds (0 skips sampling)")
    args = p.parse_args()
    if not 1024 <= args.port <= 65535:
        p.error("Use a port from 1024 through 65535")
    if not 0 <= args.seconds <= 60:
        p.error("Use a sample duration from 0 through 60 seconds")
    report = {"schema": 1, "runtime_probe": {}}
    failed = False
    for command in FIELDS:
        try:
            report["runtime_probe"][command] = request(args.port, command)
        except (OSError, ValueError) as e:
            failed = True
            report["runtime_probe"][command] = {"error": str(e)}
    if args.seconds:
        try:
            report["speed_sample"] = sample_speed(args.port, args.seconds)
        except (OSError, ValueError, KeyError) as e:
            failed = True
            report["speed_sample"] = {"error": str(e)}
    text = json.dumps(report, indent=2) + "\n"
    print(text, end="")
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
