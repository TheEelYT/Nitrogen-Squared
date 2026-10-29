#!/usr/bin/env python3
"""Link an original controller fixture separately; do not alter production binaries."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
from route import ROOT, private_output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=private_output)
    p.add_argument("--disc", required=True, type=Path)
    p.add_argument("--qualified-manifest", required=True, type=Path)
    args = p.parse_args()
    work = ROOT / ".local/runtime-dev"
    build = work / "build"
    receipt = json.loads((work / "runtime-build.json").read_text())
    if receipt["diagnostics_enabled"]:
        raise ValueError("A normal diagnostics-disabled build is required")
    normal = json.loads(Path(receipt["native_slices"][0]["manifest"]).read_text())
    if normal != json.loads(args.qualified_manifest.read_text()):
        raise ValueError("Production selection differs from qualified source/range hashes")
    args.output.mkdir(parents=True, exist_ok=True)
    obj = args.output / "normal_controller.o"
    subprocess.run(["g++", "-std=c++17", "-O2", "-DPSX_SDL3=1",
                    "-I" + str(ROOT / ".local/psxrecomp/runtime/include"),
                    "-I" + str(build / "_deps/sdl3-src/include"), "-c",
                    str(Path(__file__).with_name("normal_controller.cpp")), "-o", str(obj)], check=True)
    command = shlex.split((build / "CMakeFiles/nitrogen-runtime.dir/link.txt").read_text())
    if any("qualification/" in x or "--wrap=" in x for x in command):
        raise ValueError("Production link still contains qualification interposition")
    binary = args.output / "NitrogenSquared-controller-fixture"
    command[command.index("-o") + 1] = str(binary)
    command[1:1] = ["-Wl,--wrap=SDL_PollEvent", str(obj)]
    subprocess.run(command, cwd=build, check=True)
    env = os.environ.copy()
    env.update(SDL_VIDEODRIVER="offscreen", SDL_AUDIODRIVER="dummy", EGL_PLATFORM="surfaceless",
               PSX_DISPLAY_RING="0", PSX_OVERLAY_AUTOCOMPILE_OFF="1", PSX_DEBUG_TOGGLES="0",
               PSX_RENDER_THREAD="1", PSX_RENDER_THREAD_FRAMES="1",
               NITROGEN_NATIVE_DISC_BIN=str(args.disc.resolve()),
               PSX_OVERLAY_CAPTURES=str(args.output / "overlay_captures.json"),
               PSX_OVERLAY_CAPTURE_ROOT=str(args.output / "overlay-private"))
    # The bundled BIOS is resolved relative to this separate executable.
    import shutil
    shutil.copytree(build / "bios", args.output / "bios", dirs_exist_ok=True)
    with (args.output / "runtime.log").open("w") as log:
        result = subprocess.run([str(binary), "--game", str(work / "game.toml"), "--no-launcher",
                                 "--renderer", "opengl", "--hidden-window", "--memcard-dir", str(args.output / "cards")],
                                cwd=args.output, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=240)
    log = (args.output / "runtime.log").read_text()
    if result.returncode or log.count("native movie complete (end)") != 3 or "NORMAL_SMOKE requested SDL_QUIT" not in log or "nitrogen: native game slice: dispatches=" not in log:
        raise RuntimeError("Normal fixture failed; inspect its private runtime.log")
    print("Normal selected source/range hashes match the qualified build.")
    print("\n".join(line for line in log.splitlines() if "nitrogen:" in line or "NORMAL_SMOKE" in line))
    print("NORMAL_SMOKE_PASS")


if __name__ == "__main__":
    main()
