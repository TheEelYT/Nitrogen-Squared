# Nitrogen Squared

A Windows-first recompilation project for **N2O: Nitrous Oxide (PlayStation)**,
with a planned PS Vita port and optional remaster presentation.

**Current status: 0.0.15, expanded native gameplay and object control.**
117 additional roots cover game updates, object/presentation control, model
dispatch and resource/service control. The final selection passed 10,943 private
segment comparisons and 17 pixel-identical scanouts. The normal player build/controller fixture and Windows/Linux CI passed.
The user reports no issues in the focused Windows 0.0.15 playtest.
The user reported no issues in the focused Windows 0.0.14 playtest. Earlier
0.0.11 gameplay reached level 9 and 0.0.12 resolved the reported save/load slowdown;
those reports retain their tested version scope.

Normal launch requests the OpenGL render worker with one closed frame of lookahead.
System/Debug and analog input remain available. Native cutscene audio runs
independently of rendering. Gameplay sound production follows the guest clock;
native sound cues and unlocked presentation remain future work.

There is no public game executable or Vita VPK. The hybrid runtime uses native
boot/BIOS code, selected native game routines and interpreter fallback. Players
build privately from their verified local game input.

The 0.0.16 development branch has been reduced to 348 new entry roots: 236
call-target roots and 112 observed indirect/continuation boundaries. The O1
exploratory build reaches 34.9538% linked / 65.0462% outside and passed 18,633
comparisons plus 21 matching frames through first-level completion and bonus/shop
screens. Final O3 diagnostic, normal-production and platform checks are pending.
This is not accepted progress; main remains the accepted 0.0.15 runtime below.
No player rebuild is requested at this checkpoint.

## Native progress — 0.0.15

| Selected executable payloads | Bytes | Share |
| --- | ---: | ---: |
| Covered by linked native translations | 219,976 | **26.0073%** |
| Outside linked native translation ranges | 625,848 | **73.9927%** |
| Total | 845,824 | 100.00% |

These are executable-range measurements, not overall completion or native CPU
time. Payloads include embedded data. The selection adds 71,028 emitted bytes
from 78,396 input bytes over 0.0.14, increasing coverage from 17.6098% to 26.0073%
(about 1.48 times). N2O.EXE has 242 roots and 7,440 continuation aliases; aliases
add no byte/function credit. Analysis-only outputs for N2O.EXE and NEW.EXE receive
no credit. The normal player build reproduces the qualified diagnostic counts and
selected source/range hashes.

Native services are tracked separately: desktop presentation and controller
input use host implementations, and **3 of 3 opening movie routes** use native
playback. Game routines still submit PS1 drawing packets and use GTE, guest
SPU/CD audio and BIOS/card compatibility services. These services do not increase
the linked-range percentage above.

All 117 new roots were entered on the controlled menu/first-level route. The
final binding passed 968 live comparisons and 9,975 isolated replay comparisons
at 399 captured PCs, plus 17 matching-frame checks. Three mismatch owners and
140 other candidates without sufficient evidence remain unselected. These
bounded checks do not establish every branch, input or later campaign behavior.
All emitted bodies, instruction guards, witnesses and captures remain private.
Results and player status are recorded in the [native slices](docs/NATIVE_GAME_SLICES.md),
[metric](docs/NATIVE_PROGRESS.md), [validation](docs/VALIDATION.md) and
[focused testing instructions](TESTING.md).

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
