# Apply the complete 0.2.2 game-icon and setup-recovery candidate

Full source based on dev 64c71b7967d55b6204da9348916902093c7242d8. Version stays 0.2.2.
Includes the previous missing-origin repair source; no need to apply its ZIP first.
Nothing was pushed, promoted, tagged or published. The owner performs all pushes.

The owner reports the installed 64c71b7 launcher works as intended, then requests
the disc's yellow N as the compiled game program icon before committing 0.2.2.
This source verifies the imported USA N2O.EXE, decodes its exact palette/bitmap,
and writes private multi-size ICO, PNG and icon.json files under
.local/runtime-dev/private/game-icon. The pinned framework embeds APP_ICON into
the Windows game EXE and stages the PNG for its existing game-window icon loader.
No disc-derived icon bytes, generated icons or derived headers are in this ZIP.
The new config contains only format, offsets, dimensions and hashes.

The icon changes compiled-game inputs, so allow ONE build update after installing
the new candidate. Do not delete .local; imports, tools, saves, settings and input
profiles remain. Subsequent Play reuses the new compatible build. Native selected
code/coverage stay 38.4156% linked / 61.5844% outside; clocks are unchanged.
New compiled-game input fingerprint:
5452a0ea2e4d2e60e27d4b71d9319f64133f94d558d898c3c923c69a02bf81f4.

Qualification: all 158 local Python tests pass with no skips. Actual verified-disc
extraction produced the requested yellow N. An independent PNG/ICO reader checked
every size (16,32,48,64,128,256), and a compiled harness using the exact pinned
framework's real SDL window-icon loader decoded/applied the exact private pixels.
CMake integration tests exercise APP_ICON propagation and incomplete-input failure.
The game build verifies its staged PNG and, on Windows, compares every embedded
PE icon resource against the private ICO. Real cross-platform runtime/package CI
now uses an original checkerboard icon to verify that path without commercial data.
Windows CI, actual shell/taskbar appearance and owner verification remain pending.
No full native-game rebuild/playtest was performed in this Linux source workspace.

Before copying, go to your source checkout and switch to dev:

```powershell
cd B:\Nitrogen-Squared-dev
git switch dev
git status --short
```

Extract this ZIP separately. Copy ALL contents of its Nitrogen-Squared folder over
B:\Nitrogen-Squared-dev, replacing source files. Preserve .git and all of .local.
No tracked deletions are required. Expected existing changes from the preceding
uncommitted origin-repair ZIP are included in this complete snapshot.

```powershell
git add -A
git diff --cached --stat
git diff --cached --check
git status --short
git commit -m "Add private disc-derived game icon and repair interrupted setup"
git push origin dev
```

Stop if a command fails or the staged list contains unrelated files. Do not push
main, create a release tag or publish this unverified candidate. Wait for all three
workflows, then download the NEW Windows artifact from that commit. Close the game
and launcher, overlay the complete platform package, keeping .local, and run it.
Let the game build update finish; check the yellow N on the EXE and running game.
Close the game and Play once more to confirm reuse and retained player state.

The source keeps the interrupted SDL/framework remote repair and query isolation,
cancellation, deadlines and command logs. A missing expected origin is restored;
a different existing origin/revision is reported and preserved. A separate blank
setup can verify automatic recovery without clearing the working installation.
TESTING.md keeps n0202, adds a fresh N2-GAME-ICON check and preserves result bodies.
The owner requested withdrawal of the broken 0.2.1 release download; preserve its
source history and do not recreate a withdrawn release without authorization.
