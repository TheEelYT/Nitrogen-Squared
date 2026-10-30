# Nitrogen Squared

A Windows-first recompilation project for **N2O: Nitrous Oxide (PlayStation)**,
with a planned PS Vita port and optional remaster presentation.

**Current status: 0.0.20 — 53 further qualified native entry roots.**
The new binding adds 8,188 linked bytes: **36.4341% linked / 63.5659% outside**.
These are observed game/library fragments, not 53 newly identified complete
functions or a native CPU-time share. Final checks passed 3,044 bounded comparisons
and 50 pixel-identical frames across two routes reaching second-level play.

The Windows release includes `launcher.exe`, supporting source and portable
Python. First launch selects your CUE sheet and automatically verifies, extracts,
generates, compiles and starts your private game. Use **Check for updates** in an
existing launcher; keep .local and your saves. No separate Python or Visual Studio
installation is needed. The short 0.0.20 Windows player check is pending; see TESTING.md.

The user accepted 0.0.18 launcher-built gameplay through level 9 with successful
saving and no issues noticed, then confirmed gameplay and **Asset folders** in
0.0.19. Those reports retain their version scope; no repeated campaign is needed.

Use **Asset folders** after disc import to extract original texture/model/map/
sound/text containers, raw movie streams and ten PCM WAV music tracks into
`.local/game`. Later uses open that folder and preserve edits. The runtime still
uses the original CUE/BIN; folder-backed loading and replacement packs remain
future work. Logic/render clock separation remains deferred.

## Play on Windows

1. Download [Nitrogen-Squared-Windows-x64.zip](https://github.com/TheEelYT/Nitrogen-Squared/releases/download/v0.0.20/Nitrogen-Squared-Windows-x64.zip)
   from the [0.0.20 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.20).
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

## Native progress — 0.0.20

| Selected executable payloads | Bytes | Share |
| --- | ---: | ---: |
| Covered by linked native translations | 308,168 | **36.4341%** |
| Outside linked native translation ranges | 537,656 | **63.5659%** |
| Total | 845,824 | 100.00% |

This batch adds 40 N2O and 13 NEW entry roots, preserving all earlier bindings.
N2O.EXE contributes 282,576 bytes (61.5967%); NEW.EXE contributes 7,684 bytes
(2.3018%); boot is unchanged. There are 602 N2O roots, 127 NEW roots and 10,717
continuation aliases. Aliases earn no extra byte credit. Failed or insufficiently
observed candidates retain fallback.

Final O3 qualification passed 269 live plus 2,775 fail-fast replay comparisons,
with no mismatches and 50 pixel-identical frames through second-level play.
The normal build matches the qualified source/range hashes, has no comparison
hooks, and passes the movie/controller/pause/quit fixture. Windows/Linux source,
runtime and portable package/update checks gate publication. See
[validation](docs/VALIDATION.md) and [focused player checks](TESTING.md).

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
