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


## 0.0.12 candidate — card control and BIOS-call entries

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

The 0.0.11 baseline is accepted through level 9. This candidate has not yet been
accepted on Windows; focused card-read/write checks will replace an unrelated
campaign replay. The selected new ranges total 2,072 bytes. A production build
and verified coverage report are required before updating the reported metric.
