# In-game options

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
