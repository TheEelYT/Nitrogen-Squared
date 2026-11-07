# In-game options

Version 0.1.1 keeps complete two-line Audio track names, including remix names
and their shadows, centred together. Audio has only a bottom-left Back footer;
low text on its right side must not be classified as a right footer. Hold Back
on the title screen for two seconds to close; closing... fades in over the first
second at the game area's top third. Release cancels, and main-menu and submenu Back are unchanged.
Holding Tab no longer triggers Turbo. Ordinary Tab UI input is retained.

Version 0.0.30 places Master immediately above SFX and keeps Play in order's
song title text only, even when selected. Master, effects, ambient and music
sliders share the original additive luminous fill and aligned tick tracks. The
bottom Audio arrow clears the last row. Video uses the original help-atlas
left/right icons and the same slider fill. Complete help-card layers and the
Controls model/callouts keep a shared UI transform across window shapes.

Version 0.0.29 replaces Center screen with Video, locks the game's display
offsets to zero, and renames the other option entries to Audio, Controls and
Extras. Focused player checks are listed in TESTING.md; qualification receipts live in docs/VALIDATION.md.

Video provides desktop window mode, AUTO/2X/3X/4X/6X HUD scale and a world render
percentage (25–200 in five-point steps). AUTO keeps the existing square-pixel formula and 2X minimum. The
world target follows the drawable dimensions, while tagged interface primitives
retain their separate resolution and transform. Movie framing remains unchanged.

Audio retains its speaker-mode, effects, ambient, music and track controls and
adds Master volume. The master affects both game output and native movies. The
desktop F1 menu no longer duplicates this volume slider.

Preferences use the launcher's `NITROGEN_OPTIONS_FILE` inside the installation's
private working directory, outside the replaceable runtime build. An older F1
volume is migrated when no new settings file exists. Video mode is hidden on
mobile/Vita targets, which use fullscreen. The current public packages remain
desktop Windows/Linux; this is not a new mobile or Vita release.

Menu extensions call the imported game's font and decoration routines. Both
entry guards and complete function hashes come from the verified player import;
other executable occupants retain the original dispatch path. No game strings,
font pixels, instruction guards or compiled game modules are distributed.

The presentation enhancement changes no native-range selection or coverage
credit. Local menu/controller, persistence and world/UI renderer checks pass.
Normal production and platform/package receipts are recorded in
[validation](VALIDATION.md); fresh player checks remain version-specific.
