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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work-dir", type=Path, default=ROOT / ".local/runtime-dev")
    p.add_argument("--renderer", choices=["software", "opengl"], default="opengl")
    p.add_argument("--headless", action="store_true")
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
                   "--memcard-dir", str(work / "saves")]
        if args.headless:
            command.append("--headless")
        env = os.environ.copy()
        # Captures and caches are private, and automated overlay compilation is
        # not yet integrated. Do not accidentally invoke upstream's default shell recipe.
        env["PSX_OVERLAY_AUTOCOMPILE_OFF"] = "1"
        env["PSX_OVERLAY_CAPTURES"] = str(work / "overlay_captures.json")
        env["PSX_OVERLAY_CAPTURE_ROOT"] = str(work / "overlay-private")
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
