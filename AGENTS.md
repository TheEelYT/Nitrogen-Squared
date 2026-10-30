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
