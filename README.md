# Nitrogen Squared

A Windows-first recompilation project for **N2O: Nitrous Oxide (PlayStation)**,
with a planned PS Vita port and optional remaster presentation.

**Current status: 0.0.11, private Windows runtime with expanded native drawing preparation.**
The Windows build-metadata filename lookup is corrected; pull and rerun the build
if it failed after linking. Native coverage is unchanged at **4.0193%**, with
**95.9807%** outside linked ranges.
Twenty-five packet-building entries now join the two native angle-table readers.
Internal computed transfers resume in guarded native blocks; unsupported or changed
code retains interpreter fallback. Windows acceptance of this update is pending.
The user verified first-level gameplay in 0.0.10 and gameplay through level 4,
saves and high scores in 0.0.9. Later campaign levels remain unverified.
Normal launch requests the OpenGL render worker with one closed frame of lookahead.
System/Debug and analog input remain available. Native cutscene audio already
runs independently of rendering. Gameplay sound production still follows the
guest clock; native sound cues and unlocked presentation remain future work.

There is no public game executable or Vita VPK. The current hybrid runtime uses
native boot/BIOS code and interpreter fallback for much of the loaded game code.
A repeatable private build command is included.

## Native progress — 0.0.11

| Selected executable payloads | Bytes | Share |
| --- | ---: | ---: |
| Covered by linked native translations | 33,996 | **4.0193%** |
| Outside linked native translation ranges | 811,828 | **95.9807%** |
| Total | 845,824 | 100.00% |

These are executable-range measurements, not overall completion or the share of
CPU time spent natively. Payloads include embedded data. Linked translations
cover the boot loader and 27 selected entries in `N2O.EXE`; the full analysis
outputs for `N2O.EXE` and `NEW.EXE` are not linked. Game code still relies heavily
on interpreter fallback. This update adds 16,032 bytes over 0.0.10. Internal resume
aliases receive no additional byte or function credit.

Native services are tracked separately: the desktop frontend and controller input
use host implementations; **3 of 3 opening movie routes** use native playback.
Gameplay logic remains largely guest code, music/effects retain the guest SPU/CD
path, and ending/separate STR playback retains the original route. The OpenGL
worker schedules PS1 graphics commands; it does not replace the game's renderer
with a native scene engine. Host services do not increase the percentage above.

Next: expand verified slices and qualify their callers while retaining the
working fallback. See the [native slices](docs/NATIVE_GAME_SLICES.md),
[native roadmap](docs/ROADMAP.md) and [metric definition](docs/NATIVE_PROGRESS.md).
Every runtime update will refresh this section and [TESTING.md](TESTING.md),
including an explicit unchanged percentage when no new native ranges are linked.

## Bring your own game

The repository and release packages must contain **no game files**. Players
provide the complete USA BIN/CUE on first launch. Game executables, original
assets, music, generated game C, compiled game modules, memory snapshots and saves
remain private local data. Packaging uses an explicit source allowlist and rejects
unexpected staged files. See [distribution policy](docs/DISTRIBUTION.md).

The current verifier accepts one verified merged BIN/CUE layout, with one data
track and ten audio tracks. A different dump layout is rejected until separately
verified; that does not mean the user's disc is bad. Extract ZIPs before import.

## Try the importer

Requires Python 3.10 or later. It uses the standard library; no pip dependencies.
On Windows, the Python installer includes Tk for the initial setup interface.

```powershell
python tools/first_boot.py
```

This investigation UI imports inputs only. It does not launch a game. The complete
disc is verified using bounded reads, executables are extracted into the local user
data directory, and the original CUE/BIN stays in place for future disc/audio access.
Existing prepared directories are never overwritten.

For command-line inspection or private preparation:

```powershell
python tools/n2o_disc.py 'B:\Discs\N2O\N2O - Nitrous Oxide (USA).cue'
python tools/n2o_disc.py 'B:\Discs\N2O\N2O - Nitrous Oxide (USA).cue' --prepare .local/installation
```

## Developer analysis

Install Git, CMake 3.20+, Python 3.10+ and a C/C++ toolchain. On Windows, run in
a Visual Studio developer shell (VS 2022+), or use a working MinGW environment.
The bootstrap downloads a pinned upstream checkout separately into `.local/`.
Python 3.10 native-slice builds additionally need `python -m pip install tomli`;
Python 3.11+ includes its TOML reader. The importer needs neither.

```powershell
python tools/build_recompiler.py
python tools/generate.py --installation .local/installation --framework .local/psxrecomp --recompiler .local/build-recompiler/Release/psxrecomp-game.exe --output .local/analysis
```

For MinGW/Linux, the emitter is usually directly under `.local/build-recompiler/`;
adjust the `--recompiler` path. The generation command writes separate analysis
outputs for the boot loader, `N2O.EXE` and `NEW.EXE`, using the OpenBIOS profile.
It deliberately does not merge their overlapping code addresses or claim to build
a working runtime. Generated C and all private caches must stay out of Git/releases.

## Build the private development runtime

After importing the game, open a Visual Studio developer PowerShell with the C++
compiler and CMake available. In this repository:

```powershell
python tools/build_runtime.py
python tools/run_runtime.py
```

The build command uses the existing import in `%LOCALAPPDATA%\NitrogenSquared`,
builds the pinned framework tools, generates OpenBIOS and local game C, and links
a private desktop executable under `.local/runtime-dev`. It downloads third-party
source dependencies on the first build. Keep the original CUE/BIN in place.

**Do not upload or redistribute that executable:** it contains game code generated
from your own disc. The public source package still contains no game inputs,
generated game C, compiled game modules, captures, or assets. A toolchain-free
first-run compilation package remains future work.

See [Windows testing steps](TESTING.md). The current baseline uses original 4:3
presentation; remaster features follow gameplay validation. Vita remains planned.
The OpenGL window now has **System** and **Debug** menus. **F1** hides/restores
the bar; **F11** toggles fullscreen. Settings and dropdowns pause the guest and
audio, while passive performance/audio overlays allow gameplay to continue.

After building, measure linked native translations with
`python tools/native_progress.py`. See [native progress](docs/NATIVE_PROGRESS.md)
for the denominator and the distinction between native game code and host services.

## Checks

```powershell
python -m unittest discover -s tests -v
python tools/package_source.py --check-tracked
python tools/package_source.py --output dist/Nitrogen-Squared-source.zip
```

Tests use hand-authored synthetic sectors and code, never the commercial disc.
The source ZIP uses only reviewed text files; `.local/` is never traversed.
CI runs the tests and packaging audit on Windows and Linux without game data.
It also links the complete runtime with an original synthetic program, exercises
virtual gamepad input, and compares the reference/enhanced renderer on Linux.

See [disc findings](docs/DISC_ANALYSIS.md), [roadmap](docs/ROADMAP.md), and
[validation record](docs/VALIDATION.md). Original code is MIT licensed. Dependencies
have separate terms described in [THIRD_PARTY.md](THIRD_PARTY.md).
