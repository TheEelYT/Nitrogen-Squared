# First loaded-game native slice

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
edited. Larger routines with calls, shared continuations or self-modification
will need additional boundary qualification before they are selected.

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
