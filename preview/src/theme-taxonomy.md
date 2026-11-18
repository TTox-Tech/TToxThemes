# Theme families and colour variants

TToxThemes is the collection. MinimalistiX is the glass desktop theme; Sterling, Vino and Graphite are its colour variants. V-R-V3N0M is a separate symbiote theme. A new colour does not create a new layout, and V-R-V3N0M is not a fourth MinimalistiX colour.

The UI selects Theme first, then Colour only where multiple variants exist. `TToxThemeFamilies` declares ownership; the existing flat variant/material records remain as a compatibility layer for saved preferences. Canonical links use `?theme=minimalistix&colour=sterling` or `?theme=v-r-v3n0m`. Older `?theme=sterling|vino|graphite` links remain accepted. The last MinimalistiX colour is remembered when switching themes.

## MinimalistiX composition

The five screenshots supplied on 18 November 2026 are the composition reference: narrow floating pill bar, bare clock, unframed sparkline widget, overlapping file/terminal glass sheets, narrow right-side dock, three-column HUD with Kali row, top terminal drawer and a compact search launcher.

`src/minimalistix-design.json` keeps the native palette/mode/token snapshot and percentage placement together. `tools/build-minimalistix.cjs` generates the browser design data and embeds `src/minimalistix.html`. All three colours use the same template/controller/CSS. Sample records live with other provider fixtures in `desktop-fixtures.js`, and runtime metrics/container/service state is shared with the existing inspectors.

The wallpaper is a CSS/SVG geometric placeholder inspired by the screenshot's neutral composition, not a recovered original illustration. The V-R-V3N0M wallpaper is unchanged. The mobile reference preserves desktop proportions in a horizontally scrollable viewport.

## Behavior and limits

H opens the HUD; grave/backtick opens the retained five-tab drawer; Space opens the launcher; N shows a five-second actionable notification; Escape closes an overlay. Inputs keep normal typing behavior. The top bar includes the existing control-center button.

Sample windows support focus, close/reopen, maximize/restore and bounded titlebar dragging. Workspace buttons switch visible sample windows. These are browser-session window states, not a native workspace/layout manager. File navigation is a sample tree and never reads the real filesystem. Drawer tabs retain a scratch buffer and show shared process/container/log data; there is no terminal command execution or native tmux connection. Kali/tool/power actions are demo-only. CPU replay stops when the theme or page is hidden. Lite removes blur/shadows and sparkline rendering and samples at five seconds.

DOM integration tests check the hierarchy, colour switching, window state, HUD actions, drawer state, launcher keyboard path, Wi-Fi routing and timer cleanup. They do not verify rendered pixels, actual GPU behavior, operating-system effects or target hardware performance.
