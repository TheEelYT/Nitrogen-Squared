# Development

Private builds and analysis require your own verified USA CUE/BIN. For the player
launcher, see the [README](../README.md#quick-start). Run the commands below from
the repository root.

## Developer importer

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
generated game C, compiled game modules, captures, or assets. The portable launcher described in the README automates this private build using downloaded tools.

See [player testing steps](../TESTING.md). World resolution and aspect follow the
window; the interface uses AUTO or a selected whole-number scale. Vita remains planned.
The OpenGL window now has **System** and **Debug** menus. **F1** hides/restores
the bar; **F11** toggles fullscreen. Settings and dropdowns pause the guest and
audio, while passive performance/audio overlays allow gameplay to continue.

After building, measure linked native translations with
`python tools/native_progress.py`. See [native progress](NATIVE_PROGRESS.md)
for the denominator and the distinction between native game code and host services.

## Direct-launch save paths

Portable preparation supplies `--save-dir` to build_runtime.py, which persists an
absolute save directory in game.toml. The portable launcher also repairs existing
configs and stale settings.toml memory-card overrides at startup and before play.
It backs up changed configuration and leaves the compiled executable untouched.
Both Ninja/Make and Visual Studio Release/ layouts are covered. Standalone
run_runtime.py follows the generated save directory unless --save-dir overrides it.
Older developer configurations retain their work-directory saves default.

The current 0.1.x launcher still refreshes a build when its public version changes;
this patch does not bring forward the general compilation-reuse work planned for
0.2.0. Opening the updated launcher alone applies this configuration repair without
running preparation. Direct launches still lack the environment setup supplied by
the launcher, including the native-movie disc binding; launcher play remains the
qualified route for the full startup/audio setup.

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
