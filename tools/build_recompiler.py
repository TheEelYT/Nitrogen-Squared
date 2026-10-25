#!/usr/bin/env python3
"""Build the pinned upstream analysis tool in a private developer directory."""
from __future__ import annotations
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_URL = "https://github.com/RetroPortingToolKit/psxrecomp.git"
FRAMEWORK_REV = "f42d2c004b3dd6ef6ccb83101b40ede55f24bf59"


def verify_framework(path: Path):
    head = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if head != FRAMEWORK_REV:
        raise ValueError(f"Framework revision mismatch: expected {FRAMEWORK_REV}, got {head}")
    for extra in ([], ["--cached"]):
        subprocess.run(["git", "-C", str(path), "diff", "--exit-code", *extra], check=True)


def build(framework: Path, build_dir: Path, cmake="cmake", bios=False):
    framework = framework.resolve()
    if not framework.exists():
        framework.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--no-checkout", FRAMEWORK_URL, str(framework)], check=True)
        subprocess.run(["git", "-C", str(framework), "checkout", "--detach", FRAMEWORK_REV], check=True)
    verify_framework(framework)
    subprocess.run([cmake, "-S", str(framework / "recompiler"), "-B", str(build_dir.resolve()),
                    "-DCMAKE_BUILD_TYPE=Release", "-DPSXRECOMP_ENABLE_CHD=OFF", "-DBUILD_TESTING=OFF"], check=True)
    targets = ["psxrecomp-game"] + (["psxrecomp-bios"] if bios else [])
    subprocess.run([cmake, "--build", str(build_dir.resolve()), "--config", "Release",
                    "--target", *targets, "--parallel", "2"], check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--framework", type=Path, default=ROOT / ".local/psxrecomp")
    p.add_argument("--build-dir", type=Path, default=ROOT / ".local/build-recompiler")
    p.add_argument("--cmake", default="cmake")
    args = p.parse_args()
    build(args.framework, args.build_dir, args.cmake)


if __name__ == "__main__":
    main()
