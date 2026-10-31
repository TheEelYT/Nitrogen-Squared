# Project continuity and update reporting

- The user authorizes repository updates. Keep the current working Windows
  baseline usable while advancing native execution in small qualified steps.
- The user gives standing approval to promote updates to `main` whenever the
  agent judges them ready. This covers 0.0.14 and future updates; do not request
  separate promotion approval unless the user changes this instruction.
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
