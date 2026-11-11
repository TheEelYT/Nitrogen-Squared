# Apply the 0.2.2 build-progress and timestamp-loop update

Complete source based on dev 1409f36bbac2cfccc9b1399da2a83b412ff5edfd.
Version remains unreleased 0.2.2. Includes the prior setup, origin repair,
private disc-icon extraction and CMake icon-forwarding fixes. No remote write,
main promotion, release branch, tag or publication was performed.

The owner's new Ninja explain trace identifies the repeated configuration input:
app/CMakeLists.txt remains newer than every newly generated build.ninja. The
separate VerifyGlobs check reported no changed lists. This timestamp ordering
causes Ninja to regenerate repeatedly before compiler work. A local original
CMake/Ninja fixture reproduces the loop, stops after three regenerations, then
completes in the SAME build directory after future input timestamp repair.
ZIP dates have no timezone and are a plausible source of the future dates; the
trace does not independently establish which extractor/clock created them.

This update:
- repairs only future mtimes on reviewed source build inputs and VERSION before
  configuration, preserving their bytes and private/user files;
- writes timezone-safe fixed dates in source/Windows/Linux ZIP entries, keeping
  file permissions, and stops repeated regeneration with child-tree cleanup;
- uses floor(80% of available logical threads), minimum one, for desktop tool
  and game builds; respects a smaller CMAKE_BUILD_PARALLEL_LEVEL override;
- retains the future Vita two-job ceiling and controlled two-job CI builds;
- runs build Python unbuffered and reports distinct configuration, generation,
  asset preparation, tool build, game build and final verification stages;
- shows current build action/counter, worker summary and live elapsed time on
  Home, including after navigation. Unknown totals remain indeterminate.

Validation: all 166 Python tests pass without skips, including real Ninja
reproduction/repair, job-budget/affinity/override checks, archive timestamp and
permission checks, stage/elapsed service state, isolated copied updaters and
existing startup/Stop regressions. Frontend unit tests and production build pass.
The seven browser interaction tests could not start Chromium here: its process
singleton socket is denied by this workspace. They remain part of Source checks
CI, including the new detail/elapsed/unknown-progress/navigation regression.
Fresh Windows/Linux runtime/package CI and owner retry are still pending.

Compiled-game input fingerprint:
7bf57fbc867fa84052d5a6b0a3d0e4a4ffe0fc2a74b480561151f2f3d50718eb.
Build/generator scripts changed, so allow one preparation/build update; completed
tools/imports and all saves/settings are retained. No native selection, game
logic or clocks changed. Coverage stays 38.4156% linked / 61.5844% outside.
No commercial icon pixels or other game-derived payloads are in this source ZIP.

1. With your source checkout on dev, copy ALL contents of this ZIP's
   Nitrogen-Squared folder into B:\Nitrogen-Squared-dev, replacing existing files.
   Preserve .git and .local. There are no tracked deletions.
2. Review and commit in PowerShell:

```powershell
cd B:\Nitrogen-Squared-dev
git switch dev
git add -A
git diff --cached --stat
git diff --cached --check
git status --short
git commit -m "Fix setup timestamp loop and improve desktop build progress"
git push origin dev
```

3. Wait for ALL three workflows to pass on that exact commit. Install the
   complete new Windows ARTIFACT with game/launcher closed, retaining .local.
   Source copied into the Git checkout does not update your installed launcher.
4. Click Play and confirm setup advances from configuring into actual compiler
   jobs, shows useful status/elapsed/workers, and opens the game with its yellow N
   icon. Close the game and click Play again to verify reuse and preserved saves.
   The job budget does not promise 80% CPU usage during serial stages.
5. Report the focused n0202 Dashboard results; its earlier submitted result bytes
   are preserved. Keep this candidate on dev until owner verification and explicit
   release clearance. No repeat campaign or deliberate save overwrite is needed.

Immediate repair for the already installed old candidate (game/launcher/Ninja
stopped; run in B:\Games\Nitrogen-Squared):

```powershell
$now = (Get-Date).ToUniversalTime()
Get-ChildItem .\app -Recurse -File |
    Where-Object { $_.LastWriteTimeUtc -gt $now } |
    ForEach-Object { $_.LastWriteTimeUtc = $now }
```

Then reopen the launcher and retry Play. This changes only future source-file
metadata and preserves .local. The new candidate automates the narrower reviewed
build-input repair and prevents newly packaged ZIPs from carrying future dates.
