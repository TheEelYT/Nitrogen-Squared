# Nitrogen Squared

A Windows-first recompilation project for **N2O: Nitrous Oxide (PlayStation)**,
with a planned PS Vita port and optional remaster presentation.

**Current status: investigation and disc preparation. There is no playable
Windows executable or Vita VPK yet.** The disc importer is implemented; isolated
entry-reachable C generation has been exercised against the USA disc. That is
not proof of working gameplay or complete code coverage.

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

```powershell
python tools/build_recompiler.py
python tools/generate.py --installation .local/installation --framework .local/psxrecomp --recompiler .local/build-recompiler/Release/psxrecomp-game.exe --output .local/analysis
```

For MinGW/Linux, the emitter is usually directly under `.local/build-recompiler/`;
adjust the `--recompiler` path. The generation command writes separate analysis
outputs for the boot loader, `N2O.EXE` and `NEW.EXE`, using the OpenBIOS profile.
It deliberately does not merge their overlapping code addresses or claim to build
a working runtime. Generated C and all private caches must stay out of Git/releases.

## Checks

```powershell
python -m unittest discover -s tests -v
python tools/package_source.py --check-tracked
python tools/package_source.py --output dist/Nitrogen-Squared-source.zip
```

Tests use hand-authored synthetic sectors and code, never the commercial disc.
The source ZIP uses only reviewed text files; `.local/` is never traversed.
CI runs the tests and packaging audit on Windows and Linux without game data.

See [disc findings](docs/DISC_ANALYSIS.md), [roadmap](docs/ROADMAP.md), and
[validation record](docs/VALIDATION.md). Original code is MIT licensed. Dependencies
have separate terms described in [THIRD_PARTY.md](THIRD_PARTY.md).
