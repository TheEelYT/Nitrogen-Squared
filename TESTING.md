# Windows development test — 0.0.9

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

Version 0.0.7 adds **System** and **Debug** menus to the OpenGL window. The first
build downloads a pinned Dear ImGui dependency. The persistent bar reserves space
above the complete 4:3 game image. Autohide instead reveals it over the image when
the mouse reaches the top. This frontend is separate from the diagnostic software
renderer; use the default OpenGL launch to test the menu.

Version 0.0.8 moves the three opening clips to native STR/XA decoding. A video
worker prepares frames while an independent SDL callback consumes predecoded
audio. Presentation follows the audio timeline; no FFmpeg install is required.
Media and instruction guards come only from the verified local import. The ending
and separate in-game movie route retain original playback.

Version 0.0.9 requests the existing OpenGL render worker through the launch
wrapper, with one closed frame of queued work. The original game clock remains
unchanged. Shutdown joins the worker. Audio Status now shows buffer fill/target
and starvation counters through a safe snapshot, including in normal builds.
The FPS title retains its original base across menu pauses.

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

1. Let all three opening clips finish. The title bar says **[Native video]**.
   Listen for continuous audio and check sound/image synchronization. Resize and
   toggle fullscreen, then confirm the complete title image appears afterward.
2. Restart and skip clips with Xbox **A/Start** or keyboard **X/Enter**. During a
   clip open **System → Settings**: audio and video should pause and resume
   together. Check volume/mute as well.
3. The attract demo animates and displays the prompt to start.
4. With an Xbox controller connected, press **A** (PlayStation Cross) to enter the menus.
5. Check that the game recognizes an analog controller. Navigate ship/level selection
   with the D-pad or left stick; use **A** to confirm. Stick movement is now sent as
   analog axes rather than converted into D-pad presses; menu behavior follows the game.
6. Continue through the tutorial prompts and try movement/firing in the first level.
   Record speed both while **entering game** is displayed and after it disappears.
7. Close the window and confirm the command returns to PowerShell.

Other default keyboard buttons: **S** = Circle, **Z** = Square, **A** = Triangle,
**Enter** = Start, **right Shift** = Select. **X on the keyboard** is PlayStation
Cross and the arrow keys move. Keyboard bindings stay available alongside the
first gamepad, including when no pad is connected. Xbox **B/X/Y** map to
Circle/Square/Triangle; the Menu button maps to Start. Selection/remapping UI is
not integrated yet. A successful controller open is recorded in `runtime.log`.

During native movies, the guest simulation is intentionally frozen. Its FPS
is not movie speed. Compare the **Game** readout on the swirling main menu
background, and first level. About **1.00x** is the target; record the speed where
audio breaks up. This counts simulated frames, so a static logo can update the
window infrequently while the game itself still runs at full speed.

### Desktop menu checks

1. With `--show-fps`, open **System**, then click back into the game at least six
   times. Allow a second between cycles. There should remain one **Game** group
   and one **Present** group in the title bar, with current values.
2. Confirm the top bar contains only **System** and **Debug**, and that the top of
   the game image/HUD remains visible below it.
3. Open **System → Settings**. The game and audio should pause; **Escape** or the
   settings window's close button resumes them. Game controls must not leak through.
4. Change volume/mute, close Settings, and listen. Reopen the application and check
   that the volume and menu visibility preferences were retained.
5. Test **F1** to hide and restore the bar, **Autohide Menu Bar** with the mouse at
   the top edge, and **F11** to enter/leave fullscreen. Resize the window as well.
6. Enable the two **Debug** overlays. Gameplay should continue. Display FPS is a
   presentation measurement; it is separate from the title bar's guest-speed value.
7. **Hard Reset** must ask before restarting. Cancel once, then test Restart only
   when losing current unsaved progress is acceptable. Confirm saved data remains.
8. Test **Quit Application**, and check the ordinary window-close button as well.

Menu preferences are private `nitrogen-menu.ini` beside the executable. Fullscreen
uses the framework's existing settings persistence. During native clips,
**Debug → Audio Status** shows media seconds and submitted
samples. Gameplay music/effects retain the guest SPU/CD path; those are not yet
decoupled from simulation.

### Render worker and audio checks

Enable **Debug → Performance Overlay**. During gameplay the worker should show
active (or synchronized briefly at a required readback), with a queued-frame
bound of 1. Check menu pause/resume, fullscreen, movie skipping and ordinary
window close. The two debug panels should stack without overlapping.

**Debug → Audio Status** shows SPU output rate, host format, buffer fill/target,
underflow samples and overflow frames. Legacy queue mode labels empty-queue
events instead. Counters are cumulative; note whether they grow during steady
gameplay separately from startup, loading or fullscreen changes. Guest sound
production still follows the game clock. The last sampled counters are written
to `runtime.log` on clean shutdown, without needing the TCP debugger.

Compare synchronous rendering without rebuilding:

```powershell
python tools/run_runtime.py --show-fps --render-worker off
```

Ordinary launch requests the worker again. An existing `PSX_RENDER_THREAD`
environment value is honored unless `--render-worker on` or `off` is supplied.
Software rendering always disables the worker. Higher presentation rates beyond
the original game cadence remain future work.

To generate the native coverage report after building:

```powershell
python tools/native_progress.py
```

The report counts only native ranges linked into the build, excluding generated
analysis-only translations and host/BIOS code. Its payload denominator includes
embedded data, so it is not an estimate of overall project completion.

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
