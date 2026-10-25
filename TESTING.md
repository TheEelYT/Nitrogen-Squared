# Windows development test — 0.0.4

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
python tools/run_runtime.py
```

The command rechecks the disc and local executable inputs, starts a window, and
writes output to `.local/runtime-dev/runtime.log`. Test these in order:

1. Opening videos display and advance to the title screen. Check their audio.
2. The attract demo animates and displays the prompt to start.
3. Press **X on the keyboard** (PlayStation Cross) to enter the menus.
4. Navigate ship/level selection with the arrow keys; use **X** to confirm.
5. Continue through the tutorial prompts and try movement/firing in the first level.
6. Close the window and confirm the command returns to PowerShell.

Other default keyboard buttons: **S** = Circle, **Z** = Square, **A** = Triangle,
**Enter** = Start, **right Shift** = Select. Keyboard input is the initial P1 device;
gamepad selection/remapping UI is not integrated in this development wrapper yet.

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

While the game is running, a second PowerShell in the repository can collect
status counters without dumping RAM, code captures, or screenshots:

```powershell
python tools/probe_runtime.py
```

Do not attach the `generated`, `cache`, `overlay-private` directories or
`overlay_captures.json`; those can contain original game code/data.
