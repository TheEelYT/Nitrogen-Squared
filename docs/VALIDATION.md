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

The small configuration fixture now compiles an original C++17 constexpr-lambda
example and a C11 atomic operation. A separate Windows workflow compiles and links the complete pinned
runtime with an original two-instruction synthetic PS-X program and OpenBIOS.
It uses no game disc, assets, music, or commercial executable and uploads no
binaries. This expands compiler coverage; it does not validate N2O gameplay.
