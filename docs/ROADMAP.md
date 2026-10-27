# Windows first, Vita by design

## Accepted baseline — 0.0.9

Windows gameplay is user-tested through level 4 with no issues reported. Saving
and high scores work. Native openings/skipping, analog input and consistent 60 FPS
gameplay were verified in preceding updates; the user reports no regressions in
0.0.9. That is enough player coverage to continue native work. Later levels and
two-player behavior remain unverified, without blocking this next milestone.

The verified importer, private build and source-only distribution gate stay in
place. Version 0.0.10 adds two native gameplay lookup routines to the boot-loader
translations: 2.1238% of selected executable payload bytes, with 97.8762% outside
linked ranges. Windows player acceptance of this new slice is pending. See
[native progress](NATIVE_PROGRESS.md) for the metric and separate native services.

## 1. Loaded-code identity and native game slices — underway

The [first slice](NATIVE_GAME_SLICES.md) uses per-entry resident code identity and
retains the interpreter on a mismatch. Private comparisons qualify its two leaf
routines. Continue with measured candidates and their caller boundaries below;
the general load/transition and nested-call problem is not yet fully qualified.

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
