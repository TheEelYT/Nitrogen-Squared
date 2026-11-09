# Development, verification and releases

This policy supersedes the earlier standing approval to publish updates.
Only the owner can clear a verified candidate for release. Passing automated
checks or individual Dashboard checks does not itself grant that clearance.
The approval rule is also recorded in main's agent instructions as a
documentation-only policy change; this does not approve any development code.

## Branches

Keep main, the persistent dev branch and release/x.y.z branches for versions
that have actually been released. Start dev from the current main once. Work
and bug fixes stay on dev under the planned version until verification finishes.
Preserve unfinished dev work; do not recreate it from main each time.

Source and Windows/Linux runtime/renderer checks run on dev. The Release workflow
also builds both platform packages on dev, validates the extracted launchers and
preparation/update paths, then waits for the exact commit's source/runtime checks.
It uploads a dev-COMMIT Actions artifact with both ZIPs and SHA256SUMS.txt for
30 days. It cannot create a GitHub release, tag or release branch from dev.
GitHub Actions artifacts require a signed-in account with repository access.

## Testing a candidate

1. Open the linked successful dev Actions run and download its dev-COMMIT artifact.
2. Unzip that artifact, then the Windows or Linux platform ZIP inside it.
3. Close the game and launcher before installing into the existing folder. Keep
   the complete .local directory, including saves, settings and the private build.
4. Use Play. The first 0.2.x setup establishes a compatibility identity;
   later compatible candidates reuse the same compiled game. Follow the candidate's
   app/TESTING.md or the dev branch's TESTING.md for focused checks.
5. Report noticed bugs against that candidate; fix and retest on dev. Existing
   published-version reports remain history. The current Dashboard follows main,
   so development-only reports can be supplied in chat until branch-aware sync
   is available; do not submit development-only definitions into released main.

## Owner-cleared publication

Before final testing, incorporate any newer main commits into dev, preserving
all submitted results. A merge or rebase that changes the candidate creates a
new commit that must pass its own automated checks. Record the tested candidate
and obtain the owner's explicit release clearance. If code changes afterward,
return to dev testing before publication.

Fast-forward main to that exact qualified dev commit and create release/x.y.z
at the same commit. Build/publish the release from main. Main's Release workflow
requires the exact commit's passing source/runtime checks and both platform
package checks. Recheck actual downloads, manifests and combined checksums after
publication. Keep the released branch, tag and assets immutable; later receipts
are documentation-only main commits. Bring those main receipts into dev before
the next update cycle. Do not create extra feature or unreleased release branches.

## Versions and compilation

Until the owner declares 1.0.0, major game-code updates advance 0.x.0; patches
and launcher updates advance 0.0.x. A version change alone never invalidates a
0.2.0-compatible game build. Changed runtime/native sources, build/generation
recipes, dependency pins or compiler options require rebuilding. Launcher,
documentation and test changes can reuse the existing compatible executable.

The owner verified 0.2.0 and skipped its publication. Version 0.2.1 includes those changes and the launcher redesign; it requires fresh UI verification and explicit release clearance. Do not create a 0.2.0 release branch or tag.
