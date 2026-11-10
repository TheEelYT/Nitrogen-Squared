# Project continuity and update reporting

- The user authorizes repository updates. Keep the current working Windows
  baseline usable while advancing native execution in small qualified steps.
- RELEASE POLICY CHANGED by the owner on 2026-11-08: new update work belongs
  on the persistent `dev` branch, initialized from main. Wait for the owner's
  explicit verification AND release clearance before promoting to main or
  creating a release branch/tag or publishing any release, including prereleases.
  This supersedes every earlier standing-promotion approval below. Automated
  checks and downloadable Actions test artifacts on dev are authorized.
- Keep remote branches limited to main, dev and already released release/x.y.z
  branches. Fix/retest candidates on dev under the same planned version. Before
  final testing incorporate any newer main commits into dev; after clearance,
  fast-forward the exact qualified dev commit to main, preserve that commit on
  release/x.y.z, then build/publish from main. Never recreate/reset dev over work.
  Later documentation receipts stay on main; released branches/tags/assets stay
  immutable. A passed Dashboard check alone is not release clearance.
- The accepted 0.0.9 player baseline reaches level 4 with no issues reported and
  working saves/high scores. Do not require later-level progression before the
  next native milestone. Add focused checks for behavior affected by each change.
- The user also verified first-level gameplay without issues in 0.0.10 and
  authorized a substantially larger next conversion batch. Its temporary startup
  loading dip returns to 60 FPS and may predate that version; it is unconfirmed.
- The user verified 0.0.11 gameplay through level 9 with no other gameplay issues.
  They report FPS dips during save-slot listing and saving, and suspect startup
  high-score reads. Local baseline tracing overlaps the startup dip with card
  reads, but does not establish the high-score caller or root cause. Treat card
  access performance as historical; the 0.0.12 save/load report below supersedes
  its open status. Do not require later levels or new user files.
- Version 0.0.12 adds 20 native card-control/BIOS-call entry ranges. Local
  diagnostic card-access samples improved to about 60 FPS; fresh setup creation
  and existing-card overwrite matched the 0.0.11 images. BIOS/serial handling and
  synchronous file publication remain compatibility services. The user reports no
  saving/loading slowdowns on Windows in 0.0.12; record that specific performance
  check as passed. Exact FPS, startup-only timing and a new campaign playthrough
  were not separately reported. Keep the 0.0.11 level-9 report as prior gameplay
  acceptance; no repeated playthrough is required for this acceptance note.
- The next test-only chunk adds 122 original synthetic mixed native/interpreter
  call cases through the production dispatcher, including callbacks, tail flow,
  PC segments, two-page guards, mid-call code changes and RAM restore. Local
  enhanced/reference and renderer checks pass, as do Windows/Linux runtime and
  source CI. Keep the fixture in future native batch qualification.
  It enables no additional game ranges and needs no player rebuild or replay.
  Coverage remains 4.2642% / 95.7358%. The original user disc upload was recovered
  and privately reimported after the prior scratch workspace disappeared; reuse
  that existing saved input rather than requesting another upload unnecessarily.
- Version 0.0.13 adds 32 qualified geometry/object-presentation, angle and text
  roots: 36,932 new bytes, 73,000 / 845,824 = 8.6306% linked, 91.3694% outside.
  N2O has 79 roots and 1,523 aliases. Private qualification passed 17,475
  segment comparisons across all new roots and 20 matching-frame comparisons
  across two first-level routes. The normal build and Windows/Linux CI passed.
  The user subsequently reports no issues noticed in the focused Windows
  0.0.13 playtest. Record that route as accepted without implying exhaustive
  branch coverage or a new level-9 campaign playthrough.
- Version 0.0.14 selects 46 further model/packet and game/menu presentation
  roots, adding 75,948 bytes. Reduced diagnostic coverage verifies 148,948 /
  845,824 = 17.6098% linked, with 82.3902% outside. N2O has 125 roots and 4,189
  aliases. One constructed exception/return mismatch and 28 unqualified roots
  remain unselected. The final reduced selection passed 10,316 private segment comparisons
  and 17 matching-frame checks, the normal production/controller fixture and
  Windows/Linux CI. The user reports no issues noticed in the focused Windows
  0.0.14 playtest and authorizes the next substantial batch. Record that route
  as accepted without implying a new level-9 playthrough or exhaustive coverage.
- The user requests substantial coherent conversion batches. Continue through
  preparation and qualification to an actual conversion when viable; do not
  use test-only preparation as the default stopping point.
- Every runtime update must update `TESTING.md` with the version, concrete changes,
  focused player checks and pending/verified status. Prior acceptance is history,
  not automatic verification of a replacement. Avoid requesting unrelated full
  checklist repeats. Record results and limits in `docs/VALIDATION.md`.
- Every runtime update must refresh README.md's native and uncovered shares using
  the metric defined in `docs/NATIVE_PROGRESS.md`, and update the separate native
  service inventory when affected. Explicitly report unchanged coverage for
  host-only work. Analysis-only generated code does not count. Do not equate the
  uncovered share with interpreter CPU time or overall remaining project work.
- No commercial game files, derived game code, generated guards containing game
  instructions, compiled game modules, media, captures or saves may enter Git or
  releases. All game inputs come from the verified user import. Preserve the
  reviewed text allowlist in `configs/source_package.json`.
- Keep the existing C11/C++17 implementation. Read and follow the pinned
  framework's instructions when working on its integration; do not edit its
  checkout. Limit builds to two compile jobs and serialize local game sessions
  and builds. Retain qualified reference/fallback paths.
- Documentation-only changes need no runtime VERSION bump, rebuild or player
  retest. Explain what was published and what testing, if any, is still needed.

- Version 0.0.15 retains 117 new game/object, model-dispatch and resource-control
  roots, adding 71,028 emitted bytes. The final diagnostic and normal builds
  verify 219,976 / 845,824 = 26.0073% linked, with 73.9927% outside. N2O has
  242 roots and 7,440 aliases. All 117 new roots were observed directly; final
  qualification passed 10,943 comparisons and 17 pixel-identical frames, the
  normal production/controller fixture, 40 source tests, the 79-file source
  audit and Windows/Linux CI. Three mismatch owners (0x80039E50, 0x80040D44,
  0x800440DC) and 140 other candidates without sufficient evidence stay
  unselected. The normal fixture's residency declines stop during startup;
  overlapping images retain guarded fallback. The user reports no issues noticed
  in the focused Windows 0.0.15 playtest. Record that route as accepted without
  implying exhaustive coverage or a new level-9 campaign playthrough.
  The existing private upload was restored after connection loss; do not
  request it again unnecessarily. Preserve existing record order and append
  new candidates so unchanged generated units keep their identities. When
  reducing a private exploratory pool, regenerate in a fresh source directory
  and check for stale parts before building. Game-derived files remain private.

- The next frontend/library batch is on native-frontend-library-batch. A fresh
  0.0.15-selection reference route passed 17 captures after another workspace
  reset. The original upload remains available; no new user input is needed.
  New diagnostic selectors distinguish exact guarded code identities across
  overlapping images; optional failure collection still exits unsuccessfully
  and is exploratory only. Keep failed/unobserved owners out of final binding,
  then repeat strict reduced-selection and normal-production qualification.
  Main remains accepted 0.0.15 at 26.0073%; new candidate coverage is unqualified.

- The 0.0.16 exploratory pool adds 595 candidates (395 N2O, 200 NEW), with
  provisional 46.9237% linked / 53.0763% outside; none is final qualified progress.
  The pool uses private O1 flags. Restore both C and C++ Release flags to
  -O3 -DNDEBUG for final diagnostic and normal builds, then verify the cache.
  NEW's CPS movie-control callers bypass the existing call-site native movie
  hooks: keep that control path on fallback rather than changing override
  dispatch semantics for this batch. Additional startup owners fail comparisons
  or exceed the checker budgets. N2O_BLOCKED_IDS is an exploratory, v2-only
  exclusion file, verified before the first dispatch; final builds must remove
  these owners and contain no diagnostic interposition. Main remains 0.0.15.

- The reduced 0.0.16 candidate contains 348 new entry roots: 236 call-target
  roots and 112 observed indirect/continuation boundaries. Its O1 pool passed
  1,458 live plus 17,175 replay comparisons at 687 identity/PC pairs, zero
  failures, and 21 exact-frame checks through first-level completion/bonus/shop.
  Preliminary coverage is 295,648 / 845,824 = 34.9538%, with 65.0462% outside;
  N2O has 546 roots and NEW 44. This is pending final strict O3 diagnostic,
  normal-production and final platform checks. All earlier failed owners and
  their whole input intervals stay excluded, including new fragment discovery.

- Version 0.0.16 final O3 diagnostic and normal-production checks supersede the
  preliminary pool status above. The reduced binding adds 348 entry roots
  (236 call targets, 112 observed indirect/continuation boundaries), not 348
  newly identified complete functions. All identities were observed, 347 direct
  and one through a continuation. Final evidence: 1,458 live + 17,175 replay =
  18,633 passing comparisons at 687 identity/PC pairs; 21 exact frames through
  first-level completion and bonus/shop. Normal coverage is 295,648 / 845,824 =
  34.9538%, with 65.0462% outside; +75,672 bytes over 0.0.15. N2O has 546 roots
  and 10,144 aliases; NEW has 44 roots and 87 aliases. The normal movie/controller/
  quit fixture, 45 source tests, 83-file source audit and final Windows/Linux CI
  passed. Focused Windows 0.0.16 player acceptance is pending; no repeat campaign,
  new input or deliberate save overwrite is requested. Keep failed-owner input
  spans excluded from fragment discovery. NEW movie-control callers stay on
  fallback; preserve pinned dispatch semantics. Production has no qualification
  hooks. Both Release flag sets are -O3 -DNDEBUG. Reuse the existing private upload.

- The user reports no issues noticed in Windows 0.0.16 when launched through
  Python, with everything looking the same as before. Accept that reported route
  without implying exhaustive coverage, every checklist action or a new campaign.
  They separately report intro-video stutter when launching the EXE directly.
  Source inspection finds tools/run_runtime.py supplies NITROGEN_NATIVE_DISC_BIN;
  native/media_entry.cpp refuses native playback without it and retains guest
  playback. The launcher also sets OpenGL/worker/history options. This is a likely
  launch-path explanation, not a reproduced Windows diagnosis or implemented fix.
  Keep the direct-launch issue open and use the Python launcher as the qualified
  route. No runtime change, VERSION bump, rebuild or repeat playtest is needed
  for this documentation-only acceptance note. Coverage stays 34.9538% / 65.0462%.

- The user authorizes the next substantial native batch, with incremental code/data
  mapping and no change to the existing linked-range metric. They prefer to defer
  logic/render clock separation. For 0.0.17 they also explicitly request a Windows
  repository release: extract a Nitrogen-Squared folder, launch launcher.exe,
  select the user's CUE/BIN, automatically verify/import/generate/compile/play,
  and handle updates. Every generated/extracted file and save must stay inside
  that folder. Original disc inputs may remain at the user's selected location.
  Bundle only the original bootstrap, reviewed source and permitted portable
  Python. Download pinned preparation tools into .local on first setup; never
  require a separate Python or Visual Studio installation. Updates must preserve
  .local, verify package hashes/inventory and recover interrupted replacement.
  No game-derived runtime or user disc files may enter the release.

- Version 0.0.17 selects 86 new entry roots and expands one existing owner,
  adding 4,332 emitted bytes. Final O3 diagnostic and normal reports agree on
  299,980 / 845,824 = 35.4660% linked, 64.5340% outside. N2O has 562 roots and
  10,183 aliases; NEW has 114 roots and 156 aliases. All 87 changed guarded
  identities were observed (86 direct, one continuation-only); final strict
  qualification passed 462 live plus 4,700 fail-fast replay comparisons and
  42 exact frames across two routes. Normal production hashes match, hooks are
  absent, both Release flags are -O3 -DNDEBUG, and the three-movie/analog/fire/
  pause/quit fixture passed. Sixty-nine source tests and the 95-file audit pass.
  These fragments are not 86 newly identified complete functions. Preserve the
  45 whole-owner exclusions; new boot and NEW movie-control callers stay fallback.
- Incremental code/data inventory now labels linked, static/data hints, conflicts
  and unknown bytes separately against verified source identities. Continue it
  with each batch. Hints cannot qualify entries or change the coverage denominator.
  Preserve source record order, qualified identities and the reference path.
  Logic/render clock separation remains deferred at the user's preference.
- The user explicitly authorizes a 0.0.17 repository release and standing main
  promotion. Public ZIP: Nitrogen-Squared/launcher.exe, reviewed app source and
  clean portable Python only. Pinned tools/framework download privately; CUE
  selection verifies/imports/generates/compiles/plays automatically. Every tool,
  extracted/generated file, cache, build, log, update backup and save stays under
  that folder's .local; original disc remains at its selected path. Portable saves
  use .local/saves, separate from the legacy developer .local/runtime-dev/saves.
  Updates validate manifests/checksums, preserve private/unknown files, back up and
  roll back owned replacements, and restart via a copied updater after old
  processes exit. Actual Windows startup, isolated bundled compiler/runtime and
  copied-update/restart preservation tests pass. Real-disc Windows first setup
  and the short 0.0.17 player route remain pending; no new upload, repeat campaign
  or deliberate save overwrite is requested. The public launcher supplies the
  verified-disc environment; raw private game EXE launch is still a separate path.

- Final 0.0.17 code at 5ace72d09c51d72f43de5f1eb6e2a6b4b1d45427 passes source
  workflow 40960407083, Windows/Linux runtime/renderer workflow 40960407040 and
  portable package/update workflow 40960406995. Final documentation records
  these receipts. Main publication repeats the complete gated workflow set;
  preserve public version assets and verify the published ZIP/source inventory.


- Version 0.0.18 repairs the user's reported first-setup CMakeRCCompiler.cmake
  escape failure. Explicit portable compiler/Python definitions must use forward
  slashes and be shared with the actual Windows synthetic-runtime fixture.
  Detect damaged compiler metadata/cache and archive only runtime-dev/build;
  retain imports, generated inputs, compiled preparation tools, settings and saves.
  Do not ask the user to delete .local or repeat tool downloads. The existing
  updater works before game preparation succeeds. Seventy-three local tests pass,
  the source allowlist stays 95 files, and coverage is unchanged at 35.4660% /
  64.5340%. The user's real-disc Windows retry remains pending; earlier native
  qualification is history, not evidence that first setup succeeded on their PC.


- The user reports successful Windows 0.0.18 launcher-built gameplay through
  level 9 with no issues noticed, the same behavior as command-line builds, and
  successful saving. Accept real-disc preparation and that reported route,
  superseding pending retry/player status above. This also accepts the unchanged
  0.0.17 native selection within the tested 0.0.18 build. Do not infer every
  checklist action, explicit save reload, update-installation method or later
  campaign coverage. No rebuild, new files or repeat playthrough is needed for
  this documentation-only acceptance note. Coverage stays 35.4660% / 64.5340%.


- The user authorizes the next native batch and requests eventual full asset/music
  folders for future mod packs, with runtime reads moved off the original BIN.
  Extraction and loader migration may proceed incrementally before 100% linkage;
  clock separation remains deferred. The active next-batch checkpoint adds an
  optional private asset extractor: original containers, raw movie sectors, PCM
  WAVE CD tracks, preserved pregaps and explicit ISO audio aliases. All 27 records,
  ten tracks and 37 outputs were extracted privately and checked byte-for-byte
  against verified input; no runtime asset redirection or mod loading is enabled.
  Preserve original inputs and existing edited extraction directories. Public
  source inventory is 98 original text files. The accepted 35.4660% coverage is
  unchanged at this checkpoint; new native candidates remain unqualified. A
  fresh O1 baseline is tracing an ordinary-input route through frame 18300.
  Final diagnostic and production builds must restore both Release flags to O3.

- The asset tooling now also has a launcher Asset folders button: extract once,
  then open the preserved folder. It is unavailable until a verified import
  exists and disabled during preparation/play/update. Backend extraction is
  independent of game launch and retains the shared setup log/cancellation path.
  Seven synthetic asset tests cover source preservation and this launcher action;
  the total source suite is now 80 cases. The Windows startup fixture requires
  the asset-tools control to exist. Native pool source is private/unqualified;
  do not include its temporary configs/native_usa.json in source checkpoints.

- 0.0.19 releases only the tested asset feature after the execution environment
  became unavailable during final native O3 compilation. Its production native
  config stays the accepted 0.0.18/0.0.17 selection: 299,980 / 845,824 = 35.4660%
  linked, 64.5340% outside. Do not count the private 302-candidate pool or its
  provisional 80-root reduction as converted code. Main must keep the qualified
  config; private configs and witnesses stay out of Git/releases.
- Native recovery checkpoint: both O1 reference routes use route.py --long through
  frame 18300, 25 captures each, reaching second-level play. The private pool
  default produced 276 comparisons/two failures/110 PC pairs, and its later
  frames differed. The alternate route with those IDs preblocked passed 224
  comparisons and 25 exact frames. Retained provisional roots: 80 (47 N2O,
  33 NEW), 16,712 input bytes; final strict/replay/normal evidence is incomplete.
  Hold whole N2O inputs 0x80070B1C/4 and 0x800728E8/384. The candidate's private
  final-native.json is not the release config. Restore both Release flags to
  O3 for resumed final checks and preserve a fresh generated-source directory.
- Asset feature checkpoint 580e2c23de047778fd8b69d7c0c747cb5a024d58 passed source
  40991982195, runtime/renderer 40991982081 and portable Windows 40991982177.
  All 80 source tests and the 98-file audit pass. Real-input extraction catalogued
  27 records, ten music tracks and 37 outputs (539,899,114 bytes), with all
  preserved source payloads checked. The launcher Asset folders action extracts
  separately from play, opens existing folders and keeps edits. The user's
  focused asset-folder check was pending at this checkpoint; the acceptance note
  below supersedes it. Do not ask for another disc upload.

- The user downloaded and tested 0.0.19, reports gameplay is still fine and confirms
  that Asset folders works as intended. Accept the reported Windows route and
  asset-folder flow without inferring each extracted file, mod loading, a new
  level-9 campaign or additional save/reload coverage. The 0.0.18 level-9/save
  report retains its version scope. This documentation-only note requires no
  runtime rebuild, release, repeat playthrough or new user input. Native coverage
  stays 35.4660% / 64.5340%; the unfinished native reduction remains unqualified.


- Version 0.0.20 supersedes the interrupted native checkpoint with 53 qualified
  entry roots (40 N2O/13 NEW), +8,188 emitted bytes. Diagnostic and normal reports
  agree: 308,168 / 845,824 = 36.4341% linked; 63.5659% outside. Preserve all 675
  old config records in order, all 47 whole-owner exclusions and fallback.
  N2O: 602 roots/10,525 aliases; NEW: 127 roots/192 aliases. Boot is unchanged.
- Fresh reduced O3 qualification passes 269 live + 2775 fail-fast replay =
  3044 comparisons, no failures, and 50 exact frames across two --long routes
  through frame 18300/second-level play. All 53 identities were observed,
  52 directly and 1 continuation-only. Normal hashes match, diagnostics and
  qualification hooks are absent, and the normal controller/movie/quit fixture
  passes. The 261-root exploratory pool and 208 unobserved candidates receive
  no extra credit; the older failed pool/provisional 80 roots remain unqualified.
- The reported 0.0.20 Windows gameplay route is accepted below. Earlier reports retain
  scope: 0.0.18 level 9/saving and 0.0.19 gameplay/Asset folders. No new upload,
  repeated campaign or deliberate save overwrite is required. Clock separation
  remains deferred; folder-backed runtime assets and mod-pack loading are future
  work. Continue code/data mapping without changing the linked-range metric.
- Recovery metadata is privately saved as Nitrogen-Squared-0.0.20-native-recovery.zip,
  in the user's project files. It contains root/address/hash
  metadata and original helper scripts, not disc bytes, guards, generated C,
  compiled game, media, RAM witnesses or saves. Reuse the existing verified disc
  upload. Inspect checkpoint phase; provisional metadata is not qualification.
- All 80 local source tests pass with no skips, and the 98-file source audit
  passes with the unchanged 128 KiB bound, including Windows CRLF sizes.
- Published 0.0.20 code b8a631621094266a6d22089499d3ab326738673d passes source
  41007750065, Windows/Linux runtime 41007750056 and portable Windows 41007750099.
  The actual public ZIPs, checksum/digests, 1,749-file owned manifest, x64 launcher
  and 98-file source inventory were downloaded/verified. Preserve public assets;
  the subsequent 0.0.20 acceptance note below supersedes pending player status.
  Release-receipt documentation
  changes need no runtime rebuild, VERSION bump or repeat player check.

- The user reports that 0.0.20 still plays with no issues noticed. Accept that
  reported Windows route without inferring a new level-9 playthrough, save/reload
  result or every checklist action. This documentation-only acceptance needs no
  runtime rebuild, version bump, additional files or repeat player check. Coverage
  remains 36.4341% linked / 63.5659% outside.


- Version 0.0.21 adds 26 observed entry roots (22 N2O/4 NEW), +6,304
  emitted bytes. Preserve all 728 prior records in order. Final diagnostic and
  normal reports agree: 314,472 / 845,824 = 37.1794% linked,
  62.8206% outside. Boot is unchanged. Keep all 47 whole-owner exclusions
  and guarded fallback; unobserved or failed contexts receive no credit.
- Final strict O3 qualification passes 106 live + 975 replay = 1081
  comparisons, zero failures, and 62 exact frame checks. All 26 identities
  were observed (26 directly/0 continuation-only). Deep reference
  covers high-score entry and return to gameplay; it does not prove later levels.
  Normal hashes match, hooks are absent, and normal movie/controller/quit checks
  pass. Focused Windows 0.0.21 player acceptance is pending. The reported 0.0.20
  route remains accepted; no new upload, repeat campaign or valued-save overwrite
  is required. All 80 source tests and the 99-file source audit pass.
- USA remains the sole supported base. The user defers EU comparison/support;
  later optional language import should use a user's own EU assets after runtime
  folder-backed loading exists. Clock separation remains deferred. Continue
  code/data mapping without changing the linked-range denominator.
- Existing framework compiler-cache support is enabled privately with compiler-
  content/source/flag checks intact. Recovery archive
  PRIVATE-Nitrogen-Squared-0.0.21-recovery.tar.gz contains compiled game objects;
  keep it private and out of Git/releases. Public source remains in Git. Recover
  metadata into .local/qualification-021 and compiler-cache into .local/compiler-cache;
  reuse the original verified user upload. Inspect checkpoint phase before trusting
  any qualification receipt after a reset. Validation through 0.0.20 is archived in
  docs/VALIDATION_THROUGH_0.0.20.md; current results are in docs/VALIDATION.md.


- Published 0.0.21 code 891f1a2d47ea7a69843ce679f61335277867d363 passes source
  41159267588, Windows/Linux runtime 41159267620 and portable Windows 41159267649.
  Actual public ZIPs, checksums/digests, 1,750-file owned manifest,
  x64 launcher, portable Python license and 99-file source inventory were
  downloaded and verified. Preserve published assets/tag. This receipt is
  documentation only; no rebuild, VERSION bump or repeat player check is needed.
  Focused Windows 0.0.21 player acceptance remains pending.


- The user completed 0.0.21 gameplay and reports unchanged behavior with no issues
  noticed. Submitted n0021 dashboard results pass N2-UPDATE, N2-PLAY, N2-SCORE and
  N2-STARTUP. Accept the reported route without inferring a new campaign/save
  check. The startup dip is reported absent for several updates; native save/load
  is the user's suspected cause, not an established diagnosis. No repeat test,
  rebuild or VERSION bump is needed for this acceptance note.
- TESTING.md now contains the Test Dashboard v1 import contract and submitted
  version-scoped results. Read its maintainer instructions and the linked
  projects-dashboard-site/docs/TESTING-FORMAT.md before updating it. Preserve
  project id nitrogen, exactly one strict test-dashboard JSON definition block,
  and the project-lab-results markers/results block byte-for-byte when changing
  definitions. New releases need a fresh version ID, matching name/title/date/
  metric/scope, stable per-version check IDs and no inherited results. Keep
  prose and JSON checks consistent. Never put statuses in definitions or
  auto-submit results. Use GitHub SHA guards and preserve concurrent feedback.


## Historical 0.0.22 execution interruption (superseded below)

- The execution environment became unavailable during final qualification.
  Public production keeps accepted 0.0.21, its 754 input records and 37.1794%
  linked / 62.8206% outside. User gameplay and all four submitted n0021 dashboard
  checks are accepted. Preserve their result markers, notes and timestamps.
- A private reduced candidate has 29 new roots (8 N2O / 21 NEW), 3,520 input
  bytes, +3,496 emitted bytes: provisional 317,968 / 845,824 = 37.5927% linked,
  62.4073% outside. All accepted records remain identical and in order. This is
  pending final qualification, not credited public progress or a 0.0.22 release.
- The original --combat-inputs tool adds short ordinary face-button presses,
  preserving the original initial prefix and loop duration. Its reference passed
  37 captures through frame 36308; the first 17 match accepted hashes. Exploration
  ended with 29 retained roots, one held whole input and 74 exact frame checks.
  Keep all 48 whole-owner exclusions. No reduced emitted guard intersects them;
  accepted capture scaffolds can span un-emitted gaps and must not be removed
  merely because their input scaffold spans a held gap.
- The reduced O3 binary passed 1,550 preliminary captured-input/GTE replay cases.
  Fresh strict combat then passed 90 comparisons, zero failures, 37 exact RGB
  frames and three identical fresh test-card files. The second strict deep route
  was observed through frame 12000 with 64 comparisons and zero failures before
  execution access was lost; its completion is unverified. Inspect surviving
  logs if access returns. Do not assume transport loss means the process either
  finished or stopped, or add preliminary tests to final-only totals.
- Finish/verify strict routes with collection/preblocks/traces/edge options clear,
  fresh fail-fast replay without keep-going, normal diagnostics-OFF/O3 build
  with empty qualification include and matching source/range hashes, the normal
  movie/controller/pause/quit fixture and image inspection, 80 source tests,
  99-file audit including 128 KiB Windows CRLF bounds, dashboard import preview,
  Windows/Linux and portable package/update CI, and actual public ZIP audit.
  Publish 0.0.22 only after that work. Standing main/release authorization remains.
- The private recovery archive in the project files saves the reduced config,
  selector/manifest, exclusions, accepted frame/card hashes, original helper
  scripts, preliminary replay receipts and compiler cache. Its latest saved
  snapshot predates completion of the first strict route; the completion totals
  above were observed afterward. Raw witnesses/captures/saves are omitted.
  Restore metadata under .local/qualification-022 and compiler-cache under
  .local/compiler-cache. Inspect checkpoint phase and repeat any required final
  tests with fresh output/card directories if scratch was lost. Never publish
  exploratory configs or compiled game/cache data.
- Keep ccache compiler-content/source/flag checks, both Release flag sets
  -O3 -DNDEBUG, two compile jobs, serialized game sessions and the unmodified
  pinned framework. Reuse the verified existing USA input; no new upload,
  repeated campaign or valued-save overwrite is required. USA-only scope and
  deferred EU/assets/clock work remain. Continue the code/data inventory.
- Eventual TESTING.md definitions need fresh n0022 checks and matching prose,
  metric and release date while preserving submitted n0021 results exactly.
  Keep project id nitrogen, one strict definition block and the result markers.
  Use the linked dashboard format/importer and SHA guards for concurrent edits.
  The planned focused scope is updating, opening playback/menus/short gameplay/
  pause/quit, and optional natural high-score entry. Startup performance was
  already accepted and needs no unrelated repeat.


- Version 0.0.22 adds 29 observed native roots (8 N2O/21 NEW), +3,496
  emitted bytes. Preserve all 754 earlier input records in order and all
  48 whole-owner exclusions/fallback. Final diagnostic/normal coverage
  agrees: 317,968 / 845,824 = 37.5927% linked, 62.4073%
  outside. Boot is unchanged. Unobserved/failed candidates earn no credit.
- Final strict O3 tests pass 163 live + 1550 replay = 1713 comparisons,
  zero failures; 74 exact frame checks and 3 fresh-card files match.
  All 29 identities were observed (29 direct/0 continuation-only).
  Normal hashes match, hooks are absent, movie/controller/pause/quit checks pass.
  All 80 source tests and the 99-file source audit pass. Both Release flag sets
  remain -O3 -DNDEBUG. The new --combat-inputs route uses ordinary face buttons,
  not guest patches; requested input does not prove each weapon or later level.
- TESTING.md n0022 contains fresh focused Windows checks; player acceptance is
  pending. Accepted n0021 results/notes/timestamps and their markers are preserved
  exactly. The actual dashboard importer accepts definitions and preserves prior
  results. No repeat campaign, upload or valued-save overwrite is needed.
- NEW CPU closure admits only explicitly source/body-hash-reviewed small CPU
  leaves despite low static confidence; returns/control flow and sensitive
  contexts are checked before emission and every entry still needs qualification.
  It also rejects any intersecting failed-owner interval in its static call closure. Reviewing local jump geometry does not override an
  existing exclusion; NEW 0x8002A44C..0x8002A9A8 stays held. New boot/movie-control
  callers and all other unresolved indirect closures retain fallback.
- Private recovery PRIVATE-Nitrogen-Squared-0.0.22-recovery.tar.gz contains
  compiler-cache game objects and qualification metadata; keep it private.
  Source checkpoints belong in Git. Restore metadata to .local/qualification-022
  and compiler-cache to .local/compiler-cache. Reuse the verified existing USA
  upload. Inspect checkpoint phase; incomplete exploratory work is unqualified.
  USA-only scope, deferred EU/assets/clock work and per-batch code/data mapping
  remain as described above.


- Published 0.0.22 code 51d6a71be26e1ebc88ac0d7cd017a9bf77b01485 passes all required source,
  Windows/Linux runtime and portable package/update workflows. Run IDs:
  41229625471, 41229625432, 41229625466. Actual public assets,
  checksums/digests, 1,750-file owned manifest, x64 launcher,
  Python license and 99-file source inventory were downloaded and verified.
  Preserve assets/tag. This receipt needs no rebuild, VERSION bump or repeat
  player check. Focused Windows/dashboard n0022 player acceptance is pending;
  preserve earlier submitted results by version.


- The user submitted v0.0.22 dashboard results in main commit
  a6183f1b4c594ea5de166436f8f195c70ba94882. All three checks pass:
  N2-UPDATE (launcher/private-build refresh), N2-PLAY (opening playback, menus,
  short gameplay and defined pause/quit scope), N2-SCORE (high-score display).
  Accept that reported Windows route, superseding pending 0.0.22 status above.
  Do not infer a new campaign, save/reload check, every weapon or exact FPS.
  Preserve both n0021/n0022 reports, notes, timestamps and result markers exactly;
  the current report uses project-prefixed version/check IDs. Definition IDs
  remain stable. Future versions start with fresh checks. This docs-only note
  needs no VERSION bump, rebuild, release replacement or repeat player test.
  Coverage remains 37.5927% linked / 62.4073% outside.


- The user accepts the change in approach for the next native batch after small
  gains in 0.0.20–0.0.22. Prioritize larger uncovered call paths and expand ordinary
  automated controller routes to reach them. Rank by potential newly emitted
  bytes and verified reachability; avoid defaulting to another broad tiny-leaf
  pool. Keep whole-owner exclusions, final reduced O3/replay/normal qualification,
  code/data mapping and all source/platform/release checks. Do not promise a
  percentage jump or credit unobserved/failed candidates. Work solo and checkpoint
  meaningful stages. Current accepted baseline is 0.0.22 at 37.5927% linked.

- Active 0.0.23 work follows the larger-call-path strategy. The accepted 0.0.22
  diagnostic guarded manifest and execution identity were reproduced exactly.
  Static ranking proposes 32 larger N2O targets and 12 supporting CPU routines
  (31,088 input bytes; 29,256 seed bytes outside current linked ranges). All 44
  pass preflight generation; none is qualified or credited yet. Keep production
  VERSION/native selection at accepted 0.0.22 until final reduced checks pass.
- Original route tooling now accepts bounded JSON controller scripts and optional
  copied disposable test cards. Existing default/deep/all-flag queued inputs and
  captures were checked unchanged. The expanded tutorial reference completed 37
  captures; menu discovery is being refined from actual captures. Requested
  inputs and short prefix hashes remain discovery hints. Qualify exact guarded
  identities, reduce to passing observed roots and repeat final O3/live/replay/
  visual/normal/source/platform/public-release checks before promotion.

- The user's additional USA memory-card input is used only through disposable
  copies; preserve the uploaded original and verify its fingerprint. The first
  two targeted exploratory routes pass 94 comparisons, zero failures, and 55
  exact frame checks. They observe nine candidate roots (4,664 input bytes),
  including a larger gameplay/render helper in level 12. These are exploratory
  receipts, not final reduced qualification or credited release coverage.
  Save-slot and fresh-card create/load/overwrite paths are being tested next.
- Seeded controller routes copy file bytes into a fresh writable directory and
  record initial file fingerprints. Test copies must not inherit the uploaded
  file's Library identity. Keep raw cards/captures/witnesses private and preserve
  n0021/n0022 dashboard results when defining a later release's fresh checks.

- The 0.0.23 execution environment became unavailable after four targeted final
  reduced strict routes and fail-fast replay completed. Their observed receipts:
  loaded game: 56 live/650 replay/31 exact frames; disposable saved-slot overwrite:
  51/550/34; fresh setup create/load/overwrite: 89/1425/33; second saved slot:
  44/550/31. Total 240 live + 3,175 replay = 3,415 passing comparisons,
  zero failures, 129 exact frames and 12 matching output-card file comparisons
  (three per route). Actual saved-game stages were level 12 and level 9.
  The uploaded original fingerprint was rechecked unchanged.
- The reduced O3 diagnostic build keeps 13 roots, 6,972 input bytes and adds
  6,960 emitted bytes: provisional 324,928 / 845,824 = 38.4156% linked,
  61.5844% outside. All 783 accepted input records/order and guarded identities
  match the accepted baseline; reduced identities match the observed pool.
  All 48 exclusions remain. The 31 unobserved pool candidates stay unselected.
  This is NOT yet a qualified public release or credited production coverage.
- The expanded pool tutorial route completed 37 exact frames with no new selected
  target calls; count it as compatibility evidence, with zero native comparison
  or replay credit. The reduced broad regression had only just started when
  access was lost. Its completion is unverified. Do not assume transport loss
  means it either stopped or completed, or add exploration counts to final totals.
- The current private 0.0.23 recovery archive was saved successfully after the
  reduced diagnostic build, before those four strict routes finished. It contains
  the reduced config, selector/manifest, original helpers and compiler cache.
  Later strict receipts above were observed afterward; raw witnesses, cards,
  captures, game C/guards and binaries are omitted. Restore/recollect required
  evidence if scratch was lost. The compiler cache stays private.
- Finish the reduced broad regression, exact frame/card checks, normal O3
  diagnostics-OFF build with empty qualification include and matching hashes,
  normal movie/controller/pause/quit fixture and image review, code/data inventory,
  final source tests/audit/CRLF bounds, fresh n0023 dashboard import preview,
  Windows/Linux and portable release CI, and actual public ZIP audit.
  Earlier 80 source tests passed for the route tooling, not the unfinished final
  0.0.23 source/version state. Preserve n0021/n0022 submitted results byte-for-byte.
  Main remains accepted 0.0.22 at 37.5927%; do not publish an unqualified config
  or substitute a tooling-only release for the viable native batch.

- Version 0.0.23 retains 13 observed N2O save/load, gameplay and supporting roots,
  +6,960 emitted bytes: 324,928 / 845,824 = 38.4156% linked,
  61.5844% outside. All 783 accepted input records/order/guarded identities
  and all 48 exclusions remain. NEW/boot are unchanged. Larger 44-root exploration
  earns no unobserved credit. Final fresh regeneration removes stale pool parts.
- Final strict O3 routes pass 240 live + 3,175 fail-fast replay =
  3,415 comparisons, zero failures; 166 exact frames and three output-card
  files per route match reference bytes. All 13 identities are observed
  (11 direct/2 continuation-only). Disposable copied-card
  load/save/overwrite checks preserve the uploaded original fingerprint. Keep raw
  card/capture/witness data private. These game entries retain compatibility services.
- Normal diagnostics-OFF source/range hashes match, hooks are absent, both Release
  flags remain -O3 -DNDEBUG and the movie/controller/pause/quit fixture passes.
  All 80 source tests, 99-file audit, CRLF text bounds and dashboard preview pass.
  Final platform/package/public-asset receipts are pending until recorded.
  Fresh n0023 checks do not inherit accepted n0021/n0022 passes; their submitted
  markers/results remain byte-identical. No new campaign, upload or valued-save
  overwrite is requested. Continue code/data mapping and work solo.
  New private checkpoints retain the exact tested developer binary, execution
  contract and bundled OpenBIOS/MIT notice, with SHA/staging verification before
  reuse. Keep every compiled game artifact private, out of Git/releases.

- Published 0.0.23 code 08f42bff99ac548026063a68429335ed944b519c passes source workflow
  41250851616, Windows/Linux runtime/renderer workflow 41250851661 and portable
  package/update workflow 41250851730. All required jobs, including publication,
  pass. Actual three release assets, SHA/digests, 1,750-file owned manifest,
  x64 launcher, Python license and 99-file source inventory were downloaded
  and audited. Preserve the published tag/assets. This docs-only receipt requires
  no VERSION bump, rebuild or repeated qualification. Fresh n0023 player checks
  remain pending; preserve n0021/n0022 submitted results exactly. The local normal
  cache repair changed no source; exact tested binaries/contracts are retained
  only in private recovery, never Git/releases.

- The user submitted v0.0.23 project-lab results in main commit
  a1c83008b716cf8ea866dd58e648964934f138e6. All three nitrogen:n0023 checks pass:
  N2-UPDATE (update/private-build refresh), N2-PLAY (opening playback, menus and
  short gameplay with the defined control/pause/quit scope), N2-LOAD (familiar
  existing saved-slot load). Accept the reported Windows route, superseding
  pending 0.0.23 player status above. Do not infer a new campaign, deliberate
  save overwrite, every branch or exact FPS. No repeat test/upload/reimport is
  needed. Preserve all n0021/n0022/n0023 reports, notes, timestamps and markers
  exactly and keep definition IDs/steps/expected results stable. Future releases
  need fresh checks. This docs-only acceptance leaves VERSION/releases/native
  config unchanged; no rebuild/requalification is needed. Coverage remains
  38.4156% linked / 61.5844% outside.

- All three build workflows ignore TESTING.md-only push changes so
  Project Lab submissions do not start source/runtime/package builds. Mixed
  commits with code/config/workflow or any other file still run the full checks.
  Pull-request checks and manual portable workflow_dispatch stay unchanged. Keep the same path
  filter on all release-gating workflows so a code release cannot wait for an
  intentionally skipped required workflow. This CI-only change does not bump
  VERSION or replace published release assets.


- Active 0.0.24 implements the user's window-driven resolution/aspect, integer
  UI plateaus and nearest sampling request. It is a host presentation update;
  native selection stays at 796 records/all 48 exclusions and 38.4156% linked.
  Work solo. Preserve submitted n0021/n0022/n0023 reports byte-for-byte.
- Real-X11/EGL worker-on menus, first-level gameplay/firing and resizes pass.
  Wider projection inside the authored viewport fixes observed tunnel-edge gaps;
  portrait crops 4:3. Exact weapon projection metadata preserves the complete
  widget. Dedicated menu ray sprites use uniform cover/crop. The earlier
  native-wide-only candidate is superseded. All 83 source tests pass. Nearest
  movie sampling is checked using the actual half-texel mapping.
- Final worker-off menu, normal diagnostics-OFF/O3, 83 source tests without skips,
  106-file audit/CRLF bounds and dashboard import preservation pass. The normal
  manifest matches the accepted selection; its movie/analog/fire/pause/quit fixture
  passes, with no hooks or instrumentation. Complete Windows/Linux/package and
  public-asset checks before calling publication verified. Standing main
  and release authorization applies once qualified. SDL offscreen resize is
  invalid evidence; use actual window surfaces. Two compile jobs; serialize
  builds/game sessions. Preserve private tested binaries/contracts and recovery
  receipts. Never publish disc bytes, derived game C/guards, compiled game
  modules or private recovery identifiers. The pinned framework stays unmodified.

- Published 0.0.24 code 6299190 passes required main source, Windows/Linux runtime
  and portable workflows 41282459215, 41282459204, 41282459250. Actual public three assets, SHA/digests,
  1,757-file owned manifest, x64 launcher/Python license and 106-file source
  inventory are downloaded/audited. Preserve published assets/tag. This receipt
  is docs only; no VERSION bump, rebuild or repeat local checks are needed.
  Fresh n0024 Windows display/update/sharpness player checks remain pending.
  Preserve all earlier submitted reports. Coverage stays 38.4156% linked / 61.5844% outside.

- The user reports 0.0.24 presentation regressions: split attract/menu phrases,
  widescreen squashing, omitted bonus weapon/shield UI and broken help panels.
  Earlier local checks did not cover those screens and do not supersede this
  player report. Work on ui-coherence-025; do not replace published 0.0.24 assets.
  The user now requests a 2x minimum and square-pixel output. UI steps use a
  365x240 reference; 3D resolution/aspect still follows the window.
- The candidate replaces per-glyph anchor thresholds with shared roles, records
  actual scanout height, treats menu art and footer decorations as UI separately
  from the ray field, and adds observed bonus-icon/count palettes. Opaque HUD
  font packets distinguish the score stack from semi-transparent menu sentences.
  Nearest presents remove their half-texel zoom and UI geometry compensates the
  PS1 raster bias to target physical integer pixels. Qualification is ongoing;
  no native selection changes or new coverage credit. Require expanded real-
  window menu/help/bonus/level-end checks, pixel-grid evidence, worker on/off,
  normal O3/no-hook smoke, source/dashboard and platform/public-asset checks.
  Preserve submitted results byte-for-byte and work solo.

- 0.0.25 local qualification passes: coherent attract/menu phrases and art,
  exact square score blocks at 2x/3x in four window shapes, complete observed
  shield/count widget, and final popup fill/border/text with worker on and off.
  Boundary captures verify 1094x720=2x, 1095x720=3x, 1095x719=2x game areas.
  The sampled opening movie has exact 3x3 blocks; portrait framing is inspected.
  The separate normal movie/analog/fire/pause/quit fixture passes at frame 4500;
  normal manifest matches accepted selection, diagnostics are OFF, both flags
  are O3, qualification include empty and instrumentation/interposition absent.
  All 83 source tests pass without skips; 106-file audit/CRLF/dashboard preview pass.
  Preserve all submitted reports and uploaded original card. Platform/package/
  public-asset qualification remains required; fresh n0025 player checks pending.

- 0.0.25 publication is verified at immutable code/tag
  5b15c8466be50a0b2cc2be3a95121fc4533e91bb. Main source checks 41290793754,
  Windows/Linux runtime and renderer checks 41290793790 and portable package/
  update/publication checks 41290793802 all pass. Actual downloaded release assets
  pass tag/latest/SHA/digest checks, the 1,757-file owned manifest, x64 launcher,
  Python license and 106-file source equality after Git line-ending normalization.
  Windows ZIP SHA-256 is
  aa361596ac4eae269ee5aaeb8dd8d4b8fe108f1c798199733f95a0fd11ac474f.
  This supersedes pending platform/publication status above. Preserve published
  assets and tag; this receipt is documentation only, with no rebuild or VERSION
  bump. Fresh n0025 player checks remain pending. Preserve all earlier submitted
  reports exactly. Native coverage stays 38.4156% linked / 61.5844% outside.


- Published 0.0.29 code/tag 36ff596c54cf13c7ac48f4ecf789ac41d3f1bae0 adds original guarded
  in-game Video/Audio extensions: zero centering, desktop modes, AUTO/2X/3X/4X/6X
  HUD, independent 25–200% world raster and persisted Master volume. Controls,
  Audio and Extras are renamed; F1 no longer duplicates Master volume. This is
  host/product work: all 796 native records/48 exclusions and 38.4156% linked /
  61.5844% outside stay unchanged. Work solo and keep the pinned SDK unmodified.
- All 92 source tests, 123-file text/CRLF audit, SDK and actual adapted renderer
  synthetic world/UI proofs, render queue/worker checks, ordinary X11 worker-on/off
  menus/gameplay and final normal O3/diagnostics-OFF/no-hook fixture pass. Renamed-
  header diagnostic and normal checks are repeated; exact private binaries,
  execution contracts and BIOS/license are saved privately. Keep raw game inputs,
  derived C/guards, compiled game, captures and cards out of Git/releases.
- Do not name the project options header game_options.h: MSVC nested include lookup
  shadows the SDK header. Use compat/nitrogen_options.h. F11 now changes the shared
  Video preference; the provider test must not expect the former host callback or
  claim an offscreen fullscreen transition. Runtime matrix jobs finish independently.
- Main source CI41395518250, Windows/Linux runtime/renderer CI41395518219 and
  portable Windows/Linux CI41395518236 pass, including publication. All five actual
  public assets, tag/latest/SHA/digests, Windows 1774-file manifest/x64 launcher/
  Python license, Linux 125-file manifest and 123-file source equality are audited.
  Preserve published v0.0.29 assets/tag. This receipt is docs only; no rebuild or
  VERSION bump is needed. Fresh n0029 player checks remain pending. Carry the
  unresolved optional Linux check; preserve all earlier result bodies exactly.
  Virtual X11 cannot verify real desktop mode transitions; pause-options was not
  observed locally. Intermittent Windows level-entry stutter remains OPEN and
  clocks remain unchanged. No unrelated campaign, upload or save overwrite is needed.

- 0.0.30 repairs complete help/Controls layers and Audio layout/fills. Master is
  immediately above SFX; Play in order's song title stays text only even selected.
  Volume/render tracks use the original luminous fill; Audio's bottom arrow clears
  the last row and Video uses help-atlas direction icons. Controls context expires
  when its presenter stops. Work solo, keep SDK unchanged, preserve submitted
  results and carry the unresolved Linux check. Four n0029 passes remain historical;
  Audio fails for graphics/order despite working volume. Coverage remains
  38.4156%/61.5844%; level-entry stutter remains OPEN and clocks unchanged.
- The recovered 0.0.30 normal O3 build matches the observed diagnostic execution
  identity and accepted native manifest. Diagnostics OFF, empty qualification
  include and no comparison/replay hooks are checked; the normal three-movie/
  controller/SDL_QUIT fixture passes at frame 4500. All 92 source tests without skips, the 123-file
  audit and Dashboard parser/unchanged submitted tail pass after recovery.
  Platform/publication receipts must still be recorded; fresh n0030 player
  checks remain pending. Keep a private recovery with the final production build,
  execution contract, compiler cache and scalar qualification receipts.

- Published 0.0.30 code/tag ed3cdb686e6c0af1d1300394a0e3dacae2242ebe passes source CI
  41569591629, Windows/Linux runtime/renderer 41569591595 and portable
  package/publication 41569591582. All five actual public assets/tag/latest/
  checksums/digests, Windows 1774-file and Linux 125-file owned manifests,
  x64 launcher/Python license and 123-file source equality are audited.
  Preserve immutable tag/assets. Receipt is docs only: no VERSION bump/rebuild.
  Fresh n0030 player checks remain pending; Linux is carried unchanged, submitted
  results preserved. Coverage 38.4156%/61.5844%, transition stutter OPEN, clocks unchanged.

- 0.0.31 repairs the 0.0.30 title-preview regression. Rank 441 is shared by help
  and 32 textured preview-frame quads; rank alone is not UI ownership. Recognize
  bevel quads and four exact help-arrow cells separately. Keep preview polygons
  on their world transform and retain Audio/Controls repairs. The negative
  preview-segment fixture fails on 0.0.30 and passes on 0.0.31; all 92 final source tests without
  skips, the 123-file audit, Dashboard parser and exact results/check carry pass.
  Actual X11 with the worker ON/OFF title/logo, usual/wide/portrait and Main/Audio/Controls
  help routes pass. Normal/platform/publication qualification is still required.
  Coverage 38.4156%/61.5844% unchanged, level-entry stutter OPEN, clocks unchanged.
- The final 0.0.31 normal O3 build matches the diagnostic identity and accepted
  native manifest; diagnostics OFF, empty qualification include and no hooks
  are verified. The three-movie/controller/SDL_QUIT fixture passes at frame4500.
  Platform checks/publication audit are pending; fresh n0031 player checks remain
  untested and unsubmitted n0030 checks are carried unchanged.

- Published 0.0.31 code/tag 513bde19318764125c742782cf6e8df7e7c6243a passes source CI
  41639675693, Windows/Linux runtime/renderer 41639675754 and portable
  package/publication 41639675731. All five actual public assets/tag/latest/
  checksums/digests, Windows 1774-file and Linux 125-file owned manifests,
  x64 launcher/Python license and 123-file source equality are audited.
  Preserve immutable tag/assets. Receipt is docs only: no VERSION bump/rebuild.
  Fresh n0031 player checks remain pending; Linux is carried unchanged, submitted
  results preserved. Coverage 38.4156%/61.5844%, transition stutter OPEN, clocks unchanged.

- Starting with 0.1.0, each release gets `release/x.y.z` at its final tested
  code commit. Preserve that branch and the matching public tag/assets; later
  documentation receipts remain on main. Remove retired unused work branches
  only after confirming no open PR and that their commits are already in main.
  The owner explicitly authorizes this cleanup; preserve changed/unmerged work.
- Active 0.1.0 repairs multi-line Audio track-name anchoring, adds cancellable
  main-menu Back hold (3 monotonic seconds; closing... fades in over the first
  second at the game area's top third), and removes Tab hold Turbo through the
  title host bridge. Preserve Tab for ordinary UI and pinned SDK unchanged.
  Native selection/coverage stay 796 records, 48 exclusions, 38.4156%/61.5844%.
  Final runtime/normal/platform/publication qualification is still pending.

- Starting at 0.2.0, release updates must distinguish compiled-game inputs from
  launcher-only changes. Require recompilation when game/runtime build inputs
  change; otherwise reuse the current compatible compilation. A release VERSION
  bump or launcher/docs-only edit must not by itself invalidate that compilation.
  Implement and qualify this behavior for 0.2.0, not the current 0.1.0 release.
- Until the owner explicitly declares 1.0.0, major game-code updates increment
  the middle version component (0.x.0); patches and launcher updates increment
  the final component (for example 0.2.0 -> 0.2.1). A game-code patch still
  requires rebuilding when its compiled inputs change. Release branches use the
  complete version, including patches, such as release/0.2.1.

- 0.1.0 final local presentation/source checks pass: complete Audio track values,
  normal title/Main and Audio help, worker on/off, usual/wide/portrait resizes,
  main-only hold cancellation/clean quit and physical X11 Tab without Turbo.
  The parent presenter must stay on normal dispatch; only the guarded small
  header helper is wrapped. Its caption uses brightness on both font passes,
  not the imported menu's positional ghost-transition parameter or highlight.
  All 93 source tests without skips, 124-file audit and actual Dashboard parser/
  carry/result-tail checks pass. Normal/platform/publication checks remain pending.
  Future 0.2.0 policy remains scheduled; preserve SDK, native selection and clocks.

- The final 0.1.0 normal production build matches the diagnostic execution
  identity and accepted native manifest. Diagnostics OFF, empty qualification
  include, no comparison/replay hooks and both O3 Release flag sets are checked.
  Its three-movie/analog/fire/SDL_QUIT fixture passes at frame 4500. Complete
  final Windows/Linux CI, actual public-asset audit and retired-branch cleanup;
  then retain release/0.1.0 at the immutable release code and record receipts on
  main only. All fresh n0100 player checks remain untested until reported.

- Published 0.1.0 code/tag de0866abaeeb1b33ca4aa11990224b66f190a527 passes source CI
  42325757345, Windows/Linux runtime/renderer 42325757942 and portable
  package/publication 42325757319. All five actual public assets/tag/latest/
  checksums/digests, Windows 1775-file and Linux 126-file owned manifests,
  x64 launcher/Python license and 124-file source equality are audited.
  The 27 retired merged work branches are removed; main and release/0.1.0 remain.
  Preserve immutable tag/release branch/assets. Receipt is docs only: no VERSION bump/rebuild.
  Fresh n0100 player checks remain pending; Linux is carried unchanged, submitted
  results preserved. Coverage 38.4156%/61.5844%, transition stutter OPEN, clocks unchanged.

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

- Published 0.1.1 code/tag/release branch 3c806ae8788653e455ea6213019777b5ae86983e passes source
  42330340563, Windows/Linux runtime/renderer 42330340586 on its release
  branch, then Release 42330636415 on main at the identical SHA. All five public
  assets, combined/legacy hashes, owned manifests and 125-file source equality
  pass. The 0.1.0 redundant source ZIP is removed after verification; original
  platform ZIPs/tag/branch remain intact. Sidecars bridge through 0.1.x, then
  two ZIPs plus SUMS from 0.2.0. Local 101 tests/no skips, copied-updater negative/
  positive test, Dashboard carry/result tail, worker ON/OFF and normal O3/no-hook
  frame4500 smoke pass. Title-only Back holds for TWO seconds with first-second
  fade; ordinary Main Back is restored. Native coverage/clocks unchanged;
  level-entry stutter OPEN. This receipt is docs-only; preserve release code.
  Fresh n0101 player checks pending; future 0.2.0 reuse policy remains planned.

- Branding provenance clarified by the owner: logo.png (orange/cyan N-squared)
  was made by the owner in GIMP and is authorized for public GitHub use. Preserve
  the supplied artwork when integrating it. The supplied pixel N icon.png is
  ripped from N2O's PS1 memory-card save icon; it is commercial game content,
  not original project artwork. Never commit or ship that PNG, derived public
  icons, or encoded copies of its pixels in source/bootstrap/release packages.
- For the next branding update, locate the memory-card icon in the player's
  verified disc resources and decode/cache it privately under .local. Its exact
  source container/offset has not yet been identified. The current extractor
  preserves containers and does not export a standalone icon. Use the owner's
  project logo as a public/first-run fallback before a verified import exists.
  This provenance note implements no branding/runtime changes and needs no
  VERSION bump, release, private rebuild or repeat player check.

- Active 0.2.1 includes the owner-verified 0.2.0 compatibility changes; the owner
  explicitly skipped a separate 0.2.0 release. Keep 0.2.1 on dev until its new
  launcher UI is verified and explicitly cleared for publication. No Link Play.
  Use original N2O-inspired tunnel artwork and the exact owner-created N² logo;
  never ship the ripped memory-card icon. launcher_assets.json separately gates
  these two PNGs by exact path/hash; source_package.json remains text-only.
  The compiled-game fingerprint must remain identical to verified 0.2.0.


- 0.2.1 UI revision: the owner found the Tk canvas launcher clunky and authorized
  adapting Recompia's actual frontend/Tauri shell and adopting GPL-3.0-or-later
  for original project code. Preserve Recompia provenance and all component
  notices; prior MIT distributions retain their permissions. Only original
  N²/tunnel artwork is public. Runtime C11/C++17 inputs remain identical.
- The owner explicitly requests SOURCE ZIP delivery and will push personally.
  Do not push, promote, tag or publish this revision. Keep it at 0.2.1 on dev.
  SOURCE_UPDATE.md records the two tracked deletions required for ZIP overlays.


- 0.2.1 follow-up: owner accepts the Tauri look/feel but reports Play appearing
  stuck until Stop; no release clearance. Publish startup/verification/running
  transitions even within the progress throttle, use unbuffered run_runtime
  output, isolate worker stdin from the service protocol and require the actual
  Runtime started PID receipt for Running. Retain full disc validation and the
  accepted compiled-game fingerprint. The Linux 21f7b1d host/package/interface
  succeeded; its subsequent synthetic media check failed the fixed 180 ms
  audio-startup assumption. Keep the same progress criteria with a bounded wait,
  no main-thread/event assistance and no runtime/player-clock changes. Deliver
  source only; the owner still pushes personally. Keep version 0.2.1 on dev.
