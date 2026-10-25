# Windows first, Vita by design

## 1. Disc and code analysis — underway

- Verified one USA merged BIN/CUE and all executable inputs.
- Implemented local import and a first-run setup prototype.
- Built the pinned recompiler on the development host and generated isolated C.
- Linked a private runtime and reached opening videos, title/attract sequence,
  ship selection, level selection, tutorial screens and first-level gameplay on the development host.
- Next: validate the Windows window/audio/input path and first playable level,
  then establish code identity where executables share addresses and replace
  loaded-region interpreter fallback with verified native translations.
- Measure native execution and remaining fallback; do not report generation counts
  as a completion percentage.

## 2. Repeatable faithful Windows runtime

Integrate native game modules with graphics, SPU audio, CD/audio playback, input,
timing and memory cards. Validate a repeatable play route, two-player behavior and
save/load before visual changes. The native module/cache must be generated from
each player's own disc; no game-derived module is shipped in the public package.

## 3. Optional remaster presentation

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
