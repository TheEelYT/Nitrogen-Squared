# Launcher provenance

Frontend adapted from [Dittobyte/Recompia](https://github.com/Dittobyte/Recompia),
commit `56fca2b30cc900971b8871eaa1b9b7343c91e16a`, retrieved 2026-11-09.
License: GPL-3.0-or-later (upstream launcher/package.json and src-tauri/Cargo.toml).
The full GPL v3 text is in ../LICENSE. Preserve this attribution in distributions.

Adapted files: src/theme.css, layout.css, components.css, ui.js,
 pages/home.css, pages/news.css, pages/settings.css and index.html.
Home rendering and the navigation lifecycle follow upstream home.js/main.js;
these are adapted to our own command/state contract. Modified 2026-11-09 by
N2O Recomp contributors: N² branding and original tunnel art, portable Python
backend bridge, three-page navigation, settings, release notes, progress and
reduced-motion/responsive behavior. Recompia's Pokopia backend, artwork, game
code, Link Play and shader system are not included.

Inter Variable: Rasmus Andersson, SIL Open Font License 1.1.
Lucide icons: Lucide contributors, ISC; includes Feather-derived icons under MIT.
Tauri: Tauri contributors, MIT OR Apache-2.0. Dependency notices are collected
in third_party/launcher/ before packaging. Preferred modifiable launcher source,
lockfiles and build instructions ship in app/launcher; Node and Rust are build
tools and are not required on the player's Windows PC.
