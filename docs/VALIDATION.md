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
