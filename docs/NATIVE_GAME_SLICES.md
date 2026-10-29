# Loaded-game native slices

Version 0.0.10 links two privately generated leaf routines from the verified USA
N2O.EXE. This establishes a small native gameplay path through the existing
static-overlay mechanism. It does not link either main executable wholesale or
establish all of their load/call boundaries.

## Binding and behavior

The source facts in `configs/native_usa.json` name the half-open instruction band
`0x800566D4..0x8005670C` and its two 28-byte function entries. Preparation rechecks
the complete extracted executable size/SHA-256 against the verified disc identity.
The pinned emitter produces the C bodies, entry identities and covered ranges
from those local bytes. Every generated file remains under the private work
directory; no instruction bytes are present in the public binding.

Each routine masks `$a0` to a 12-bit angle, uses it to read one signed 16-bit lane
of the paired table in live guest RAM, and returns the value in `$v0`. The first
reads the lane at `0x80085D9C + 4 * angle`, the second the lane two bytes later.
The translated instructions retain their `$a0`/`$at` scratch effects. Neither
routine writes guest memory, changes SP/RA or makes a nested call. Their original
return/delay-slot behavior and generated timing helpers are retained. Table data
is read at runtime, never substituted with a distributed decoded table.

The static dispatcher keys the full guest PC. Only KSEG0 entries are generated;
KUSEG/KSEG1 aliases need their own translations and currently decline. For a
candidate PC, the framework gates execution on the CRC of every emitted code
range. Its page-generation cache watches those ranges and revalidates after code
writes or restore. A different executable, changed instruction body or unknown
entry falls back to the existing interpreter. A successful match is not inferred
from a shared address or matching prologue. Identical routine bytes need no
separate global executable switch to execute that routine correctly.

This uses CRC residency checks, not a cryptographic runtime-authentication claim.
The original input is separately SHA-256 verified. No pinned framework source is
edited. Nested calls, shared continuations and self-modification require additional
boundary qualification before their ranges are selected.

## Build selection and measurements

ENHANCED selects the generated slice; REFERENCE retains the interpreter route
and needs no private slice files at CMake configuration. The selected bodies,
binding facts, preparation recipe, CMake recipe and residency implementation are
included in the execution identity. The private build receipt records only the
selected slice inventory; reference builds do not receive native coverage credit.

`tools/native_progress.py` checks the receipt and generated source/range hashes,
then unions emitted ranges with existing translations per executable. It rejects
modified files rather than counting a stale build. The two routines add 56 bytes:
17,964 / 845,824 = **2.1238%** linked coverage, with **97.8762%** outside linked
ranges. The denominator and separate native-service accounting are unchanged.

Normal clean shutdown logs native dispatch and residency-rejection counts.
Diagnostic `probe_runtime.py` also keeps bounded aggregate counters; it excludes
private entry listings and capture data. Calls are not instruction counts or an
execution-weighted native percentage.

See [validation](VALIDATION.md) for private interpreter comparisons and synthetic
same-address replacement tests, and [Windows checks](../TESTING.md) for acceptance.

## 0.0.11 — drawing packet preparation

Twenty-five additional entry ranges in the existing declarative binding select
16,032 bytes of packet/geometry preparation from the local N2O.EXE. Together with
the two lookup readers, N2O has 27 selected roots and 16,088 linked bytes. Combined
with boot translations this is **33,996 / 845,824 = 4.0193%**, with **95.9807%**
outside linked ranges. Some ranges are prefixes that tail-transfer to unselected
shared code. No complete native scene-rendering engine is claimed.

The pinned emitter identifies internal continuations. Preparation uses its
resume-arm helper and emits wrappers that set the exact guest PC before entering
the owning native function. Each alias carries the complete owner's residency
ranges/CRC; missing owners are rejected. Real roots take priority. A code change
invalidates both the root and its aliases. The build currently has 397 aliases;
range manifests credit only the 27 roots, with no duplicate byte coverage.

Private qualification compares CPU registers, HI/LO, return PC, COP0, GTE state,
main RAM and scratchpad against the interpreter. Twenty-five live calls across
four packet-entry groups matched; adapted contexts and geometry edge states
produced 2,856 successful comparisons across the selected 25 entries. This is a
bounded corpus, not every possible game input. Device time is frozen for isolated
comparisons, so full-session timing is checked separately. An additional candidate
with reference/native exception behavior mismatches remains excluded entirely.

Original synthetic CI programs test RAM-writing loops, unsigned wrap, GTE
saturation and a computed transfer that must resume rather than restart. Owner
mutation invalidates its continuation. No game instructions, witnesses, generated
bodies or private capture/replay sources are included in Git or packages.

Dispatch counters include internal resumes from this version onward. They are
neither original function-call counts nor an execution-weighted native share.
The PS1 GPU command path and guest-timed SPU/CD path remain in use.


## 0.0.12 — card control and BIOS-call entries

Twenty additional entry ranges cover card-control/event-polling code and its
small BIOS-call trampolines. They use the existing private emitter and whole-range
residency gate, including internal continuation aliases. The polling code retains
its original BIOS calls and guest instruction timing. It does not skip the wait,
fabricate completion or replace the serial device or persistence service.

The new boundary is a caller that yields to separately dispatched callees and
resumes afterward. The original synthetic fixture tests this across separate
compiled records, with zero/1/2/7/64 iterations, the call/return delay slots and
restoration of the saved SP/RA. Private live tests compare each observed compiled
segment with interpreted execution up to the next outgoing call or return.
Device time is frozen for comparison; the live call then executes normally.
Full save/load tests and exact frame comparisons remain separate requirements.

The 0.0.11 baseline is accepted through level 9. The user subsequently reports no
saving/loading slowdowns on Windows in 0.0.12, passing that focused performance
check without implying a new campaign playthrough. The selected new ranges total
2,072 bytes. The production report verifies
36,068 / 845,824 = **4.2642%**, with **95.7358%** outside linked ranges. N2O has
47 roots and 531 continuation aliases; aliases receive no additional byte credit.

## Mixed-backend qualification for later batches

The original boundary fixture uses `psx_dispatch_call` from the linked OpenBIOS
backend rather than a test loop that selects a backend or repairs CPU return
state. Indirect native callers reach untranslated callees, interpreted callees
call or tail-transfer into a compiled callback, and the dispatcher resumes the
caller. KUSEG/KSEG1 callers retain their segment and use fallback. Register,
stack, delay-slot and neighboring-data checks detect a duplicated continuation.

A second caller placement spans two code pages. Byte/halfword writes through a
different data segment must invalidate/revalidate both its root and continuation.
An interpreted guest callee changes the suspended caller's return-delay
instruction; the whole-owner guard must decline its old native continuation,
and fallback must execute the changed result exactly once. Bulk RAM restoration
also invalidates warm cached matches. These are original synthetic programs, not
qualification of additional N2O functions, device timing or full-session gameplay.
All 122 production-dispatch cases passed locally and in Windows/Linux CI;
linked coverage and player behavior are unchanged. The fixture publishes its
original instructions as executable RAM, as the loader does, and needs no live
backend-selection switch. CI keeps failure output and writes fixture reports
under its private work directory.


## 0.0.13 — geometry, object presentation and text

Thirty-two further roots add 36,932 bytes from verified local N2O.EXE inputs.
The group includes geometry/packet preparation, object transforms and animation,
angle calculation and the text-formatting pair used by game presentation. The
existing pinned emitter, build-selected reference path and whole-owner residency
gates are unchanged. All 79 N2O roots and 1,523 aliases remain private generated
inputs; public bindings contain addresses/sizes, never instructions or guards.

Two controlled routes completed through guest frame 4,500. Live input replay
matched 212 segments across 71 PCs; the prompt-disabled route and adapted GTE
states matched another 548 segments across 73 PCs. Fifteen new roots were seen
live. A separate bounded corpus covered the other 17 roots and additionally
checked angle/text inputs: 4,320 complete calls across 20 roots produced 16,715
matching segments. Cases include primitive types/flags, empty/one-record models,
animation boundaries, signed numeric inputs, formatting options, extreme vertex
coordinates and projection/GTE edge states. Compatibility callees keep their
existing backend; their outputs feed the next checked native caller segment.

Across these corpora all 32 new roots have comparison evidence and all 17,475
segments matched GPRs, HI/LO, PC, COP0, GTE data/control, 2 MiB RAM and scratchpad.
Device time is frozen for isolated comparisons; this does not prove every cycle
or device interaction. Twenty matching-frame comparisons across the two live
routes were pixel-identical to 0.0.12. These are bounded corpora, not all possible
inputs, every branch or later campaign acceptance. Raw inputs, witnesses, private
checker code and captures remain outside Git and packages.

The normal build verifies 73,000 / 845,824 = **8.6306%**, with **91.3694%**
outside linked ranges. GTE/PS1 packet rendering, guest SPU/CD and card compatibility
services remain in use. This is native execution of more game code; it does not
replace the scene renderer or audio engine. The normal build and final platform
checkpoint checks passed. The user subsequently reports no issues in the focused
Windows 0.0.13 playtest.

## 0.0.14 — model primitive and game/menu presentation control

Forty-six further roots add 75,948 bytes from the verified local N2O.EXE.
Model primitive preparation, object packet helpers and game/menu presentation
control use the existing private emitter, complete-owner residency checks and
CPS continuation mechanism. The selected inventory has 125 N2O roots, 4,189
aliases and 131,040 N2O bytes; combined linked ranges total 148,948 / 845,824 =
17.6098%, with 82.3902% outside. No alias receives duplicate byte/function credit.

Thirty-five added roots were observed on controlled live routes. Eleven more
packet roots completed 216 constructed calls each, including numeric/dimension,
flag and GTE boundaries. The model roots at 0x8004532C and 0x8004A46C additionally
completed 648 constructed calls each across primitive types/flags, empty/one-record
models, extreme vertices and GTE/projection states. Captured continuation inputs
also receive isolated GTE-state comparisons. Device time is frozen for these
CPU/RAM/scratchpad/GTE checks; matching-frame sessions test the sampled route's
visual behavior separately.

The original 75-root candidate was reduced: 0x8004EB48 showed a native-return
versus interpreter-exception mismatch on a constructed input and is entirely
unselected. Another 28 roots lack adequate qualification. Their callers continue
through the existing backend; no pinned framework changes or exception bypass
are introduced. Native scene rendering, independent gameplay audio, BIOS/card
services and later-level campaign qualification remain separate work.

The final reduced build passed 10,316 segment comparisons and 17 matching-frame
checks. The normal production build reproduces the qualified source/range hashes;
its movie/controller/shutdown fixture and Windows/Linux CI passed. See
VALIDATION.md for the counts and limits. The user reports no issues in the focused Windows 0.0.14 playtest. All game instructions, emitted bodies/guards, snapshots,
comparison helpers and captures remain outside Git and release packages.

## 0.0.15 gameplay, object and resource-control roots

117 additional roots extend game/object updates and presentation control (86),
model dispatch (2) and resource/service control (29). Preparation revalidates the
private executable hashes and uses the pinned emitter and existing residency
gates. Complete generated bodies and instruction guards remain private.

The final binding has 242 N2O roots and 7,440 continuation aliases, contributing
202,068 N2O bytes. Combined linked coverage is 219,976 / 845,824 = 26.0073%, with
73.9927% outside. The update adds 71,028 emitted bytes from 78,396 selected input
bytes. Aliases, host services and analysis-only translations add no credit.

All 117 new roots were observed directly. Final reduced-binding checks passed
968 live comparisons, 9,975 isolated replays at 399 PCs and 17 pixel-identical
frames. Three mismatch owners and 140 other candidates without adequate evidence
remain unselected. These bounded tests do not prove all branches or later levels.
The normal production build/controller fixture and Windows/Linux CI passed;
the user reports no issues in the focused Windows 0.0.15 playtest.
PS1 rendering/GTE, guest sound and BIOS/card compatibility services
remain separate from this native-game range inventory.

## 0.0.16 game/library and observed indirect entries

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
passed, as did source audits and Windows/Linux CI. The user reports no issues
noticed on the Python-launched Windows 0.0.16 route; that reported route is
accepted. Direct-launch intro stutter remains a separate open issue. Earlier failed owners and their complete input spans
remain excluded. NEW additions are conservative CPU/RAM leaf paths; CPS movie
control callers remain interpreted to preserve the existing native movie override.
The pinned framework and production dispatch semantics are unchanged.

The original diagnostic selector now distinguishes guarded code identities at
shared PCs, records identity/PC witnesses and supports bounded exploratory failure
collection. Final qualification runs without collection, preblocks or miss tracing.
No diagnostic interposition remains in the normal player. Private generated code,
full guards, instruction words, witnesses, snapshots, captures and media stay out
of Git and releases. Bounded comparisons do not prove every branch or campaign.
