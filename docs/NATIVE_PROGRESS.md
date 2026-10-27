# Native translation progress

The 0.0.10 baseline has **2.1238% linked native translation coverage** against the
combined payload sizes of the three selected USA game executables:

The complementary **97.8762% (827,860 bytes)** is outside those linked translation
ranges. It is not a measured interpreter-execution percentage: payload data and
separately tracked native service replacements prevent that interpretation.

| Executable | Linked native range bytes | Payload bytes | Coverage |
| --- | ---: | ---: | ---: |
| SLUS_006.37 (boot loader) | 17,908 | 53,248 | 33.63% |
| N2O.EXE | 56 | 458,752 | 0.0122% |
| NEW.EXE | 0 | 333,824 | 0.00% |
| Combined | 17,964 | 845,824 | 2.1238% |

This deliberately conservative metric counts the union of emitted native code
ranges for executables actually linked into the private runtime. The boot loader
has 86 linked generated functions. Two privately generated leaf routines in
N2O.EXE add 56 bytes; the full analysis C for N2O.EXE and NEW.EXE does not count.
BIOS, interpreter, renderer, audio backend and desktop menu do not
count as native game code.

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
| Gameplay angle-table lookups | Two native leaf translations in N2O.EXE; private interpreter comparisons passed, Windows player check pending |
| Music and effects | Emulated SPU/CD path; no independent cue-driven player yet |
| Opening movies | Native STR/XA service for three opening routes; user verified Windows playback and skipping |
| Ending / separate STR route | Original playback until full call/return paths are qualified |
| Saves and high scores | Guest persistence through compatibility services; user reports working on Windows, not a native save-system replacement |

The Windows player baseline now reaches level 4 with no issues reported. Further
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
