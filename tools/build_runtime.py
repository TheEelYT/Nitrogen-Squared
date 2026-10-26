#!/usr/bin/env python3
"""Build a private desktop runtime from an already imported, user-owned disc.

No disc or generated game source is downloaded. This executable links private
game code and is NOT a public release artifact. No Sony BIOS is required.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from build_recompiler import FRAMEWORK_REV, build, verify_framework
from generate import generate
from n2o_disc import ROOT, DiscError, default_data_dir, digest, inspect


def find_binary(directory: Path, name: str) -> Path:
    # Both Visual Studio multi-config and Ninja/Make single-config layouts.
    names = [name + ".exe", name] if os.name == "nt" else [name, name + ".exe"]
    for subdir in (directory / "Release", directory):
        for filename in names:
            candidate = subdir / filename
            if candidate.is_file():
                return candidate.resolve()
    raise FileNotFoundError(f"Build did not produce {name} under {directory}")


def load_installation(installation: Path) -> dict:
    identity = json.loads((ROOT / "configs/disc_usa.json").read_text())
    manifest = json.loads((installation / "installation.json").read_text())
    if manifest.get("schema") != 1 or manifest.get("game_id") != identity["game_id"]:
        raise DiscError("Unsupported installation manifest; run the importer first")
    if manifest.get("bin_sha256") != identity["bin_sha256"]:
        raise DiscError("Installation was made from another disc revision")
    # An import from an earlier session does not establish today's image contents.
    current = inspect(Path(manifest["cue"]), identity, print)
    for expected in identity["executables"]:
        path = installation / "executables" / expected["path"]
        if not path.is_file() or path.stat().st_size != expected["size"] or digest(path) != expected["sha256"]:
            raise DiscError(f"Local executable changed or missing: {expected['path']}")
    return current


def runtime_config(manifest: dict, installation: Path, generated: Path, controller_mode: str = "analog") -> str:
    if controller_mode not in ("analog", "digital"):
        raise ValueError("Controller mode must be analog or digital")
    boot = next(e for e in manifest["executables"] if e["path"] == "SLUS_006.37")
    q = lambda value: json.dumps(str(value))
    return (
        '# Private development configuration; do not distribute.\n'
        '[game]\nname = "Nitrogen Squared"\nid = "SLUS-00637"\nplayers = 2\n'
        f'exe = {q(installation / "executables/SLUS_006.37")}\ndisc = {q(manifest["cue"])}\n'
        + ''.join(f'{key} = "0x{boot[key]:08X}"\n' for key in
                  ("load_address", "entry_pc", "text_size", "stack_base"))
        + '\n[recompiler]\nstrict = true\ndiscovery = "reachable"\n'
        f'seeds = {q(generated / "entry.txt")}\nout_dir = {q(generated)}\n'
        '\n[runtime]\nwindow_title = "Nitrogen Squared development"\n'
        'memcard_dir = "saves"\noverlay_cache = true\n'
        '\n[video]\nrenderer = "opengl"\naspect_ratio = "4:3"\n'
        'internal_resolution = "native"\nsupersampling = 1\ndynamic_resolution = false\n'
        f'\n[controller]\ndefault_mode = "{controller_mode}"\np1_device = "auto"\np2_device = "none"\n'
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--installation", type=Path, default=default_data_dir() / "SLUS-00637")
    p.add_argument("--framework", type=Path, default=ROOT / ".local/psxrecomp")
    p.add_argument("--recompiler-build", type=Path, default=ROOT / ".local/build-recompiler")
    p.add_argument("--work-dir", type=Path, default=ROOT / ".local/runtime-dev")
    p.add_argument("--cmake", default="cmake")
    p.add_argument("--console-host", action="store_true", help="Linux headless/offscreen build; not for Windows")
    p.add_argument("--configure-only", action="store_true")
    p.add_argument("--diagnostics", action="store_true",
                   help="Enable the slower per-instruction instrumentation and TCP status probe")
    p.add_argument("--controller-mode", choices=["analog", "digital"], default="analog",
                   help="PS1 controller type presented to the game (default: analog DualShock)")
    p.add_argument("--cmake-arg", action="append", default=[], help="Additional configure argument, e.g. --cmake-arg=-DNAME=VALUE")
    args = p.parse_args()
    try:
        if not shutil.which(args.cmake):
            raise FileNotFoundError("CMake is not on PATH. Use a Visual Studio developer shell with CMake installed.")
        installation = args.installation.resolve()
        manifest = load_installation(installation)
        framework, compiler_build, work = (d.resolve() for d in (args.framework, args.recompiler_build, args.work_dir))
        if work == ROOT or work == installation or work == framework:
            raise ValueError("Choose a separate private runtime work directory")
        build(framework, compiler_build, args.cmake, bios=True)
        emitter = find_binary(compiler_build, "psxrecomp-game")
        bios_emitter = find_binary(compiler_build, "psxrecomp-bios")
        verify_framework(framework)
        # Use the canonical profile and portable CMake fingerprint, without Bash.
        subprocess.run([str(bios_emitter), "--config", "bios/OpenBIOS.toml"], cwd=framework, check=True)
        fingerprint = subprocess.check_output([
            args.cmake, f"-DROOT={framework}", "-DPROFILE=bios/OpenBIOS.toml", "-P",
            str(framework / "tools/bios_emitter_fingerprint.cmake")], cwd=framework, text=True).strip()
        if len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
            raise RuntimeError("Invalid BIOS emitter fingerprint")
        (framework / "generated/OpenBIOS.emitter.sha").write_text(fingerprint + "\n", encoding="utf-8")

        signature = hashlib.sha256((FRAMEWORK_REV + manifest["bin_sha256"] +
                                    digest(ROOT / "tools/generate.py")).encode()).hexdigest()
        generated_root = work / "generated" / signature[:16]
        if not generated_root.exists():
            generate(installation, framework, emitter, generated_root)
        else:
            record = json.loads((generated_root / "generation.json").read_text())
            if record.get("framework_revision") != FRAMEWORK_REV or len(record.get("executables", [])) != 3 or any(
                    row.get("exit_code") != 0 for row in record["executables"]):
                raise RuntimeError("Incomplete cached generation; use a new --work-dir")
        generated = generated_root / "SLUS_006.37"
        work.mkdir(parents=True, exist_ok=True)
        (work / "game.toml").write_text(runtime_config(manifest, installation, generated, args.controller_mode), encoding="utf-8")
        build_dir = work / "build"
        command = [args.cmake, "-S", str(ROOT), "-B", str(build_dir),
                   f"-DPSXRECOMP_ROOT={framework}", f"-DNITROGEN_GENERATED_DIR={generated}",
                   "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=OFF", "-DNITROGEN_INPUT_SMOKE=OFF",
                   f"-DNITROGEN_DIAGNOSTICS={'ON' if args.diagnostics else 'OFF'}"]
        if args.console_host:
            command.append("-DSDL_UNIX_CONSOLE_BUILD=ON")
        command.extend(args.cmake_arg)
        subprocess.run(command, check=True)
        if args.configure_only:
            print(f"Configured private runtime: {build_dir}")
            return 0
        subprocess.run([args.cmake, "--build", str(build_dir), "--config", "Release",
                        "--target", "nitrogen-runtime", "--parallel", "2"], check=True)
        executable = find_binary(build_dir, "NitrogenSquared-dev")
        record = dict(schema=1, framework_revision=FRAMEWORK_REV, source_signature=signature,
                      generated_dir=str(generated_root), linked_executables=["SLUS_006.37"],
                      executable=str(executable), config=str(work / "game.toml"),
                      installation=str(installation),
                      disc_sha256=manifest["bin_sha256"], build_succeeded=True,
                      gameplay_verified=False, public_distribution_allowed=False,
                      diagnostics_enabled=args.diagnostics)
        (work / "runtime-build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"\nPrivate runtime built: {executable}\nStart with: python tools/run_runtime.py")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
        p.exit(1, f"Runtime build failed: {e}\n")


if __name__ == "__main__":
    raise SystemExit(main())
