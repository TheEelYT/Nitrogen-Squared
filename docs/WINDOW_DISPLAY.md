# Window-driven presentation

The 0.0.24 candidate follows the drawable game area, excluding the desktop menu
bar. Qualification is in progress; 0.0.23 remains the accepted public release.

The game view uses the window's aspect. Wider windows use the pinned toolkit's
native-wide compositor, preserving the original projection and revealing side
columns. Narrower windows crop a proportion-correct 4:3 world. They do not
stretch the backdrop or change the projection. Authored movie/logo/image screens
retain their 4:3 framing with bars where needed.

The interface scale is `max(1, floor(min(width / 320, height / 240)))`, using
physical game-area pixels. Thus 480x360 and 608x456 use 1x; 640x480 and 800x600
use 2x; 960x720 uses 3x. A portrait window also respects its available width.
Original PS1 pixel proportions are retained across N2O's display modes. Menus,
score widgets and the weapon preview have title-specific shared anchors.
The System > Settings display readout reports the game area and interface step.

The toolkit rasterizes at integer internal scales, rounded up from the game-area
height with a 240-line reference, then presents at the actual drawable size.
Texture, movie and presentation sampling use nearest-neighbor. Nearest presents
also bypass the toolkit's implicit area resolve. Fractional sizes can have pixel
phase differences; this is not a pixel-identical integer upscaler for every
window size. Game update and video/audio clocks are unchanged.

Original build-time adapters operate on private copies of the pinned GPU,
renderer and host main. Exact source contracts fail closed on upstream drift.
The checkout is not modified. UI metadata recognizes the USA font/UI palette
column and the bounded weapon-preview ordering layers, with guarded front-layer
flat backing panels. Unrecognized world sprites are not classified as UI.
Per-primitive tags travel with render-worker records; the worker never queries
live guest packet state. CPU packet coordinates and UVs are not rewritten.

`-DNITROGEN_WINDOW_DISPLAY=OFF` retains the original fixed-aspect presentation
path for diagnosis. Native slice selection and its linked-range metric are
unchanged: 324,928 / 845,824 bytes, 38.4156% linked and 61.5844% outside.

Validation must include real window surfaces. SDL 3.4.10's offscreen driver
reports a resize without reallocating its EGL pbuffer; captures beyond its
creation size are invalid evidence. Use Windows or X11/EGL for resize checks.
