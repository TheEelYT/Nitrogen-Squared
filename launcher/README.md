# Nitrogen Squared launcher

Tauri 2 desktop launcher, adapted from Recompia's GPL-3.0-or-later frontend.
See UPSTREAM.md for exact provenance and THIRD_PARTY.md for component licenses.
The runtime game code stays C11/C++17; this launcher calls the existing portable
Python backend over local JSON-lines pipes. No local web server runs in release.

## Build

Build tools (maintainers only): Node.js 24, Rust stable, Python 3.11+ and Pillow.
Windows: use the x64 Visual Studio C++ build environment and the Windows SDK.
Linux: install `build-essential pkg-config libgtk-3-dev libwebkit2gtk-4.1-dev
librsvg2-dev patchelf` (Ubuntu 24.04+). Windows players need no Node/Rust/VS;
Microsoft Edge WebView2 must be available. Linux players use GTK/WebKitGTK and
system Python; runtime build prerequisites remain in README-FIRST.txt.

From the repository root:

```sh
python -m pip install pillow
python tools/build_launcher.py
python tools/package_windows.py  # Windows only
# or: python tools/package_linux.py
```

`build_launcher.py` uses npm ci and Cargo --locked, limits compilation to two
jobs, derives native icons from the exact owner logo, builds the frontend/native
host and collects resolved Rust dependency notices. No game input is read.
Outputs are under dist/launcher-windows or dist/launcher-linux. Package builders
refuse to ship without the native binary and dependency notices. Full preferred
modifiable source, dependency locks, GPL and credits ship in app/.

## Work on the interface

```sh
cd launcher
npm ci --ignore-scripts
npm run dev
```

Open the Vite URL in a browser. Its development-only adapter uses synthetic
state; it neither reads your files nor performs setup. This adapter is removed
from production. `npm test` checks readiness/cancel rules. Source CI additionally
runs browser interaction checks against this adapter (with Playwright).

For the actual native host, first build/package, extract the complete package,
then run its launcher.exe (Windows) or `sh launcher.sh` (Linux). Do not point it
at a source checkout: its backend/source are intentionally under app/.

## Qualification

`launcher.exe --self-test --report <install>/.local/launcher-smoke.json` (or
`sh launcher.sh` with the same flags) checks the real system webview, frontend,
artwork, navigation, settings and two responsive window sizes. It writes its
report through the actual Python bridge and exits. Self-test makes no network
requests, imports no game and changes no user preferences.

Portable CI also exercises bundled preparation tools against an original
synthetic runtime and the real copied updater/restart with private sentinels.
The updater waits for both the native host and Python service before replacing
files. Busy setup/game sessions reject closing and conflicting operations.


Build progress (0.2.2): Home shows the current preparation/build stage, current
compiler action, stage-local counter, selected worker budget and elapsed time.
The task continues across navigation. Quiet stages keep an indeterminate bar
and a moving elapsed clock; they do not invent an overall percent or estimate.
Desktop jobs default to 80% of available logical threads, rounded down.
