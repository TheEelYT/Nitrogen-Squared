# Apply the 0.2.1 native launcher regression-fixture revision

Complete source snapshot based on dev bb8245b. Version remains 0.2.1.
Nothing was pushed, promoted, tagged, published or rerun in Actions. The owner
canceled the other bb8245b workflows after the Windows source check failed.

Copy this ZIP's Nitrogen-Squared contents into B:\Nitrogen-Squared-dev,
preserving .git. There are no new deletions. Preserve your entire .local folder.

The preceding UTF-8 file-writing fix did not resolve the Windows CI assertion.
This revision gives the subprocess regression the native Windows/Linux layout,
the same isolated UTF-8 interpreter flags as the actual launcher, and a prepared
synthetic receipt generated in the interpreter that consumes it. Test workers
use the host interpreter rather than an absent portable interpreter. An unexpected
rebuild fails explicitly. The one-Play/no-follow-up-input and separate worker
stdin assertions are retained. No launcher, game, audio or UI code changes.

The test now captures child stderr, non-JSON output, state/error responses and
the backend setup log. A dead child or explicit backend error fails promptly;
otherwise its bounded cold-start deadline is 15 seconds. Nothing is skipped or
retried. A future failure must expose the real child error in the Actions log.

All 145 local tests pass. Both layout classes were exercised locally on Linux;
a deliberately broken child still fails and displays its real traceback.
These checks do not substitute for an actual Windows CI run. Windows CI still
needs to confirm this revision; do not treat this handoff as a verified Windows fix.

```powershell
git add -A
git diff --cached --stat
git status --short
git commit -m "Use native launcher fixture setup and expose subprocess failures"
git push origin dev
```

Both actual platform package jobs and both runtime jobs from 3564c80 succeeded;
its final candidate staging was blocked by the source-test gate. Keep new work on
dev, and wait for explicit owner release clearance before promoting main.
