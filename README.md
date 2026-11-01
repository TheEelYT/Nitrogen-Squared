# Nitrogen Squared

A Windows-first recompilation project for **N2O: Nitrous Oxide (PlayStation)**,
with a planned PS Vita port and optional remaster presentation.

**Current status: 0.0.28 — bonus HUD anchors and a Linux launcher package.**
All bonus stars stay beside the score, and the bonus-level speed readout and
backing share the bottom-left HUD transform. Other reported UI fixes retain
their tested behavior. Square pixels, 2x floor and 365x240 reference remain.
[Display policy](docs/WINDOW_DISPLAY.md).

Native coverage stays **38.4156% linked / 61.5844% outside**, 324,928 / 845,824
bytes. This host/launcher update adds no native ranges. The metric includes
payload data and is not project completion or CPU time. Windows/Linux runtime
and both package checks pass; all five published assets are audited. Fresh focused
player checks are pending.
The previous level-entry hitch still needs explicit Windows confirmation.

The Windows release contains launcher.exe, supporting source and portable Python.
First launch selects your USA CUE/BIN and privately verifies, extracts, generates,
compiles and plays. Use **Check for updates**, preserving .local and existing saves.
No separate Python or Visual Studio installation is needed.

All three submitted 0.0.23 Windows/dashboard checks pass: update/private-build
refresh, opening playback/menus/short gameplay and existing saved-slot loading.
The reported route is accepted; earlier reports retain their version. No repeat
test, new campaign, upload or valued-save overwrite is requested. USA remains
the supported base.

**Asset folders** preserves original containers, raw movie streams and ten PCM
WAV tracks under .local/game. Runtime still uses the original disc. Folder-backed
loading, mod packs, optional user-owned EU language assets and logic/render clock
separation remain future work.

## Play on Windows

1. Download [Nitrogen-Squared-Windows-x64.zip](https://github.com/TheEelYT/Nitrogen-Squared/releases/download/v0.0.28/Nitrogen-Squared-Windows-x64.zip)
   from the [0.0.28 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.28).
2. Extract the complete **Nitrogen-Squared** folder somewhere you can write to,
   then run **launcher.exe**. Windows 10/11 x64 is supported.
3. Select your supported USA **CUE** sheet, keeping its matching BIN beside it.
   A BIN selection works only when its matching CUE can be found beside it.
4. Let first preparation finish. Internet access is needed to download pinned
   tools and dependencies; compilation can take several minutes. Later launches
   reuse the prepared game. Keep your original disc files available.

Everything downloaded, extracted or generated, including saves, stays under
`Nitrogen-Squared/.local`. The original selected disc stays at its existing path.
Use **Check for updates** in the launcher; updates preserve `.local` and rebuild
the private game when needed. Keep the whole folder together. Moving it causes a
fresh build cache to be prepared while retaining saves. Do not delete `.local` to
update. Portable saves are in `.local/saves`; developer-build saves remain in their
existing location unless copied deliberately.

The public executable is the original launcher. The game executable is generated
privately from the player's verified input and must not be redistributed. No Vita
VPK is available. The runtime retains native boot/BIOS, selected native game
routines and interpreter fallback, with the pinned PSXRecomp framework still in use.

## Play on Linux x86_64

Download [Nitrogen-Squared-Linux-x64.zip](https://github.com/TheEelYT/Nitrogen-Squared/releases/download/v0.0.28/Nitrogen-Squared-Linux-x64.zip),
extract the whole folder and run `sh launcher.sh`. Select the same supported USA
CUE/BIN. The shared launcher verifies/imports/generates/builds/plays and handles
updates, keeping all project state and saves in .local. Keep Windows and Linux
installations in separate folders.

Linux uses system Python 3.11+ with Tk, Git, CMake, Make, a C11/C++17 compiler,
pkg-config and graphics/audio development packages. See README-FIRST.txt for the
Ubuntu 24.04+ prerequisite command and equivalent packages on other distributions.
The launcher does not use sudo. Framework/SDL revisions stay pinned and download
inside .local. This is a source launcher package; no game binary or commercial
assets are distributed. Local gameplay uses Linux OpenGL; broader desktop,
Wayland and audio-device compatibility remain player checks.

## Native progress — 0.0.28 (unchanged selection)

| Selected executable payloads | Bytes | Share |
| --- | ---: | ---: |
| Covered by linked native translations | 324,928 | **38.4156%** |
| Outside linked native translation ranges | 520,896 | **61.5844%** |
| Total | 845,824 | 100.00% |

The retained 0.0.23 batch adds 13 N2O roots while preserving all 783 earlier
input records; 0.0.26 adds no further native ranges.
N2O: 296,520 bytes (64.6362%), 645
roots and 11,133 aliases. NEW: 10,500 bytes
(3.1454%), 152 roots and 300 aliases.
Boot is unchanged. Aliases earn no extra byte credit.

Larger-target exploration uses ordinary scripted controller inputs and disposable
card copies. Final routes cover saved-game loading, later-level play, slot saving,
fresh setup creation/load/overwrite and the expanded tutorial/gameplay route.
Final reduced O3 checks pass 240 live + 3,175 replay = 3,415
comparisons, zero mismatches, and 166 exact frames. Card outputs match reference
bytes. Normal source/range hashes match and the movie/controller/pause/quit fixture
passes without qualification hooks. Source and cross-platform package/runtime CI
gate publication. See [validation](docs/VALIDATION.md) and [player checks](TESTING.md).

These are executable-range measurements, not overall completion or native CPU
time. Payloads include embedded data. A new private code/data inventory records
linked translations, tentative static-code/data hints, conflicts and unknown
ranges separately; it does not invent a code-only denominator or change this
metric. The launcher and mapping tools add no native byte credit.

Desktop presentation and controller input use host implementations, and **3 of 3
opening movie routes** use native playback. The launcher supplies the verified disc
and the same runtime settings as the Python launch path. Game routines still use
PS1 drawing packets/GTE, guest SPU/CD audio and BIOS/card compatibility services.
Normal launch requests the bounded OpenGL render worker. Native movie audio has
its own timeline; gameplay audio and simulation/render clock separation remain
future work. The user accepted launcher-built Windows 0.0.18 through level 9
with successful saving and no issues noticed; see TESTING.md.

## Bring your own game

The repository and release packages must contain **no game files**. Players
provide the complete USA BIN/CUE on first launch. Game executables, original
assets, music, generated game C, compiled game modules, memory snapshots and saves
remain private local data. Packaging uses an explicit source allowlist and rejects
unexpected staged files. See [distribution policy](docs/DISTRIBUTION.md).

The current verifier accepts one verified merged BIN/CUE layout, with one data
track and ten audio tracks. A different dump layout is rejected until separately
verified; that does not mean the user's disc is bad. Extract ZIPs before import.

## Private asset extraction

The launcher's **Asset folders** button optionally organizes the verified player's
textures, models, maps,
sound banks, text, movies and CD music under `.local/game`. It preserves original
containers and movie sectors, exports CD music as PCM WAV, and records file/track
aliases and hashes. Runtime still needs the original BIN; replacement-pack loading
and folder-backed runtime access are separate work. See [asset folders and the
modding plan](docs/ASSETS.md) for the bundled-Python command and current scope.

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
generated game C, compiled game modules, captures, or assets. The portable release above automates this private build using downloaded tools.

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
