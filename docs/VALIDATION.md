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


## 0.0.9 render worker, telemetry and title ownership

Normal launch requests the pinned framework's OpenGL worker with one closed frame
of lookahead. A launch option retains synchronous rendering for comparison;
software rendering disables the worker. Ordered drawing, copied command payloads,
required readbacks and backpressure remain in the framework. Guest simulation and
SPU sample production keep their timing. This does not implement native sound
cues or unlocked presentation.

The reported title duplication was traced to `present_session_reset`: it clears
the FPS base while leaving the decorated SDL title intact. A narrow getter in
the original host bridge retains the original title by SDL window ID. Menu resume
re-anchors timing without adopting a previous Game/Present suffix. Native movies
retain that base; a new window gets its own title. No pinned framework file is
edited.

The bridge observes the original SPU drain and publishes a mutex-protected host
snapshot. It preserves drain bytes/count and locks the audio bridge while reading
its callback-owned statistics. UI drawing reads that snapshot, not a mutable DSP
or audio device. Queue statistics are sampled on their owning main thread without
a graphics-context handoff. Normal shutdown joins the GL worker before final host
teardown completes and logs the last sampled counters. Underflow is labeled in
samples for the bridge and empty-queue events for the legacy path. Passive panels
stack using their measured heights.

Local qualification used Linux x86-64/GCC 13.3, Mesa llvmpipe, native-resolution
OpenGL, a dummy audio device and separate private saves:

- All 34 synthetic source tests passed; source audit passed with 62 reviewed
  text files and no commercial payloads.
- The native fixture passed exact SPU drain/count, host snapshots, six repetitions
  of the real pause-reset path and a new-window title. Real menu, analog virtual
  gamepad and independent native media smoke checks also passed.
- The pinned render queue passed 8,843 checks for command/payload order, ring
  wrap, frame bounds, context handoffs and shutdown. OpenGL worker-on/off fixtures
  matched readback/native/hires/wide digests at 1x and 4x, including dynamic
  resolution transitions. All 671 existing batching checks also passed.
- Fresh N2O boots used the same frame-scheduled input route with the worker off/on.
  Both skipped all three native movies, reached first-level tutorial gameplay,
  completed six host pause/resume cycles, dispatched F1/F11 and closed normally.
  GPU captures at frames 800, 1500, 2800 and 3600 were pixel-identical.
- At the final worker sample, the bound was 1 and produced/consumed frames both
  read 4,203. About 16.5 million commands had been recorded. The synchronous run
  recorded none, establishing that rendering actually used the worker.
- A sampled loading interval around frames 1200–1500 ran at 59.93 guest FPS both
  ways, with no bridge underflow in that interval. Later cumulative counters
  recorded underflow in both instrumented routes, which enabled full-VRAM history
  and exercised pause/fullscreen. This does not establish starvation-free gameplay.
- A normal build including the worker shutdown hook completed all three native
  movies and closed cleanly in 34.6 seconds. A subsequent extended normal-build
  counter comparison was interrupted by loss of the development environment;
  no result is claimed for that unfinished comparison.

Commercial captures, private routes and generated game inputs remain outside
Git/releases. Linked game-code coverage stays 2.12%; host scheduling and telemetry
do not increase it. Windows worker/menu/audio acceptance remains a player check.

The final CI attempt initially passed native title/menu/input/media checks but
failed two analytic fractional-UV samples in the unchanged, standalone pinned
renderer fixture on Linux. That fixture passed locally and on two preceding
commits; it does not link the title host bridge or frontend. The isolated Linux retry and a fresh full
Windows/Linux run subsequently passed with all original assertions retained.
The cause of the initial failure remains unresolved; it is not hidden by a
changed tolerance or omitted check.

The complete normal runtime and native fixtures passed on Windows and Linux in
[run 40308692238](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40308692238).
Both platforms passed analog input, independent media, and the exact-drain/title
regression checks. Linux also passed both execution profiles, queue lifecycle,
worker pixel equivalence and all 671 batching checks. Source tests and packaging
passed on both platforms in
[run 40308692247](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40308692247).
No binary artifact was uploaded.

## Windows acceptance of 0.0.9 and native-work baseline

The user reports no issues with 0.0.9, describes the game as fully playable in
their testing through level 4, and confirms saving works, including high scores.
This closes the general pending Windows acceptance for the render-worker update.
It is a player report, not an isolated benchmark or proof of every individual
menu/audio counter check. Later campaign levels remain unverified and are not a
prerequisite for continuing native development.

The following documentation update records that acceptance, places both linked
native coverage (2.12%) and its uncovered complement (97.88%) in README.md, and
defines the next native milestones. It changes no runtime code or VERSION and
requires no additional player test. Saving currently validates the guest
compatibility/persistence path; it is not evidence of a native save-system rewrite.

Documentation maintenance instructions are now recorded in root AGENTS.md and
included in the reviewed source allowlist. All six packaging regression tests,
the source audit (63 reviewed text files), and `git diff --check` passed locally.
No runtime code changed, so no runtime rebuild or additional player test was run.

## 0.0.10 — first loaded-game native slice

The update uses the pinned static-overlay emitter and its per-range
CRC/page-generation residency gate for two leaf angle-table readers in N2O.EXE.
Only this 56-byte slice is selected, not the executable's full analysis output.
Each source/range manifest remains private and is hashed in the build receipt.
The selected implementation and preparation/residency contracts participate in
execution identity. REFERENCE retains interpreter execution.

Local qualification used Linux x86-64/GCC 13.3, Mesa llvmpipe at native resolution,
dummy audio, separate private saves and the verified USA disc:

- All 37 source tests passed, including slice-input bounds, source/range changes
  after linking, union coverage without double-counting, reference omission and
  aggregate-only probe filtering. The source audit passed with 70 reviewed text
  files; `git diff --check` passed.
- An isolated private fixture linked the production objects and compared native
  execution against `dirty_ram_run_span` from the real interpreter. All 4,096
  angles, three upper-bit patterns and both routines passed: 24,576 calls with
  equal GPRs, HI/LO and return PC. Warmed per-call guest-cycle deltas matched;
  native work charged 319,515 cycles overall. This is a bounded routine test,
  not a full-session timing-equivalence or speed-improvement claim.
- A changed covered instruction declined, restoring the instruction rematched,
  and the actual NEW.EXE bytes loaded at these same addresses declined both
  N2O.EXE entries. No global active-executable guess was needed for this slice.
- The pinned production static-match stress fixture passed cache saturation,
  eviction and code replacement. A REFERENCE CMake configuration also succeeded
  with the private generated slice directory temporarily absent. Restoring that
  directory and ENHANCED selection reproduced the exact prior profile header.
- A fresh diagnostic boot skipped all three native movies, reached first-level
  tutorial gameplay and closed normally. The static-entry counters recorded
  5,120 calls to the first routine by frame 4,228. The second was qualified in
  the exhaustive fixture but was not observed in this sampled gameplay route.
- A normal build with diagnostics disabled completed all three native openings.
  A private host fixture added an SDL virtual controller and injected real
  controller presses plus F1 twice. The normal runtime recorded 453 native game
  dispatches, zero residency rejections and clean window-close shutdown. The
  fixture changed only test entry/input plumbing; production runtime objects
  were reused. Dummy-device underflow/overflow counters occurred, so this does
  not establish physical audio quality or starvation-free playback.
- The normal build report reproduced 17,964 / 845,824 bytes = 2.1238% linked
  native coverage and 97.8762% outside linked ranges. The denominator is unchanged;
  the increase over 0.0.9 is 56 bytes, not an estimate of overall completion.

The initial Windows/Linux runtime matrix passed in
[run 40433168990](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40433168990).
Both platforms passed the generated original same-address fixture: two programs
share their first four words and differ in the fifth, with 384 successful calls,
tail invalidation, KUSEG/KSEG1 isolation and restore checks. Linux also passed the
REFERENCE profile with no linked loaded-code translations, menu/input/media/title
checks, all 671 batching checks, 8,843 queue checks and worker pixel equivalence
at 1x/4x. All original assertions were retained. Source CI also passed in
[run 40433168984](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40433168984).

Final shutdown-count logging and additional report/filter checks were added after
that matrix; local normal linking/playback and the 37-test suite passed with those
refinements. The fresh final Windows/Linux matrix passed in
[run 40434467307](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40434467307),
retaining all native/input/media/title, reference, renderer and queue assertions
listed above. Source tests and packaging passed on both platforms in
[run 40434467313](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40434467313).
Windows player acceptance of 0.0.10 remains the focused checks in TESTING.md;
0.0.9 through level 4 remains the accepted
player baseline. No commercial payload, capture, generated body or executable was
added to Git or uploaded by CI.

Final review also kept native counter probing on `overlay_loader_status`, which
is supported in both profiles. A separate static-entry query is unavailable in
REFERENCE and was removed from the probe's default command list before promotion.
The revised filtering test retains only aggregate counters, excluding entry/code
data. This Python-only compatibility refinement receives local source tests;
it does not change the runtime objects exercised by the final matrix. All 37
source tests, the 70-file source audit and `git diff --check` passed again locally
after that refinement. The final validation/probe commit skips CI because the
compiled runtime is unchanged and the Python-only adjustment was tested locally.

## 0.0.10 startup-loading observation

The user clarified that the observed "20 fps slowdown" occurs at the loading
screen after the movies and splash, immediately before the attract/title screen.
Performance returns to 60 FPS. They also note the slowdown may have existed in
the preceding update, so this is not yet an established 0.0.10 regression.

Saved diagnostic routes include an approximately 300-frame interval around
frames 1200–1500 at roughly 59 FPS in the baseline and 40 FPS in the candidate,
with zero native-slice calls in the candidate through that sample. These were
instrumented development-host runs using wall-time-held input, not repeated
controlled samples with an explicit marker for the user's loading screen.
They do not isolate dispatch overhead or establish the cause of the Windows
observation. The native routine bodies were not executing during that sampled
interval; dispatch checks and other loading work remain possible contributors.

The screen location and recovery to 60 FPS are recorded in TESTING.md. No runtime
code, timing policy, VERSION or coverage measurement changes with this note.
The source audit and `git diff --check` passed. No new player files or immediate
repeat testing are requested.

## Windows first-level acceptance of 0.0.10

The user reports no issues during first-level gameplay in 0.0.10 and authorizes
a substantially larger native conversion group next. This accepts the tested
first-level route. Later-level testing and an exhaustive repeat of every host
menu/save check are not inferred. The startup-loading observation above remains
unconfirmed, with recovery to 60 FPS.

## 0.0.11 — expanded native packet preparation

The integration-only checkpoint passed Windows/Linux runtime CI in
[run 40441495690](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40441495690)
and source CI in
[run 40441495682](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40441495682).
Original synthetic programs cover RAM-writing loops, unsigned wrap, GTE saturation
and computed internal transfers. A resume fixture clears the incoming CPU PC and
checks that the alias resumes instead of restarting; modifying its owner's code
invalidates that alias. Source tests reject missing/unguarded continuation owners.

The selected production binding adds 25 packet-building entry ranges to the two
lookup entries. It contains only declarative addresses, lengths and descriptions
in the existing reviewed schema. Generated translations, instruction guards,
private capture/replay sources, candidate inventories and witness files remain
outside Git/releases. One additional candidate produced mismatching exception
behavior in adapted contexts and is excluded entirely, including its passing cases.

Local qualification uses the same Linux/GCC/Mesa/dummy-audio environment as
0.0.10, a verified local disc and isolated saves:

- All 25 complete live calls across four packet-entry groups matched GPRs, HI/LO,
  PC, COP0, GTE data/control, all 2 MiB main RAM and the 1 KiB scratchpad. Capturing
  scratchpad and driving internal native resumptions were required for a valid
  comparison; incomplete earlier fixtures are not counted as product failures.
- Adapted captured contexts and sixteen geometry-state edge variations produced
  2,856 successful comparisons across the 25 selected entries. This is bounded
  input coverage, not proof of all possible inputs or observed live execution of
  all 25 roots. Non-RAM/non-scratch device accesses are rejected by this fixture.
  Isolated device time is frozen; full-session timing equivalence is not inferred.
- The actual candidate built and linked 27 N2O root entries plus 397 guarded
  continuation aliases. Aliases use the complete owning root's residency ranges;
  range manifests award no extra bytes/functions for them. The verified report is
  33,996 / 845,824 bytes = **4.0193%** linked, **95.9807%** outside linked ranges.
- A controlled diagnostic route skipped all native openings, followed identical
  frame-scheduled input through menus/first-level tutorial, reached frame 4,500
  and closed normally. By frame 4,359 it recorded 23,262 native dispatches across
  eight entry PCs, including internal resumes. These are not original function
  call counts or execution-weighted native percentages. Late sampled intervals
  ran at 59.94 guest FPS on this host. Physical audio/controller quality still
  needs the Windows player check.
- Controlled loading samples around frames 1,200–1,350 measured 28.19 FPS for the
  old native build, 29.47 with a no-op dispatcher, 28.42 with interpreter dispatch
  consultation compiled out, and 28.48 for this candidate. Native calls were zero
  during the interval. These single local samples reproduce the dip without the
  hooks, but do not establish its cause or explain Windows performance. All routes
  recovered afterward. No speculative guest-clock/CD-timing change was made.
- All 39 source tests passed locally with CMake available; the source audit passed
  with 70 reviewed text files. No tests were skipped in that final local suite.

A separate visual comparison enabled full-VRAM frame history and repeated the
same frame-scheduled input route once per build. The baseline and candidate
scanout images at guest frames 800, 1,500, 2,200, 3,000 and 4,000 were pixel-identical,
including first-level enemies/HUD. These history-enabled runs are not performance
samples and do not establish parity for unsampled frames or later levels.

The normal build with diagnostics disabled also completed successfully and
reproduced the coverage report. A private host fixture reused its production
objects, attached an SDL virtual controller, let all three opening clips finish,
injected gamepad input and F1 hide/restore, then closed via SDL_QUIT. It exited
successfully, recording 952 native dispatches and zero residency rejections.
Dummy-device audio underflows/overflows were recorded; this is not a physical
audio-quality or starvation-free claim. No TCP diagnostic server was used.

The final Windows/Linux runtime matrix passed in
[run 40444614554](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40444614554).
Both platforms passed the original native slice, input, media and title checks.
Linux additionally passed menu composition, the reference profile, renderer
batching, queue and worker-equivalence checks. Source tests and packaging passed on both platforms in
[run 40444614449](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40444614449).
No binary artifact was uploaded. A final documentation-only validation commit
records these results without changing the tested runtime code. Windows 0.0.11 player acceptance
is pending the focused first-level checks in TESTING.md; the user's successful
0.0.10 first-level route remains the previous accepted result.


## 0.0.11 Windows build-receipt correction

The user's Visual Studio build linked successfully, then failed while reading
`NitrogenSquared-dev.exe.execution.json`. The pinned framework's post-build copy
uses `TARGET_FILE_BASE_NAME`, producing `NitrogenSquared-dev.execution.json`.
Appending the suffix to the entire executable path worked on Linux but was wrong
on Windows. The common manifest reader now replaces the executable suffix and is
used by both the private build wrapper and CI. Missing metadata still fails; no
profile or native coverage is guessed from a filename or build option.

All 40 local source tests passed, with no skips. The new regression covers
Visual Studio Release/.exe and single-config layouts, both execution profiles,
a misleading stale .exe.execution.json file and missing-sidecar failure. The
same reader successfully loaded the existing complete normal runtime's ENHANCED
manifest. The 70-file source-package audit and diff whitespace check passed.

CI previously read profile manifests only inside its Linux-only reference check,
so a successful Windows compile did not exercise the failing lookup. Both hosts
now read the normal runtime and input fixture manifests. The expanded Windows/Linux runtime matrix passed in
[run 40447137969](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40447137969),
and both source jobs passed in
[run 40447137991](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40447137991). No compiled runtime code,
framework source or game binding changed; VERSION stays 0.0.11-development and
coverage stays 4.0193% linked / 95.9807% outside linked ranges. No additional local
runtime rebuild or play test was needed for this Python metadata correction.
The user's existing Windows build can be reused by rerunning the normal build
command; import and saves remain in place.


## Windows 0.0.11 acceptance and card-access performance lead

The user reports reaching level 4 again in the corrected 0.0.11 build, with no
other gameplay issues. They observed the FPS dip while loading the save-slot
list and again during saving. They suspect startup high-score loading explains
the earlier opening-to-title dip. Record that caller identity as a hypothesis;
this report does not independently verify a specific high-score read or imply
an exhaustive repeat of all host-menu/save checks.

A bounded local diagnostic run used the preserved 0.0.10 executable, which has
the same card implementation, an isolated newly formatted card and the existing
frame-scheduled route. Full-VRAM history stayed off. Samples every roughly 30
guest frames showed successful card reads from about frame 1,026 to 1,361. The
1,179–1,329 intervals measured 24.47–29.78 guest FPS while reads continued; after
the sequence ended, subsequent intervals returned to roughly 60 FPS. Earlier
read intervals also ran at 60 FPS. There were 149 closed card transactions and no
reported card aborts. The run reached frame 1,900 and closed normally. These are
instrumented Linux-host observations, not a Windows benchmark or proof of the
root cause; the blank-card run cannot identify saved high-score processing.

Source inspection shows sector reads copy from the already resident card buffer.
Each successful sector write reaches synchronous whole-card publication, including
flush/durability operations. This gives two distinct costs to profile: interpreted
guest protocol/interrupt work and host persistence latency. No runtime or save
behavior has been changed on the strength of correlation alone. All private
traces, card data, screenshots and test scripts remain outside Git/releases.

This update records acceptance and the investigation only. VERSION remains
0.0.11-development; linked coverage remains 4.0193%, with 95.9807% outside linked
ranges. No runtime rebuild or new player test is required by these documentation
changes. The source-package audit and whitespace check are the relevant checks.


## Extended Windows acceptance — 0.0.11 through level 9

The user extended the same build's play session through level 9 and reports no
bugs noticed other than the save slowdown. This supersedes level 4 as the furthest
reported 0.0.11 gameplay coverage. It does not establish coverage beyond level 9
or independently verify every historical host-menu check. Card-access performance
remains open; no additional progression, save files or repeat playthrough is
requested for this documentation update.

Runtime code and VERSION are unchanged. Linked native coverage remains 4.0193%,
with 95.9807% outside linked ranges; longer playtesting does not increase that
metric. The source-package audit and whitespace check passed. No runtime rebuild
or new gameplay test was needed.


## Card-control conversion — qualification checkpoint

A next candidate selects a coherent group of card-control routines and BIOS-call
trampolines. In a preserved 0.0.10 diagnostic baseline, the sampled startup dip
was predominantly interpreted work (88.47% wall samples in a two-second window),
including a game loop repeatedly polling four BIOS events. Graphics processing
accounted for negligible samples in that window. The same frame-scheduled route
measured 26.52 FPS, then 25.52 FPS with the current 0.0.11 diagnostic baseline;
the private experimental card candidate measured 60.00 FPS in its corresponding
interval. All three interval samples completed 73 card reads and their startup
routes closed 149 card transactions. These are local diagnostic observations,
not Windows performance or physical-audio measurements.

A private live-boundary fixture matched 125 comparisons at 54 observed entry/
continuation PCs during startup. It compares CPU architectural registers, main
RAM, scratchpad and GTE state up to the next outgoing call/return, with device
time frozen during comparison. It restores the live state and runs the selected
code normally afterward. It does not replay device I/O twice. Unobserved entries
and full save/load sequences remain to be qualified. No private fixture source,
instruction bytes, snapshots or captures are included in this checkpoint.

The original synthetic CI programs now include a separately compiled caller and
callee, with zero/1/2/7/64 iterations, branch-delay accounting and saved SP/RA.
The complete native fixture passed locally using the actual pinned emitter and
production runtime objects. This checkpoint adds tests/documentation only;
shipping VERSION, bindings and the 4.0193% coverage report remain unchanged.
Remote CI is deferred to the complete candidate commit; no player rebuild is
requested for this intermediate work branch.


## 0.0.12 — card-control production selection

The existing declarative native binding now selects 20 additional entries:
12 card-control/event-polling routines and eight BIOS-call trampolines, totaling
2,072 bytes. All bodies and full-range guards are generated privately from the
verified user input. No instructions, private test sources, card data or compiled
game modules are added to Git. Interpreter fallback and REFERENCE remain intact.

The private live-boundary checker matched 218 comparisons at 57 entry/continuation
PCs across startup, empty-card error paths and a manually confirmed setup save.
That disposable card showed an allocated save block, the game displayed its
successful-save result, and publication reported flush_result=0 with no dirty
buffer remaining. A complete automated save/reload comparison, final production
coverage report, normal-build checks and Windows/Linux matrix remain pending.
The selected routines retain BIOS event calls and guest timing; the serial device
and synchronous whole-card publication remain unchanged. Windows player
acceptance is pending, separately from the accepted 0.0.11 level-9 route.


The complete production diagnostic candidate built successfully. Its verified
native report is 36,068 / 845,824 = 4.2642%, with 95.7358% outside linked ranges;
N2O has 47 root entries and 531 continuation aliases. All 40 source tests passed
locally with no skips, and the source audit still contains 70 reviewed text files.
The original cross-slice native fixture passed locally as well. Both remote source
jobs passed in
[run 40453311216](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40453311216).
Final save/reload, normal-runtime and platform checks are still pending. Automated
menu routes that failed to reach a save confirmation are excluded from save and
card-image equivalence evidence; only the confirmed manual write above is counted
at this intermediate checkpoint.


The final candidate code passed the complete Windows/Linux runtime matrix in
[run 40453311167](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/40453311167).
Both hosts passed the new original cross-slice call fixture and retained the
existing native/input/media/title checks. Linux additionally passed the menu,
reference-profile, renderer and worker checks. Neither workflow uploads a game
binary or commercial input. The later coverage/checkpoint changes are documents
only and do not change that tested code.

A manual cross-version setup-card test succeeded in both directions: 0.0.11
loaded a candidate-created disposable card, then wrote it again; the production
candidate loaded that baseline-written card and rewrote it. Both games displayed
successful read/save results with flush_result=0 and no remaining dirty buffer.
The resulting complete 128 KiB images were byte-identical. A separate fresh-card
0.0.11 run reproduced the earlier candidate's first-create image exactly. First
creation and later overwrite differ in the baseline too; this observation is not
a claim that every setup-file initialization detail is understood or fixed.
A production fresh-card repeat and normal-build verification are still pending.


The corrected frame-scheduled fresh-card route subsequently reached the actual
setup-save confirmation, completed the write and confirmed a reload in both the
preserved 0.0.11 baseline and the production 0.0.12 candidate. Both complete
128 KiB card images matched byte for byte, with an allocated save block and clean
publication status. The first-create result matches the earlier manual candidate
image too. Thus both fresh creation and existing-card overwrite reproduce the
baseline in these tested setup-card cases. This does not claim full campaign-save,
physical-device or every error-path coverage. Windows checks should include the
player's existing game-progress saves and high scores using backed-up cards.
The preceding invalid navigation routes are not included in this evidence.

The normal build with diagnostics disabled and a short first-level comparison
remain the final local checks before promotion.


The production fresh-card repeat completed and matched the baseline's entire
128 KiB image byte for byte after save and reload. Both fresh creation and
existing-card overwrite are now covered by successful UI outcomes and card-image
comparisons, using disposable cards only. The focused frame-scheduled setup-card
route produced the following approximate diagnostic guest-speed samples. Bounds
use the nearest approximately 30-frame sample, so these are not exact per-call
latencies or Windows benchmarks.

| Sample window (guest frames) | 0.0.11 baseline FPS | 0.0.12 candidate FPS |
| --- | ---: | ---: |
| Startup card read (1180–1330) | 27.01 | 59.94 |
| Setup-save card check (3180–3540) | 46.70 | 59.89 |
| Setup save/write (3600–4200) | 52.26 | 59.90 |
| Setup-load card check (4380–4740) | 48.22 | 59.95 |
| Confirmed setup read (4800–5160) | 47.22 | 59.94 |

Synchronous file publication still runs on the emulation thread. These local
results do not establish starvation-free audio, device-independent write latency,
full game-progress-save coverage or every card error path. The normal build and
short first-level comparison remain pending at this checkpoint.


The full normal build with diagnostics disabled completed and reproduced the
4.2642% report. A private SDL host fixture reused the production objects, let all
three native opening movies finish, supplied virtual-controller input, exercised
F1 hide/restore and closed through SDL_QUIT. It returned successfully, recording
1,340,425 native dispatches and zero residency rejections. The final dummy-device
snapshot reported zero underflow samples and 44,726 overflow frames. This is one
local transport check, not proof of physical audio quality or starvation-free
playback. The bounded render worker remained active with one frame in flight.
A final diagnostic first-level visual comparison is still pending.


Final visual qualification repeated the existing frame-scheduled opening/menu/
first-level route with full-VRAM history enabled, separately for the preserved
0.0.11 and production 0.0.12 diagnostic executables. Scanout images at guest
frames 800, 1,500, 2,200, 3,000 and 4,000 were pixel-identical, including first-level
enemies and HUD. Both routes reached frame 4,500 and exited successfully. These
history-enabled runs are visual checks, not performance samples or later-campaign
qualification. The normal build, real-disc route, cross-version setup-card tests,
original synthetic native fixtures and complete Windows/Linux matrix are now
complete. No pinned framework source was changed.

The final documentation-only commit records these completed checks and skips a
redundant CI run; compiled candidate code is the code tested in run 40453311167.
The 70-file source-package audit and whitespace check passed after the final
reporting changes. Windows 0.0.12 player acceptance remains pending the focused
card-read/write and short first-level checks in TESTING.md. Existing 0.0.11
acceptance through level 9 remains history; neither full game-progress-save
coverage nor a physical Windows audio/performance result is inferred from these
local setup-card tests.
