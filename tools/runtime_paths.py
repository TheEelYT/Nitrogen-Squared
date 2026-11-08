"""Keep portable direct launches on the launcher's existing save directory."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import os


def load_toml(text: str) -> dict:
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError as error:
            raise ValueError("Python 3.10 setup needs: python -m pip install tomli") from error
    return tomllib.loads(text)


def configured_saves(config: Path) -> Path:
    value = load_toml(config.read_text(encoding="utf-8-sig")).get("runtime", {}).get("memcard_dir", "saves")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("The runtime save directory must be a non-empty string")
    path = Path(value)
    return (path if path.is_absolute() else config.parent / path).resolve()


def _rewrite(original: bytes, section: str, values: dict) -> bytes:
    text = original.decode("utf-8-sig")
    before = load_toml(text)
    expected = dict(before)
    expected[section] = dict(before.get(section, {}), **values)
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    header = re.compile(r"^\s*\[([A-Za-z0-9_.-]+)\]\s*(?:#.*)?$")
    key = re.compile(r"^\s*([A-Za-z0-9_-]+)\s*=")
    result = []
    active = False
    found = False
    written = set()

    def missing():
        for name, value in values.items():
            if name not in written:
                result.append(name + " = " + json.dumps(value, ensure_ascii=False) + newline)
                written.add(name)

    for line in lines:
        match = header.match(line.rstrip("\r\n"))
        if line.lstrip().startswith("["):
            if active:
                missing()
            active = bool(match and match[1] == section)
            found |= active
        assignment = key.match(line) if active else None
        if assignment and assignment[1] in values:
            name = assignment[1]
            result.append(name + " = " + json.dumps(values[name], ensure_ascii=False) + newline)
            written.add(name)
        else:
            result.append(line)
    if active:
        if result and not result[-1].endswith(("\n", "\r")):
            result[-1] += newline
        missing()
    if not found:
        if result and not result[-1].endswith(("\n", "\r")):
            result[-1] += newline
        result.append(newline + "[" + section + "]" + newline)
        missing()
    updated = "".join(result)
    if load_toml(updated) != expected:
        raise ValueError("Cannot safely repair save paths; the configuration was preserved")
    return (b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b"") + updated.encode("utf-8")


def repair_portable_saves(layout) -> list[Path]:
    """Repair configuration only; never overwrite or combine existing card files."""
    from portable_support import beneath
    work = layout.work
    if not (work / "runtime-build.json").is_file():
        return []
    record = json.loads((work / "runtime-build.json").read_text(encoding="utf-8"))
    if not record.get("build_succeeded") or record.get("public_distribution_allowed") is not False:
        return []
    saves = beneath(layout.root, ".local/saves")
    legacy = beneath(layout.root, ".local/runtime-dev/saves")
    canonical = saves.resolve().as_posix()
    changes = []
    for relative in ("game.toml", "build/game.toml", "build/Release/game.toml",
                     "build/settings.toml", "build/Release/settings.toml"):
        path = beneath(layout.root, ".local/runtime-dev/" + relative)
        if not path.is_file():
            continue
        original = path.read_bytes()
        section = "memcard" if path.name == "settings.toml" else "runtime"
        values = {"dir": canonical, "card1": "", "card2": ""} if section == "memcard" else {"memcard_dir": canonical}
        data = _rewrite(original, section, values)
        if data != original:
            changes.append((path, original, data))
    # Preserve the old developer/direct-launch cards if no portable folder exists.
    # If both exist, the launcher's cards win; keep the other folder untouched.
    if legacy.is_dir() and not saves.exists():
        with tempfile.TemporaryDirectory(prefix=".save-migration-", dir=layout.local) as temporary:
            staged = Path(temporary) / "saves"
            shutil.copytree(legacy, staged)
            if saves.exists():
                raise ValueError("A portable save folder appeared during migration; both originals were preserved")
            os.rename(staged, saves)
    saves.mkdir(parents=True, exist_ok=True)
    for path, original, data in changes:
        backup = path.with_name(path.name + ".before-shared-saves-" + hashlib.sha256(original).hexdigest()[:16])
        if backup.exists():
            if backup.is_symlink() or backup.read_bytes() != original:
                raise ValueError("Save-path configuration backup differs; existing files were preserved")
        else:
            with backup.open("xb") as stream:
                stream.write(original)
        if path.read_bytes() != original:
            raise ValueError("Configuration changed while repairing save paths; retry with the game closed")
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".save-path-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        try:
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    return [path for path, _, _ in changes]
