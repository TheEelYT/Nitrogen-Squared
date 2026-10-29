#!/usr/bin/env python3
"""Launch the private development runtime and retain its startup log locally."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
from build_runtime import load_installation
from n2o_disc import ROOT


def runtime_environment(work: Path, display_ring: bool = False, show_fps: bool = False,
                        render_worker: bool | None = None) -> dict[str, str]:
    env = os.environ.copy()
    # Full-VRAM history takes a synchronous GPU readback every frame. Keep
    # one-shot diagnostics available without paying that cost during play.
    env["PSX_DISPLAY_RING"] = "1" if display_ring else "0"
    env.setdefault("PSX_DEBUG_TOGGLES", "0")
    if render_worker is None:
        env.setdefault("PSX_RENDER_THREAD", "1")
    else:
        env["PSX_RENDER_THREAD"] = "1" if render_worker else "0"
    # One closed frame of lookahead bounds queued work and controller latency.
    env.setdefault("PSX_RENDER_THREAD_FRAMES", "1")
    if show_fps:
        env["PSX_FPS_TELEMETRY"] = "1"
    # Captures and caches are private. Overlay compilation has no configured
    # recipe yet; do not invoke the upstream default shell recipe.
    env["PSX_OVERLAY_AUTOCOMPILE_OFF"] = "1"
    env["PSX_OVERLAY_CAPTURES"] = str(work / "overlay_captures.json")
    env["PSX_OVERLAY_CAPTURE_ROOT"] = str(work / "overlay-private")
    return env


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work-dir", type=Path, default=ROOT / ".local/runtime-dev")
    p.add_argument("--save-dir", type=Path, help="Private save folder (default: work-dir/saves)")
    p.add_argument("--renderer", choices=["software", "opengl"], default="opengl")
    p.add_argument("--render-worker", choices=["on", "off"],
                   help="OpenGL render worker (default: on; environment override honored)")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--display-ring", action="store_true",
                   help="Expensive full-VRAM frame history for developer diagnosis")
    p.add_argument("--show-fps", action="store_true", help="Show guest FPS and speed in the window title")
    p.add_argument("--debug-port", type=int, default=4370)
    args = p.parse_args()
    try:
        work = args.work_dir.resolve()
        record = json.loads((work / "runtime-build.json").read_text())
        if not record.get("build_succeeded") or record.get("public_distribution_allowed") is not False:
            raise ValueError("No complete private development build is recorded")
        current = load_installation(Path(record["installation"]))
        if current["bin_sha256"] != record.get("disc_sha256"):
            raise ValueError("Build and installed disc do not match")
        if not 1024 <= args.debug_port <= 65535:
            raise ValueError("Use a debug port from 1024 through 65535")
        command = [record["executable"], "--game", record["config"], "--no-launcher",
                   "--renderer", args.renderer, "--debug-port", str(args.debug_port),
                   "--memcard-dir", str(args.save_dir.resolve() if args.save_dir else work / "saves")]
        if args.headless:
            command.append("--headless")
        if args.display_ring and record.get("diagnostics_enabled") is False:
            raise ValueError("--display-ring requires a build made with build_runtime.py --diagnostics")
        worker = None if args.render_worker is None else args.render_worker == "on"
        if args.renderer != "opengl": worker = False
        env = runtime_environment(work, args.display_ring, args.show_fps, worker)
        env["NITROGEN_NATIVE_DISC_BIN"] = current["bin"]
        with (work / "runtime.log").open("w", encoding="utf-8") as log:
            proc = subprocess.Popen(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
            print(f"Runtime started (PID {proc.pid}). Log: {work / 'runtime.log'}", flush=True)
            try:
                return proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                return 130
    except (OSError, ValueError) as e:
        p.exit(1, f"Cannot start runtime: {e}\n")


if __name__ == "__main__":
    raise SystemExit(main())
