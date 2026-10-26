# Initial validation — 2026-10-25

Development host: Linux x86-64, GCC 13.3, Python 3.12.14, CMake 4.4.4.
Target priority remains Windows x64, then Vita ARM.

Validated against the supplied USA image:

- Complete merged BIN/CUE and eleven-track layout verified.
- Read-only ISO traversal and boot identity checked.
- All three selected executable hashes and PS-X EXE headers checked.
- Local preparation completed; the commercial disc remains outside the repository.
- Pinned PSXRecomp analysis/emitter tool built with CHD support disabled.
- Separate OpenBIOS-profile, entry-reachable translations emitted for the three
  executables. No generated C or native object is included in the repository.
- All seven resulting C translation units compiled to x86-64 objects with GCC
  (`-std=c11 -O1`). This validates compilation of that limited analysis output;
  the objects have not been linked into a runtime or execution-verified.
- All 15 synthetic tests passed locally; source packaging audit passed.

This does not validate boot, title screen, gameplay, rendering, audio, saving,
Windows execution, a packaged setup application, or Vita execution. The Tk first-run
UI has not been visually exercised on Windows. The command-line importer has been
exercised on the supplied disc.

Automated tests exercise synthetic disc import, changed audio, missing tracks,
path rejection, invalid extents/headers, failure cleanup, preservation of existing
data, and packaging rejection of unexpected or renamed game content. CI repeats
these on Windows and Linux without any commercial files.

## 0.0.2 runtime update

The user supplied a Windows screenshot showing the expected prepared import
directories and manifest. The private runtime now builds and executes on the
development host. Opening videos, title/attract sequence, ship selection, level
selection, tutorial screens and first-level gameplay were visually inspected from live software scanout.
Scripted digital input advances menus. Window/audio-device and Windows execution
validation are still pending. See [runtime findings](RUNTIME_BRINGUP.md) and
[Windows testing](../TESTING.md).

The suite now has 18 tests, adding checks for revalidation of a changed disc,
modified extracted executable, and compiler output discovery across build layouts.

## 0.0.3 Windows configuration fix

Reproduced the reported `psx_game_version.txt` conflict with Ninja Multi-Config.
The pinned framework defaults to a configuration-dependent game version and
generates a shared build-root stamp, which cannot have different content for each
configuration. The project now explicitly sets its VERSION value for every
configuration and refreshes the cache on reconfigure.

The added regression configures the actual project wrapper against an original
synthetic runtime contract, checks Debug/Release/root stamps, changes VERSION in
the same build cache, and builds the synthetic Release target. Linux uses Ninja
Multi-Config; Windows CI uses its installed Visual Studio generator. No game or
BIOS files are used by the test. There are now 19 automated tests.

The user's cross-function-target warnings also occur in the recorded successful
OpenBIOS generation and gameplay bring-up. This fix addresses the fatal CMake
collision; it does not hide those emitter diagnostics or establish every BIOS path.

The actual pinned framework runtime also configured successfully with Ninja
Multi-Config after the fix. Its root, Debug and Release version stamps all contain
`0.0.3-development`.

## 0.0.4 MSVC runtime compile

The user reached native runtime compilation and reported C2131 in the session
lambda's `static_assert`. The runtime target now enables `/Zc:lambda` for MSVC
C++ compilation, retaining the existing language mix and assertion. The first
full Windows compile confirmed that C2131 was resolved, then exposed C1189 from
the runtime's existing C atomics. C compilation now also enables
`/experimental:c11atomics`. Microsoft
documents this mode for standard-conforming C++17 lambda handling:
https://learn.microsoft.com/en-us/cpp/build/reference/zc-lambda

The next full compile exposed two unguarded GNU-style atomic calls in the OpenGL
renderer. An original, MSVC-only forced-include header adapts those 32-bit int
loads/stores to Interlocked intrinsics with full memory barriers. The pinned
framework checkout remains unchanged. The adapter is deliberately limited to
these calls; GCC and Clang keep their own builtins.

The small configuration fixture now compiles and executes an original C++17
constexpr-lambda example, a C11 atomic operation, and the GNU-style flag
loads/stores (including negative values and integer bounds). A separate Windows
workflow compiles and links the complete pinned
runtime with an original two-instruction synthetic PS-X program and OpenBIOS.
It uses no game disc, assets, music, or commercial executable and uploads no
binaries. This expands compiler coverage; it does not validate N2O gameplay.

The complete Windows runtime compiled and linked successfully in
[run 40239430944](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40239430944).
The user subsequently confirmed Windows boot and reported low speed, audio
stutter, title-screen corruption and an unresponsive Xbox controller.

## 0.0.5 playback corrections

The wrapper previously forced `PSX_DEBUG_TOOLS=ON`. Besides enabling continuous
full-VRAM capture, that keeps per-instruction tracing and disables the pinned
framework's production RAM-load/cycle fast paths. Normal builds now omit that
instrumentation; `--diagnostics` retains it in a separate private build when
needed. Normal launch disables display history and offers `--show-fps` for the
lightweight guest-speed readout. Native internal resolution is explicit so
removing the debug toggles cannot silently select the framework's HD defaults.

A private trace identified N2O's 640x480 title upload at frame 833 while GP1 still
selected 24-bit movie output; GP1 changed to 15-bit at frame 834. The GL movie-upload
heuristic skips that transfer. The project's GP1 adapter republishes the
CPU-authoritative VRAM once at a 24-to-15-bit transition. It neither changes the
guest image nor crops the output. The adapter test checks ordering, repeated
mode writes, unrelated commands, and non-GL backends.

The generated game configuration now requests `p1_device = "auto"` explicitly;
the framework's existing keyboard source remains available. A native smoke-test
entry point uses an original SDL virtual gamepad with the real runtime routing
and mapping functions, including face buttons, Start/Select, D-pad, digital stick
movement and unplug handling. It never executes a guest program. Windows
physical-controller behavior and real audio-device playback still need user
verification.

The status probe now filters nested audio/pad counters and can measure guest
frame progress over a bounded interval. Its tests reject commands outside the
allowlist and omit unrequested response fields. No private game images, generated
C, captures, snapshots, or linked binaries are part of this update.

The 27 source tests passed locally and in Windows/Linux CI. The full Windows
runtime compiled and linked, and its virtual-gamepad smoke process exited
successfully in [run 40248055918](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40248055918).
The Linux smoke test also printed its success receipt for auto routing, ten
buttons, digital stick movement, unplug and keyboard-source availability.
Composed OpenGL frame captures showed the complete title after the GP1 adapter,
including the right-hand logo and copyright text.

Private fresh-boot comparisons used Linux x86-64, GCC 13.3 and Mesa llvmpipe
OpenGL at native internal resolution, with a dummy audio device. Both builds
disabled display history and used the same disc/configuration and no input.
In the animated attract background at guest frames 4500–4800, 300 frames took
6.069 seconds with tracing and 5.061 seconds without it: **49.4 to 59.3 guest
FPS**. Guest work fell from 5.244 to 4.238 seconds. An earlier 300-frame window
at 3000–3300 was already paced near 60 FPS in both builds, but guest work fell
from 3.342 to 2.407 seconds (about 28%). These are local timing results, not a
Windows hardware/audio acceptance result or a native-code coverage percentage.

## 0.0.6 main-menu batching and analog input — 2026-10-26

The user reports opening videos at roughly 55–60 FPS, functional Xbox input,
and smooth 60 FPS gameplay after the entering-game text disappears. The actual
swirling main menu remains slow (the supplied screenshot shows 26 guest FPS),
level entry runs around 40–48 FPS, and the game identifies the pad as digital.
The 0.0.5 attract-sequence benchmark above did not exercise this main menu.

A new private main-menu trace measured 3,218 primitives and about 2,837 OpenGL
batches per frame. Graphics accounted for roughly 71% of instrumented wall time.
The pinned renderer already provides an ordered dual-source batching implementation;
this update selects it through an original implementation-family wrapper instead
of modifying the pinned checkout. Mask-check and subtractive operations retain
the reference path. `REFERENCE` and `ENHANCED` builds record distinct execution
identities, and switching profiles refreshes the existing cache.

With otherwise identical native-resolution, diagnostic builds on Linux/Mesa
llvmpipe, batches fell to 218 per frame. Average CPU textured-flush time fell
from 37.724 to 6.983 ms, and average total frame time from 56.867 to 26.319 ms.
These are instrumented development-host samples at different animation frames,
not a Windows performance guarantee. Fresh boots with the same frame-scheduled
Cross input also captured guest frame 4200: both 364x238 main-menu images were
pixel-identical (zero changed pixels). Commercial images and captures remain private.

The upstream original renderer fixture passed 331 checks at native resolution
and 340 at 4x, comparing LLE/HLE output for overlapping blend modes, masking,
texturing, filtering and feedback. Linux CI repeats these checks without game
data and compiles/runs both execution profiles. The 27 synthetic source tests
also passed locally and in Windows/Linux CI; the source package contains 37
reviewed text files.

The previous generated configuration explicitly selected a digital controller.
The default is now analog DualShock, with `--controller-mode digital` as an
explicit comparison option. The runtime's virtual-gamepad smoke test now checks
the guest-facing DualShock identity and analog-axis sample, including that moving
the stick does not also press the digital Right button. The complete runtime
compiled and linked on Windows and Linux in
[run 40251120659](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40251120659).
Both platforms printed the analog smoke-test success receipt; Linux also passed
the test in the reference profile. Physical Xbox behavior, real audio playback,
and the level-entry frame rate still need Windows acceptance testing.

A private fresh boot with injected DualShock protocol input also advanced through
the main menu and level selection into the first level and tutorial prompts.
The pad status reported connected analog type 1. The entry logo/transition still
adds rendering work on the instrumented llvmpipe host; this check establishes
progress with the enhanced renderer and analog protocol, not sustained 60 FPS
during that transition or physical-controller acceptance.

## 0.0.7 desktop menu and coverage reporting

The user verified 0.0.6: analog input works, gameplay is consistently 60 FPS,
and only the intro cutscenes retain small drops of about 2–3 FPS. This replaces
the earlier pending Windows acceptance for menu/gameplay speed and analog input.

The new frontend implements the framework's existing menu-provider contract.
Dear ImGui and its SDL3/OpenGL backends are pinned and fetched privately. A
build-local copy of the pinned presenter changes only the letterbox helper to
reserve the persistent menu strip. The source checkout stays clean; framebuffer
dimensions and aspect ratio remain intact. Autohide uses a transient overlay.
Settings/dropdowns use the host's existing pause and input-capture policy.
Fullscreen and restart/quit requests use the host interface; volume changes are
posted to the main event thread. No Mods tab or unimplemented media controls are
shown. The software renderer retains its diagnostic role without this frontend.

The native SDL/OpenGL smoke test renders an original colored canvas and the real
menu, checks pixels above/below the strip, verifies the 4:3 inset, opens System by
mouse, tests F1/F11, captures gamepad input in Settings, preserves Quit events,
checks Escape/resume, and detaches/reattaches the provider. The development-host
test passed. An actual N2O fresh boot also logged the attached desktop provider
and reached guest frame 4800. The menu-enabled normal build ran frames 4500–4800
of the attract sequence in 5.120 seconds (58.6 FPS) on Mesa llvmpipe with dummy
audio. This is not a main-menu benchmark or physical Windows audio/UI acceptance.

All 30 synthetic source tests passed locally and on Windows/Linux CI. The public
source package audit passed with 44 reviewed text files and no game payloads.
The new native-progress command reproduced 17,908 linked native range bytes over
845,824 original executable payload bytes: 2.1172%. See
[the metric definition](NATIVE_PROGRESS.md); it does not count host code, BIOS or
analysis-only translations and is not an overall completion estimate.

Native music, effects and movies are not enabled in this update. Disc inspection
identified standard STR video packets and interleaved XA audio in all five movie
extents, including files named .SXA. That is a concrete starting point for a
native synchronized cutscene player; skip/stop/return-to-game behavior still needs
title-specific qualification.

The complete runtime compiled and linked on Windows and Linux in
[run 40256098996](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40256098996).
Windows passed the real virtual-gamepad test. Linux passed both the real menu
and input tests in ENHANCED and REFERENCE builds, plus all 671 renderer
equivalence checks. Physical Windows menu, fullscreen, reset and real audio
behavior remain the player checks listed in TESTING.md.

## 0.0.8 native opening movies

The user verified the 0.0.7 menu and keybinds on Windows. The new native service
replaces the guarded inner movie loop at NEW.EXE 0x80022350–0x80022688 while
retaining its original setup/teardown caller. The verified import generates the
instruction guard, full-body hash and ISO extents into a private build header.
Supported native routes are FOX, N2O and CRYSTAL, in the original opening order.
Other overlay identities, netplay, software display, the ending and separate STR
route retain original playback. No commercial instructions, media, decoded
caches or linked executables are included in the source package.

A bounded STR assembler handles v2/v3 bitstreams, padding-only tail chunks and
noncontinuous frame IDs. Sector position provides timestamps at this title's
2x CD cadence. An isolated framework MDEC DSP decodes on a video worker with a
three-frame queue. XA is decoded before playback into immutable stereo PCM.
An independent SDL callback consumes it; the audio timeline schedules video.
Late presentation can drop video frames without starving the audio producer.
Guest clocks remain frozen during native playback. Live guest snapshots during
a native clip are unsupported.

Private qualification on Linux/Mesa llvmpipe with a dummy audio device:

- Fresh boots completed all three native openings, displayed the complete title,
  and reached menus and first-level tutorial gameplay. The normal build repeated
  all three openings and closed cleanly in a 34.59-second test session.
- A main-thread service fixture opened Settings during playback, verified stable
  audio sample count and media time while paused, injected a skip key while the
  menu captured input, then resumed and successfully skipped the clip. Fullscreen
  shortcuts were dispatched through the actual menu provider. Another session
  closed during native playback and exited normally.
- All four SXA extents decoded completely, including the ending codec input
  whose game-call route is deliberately not enabled. Mean decode time was
  0.85–0.99 ms per frame on this development host. This is not a Vita benchmark.
- FOX stereo PCM matched FFmpeg sample for sample after accounting for 756 initial
  silence frames retained by native sector timing. A selected RGB frame differed
  by 0.205 levels on average, maximum 5, across 8-bit channels. FFmpeg was an
  independent test oracle only; it is not a runtime dependency.
- The native media smoke test passed STR v2/v3, isolated guest DSP state, stereo
  XA, malformed/truncated data, transport bounds and padding chunks. Audio advanced
  during a deliberate main-thread/rendering stall, then paused/resumed without a
  time jump. Real menu and virtual-controller smoke tests also passed locally.
- All 32 synthetic source tests passed, and the source package audit passed with
  60 reviewed text files and no game payloads.

The title display writes its vertical range after selecting its mode. The GP1
adapter waits for the 640-wide, high-line title configuration after native movie
completion, then republishes CPU VRAM once. Composed OpenGL captures show the
complete title, both publisher logos and copyright below the desktop bar. The
synthetic GPU fixture covers the later range write and repeated mode writes.

Private service fixtures, commercial captures and decoded comparison inputs
remain outside the repository. Windows physical-device audio synchronization,
volume, skipping and fullscreen during native clips remain player acceptance
checks. Gameplay audio retains its guest SPU/CD timing. Linked AOT coverage stays
2.12%; the three native opening routes are reported separately from that metric.

The complete normal runtime compiled and linked on Windows and Linux in
[run 40293176452](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40293176452).
Both platforms passed the real analog virtual-controller and independent native
media smoke tests. Linux additionally passed the menu/input tests in ENHANCED
and REFERENCE profiles and all 671 OpenGL renderer equivalence checks. The
execution identity includes the native movie implementation, its private binding
when selected, codec/host bridge inputs and build recipe. Source checks also
passed on Windows and Linux in
[run 40293176502](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40293176502).
These workflows use only original synthetic inputs and upload no binaries.


## Windows acceptance of 0.0.8

The user verified native opening movies with no noticeable playback issues,
working movie skipping, analog input, and continued consistent 60 FPS gameplay.
This closes the pending Windows playback/skip and core input/speed checks for
0.0.8. A subsequently reported title-bar issue repeats the FPS suffix after
opening System and resuming; it is covered by the next update's title ownership
fix and repeated-pause regression test.
