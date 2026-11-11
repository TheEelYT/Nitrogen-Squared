# Apply the 0.2.2 CMake icon-forwarding correction

Complete source based on dev bcd506ff0f9a7065835b693a9e9b29effc9e97d8.
Version remains 0.2.2. Includes every prior setup, icon extraction and resource
check change. Nothing was pushed, promoted, tagged or published by the assistant.

Source checks passed for bcd506f. Both runtime jobs and both package jobs compiled
and linked, but the framework selected its default controller icon. The unchanged
staged-PNG identity assertion correctly stopped qualification. No qualified
Windows/Linux test candidate is available from that run.

Root cause: APP_ICON was after GEN_FULL_GLOB, a multi-value argument parsed by the
high-level psxrecomp_add_game_runtime helper. That parser does not recognize
APP_ICON itself and consumed the keyword/path as glob entries, so the lower
runtime target never received it. This revision moves the icon argument before
the list. The regression now models both CMake parser layers instead of bypassing
the high-level one. The old caller fails; the corrected caller passes. No image
format, decoder, private icon data or verification criterion changed.

Local checks: all 158 Python tests pass with no skips. A separate harness uses
the actual unmodified pinned high-level function with an instrumented lower
target: the prior caller reproduces the missing argument, and the corrected caller
builds and stages the exact requested private PNG. This is not a full Windows
runtime build; Windows PE resource verification and all platform CI remain pending.
The source audit passes. No commercial icon bytes are in this ZIP.

Compiled-game input fingerprint:
0df3326a448c5a4eb6970ae138908d2767e5a86a195798c5c22d8b537a0eb835.
Native selection/coverage stay 38.4156% linked / 61.5844% outside; clocks unchanged.
Keep .local, saves, settings and existing preparation data. The icon build update
is still needed; subsequent compatible launches reuse that built game.

With your source checkout on dev, copy all of this ZIP's Nitrogen-Squared contents
into B:\Nitrogen-Squared-dev, preserving .git and .local. No tracked deletions.
This is a complete SOURCE snapshot, not a compiled Windows artifact.

```powershell
git switch dev
git add -A
git diff --cached --stat
git diff --cached --check
git status --short
git commit -m "Fix private game icon forwarding through CMake helper"
git push origin dev
```

Expect eight changed files over bcd506f. Do not push main or create a release.
Wait for all three workflows to pass on the new commit, install the complete new
Windows artifact while retaining .local, and let its icon build update finish.
Then verify the yellow N on the game EXE and running game, and a second Play with
no recompilation. The same staged-PNG and Windows PE resource checks stay enabled.
TESTING.md keeps n0202 and its submitted result bytes unchanged. The owner still
performs every push and decides release clearance after testing.
