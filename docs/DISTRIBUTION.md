# No game content in Git or releases

This is an explicit project requirement, including derived game code.

Allowed in source: original tools/runtime code, documentation, identity hashes,
track metadata, addresses, configuration and original synthetic test fixtures.
The Windows release additionally contains an original Win32 launcher executable
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
is restricted to launcher.exe, reviewed app source, portable Python and package
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

The source gate, tools/package_source.py, uses a reviewed 95-file text allowlist
and an unchanged 128 KiB per-file limit. CI rejects tracked files outside it and
recognizable binary/game/emitter content. This guards against accidental inclusion;
it is not a claim about arbitrary obfuscation. Review every allowlist change.

The Windows packager compiles only launcher/launcher_win.c into the public EXE,
copies reviewed source and a clean CPython runtime, writes a size/SHA-256 manifest,
and reextracts/audits the finished ZIP. It never traverses a private .local tree
or links any game/runtime output into the public launcher. Package CI tests an
extracted copy with synthetic inputs after the release ZIP has been finalized,
then checks that its checksum has not changed. Private fixture output is not repacked.

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
