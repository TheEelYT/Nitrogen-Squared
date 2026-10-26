# Native translation progress

The 0.0.8 baseline has **2.12% linked native translation coverage** against the
combined payload sizes of the three selected USA game executables:

| Executable | Linked native range bytes | Payload bytes | Coverage |
| --- | ---: | ---: | ---: |
| SLUS_006.37 (boot loader) | 17,908 | 53,248 | 33.63% |
| N2O.EXE | 0 | 458,752 | 0.00% |
| NEW.EXE | 0 | 333,824 | 0.00% |
| Combined | 17,908 | 845,824 | 2.12% |

This deliberately conservative metric counts the union of emitted native code
ranges for executables actually linked into the private runtime. The boot loader
has 86 linked generated functions. Analysis-only C for N2O.EXE and NEW.EXE does
not count. BIOS, interpreter, renderer, audio backend and desktop menu do not
count as native game code.

The denominator includes embedded data, which has not yet been fully separated
from instructions. Therefore this is **not a project-completion percentage**, a
confirmed-function conversion percentage, or a scene-weighted native instruction
percentage. The two main executable translations are not linked yet; current
playability relies heavily on the interpreter. A future instruction/data map and
execution measurements will refine the metric rather than silently change its
meaning. Overlapping addresses in the two main executables remain separate
identities, never deduplicated by RAM address alone.

Reproduce after a successful build:

```powershell
python tools/native_progress.py --output .local/runtime-dev/native-progress.json
```

The command rechecks the extracted executable hashes, counts coalesced ranges
without double-counting overlapping blocks, and uses the build receipt's linked
executable list. It writes counts/metadata, not game code or media. Reject a stale
pre-0.0.7 receipt by rebuilding first.

## Native services tracked separately

| Service | Current status |
| --- | --- |
| Desktop presentation and menu | Host implementations; user verified menu and keybinds on Windows |
| Controller input | Host SDL input; analog gameplay verified by the user in 0.0.6 |
| Music and effects | Emulated SPU/CD path; no independent cue-driven player yet |
| Opening movies | Native STR/XA service for three opening routes; Windows audio acceptance pending |
| Ending / separate STR route | Original playback until full call/return paths are qualified |

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
