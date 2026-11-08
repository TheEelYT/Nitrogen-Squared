"""Identify compiled-game inputs independently of public launcher versions."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform


def file_sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def platform_id() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        machine = "x86_64"
    return system + "-" + machine


def _input_path(root: Path, name: str) -> Path:
    parts = PurePosixPath(name)
    if not name or parts.as_posix() != name or "\\" in name or ":" in name or parts.is_absolute() or any(p in (".", "..") for p in name.split("/")):
        raise ValueError("Invalid compiled-game input path")
    path = root.joinpath(*parts.parts)
    if any(p.is_symlink() for p in [path, *path.parents] if p != root and root in p.parents):
        raise ValueError("Compiled-game inputs cannot be symbolic links")
    return path


def input_fingerprint(root: Path) -> str:
    root = root.resolve()
    definition = json.loads((root / "configs/runtime_inputs.json").read_text(encoding="utf-8"))
    if definition.get("schema") != 1 or not all(isinstance(definition.get(k), list) for k in ("files", "trees")):
        raise ValueError("Unsupported compiled-game input definition")
    paths = set()
    for name in definition["files"]:
        path = _input_path(root, name)
        if not path.is_file():
            raise ValueError("Missing compiled-game input: " + name)
        paths.add(name)
    for name in definition["trees"]:
        tree = _input_path(root, name)
        if not tree.is_dir():
            raise ValueError("Missing compiled-game input tree: " + name)
        for path in tree.rglob("*"):
            relative = path.relative_to(root).as_posix()
            _input_path(root, relative)
            if path.is_file():
                paths.add(relative)
    result = hashlib.sha256(b"Nitrogen compiled-game inputs v1\0")
    for name in sorted(paths):
        # Git's Windows line endings do not constitute a code change.
        content = _input_path(root, name).read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
        result.update(name.encode("utf-8") + b"\0" + hashlib.sha256(content).digest())
    return result.hexdigest()


def build_options(*, diagnostics=False, controller_mode="analog", console_host=False, cmake_args=(), environment=None):
    env = os.environ if environment is None else environment
    compiler_environment = {k:env[k] for k in ("CC", "CXX", "RC", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS",
                                             "CMAKE_GENERATOR", "CMAKE_TOOLCHAIN_FILE") if k in env}
    return dict(diagnostics=diagnostics, controller_mode=controller_mode,
                console_host=console_host, cmake_args=list(cmake_args), environment=compiler_environment)


def build_identity(root: Path, executable: Path, options: dict) -> dict:
    return dict(schema=1, inputs_sha256=input_fingerprint(root), platform=platform_id(),
                options=options, executable_sha256=file_sha256(executable),
                execution_sha256=file_sha256(executable.with_suffix(".execution.json")))


def reusable_runtime(root: Path, work: Path, expected_platform: str, options: dict) -> bool:
    """Missing/old/incomplete receipts request a rebuild, preserving private data."""
    try:
        work = work.resolve()
        record = json.loads((work / "runtime-build.json").read_text(encoding="utf-8"))
        identity = record["build_identity"]
        if (record.get("schema") != 1 or record.get("build_succeeded") is not True or record.get("public_distribution_allowed") is not False
                or identity.get("schema") != 1 or identity.get("platform") != expected_platform
                or identity.get("options") != options or identity.get("inputs_sha256") != input_fingerprint(root)):
            return False
        executable, config = (Path(record[k]) for k in ("executable", "config"))
        manifest = executable.with_suffix(".execution.json")
        if any(not p.is_absolute() or not p.resolve().is_relative_to(work) or p.is_symlink() for p in (executable, config, manifest)):
            return False
        return (config.is_file() and identity.get("executable_sha256") == file_sha256(executable)
                and identity.get("execution_sha256") == file_sha256(executable.with_suffix(".execution.json")))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False
