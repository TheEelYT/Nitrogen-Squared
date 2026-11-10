# Apply the 0.2.1 launch/progress and Linux CI fix

This complete source snapshot is based on dev commit 21f7b1d. Version stays
0.2.1, pending owner testing and explicit release clearance. Nothing was pushed,
promoted, tagged or released. The owner will push this source personally.

1. Extract this ZIP somewhere temporary.
2. Copy the contents of its Nitrogen-Squared folder into B:\Nitrogen-Squared-dev.
   Keep the checkout's .git directory. No .git, private game files or build tools
   are included in this ZIP. Keep your entire .local folder.
3. This revision has no new tracked-file deletions relative to the Tauri commit.
4. Stage and inspect, then commit/push dev when ready:

```powershell
git add -A
git diff --cached --stat
git status --short
git commit -m "Fix launcher startup progress and Linux audio smoke timing"
git push origin dev
```

Play now reports actual disc verification, relays child output without buffering,
and switches to Running only after the runtime supplies its PID receipt. Worker
processes receive EOF on stdin, keeping the UI protocol pipe private. Rapid
lifecycle/stage changes are always published. The Linux package had compiled;
its later audio smoke check assumed callback startup within 180 ms. That check
now waits for the same actual sample/clock progress with a three-second deadline,
without video/event pumping or game-clock changes. No test is skipped or retried.

After Actions completes, install the new Windows candidate preserving .local.
Click Play once and leave Stop alone: expect disc verification followed by the
game window, then Running. On game exit the launcher should become ready again.
A compatible 0.2.0 build is retained; no new campaign or save overwrite is needed.
The updated Linux package/complete runtime checks remain to be confirmed in CI.
