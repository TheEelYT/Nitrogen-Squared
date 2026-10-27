# Project continuity and update reporting

- The user authorizes repository updates. Keep the current working Windows
  baseline usable while advancing native execution in small qualified steps.
- The accepted 0.0.9 player baseline reaches level 4 with no issues reported and
  working saves/high scores. Do not require later-level progression before the
  next native milestone. Add focused checks for behavior affected by each change.
- The user also verified first-level gameplay without issues in 0.0.10 and
  authorized a substantially larger next conversion batch. Its temporary startup
  loading dip returns to 60 FPS and may predate that version; it is unconfirmed.
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
