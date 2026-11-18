# TToxThemes interactive preview

Interactive browser design reference imported from the hosted preview. Metrics/actions are demo data; native KDE/XFCE work lives at the repository root. The native source of truth is [`../SPEC.md`](../SPEC.md).

Source snapshot: `68e448e310674a8ce92dcf5b4e044698bf73539c` (18 November 2026 import). Hosted reference: https://ttox-theme-design-preview.aquaopera2.chatgpt.site

The PRD coverage pages retain the **17 November historical local-scaffold audit**. Their native inventory is not an assessment of the current repository, which already contains additional generator and daemon work.

To prepare the browser assets and verify the reference:

```sh
cd preview
npm ci --ignore-scripts
npm run prepare:icons
npm test
```

Serve `preview/dist/` with your preferred static server. Lucide is pinned in the lockfile and copied from the installed package; its library bundle is not vendored in Git.

## V-R-V3N0M desktop

Open `/?theme=v-r-v3n0m&view=desktop`. Terminal windows, widgets, dock, quick settings and notifications use a charcoal/silver symbiote material. The approved wallpaper and native cursor are preserved.

### Concurrent proximity

Each admitted surface owns its own `idle → seek → grow → hold → snap` simulation. When A holds the pointer and B comes within sensing range, B can seek, grow and hold independently. A is reserved until it crosses its own release radius; it is not reset because a closer button appears. A snapping back does not release B.

The registry sets sense/reach/release distances and concurrent budgets: Balanced 3, Full 4. Existing holds reserve capacity first. A container does not compete with its nearby child controls. Recoil normally finishes before a presentation layer is removed; an out-of-range, unreserved layer can be reclaimed to admit a new surface when the budget is full.

### Shared graphics, independent state

`venom-desktop.js` admits visible nearby surfaces. They share one off-DOM WebGL canvas, compiled shader program and buffer. Each simulation draws sequentially into this shared buffer and immediately copies its frame into its own local 2D presentation canvas, with a separate local thread overlay. Idle presentations retain their last frame. Text/input/click nodes are untouched and the decorative canvases ignore pointer events.

The number of live presentation pairs is bounded; resources are destroyed when changing modes, disabling effects or disposing the controller. Lite/reduced motion uses the static material. WebGL failure is labelled. Copy/compositing and real GPU cost need browser and hardware measurement.

## Renderer provenance

`src/reference/VenomButton.originkit.tsx` preserves the user-supplied **Venom Button — Originkit**. The generated native renderer retains its material lighting and Verlet rope solver, removes React, drawn pointer/skin coating and ghost autoplay, and adds sleep/visibility scheduling. The SDF and perimeter support rounded windows as well as pills. `src/venom-backend.ts` owns the shared graphics resources.

The isolated reference remains at `/?theme=v-r-v3n0m&view=material`.

## Build and checks

Node 24+ and Python 3; no framework runtime or browser-side compiler:

```
python3 tools/port-reference.py
node tools/build-renderer.cjs
node tools/stamp-assets.cjs
node tests/check-theme.cjs
node tests/check-surface-geometry.cjs
node tests/check-native-renderer.cjs
node tests/check-concurrent-renderers.cjs
node tests/check-desktop-controller.cjs
# Optional: requires EGL/OpenGL ES compiler libraries
python3 tests/check-shader-egl.py
```

The concurrent regression drives two real simulation instances through A hold/B seek, both hold, then A snap/B hold. It checks one graphics context/program and presentation into both local canvases, using fake DOM/graphics APIs. Other tests cover capacity reservation, release hysteresis, finite uniforms, geometry, cleanup and fallback. The shader has compiled/linked through Mesa llvmpipe on this build machine; that is not a visual/GPU performance check. Live browser QA and low-RAM KDE/XFCE performance remain unverified.

Assets have content-hash query versions so page refresh does not mix renderer, controller and theme files from different versions. Settings stay in browser-local storage. Lucide's license is bundled in `dist/assets/LUCIDE-LICENSE.txt`.

## Wi-Fi interaction and PRD coverage

Open `/?theme=v-r-v3n0m&view=desktop&panel=wifi` for the new network panel. The Wi-Fi quick tile opens details instead of immediately toggling the radio. The adapter is a deterministic, session-only demo: network inspection, test-passphrase connect/cancel, radio/scan, profile validation/review, keep/revert and visibility-scoped polling are implemented. No native network access is claimed. See `src/network-contract.md` for the pending NetworkManager/secret-agent/polkit boundary.

Run `python3 tools/embed-network-panel.py`, `python3 tools/build-prd-status.py`, then `node tools/stamp-assets.cjs` after source edits. Network checks are `node tests/check-network-model.cjs` and `node tests/check-network-panel.cjs`; coverage checks are `node tests/check-prd-coverage.cjs`.

`/prd-status.html` and `/prd-coverage.json` record all 107 unique FR/NFR IDs and 24 acceptance checks. The historical audit recorded native status as 35 scaffold-only, 66 missing, 5 unverified and 1 blocked input; 0 native requirements have been verified end-to-end. This is explicitly separate from the working browser reference. Scope changes and unresolved deviations, native inventory checksums, exact gaps and recovery order are recorded rather than silently dropping PRD features.

## Connected desktop interactions

`/?theme=v-r-v3n0m&view=desktop&panel=Bluetooth` starts the device → audio story. The inspector contains System, Bluetooth, Audio, Display, Notifications, Dev, Widgets, Media and Notes. `/interaction-depth.html` links 40 concrete paths, their earlier limitation, expected outcome, PRD relationship and verification boundary. These paths do not exhaust the product backlog.

`desktop-fixtures.js` keeps sample provider records separate from `desktop-model.js`, which owns validated preferences and domain state. `desktop-depth.js` presents that state and connects existing widgets, the control center and inspectors. Native device/system operations remain simulated. The original wallpaper is unchanged; the shader/native-cursor behavior is retained.

Settings, layout profiles, transport position and notes persist in the browser. Bluetooth connections, container/service state and notification history are session-only; a page reload does not fabricate connected devices or autoplay audio. Preference writes during slider drags are debounced. Notes have a separate debounce, flush on close/page hide, and retain the editor element during autosave. Storage failures are reported as session-only for notes.

System replay runs only while its inspector is open, visible and unfrozen. Media transport ticks while an applicable UI consumer is visible; it pauses its simulated clock while the document is hidden. This is not background MPRIS playback. No music is streamed. The explicit Test sound action is a short browser oscillator tone and cannot route to simulated Bluetooth hardware or control other applications. No microphone is captured.

The new domain/UI use direct DOM and native controls without framework runtime dependencies. `linkedom` is a test-only development dependency; it is not shipped in `dist/`.

```
npm ci --ignore-scripts
npm run prepare:icons
npm run test:depth
python3 tools/build-depth-status.py
python3 tools/build-prd-status.py
node tools/stamp-assets.cjs
```

The full-shell DOM test executes the shipped HTML/controller and assets. It checks inter-panel routing, paired audio fallback, cancellation, expired arming, denied actions, dependent widget summaries, notification recovery, power/effects coupling, layouts, transport boundaries and note recovery. It also checks that slider/editor nodes survive continuous edits and no inspector timers remain after close. This does not render CSS or verify audible output. Live browser, real KDE/XFCE and low-RAM performance checks remain pending.

## MinimalistiX theme and colour variants

**MinimalistiX** is one theme with **Sterling**, **Vino** and **Graphite** colour variants. **V-R-V3N0M** is a separate theme. Choose Theme first, then Colour. Existing colour links and saved choices remain supported.

Open `/?theme=minimalistix&colour=sterling&view=desktop`. This composition follows the five 18 November screenshot references: thin floating bar, bare clock and metrics, overlapping glass file/terminal windows, right dock, three-column HUD/Kali row, terminal drawer and launcher. Try H, backtick, Space, N and Escape while the desktop has focus. The UI remains a reference with sample providers.

The native colour/geometry snapshot and mode ladder are centralized in `src/minimalistix-design.json`; rebuild with `node tools/build-minimalistix.cjs` and `node tools/stamp-assets.cjs`. Run `npm run test:minimalistix` for the new full-shell DOM stories. See `src/theme-taxonomy.md` for composition, compatibility, sample behavior and verification limits. Browser visuals and native KDE/XFCE behavior remain unverified.
