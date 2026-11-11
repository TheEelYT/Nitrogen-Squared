# Apply the 0.2.2 ZIP packaging date correction

Complete source based on dev d83eeddcbe10c79abb785dc71812e7b9830200b2.
Version stays unreleased 0.2.2. Includes all prior timestamp-loop recovery,
desktop job scheduling, detailed progress, setup recovery and game-icon work.
No remote write, promotion, tag or release was performed.

At d83eedd, Source checks 42967736778 passed (Windows, Linux and launcher UI),
and Runtime and renderer checks 42967736765 passed on Windows/Linux. Release
42967736853 failed both package jobs before smoke tests/artifact staging:
ValueError: ZIP does not support timestamps before 1980.

The shared archive_file helper called ZipInfo.from_file with strict timestamps,
so an old bundled file was rejected BEFORE its safe 1980 archive date was set.
The ZipFile object's strict_timestamps=False did not control this separate
metadata call. The fix passes that flag to from_file too, preserving the fixed
archive date, file modes and bytes. No launcher, build-policy or game change.

Regression: a new original dependency notice dated 1970 reproduces the exact
failure with the prior helper. It passes with the correction and retains its
source timestamp/content. The actual Linux package/update fixture also includes
a 1970 notice and passes. All 167 Python tests pass without skips; source audit
passes. Fresh platform package/smoke CI remains required; a full Windows package
was not built locally. No browser rerun was needed for this packaging-only edit.

Compiled-game fingerprint stays:
7bf57fbc867fa84052d5a6b0a3d0e4a4ffe0fc2a74b480561151f2f3d50718eb.
This correction itself requires no additional game rebuild. Keep the existing
0.2.2 candidate's setup/build update and focused player checks. Native selection,
coverage (38.4156% linked / 61.5844% outside) and clocks are unchanged.

Copy all contents of this ZIP's Nitrogen-Squared folder over the source checkout
B:\Nitrogen-Squared-dev on dev, replacing files. Preserve .git and .local.
No tracked deletions. This is complete source, not a compiled Windows artifact.

```powershell
cd B:\Nitrogen-Squared-dev
git switch dev
git add -A
git diff --cached --stat
git diff --cached --check
git status --short
git commit -m "Fix packaging of files with pre-1980 timestamps"
git push origin dev
```

Wait for all three workflows on the new commit, then install the complete new
Windows artifact with the launcher/game closed and .local preserved. Retry the
focused setup/progress/icon/reuse checks. Source copied into the Git checkout
does not update an already installed launcher. n0202 submitted result bytes are
preserved. Keep this on dev pending owner verification and release clearance.
