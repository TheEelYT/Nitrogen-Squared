# Native batch qualification tools

These are original developer tools, with no game instructions, generated bodies,
guards, media or captured inputs. They preserve the comparison process across
scratch-workspace resets. They are not linked into normal player builds.

Use the pinned framework and a verified private import. Linux diagnostics only;
builds and game sessions remain serialized, with two compile jobs. The ordinary
Windows/Linux synthetic CI fixtures remain separate from private game comparisons.

Create a private selection file under `.local/`, one hexadecimal `start size`
pair per newly selected owner. This is address/size metadata, never instructions.
The comparator uses this file for root/continuation selection and each compiled
owner still passes the production residency gate. Empty/invalid metadata fails.

Build diagnostically with the existing wrapper, adding:

```sh
--diagnostics --cmake-arg=-DCMAKE_PROJECT_NitrogenSquared_INCLUDE="$PWD/tools/qualification/inject.cmake"
```

For a baseline route omit that include. Run `route.py --output .local/...`
with `--disc` pointing to the verified merged BIN and `--binary` when using a
preserved baseline executable. The input sequence covers opening movies, menus,
first-level movement/firing and pause/resume. Seventeen exact-frame scanouts and
aggregate device reports are saved privately. Compare decoded pixels, not file
encoding or approximate wall-clock capture times.

For the candidate route, set `N2O_COMPARE=1`, optionally `N2O_EDGE=1`, and
`N2O_SELECTION` to the absolute private selection-file path. The comparator
checks three bounded samples per observed PC and optionally 24 GTE variants at
each first observed root. It compares GPRs, HI/LO, PC, COP0, GTE data/control,
2 MiB main RAM and scratchpad. Device time is frozen for isolated segments;
device timing and host globals are not a universal equivalence claim. Restrict
selection to boundaries suitable for isolated CPU/RAM comparisons and retain
full-session visual and normal-production checks.

The reference pass is bounded to 1,048,576 basic blocks per segment to admit
full-memory word scans. Exhausting that budget leaves the segment unqualified;
inspect the input and control flow before changing the bound or selection.

Each first observed selected PC writes a private same-build raw CPU/RAM/scratchpad
witness. Never commit these files. They are intentionally not portable across
framework/ABI/platform changes. `replay.py` repeats each selected witness with
25 original input/GTE variants. `--keep-going` collects isolated failures across
the pool but still exits unsuccessfully if any fail. A mismatch stops
qualification for the affected owner; do not count an
unobserved or failed owner merely because generation succeeded. Constructed
complete-call cases may supplement live evidence but must document their inputs
and limits separately.

After final selection, rebuild and repeat qualification for the reduced binding.
Preserve its `game-slices.json` metadata privately. Clear the CMake project include
and rebuild without `--diagnostics` before testing the player executable.
`normal.py` verifies selected hashes against that qualified metadata, rejects a
production link containing comparison/replay hooks, and links a separate original
SDL controller fixture from production objects. Its captures and output stay
under `.local/`; the production executable is not replaced.

Check the normal fixture's movie completion, controller samples, gameplay images
and clean SDL_QUIT. Dummy-device audio counters are transport observations, not
physical audio quality or a Windows FPS benchmark. Record final-only comparison
counts, frame parity, production/source checks and pending player acceptance in
the project validation/testing documents. Count only linked emitted ranges using
`tools/native_progress.py`; these tools add no native game coverage themselves.

## Overlapping executable occupants

Current receipts include per-owner guarded ranges, CRC and a SHA-256 of the
covered instruction bytes as private metadata. `selection.py --manifest ...
--roots ... --output .local/.../selection.tsv` verifies the generated-file hashes
and produces a v2 selector plus a JSON image/owner map. The root file is the
address/size configuration subset being evaluated, not game instructions.

The v2 selector names exact entry/continuation PCs and their full guarded code
identity. Samples, counters and witnesses are keyed by identity plus PC. Distinct
occupants at the same address cannot consume each other's sample budget or
overwrite witnesses. Identical guarded code and PCs can be explicitly shared
across images; different code with an ambiguous CRC is rejected by the selector
generator. The existing production residency gate remains the authority at
runtime. The extra SHA/token metadata is not a new runtime authentication claim.
Legacy two-column selectors remain available for existing single-image checks.

For exploratory pools only, `N2O_COLLECT_FAILURES=1` requires a v2 selector. A
failed CPU/RAM comparison restores the input, disables that identity's native
entry/resume paths in the diagnostic interposer and returns control to the
interpreter fallback. It records blocked IDs and continues collecting evidence
for other candidates. The process still exits unsuccessfully (91) if any failed.
This does not qualify the failed owner, hardware side effects or the final build.
Prune failed/unobserved owners, regenerate into a fresh private source directory,
and repeat final live/replay/visual checks without collection before production
testing. These hooks are diagnostic-only and never enter normal player builds.

The native/reference uncharged windows are bounded to 16,777,216 cycles each,
in addition to the reference basic-block limit. Budget exhaustion leaves the
segment unqualified and stops collection to avoid reusing a device-advanced
state. `check.py --output .local/...` exercises the controller logic with original
stub backends; Linux runtime CI runs it automatically. `N2O_TRACE_MISSES=1` adds
private PC/prefix-hash discovery hints for untranslated dispatches. Those hints
must be checked against the original verified image and fully qualified before
any coverage credit.
