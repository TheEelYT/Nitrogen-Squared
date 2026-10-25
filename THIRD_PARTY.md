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
