# Windows development test — 0.0.6

The disc import already created `%LOCALAPPDATA%\NitrogenSquared\SLUS-00637`.
Leave that folder and your original CUE/BIN in place. You do not need to reimport.

## Build

Open **Developer PowerShell for Visual Studio**, with the Desktop development with
C++ workload installed. Use the installed Visual Studio development environment;
ordinary PowerShell may not have CMake/compiler tools on PATH.

```powershell
Set-Location B:\Nitrogen-Squared
git pull --ff-only
python --version
cmake --version
python tools/build_runtime.py
```

If CMake is missing, enable **C++ CMake tools for Windows** in the Visual Studio
Installer, reopen Developer PowerShell, and repeat the command. Python 3.10+ and
CMake 3.20+ are required. No Sony BIOS or additional game download is needed.

Version 0.0.3 fixes the Visual Studio configuration failure mentioning
`psx_game_version.txt` being written multiple times with different content. Pull
the update and repeat `python tools/build_runtime.py` in the existing build folder;
the project refreshes the cached version automatically.

Version 0.0.4 enables MSVC's conforming lambda processor for the runtime C++ code
and its C11 atomics support for the C code. These address C2131 at the session-start
`static_assert` and C1189 (`C atomic support is not enabled`). A small MSVC-only
adapter also supplies the renderer's two GNU-style atomic calls using Windows
Interlocked intrinsics. Pull and repeat the same build command; the existing
C11/C++17 language mix and build folder are reused.

Version 0.0.5 makes expensive per-instruction diagnostics opt-in, removes
continuous full-VRAM history from normal launch, and explicitly routes the first
gamepad to Player 1. A small OpenGL adapter republishes CPU VRAM when N2O switches
from movie mode to its title image. Rebuild with the normal command above to
replace the older instrumented executable and refresh the controller defaults.
The baseline explicitly uses native internal resolution; HD enhancements remain
future work.

Version 0.0.6 enables the pinned renderer's ordered textured batching. The animated
main menu previously submitted almost one OpenGL batch per primitive. The enhanced
path combines compatible work while retaining draw order and the reference path
for mask checks and subtractive blending. The same build command replaces the
cached renderer selection. It also refreshes the controller configuration to
analog DualShock mode, so the game can recognize analog support. No reimport is
needed. To compare the old digital pad deliberately, rebuild with
`python tools/build_runtime.py --controller-mode digital`.

The OpenBIOS emitter currently prints cross-function-target warnings. The same
warnings appeared in the development-host run that reached the first level;
they do not themselves indicate that CMake configuration or compilation failed.
Keep the warnings when reporting an actual runtime failure.

The first build fetches the pinned framework/dependencies, builds the analysis
tools, generates local game code, then compiles the desktop runtime. It can take
several minutes. Subsequent builds reuse the private generated inputs and build
tree. If preparation was interrupted, use a new `--work-dir` instead of deleting
or replacing an existing import/save folder.

Success prints a path to `NitrogenSquared-dev.exe` and creates
`.local/runtime-dev/runtime-build.json`. A compiled binary is not by itself proof
of working gameplay. Do not upload this executable or its generated inputs.

## Launch and check

```powershell
python tools/run_runtime.py --show-fps
```

The command rechecks the disc and local executable inputs, starts a window, and
writes output to `.local/runtime-dev/runtime.log`. Test these in order:

1. Opening videos display and advance to the title screen. Check their audio.
2. The attract demo animates and displays the prompt to start.
3. With an Xbox controller connected, press **A** (PlayStation Cross) to enter the menus.
4. Check that the game recognizes an analog controller. Navigate ship/level selection
   with the D-pad or left stick; use **A** to confirm. Stick movement is now sent as
   analog axes rather than converted into D-pad presses; menu behavior follows the game.
5. Continue through the tutorial prompts and try movement/firing in the first level.
   Record speed both while **entering game** is displayed and after it disappears.
6. Close the window and confirm the command returns to PowerShell.

Other default keyboard buttons: **S** = Circle, **Z** = Square, **A** = Triangle,
**Enter** = Start, **right Shift** = Select. **X on the keyboard** is PlayStation
Cross and the arrow keys move. Keyboard bindings stay available alongside the
first gamepad, including when no pad is connected. Xbox **B/X/Y** map to
Circle/Square/Triangle; the Menu button maps to Start. Selection/remapping UI is
not integrated yet. A successful controller open is recorded in `runtime.log`.

Compare the **Game** speed readout on the opening videos, swirling main menu
background, and first level. About **1.00x** is the target; record the speed where
audio breaks up. This counts simulated frames, so a static logo can update the
window infrequently while the game itself still runs at full speed.

If OpenGL fails or draws incorrectly, compare with:

```powershell
python tools/run_runtime.py --renderer software
```

The software path is a diagnostic comparison, not an HD rendering mode. This build
retains original 4:3 presentation and timing goals; the remaster work is not enabled.

## Report

Report the furthest screen reached, any visual/audio issues, movement/firing
behavior, and whether closing works. For a build failure, paste the last error block
from PowerShell. For a startup failure, attach `.local/runtime-dev/runtime.log`.

The normal build omits the TCP server and per-instruction tracing. If detailed
diagnosis is needed, prepare a separate instrumented build:

```powershell
python tools/build_runtime.py --diagnostics --work-dir .local/runtime-diagnostics
python tools/run_runtime.py --work-dir .local/runtime-diagnostics --show-fps
```

While that build runs, a second PowerShell in the repository can collect bounded
status, audio underruns, pad state and a ten-second guest-speed sample:

```powershell
python tools/probe_runtime.py --seconds 10 --output .local/runtime-diagnostics/status.json
```

Use the normal build to assess play speed: tracing can make the diagnostic build
slower. Full-VRAM frame history remains off unless a diagnostic run explicitly
uses `run_runtime.py --display-ring`.

Do not attach the `generated`, `cache`, `overlay-private` directories or
`overlay_captures.json`; those can contain original game code/data.
