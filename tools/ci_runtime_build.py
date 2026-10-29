#!/usr/bin/env python3
"""Compile the real runtime with an original synthetic program, never game data.

This CI-only fixture validates compiler/linker integration. It cannot validate
N2O behavior, disc access, assets or audio. It is not a player import bypass.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess

from build_recompiler import build
from build_runtime import find_binary, load_execution_manifest
from n2o_disc import ROOT
from prepare_native import capture, emit


def run_smoke(binary: Path, work: Path):
    # The combined SDL/GL, audio and dispatcher fixture can cold-start slowly
    # on shared runners. Keep a bounded timeout and preserve phase receipts.
    try:
        result = subprocess.run([str(binary)], cwd=work, timeout=60,
                                capture_output=True, text=True)
    except subprocess.TimeoutExpired as exc:
        def decoded(value):
            return value.decode(errors="replace") if isinstance(value, bytes) else value or ""
        raise RuntimeError("Runtime fixture exceeded 60 seconds:\n" +
                           decoded(exc.stdout) + decoded(exc.stderr)) from exc
    if result.returncode:
        raise RuntimeError(f"Runtime input fixture exited with {result.returncode}:\n" +
                           result.stdout + result.stderr)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--framework", type=Path, default=ROOT / ".local/psxrecomp")
    p.add_argument("--work-dir", type=Path, default=ROOT / ".local/ci-runtime")
    args = p.parse_args()
    framework, work = args.framework.resolve(), args.work_dir.resolve()
    build(framework, work / "emitters", bios=True)
    bios = find_binary(work / "emitters", "psxrecomp-bios")
    game = find_binary(work / "emitters", "psxrecomp-game")
    subprocess.run([str(bios), "--config", "bios/OpenBIOS.toml"], cwd=framework, check=True)
    fingerprint = subprocess.check_output([
        "cmake", f"-DROOT={framework}", "-DPROFILE=bios/OpenBIOS.toml", "-P",
        str(framework / "tools/bios_emitter_fingerprint.cmake")], cwd=framework, text=True).strip()
    if len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
        raise RuntimeError("Invalid BIOS emitter fingerprint")
    (framework / "generated/OpenBIOS.emitter.sha").write_text(fingerprint + "\n", encoding="utf-8")

    # Hand-authored infinite loop (beq zero,zero,-1; nop), plus a PS-X header.
    # The basename satisfies the existing project wrapper, not a disc identity.
    program = bytearray(4096)
    program[:8] = b"PS-X EXE"
    for offset, value in [(16, 0x80010000), (24, 0x80010000), (28, 2048), (48, 0x801fff00)]:
        struct.pack_into("<I", program, offset, value)
    struct.pack_into("<II", program, 2048, 0x1000ffff, 0)
    fixture = work / "SLUS_006.37"
    fixture.write_bytes(program)
    seeds = work / "entry.txt"
    seeds.write_text("0x80010000\n", encoding="utf-8")
    generated = work / "generated"
    q = lambda value: json.dumps(str(value))
    config = work / "synthetic.toml"
    config.write_text(
        '[game]\nname = "Original CI fixture"\nid = "SYNTHETIC"\n'
        f'exe = {q(fixture)}\nload_address = "0x80010000"\nentry_pc = "0x80010000"\n'
        'text_size = "0x800"\nstack_base = "0x801FFF00"\n'
        f'[recompiler]\nseeds = {q(seeds)}\nout_dir = {q(generated)}\n'
        f'bios_config = {q(framework / "bios/OpenBIOS.toml")}\nstrict = true\ndiscovery = "reachable"\n',
        encoding="utf-8")
    subprocess.run([str(game), "--config", str(config), "--project-root", str(framework)], check=True)
    # Original leaf programs: identical entry and first four words, different
    # fifth instruction. This tests complete-body identity, not a prologue guard.
    prefix = [0x3408000B, 0x00A64821, 0x00094840, 0x00E05025]
    records = [("SYNTHETIC", capture(struct.pack("<7I", *prefix, delta, 0x03E00008, 0x012A1821),
                                       0x8001B000, [0x8001B000]))
               for delta in (0x24820007, 0x2482FFF7)]
    # Original RAM loop: copy/add words, including zero count and load/branch
    # delay slots. Original GTE leaf: square signed IR values and read MAC/IR.
    loop = [0x10C00009, 0, 0x8C880000, 0x24840004, 0x01074021, 0xACA80000,
            0x24A50004, 0x24C6FFFF, 0x14C0FFF9, 0, 0x03E00008, 0x00A01021]
    geometry = [0x48844800, 0x48855000, 0x48865800, 0, 0,
                0x4A000028, 0x4802C800, 0x48034800, 0x03E00008, 0]
    resume = [0x10800003, 0, 0x00E00008, 0x24820007, 0x00A61821, 0x03E00008, 0]
    records.extend(("SYNTHETIC", capture(struct.pack("<" + "I" * len(words), *words), pc, [pc]))
                   for pc, words in [(0x8001B100, loop), (0x8001B200, geometry), (0x8001B300, resume)])
    # Original caller and separately compiled callee. Exercise repeated calls,
    # caller continuation aliases, saved RA and zero-count loop termination.
    caller = [0x27BDFFF0, 0xAFBF000C, 0x10800005, 0, 0x0C006D40, 0,
              0x1440FFFD, 0x24630001, 0x8FBF000C, 0x27BD0010, 0x03E00008, 0]
    callee = [0x2484FFFF, 0x03E00008, 0x00801021]
    records.extend(("SYNTHETIC", capture(struct.pack("<" + "I" * len(words), *words), pc, [pc]))
                   for pc, words in [(0x8001B400, caller), (0x8001B500, callee)])
    # Original indirect caller, also placed across a code-page boundary, and
    # callback. Other callees are installed only by the runtime test so they
    # necessarily execute on fallback. No live backend-selection switch.
    indirect = [0x27BDFFE8, 0xAFBF0014, 0xAFB00010, 0x00808025,
                0x0320F809, 0x24A50001, 0xAE020000, 0x8FB00010, 0x8FBF0014,
                0x27BD0018, 0x03E00008, 0x24630001]
    callback = [0x8C880004, 0x24C60003, 0x01051021, 0x03E00008, 0x00461021]
    records.extend(("SYNTHETIC", capture(struct.pack("<" + "I" * len(words), *words), pc, [pc]))
                   for pc, words in [(0x8001B600, indirect), (0x8001BFE8, indirect),
                                     (0x8001B700, callback)])
    native = emit(records, framework, game, config, work / "native-slices")
    configure = ["cmake", "-S", str(ROOT), "-B", str(work / "build"),
                    f"-DPSXRECOMP_ROOT={framework}", f"-DNITROGEN_GENERATED_DIR={generated}",
                    f"-DNITROGEN_NATIVE_STATIC={native.parent / 'overlays_static.c'}",
                    "-DNITROGEN_NATIVE_SMOKE=ON",
                    "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=OFF", "-DNITROGEN_INPUT_SMOKE=OFF",
                    "-DNITROGEN_DIAGNOSTICS=OFF", "-DPSX_EXECUTION_PROFILE=ENHANCED"]
    if os.name != "nt":
        configure.append("-DSDL_UNIX_CONSOLE_BUILD=ON")
    subprocess.run(configure, check=True)
    subprocess.run(["cmake", "--build", str(work / "build"), "--config", "Release",
                    "--target", "nitrogen-runtime", "--parallel", "2"], check=True)
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    if os.name != "nt":
        os.environ.update(SDL_VIDEODRIVER="offscreen", SDL_AUDIODRIVER="dummy", EGL_PLATFORM="surfaceless")
    runtime_binary = find_binary(work / "build", "NitrogenSquared-dev")
    if load_execution_manifest(runtime_binary)["profile"] != "ENHANCED":
        raise RuntimeError("Normal runtime execution manifest has the wrong profile")
    print(f"Real runtime linked with original synthetic input: {runtime_binary}")
    # Reuse this build tree to run the real runtime's SDL routing/mapping with
    # a virtual controller. This entry point never boots the synthetic guest.
    subprocess.run(["cmake", "-S", str(ROOT), "-B", str(work / "build"),
                    "-DNITROGEN_INPUT_SMOKE=ON"], check=True)
    subprocess.run(["cmake", "--build", str(work / "build"), "--config", "Release",
                    "--target", "nitrogen-runtime", "--parallel", "2"], check=True)
    result = run_smoke(find_binary(work / "build", "NitrogenSquared-input-test"), work)
    if ("Runtime input smoke passed:" not in result.stdout or
            "Runtime media smoke passed:" not in result.stdout or
            "Runtime native slice smoke passed:" not in result.stdout or
            "Runtime native boundary smoke passed:" not in result.stdout or
            "Runtime status/title smoke passed:" not in result.stdout):
        raise RuntimeError("Virtual input test exited without its success receipt: " + result.stdout + result.stderr)
    print(result.stdout, end="", flush=True)
    enhanced = load_execution_manifest(find_binary(work / "build", "NitrogenSquared-input-test"))
    if enhanced["profile"] != "ENHANCED":
        raise RuntimeError("Input fixture execution manifest has the wrong profile")
    if os.name != "nt":
        # These original developer tools embed no guest instructions. Catch
        # pinned-header ABI drift without loading private captures or game data.
        qualification = ROOT / "tools/qualification"
        runtime_include = "-I" + str(framework / "runtime/include")
        subprocess.run(["c++", "-std=c++17", "-fsyntax-only", runtime_include,
                        str(qualification / "compare.cpp"),
                        str(qualification / "replay.cpp")], check=True)
        subprocess.run(["c++", "-std=c++17", "-fsyntax-only", "-DPSX_SDL3=1",
                        runtime_include, "-I" + str(work / "build/_deps/sdl3-src/include"),
                        str(qualification / "normal_controller.cpp")], check=True)
        print("Original qualification helper syntax checks passed", flush=True)
        subprocess.run(["python", str(ROOT / "tools/check_renderer.py"),
                        "--framework", str(framework), "--runtime-build", str(work / "build"),
                        "--output", str(work / "renderer-check")], check=True)
        subprocess.run(["cmake", "-S", str(ROOT), "-B", str(work / "build"),
                        "-DPSX_EXECUTION_PROFILE=REFERENCE"], check=True)
        subprocess.run(["cmake", "--build", str(work / "build"), "--config", "Release",
                        "--target", "nitrogen-runtime", "--parallel", "2"], check=True)
        reference_binary = find_binary(work / "build", "NitrogenSquared-input-test")
        reference = load_execution_manifest(reference_binary)
        if (enhanced["profile"] != "ENHANCED" or reference["profile"] != "REFERENCE" or
                enhanced["identity"] == reference["identity"] or
                not any(x["name"] == "n2o-textured-batching" for x in reference["implementations"])):
            raise RuntimeError("Renderer profiles did not select distinct implementation identities")
        result = run_smoke(reference_binary, work)
        print(result.stdout, end="", flush=True)


if __name__ == "__main__":
    main()
