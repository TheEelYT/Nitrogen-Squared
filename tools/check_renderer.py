#!/usr/bin/env python3
"""Run the pinned renderer's original LLE/HLE pixel-equivalence fixture on Linux.

Uses an already built SDL3 and synthetic texture/primitive data only. It does
not execute N2O or read the player's disc, captures, saves or generated code.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from build_recompiler import verify_framework
from n2o_disc import ROOT


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--framework", type=Path, default=ROOT / ".local/psxrecomp")
    p.add_argument("--runtime-build", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT / ".local/renderer-check")
    p.add_argument("--cc", default="gcc")
    p.add_argument("--cxx", default="g++")
    args = p.parse_args()
    if not sys.platform.startswith("linux"):
        p.error("This synthetic OpenGL check uses the Linux offscreen EGL backend")
    framework, build, out = (x.resolve() for x in (args.framework, args.runtime_build, args.output))
    verify_framework(framework)
    sdl = build / "_deps"
    library = sdl / "sdl3-build/libSDL3.a"
    if not library.is_file():
        p.error(f"Build the runtime first; missing SDL3 static library: {library}")
    out.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(SDL_VIDEODRIVER="offscreen", SDL_AUDIODRIVER="dummy", EGL_PLATFORM="surfaceless")
    receipt = []

    def run(command):
        result = subprocess.run([str(x) for x in command], cwd=out, env=env,
                                capture_output=True, text=True, errors="replace", timeout=180)
        receipt.append(dict(command=[str(x) for x in command], exit=result.returncode,
                            stdout=result.stdout, stderr=result.stderr))
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return result

    sources = [framework / "runtime/tests/test_gl_readback_region.c"]
    sources += [framework / "runtime/src" / (name + ".c") for name in (
        "gpu_sw_renderer", "render_pass_plan", "psx_openxr", "render_thread",
        "present_thread", "frame_gen", "host_overlay")]
    includes = ["-I" + str(framework / "runtime/include"),
                "-I" + str(framework / "runtime/src"), "-I" + str(sdl / "sdl3-src/include")]
    objects = []
    for index, source in enumerate(sources):
        obj = out / f"fixture-{index}.o"
        run([args.cc, "-std=c11", "-O2", "-flto", "-D_GNU_SOURCE=1", "-pthread",
             "-DPSX_SDL3=1", "-DPSX_NO_DEBUG_TOOLS=1",
             *includes, "-c", source, "-o", obj])
        objects.append(obj)
    executable = out / "renderer-check"
    run([args.cxx, "-O2", "-flto", *objects, library, "-l:libGL.so.1", "-lm", "-ldl", "-lpthread", "-lrt", "-o", executable])
    for scale in (1, 4):
        result = run([executable, scale])
        lines = result.stdout.rstrip().splitlines()
        summary = re.fullmatch(r"checks=(\d+) failures=0", lines[-1]) if lines else None
        if not summary or int(summary[1]) == 0 or "FAIL " in result.stderr:
            raise RuntimeError("Renderer fixture did not report a complete passing result")
        print(f"OpenGL LLE/HLE equivalence at {scale}x: {lines[-1]}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
        raise SystemExit(f"Renderer check failed: {e}")
