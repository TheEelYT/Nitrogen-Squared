# Project continuity and update reporting

- The user authorizes repository updates. Keep the current working Windows
  baseline usable while advancing native execution in small qualified steps.
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
  enhanced/reference and renderer checks pass; Windows/Linux CI is pending.
  It enables no additional game ranges and needs no player rebuild or replay.
  Coverage remains 4.2642% / 95.7358%. The original user disc upload was recovered
  and privately reimported after the prior scratch workspace disappeared; reuse
  that existing saved input rather than requesting another upload unnecessarily.
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
