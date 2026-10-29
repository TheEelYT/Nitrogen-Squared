# Native translation progress

The 0.0.16 normal build verifies **34.9538% linked native translation coverage**
against the combined payload sizes of the three selected USA game executables.
Its counts and selected source/range hashes match the qualified O3 diagnostic build.

The complementary **65.0462% (550,176 bytes)** is outside those linked ranges.
This is not a measured interpreter-execution percentage: payload data and
separately tracked native services prevent that interpretation.

| Executable | Linked native range bytes | Payload bytes | Coverage |
| --- | ---: | ---: | ---: |
| SLUS_006.37 (boot loader) | 17,908 | 53,248 | 33.6313% |
| N2O.EXE | 274,800 | 458,752 | 59.9016% |
| NEW.EXE | 2,940 | 333,824 | 0.8807% |
| Combined | 295,648 | 845,824 | 34.9538% |

This metric counts the union of emitted native code ranges actually linked into
the private runtime. The boot loader has 86 linked generated functions. The game
inventory has 546 N2O roots with 10,144 aliases and 44 NEW roots with 87 aliases;
aliases receive no extra byte/function credit. The 348 additions contribute
75,672 emitted bytes from 119,332 input bytes over 0.0.15, about 1.34 times its
combined linked share. They include 236 call-target roots and 112 observed
indirect/continuation boundaries, not 348 newly identified complete functions.
Full analysis C, BIOS, interpreter, renderer, audio backend and desktop menu do
not count.

The denominator includes embedded data, which has not yet been fully separated
from instructions. Therefore this is **not a project-completion percentage**, a
confirmed-function conversion percentage, or a scene-weighted native instruction
percentage. The two main executable translations are not linked wholesale;
current playability relies heavily on the interpreter. A future instruction/data map and
execution measurements will refine the metric rather than silently change its
meaning. Overlapping addresses in the two main executables remain separate
identities, never deduplicated by RAM address alone.

Reproduce after a successful build:

```powershell
python tools/native_progress.py --output .local/runtime-dev/native-progress.json
```

The command rechecks the extracted executable hashes, counts coalesced ranges
without double-counting overlapping blocks, and uses the build receipt's linked
executable/slice lists. Selected slice manifests and source/range hashes are also
checked; reference builds get no slice credit. It writes counts/metadata, not
game code or media. Reject a stale
pre-0.0.7 receipt by rebuilding first.

## Native services tracked separately

| Service | Current status |
| --- | --- |
| Desktop presentation and menu | Host implementations; user verified menu and keybinds on Windows |
| Gameplay render scheduling | Bounded OpenGL worker; local pixel parity checked, user reports no issues with 0.0.9 on Windows |
| Controller input | Host SDL input; analog gameplay verified by the user in 0.0.6 |
| Gameplay angle-table lookups | Two native leaf translations in N2O.EXE; private comparisons passed and user verified first-level gameplay in 0.0.10 |
| Drawing packet preparation | 25 additional native entry ranges, with guarded internal resumes; user verified 0.0.11 gameplay through level 9 |
| Geometry/object presentation and text | 32 additional native entry ranges in 0.0.13; private comparisons, first-level visuals, normal build and Windows/Linux CI passed; user reports no issues in the focused Windows playtest |
| Model primitives and game/menu control | 46 additional roots in 0.0.14; 10,316 private comparisons, 17 exact-frame checks, normal production/controller fixture and Windows/Linux CI passed; user reports no issues in the focused Windows playtest |
| Game/object updates and resource control | 117 additional native roots in 0.0.15; final diagnostic/replay, 17 exact-frame checks, normal/controller fixture and Windows/Linux CI passed; user reports no issues in the focused Windows playtest |
| Game/library and indirect entries | 348 additional entry roots in 0.0.16; strict O3 comparison/replay, 21 exact frames, normal controller and Windows/Linux CI passed; focused Windows player check pending |
| Card-control/event polling | 20 additional native entry ranges; BIOS/serial protocol and file publication retain compatibility services; user reports no Windows saving/loading slowdowns in 0.0.12 |
| Music and effects | Emulated SPU/CD path; no independent cue-driven player yet |
| Opening movies | Native STR/XA service for three opening routes; user verified Windows playback and skipping |
| Ending / separate STR route | Original playback until full call/return paths are qualified |
| Saves and high scores | Guest persistence through compatibility services; user reports working on Windows, not a native save-system replacement |

The Windows player baseline now reaches level 9 in 0.0.11, with no other gameplay
issues reported. The later 0.0.12 save/load slowdown check passed on the user's
Windows route; no new level-9 playthrough is inferred. Further
campaign progression is not required for the next native milestone. This does not
change the linked-range count or qualify untested later-level behavior.

Every runtime update must refresh the README's measured native/uncovered shares,
this service inventory when affected, and TESTING.md's specific player checks.
Report unchanged coverage explicitly for host-only work. Future execution-weighted
native/fallback measurements must be labeled separately with their sampled route;
they must not replace this denominator without a documented metric change.

The inspected disc contains interleaved XA audio in the movie extents. Replacing
CD music alone would not replace intro audio. Native movies should own synchronized
audio/video playback on one media timeline, with verified play, skip, stop and
return-to-game behavior. All media must continue to come from the user's verified
disc; no movie, sound bank, decoded cache or generated game code may ship publicly.

Direct packet inspection identified standard STR video headers in `CRYSTAL.SXA`,
`FOX.SXA`, `N2O.STR`, `N2O.SXA` and `N2OEND.SXA`. Most frames are 320x240;
`N2O.STR` uses 320x192. Small 16x16 frames and noncontinuous frame numbers also
occur, so native playback must handle those cases and qualify each clip's ending
rather than infer playback rules from its filename extension. No decoded media
was added to the repository.

The opening-movie service replaces one guarded 824-byte loop while retaining its
original setup/teardown caller. Track this separately as **3 of 3 opening routes**;
it does not add AOT ranges to the metric above. This is not all of NEW.EXE, nor
a defensible overall completion percentage.

Native audio is fully decoded before playback and consumed on its own callback.
Video follows that media timeline and may drop late frames. This removes rendering
as an audio producer for these clips; it cannot eliminate OS/device interruptions.
Gameplay audio remains guest timed.

Version 0.0.9 changes host scheduling, telemetry and window-title ownership. None
of those changes add native game ranges to the numerator. Coverage remains
**2.12%**. Native sound-driver work must establish the game's cue/bank interface;
a hardware SPU worker alone would still need correct register, DMA and interrupt
ordering. Gameplay audio production remains guest timed.

Version 0.0.10 adds the [first loaded-game slice](NATIVE_GAME_SLICES.md). Coverage
rises from 17,908 to 17,964 bytes (2.1172% to 2.1238%). Four decimal places now
show small increments; the metric itself has not changed. Both lookup routines
were exhaustively compared privately, although the sampled first-level route
observed calls to only the first. Do not count a synthetic fixture, emitted but
unlinked function, or host service toward these numbers.

Version 0.0.11 adds 25 drawing-packet entry ranges totaling 16,032 bytes. The
linked report now counts 113 root entries (86 boot, 27 N2O) and 33,996 bytes.
The 397 internal continuation aliases in the selected N2O slices receive no extra
function or byte credit. Some selected ranges transfer into unselected shared
code, which continues through fallback. These are native packet-preparation
translations, not a replacement scene renderer or native gameplay audio service.

Version 0.0.12 adds 20 card-control/BIOS-call entry ranges totaling 2,072 bytes.
The linked report counts 133 roots (86 boot, 47 N2O) and 36,068 bytes: **4.2642%**,
with **95.7358%** outside linked ranges. The selected N2O inventory has 531
continuation aliases, with no extra function/byte credit. Local startup samples
improved to 60 FPS; this is not an execution-weighted native percentage or a
Windows performance guarantee. The service still uses original BIOS events,
serial timing and synchronous card-file publication. Save-system replacement,
independent gameplay audio and unlocked presentation remain separate work.

The following development chunk adds original mixed-backend qualification to the
synthetic runtime fixture only. It exercises production dispatch across native
and interpreted calls, callbacks, tail transfers, code-page boundaries and a
suspended caller whose instructions change. All 122 cases passed locally and in
Windows/Linux CI. No new game ranges or services are selected:
**4.2642% linked / 95.7358% outside** remains
unchanged, and no player rebuild is needed.


Version 0.0.13 selects 32 further roots totaling 36,932 bytes. Together the
linked slices have 79 N2O roots and 1,523 continuation aliases, with no alias
byte/function credit. All 32 roots have private comparison evidence, including
constructed geometry and text inputs for entries absent from the live route.
The count measures emitted ranges, not coverage of every branch or game scenario.
The normal build and final Windows/Linux CI passed. The user subsequently
reports no issues noticed in the focused Windows playtest; no new level-9
campaign acceptance or exhaustive branch coverage is inferred.

## 0.0.14 — model primitives and game/menu control

Forty-six new roots add 75,948 bytes. The reduced binding has 125 N2O roots and
4,189 continuation aliases; aliases add no byte/function credit. Combined linked
coverage rises from 73,000 / 845,824 (8.6306%) to 148,948 / 845,824 (17.6098%),
about 2.04 times the previous share. The excluded share is 82.3902%.

Thirty-five new roots were observed live; 11 further packet roots have bounded
complete-call comparisons. The two large model roots have additional constructed
primitive/geometry cases. A candidate with an exception/return mismatch and 28
without adequate evidence remain on fallback. This is the selected emitted-range
inventory, not proof of every branch or an execution-time share. The final selection passed 10,316 private comparisons and 17 exact-frame
checks. The normal production build/controller fixture and Windows/Linux CI passed. The user reports no issues in the focused Windows 0.0.14 playtest; no new
level-9 campaign playthrough or exhaustive coverage is inferred.

## 0.0.15 gameplay/object selection

The final selection adds 86 game/object/presentation-control roots, two model
dispatch roots and 29 resource/service-control roots. Input bands total 78,396
bytes; the pinned emitter contributes 71,028 new reachable bytes. All 117 direct
roots were observed on the controlled first-level route. Final qualification
passed 968 live comparisons and 25 variants at each of 399 captured segment PCs
(9,975 replays), with 17 pixel-identical frames. The combined 10,943 comparisons
apply only to the final reduced binding. Three mismatch owners and 140 other
candidates without adequate evidence stay unselected. Native service counts and
compatibility services are unchanged. Normal-production/controller checks and
Windows/Linux CI passed. The user reports no issues in the focused Windows
0.0.15 playtest. See VALIDATION.md for the bounded inputs and limits.

## 0.0.16 final selection

The reduced binding adds 348 entry roots: 236 original call-target roots and 112
observed indirect/continuation boundaries. These are not 348 newly identified
complete functions. All 348 guarded code identities were observed: 347 direct
owner entries and one continuation-only entry. The final game inventory contains
546 N2O roots and 44 NEW roots with 10,231 continuation aliases. Input bands total
119,332 bytes; the emitted union adds 75,672 bytes. Combined normal coverage is
295,648 / 845,824 = **34.9538%**, with **65.0462%** outside. N2O itself reaches
59.9016%; this must not be presented as combined coverage or overall completion.

Final O3 qualification passed 18,633 private segment comparisons (1,458 live and 17,175 isolated replay) at 687 identity/PC
pairs, with 21 pixel-identical frames through first-level completion and bonus/shop.
Both C and C++ Release flags are -O3 -DNDEBUG. Normal-production source/range hashes
and coverage match; its three native openings, analog/fire and clean-quit fixture
passed, as did source audits and Windows/Linux CI. Focused Windows 0.0.16 player
acceptance remains pending. Earlier failed owners and their complete input spans
remain excluded. NEW additions are conservative CPU/RAM leaf paths; CPS movie
control callers remain interpreted to preserve the existing native movie override.
The pinned framework and production dispatch semantics are unchanged.

The original diagnostic selector now distinguishes guarded code identities at
shared PCs, records identity/PC witnesses and supports bounded exploratory failure
collection. Final qualification runs without collection, preblocks or miss tracing.
No diagnostic interposition remains in the normal player. Private generated code,
full guards, instruction words, witnesses, snapshots, captures and media stay out
of Git and releases. Bounded comparisons do not prove every branch or campaign.
