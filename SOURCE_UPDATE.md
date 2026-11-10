# Apply the 0.2.1 Tauri launcher source revision

This is source, based on dev commit 1b94d4c. Nothing has been pushed or released.
Keep using dev. Version remains 0.2.1 pending owner testing/release clearance.

1. Close the running game/launcher. Keep your entire .local folder.
2. Extract this ZIP somewhere temporary and copy the contents of its
   Nitrogen-Squared folder into your B:\Nitrogen-Squared-dev checkout.
   Preserve the checkout's .git directory; there is no .git in this ZIP.
3. ZIP copies cannot express deletions. Remove the two superseded tracked files:

```powershell
git rm --ignore-unmatch launcher/launcher_win.c tools/launcher_ui.py
git add -A
git diff --cached --stat
git status --short
```

The removed files are the former C bootstrap and canvas GUI. The new Tauri
source lives under launcher/src and launcher/src-tauri. Source/package CI now
builds it with Node/Rust and exercises the actual launcher in a system webview.
See launcher/README.md for local builds. LICENSE is GPL v3; COPYRIGHT declares
GPL-3.0-or-later for original code, with historical MIT and dependency notices
retained. Recompia credit and exact upstream revision are in launcher/UPSTREAM.md.

Commit/push dev when ready to build the candidate. Do not promote main or create
a release tag until you have tested it and explicitly cleared publication.


Local checks: 143 Python tests (no skips), two JavaScript action tests and six
Chromium interaction tests pass. Vite production and native Linux Tauri builds
pass; the native Linux package inventory is verified. Windows native/webview
checks and actual copied-host update/restart remain for Actions after your push.
No Windows build or player verification is implied by the source ZIP.
