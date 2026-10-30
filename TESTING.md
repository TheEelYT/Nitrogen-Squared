# Windows release and development test — 0.0.19

## Current acceptance and update checks

**0.0.19 — reported Windows gameplay and Asset folders flow accepted.**
After a verified disc import, **Asset folders** extracts original containers and
movie sectors plus ten PCM WAVE music tracks into .local/game. Later uses open
the existing folder without overwriting edits. The game still reads its original
CUE/BIN; replacement-pack loading and folder-backed runtime access are future work.

The extractor privately catalogued all 27 ISO records and produced 37 outputs,
including track pregaps. Every output payload matched its source bytes. Seven
original synthetic asset tests cover formats, aliases, preservation, interrupted
extraction and launcher action; the source suite has 80 cases. Windows package/
startup/update and Windows/Linux source/runtime CI passed for this feature.
Release publication independently requires the complete check set.

The user downloaded and tested 0.0.19, reports gameplay is still fine, and
confirms that **Asset folders** works as intended. Accept that reported Windows
route and asset-folder flow. This report does not separately establish every
output file, mod loading, a new level-9 campaign or another save/reload test.
The 0.0.18 level-9/save report retains its version scope. No rebuild, repeat
campaign, deliberate save overwrite or new upload is requested for this
documentation-only acceptance note. Preserve .local and the original disc.

This release enables no further game ranges. Coverage remains **35.4660% linked /
64.5340% outside**, 299,980 / 845,824 bytes. The exploratory native batch was held
when its execution environment became unavailable during final O3 compilation;
its final strict/replay/normal checks are incomplete, so it earns no coverage.

**0.0.18 — Windows launcher preparation and gameplay accepted through level 9.**
The supplied setup.log shows successful disc verification and preparation-tool
compilation, followed by CMake rejecting backslashes in the explicit resource-
compiler path as escapes (`\G`). The launcher now passes forward-slash compiler
and Python paths. It also archives an existing broken runtime build configuration,
including persisted compiler files, without discarding completed preparation,
imports or saves. Nothing needs to be deleted or reuploaded.

All 73 local source tests pass, including reproduction of the actual CMake syntax
failure, its corrected path, damaged-cache recovery and reuse of healthy caches.
The portable Windows runtime fixture now consumes the same CMake arguments as the
player build, covering the previously missed configuration path. The Windows
package/toolchain/update fixture and both operating systems' source/runtime
workflows passed before publication. No native code or service selection changes:
**35.4660% linked / 64.5340% outside**, 299,980 / 845,824 bytes, unchanged.

The user reports that the launcher-built game plays the same as the command-line
build, completed another playthrough through level 9 with no issues noticed, and
saved successfully. This accepts real-disc preparation and the reported Windows
0.0.18 player route, superseding the pending retry. It also provides player
acceptance of the unchanged 0.0.17 native selection as shipped in 0.0.18.

This report does not establish every checklist action, every branch or levels
beyond 9; save reload and a particular update-installation method were not
separately reported. No rebuild, additional files, repeat campaign or deliberate
save overwrite is requested for this documentation-only acceptance note. Preserve
existing saves. Further focused checks will accompany actual behavior changes.

**0.0.17 — portable launcher and native fragment batch; preparation repaired and player route accepted in 0.0.18 above.**
The public Windows ZIP now contains a Nitrogen-Squared folder with launcher.exe,
portable Python and reviewed supporting source. CUE selection verifies the user's
complete disc, then privately downloads tools, extracts/generates/compiles and
launches the game. No separate Python or Visual Studio installation is needed.
Updates use a copied process, verify package hashes/inventory, back up owned files
and preserve .local, including saves and the private game cache.

The native batch adds 86 entry roots and expands one existing owner: +4,332 linked
bytes, **35.4660% linked / 64.5340% outside** (299,980 / 845,824). This measures
executable ranges, not project completion or native CPU time. The incremental
code/data inventory labels hints and unknowns without changing that denominator.
Final O3 qualification passed 5,162 comparisons with zero mismatches and 42
matching captures; normal production coverage/hashes and the movie/controller/
pause/quit fixture passed. All 69 source tests, the 95-file audit, Windows/Linux CI and Windows package/update
integration pass.
Automated results and limits are recorded in docs/VALIDATION.md.

Focused Windows release checks:

1. Extract the complete release folder to a writable location. Run launcher.exe,
   choose the supported USA CUE with its matching BIN beside it and let preparation
   finish. Check that all preparation files are inside the extracted folder.
2. Let the opening movies play; confirm **[Native video]**, normal audio/video
   playback and return to the title. The launcher supplies the verified-disc
   environment that direct execution of the private game EXE lacked.
3. Navigate menus/ship selection, play a short first-level session with analog
   movement and firing, then pause/resume and quit normally.
4. Reopen the launcher and use Check for updates. An unchanged release should
   report that it is current. A real newer-release update will be checked when
   one exists; CI separately tests replacement, restart and save preservation.

The initial 0.0.17 real-disc preparation stopped at the compiler-path error.
Version 0.0.18 repairs it, and its reported launcher-built route is now accepted
through level 9. Windows CI separately tests actual startup, bundled-toolchain/
runtime compilation on synthetic inputs and copied-process update/restart.
The historical checklist above is not a request to repeat the accepted route.
No repeated campaign, new upload or deliberate save overwrite is requested.
Preserve existing saves; the release uses .local/saves. To bring developer saves
across, close both versions and copy valued files from .local/runtime-dev/saves
into the release's .local/saves without overwriting another valued save.

The developer instructions below remain available for source builds; the release
launcher does not require them. Prior acceptance retains its tested version scope.

**0.0.16 — automated checks passed; reported Windows player route accepted.**
The user reports no issues noticed and that everything looks the same as before
when launched through Python. Direct EXE launch stutters during intro videos;
that separate launch-path issue is open. This report accepts the tested route,
without implying exhaustive coverage or a new campaign playthrough.
348 additional game/library entry roots add 75,672 emitted bytes. Combined
normal-build coverage is **34.9538% linked / 65.0462% outside** (295,648 /
845,824 bytes). This is executable-range coverage, not overall completion or
native CPU time. The additions include 236 call-target roots and 112 observed
indirect/continuation boundaries, not 348 newly identified complete functions.

Final O3 qualification passed 18,633 private segment comparisons (1,458 live and 17,175 isolated replay) at 687 identity/PC
pairs and 21 pixel-identical frames through first-level completion and bonus/shop.
All 348 identities were observed. The normal diagnostics-disabled player and
movie/controller/quit fixture passed with matching selected source/range hashes.
All 45 source tests, the 83-file source audit and both Windows/Linux CI matrices
passed. Failed/unobserved candidates and NEW movie-control callers remain on
fallback. These bounded checks do not establish every input or later-level behavior.

The focused player-check scope for this update is:

1. Navigate title/menu, ship and level selection; check labels, models and animation.
2. Play a short first-level session with analog movement and firing. Check enemies,
   shots, explosions, HUD, score/life counters and transitions. If bonus/shop screens
   arise naturally, check their labels and controls; reaching them is not required.
3. Pause/resume, continue playing briefly and quit normally.

No repeated campaign, new files, reimport or deliberate save overwrite is required.
Preserve existing saves. No rebuild or repeat playtest is required for this
acceptance note. Prior reports retain their tested version scope.

Direct-launch diagnosis: tools/run_runtime.py supplies NITROGEN_NATIVE_DISC_BIN
from the verified import. native/media_entry.cpp declines native movie playback
when this variable is absent and keeps the original guest playback path. The
launcher also explicitly selects OpenGL, enables the bounded render worker and
disables full-VRAM history. This provides a likely explanation for the observed
launch difference; the user's direct-launch log has not been inspected and no
fix is claimed. Continue using tools/run_runtime.py for the qualified launch path.
Making direct EXE launch initialize the same settings remains follow-up work.

**0.0.15 — focused Windows playtest accepted:** the user reports no issues
noticed. This accepts the reported route without implying exhaustive coverage
or a new level-9 campaign playthrough. No repeat test is needed for this note.
117 additional roots cover game updates, object/presentation control, model
dispatch and resource/service control. The final binding passed 10,943 private
comparisons (968 live and 9,975 replay) and 17 pixel-identical scanouts. All 117
new roots were observed directly. The normal diagnostics-disabled build and
movie/controller/shutdown fixture passed, selected source/range hashes match,
all 40 source tests and the 79-file source audit pass, and Windows/Linux source
and runtime CI matrices passed for the final code.

Linked normal-build coverage is **26.0073% / 73.9927%** (219,976 / 845,824 bytes,
+71,028 from 0.0.14). N2O has 242 roots and 7,440 aliases. This measures linked
executable ranges, not overall completion or native CPU time. Three mismatch
owners and 140 other unqualified candidates remain on fallback. Captured inputs
and generated game code stay private. Bounded comparisons do not prove every
branch, input or later-level scenario.

The focused player-check scope was:

1. Navigate title/menu, ship and level selection; check labels, models and animation.
2. Play a short first-level session with analog movement and firing. Check enemies,
   shots, explosions, ship/object effects, HUD and score/life counters.
3. Pause/resume, continue playing briefly and quit normally.

The user reports no issues noticed in Windows 0.0.15; the focused playtest is
accepted. No repeated campaign, new files, reimport or deliberate save overwrite
is required. Preserve existing saves.
The accepted 0.0.14 Windows playtest remains history for that version.

**0.0.14 — focused Windows playtest accepted:** the user reports no issues
noticed. This accepts the tested route without implying a new level-9 campaign
playthrough or exhaustive coverage. No repeat test is needed for this note. 46 additional roots now cover model/object primitive
preparation and game/menu presentation control. Residency guards, continuation
aliases and interpreter fallback remain in use. The previous 0.0.13 focused
Windows playtest was accepted; it does not automatically accept this update.

Linked coverage is **17.6098% / 82.3902%** (148,948 / 845,824 bytes, +75,948
bytes from 0.0.13), about 2.04 times the previous linked share. N2O has 125 roots
and 4,189 aliases; aliases add no byte/function credit. This measures executable
ranges, not project completion or native CPU time. PS1 graphics/GTE, guest SPU/CD
and BIOS/card compatibility services remain in use.

Completed: 10,316 final-selection CPU/RAM/scratchpad/GTE segment comparisons,
with all 46 new roots covered; 17 pixel-identical scanouts on the extended
menu/first-level route; 40 local source tests; the 71-file source-package audit;
and both Windows/Linux source and runtime CI matrices for the final binding.
The normal diagnostics-disabled build and movie/controller/shutdown fixture
passed, and its selected source/range hashes match the qualified build. One candidate with an exception/return mismatch and 28 without adequate
evidence remain unselected. These bounded checks do not prove every branch,
input or later-level scenario. Details are in docs/VALIDATION.md.

The completed focused player checks were:

1. Navigate title/menu, ship and level selection. Check labels, models and animation;
   confirm existing score/save-slot labels remain readable.
2. Play a short first-level session with analog movement and firing. Check tunnel
   surfaces, enemies, shots, explosions, ship effects, HUD and score/counters.
3. Pause/resume, continue moving/firing, return to the menu and quit normally.

No later-level progression, reimport, new files or deliberate save overwrite is
required. Preserve existing saves. The focused Windows 0.0.14 route is accepted;
no repeated campaign playthrough is requested.

**0.0.13 — focused Windows playtest accepted:** the user reports no issues
noticed. This accepts the tested menu/first-level route without implying a new
level-9 campaign playthrough or exhaustive coverage. No repeat test is needed
for this acceptance note. 32 additional geometry, object/drawing, angle and
text-formatting entry ranges now execute natively. Whole-owner residency guards,
internal resumes and interpreter fallback remain in use. Saves retain their
existing card format and BIOS/serial services.

Linked coverage is **8.6306% / 91.3694%** (73,000 / 845,824 bytes, +36,932 bytes
from 0.0.12). This is executable-range coverage, not total completion or native
CPU time. The update does not enable a native scene engine, independent gameplay
audio or unlocked framerate.

Completed: 17,475 private CPU/RAM/scratchpad/GTE segment comparisons across live
and constructed inputs, with all 32 new roots covered; 20 pixel-identical frame
comparisons across two controlled menu/first-level routes; 40 local source tests;
and Windows/Linux runtime/source CI for the final code checkpoint. The normal
diagnostics-disabled build and private movie/controller/shutdown fixture passed. Prior level-9 gameplay
and 0.0.12 save/load acceptance remain history, not acceptance of this replacement.

The completed focused player checks were:

1. Navigate the title/menu, ship and level selection; check labels and animation.
2. Play a short first-level session with analog movement and firing. Check the
   tunnel, enemies, shots, explosions, HUD and score text.
3. Pause/resume, return to the menu and quit normally. Check existing high scores
   and save-slot labels are still readable; no deliberate save overwrite is needed.

No later-level progression, reimport or new files are required. Completed local
and platform results are recorded in docs/VALIDATION.md.

**Historical 0.0.12 native-call qualification — passed; no rebuild for that
test-only update:** new
original synthetic programs test the real runtime dispatcher across indirect
calls, interpreted callees, native callbacks, tail transfers, segment aliases,
two-page code guards and code changed while a native caller is suspended. All 122
local production-dispatch cases passed with the existing host/native fixtures,
as did both Windows/Linux runtime and source CI matrices. This changes test-only
builds, not the normal player runtime or selected game ranges. VERSION stays 0.0.12;
coverage stays **4.2642% / 95.7358%**. No rebuild, new files or player playthrough
is requested for this qualification chunk. The accepted save/load result below
remains the Windows baseline.

**0.0.12 — Windows save/load slowdown check passed:** 20 additional card-control
and BIOS-call entries now execute natively. The hot card-event polling loop is
compiled; BIOS events, serial timing, card format and synchronous file publication
retain their original paths. Local sampled startup performance improved from
roughly 25–27 FPS to 60 FPS. The user reports no more slowdowns when saving or
loading on Windows. This confirms the reported performance fix on their tested
route; exact FPS and startup-only timing were not separately reported. The BIOS,
serial and persistence paths remain in use.

The production build reports **4.2642% linked native ranges / 95.7358% outside
those ranges** (2,072 new bytes). Those are payload-range measurements, not total
completion or a native CPU-time share. All 40 local source tests passed.

No rebuild or repeat save/load test is needed for this acceptance note. The
previous level-9 gameplay acceptance below remains the 0.0.11 baseline; this
save/load report does not imply a new campaign playthrough, an exhaustive
persistence check or a repeat of every historical host-menu test. Future player
checks will be tied to the behavior changed by the next runtime update.

Local qualification completed fresh setup-card creation/reload and existing-card
load/overwrite with full card images identical to 0.0.11. Five matching-frame
visual checks through first-level gameplay were pixel-identical. The normal
movie/controller/close check and both Windows/Linux CI matrices passed. These
checks complement the Windows save/load report; they do not establish physical
audio quality, every game-progress-save case or later campaign coverage.

Copy the private `.local/runtime-dev/saves` folder before a deliberate write test
with valued saves. No reimport, cache deletion or new user files are needed.
Final local runtime and platform results are recorded in docs/VALIDATION.md.

**0.0.11 Windows build fix:** if compilation finishes but the wrapper reports a
missing `NitrogenSquared-dev.exe.execution.json`, pull and repeat
`python tools/build_runtime.py`. CMake produces `NitrogenSquared-dev.execution.json`
without the executable suffix; the wrapper now reads that name on both platforms.
Keep the existing build/import/save folders. The compiled runtime and native
coverage are unchanged (**4.0193% / 95.9807%**). All 40 local source tests pass,
including both filename layouts; Windows CI now reads the real sidecar as well.
The user subsequently built/tested this version and reached level 9; see acceptance below.

**0.0.11 — Windows gameplay verified through level 9:** 25 additional drawing-packet
entry ranges now execute natively, with guarded internal-block resumes for
computed jumps. Unqualified, changed and unselected code retains fallback. The
linked report is **4.0193% native ranges / 95.9807% outside those ranges**; this
is not overall completion or an execution-time percentage. Original timing,
audio and graphics services are unchanged. This update does not promise a speed
increase, independent gameplay audio or unlocked framerate.

Local qualification passed a controlled first-level route and five matching-frame
pixel comparisons against 0.0.10. All 39 source tests and the 70-file source audit
passed. The final Windows/Linux runtime and source CI jobs also passed.
These local checks complement the user report below; they do not establish
physical audio quality or untested campaign coverage.

The user extended the same build's play session through level 9 and reports no
bugs noticed other than the save slowdown. They previously observed the FPS dip
both while loading save slots and while actually saving. This accepts the tested gameplay route, while leaving card-access
performance open. It does not imply that every historical host-menu check or
later campaign level was retested. No additional campaign progression is needed.

**0.0.9 accepted on Windows:** the user reports no issues, playable gameplay
through level 4, and working saving, including high scores. Earlier checks also
verified native opening playback/skipping, analog input and consistent 60 FPS
gameplay. Testing through level 4 is sufficient for the current native-work
baseline; reaching later levels is not a prerequisite for continuing.

**0.0.10 — first-level gameplay verified by the user:** two gameplay angle-table
lookup routines are generated privately, linked and selected only when their
resident code ranges match. Changed code and unsupported PC segments retain
interpreter fallback. This is a small native-execution milestone, not a promised
speed increase. Native-progress reporting now includes the linked slice and
rejects source/range files changed after the recorded build.
The user reports no issues during first-level gameplay and permits a larger
native conversion group for the next update. This confirms that route, without
implying a later-level or exhaustive repeat of all host-menu/save checks.

**Reported startup observation:** the user noticed a "20 fps slowdown" during
the loading screen after the opening movies and splash, immediately before the
attract/title screen. Performance returns to 60 FPS afterward. The user notes it
may also have occurred in the preceding update. Track this as an unconfirmed
startup performance issue, not an intentional delay or established regression.
Controlled local startup tests reproduced a loading dip with native-dispatch
hooks compiled out as well. Its cause remains unresolved; it is not an intentional
delay. No additional files or immediate repeat test are needed for this report.

**Historical memory-card performance lead (0.0.11):** slot enumeration and saving reproduced the
reported dip on Windows. The user suspects the startup phase reads high scores.
A local preserved 0.0.10 diagnostic baseline confirms card reads throughout its
startup dip and recovery afterward, but also reads before the dip. That is a
correlation, not a confirmed high-score call or root cause. Reads use card data
already held in RAM; save publication performs synchronous file writes. Investigate
guest protocol/driver cost and file-write cost separately. The later 0.0.12 native
card-control batch addresses the measured CPU cost; the user's save/load report
above supersedes this earlier open performance status. No save-format change was made.

This documentation-only acceptance update needs no rebuild or repeat playthrough.
Keep existing saves. Further card-performance checks will be specified with an
actual runtime change; no additional files are requested now.

Each runtime update will replace this update-specific summary with what changed,
the affected checks to run, and their pending/verified status. Unrelated historical
checks below are a reference, not a request to repeat every test on every update.
Newly affected behavior remains pending until tested; previous acceptance does not
automatically qualify a new native implementation.

Do not overwrite a valued save to perform a test; copy the
private `.local/runtime-dev/saves` directory before any deliberate save-write test.

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
Python 3.10 additionally needs `python -m pip install tomli` for the pinned
native-slice generator. Python 3.11+ includes its TOML reader already. The disc
importer remains standard-library-only.

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
The default 0.0.17 ENHANCED build should report **35.4660%** linked and **64.5340%**
outside linked ranges. Its normal clean-shutdown log also prints
`nitrogen: native game slice: dispatches=... residency_rejections=...`.
After first-level gameplay the dispatch count should be positive. This is an
execution check, not a native-instruction percentage or speed measurement.
The count includes internal continuation resumes; card polling can generate
large counts without increasing the reported byte coverage. It is not a count of
original function calls and should not be compared directly with 0.0.10.
Residency rejections select the interpreter and can be normal while different
code occupies the address; they are not failed game calls.

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
