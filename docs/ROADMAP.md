# Windows first, Vita by design

## Accepted player baseline — 0.0.11 through level 9

The user tested Windows gameplay through level 9 with no bugs noticed beyond the
save slowdown. Saving/high scores, native openings/skipping and analog input were
accepted in preceding updates. This is enough player coverage to continue native
work; levels beyond 9 and two-player behavior remain unverified.

The importer, private build and source-only distribution gate remain in place.
Version 0.0.12 adds 20 card-control/BIOS-call entry ranges to the previous packet
and angle group. Linked coverage is 4.2642%, with 95.7358% outside linked ranges.
Local card-access samples improved to roughly 60 FPS, and setup-card images
matched the baseline after fresh creation and overwrite. The user reports no
saving/loading slowdowns on Windows in 0.0.12, passing that focused performance
check. Exact FPS and a new campaign playthrough were not separately reported. See
[native progress](NATIVE_PROGRESS.md) for the metric and separate native services.

## 1. Loaded-code identity and native game slices — underway

The [first slice](NATIVE_GAME_SLICES.md) uses per-entry resident code identity and
retains the interpreter on a mismatch. Private comparisons qualify its two leaf
routines. Continue with measured candidates and their caller boundaries below;
the general load/transition and nested-call problem is not yet fully qualified.

Original synthetic tests now cover mixed native/interpreted indirect calls,
callbacks, tail transfers and code replaced while a compiled caller is suspended.
All 122 cases pass locally and in Windows/Linux CI. This qualifies those
runtime mechanisms on the tested original programs, not additional game callers.
The next game group still needs fresh private caller/result comparisons before
selection. The user's original disc input has been restored and reverified;
there is no new-file or repeated campaign-test requirement for this test chunk.

`N2O.EXE` and `NEW.EXE` have overlapping addresses. Simply linking all analysis
output could dispatch a function belonging to the wrong executable. The next
runtime milestone is therefore a small, guarded native slice of loaded game code:

1. Map load/transition boundaries and active executable identity on the accepted
   opening-to-menu/first-level route. Select candidate functions using bounded
   private execution measurements, not generated function counts alone.
2. Qualify dispatch against the active executable and verified code bytes, with
   stale native mappings invalidated when code is replaced. Establish handling of
   calls into/out of the selected slice and preserve interpreter fallback for
   unknown or changed code. Test same-address/different-code dispatch with original
   synthetic fixtures before enabling commercial-game translations privately.
3. Link a small verified function group generated from the player's own import.
   Compare its results with the reference path at the function's observable
   boundary, including memory/register effects and timing-sensitive behavior.
4. Repeat the short Windows route and affected persistence/menu/input checks.
   Increase the linked coverage only for ranges actually linked and qualified;
   if this update establishes infrastructure alone, report unchanged coverage.

Do not enable both full executable translations in one unqualified change. No
game-derived source, guard instructions, modules or captures may ship publicly.

## 2. Expand native game execution and replace guest services

Grow the verified slices through frequently executed routines and then their
callers: menu/level transitions, simulation and rendering preparation. Keep the
working reference route available for comparisons. Track linked range coverage
and, when available, route-specific native/fallback execution separately so a
small hot function's runtime benefit is visible without inflating completion.

The reported save/load slowdown is resolved on the user's 0.0.12 Windows route.
Retain the card benchmarks and reference path as native groups expand. Guest
serial-driver/interrupt work and synchronous file publication remain distinct
costs. Preserve card formats and error/completion semantics; qualify any future
native save service against private copies of existing saves.

Version 0.0.12 advances that card-control work through 20 guarded native entry
ranges, retaining original BIOS-event and persistence paths. The production build
reports 4.2642% linked payload coverage and 95.7358% outside linked ranges. Windows
save/load slowdown check passed on Windows; 0.0.11 through level 9 remains the
previous accepted campaign baseline. This does not establish a native save-system service.

Native gameplay audio follows qualification of the game's sound-driver boundary:
identify cue IDs, bank/sequence ownership, voice control, music transport and
volume behavior. Then deliver timestamped commands to a host audio service with
independent sample production. Qualify pause/resume, stop/reset, scene changes,
looping and buffer bounds. Moving the hardware SPU to a worker alone would still
retain PS1 sound emulation and would not establish a native cue interface.

Keep existing saves/high scores readable while replacing their game-facing
services. Test writes using private copies. Full campaign and two-player checks
can be added as coverage reaches their distinct code paths; do not require a full
playthrough for each small update.

## 3. Native rendering and optional remaster presentation

After game execution boundaries are understood, replace selected graphics
submission paths with host rendering at a stable game-facing boundary. The
current GL worker consumes PS1 commands; it is not this scene-level replacement.
Introduce higher resolution and other options separately so visual changes can
be compared against the original presentation. For unlocked display rates, first
separate fixed simulation ticks from presentation and qualify interpolation;
changing the guest clock is not a framerate-unlock implementation.

| Feature | Windows target | Vita target |
| --- | --- | --- |
| Rendering | Higher internal resolution, user-selectable | 960×544 output; internal resolution based on measured performance |
| Aspect | Original 4:3 plus true widescreen after camera/culling work | Same optional widescreen when validated |
| Geometry | Optional subpixel precision and perspective correction | Enable only where renderer and performance permit |
| Textures/HUD | Original art initially; optional original replacement packs later | Fit texture/cache limits; readable HUD |
| Controls | Remapping and modern controller support | Vita buttons/sticks; touch only when useful |
| Timing | Original simulation speed; higher presentation rate only after analysis | Stable original simulation timing |

These are targets, not implemented options. Increasing resolution cannot create
texture detail or higher-resolution prerecorded movies. Widescreen must show more
of the scene without stretching it; camera framing, culling, HUD and two-player
layouts need per-game work. Do not tie simulation speed to presentation FPS.

## 4. Vita runtime and preparation

Keep game-facing code free of Windows APIs. Platform-specific services must cover
display/rendering, audio, input, filesystem/user-data paths, fibers, and module loading.
Windows and Vita require different native module architectures and cache identities.
Run small ARM/platform feasibility checks alongside the Windows native milestones;
do not wait for nominal 100% coverage to discover a blocking Vita assumption.

The candidate runtime currently targets desktop SDL/OpenGL/Vulkan and Win32/POSIX
fibers. A Vita build is **not** available by simply changing the compiler:

- Evaluate SDL2/vitaGL against the runtime's graphics/shader requirements; desktop
  rendering paths cannot be assumed compatible with vitaGL.
- Add/validate a Vita fiber implementation; inspect 32-bit assumptions in the
  existing POSIX backend before considering it usable on ARM.
- Replace desktop native-library/compiler assumptions with Vita-compatible modules
  and a user-side desktop preparation path.
- Profile native code size, allocations, disc streaming and audio buffers on real
  hardware before selecting presentation features.

No Vita release date or performance claim until the core runtime is measured there.

## Update reporting

For every runtime update, refresh README.md's native/uncovered measurements and
native-service summary, and TESTING.md's current changes, focused player checks
and verification status. Record evidence and limitations in VALIDATION.md. Keep
earlier acceptance as history; never mark a replacement verified solely because
its previous implementation worked. Documentation-only updates need no runtime
version bump or player rebuild.
