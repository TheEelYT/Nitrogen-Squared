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
