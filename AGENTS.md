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
