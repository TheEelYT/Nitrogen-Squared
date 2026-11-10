# Apply the 0.2.1 Windows source-check fixture fix

Complete source snapshot based on dev commit 3564c80. Version stays 0.2.1.
Nothing was pushed, promoted, tagged or published. The owner pushes personally.

Copy the contents of this ZIP's Nitrogen-Squared folder into your existing
B:\Nitrogen-Squared-dev checkout, preserving .git. There are no new file deletions.
Keep your entire .local folder and close the game/launcher before replacing a
built package. This source ZIP contains no compiled game, caches or saves.

The only code change is in tests/test_launcher_service.py: both generated Python
fixture scripts now specify UTF-8 when written. The child script contains an
ellipsis; Windows Python 3.10's default ANSI encoding could make its source
unreadable to Python's UTF-8 parser, causing a misleading failed launch marker.
Launcher, game, audio and compiled-game inputs are unchanged by this correction.

```powershell
git add -A
git diff --cached --stat
git status --short
git commit -m "Write launcher subprocess fixtures as UTF-8 on Windows"
git push origin dev
```

The Windows-encoding reproduction failed before the fix and passes afterward.
All 145 local Python tests pass. Actions still needs to verify the new commit;
no actual Windows CI rerun is claimed by these local results. The earlier
3564c80 launcher UI and Linux source checks passed, and Windows runtime checks
passed. Platform packaging and remaining runtime results are read separately.
Do not promote main or create a release until explicit owner clearance.
