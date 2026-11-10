# Validation

Reports through 0.0.20 are preserved in
[the validation history](VALIDATION_THROUGH_0.0.20.md). Historical claims retain
their tested version and scope.

## 0.2.0 dev candidate — not released

The owner supersedes standing promotion approval: all work/fixes go on dev,
with explicit player verification AND release clearance before main, tags,
release branches or publication. Main/latest remain at 0.1.3. Dev source/runtime
checks and both package checks gate downloadable Actions candidates only.
The workflow condition fixture exercises dev/main/other refs and proves dev
cannot reach release creation or ref writes. No release/0.2.0 branch is created.

The launcher now distinguishes public VERSION from compiled-game inputs. New
receipts capture source/dependency/build settings and exact executable/manifest
hashes. Launcher/docs/version-only changes reuse the compatible game. Changed
build inputs/options, missing or inconsistent receipts and changed outputs request
rebuilding; failed preparation does not launch stale code. Legacy 0.1.x builds
prepare once. Settings and custom input profiles survive cache replacement.
Direct Python launch refuses stale receipts. Generated boot input cache identity
also includes the importer and emitter-build scripts.

All 128 local source tests and the 138-file reviewed source audit pass.
Windows/Linux runtime and package results are recorded by Actions for each dev
candidate commit, including the real-binary reuse fixture. Player verification
and explicit release clearance remain pending. Preserve prior submitted report bytes and
carry unfinished checks. No native game range changes: all 796 records and 48
exclusions remain, at 324,928 / 845,824 = 38.4156% linked / 61.5844% outside.
Clocks are unchanged and level-entry stutter remains OPEN.

## 0.1.3 PC keyboard defaults

The README's PC table previously differed from the compiled SDK stock layout.
The title's C11 adapter now supplies the documented defaults for new and unchanged
stock profiles, with the deliberate S Down/L1 overlap and A/D analog X steering.
W/S do not move analog Y. Custom profiles, including partial legacy and alternate
mouse bindings, are retained without rewriting their files. Explicit reset/save
uses the title defaults. Executable-relative discovery handles Linux binaries
without filename extensions. The pinned parser/sampler remains the implementation;
a configure-time source hash rejects an unreviewed change to its private contract.

This changes compiled runtime inputs and requires Prepare & play after updating.
No selected game ranges change: all 796 records and 48 exclusions remain, with
324,928 / 845,824 = 38.4156% linked / 61.5844% outside. Game/audio clocks remain
unchanged and level-entry stutter remains OPEN. Fresh n0103 player checks are
pending, unfinished checks carry forward and submitted result bodies are preserved.
The original runtime input fixture now exercises fresh/stock/custom bindings,
all documented key-to-button masks, analog axes, duplicate S, file preservation
and reset/save/reload through actual startup discovery from an unrelated cwd.
All 113 local source tests pass without skips; the 133-file source audit and
actual Dashboard parser/carry/idempotence/result-tail checks pass. The production
C11 adapter also passes the full keyboard fixture locally with the actual pinned
parser/sampler and installed SDL2; CI exercises the default SDL3 runtime. Final
Windows/Linux source/runtime/renderer and publication checks pass; the receipt
below records the released code and public-asset audit.

### 0.1.3 publication receipt

[0.1.3](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.1.3)
is published at immutable code, tag and release/0.1.3 commit
`b6dfc1c51ecd3627637b097e31de02f456b0210c`.
[Source checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/42513804052),
[Windows/Linux runtime and renderer checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/42513803983)
and [Release](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/42514544440)
all pass. Main was fast-forwarded to the exact checked release-branch commit.
The keyboard fixture passes with Windows CI and bundled toolchains, Linux
ENHANCED/REFERENCE builds and the actual packaged preparation paths. Existing
virtual-gamepad and direct-save parser fixtures also pass. The local CMake
contract check accepts LF/CRLF and rejects unexpected parser changes.

All five public assets were downloaded and verified against GitHub digests,
SHA256SUMS.txt and legacy sidecars. The Windows package owns 1,784 files, with
x64 bootstrap and Python license; Linux owns 135 files. Both contain the exact
133 reviewed source files after Git line-ending normalization; neither contains
private build output or README PNGs. Latest points to v0.1.3, while earlier
0.1.0/0.1.1/0.1.2 release targets, asset IDs, sizes and digests are unchanged.

- Windows ZIP SHA-256: `e941d13afca7def604bfa443ea965d38a35c28c492864244fbae7a3286864bac`.
- Linux ZIP SHA-256: `13f32475ba1f2f3ff8d8de4362a9367d6b73968f48115bb3c3fd4b87a7738c5e`.

This later receipt is documentation only; preserve the released code, branch,
tag and assets. Updating to the keyboard patch requires Prepare & play to
rebuild the private game. Fresh n0103 player keyboard checks remain pending;
these synthetic checks do not establish new gameplay acceptance. Historical
submitted report bytes are preserved and unfinished/blocked checks carry forward.
Native coverage stays 38.4156% linked / 61.5844% outside; all 796 records and
48 exclusions are unchanged. Clocks are unchanged and level-entry stutter is OPEN.

## 0.1.2 direct-launch save directory

The owner reports that launcher play uses .local/saves while direct execution
from runtime-dev/build selects runtime-dev/saves. Source inspection confirms the
launcher CLI override and the generated relative saves default diverge. Existing
settings.toml memory-card directory and per-slot paths can override game.toml.

This launcher/configuration repair persists the portable directory on preparation
and repairs already prepared game.toml files (including executable-local shadows)
and saved card-path overrides when the launcher opens and before play. Changed
configuration is backed up; both existing card folders are preserved without merge
or overwrite. Legacy-only cards are copied only if the portable folder is absent.
The Python launch path follows the persisted directory unless explicitly overridden.
No compiled runtime implementation, selected native ranges or game/audio clocks
change. Coverage remains 324,928 / 845,824 = 38.4156% linked / 61.5844% outside;
all 796 records and 48 exclusions remain. Level-entry stutter is still OPEN.

Local synthetic tests cover both binary layouts, stale per-slot settings, spaces,
unrelated cwd, idempotence/backups, binary preservation, conflicting and legacy-only
cards, malformed settings, symlink refusal and repair without invoking compilation.
All 113 source tests pass without skips with CMake/Ninja available. Final
Windows/Linux source, actual SDK parser/discovery, runtime/renderer and both
package/publication checks pass; release receipts follow below. Fresh n0102
player checks remain pending. Historical submitted results are preserved and
unfinished checks carried.

The save-path fix itself works with the existing compiled executable. The 0.1.x
Prepare & play version refresh is retained; general reuse remains scheduled for
0.2.0. Direct native-movie/environment parity is separate existing work. This is
not a new gameplay acceptance or a stutter fix.

### 0.1.2 publication receipt

Final release code, tag v0.1.2 and release/0.1.2 all identify
`f7aee187f2993ee3bb22fc8fa86bf316a4e4acac`.
[Source checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/42499682748)
and [Windows/Linux runtime and renderer checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/42499682728)
pass on that release-branch commit. Promotion keeps the identical commit;
[Release](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/42500620393)
then passes Windows/Linux packaging, startup, actual bundled/system-toolchain
synthetic runtime tests and copied-updater/restart preservation checks on main.
The real SDK discovery/settings parser reads the shared card sentinel from an
unrelated cwd, including the Windows Release/ layout. Linux renderer/worker
comparisons pass as well. No commercial game data is used by these CI fixtures.

All five actual public assets were downloaded and verified against GitHub's
SHA-256 digests, combined SHA256SUMS.txt and legacy sidecars. The Windows package
has 1,781 owned files, an x64 launcher and Python license; Linux has 132 owned
files. Both contain the exact 130 reviewed source files (accounting for Git line
endings), with README PNGs excluded from launcher packages. Latest points to
v0.1.2. Version 0.1.0 and 0.1.1 release targets, asset IDs, sizes and digests are
unchanged. Preserve the released code, tag, branch and assets; this later receipt
on main needs no version bump, private game rebuild or unrelated repeat playtest.

The fix changes configuration, not compiled game implementations or native
selection. Coverage stays 38.4156% linked / 61.5844% outside; game/audio clocks
are unchanged and level-entry stutter remains OPEN. General build reuse remains
planned for 0.2.0. Fresh player evidence is still limited to the pending n0102
checks; automated synthetic checks are not a player save/gameplay acceptance.

## 0.1.0 main-menu close, Audio titles and release branches

This host/product update changes no selected native ranges: all 796 records and
48 exclusions remain, with 324,928 / 845,824 = 38.4156% linked / 61.5844% outside.
Game/audio clocks are unchanged; intermittent Windows level-entry stutter remains
open. The 0.2.0 compilation-reuse and version policy is recorded in DISTRIBUTION.md
and ROADMAP.md; 0.1.0 keeps the existing build-refresh behavior.

Audio's fresh page context prevents the right side of its two-line track value
from being classified as a footer. That screen retains its bottom-left Back
footer. The old 0.0.31 packet fixture fails for the low remix glyphs; the repair
passes with foreground and shadows together. Other screens retain their right
footer and the title preview's world polygons remain outside help tagging.

Main-menu Back uses monotonic time: release resets the hold; three seconds queues
normal SDL quit. The caption sits near the game area's top third and reaches full
brightness during the first second. Its additive foreground and subtractive
shadow fade together, with no position trail or selection gradient. Only the new
caption packet span is recolored, after validation; original menu packets and
blend-state commands stay unchanged. The frame-yielding parent presenter stays
on normal dispatch; a guarded small header helper appends the caption after the
menu's font context is established. Imported fonts/guards remain private.

Tab is masked only for host hold-Turbo polling, including saved Tab bindings.
Other Turbo bindings and ordinary Tab input remain available. Both polling sites
use the original title bridge, with no pinned SDK edits.

All 93 final source tests pass without skips and the 124-file text/CRLF audit
passes. Fixtures cover hold thresholds/cancellation, submenu scope, header ABI,
font initialization, foreground/shadow fade endpoints, original-packet isolation,
normal blend state, and Tab filtering without modifying the input array. Existing
Video, Audio, Controls, title-preview and native-boundary regressions remain.
The actual Dashboard parser accepts ten n0100 checks; all seven prior definitions
and submitted result bytes are unchanged. Its merge test preserves completed
history, blocked notes/timestamps and repeated-import idempotency.

Final real X11/EGL runs use disposable cards and ordinary controller input.
Worker-on checks include the three opening clips, title/attract, Main, a 3.7-second
Back hold on the title screen without closing, a cancelled main-menu hold, and a
fresh full hold ending in clean shutdown. Captures show one stationary caption;
its ten foreground and ten shadow glyphs share the expected positions/colors.
Worker-off checks cycle sixteen Audio track choices, open/close Audio help, resize
through 1600x900, 730x501 and 600x900, return through normal submenu Back, cancel the
hold and close cleanly. Both close runs exit normally about 3.4 seconds after the
script begins the hold, including input pickup and shutdown. The state fixture
checks the close request at exactly three seconds; this is not a hardware timing
benchmark. A physical X11 Tab press is verified registered; it advances 15 frames
in about 0.83 seconds versus 14 in about 0.81 without Tab, with no Turbo observed.
Dummy audio counters are not a physical audio-device or performance measurement.

The release-branch job preserves release/x.y.z at final tested source and refuses
to move an existing branch identifying other code. The 27 retired branch heads
were reviewed as ancestors of main, with no open PRs. Its local dry run checks
creation, idempotency and conflict/open-PR/changed-head/unmerged guards. Actual
cleanup is gated behind successful release publication; tags/history remain.

Normal production is staged with the same execution identity as the diagnostic
build. Its native manifest matches the accepted SHA; diagnostics are OFF, both
Release flags are -O3 -DNDEBUG, the qualification include is empty and comparison/
replay interposition is absent. The separate production-object fixture passes all
three opening movies, analog/fire input and clean SDL_QUIT at frame 4500.
Platform and publication receipts will be recorded on main without moving the
final release branch or replacing published assets.

## 0.0.29 in-game options and independent world raster

This is a product/presentation update, with no new linked game ranges. All 796
native records and 48 exclusions remain unchanged: 324,928 / 845,824 = 38.4156%
linked, 61.5844% outside. Complete imported-function hashes and private entry guards
protect the original menu extensions; other occupants retain dispatch fallback.

All 92 source tests pass without skips. New fixtures cover settings migration,
restart with a moved build directory, malformed preferences, fixed-fullscreen
platform behavior, manual HUD steps, fractional scene size, menu exit fading,
Cross/Confirm and caller-saved argument clobbers around the Audio wrapper.
The submitted dashboard result tail is preserved byte-for-byte; six current
checks include the carried optional Linux check, with historical passes/failures
remaining scoped to their original reports.

The SDK OpenGL oracle passes 331/340 checks at 1x/4x. A private copy using the
actual title renderer adapter passes 343/352 checks. Added synthetic world/UI
checks prove that 50 versus 100 percent changes scene raster sampling, leaves
interface pixels identical and preserves texture/CLUT storage outside the drawn
rectangle. Render queue checks pass 8,843 cases. SDK worker on/off comparisons
at 1x/4x, including dynamic internal-resolution changes, pass. A missing local
libGL development link and missing offscreen environment were corrected for the
worker-only rerun; these were fixture-environment failures, not waived checks.

Real X11/EGL tests use disposable cards and ordinary controller input. Worker-on
and worker-off runs cover all three opening clips, renamed Game Options, Video,
the original Audio controls plus Master, Back/Confirm transitions and persistent
settings. Manual 2X/3X/4X/6X and AUTO, wide/portrait resizes and 50 percent scenes
are inspected. Worker-off first-level play shows movement, firing, scoring,
HUD and help panels. Injected pause inputs did not expose the pause-options
screen in this route, so that screen remains a focused player check.

The virtual X11 display has no window manager and refuses exclusive modes.
The final diagnostic test verifies refusal returns the preference and menu to
the actual mode, emits one error for the request, and permits returning to
windowed. This is not verification of all three modes on Windows or a Linux
window manager; that remains a fresh player check.

The final diagnostic and normal binaries are staged with the pinned shared
stager, including the matching execution sidecars and bundled OpenBIOS/license.
Normal production has diagnostics disabled, both Release flags at -O3 -DNDEBUG,
an empty qualification include and no qualification wrappers or instrumentation.
Its selected source/range manifest matches the qualified diagnostic build.
The separately linked normal controller fixture completes all three native movies,
samples analog input and firing, sends the existing Start inputs and exits cleanly
at frame 4500. Sending Start does not establish that the pause menu was observed.
The normal binary SHA-256 is
33f6edb619ee354eeff378477a9cd82d5a83819dbcca826bfcce9decbd6da42a.
The 123-file reviewed text audit, Windows CRLF size bounds and submitted-result
preservation checks pass. The first platform run caught an obsolete provider-test
expectation: F11 now changes the shared Video preference, rather than calling the
former host video callback. The fixture is updated to verify both requests without
claiming an offscreen fullscreen transition. The corrected fixture passes locally
against the actual provider/SDL/GL objects, including composition, F1/F11, pause,
input capture, Escape and reattach; no production source changed for this repair.
A subsequent Windows MSVC compile found that the project header's former name
collided with the SDK game_options.h through nested include lookup. The project
header is renamed nitrogen_options.h, leaving the SDK declarations unambiguous.
The renamed-header diagnostic repeats the ordinary-controller Video/Confirm and
Audio/Master route; settings persist. The rebuilt normal fixture and actual menu
provider checks pass again. Final platform and publication receipts follow. No claim is made that
intermittent Windows level-entry stutter is fixed, or that simulation/render/audio
clocks are separated.

## 0.0.29 publication

Published code/tag 36ff596c54cf13c7ac48f4ecf789ac41d3f1bae0 passes final main source checks
41395518250, Windows/Linux runtime and renderer checks 41395518219, and portable
package/update/publication checks 41395518236. All required jobs pass, including
both platform preparation/update fixtures and publication. Earlier attempts were
blocked by the obsolete F11 fixture and MSVC header collision described above;
these are corrected, not waived or retried unchanged.

All five actual public release assets are downloaded and audited. Tag, latest,
release target, SHA sidecars and GitHub asset digests match. Windows has 1774
owned files, a verified x64 launcher and Python license; Linux has 125 owned
original-source/launcher files. Both packages contain the same 123 reviewed source
files as the release commit after Git line-ending normalization. The source ZIP
matches both packages. No imported game data, generated game code, prepared game
executable or private captures are distributed.

Windows ZIP SHA-256: c0d70a7a221ba75384696034ca7deceb8d244a3e515a16b4a43193cb946f4fe7.
Linux ZIP SHA-256: 86c70c79ae3e82ecfee45373b0aaadac71511842b82076808589c054a9b9e7d2.

Fresh n0029 Video/Audio/brief-play player checks remain pending. The unresolved
optional Linux check is carried forward; submitted earlier reports retain their
exact contents and version scope. Real desktop modes and the pause-options screen
retain the local-check limits above. Native coverage remains 38.4156% linked /
61.5844% outside; intermittent Windows level-entry stutter remains open. This
publication receipt changes documentation only, with no rebuild, VERSION bump or
replacement of the immutable published assets.

## 0.0.23 saved-game, card and gameplay paths

The accepted 0.0.22 O3 baseline was reproduced with identical guarded manifest
and diagnostic execution identity. All 783 accepted input records and their
order remain intact. The revised strategy ranks larger uncovered call paths;
32 larger N2O seeds plus 12 supporting helpers pass preflight (31,088 input bytes).
The provisional pool is exploratory only. Reduction retains 13 observed roots;
unobserved candidates and all 48 whole-owner exclusions remain unselected.
Fresh reduced generation has matching observed guarded identities and no stale
pool source parts. NEW/boot bindings are unchanged.

Original bounded JSON scripts drive ordinary queued controller inputs, with no
guest memory patches. Default/deep/all-flag queues and captures remain unchanged.
The additional uploaded USA card is fingerprint-checked and used only through
fresh byte copies, without inherited file identity metadata. Reference and candidate
start from the same seed; the original card's SHA-256 remains unchanged.
Actual captures confirm populated slot selection/cancellation, confirmed level-12
loading, slot overwrite on a disposable copy and return to gameplay. The second
saved-slot route loads level 9. The tutorial route includes prompts, ship selection,
high-score/restart and ordinary gameplay. Requested buttons alone do not establish
every action, stage or weapon. Fresh-card
captures confirm setup creation, setup load and overwrite. This extends scenario
coverage without requiring another player campaign or altering valued saves.

The four targeted strict routes and their fail-fast replays completed before an
execution-environment reset. Completion is recorded in Git commit
e53f763331029b59dee7143f99c10dcbbf73830e. Their raw witnesses/captures were omitted
from recovery; counts below retain those observed completed runs, not recreated
per-witness records. Restoration reproduces the saved full diagnostic execution
identity and guarded manifest exactly, with the same GNU 13.3 compiler and both
Release flag sets. The four completed stages are retained. The broad reduced
regression is rerun after restoration against retained accepted RGB/card hashes.

Final reduced O3 routes clear exploratory failure collection, forced blocks,
miss/edge tracing and use only the final identity-qualified selector:

| Final route | Live comparisons | Captured inputs | Exact frames |
| --- | ---: | ---: | ---: |
| loaded | 56 | 26 | 31 |
| saved-slot | 51 | 22 | 34 |
| card-roundtrip | 89 | 57 | 33 |
| second-slot | 44 | 22 | 31 |
| tour | 0 | 0 | 37 |

All 13 retained identities have archived identity-qualified pool observations
(11 direct, 2 through continuations only) at
78 distinct identity/PC pairs. The targeted strict runs passed
fail-fast replay with 25 captured CPU/RAM/scratchpad/GTE variants per input,
without --keep-going: 3,175 passing comparisons. Total is **240 live +
3,175 replay = 3,415, zero failures**. All **166 decoded-RGB
frames match**. All 15 output file comparisons (three per
route, not that many unique cards) match accepted reference bytes.

Isolated bounded comparisons freeze device time; they do not establish all
branches, device/host side effects, campaigns or player systems. Normal production
has diagnostics disabled, an empty qualification include and no comparison/replay/
wrapper link hooks. Normal source/range hashes and coverage match the diagnostic
manifest exactly; C and C++ Release flags remain -O3 -DNDEBUG. The separate normal
movie/controller/pause/quit fixture passes; inspected images confirm presentation.
A restored cached object still carried diagnostic call references during the
normal link. Recompiling that object with the compiler cache disabled removed
those references; the production build continued with the cache disabled.
Framework and generated game sources were unchanged. The completed normal
fixture and source/range checks above use that repaired production binary.
Both reports verify **324,928 / 845,824 = 38.4156% linked**,
**520,896 / 61.5844% outside**, +6,960 emitted bytes.
The metric includes payload data, not CPU time or overall completion.

Source-identity-bound code/data analysis is refreshed with current static and
observed trace hints; hints neither qualify entries nor change the denominator:

| Payload | Linked | Static-code hint | Data hint | Conflict | Unclassified |
| --- | ---: | ---: | ---: | ---: | ---: |
| N2O.EXE | 296,520 | 73,388 | 15,679 | 0 | 73,165 |
| NEW.EXE | 10,500 | 35,752 | 184,128 | 0 | 103,444 |
| SLUS_006.37 | 17,908 | 0 | 677 | 0 | 34,663 |

All 80 source tests, the 99-file reviewed source audit, Windows CRLF 128 KiB text
bounds and diff checks pass. The current dashboard parser/importer accepts fresh
n0023 definitions, preserves both earlier submitted reports byte-for-byte and
leaves new checks untested. Source, Windows/Linux runtime/renderer and portable
package/update CI gate release publication; final receipts and public ZIP audit
are recorded separately below. Submitted 0.0.23 Windows player checks are
accepted in the acceptance note below. No commercial inputs, derived C/guards, compiled game, captures,
witnesses or saves enter Git/releases. Private recovery includes compiler-cache
objects and stays private. USA-only scope and deferred asset/EU/clock work remain.

## 0.0.22 further observed native game/library batch

The user accepts 0.0.21 gameplay and its submitted dashboard n0021 results,
including update/private-build refresh, menus/first-level gameplay, high-score
name selection and startup performance. The historical dip is reported absent;
its suspected save/load cause is not an established diagnosis. The new candidate
keeps all 754 accepted input records semantically identical and in order.
The restored accepted O3 build exactly reproduces its saved execution identity.

The original optional route.py --combat-inputs adds 20-frame Triangle/Circle/
Square presses in rotation alongside ordinary firing in the extended movement
loops, preserving their total frame count and the initial prefix through frame
6100. All 17 prefix frames match retained accepted RGB hashes. The new accepted
reference runs --deep --combat-inputs through frame 36300 with 37 captures.
The other route uses the unchanged --deep schedule and its 37 retained accepted
0.0.21 RGB hashes. Both use fresh test cards, separate from personal saves.
Requested face-button inputs do not prove a specific weapon/action or later level.

Verified source-labelled analysis and observed miss hints propose 421
candidates. Preflight passes 297 and holds 124 before exploration.
NEW still requires a conservative CPU call closure: unresolved indirect transfers,
hardware/exception contexts and closure through native movie control stay out.
The prior reviewed local-switch library helper remains allowed. Source- and
body-hash-bound review additionally admits low-confidence CPU leaves only when
the analyzed bodies end with returns, contain no unresolved indirect/external direct transfer,
keep conditional branches inside the reviewed function and contain no detected
hardware/exception/GTE context. This makes specific small non-prologue library
leaves eligible for discovery and caller-closure analysis; it does not qualify
them. Non-leaf low-confidence callees still require the previous evidence.
Reviewing local switch geometry never overrides a failed-owner exclusion: NEW
0x8002A44C..0x8002A9A8 stays held by its earlier complete-input failure. NEW call
closure also rejects every intersecting failed-owner interval. All other
unresolved indirect sites remain rejected.
New boot code and movie-control callers retain fallback. Preserve the complete
48 whole-owner exclusion list, including any newly failed whole inputs.

The exploratory pool receives no extra credit. Reduction retains 29 observed
roots (8 N2O/21 NEW); failed/unobserved candidates stay unselected. Final
regeneration uses a fresh private source directory and omits stale pool parts.
Reduced guarded identities match their observed pool identities. Both Release
flag sets remain -O3 -DNDEBUG. Final strict routes clear exploratory collection,
forced blocks, miss tracing and edge options:

| Final route | Live comparisons | Captured inputs | Exact frames |
| --- | ---: | ---: | ---: |
| combat | 90 | 35 | 37 |
| deep | 73 | 27 | 37 |

All 29 identities were observed (29 at owner entry, 0
continuation-only), across 35 distinct identity/PC pairs. Fresh
fail-fast replay with the final O3 binary uses 25 original input/GTE variants per
captured input, without --keep-going: 1,550 comparisons. Live plus replay is
**1,713 comparisons, zero failures**. The 74 exact frame checks all pass:
both routes match retained accepted decoded-RGB SHA-256 records after the
execution reset. All 3 fresh-card files from the
combat route match the retained accepted fresh-card file SHA-256 records.

These isolated CPU/RAM/scratchpad/GTE comparisons freeze device time. They do not
prove every branch, device/host side effect, compiler, player or campaign. Normal
production source/range hashes match the final diagnostic manifest exactly; both
reports agree on 317,968 / 845,824 = **37.5927% linked**,
527,856 / **62.4073% outside**, +3,496 emitted bytes.
N2O: 289,560 bytes/63.1191%, 632 roots and
10,855 aliases. NEW: 10,500 bytes/3.1454%,
152 roots and 300 aliases. Boot remains 17,908 bytes/
86 functions. Aliases earn no duplicate credit and data stays in the denominator.
This is not overall completion or CPU time. Input bands total 3,520 bytes.

The normal cache has diagnostics OFF and an empty qualification include. Its link
contains no comparison/replay objects or --wrap interposition. Execution identity:
b42738b02a9015dfe23f695c343d0b792be0dfccea25d499fc38784fd5b3a162. The separate normal controller fixture completes
all three native movies, samples analog movement/firing, checks pause/resume and
exits through SDL_QUIT; its two private gameplay captures were inspected. Dummy
and offscreen device observations do not establish physical audio quality or
sustained Windows FPS. Submitted Windows 0.0.22 checks are accepted below.
No repeated campaign, new upload or valued-save overwrite is requested.

The 80 local source tests and 99-file reviewed source audit pass, including the
unchanged 128 KiB Windows CRLF bounds. The actual dashboard parser/import preview
accepts the new n0022 definition, preserves all four n0021 statuses/notes/timestamps
and starts new checks untested. The submitted result block remains byte-identical.
TESTING.md keeps one strict test-dashboard block, stable project id nitrogen and
the result markers. No result is automatically submitted. Windows/Linux source,
runtime/renderer and portable startup/preparation/update checks gate publication.

The restored private compiler cache reduces unchanged recompilation with normal
compiler-content/source/flag checks intact. It contains compiled game objects;
keep it out of Git/releases. Public source is original reviewed text only. The
private code/data inventory retains source identity and separates hints from
linked credit:

| Payload | Linked | Static-code hint | Data hint | Conflict | Unclassified |
| --- | ---: | ---: | ---: | ---: | ---: |
| N2O.EXE | 289,560 | 80,348 | 15,679 | 0 | 73,165 |
| NEW.EXE | 10,500 | 35,752 | 184,128 | 0 | 103,444 |
| SLUS_006.37 | 17,908 | 0 | 677 | 0 | 34,663 |

USA is still the sole supported input. Runtime still reads the original disc;
folder-backed assets, mod packs, optional user-owned EU language assets, EU support
and logic/render clock separation remain separate future work. No commercial
bytes, generated game C/guards, compiled game, media, witnesses or saves enter
Git or public release packages.

## 0.0.21 native game/library batch

The user reports 0.0.20 still plays with no issues noticed. Its Windows route
is accepted without inferring another campaign or save/reload operation. This
batch uses the unchanged accepted 728-band binding as reference. Recovery reused
the existing verified USA disc and restored current source after a snapshot
rollback. The rebuilt reference matches the saved 0.0.20 execution identity.

The optional original route.py --deep extends the existing input prefix through
frame 36300, with 37 captures and a bounded 1200-second default. Old modes retain
their schedules. The new reference's first 25 decoded RGB hashes equal the saved
accepted 0.0.20 hashes. Later captures include high-score name entry and a return
to gameplay; they do not establish later campaign levels. The alternate route
uses the unchanged --long --alternate-ship --alternate-difficulty schedule and
25 retained accepted-reference RGB hashes. A difficulty-input flag does not
prove an actual changed menu difficulty.

Source-labelled analysis and observed misses proposed 369 candidates.
Preflight passed 225 and held 144 before exploration. Conservative NEW
call closure continues to reject unresolved indirect calls, hardware/exception
contexts and any closure through the native movie loop. A reviewed CPU library
leaf at NEW 0x80028A5C..0x80028DD8 has two statically resolved local jump tables;
only those known JR sites may pass the previous blanket indirect rejection.
Every target is aligned and inside that function. This is a discovery condition,
not qualification credit. Curated early CPU helpers still require verified bytes,
emitter/resume geometry and final runtime comparison. Movie-control callers and
new boot code retain fallback. Whole failed-owner exclusions are preserved.

The exploratory pool is not counted. The final reduction retains 26 observed
roots (22 N2O/4 NEW). All 728 prior records remain semantically identical and
in order. Regeneration uses a fresh private source directory; stale pool parts
are absent. Reduced guarded identities match the observed pool identities.
Both C/C++ Release flags are -O3 -DNDEBUG. Final runs clear collection, forced
blocks, miss tracing and edge options:

| Final route | Live comparisons | Captured inputs | Exact frames |
| --- | ---: | ---: | ---: |
| deep | 87 | 32 | 37 |
| alternate | 19 | 7 | 25 |

All 26 guarded identities were observed: 26 at owner entry and
0 through a continuation only. There are 32 distinct identity/PC
pairs across both routes. Fresh fail-fast replay uses the final O3 binary and
25 original input/GTE variants per captured input, without --keep-going:
975 replay comparisons. Final live plus replay is **1,081 comparisons,
zero failures**. Deep frames are compared as decoded RGB bytes; alternate
frames match the retained decoded-RGB SHA-256 records. All 62 checks pass.
All 3 fresh-card files from the strict deep route equal the accepted
reference byte-for-byte. They are test cards, separate from personal saves.
These bounded CPU/RAM/scratchpad/GTE comparisons freeze device time and do not
establish every branch, host/device side effect, compiler, player or campaign.

The 26 input bands total 7,020 bytes. Diagnostic and normal builds
agree on 314,472 / 845,824 = **37.1794% linked**, with
531,352 / **62.8206% outside**; +6,304 emitted bytes over
0.0.20. N2O: 287,928 / 458,752 = 62.7633%,
624 roots/10,780 aliases. NEW: 8,636 /
333,824 = 2.5870%, 131 roots/266 aliases. Boot
remains 17,908 bytes/86 functions. Aliases earn no duplicate byte credit; payload
data stays in the denominator. These are not overall completion or CPU shares.

Normal source/range hashes match the final diagnostic manifest exactly. The
cache has diagnostics OFF and an empty qualification include. The player link
has no comparison/replay objects or --wrap interposition. Its execution identity
is 204c40aab2cfba7a6143b938aff5d39bd437041438247a7414ecf25bf647ffd9.
The separate normal fixture completes all three native movies, samples analog
movement/fire, exercises pause/resume and exits via SDL_QUIT. Its two private
gameplay images were inspected. Dummy audio/offscreen fixtures do not measure
physical audio quality or sustained Windows FPS. The focused Windows 0.0.21
player check is pending; no repeated campaign, new input or valued-save overwrite
is requested. Previous player reports retain their version scope.

The framework's existing compiler-cache launcher is enabled privately. Cache keys
retain compiler-content, source and flag checks; no sloppiness is enabled. Cache
hits reduce identical compilation but never qualify game code. The private
recovery archive includes compiled game objects and must stay out of Git/releases.
Public source inventory is 99 original text files with the unchanged 128 KiB
bound; validation history was split into its linked archive to retain that bound.
All 80 local source tests and the reviewed source audit pass. Windows/Linux
runtime/source and portable package/startup/update checks gate publication.

The verified private code/data inventory keeps hints separate from linked credit:

| Payload | Linked | Static-code hint | Data hint | Conflict | Unclassified |
| --- | ---: | ---: | ---: | ---: | ---: |
| N2O.EXE | 287,928 | 81,900 | 15,679 | 0 | 73,245 |
| NEW.EXE | 8,636 | 36,284 | 184,128 | 0 | 104,776 |
| SLUS_006.37 | 17,908 | 0 | 677 | 0 | 34,663 |

USA remains the only supported input. EU comparison/support is deferred; optional
language import can be investigated after folder-backed runtime assets exist.
The game still reads the original disc. Asset extraction, mod packs and deferred
logic/render clock separation are separate work. No commercial files, derived C,
instruction guards, compiled game, media, witnesses or saves enter Git/releases.


## Published 0.0.21 release receipts

Release commit: 891f1a2d47ea7a69843ce679f61335277867d363. All required jobs succeeded:

- Source checks: [41159267588](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41159267588), Windows and Linux.
- Runtime and renderer checks: [41159267620](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41159267620), Windows and Linux.
- Portable Windows launcher: [41159267649](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41159267649), packaging, extracted startup, actual bundled runtime tools, copied-process update/restart and gated publication.

The actual [public release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.21) assets were downloaded and audited.
Latest release and tag resolve to this release commit; published asset digests,
lengths and the standalone Windows checksum agree. The extracted owned-file
manifest verifies all 1,750 files. The launcher is x64 PE and portable
Python's license is present. There is no .local directory or private game payload.
The 99 app source files match this release checkout after Git newline
normalization, and the source ZIP entries match the packaged app byte-for-byte.

| Published asset | Bytes | SHA-256 |
| --- | ---: | --- |
| Nitrogen-Squared-source.zip | 281,863 | `23acf8858334a1a7f90eb7383d37051ad3734846115cca2c08e9cac5acfac8a3` |
| Nitrogen-Squared-Windows-x64.zip | 14,864,246 | `24765ec7dcd10e956203427084b7bbe41f9a6a98e0b1aba1a76463b390100525` |
| Nitrogen-Squared-Windows-x64.zip.sha256 | 100 | `0b309720c7c18aaea2f1e0c325f046dd225cfe51b8a7629f79df9f96a57fa64e` |

This subsequent receipt update is documentation only. Preserve the published
0.0.21 assets/tag; no VERSION bump, runtime rebuild or repeat player check is
needed for this receipt. Focused Windows player acceptance remains pending.


## 0.0.21 reported Windows/dashboard acceptance

The user completed the gameplay check and reports the same behavior as before,
with no issues noticed. The submitted version n0021 dashboard report records
passes for launcher update/private build refresh, menus/first-level gameplay,
high-score name selection and startup performance. Preserve its result markers,
notes and timestamps exactly. The startup note reports the historical dip has
been absent for several updates and suspects native save/load; this is a player
observation, not a confirmed causal diagnosis or precise FPS measurement.

Accept that reported route without inferring a new level-9 campaign or save/reload
operation. No runtime rebuild, VERSION bump or repeated check is needed for this
acceptance note. Coverage remains 314,472 / 845,824 = 37.1794% linked, 62.8206%
outside. Future release definitions must use their own version ID and start
untested; earlier passes remain evidence only for their recorded version.


## Historical 0.0.22 interruption — superseded by final qualification above

Execution access was lost during the second fresh strict route. The prepared
29-root candidate is unqualified for release; public production remains the
accepted 0.0.21 binding at 37.1794% linked. Its original qualification tooling
and newly discovered failed-owner exclusion are preserved for continuation.

The private reduced O3 candidate has 8 N2O and 21 NEW additions, preserving all
754 prior records. It adds 3,496 emitted bytes to reach a provisional 317,968 /
845,824 = 37.5927% linked / 62.4073% outside. One exploratory N2O input failed
a bounded GPR/RAM comparison and is held as a whole input. All 48 held intervals
are absent from the reduced emitted guards. Exploration matched all 74 frames.

The reduced binary passed 1,550 preliminary captured-input/GTE replay cases.
Its first fresh strict route completed 90 comparisons with zero failures,
37 identical RGB frames and three identical fresh test-card files. The second
strict route was observed through frame 12000 with 64 passing comparisons;
completion is unverified. Fresh final replay, normal-production/source/CI/package
and eventual Windows player checks remain pending. AGENTS.md records the exact
remaining steps and private recovery procedure.

The user's 0.0.21 gameplay and four submitted dashboard checks are accepted.
Keep those results by version; eventual n0022 definitions start fresh. This
checkpoint retains the accepted production binding and VERSION, and preserves
the original controller tool plus failed-input metadata. It publishes no
commercial data, generated game bodies, guards, compiled game or private files.


## Published 0.0.22 release receipts

Release commit: 51d6a71be26e1ebc88ac0d7cd017a9bf77b01485. Required workflows and all their jobs succeeded:

- Source checks: [41229625471](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41229625471), successful.
- Runtime and renderer checks: [41229625432](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41229625432), successful.
- Portable Windows launcher: [41229625466](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41229625466), successful.

The portable job confirms version 0.0.22, Asset folders tools and an actual
copied-process update/restart with private cache and test saves preserved.
The actual [public release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.22) assets were downloaded and audited.
Latest release and tag resolve to this code commit. All lengths, published
digests and the standalone Windows checksum agree. The extracted owned-file
manifest verifies 1,750 files. The launcher is x64 PE and portable
Python's license is present. There is no .local directory or private game payload.
The 99 app source files match the release checkout after Git newline
normalization; source ZIP entries match the packaged app byte-for-byte.

| Published asset | Bytes | SHA-256 |
| --- | ---: | --- |
| Nitrogen-Squared-source.zip | 291,472 | `6a4a536bf42a5022ffac4178985cf2a28db57ae2472fdc4d9f82ff6ccd804438` |
| Nitrogen-Squared-Windows-x64.zip | 14,871,830 | `6c9e7ceb1ca068f406ca1e29eb6c15b6accd1555d4ecdd1e6e6bcf1cc28508d0` |
| Nitrogen-Squared-Windows-x64.zip.sha256 | 100 | `cc052023eed8b9401c88249b4e3e83544c5bb0bc1296b8ee71d70f2b28887c84` |

This following receipt update is documentation only. Preserve the published
assets/tag; it needs no VERSION bump, rebuild or repeat player check.
The subsequent 0.0.22 acceptance note below supersedes pending Windows status.
Dashboard result markers/notes/timestamps remain preserved by version.


## 0.0.22 reported Windows/dashboard acceptance

The user submitted results in main commit a6183f1b4c594ea5de166436f8f195c70ba94882.
All three checks for v0.0.22 (`nitrogen:n0022`) are marked pass:

- N2-UPDATE: launcher update and private-build refresh.
- N2-PLAY: opening movies/audio-video, menus and short gameplay with the defined
  movement/firing, usual face-button actions, pause/resume and normal quit scope.
- N2-SCORE: readable and usable high-score name-selection display.

Accept the reported Windows route without inferring a new campaign, save/reload
operation, every weapon/action, physical performance measurement or exhaustive
branch coverage. The submitted report has no additional notes. Preserve both
n0021 and n0022 submitted results/notes/timestamps and the exact result markers.
The dashboard importer retains all seven earlier/current check results while
updating definition prose; project/version/check IDs remain unchanged.

This acceptance is documentation only: VERSION remains 0.0.22, published assets
and tag remain unchanged, and no rebuild or repeat player check is needed.
Linked coverage remains 317,968 / 845,824 = 37.5927%, with 62.4073% outside.
Future runtime releases require fresh version-scoped checks.

## Published 0.0.23 release receipts
Release code [08f42bf](https://github.com/TheEelYT/Nitrogen-Squared/commit/08f42bff99ac548026063a68429335ed944b519c) passes all required workflows:
- [Source checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41250851616): passed.
- [Portable Windows launcher](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41250851730): passed.
- [Runtime and renderer checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41250851661): passed.

The portable job verifies version 0.0.23, the Asset folders interface, bundled
preparation/runtime tools and an actual copied-process update/restart preserving
private files and saves (`PORTABLE_SELF_UPDATE_PASS`). The published
[Windows release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.23) was downloaded and audited: all three assets,
checksums/digests, 1,750-file owned manifest, 99-file source inventory,
x64 launcher PE and portable Python license pass. Source contents match the
release commit after Git line-ending normalization; no private game payload is
included. Windows ZIP SHA-256: `fb8cc48d13593fdde8933192a3270f4305d9f8fe3979a3301b6fdd200a2e73b4`.

This receipt is documentation only. Preserve the published tag/assets; no VERSION
bump, rebuild or repeat local qualification is needed. Fresh n0023 Windows player
checks remain pending; earlier n0021/n0022 reports retain their version scope.

## 0.0.23 reported Windows/dashboard acceptance

The user submitted project-lab results in main commit
[a1c8300](https://github.com/TheEelYT/Nitrogen-Squared/commit/a1c83008b716cf8ea866dd58e648964934f138e6).
All three v0.0.23 (`nitrogen:n0023`) checks pass:

- N2-UPDATE: launcher update and private-build refresh.
- N2-PLAY: opening playback, menus and short gameplay with the defined
  movement/firing/face-button, pause/resume and normal-quit scope.
- N2-LOAD: familiar existing saved-slot load and brief gameplay.

Accept that reported Windows route, superseding pending 0.0.23 player status
above. The report does not establish a new campaign, deliberate saved-slot
write/overwrite, every branch or exact FPS. No repeat testing, reimport, upload
or valued-save overwrite is requested. Preserve .local and existing saves.
All three submitted version reports, notes, timestamps and result markers remain
byte-for-byte unchanged. Definition project/version/check IDs and check steps/
expected results remain stable so reimport preserves the recorded results.

This is documentation only. VERSION remains 0.0.23; preserve the release tag and
assets. No rebuild or repeated native qualification is needed. Coverage remains
324,928 / 845,824 = 38.4156% linked / 61.5844% outside.

## Project Lab submission build triggers

Source, runtime/renderer and portable workflows now ignore TESTING.md-only
pushes. A Project Lab results submission creates such a commit,
so it no longer starts the build/package jobs. Any additional changed file,
including source/config/workflows, continues to trigger all three. Pull-request
checks and manual portable workflow_dispatch are unchanged. The filters match across the release-gating
workflows so ordinary code releases keep their full required check set. This
changes CI triggers only; game coverage, VERSION and published assets are unchanged.


## 0.0.24 window presentation

This host-only update preserves the accepted 0.0.23 native selection: 796 input
records, all 48 exclusions, 324,928 / 845,824 bytes = 38.4156% linked /
61.5844% outside. Earlier native comparisons are history, not new display evidence.

Private-copy GPU/GTE/renderer/main adapters implement window-driven aspect and
internal resolution, integer interface plateaus and nearest texture/movie/present
sampling. UI flags include complete title font palettes, bounded weapon model,
frame and actual polyline endpoints. The worker replays captured primitive flags
without consulting live GPU packet state. Line quads transform after expansion.
The verified weapon projection viewport retains its widget proportions.

Real X11/EGL qualification covers eight menu sizes (320x240, 480x360, 608x456,
640x480, 800x600, 960x720, 1280x720 and 600x800), ordinary menu/controller inputs,
first-level firing/gameplay and live landscape/portrait resizes. Native-wide-only
exploration revealed tunnel-edge culling gaps. The final implementation uses the
toolkit's wider projection within the original viewport; the tested route no
longer has those gaps. Unprojected menu ray sprites use a bounded, dedicated-bank
uniform cover transform. Portrait world rendering crops an authentic 4:3 view.
Movies retain their authored framing, and the desktop menu reserves its own area.

The worker-on route passes. Worker-off gameplay, portrait/wide movies and visible
menu inset passed with the same gameplay transform; the final menu-backdrop
refinement also passes its separate eight-size worker-off check. All 83 source tests pass,
including compiled geometry/classifier fixtures and fail-closed pinned adapters.
The movie screenshot's 76,800 source-texel groups have zero inconsistent output
pixels under the pinned nearest/half-texel mapping. A preliminary exact-3x3-block
assumption was invalid because of the UV inset and is not counted as evidence.

SDL 3.4.10's offscreen resize does not reallocate its EGL pbuffer. Initial
oversized captures are invalid resize evidence; the real-window runs replace them.
Nearest sampling can still have pixel-phase differences at fractional sizes.
The sharpness policy initializes post-process AA once per window, avoiding a
per-frame renderer-ownership query. Simulation and video/audio clocks are unchanged. The original fixed-aspect build
option is retained. The normal diagnostics-OFF build uses C/CXX -O3 -DNDEBUG with an empty
qualification include, no interposition and no temporary instrumentation. Its
source/range manifest matches the accepted selection. The three-movie/analog/
firing/pause/quit fixture passes through frame 4500; private gameplay captures
were inspected. All 83 source tests pass without skips; the 106-file source
audit, Windows CRLF bounds and actual dashboard import preview pass. Platform/
package and publication checks remain pending until their receipts are recorded. Fresh n0024 player checks do
not inherit earlier passes; all submitted n0021/n0022/n0023 reports are preserved.


## 0.0.24 publication receipt

Published code [6299190](https://github.com/TheEelYT/Nitrogen-Squared/commit/629919092801b45dae27d3787b59a81b1506f0b0) passes all required main workflows: 41282459215, 41282459204, 41282459250. Source checks, actual Windows/Linux synthetic runtime/renderer execution, portable Windows launcher/toolchain and copied-update preservation checks pass.

The [0.0.24 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.24) was downloaded and audited: all three assets, checksum/digests, 1,757-file owned manifest, x64 launcher, portable Python license and 106-file source inventory pass. Source contents match the release commit after Git line-ending normalization; no private game payload is included. Windows ZIP SHA-256: `053a1f3c8786636c31fe3004ad187c41e42118652aca56fc3b64ac174454daf7`.

This receipt is documentation only. Preserve the published tag/assets; no VERSION bump or rebuild is needed. Fresh n0024 Windows display/update/sharpness checks remain pending. Earlier n0021/n0022/n0023 submissions retain their versions and exact contents. Native coverage remains 38.4156% linked / 61.5844% outside.


## 0.0.24 player-reported presentation regressions

The user reports split attract/menu sentences, widescreen UI squashing, bonus
weapon/shield icon mismatches, a broken help popup and level-end text layout.
These reports supersede the earlier limited local acceptance for those areas.
Prior source/platform/package receipts remain valid for their stated scope;
they did not establish correctness of all menu/help/bonus screens. Preserve the
published release and all submitted version-scoped dashboard reports.

## 0.0.25 UI repair qualification

The owner additionally requests a 2x UI floor and square-pixel output. The new
365x240 step reference applies to the usable drawable game area. Shared UI roles
replace per-glyph edge thresholds. Opaque numeric HUD packets distinguish the
score stack from semi-transparent menu sentences sharing its font palette.
Observed bonus icon/count palettes join the weapon panel; menu artwork, footer
particles, popup fills, borders and text receive coherent roles. The ray field
uses a separate cover transform. Actual scanout height travels with each record,
and the game-view predicate no longer requires exactly 238 lines.

Nearest presentation removes its half-texel zoom; UI vertices compensate native
raster bias and snap anchors to physical pixels. The internal raster covers the
actual scanout/output dimensions. A real-X11/EGL capture check finds 392 bright
score-font blocks per view, with zero inconsistent RGB blocks, at 800x600,
2048x960, 900x1000 and 1280x720: 2x/3x/2x/2x with the 21-pixel desktop menu.
The first mask check omitted that menu offset and is not credited.

Expanded ordinary-input discovery reproduced the old split phrases and reached
menus, help, gameplay, weapon pickups, level completion and name entry. The shared
phrase-role logic was retained through the later pixel-alignment refinements.
Focused gameplay captures confirm the shield icon and count now join the weapon
panel; packet fixtures cover the observed bonus-icon/count family and exclude
unrelated world sprites. This is focused coverage, not every possible UI branch.

Final real-X11/EGL worker-on and worker-off popup captures verify text, button
icons, translucent fill, gradient border and separator as one layout. Additional
window boundaries verify 1094x720 game area at 2x, 1095x720 at 3x and 1095x719
back at 2x. The opening movie has 21,610 nonblack source blocks with zero
inconsistent 3x3 RGB blocks in the sampled 960x720 picture. Portrait framing is
also inspected. UI never drops below 2x; very small windows can crop it.

Final normal diagnostics-OFF production uses both C/CXX -O3 -DNDEBUG, an empty
qualification include, no interposition and no temporary line instrumentation.
Its source/range manifest matches the accepted native selection. The separate
normal movie/analog/firing/pause/quit fixture passes through frame 4500, and its
private gameplay captures were inspected. All 83 source tests pass without skips;
the 106-file source audit, CRLF bounds and actual dashboard preview pass. All
three submitted earlier reports remain byte-identical and n0025 starts fresh.
The uploaded card remains unchanged; tests use disposable copies or fresh cards.

Native inputs, all exclusions and coverage remain unchanged. No new native-
comparison credit is claimed for this host-only update. Windows/Linux CI,
portable package checks and actual public-asset audit gate final publication;
their receipts are recorded separately when complete.

## 0.0.25 publication receipt

Published code [5b15c84](https://github.com/TheEelYT/Nitrogen-Squared/commit/5b15c8466be50a0b2cc2be3a95121fc4533e91bb) passes every required main workflow:

- [Source checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41290793754): Windows and Linux passed.
- [Runtime and renderer checks](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41290793790): actual Windows and Linux synthetic runtime execution passed.
- [Portable Windows launcher](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41290793802): package, startup/toolchain, copied-update preservation and gated publication passed.

The [0.0.25 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.25) was downloaded and audited. All three assets, tag/latest target, checksums and digests pass. The Windows package has the expected 1,757-file owned manifest, x64 launcher and portable Python license. Its 106 source files match the release commit after Git line-ending normalization and match the separate source ZIP byte-for-byte. No private game payload is included. Windows ZIP SHA-256: `aa361596ac4eae269ee5aaeb8dd8d4b8fe108f1c798199733f95a0fd11ac474f`.

This supersedes pending platform/publication status above. This receipt changes documentation only; retain the published tag/assets without a VERSION bump or rebuild. Fresh n0025 Windows UI/update checks remain pending. All earlier submitted dashboard results retain their versions and exact contents. Native coverage stays 38.4156% linked / 61.5844% outside.

## 0.0.26 complete UI layers and perk icons

The owner reports remaining 0.0.25 failures in title/selection backing,
square-button outlines, pulsing footer rings, pause-menu shadows and partial
words, shield/firewall placement, and the high-score title/save prompt. These
reports supersede limited local 0.0.25 screen checks; published assets remain
unchanged.

Explicit HUD atlas cells replace the broad opaque-font position rule, keeping
menu titles, button outlines and pause shadows with their text. Selected-menu
backing and complete footer rings share their controls' transforms. The actual
shield/firewall sprite palettes and all weapon-upgrade flash frames use the
weapon-panel role alongside counts. World and lens-flare exclusions remain.
The 2x floor, square pixels, 365x240 reference and clocks are unchanged.

Final real X11/EGL captures with the render worker on and off cover main, ship
and level menus, help and pause options/quit/help toggles in wide and portrait
windows. The title plate, selected backing, square glyph/outline, full pulse
rings and text/shadows remain together. Controlled disposable inventory counts
exercise the original shield/firewall packet builder at 2x/3x/4x; both real icons
and counters follow the panel. A disposable score/life fixture reaches the
high-score entry/table; after its entrance animation all eight rows, title plate
and save-prompt square are coherent in wide and portrait views. These fixtures
verify presentation, not natural pickup/game-over acquisition or native behavior.
The supplied original card remains unchanged. Four final captures each contain
392 bright score-font blocks with zero inconsistent RGB blocks, at 4x/2x/3x/2x.

All 83 source tests pass without skips, the reviewed 106-file source audit and
CRLF text bounds pass. The actual dashboard parser/importer preserves all three
reports and ten submitted checks; five fresh n0026 checks remain untested.
The separate normal movie/controller fixture passes through frame 4500 with
three completed opening movies, both analog directions, fire, pause/resume and
SDL quit. Normal source/range hashes match the retained manifest and execution
implementations match the diagnostic build. Diagnostics are OFF, both Release
flags are -O3 -DNDEBUG, the qualification include is empty and production has no
comparison/replay/wrapper hooks. Windows/Linux platform and actual public-package
checks gate publication; their final receipts follow separately. No native
selection or comparison credit is claimed: 324,928 / 845,824 = 38.4156% linked,
61.5844% outside. Focused Windows player checks remain pending.

## Published 0.0.26 receipts

Immutable code/tag: `636e02058efc48f36644ffb39e62717847b35f1b`.
All main push gates pass: [source checks 41325695833](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41325695833),
[Windows/Linux runtime and renderer checks 41325696001](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41325696001),
and [portable launcher/preparation/update/publication 41325695818](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41325695818).
This supersedes pending platform/publication status above.

The actual [0.0.26 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.26)
was downloaded and audited. Tag/latest target, all three assets, checksums and
published digests pass. The Windows ZIP has the expected 1,757-file owned
manifest, x64 launcher and portable Python license. Its 106 source files match
the immutable code commit after Git line-ending normalization and match the
separate source ZIP byte-for-byte. No private game payload is included.
Windows ZIP SHA-256:
`8dc13d47c693f99c0809fcdf4185cac31dfc1961b47b39c19539b687f5599429`.

This receipt is documentation only: VERSION stays 0.0.26, with no rebuild, tag
replacement or asset overwrite. Fresh n0026 Windows player checks remain pending;
all submitted reports retain their versions and contents. Native coverage remains
38.4156% linked / 61.5844% outside.

## 0.0.27 password, animated HUD and interpreter overhead

The owner reports split password/code text and a final button beside Start,
an incorrectly scaled active shield ring and red boost fill, and a pause when
the playable tunnel first appears after Start. Audio/logic separation remains
deferred; performance work targets CPU overhead rather than an audio workaround.

Copied-card baseline captures reproduce the password failure on the loaded
level-12 menu. Label/shadows use rows 202/204, buttons 203 and actual footer
plates start at 205. The repaired row stays centred. The active shield's observed
OT-440 shaded polyline uses live streaming state, since the command buffer holds
a stale prior packet. Bounded boost-fill palette 7667 joins the weapon panel.
Real X11/EGL worker-on and worker-off views cover 2x/3x/4x and portrait, with all eight password
buttons together and shield ring/observed red segments aligned. A disposable
inventory fixture activates the original shield builder; this is presentation
proof, not a natural-pickup claim. A separate 240-consecutive-frame boost capture
includes the peak red highlight aligned inside its gauge backing.

Normal-build profiling found unconditional resident-occupant enrichment inside
external interpreted entries. It scans the 16,384-slot cache solely to populate
debug-server per-PC fields. An original build-time include wrapper skips that
lookup only with debug tools disabled. Entry/caller counters and every actual
native residency guard remain. Diagnostics retain enrichment; REFERENCE uses
the original pinned interpreter. Exact source SHA rejects upstream drift and a
separate implementation family records the selected code in execution identity.
The framework checkout remains unmodified. The source guard hashes CMake-read
text so unchanged LF and CRLF Git checkouts are equivalent; a complete-adapter
synthetic test accepts both and rejects a changed instruction token.

A separately linked pass-through timing fixture measures the current UI build
before/after this change. Across frames 1800–4400, main-thread CPU time is
43,099.319 ms before and 36,834.876 ms after (14.53% lower in this sample).
The prior lookup accounts for 7,069.256 ms across 248,583 calls; afterward there
are zero such calls. Entry-window frames 2390–2700 measure 7,322.132 versus
4,775.946 ms. Steady-play total varies (20,607.342 versus 20,863.812 ms), so this
is not a general FPS or repeatable steady-speed claim. Two captured frames and
all three fresh-card files are byte-identical. Three opening movies, analog in
both directions, fire, pause/resume and normal quit pass. The production binary
contains no fixture wrappers; timing/controller interposition is separately
linked and kept private.

The reported half-second Windows stall was not reproduced in a passive ordinary-
keyboard normal 0.0.26 trace: its first-tunnel maximum was 96.382 ms. One diagnostic
run had an 824.7 ms gap, but a repeat did not and enabled diagnostic GPU timers
prevent production attribution. These measurements establish removable CPU work,
not the cause or complete resolution of the user's Windows symptom. Fresh
n0027 level-entry feedback remains required; clocks/audio are unchanged.

All 85 source tests pass without skips; the 109-file audit, Windows CRLF bounds
and dashboard import preview pass. Four fresh n0027 checks start untested, while
three reports and ten submitted checks remain unchanged. The normal build has
diagnostics OFF, both Release flags -O3 -DNDEBUG, an empty qualification include
and no comparison/replay/controller/timing wrappers. Native manifest SHA matches
0.0.26 exactly. Final diagnostic and normal implementation identities match;
the three game/movie/batching families and shared contract are unchanged.
Final real-window diagnostic smoke also checks the password and shield ring
with the new attribution family present. Platform and actual public-package
checks gate publication; receipts follow separately.

Selection stays at 796 input records and all 48 exclusions:
324,928 / 845,824 = 38.4156% linked, 61.5844% outside. No new native comparison
or coverage credit is claimed. Earlier dashboard reports remain byte-identical.

## Published 0.0.27 receipts

Immutable code/tag: `8845feda8c363808dac8caf88aa6eae105168383`.
All final main-push gates pass:
[Portable Windows launcher 41353424424](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41353424424),
[Runtime and renderer checks 41353424506](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41353424506),
[Source checks 41353424419](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41353424419).
The earlier unpublished integration attempt rejected Windows CRLF checkouts in
the new source guard; the corrected guard and its LF/CRLF/change regression
supersede that failed attempt. No earlier 0.0.27 asset was published or replaced.

The actual [0.0.27 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.27)
was downloaded and audited. Tag/latest target, all three assets, checksums and
published digests pass. The Windows ZIP has 1760 owned files, an x64
launcher and portable Python license. Its 109 source files match immutable
code after Git line-ending normalization and match the separate source ZIP
byte-for-byte. No private game payload is included. Windows ZIP SHA-256:
`c0824e54504e3b5802e2810084088258554add02261a68acb76b3dfacd3227a7`.

Final normal and diagnostic builds share the refreshed implementation identity.
The final normal ordinary-keyboard smoke reaches gameplay and quits normally;
production has no qualification wrappers. This receipt changes documentation
only; preserve the published tag/assets, with no VERSION bump or rebuild.
Fresh n0027 Windows UI and level-entry feedback remain pending. Removal of
measured CPU overhead is verified; complete resolution of the reported
half-second Windows hitch is not yet confirmed. Audio/game clocks and native
coverage remain unchanged at 38.4156% linked / 61.5844% outside. Earlier dashboard
reports retain their versions and exact contents.

## 0.0.28 bonus HUD and Linux launcher qualification

The user reports the other UI failures fixed in 0.0.27 and identifies two more:
bonus stars after the sixth move toward the centre, and the bonus speed display
separates from the bottom-left HUD. Accept the reported UI scope; the earlier
Windows level-entry hitch is not explicitly confirmed resolved.

The star atlas cell now uses the score anchor regardless of its source x.
The bonus LCD's exact digit and backing cells use the weapon-panel role, with
bounds and draw rank retained; menu art sharing those palettes remains centred.
An original compiled regression checks extended star positions, all ten LCD digit
cells, the backing and unrelated menu/world exclusions. A disposable copied-card
fixture renders twelve stars and a four-digit LCD through the original packet
builders. Real X11/EGL worker-on and worker-off captures at 2x/3x/4x and portrait show one star
row and the complete LCD aligned with its panel. This controlled presentation
fixture is not a natural bonus-stage acquisition or native-comparison claim.
The final normal movie/controller fixture passes through frame 4500, including
both analog directions, firing, pause/resume and quit. Two captured RGB frames
and all three fresh-card files match 0.0.27 exactly. Normal diagnostics are OFF,
both Release flags are -O3 -DNDEBUG, the qualification include is empty and
production contains no fixture wrappers. Diagnostic/normal implementation
identities match; retained native manifest SHA and the game/movie/batching/
attribution families and shared contract match 0.0.27. Only window-role source
changes. Platform and actual public-package checks still gate publication.

The Linux x86_64 ZIP contains original launcher.sh, README-FIRST.txt and reviewed
app source only. It uses system Python/Tk, Git, CMake, Make, compiler and desktop
libraries; the package documents prerequisites and never runs sudo. The shared
GUI imports the verified USA CUE/BIN and privately prepares/plays the game under
.local. SDL/framework revisions stay pinned. Linux updates select the Linux
asset, validate checksum/platform/inventory, use a copied runner and support
rollback while preserving private/unknown files. Cross-platform replacements
are rejected. Windows continues to bundle its existing Python/tool bootstrap.
The actual extracted Linux first-run Tk window and copied-process update/restart
pass locally, including changed version and save/cache sentinels. The pristine
ZIP is created before test state and includes no game-derived binary or data.

All 89 source tests pass without skips, including three Linux packaging,
environment and platform/update tests. The 113-file source audit, Windows CRLF bounds and actual dashboard parser
pass: three fresh n0028 checks, with all three reports/ten submitted checks
unchanged. Both Windows/Linux package integration workflows gate publication. Linux first-setup
integration uses original synthetic input in CI; actual Linux game presentation
is tested privately. Broader distribution, Wayland and real audio-device support
remain player checks. Native selection, all 48 exclusions and clocks are unchanged:
324,928 / 845,824 = 38.4156% linked, 61.5844% outside. No new native credit.

The first unpublished Linux package CI run found missing XScreenSaver headers
in the documented prerequisites. The Ubuntu command and Linux CI dependency
list now include XScreenSaver/XTest/Xext development files, along with udev,
USB and D-Bus support from the pinned SDL Linux dependency guide. Publication
was blocked; the corrected package must pass the complete final gates. This
changes package instructions and CI prerequisites, not runtime code or coverage.

The next unpublished Linux attempt compiled and passed the runtime smoke, then
exposed helper assumptions about source-relative private output and SDL headers.
The synthetic-only controller check now accepts the extracted package's .local;
real-game qualification output restrictions stay unchanged. Renderer/header checks
read the actual configured SDL source. Local external-path controller (11 cases),
normal-controller syntax, renderer 1x/4x, queue and worker equivalence pass.
The new configured-header regression and all 89 source tests pass without skips.
These are test-helper fixes; no game implementation or tested binary changed.

## Published 0.0.28 receipts

Immutable code/tag: `9e1da69209f4b47d7544b921a5a2f760c25652b8`.
All exact-code main-push gates pass:
[Source checks 41361325719](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41361325719),
[Runtime and renderer checks 41361325651](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41361325651),
[Windows/Linux packages and publication 41361325646](https://github.com/TheEelYT/Nitrogen-Squared/actions/runs/41361325646).
Both package jobs, both runtime jobs, both source jobs and publication pass.
The earlier dependency/helper-path attempts remained unpublished; the corrected
final source and these gates supersede them.

The actual [0.0.28 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.28)
was downloaded and audited. Tag/latest target, all five assets, checksums and
published digests pass. Windows has 1764 owned files, an x64 launcher and portable
Python license; Linux has exactly 115 owned files plus its manifest, with executable
launcher.sh, prerequisite instructions and no bundled game/tool binary. Both apps
contain exactly the 113 reviewed source files. Windows app/source ZIP are byte-equal;
Linux, Windows and immutable source match after Git line-ending normalization.
No private payload is included. ZIP SHA-256 values:

- Windows: `dd147aaabd81fc30954ea58289263afbfc4d666d81685ea3ac6f67bb18463620`.
- Linux: `60900172ea49c9df4025fdcf7e27a6bdc7002821105e522bb638a1dd0674c429`.

The extracted Linux package passes first-run Tk, actual synthetic preparation,
11 controller-helper cases, configured-header syntax, enhanced/reference smoke,
renderer equivalence (331 checks at 1x; 340 at 4x), 8843 queue checks, render-worker
equivalence and actual copied-process update/restart with private sentinels retained.
Private real-game Linux presentation and normal-production qualification are recorded
above. Broader distribution/Wayland/audio-device checks remain player checks.

This receipt changes documentation only; preserve the published tag/assets, with
no VERSION bump or runtime rebuild. All 89 source tests pass without skips.
Fresh n0028 player checks remain pending; earlier submitted reports stay unchanged.
The Windows level-entry hitch still lacks explicit resolution confirmation.
Native selection/clocks remain unchanged: 38.4156% linked / 61.5844% outside.

## Dashboard player acceptance after 0.0.28

The owner submitted version-scoped results in
[67650e5b643b1b39f16c2a2fe898b425968ce0a6](https://github.com/TheEelYT/Nitrogen-Squared/commit/67650e5b643b1b39f16c2a2fe898b425968ce0a6).
These results supersede pending player status only for the checks below.

| Report | Submitted result | Scope |
| --- | --- | --- |
| 0.0.24 | 3 pass | Window resizing, sharp textures/proportion-correct movies, update |
| 0.0.26 | 5 pass | Menu/button layers, pause shadows, perk widget, high-score UI, update |
| 0.0.27 | 3 pass, 1 fail | Animated HUD, password/code UI and update pass; level-entry stutter fails |
| 0.0.28 | 2 pass | Update/private-build refresh and bonus stars/speed display |

The level-entry failure note is: "Stutter is still present during level transitions,
although not every time." Keep the intermittent Windows transition hitch open.
The earlier measured removal of interpreter debug-enrichment overhead remains
valid, but it did not fully resolve the reported symptom. Do not substitute an
audio workaround or mark this failure passed because the UI checks succeeded.
Audio/game clocks remain unchanged.

The optional n0028 Linux setup/play/update check has no submitted result and
remains untested. Local/CI Linux qualification above is separate evidence, not a
player pass. Accept the submitted UI/update scope without inferring a new campaign,
separate replays of every historical build, exhaustive branch coverage or exact FPS.
No repeat of passed checks, new upload or valued-save overwrite is requested.

This acceptance update changes documentation only: no runtime VERSION bump,
rebuild, renewed qualification or replacement of published release assets/tag.
All seven reports and 24 submitted check entries (23 pass, one fail), including
older n0021/n0022/n0023 results, notes, timestamps and markers remain byte-identical.
The dashboard definition IDs, steps and expected results are unchanged. Verification
compares both fenced JSON blocks and the complete submitted-results section against
the submission commit. Native selection and coverage stay unchanged at
38.4156% linked / 61.5844% outside; this adds no native execution credit.

Future dashboard imports carry untested/blocked checks and their notes into the
next update. Passed and failed evidence stays with its tested version; no pass is
inherited by a replacement release. Existing submitted reports are not rewritten.

## 0.0.29 Dashboard feedback and 0.0.30 menu repairs

The n0029 report passes update, desktop Video modes, HUD/scene scales and brief
play. Audio fails: the owner confirms Master changes volume, but reports misplaced
rows and mismatched menu layers. Keep that failure and every submitted report,
note and timestamp unchanged. The optional Linux check carries forward unchanged.
The intermittent n0027 Windows level-entry stutter remains OPEN; clocks are unchanged.

0.0.30 places Master immediately above SFX. A bounded two-pass parser validates
and moves original Audio DMA primitives as whole rows, preserving original mix,
speaker and track controls. New sliders use imported tick cells with two additive
Gouraud fill halves matching original Audio bars. Play in order's song title is
text only, including when selected. Audio's bottom arrow clears the final row;
Video uses original left/right help-atlas icons alongside To change.

Complete help groups now share one UI transform, including outer bevels and
arrow/button cells. Controls publishes a fresh page-scoped context before its
authored projection. Model polygons, flat label backings, text and outlines share
the centred transform; footer controls keep corner anchors. Context expires if
the title presenter stops. Ordinary gameplay and other executable occupants keep
their projection. The pinned SDK remains unmodified. Native selection is unchanged:
796 records/48 exclusions; 324,928 / 845,824 = 38.4156% linked, 61.5844% outside.
This adds no native credit.

Qualification observed on the checkpointed source before workspace cleanup:

- Visible X11 routes with worker OFF and ON finish all three native intro clips.
  Main, Audio and Controls help layers are inspected; ordinary input returns to
  first-level help and movement/fire without changing personal saves.
- Controls remains coherent in both configurations at 960x720, 1408x1144,
  1828x1094 and 730x800 windows, including consecutive presents and help overlays.
- Master zero/half/full has no/half/full fill with the tick track unchanged.
  Track selection stays text only. Native SFX left/right works. Video 25/100/200
  fill and arrow cells align. Scalar packet checks confirm fill widths 0/90/186
  for Master and 18/90/186 for Video, with no gradient at the song-title row.
- SDK renderer checks pass 331 at 1x, 340 at 4x; the actual adapted world/UI
  fixture passes 343/352. Queue 8,843 and worker ON/OFF equivalence pass at 1x/4x.
- All 92 source tests pass without skips. The 123-file text/CRLF audit and actual
  Dashboard parser/merge preview pass. Six fresh n0030 checks are untested; the
  submitted-results tail and carried Linux check remain unchanged.

Workspace maintenance removed the local build/capture folder during the normal
build. Source checkpoint 736e214fa22d5ca06c9fa71fbef9dad06e5f12f0 was recovered from
Git, with the accepted private cache and original USA input restored from saved
recovery. All 92 source tests pass again. The observed diagnostic execution identity
is edf0a48659cacf222538ec4a36b19c202995fded5e5854cff860c46cdfafdf9b;
The rebuilt O3 production executable matches that identity and the exact native
manifest. Diagnostics are OFF, the qualification include is empty and the
production link contains no comparison/replay interposition. The separate normal
controller fixture passes all three movie completions, analog/fire samples and
clean SDL_QUIT at frame 4500. Production binary SHA-256 is
`fd6f73542e24cb4b37366766527c76495776172891355e159512ab8729011940`.
Platform workflows and actual public-asset receipts remain pending until recorded.
Software X11/dummy audio do not verify physical Windows audio quality or real
fullscreen transitions. Fresh focused player menu checks remain pending; no new
campaign, upload or valued-save overwrite is requested.


## 0.0.30 publication receipt

The [0.0.30 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.30) is published at immutable code/tag
`ed3cdb686e6c0af1d1300394a0e3dacae2242ebe`. Source checks 41569591629, Windows/Linux runtime and renderer
checks 41569591595, and portable package/publication checks 41569591582
all pass. This supersedes pending platform/publication status above.

All five actual public assets were downloaded and audited: tag/latest target,
asset digests, checksum files and package-owned manifests pass. Windows has
1774 owned files, an x64 launcher and portable Python license. Linux has
125 owned files plus its manifest and executable launcher. Both apps and
the source ZIP contain exactly 123 reviewed text files, matching the release
commit after Git line-ending normalization. No private payload is included.

- Windows ZIP SHA-256: `d9e68ec6b159bd57061d079ae9212073a630e48ad015edac450642045c444496`.
- Linux ZIP SHA-256: `d4e322dc857054f86b55e24aaa3e9f4af23bdd1edd73d0539b6367e28ab1953d`.
- Source ZIP SHA-256: `f116771f99bef04e18f8861b4182bc3ce9556dbfb193af9f8ca1debf108fefb5`.

This receipt changes documentation only; preserve the published tag and assets.
No VERSION bump or repeated runtime build is needed. Fresh n0030 menu checks
remain pending; optional Linux stays carried. Submitted reports remain unchanged.
Coverage stays 38.4156% linked / 61.5844% outside. The intermittent Windows
level-entry stutter remains OPEN; clocks remain unchanged.

## 0.0.31 title-preview regression repair

The owner reports nested black frames on the 0.0.30 title screen. Actual reference
GPU traces identify 32 textured 0x2C preview-frame polygons at OT rank 441, the
same rank used by help cards. The 0.0.30 blanket UI tag incorrectly gave those
perspective polygons the square-pixel UI transform. An original synthetic
preview-segment regression case fails the 0.0.30 rule and passes the narrower rule.

The repair identifies untextured help bevel quads and the four exact 14x14
help-arrow atlas cells separately. Title preview polygons keep their original
world transform. Audio fills/placement, Controls context and the other 0.0.30
repairs are retained. Only the window-display execution family changes. There
is no native-range selection or clock change: all 796 records/48 exclusions,
324,928 / 845,824 = 38.4156% linked, 61.5844% outside remain unchanged.

All 92 final source tests pass without skips; the 123-file text/CRLF audit passes.
The actual Dashboard parser/merge accepts seven checks. All six prior unsubmitted
check objects, including optional Linux, carry unchanged; the complete submitted-
results tail remains byte-identical. The title report is chat feedback and does
not rewrite any submitted Dashboard body, notes or timestamps.

Visible X11 qualification with render worker ON and OFF confirms a coherent
animated preview frame. Logo frames 1750–1950 are inspected with worker OFF;
usual 730x501/960x720, wide 1600x900 and portrait 730x800 windows are inspected.
Main, Audio and Controls help cards stay aligned. Master remains above SFX and
the song title stays text only; Controls model/callouts and Video arrow/slider
layers are inspected. Ordinary input returns to first-level help. All three
native intro clips finish in both worker routes. Personal saves are untouched.

The staged O3 diagnostic execution identity is
`c7827c32f1e3c74510a4966981bdf1b4139dd3282fd9defd4b13f6a7d6c60640`,
with binary SHA-256
`68983b829d497b943addf0663fdd65699ab72e62f4c9ead68910c6ee97af55ec`.
The pinned SDK remains unmodified. The final O3 production build matches the diagnostic execution identity and
exact native manifest. Diagnostics are OFF, the qualification include is empty
and comparison/replay hooks are absent. The separate normal fixture passes
three movie completions, analog/fire input samples and clean SDL_QUIT at frame
4500. Production binary SHA-256 is
`ddb9120aaba181730be4c2973578ceffa3ba5edfeb555c54fdf9e759272af7c6`.
Platform workflows and actual public-asset receipts are pending until recorded below. Fresh player title checks remain
pending; intermittent Windows level-entry stutter remains OPEN. No new campaign,
disc upload or valued-save overwrite is requested.


## 0.0.31 publication receipt

The [0.0.31 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.0.31) is published at immutable code/tag
`513bde19318764125c742782cf6e8df7e7c6243a`. Source checks 41639675693, Windows/Linux runtime and renderer
checks 41639675754, and portable package/publication checks 41639675731
all pass. This supersedes pending platform/publication status above.

All five actual public assets were downloaded and audited: tag/latest target,
asset digests, checksum files and package-owned manifests pass. Windows has
1774 owned files, an x64 launcher and portable Python license. Linux has
125 owned files plus its manifest and executable launcher. Both apps and
the source ZIP contain exactly 123 reviewed text files, matching the release
commit after Git line-ending normalization. No private payload is included.

- Windows ZIP SHA-256: `e53f2768f62ca1c3cda5e322df12acfc228f52bc26d6e40f4f46e5c3f2b55712`.
- Linux ZIP SHA-256: `dcd7af832aeea22f449635391397a47e93d63396aaa7b4893114000020fe3be2`.
- Source ZIP SHA-256: `321dadf013c875199f6e67a8128d1bbb06cbc3a73a593792f69de0187fd5827c`.

This receipt changes documentation only; preserve the published tag and assets.
No VERSION bump or repeated runtime build is needed. Fresh n0031 menu checks
remain pending; optional Linux stays carried. Submitted reports remain unchanged.
Coverage stays 38.4156% linked / 61.5844% outside. The intermittent Windows
level-entry stutter remains OPEN; clocks remain unchanged.


## 0.1.0 publication receipt

The [0.1.0 release](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.1.0) is published at immutable code/tag
`de0866abaeeb1b33ca4aa11990224b66f190a527`. Source checks 42325757345, Windows/Linux runtime and renderer
checks 42325757942, and portable package/publication checks 42325757319
all pass. This supersedes pending platform/publication status above.

All five actual public assets were downloaded and audited: tag/latest target,
asset digests, checksum files and package-owned manifests pass. Windows has
1775 owned files, an x64 launcher and portable Python license. Linux has
126 owned files plus its manifest and executable launcher. Both apps and
the source ZIP contain exactly 124 reviewed text files, matching the release
commit after Git line-ending normalization. No private payload is included.

- Windows ZIP SHA-256: `3e8a271bd7eab32ffeb3f0d0e4c356fa67c0d3d3cadfeb64ae88d1121816df26`.
- Linux ZIP SHA-256: `1eda9456ec479c26a0e65abeae75e9249922bc2a6183afee9fd928f396c263b6`.
- Source ZIP SHA-256: `2115f1cdd01c78a0bb04b14b3d7f840c65fa3a8dfc6250d7b3df034cd752e390`.

All 27 reviewed retired work branches are removed; only main and release/0.1.0
remain. The release branch points at the same immutable code as the tag. Future
releases preserve release/x.y.z, including patch versions.

This receipt changes documentation only; preserve the published tag, release branch and assets.
No VERSION bump or repeated runtime build is needed. Fresh n0100 menu checks
remain pending; optional Linux stays carried. Submitted reports remain unchanged.
Coverage stays 38.4156% linked / 61.5844% outside. The intermittent Windows
level-entry stutter remains OPEN; clocks remain unchanged.

- Active 0.1.1 corrects the owner's clarified exit gesture: TITLE SCREEN only,
  two monotonic seconds; closing... fades over the first second at the top third.
  Main-menu Back retains its original behavior. The guarded small title prompt
  and its complete caller identity own the caption, not the frame-yielding parent.
  It adds combined SHA256SUMS.txt reading/publication, removes redundant source ZIP
  uploads and preserves old sidecars through 0.1.x. From 0.2.0 publish only platform
  ZIPs and SUMS; old clients skipping the bridge may need a manual launcher download.
  Preserve v0.1.0 code/tag/release branch/platform ZIPs. Its metadata cleanup verifies
  original ZIPs and hashes before adding SUMS/removing only the extra source ZIP.
  Native selection/coverage and clocks unchanged; source/runtime/platform/public
  validation is pending. Carry unresolved Dashboard checks and preserve result tails.

- The owner requests source and runtime/renderer workflows on release/x.y.z,
  with portable package construction/publication only from main after promotion.
  Main still gates on the exact commit's source/runtime checks; preserve release
  branches at final code. Do not run duplicate portable packages for release branches.

- CI scheduling: Source checks and Runtime and renderer checks run on release/**
  pushes (and PRs); Release packages Windows/Linux only on main. Promotion keeps
  the exact checked SHA, so main reuses its successful release-branch checks.
  A different merge SHA must receive its own passing checks before publication.
  The user requested the workflow name Release for its cross-platform role.

- A copied-updater dependency regression was caught before publication: the new
  release_checksums.py must accompany portable_update.py in both Windows and
  Linux runners. The new real copied-script fixture fails for both platforms
  without it and passes with it, using no application PYTHONPATH. Runtime code
  and qualified private binaries are unchanged; repeat source and platform CI
  on the corrected exact release commit before publishing.


## 0.1.1 publication receipt

[0.1.1](https://github.com/TheEelYT/Nitrogen-Squared/releases/tag/v0.1.1) is published at immutable code/tag/release branch
`3c806ae8788653e455ea6213019777b5ae86983e`. The two-second Back hold now belongs to the title screen;
main-menu Back retains its original action. The first-second caption fade,
release cancellation, existing Audio fixes and Tab removal are retained.

Source CI 42330340563 and Windows/Linux runtime/renderer CI 42330340586
pass on release/0.1.1. The Release workflow 42330636415 packages/publishes
from main at that exact checked commit; no duplicate branch package run occurs.
All 101 local source tests without skips, 125-file source audit, actual Dashboard
parser/carry/result-tail checks and worker ON/OFF title/Main/Audio routes pass.
The normal O3, diagnostics-OFF, no-hook production build matches the diagnostic
execution contract; its three-movie/controller/fire/quit fixture passes frame4500.
The copied-updater import regression fails before and passes after adding the
checksum reader to both platform runners.

All five public assets are downloaded/audited: platform ZIPs, SHA256SUMS.txt and
temporary legacy sidecars. Owned manifests and asset hashes/digests pass; both
apps contain exactly 125 reviewed source files matching the release commit after
Git line-ending normalization. Windows owns 1776 files, with x64 bootstrap
and portable Python license; Linux owns 127, with executable launcher.
There is no redundant uploaded source ZIP; GitHub's source archives remain.
Legacy sidecars stay through 0.1.x; from 0.2.0 publish only the two platform ZIPs
and SUMS. Old launchers that skip the bridge may need a manual launcher download,
preserving .local and saves.

- Windows ZIP SHA-256: `a33e3d5b19bcb605437f9366fd491c8277fe2f952f883454bf74fec0e4f79819`.
- Linux ZIP SHA-256: `25937acae00406b184315df82eb99ff029d351ac620458014ee25c62d89dabcf`.

The 0.1.0 metadata cleanup verifies its original packages before adding combined
checksums and deleting only its redundant source ZIP. Its two platform ZIPs,
legacy sidecars, immutable tag and release branch remain unchanged. Historical
0.1.0 audit/source-ZIP receipts above describe their state at publication.

This documentation-only receipt supersedes pending qualification/publication
status above. Preserve both released code branches/tags; no VERSION bump or
rebuild is needed for this receipt. Fresh n0101 player checks remain pending;
carry untested/blocked checks and preserve submitted pass/fail bodies, notes
and timestamps. Coverage remains 38.4156% linked / 61.5844% outside, with all
796 native records and 48 exclusions unchanged. Level-entry stutter remains
OPEN and clocks unchanged. The planned 0.2.0 compilation-reuse/version policy
is recorded; it is not implemented by this patch.

## 0.2.1 development candidate

The owner verified 0.2.0 and requested its inclusion in 0.2.1 without publishing
0.2.0 separately. New UI verification and explicit release clearance are pending.
The launcher uses original tunnel artwork and the exact owner-created N² logo,
with Home, What's New and Settings pages, offline notes, shared stage progress,
and native-compatible display/master-volume preferences. No Link Play is present.
The reviewed image manifest is separate from the text-only source allowlist.

Compiled game inputs remain `4ab9bc7e2cf8067a308fa329692040366619bfd9000b020368832efe70a156af`.
No native selection, game clocks or gameplay code changes are made: coverage stays
38.4156% linked / 61.5844% outside. Level-entry stutter remains OPEN. Automated
source, packaged UI, updater and runtime qualification are recorded on the
corresponding dev Actions commit. Main remains on 0.1.3 until owner clearance.
Unfinished player checks carry forward; historical Dashboard result bodies are
preserved exactly. New n0201 player checks remain untested until reported.


## 0.2.1 Tauri source revision — 2026-11-09

The owner reports that the first Windows Tk candidate feels clunky and authorizes
adapting Recompia's actual frontend/Tauri shell. This source revision replaces
canvas drawing with HTML/CSS controls, shared state and responsive pages. It
retains the exact owner logo and original tunnel art and connects the existing
portable Python Backend over local JSON-lines pipes. No Link Play is added.
The owner authorizes GPL-3.0-or-later for original project code; Recompia provenance,
historical MIT grants and component notices remain included. The owner explicitly
requests source ZIP delivery and will push personally: nothing is pushed, tagged,
promoted or published by this work. Version stays 0.2.1. Main is an ancestor of
the source baseline; no newer main game change needs incorporation.

Local evidence: all 143 Python synthetic/configuration tests pass with no skips;
two JavaScript readiness/cancellation tests pass. Six Chromium frontend interaction
tests pass at 760×500, 960×620, 1100×700 and 1440×900, including busy-state
settings, page navigation during tasks, persisted preference command dispatch,
literal remote notes and reduced-motion scrolling. Home and Settings browser
renders were visually inspected. Production Vite and native Linux Tauri builds
pass. A real Linux host/source package is reextracted and its 844-file manifest
checked; Cargo notice files with epoch timestamps are clamped by ZIP packaging.
The stdio bridge is exercised as a separate isolated Python process, including
invalid requests and self-test reports. The compiled-game input fingerprint remains
`4ab9bc7e2cf8067a308fa329692040366619bfd9000b020368832efe70a156af`.

Windows native compilation, actual system-webview self-tests, copied native-host
update/restart and cross-platform runtime workflows must run in Actions after the
owner pushes. Browser mocks do not qualify those native lifecycle/platform checks.
No fresh real-disc preparation or Windows player acceptance is claimed. The
packaging workflow gates downloadable candidates on its actual webview/backend
and copied-updater fixtures; it never publishes dev builds as releases.
Dashboard submitted-results suffix is unchanged. Focused n0201 player checks
remain pending. Native coverage stays 38.4156% linked / 61.5844% outside; clocks
and all game inputs are unchanged and level-entry stutter stays OPEN.


## 0.2.1 startup/progress and Linux smoke follow-up — 2026-11-09

Baseline is owner-pushed dev 21f7b1df3f9fab0bcd5619ea896160613ca4fab4.
The owner reports that the Tauri launcher looks and feels great, but Play with a
compatible game appears stuck until Stop. The supplied recording shows stale
Starting game while the backend already considers itself running; it does not
establish that Stop itself starts the game. Code inspection reproduces dropped
startup stages within the 80 ms progress throttle. The backend also announced
Running before creating the actual runtime process, while child disc-verification
output could remain buffered.

This revision publishes every stage/phase transition, uses Starting during launch,
relays run_runtime.py output unbuffered and treats its actual Runtime started PID
receipt as Running. Worker processes use DEVNULL for stdin, never inheriting the
service command pipe. Full disc validation and compiled-game reuse are retained.
Two regressions fail on the baseline and pass on the fix: rapid lifecycle updates
and a real service/worker subprocess started by one Play request while the protocol
stdin remains open and no Stop/follow-up request is sent. The child confirms EOF
on its separate stdin and writes its launch marker before reporting Running.

Baseline CI: Source checks 42730594815 and Runtime/renderer 42730594954 passed.
Release run 42730594779's Windows job 129547283338 passed native compilation,
packaging, actual webview/backend startup, synthetic runtime and copied updater.
Linux job 129547283749 compiled/packaged its host and passed the actual first-run
interface; it failed later at `audio advances through main-thread stall` in the
synthetic media check. This was not a compiler failure. The test assumed the
independent audio thread would start within a fixed 180 ms. The replacement waits
for the same >3000 submitted samples and >0.08 s media clock, at most three seconds,
without video, event or guest assistance; failure prints actual driver/count/clock.
Pause/resume checks and production audio/game clocks are unchanged. No retries,
skips or relaxed success thresholds are introduced.

Local validation: all 145 Python tests pass without skips; both JavaScript action
tests and the Vite production build pass. A focused build of the actual AudioPlayer
and revised smoke block against pinned SDL 3.4.10 revision
8e37db5e797b6167f3a00d697d816a684bd259c7 passes 20 real dummy-device startup/stall/
pause/resume cycles. Injecting a 300 ms device-start delay with real SDL streams
fails the old 180 ms check and passes five cycles with the revised check. This
focused test does not substitute for the complete Linux packaging/runtime workflow,
which must rerun after the owner pushes. Windows player verification remains pending.

Compiled-game inputs remain
4ab9bc7e2cf8067a308fa329692040366619bfd9000b020368832efe70a156af.
Native coverage stays 38.4156% linked / 61.5844% outside; game inputs, clocks and
level-entry-stutter status are unchanged. Dashboard result bytes are preserved.
Version remains 0.2.1. Deliver a complete source ZIP; nothing is pushed, promoted,
tagged or published. The owner's praise of presentation is not release clearance.
