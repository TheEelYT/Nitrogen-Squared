#!/usr/bin/env python3
"""Compile the real runtime with an original synthetic program, never game data.

This CI-only fixture validates compiler/linker integration. It cannot validate
N2O behavior, disc access, assets or audio. It is not a player import bypass.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct
import subprocess

from build_recompiler import build
from build_runtime import find_binary
from n2o_disc import ROOT


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
    subprocess.run(["cmake", "-S", str(ROOT), "-B", str(work / "build"),
                    f"-DPSXRECOMP_ROOT={framework}", f"-DNITROGEN_GENERATED_DIR={generated}",
                    "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=OFF", "-DNITROGEN_INPUT_SMOKE=OFF",
                    "-DNITROGEN_DIAGNOSTICS=OFF"], check=True)
    subprocess.run(["cmake", "--build", str(work / "build"), "--config", "Release",
                    "--target", "nitrogen-runtime", "--parallel", "2"], check=True)
    print(f"Real runtime linked with original synthetic input: {find_binary(work / 'build', 'NitrogenSquared-dev')}")
    # Reuse this build tree to run the real runtime's SDL routing/mapping with
    # a virtual controller. This entry point never boots the synthetic guest.
    subprocess.run(["cmake", "-S", str(ROOT), "-B", str(work / "build"),
                    "-DNITROGEN_INPUT_SMOKE=ON"], check=True)
    subprocess.run(["cmake", "--build", str(work / "build"), "--config", "Release",
                    "--target", "nitrogen-runtime", "--parallel", "2"], check=True)
    subprocess.run([str(find_binary(work / "build", "NitrogenSquared-input-test"))],
                   check=True, timeout=15)


if __name__ == "__main__":
    main()
