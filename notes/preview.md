# Browser reference import

Imported 18 November 2026 from preview source commit `68e448e310674a8ce92dcf5b4e044698bf73539c`, on top of native repository commit `ba8890970fd60426746219af1df69bc6f535b21d`.

## Files

Added `preview/` with browser assets, source, the user-supplied Venom interaction reference, test fixtures, build tools and historical PRD records. Added the repository entry-point README. Existing native source, SPEC and user wallpapers are preserved.

The hosted Site's `.openai/hosting.json`, credentials, execution files, dependency directories and archives are not part of this import. The Lucide library bundle is not vendored: version 0.468.0 is pinned in the npm lockfile and `npm run prepare:icons` copies its browser asset from the installed dependency. The supplied reference keeps its attribution.

## Verification

The imported browser source is checked with the theme, rounded-geometry, renderer, concurrent-tendril, desktop-controller, network-model, network-panel, PRD-coverage, desktop-model and complete-shell DOM suites. The shader has also compiled and linked with Mesa EGL. These checks do not render a browser or run a Linux desktop.

Native KDE/XFCE application, real network/device/container operations, browser visual QA and low-RAM performance remain outside this browser import. The historical PRD audit is explicitly labeled: newer native files in this repository are not counted by that old inventory.

## Requests to core

No shared-file changes are needed for this reference import. Future native integration should reconcile the reference's domain/provider contracts and tokens with `SPEC.md`; preview mock actions must not be presented as native capabilities.

## MinimalistiX alignment — 18 November

Theme/colour hierarchy corrected per the user. Added the screenshot-led MinimalistiX composition, shared-state HUD, drawer, launcher, sample file windows and an unframed metrics widget. The native palette/token snapshot is centralized in `preview/src/minimalistix-design.json`. Added a full-shell DOM regression for family switching, colour invariance, HUD actions, retained drawer state, launcher keyboard flow, Wi-Fi routing, workspaces/window geometry and lifecycle cleanup. Browser visual matching and native execution remain unverified.
