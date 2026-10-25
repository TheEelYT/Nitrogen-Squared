# No game content in Git or releases

This is an explicit project requirement, including derived game code.

Allowed in source: original tools/runtime code, original documentation, disc
identity hashes, track metadata, addresses, configuration and original test fixtures.

Excluded: disc images/CUE sheets, extracted executables, asset/audio files, generated
game C/disassembly, generated game native modules, captured RAM/overlay bytes, save
files, and Sony BIOS data. Never package a developer's private installation/cache.
No assets from the uploaded disc may be used for repository branding or setup art.

## Player flow

1. Launch a package containing only original runtime/setup code and permitted
   third-party tools. There is no prepared game data or game-specific native module.
2. Select a complete, supported local CUE/BIN image.
3. Verify disc layout, full image hash, boot identity and executable hashes.
4. Prepare required inputs and generate/compile game code into a separate private
   user-data directory. Read original assets/music from the player's disc.
5. Reuse the private cache on later launches; invalidate it when disc identity,
   translation configuration, target architecture or runtime ABI changes.

Steps 2–3 and local input extraction are implemented in this first milestone.
Generation currently exists as a separate developer command. Automated native
module compilation, ABI integration and gameplay startup remain to be implemented.

## Windows and Vita implications

Windows needs bundled, licensed preparation/compiler tools or a download/install
path that is explicit to the player. The end product should not require the player
to install Visual Studio. The investigation build still requires developer tools.

For Vita, investigate desktop preparation/cross-compilation of the player's private
game modules and transfer to the console. The distributed VPK must remain free of
those modules. Loading target-specific modules, code signing/package constraints,
and compatibility are open engineering work; do not assume a Windows DLL can be
copied to Vita. On-device preparation is not promised.

The game runtime must not treat the presence of an import manifest as proof it can
play. `runtime_ready` stays false until a validated runtime is actually integrated.

## Enforcement

`.gitignore` is a convenience; `tools/package_source.py` is the source release gate.
It reads an explicit allowlist, validates every file, rejects binary/game-format
extensions and recognizable renamed executable/emitter content, and can reject
unknown files in a staging directory. CI also rejects tracked files outside that
allowlist. This is a guard against accidental inclusion, not a proof about arbitrary
obfuscated content. Review every allowlist change.

Future binary packaging needs its own exact manifest. It must distinguish original
runtime/tool executables from user-derived game code and reject the latter even
when embedded into an otherwise original executable. Do not use the upstream
default of committing generated game C or shipping developer-built overlay caches.
