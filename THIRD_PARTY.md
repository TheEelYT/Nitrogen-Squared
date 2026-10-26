# Third-party foundation under evaluation

PSXRecomp: https://github.com/RetroPortingToolKit/psxrecomp

Pinned evaluation revision: `f42d2c004b3dd6ef6ccb83101b40ede55f24bf59`.
At this revision, the upstream root license is **PolyForm Noncommercial 1.0.0**.
That is a material condition for any future runtime distribution/commercial use;
the project's original MIT-licensed tools do not remove it. The foundation remains
under evaluation, including its suitability for the eventual release model.

The source package does not vendor or redistribute that checkout. The optional
developer bootstrap downloads it separately into `.local/`. Its upstream license
and dependency notices govern that code; this project's MIT license does not
relicense it. A binary release must first audit and include the applicable notices.

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
[third_party/COPYING.LGPLv2.1](third_party/COPYING.LGPLv2.1). This project's MIT
license does not relicense those tables. Their preferred modifiable source is
included in the source package with attribution.

The sector assembler, bit reader, XA decoder and player are original integration
code. The isolated MDEC DSP includes the pinned framework implementation privately
at build time, under its separate terms. No FFmpeg executable or library is needed
at runtime. Future binary distribution must satisfy applicable LGPL notice,
source/relinking requirements and the framework license. This project currently
distributes source only.
