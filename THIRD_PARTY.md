# Third-party foundation under evaluation

PSXRecomp: https://github.com/RetroPortingToolKit/psxrecomp

Pinned evaluation revision: `f42d2c004b3dd6ef6ccb83101b40ede55f24bf59`.
At this revision, the upstream root license is **PolyForm Noncommercial 1.0.0**.
That is a material condition for any future runtime distribution/commercial use;
the project's original GPL-3.0-or-later tools do not remove it. The foundation remains
under evaluation, including its suitability for the eventual release model.

The source package does not vendor or redistribute that checkout. The developer bootstrap and portable launcher download it separately into `.local/`. Its upstream license
and dependency notices govern that code; this project's GPL license does not
relicense it. The public launcher does not include framework objects or a generated game runtime.
Privately fetched code retains its upstream license and notices.

The upstream framework supports PCSX-Redux OpenBIOS, an independently written
BIOS implementation. A Sony BIOS is not required by the current analysis tools.
No Sony BIOS, OpenBIOS image, recompiled BIOS, or game content is in this package.

## Desktop menu

Dear ImGui: https://github.com/ocornut/imgui

Pinned revision: `f5befd2d29e66809cd1110a152e375a7f1981f06` (v1.91.9b), MIT license.
CMake fetches its original core and SDL3/OpenGL backends into the private build.
The menu uses an installed host font when available, with ImGui's bundled default
as fallback; no host font file, game artwork or game font is included. The
source package includes our integration and the dependency pin, not a vendored
copy. Any future binary distribution must include Dear ImGui's license notice.

## Native movie decoder tables

`native/mpeg_tables.h` adapts MPEG-1 VLC, DC, run/level and quantization tables
from [FFmpeg n7.1 libavcodec/mpeg12data.c](https://github.com/FFmpeg/FFmpeg/blob/n7.1/libavcodec/mpeg12data.c).
Copyright (c) 2000, 2001 Fabrice Bellard; (c) 2002-2004 Michael Niedermayer.
These tables retain **LGPL 2.1-or-later** terms. The full license is included in
[third_party/COPYING.LGPLv2.1](third_party/COPYING.LGPLv2.1). This project's GPL
license does not relicense those tables. Their preferred modifiable source is
included in the source package with attribution.

The sector assembler, bit reader, XA decoder and player are original integration
code. The isolated MDEC DSP includes the pinned framework implementation privately
at build time, under its separate terms. No FFmpeg executable or library is needed
at runtime. Future binary distribution must satisfy applicable LGPL notice,
source/relinking requirements and the framework license. The public portable package includes these preferred modifiable sources under
app/, with the full LGPL license. Its launcher executable does not link this decoder
or the game runtime; those are compiled privately after disc verification.


## Portable Windows Python and preparation tools

The Windows ZIP includes official 64-bit CPython 3.13, its standard library and
Tcl/Tk support. CPython is distributed under its PSF license and included component
terms; see support/python/LICENSE.txt and the retained upstream Tcl/Tk notices.
The package includes no pip packages. The Tauri host uses the system WebView2 on Windows and does not embed game code.

First preparation downloads these tools into .local/tools rather than shipping
them in the release ZIP: LLVM-MinGW, MinGit, CMake and Ninja. Exact official release
URLs, sizes and SHA-256 pins are in configs/portable_tools.json. Their upstream
license/notice files are retained in the extracted private distributions. LLVM-MinGW
includes LLVM/Clang, mingw-w64 and runtime libraries with their respective terms;
MinGit includes Git and its bundled dependencies; CMake and Ninja retain their
upstream licenses. This project's GPL license does not relicense any component.
SDL3, Dear ImGui and the pinned PSXRecomp checkout are likewise fetched privately
for the build, with their source notices retained. No Sony BIOS or prepared game
module is distributed in the public ZIP.

Linux launcher packages include the Tauri host and reviewed source. Python,
GTK 3, WebKitGTK 4.1, compilers and graphics/audio libraries come from the user's system packages. Resolved Rust dependency notices ship beside the host. Pinned runtime
and SDL sources are downloaded during private preparation with their notices.


## Tauri launcher and Recompia interface (0.2.1 revision)

The frontend adapts Dittobyte/Recompia's launcher at commit
`56fca2b30cc900971b8871eaa1b9b7343c91e16a`, GPL-3.0-or-later.
See [launcher/UPSTREAM.md](launcher/UPSTREAM.md) for exact files and changes.
Original N2O project code adopts GPL-3.0-or-later at the owner's direction;
LICENSE contains GPL v3 and COPYRIGHT states the later-version permission.
The historical N2O MIT copyright/permission notice is retained in
third_party/LICENSE.MIT-history. This does not revoke earlier MIT grants or
change the terms of independently licensed third-party components.

Inter Variable font: Rasmus Andersson, SIL OFL 1.1; notice in
third_party/launcher/INTER-OFL.txt. Lucide icons: Lucide contributors, ISC,
including Feather-derived icons under MIT; full notices in LUCIDE.txt there.
Tauri: MIT OR Apache-2.0; both texts in third_party/launcher/. Rust dependency
versions are locked in launcher/src-tauri/Cargo.lock. The build collects resolved
crate license/notice files and an SPDX/repository inventory into the package's
support/launcher/licenses/. Frontend locks/build instructions and preferred
modifiable source ship under app/launcher. Node/Vite/Rust build tools are not
required on a player's Windows installation. The host invokes our existing
portable Python backend through local pipes; no Recompia game backend or
commercial artwork is bundled. The pinned PSXRecomp runtime remains a separate
private download with its own terms; adopting GPL does not relicense it.
