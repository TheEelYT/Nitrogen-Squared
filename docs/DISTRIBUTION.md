# No game content in Git or releases

Development and approval policy: work on dev, keep main at cleared releases,
and publish only after explicit owner verification and release clearance.
Dev creates Actions test artifacts, never GitHub releases or release branches.
See [the current release process](RELEASE_PROCESS.md); this supersedes historical
branch/publication descriptions below.

This is an explicit project requirement, including derived game code.

Allowed in source: original tools/runtime code, documentation, identity hashes,
track metadata, addresses, configuration and original synthetic test fixtures.
The Windows release additionally contains an Tauri launcher executable
and a clean CPython distribution with its upstream licenses.

Excluded: disc images/CUE sheets, extracted executables, asset/audio files,
generated game C/disassembly/guards, compiled game modules, captured RAM/overlay
bytes, saves and Sony BIOS data. Never package a developer's private installation,
build or cache. No uploaded-disc assets may be used for branding or setup art.

## Windows player flow — 0.0.17

1. Extract the complete Nitrogen-Squared folder and run launcher.exe.
2. Select the supported local CUE/BIN. CUE is preferred because it identifies the
   data and audio tracks; a BIN selection requires its unique matching CUE beside it.
3. Verify the layout, full image hash, boot identity and extracted executable hashes.
4. Download pinned preparation tools privately, fetch the pinned framework and
   dependencies, generate and compile the player's game, then start play.
5. Reuse that build on later launches. Rebuild after a version/tool change or a
   folder move; preserve the previous incompatible build cache and existing saves.

No separate Python or Visual Studio installation is required. First preparation
and updates need internet access. All downloaded/extracted/generated files,
builds, logs, update backups and saves stay beneath the extracted folder's .local
directory. The original selected CUE/BIN stays at its selected path and remains
needed for original assets/audio and verification. The launcher does not write to
that disc input or use the legacy developer import's user-data directory.

The launcher calls the existing verified Python build/play paths with explicit
private directories, compiler, Python, save path and launch environment. This
provides native-movie disc access even though the player starts launcher.exe.
Running the generated game executable alone is still a separate developer path.
The runtime remains dependent on the pinned framework and compatibility services.

## Updates and recovery

The launcher checks this repository's latest stable release, verifies the ZIP
checksum and exact file manifest, and stages it under .local. Package ownership
is restricted to the platform launcher, reviewed app source, dependency notices, portable Python and package
metadata. Private .local data and unknown files are preserved. A collision with
an unknown file is refused instead of overwriting it.

A copied Python updater waits for the old launcher/Python to exit before replacing
owned files. It backs up the previous package, journals replacement, rolls back
on failure and restarts the launcher. Interrupted replacement offers restoration
on the next launch. The private game is rebuilt if required; saves live separately
at .local/saves. Tests cover failure rollback and a real Windows copied-process
replacement/restart with save/cache sentinels. The first real newer public release
will provide an additional player-side update check.

## Package enforcement

The source gate, tools/package_source.py, uses an explicit reviewed text allowlist
and an unchanged 128 KiB per-file limit. CI rejects tracked files outside it and
recognizable binary/game/emitter content. This guards against accidental inclusion;
it is not a claim about arbitrary obfuscation. Review every allowlist change.

The packagers ship only the Tauri host, reviewed source/artwork and dependency
notices (plus portable CPython on Windows). `tools/build_launcher.py` builds the
host with npm/Cargo lockfiles and no game inputs; it gathers resolved Rust notices.
The finished ZIP is reextracted and checked against its exact size/hash inventory.
Native webview self-tests and copied-updater tests run against extracted packages;
private synthetic fixture outputs are never repacked. The frontend adapts Recompia
under GPL-3.0-or-later; source, attribution and licenses accompany both platforms.

Main-branch publication waits for package integration and source plus Windows/Linux
runtime workflows to pass. It uploads all three assets into an unpublished draft
before publishing, and preserves already public version assets. Release assets
are the Windows ZIP, its SHA-256 file and the source ZIP. Source and third-party
notices remain available in the extracted app directory.

## Vita

Vita preparation, target modules, signing/package constraints and runtime portability
remain open engineering work. The future VPK must remain free of game-derived
modules and assets. A Windows executable cannot simply be copied to Vita, and
on-device compilation is not promised. See ROADMAP.md.

## Linux launcher package (0.0.28)

The Linux x86_64 ZIP contains launcher.sh, README-FIRST.txt and the same reviewed
source allowlist under app, a Tauri host and dependency notices. No system Python, compiler, prepared game executable
or disc data is bundled. Users install the documented system prerequisites once.
The shared GUI imports the supported CUE/BIN and privately prepares the game under
.local; saves and extracted edits remain there. Updates select the Linux asset,
validate its checksum/platform/inventory and use a copied runner with rollback.
The Windows and Linux package jobs both gate release publication.

## Release branches (0.1.0 onward)

Each release preserves its final tested source commit at `release/x.y.z`, alongside
its immutable `vx.y.z` tag. Main continues development and receives documentation
receipts. The publication job verifies an existing release branch rather than
moving it. The 0.1.0 job removes the 27 reviewed older work branches only if their
heads remain unchanged, no pull requests are open and all their commits are
already contained in the tested release. Changed or unmerged work is preserved.

## Update compatibility and version policy from 0.2.0

The released 0.1.3 updater rejects the Tauri package's new
`support/launcher/licenses/` directory during staging, before replacement. Those
users must close the launcher/game and manually overlay the complete new platform
package while preserving `.local`; replacing launcher.exe alone is insufficient.
Updating new updater code cannot change the checks already installed in 0.1.3.
Do not overwrite old published assets/tags to retrofit this change.

The 0.2.2 setup-only candidate retains compatible compiled games and completed
setup downloads. A clean Windows setup is not qualified by a successful existing
game launch or by the synthetic compiler fixture; verify the service's own first
setup and cancellation paths before clearing a release.

Major game-code updates increment the middle component (`0.2.0`, `0.3.0`, ...).
Patches and launcher updates increment the final component (`0.2.1`, `0.2.2`, ...).
Use this policy until the owner declares version 1.0.0. Every complete version
gets its own `release/x.y.z` branch.

Starting with 0.2.0, the launcher must compare compiled-game inputs separately
from the public release version. Changed game/runtime code or other inputs to
the prepared game require recompilation, including a game-code patch. A launcher
or documentation-only update reuses the current compatible compilation. Preserve
private builds and saves during either update path. Tests must cover both paths
and prove that a changed build input cannot reuse a stale executable. This policy
is implemented by the 0.2.0 dev candidate; player verification is pending.

## Public README images

The owner authorizes the original project logo and four reviewed 16:9 demonstration
images for the repository README. Their provenance is in [images/README.md](images/README.md).
The source gate verifies their exact hashes through configs/documentation_assets.json
separately from the text allowlist. They are never copied into either launcher ZIP
or the tool-built source package. GitHub's automatic source archives include the
repository's documentation images. This exception does not permit standalone game
resources (including the memory-card icon), other captures, generated C, private
modules, disc images or saves in Git or player packages.
