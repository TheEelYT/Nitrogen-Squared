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
25 original input/GTE variants. A mismatch stops qualification; do not count an
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
