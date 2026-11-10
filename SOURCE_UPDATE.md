# Apply the 0.2.2 setup-process development candidate

Complete source snapshot based on dev/released 0.2.1 commit
79a2671befd7a387f3bdd3f85f875aabf2e56091. This is a new 0.2.2 dev candidate.
The owner still pushes personally. Nothing was pushed, tagged or published.
Do not move main or modify the 0.2.1 release branch/tag/assets for this candidate.

Close the game/launcher. Before copying, switch your source checkout to dev and
ensure it has no uncommitted work. Copy this ZIP's Nitrogen-Squared contents into
B:\Nitrogen-Squared-dev, preserving .git and the entire .local folder. There are
no tracked deletions. This ZIP contains source, not a Windows launcher build.

SDL/framework revision checks previously inherited the service's command pipe
and were not tracked for cancellation. They now use DEVNULL input, a tracked
child and a 30-second deadline. Stop reaches these children. Setup logs identify
sessions, every command, exit codes and failing commands. Git downloads use
--progress and publish receiving/resolving percentages in the launcher.

These are concrete process-handling corrections and diagnostics. They do NOT
establish the root cause of the owner's Windows first-setup stall. Direct SDL
fetch and checkout in the launcher's Python environment passed; a complete clean
Windows GUI setup remains unverified. Do not claim this candidate fixes it until
the Windows Actions build and owner retry confirm that behavior.

All 151 local Python tests pass with no skips. Two frontend action tests and the
Vite production build pass. A real service subprocess with its command input kept
open completes a synthetic first-setup query and starts its synthetic game after
one Play request. Reintroducing inherited query input makes that check fail;
restoring isolated input passes. Query timeout and Stop tests terminate their
actual child processes. These are Linux/local synthetic receipts, not a Windows
first-setup qualification or a real-game rebuild.

Compiled-game inputs stay
4ab9bc7e2cf8067a308fa329692040366619bfd9000b020368832efe70a156af.
Coverage stays 38.4156% linked / 61.5844% outside. Game code and clocks are unchanged.
Compatible 0.2.0/0.2.1 games remain reusable. Keep completed downloads/imports/saves.
TESTING.md adds n0202 setup/resume/cancellation checks and preserves submitted
results byte-for-byte. A separate fresh test installation must not replace or
clear the working installation's .local folder.

```powershell
git add -A
git diff --cached --stat
git status --short
git commit -m "Fix setup query isolation and add command diagnostics"
git push origin dev
```

Wait for Source checks, Runtime and renderer checks and the dev Release candidate.
Install that complete Windows candidate over the test installation, preserving
its partial .local folder. Retry Play; do not click Stop to launch. If blocked,
send the latest setup session's final Command/Command exited/error lines and
.local/launcher-error.log. Verify a separate blank setup only after the candidate
is installed. Owner verification and release clearance are still required before
promoting 0.2.2 to main.

For old 0.1.x installations, manually overlay the full platform package while
preserving .local: their installed updater rejects support/launcher/licenses.
Updating only launcher.exe is insufficient. The public 0.2.1 remains immutable.
