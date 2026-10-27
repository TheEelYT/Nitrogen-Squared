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
    result = subprocess.run([str(find_binary(work / "build", "NitrogenSquared-input-test"))],
                            check=True, timeout=15, capture_output=True, text=True)
    if ("Runtime input smoke passed:" not in result.stdout or
            "Runtime media smoke passed:" not in result.stdout or
            "Runtime native slice smoke passed:" not in result.stdout or
            "Runtime status/title smoke passed:" not in result.stdout):
        raise RuntimeError("Virtual input test exited without its success receipt: " + result.stdout + result.stderr)
    print(result.stdout, end="", flush=True)
    enhanced = load_execution_manifest(find_binary(work / "build", "NitrogenSquared-input-test"))
    if enhanced["profile"] != "ENHANCED":
        raise RuntimeError("Input fixture execution manifest has the wrong profile")
    if os.name != "nt":
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
        subprocess.run([str(reference_binary)], check=True, timeout=15)


if __name__ == "__main__":
    main()
