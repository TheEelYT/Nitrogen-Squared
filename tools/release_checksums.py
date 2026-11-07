"""Combined release checksums; published platform ZIPs are never replaced."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from portable_support import ASSET_NAME, LINUX_ASSET_NAME, REPOSITORY, sha256

CHECKSUM_NAME = "SHA256SUMS.txt"
MAX_CHECKSUM_BYTES = 65536


def publication_asset_names(version: str) -> list[str]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Invalid publication version")
    names = [ASSET_NAME, LINUX_ASSET_NAME, CHECKSUM_NAME]
    if tuple(map(int, version.split("."))) < (0, 2, 0):
        names += [ASSET_NAME + ".sha256", LINUX_ASSET_NAME + ".sha256"]
    return names


def checksum_for(data: bytes, name: str, multiple: bool = True) -> str:
    if len(data) > MAX_CHECKSUM_BYTES:
        raise ValueError("Release checksum file is too large")
    entries = {}
    seen = set()
    for line in data.splitlines():
        if not line:
            continue
        match = re.fullmatch(rb"([0-9a-f]{64})[ \t]+\*?([A-Za-z0-9][A-Za-z0-9._-]*)", line)
        if not match:
            raise ValueError("Invalid release checksum file")
        filename = match[2].decode("ascii")
        if filename.casefold() in seen:
            raise ValueError("Duplicate release checksum entry")
        seen.add(filename.casefold())
        entries[filename] = match[1].decode("ascii")
    if name not in entries or (not multiple and len(entries) != 1):
        raise ValueError("Release checksum file does not identify this package")
    return entries[name]


def write_checksums(paths: list[Path], output: Path) -> None:
    names = [p.name for p in paths]
    if not names or len({n.casefold() for n in names}) != len(names):
        raise ValueError("Checksum inputs must have unique filenames")
    for name in names:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
            raise ValueError("Invalid checksum filename")
    data = "".join(sha256(p) + "  " + p.name + "\n" for p in sorted(paths, key=lambda p: p.name))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data.encode("ascii"))


def gh(*args: str) -> str:
    return subprocess.check_output(["gh", *args], text=True)


def maintain_published_release(tag: str, commit: str, repo: str) -> dict:
    """Authorized 0.1.0 metadata cleanup; keep its tag, ZIPs and legacy hashes."""
    if repo != REPOSITORY or tag != "v0.1.0" or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Published-asset maintenance is restricted to the reviewed release")
    base = "repos/" + repo + "/"
    ref = json.loads(gh("api", base + "git/ref/tags/" + tag))
    release = json.loads(gh("api", base + "releases/tags/" + tag))
    if ref["object"]["sha"] != commit or release.get("draft") or release.get("prerelease"):
        raise ValueError("Published release identity changed")
    assets = {a["name"]: a for a in release["assets"]}
    packages = [ASSET_NAME, LINUX_ASSET_NAME]
    required = {n for p in packages for n in (p, p + ".sha256")}
    if not required <= set(assets):
        raise ValueError("Existing updater packages are incomplete")
    with tempfile.TemporaryDirectory(prefix="nitrogen-release-checksums-") as temp:
        work = Path(temp)
        for name in sorted(required):
            gh("release", "download", tag, "--repo", repo, "--pattern", name, "--dir", str(work))
            if (work / name).stat().st_size != assets[name]["size"]:
                raise ValueError("Published asset size changed")
        hashes = {}
        for name in packages:
            digest = sha256(work / name)
            if checksum_for((work / (name + ".sha256")).read_bytes(), name, False) != digest:
                raise ValueError("Published package checksum changed")
            if assets[name].get("digest") not in (None, "sha256:" + digest):
                raise ValueError("Published package digest changed")
            hashes[name] = digest
        output = work / CHECKSUM_NAME
        write_checksums([work / name for name in packages], output)
        expected = output.read_bytes()
        if CHECKSUM_NAME in assets:
            gh("release", "download", tag, "--repo", repo, "--pattern", CHECKSUM_NAME, "--dir", str(work / "existing"))
            if (work / "existing" / CHECKSUM_NAME).read_bytes() != expected:
                raise ValueError("Existing combined checksums disagree; preserving assets")
        else:
            gh("release", "upload", tag, str(output), "--repo", repo)
        source = "Nitrogen-Squared-source.zip"
        if source in assets:
            gh("release", "delete-asset", tag, source, "--yes", "--repo", repo)
        marker = "**Checksum transition:**"
        body = release.get("body") or ""
        if marker not in body:
            note = (marker + " SHA256SUMS.txt covers both platform ZIPs. The individual .sha256 files remain "
                    "for older launchers during migration through 0.1.x; the 0.1.1 launcher reads either format. "
                    "From 0.2.0, new releases use only the platform ZIPs and SHA256SUMS.txt. "
                    "GitHub's automatic source archives replace the redundant uploaded source ZIP. "
                    "The published platform ZIPs and version tag are unchanged.")
            notes = work / "notes.md"
            notes.write_text(body + ("" if body.endswith("\n") else "\n") + "\n" + note + "\n", encoding="utf-8")
            gh("release", "edit", tag, "--repo", repo, "--notes-file", str(notes))
    return dict(tag=tag, commit=commit, package_hashes=hashes,
                source_asset_removed=True, legacy_checksums_preserved=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--maintain-release")
    parser.add_argument("--expected-commit")
    parser.add_argument("--asset-list-version")
    args = parser.parse_args()
    if args.asset_list_version:
        if args.archives or args.output or args.maintain_release:
            parser.error("Asset listing takes only a version")
        print("\n".join(publication_asset_names(args.asset_list_version)))
    elif args.maintain_release:
        if not args.expected_commit or args.archives or args.output:
            parser.error("Maintenance requires an expected commit and no build inputs")
        print(json.dumps(maintain_published_release(args.maintain_release, args.expected_commit, os.environ["GH_REPO"])))
    else:
        if not args.output or not args.archives:
            parser.error("Provide --output and the final archives")
        write_checksums(args.archives, args.output)


if __name__ == "__main__":
    main()
