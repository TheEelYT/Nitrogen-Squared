# Desktop runtime bring-up — 0.0.2

The project now has its own CMake wrapper and Python orchestration around the
pinned framework. All game inputs and build products remain private local data.

`build_runtime.py` uses the existing import, rechecks the original image and
extracted executable hashes, builds the game and BIOS emitters, regenerates the
OpenBIOS backend with the canonical CMake fingerprint, and generates the three
separate executable analysis translations. Only the boot loader's generated C is
currently linked into the desktop runtime. Loaded game regions use the runtime's
interpreter fallback; they are not blindly merged into one overlapping function map.

The private build is stored under `.local/runtime-dev` by default. Its cache key
includes the pinned framework, full disc hash and generator script. A build receipt
records the executable/config/installation paths and explicitly says that public
distribution is not allowed and gameplay has not been fully verified. The importer
manifest's `runtime_ready` is not changed into a misleading completion flag.

`run_runtime.py` validates inputs again, retains a startup log, keeps saves and
overlay captures under the private work directory, and disables unconfigured
background overlay compilation. `probe_runtime.py` reports an allowlist of numeric
status fields; it has no RAM-dump or code-capture operation.

## Observed on the development host

Linux x86-64, GCC 13.3, SDL3 3.4.10, software rendering, OpenBIOS, no window/audio
device. Source generation and native link both succeeded. Live scanout captures
showed the opening publisher video, title screen, animated attract demo, ship
selection, level selection and tutorial text, then first-level gameplay with
animated enemies and a changing score. Scripted digital Cross input advanced
the menu flow. This is stronger evidence than C generation alone, but does not
establish desktop audio, physical input, full campaign or save/load correctness.

The observed boot-to-menu route uses substantial interpreted execution in loaded
game regions. Static dispatch counters by themselves exclude much of that work;
do not turn those counters into a native coverage percentage. Captured executable
overlap identities and function discovery remain the next recompilation work.

The development host lacks desktop X11/Wayland headers, so its test build used
`--console-host` and a system GL shared library override. Those are host-specific
test flags, not Windows setup requirements. The Windows build uses desktop SDL3
and system OpenGL. Its real window, audio, keyboard, and exit path need user tests.

The source-only release gate continues to exclude binaries and generated code.
Public binary packaging and toolchain-free first-run preparation remain separate
future work. This development executable must never be published as a release.
