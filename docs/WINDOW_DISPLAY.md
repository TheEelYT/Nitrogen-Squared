# Window-driven presentation

0.0.27 keeps the row-202/204 code label and row-203 password buttons centred;
corner footer plates start at row 205. The observed OT-440 shaded shield
polyline uses the weapon-panel role through its live streaming state, without
reading a stale command header. Bounded boost-fill palette 7667 shares that
role. World shield geometry and lens-flare exclusions remain separate.

0.0.26 refines complete UI layers after the owner reported remaining 0.0.25
plate, button, pulse-ring, pause-shadow, shield/firewall and high-score issues. HUD atlas
cells distinguish score/life/multiplier content from menu letters and shadows.
Selected-menu backing and complete footer rings share their matching UI roles;
the shield/firewall icon palettes share the weapon-panel role with sprites and counts.
The 2x floor, 365x240 reference and square-pixel policy below are unchanged.

0.0.25 repairs split menu phrases, incomplete bonus widgets and help-panel
scaling reported in 0.0.24. The 3D view follows the drawable game area, excluding
the desktop menu. Wider views use the toolkit projection inside the authored
viewport; portrait views crop a proportion-correct 4:3 world. Movies keep their
authored framing. Simulation and video/audio clocks are unchanged.

UI uses square source pixels with a **2x minimum**. Its step is
`max(2, floor(min(width / 365, height / 240)))`, using physical game-area pixels.
A 730x480 or 800x600 game area uses 2x, 1095x720 uses 3x, and 1460x960 uses 4x.
The menu bar is excluded; for example, a 720-pixel-tall window with its bar visible
has less than 720 pixels for the game. Settings reports the usable area and step.
Very small windows retain 2x and may crop UI instead of shrinking it further.

The reference is 365x240 as requested. The authored drawing canvas is 368x240;
the pinned toolkit's CRTC rounding reports a 364-column scanout, with height
varying with the game's screen-centre settings. Those are distinct from the
physical window size. Primitive metadata records the actual scanout height.
No non-square-pixel correction is applied to UI glyphs. Whole phrases, their
shadows, icons and panel backing use shared transforms. The score/progress HUD,
weapon/perk widget and footer controls have explicit shared roles. Individual
glyphs do not pick anchors by crossing a screen-position threshold.

Textures, movies and presents use nearest sampling. Nearest presents avoid area
averaging and half-texel zoom. UI vertices compensate the native raster bias and
use integer physical anchors; the internal raster covers the actual output in
both dimensions. This supports whole square blocks for bitmap text at fractional
window sizes. Rotating 3D geometry retains its normal rasterization.

Original build-time adapters operate on private copies of the pinned GPU, GTE,
renderer and host main. Exact source guards fail closed on drift. The framework
checkout is unmodified. Render-worker records carry UI roles and source height;
the worker never inspects live guest packet state. CPU packet coordinates and
texture data remain intact. Menu ray sprites are distinct from footer particles.
Unrecognized world sprites and the lens-flare palette stay outside UI handling.

`-DNITROGEN_WINDOW_DISPLAY=OFF` retains the original fixed-aspect diagnosis path.
Native selection stays unchanged: 324,928 / 845,824 bytes, 38.4156% linked and
61.5844% outside. Qualification must use real window surfaces: SDL 3.4.10's
offscreen resize does not reallocate its EGL pbuffer.
