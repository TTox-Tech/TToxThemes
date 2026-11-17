"""spicetify theme "TTox": color.ini with one scheme per palette + user.css.

dist/apps/spicetify/TTox/{color.ini,user.css}
"""
from __future__ import annotations
import lib

NAME = "apps_spicetify"; PACK = "apps"; ONCE = True
SIDEBAR_DARKEN = 0.12  # "sidebars slightly darker than body"; no token for this


def scheme(p: dict) -> dict:
    """spicetify colour keys -> hex without '#'."""
    v = {
        "text": p["fg_hi"], "subtext": p["fg"], "main": p["bg"], "main-elevated": p["raised"],
        "highlight": p["surface"], "highlight-elevated": p["raised"],
        "sidebar": lib.darken(p["bg"], SIDEBAR_DARKEN), "player": p["bg"], "card": p["surface"],
        "shadow": lib.darken(p["bg"], 0.5), "selected-row": p["fg"], "button": p["accent"],
        "button-active": p["accent_text"], "button-disabled": p["muted"], "tab-active": p["raised"],
        "notification": p["raised"], "notification-error": p["err"], "misc": p["line"],
    }
    return {k: c.lstrip("#") for k, c in v.items()}


def render(ctx) -> dict:
    t = ctx.tokens
    ini = ["; TToxThemes spicetify colour schemes. Generated, do not edit."]
    for name, p in ctx.all_palettes.items():
        ini.append("")
        ini.append(f"[{name}]")
        w = max(len(k) for k in scheme(p))
        ini += [f"{k.ljust(w)} = {c}" for k, c in scheme(p).items()]
    r = t["radius"]
    css = f"""/* TToxThemes spicetify user.css. Generated, do not edit. Colours come from color.ini via --spice-*. */
:root {{
  --ttox-r-control: {r['control']}px;
  --ttox-r-wash: {r['wash']}px;
  --ttox-r-popup: {r['popup']}px;
  --ttox-r-menu: {r['menu']}px;
  --ttox-font-ui: "{t['font']['ui']}", "{t['font']['ui_fallback']}", sans-serif;
  --ttox-font-mono: "{t['font']['mono']}", "{t['font']['mono_fallback']}", monospace;
  --ttox-select: rgba(var(--spice-rgb-button), {t['wash']['select_alpha']:.2f});
  --ttox-hover: rgba(var(--spice-rgb-subtext), {t['wash']['hover_alpha']:.2f});
  --ttox-hairline: rgba(var(--spice-rgb-subtext), {t['border']['hairline_alpha']:.2f});
}}

body,
.encore-text,
.main-type-mesto,
.main-type-ballad {{
  font-family: var(--ttox-font-ui) !important;
}}
.playback-bar__progress-time-elapsed,
.main-playbackBarRemainingTime-container,
.main-trackList-rowDuration {{
  font-family: var(--ttox-font-mono) !important;
}}

/* flat one-sheet panels */
.Root__top-container {{ background: var(--spice-main) !important; gap: 0 !important; padding: 0 !important; }}
.Root__nav-bar,
.Root__main-view,
.Root__right-sidebar,
.Root__now-playing-bar {{
  border-radius: 0 !important;
}}
.Root__nav-bar {{ border-right: 1px solid var(--spice-misc) !important; }}
.Root__now-playing-bar {{ border-top: 1px solid var(--spice-misc) !important; }}
.main-entityHeader-backgroundColor,
.main-actionBarBackground-background,
.main-home-homeHeader {{
  background: none !important;
  background-color: transparent !important;
}}

/* rows: selection wash + hover */
.main-trackList-trackListRow {{ border-radius: var(--ttox-r-wash) !important; }}
.main-trackList-trackListRow:hover {{ background-color: var(--ttox-hover) !important; }}
.main-trackList-trackListRow.main-trackList-selected,
.main-trackList-trackListRow.main-trackList-selected:hover {{
  background-color: var(--ttox-select) !important;
}}

/* cards, menus, inputs */
.main-card-card {{ border-radius: var(--ttox-r-control) !important; background-color: var(--spice-card) !important; }}
.main-contextMenu-menu,
.main-popper-container > ul {{
  background-color: var(--spice-main-elevated) !important;
  border: 1px solid var(--ttox-hairline) !important;
  border-radius: var(--ttox-r-menu) !important;
  box-shadow: none !important;
}}
.main-contextMenu-menuItemButton {{ border-radius: var(--ttox-r-wash) !important; }}
.main-contextMenu-menuItemButton:hover {{ background-color: var(--ttox-select) !important; }}
input[type="search"],
.main-topBar-searchBar,
.x-searchInput-searchInputInput {{
  background-color: var(--spice-highlight) !important;
  border: 1px solid var(--spice-misc) !important;
  border-radius: var(--ttox-r-control) !important;
  box-shadow: none !important;
  font-family: var(--ttox-font-mono) !important;
}}
input[type="search"]:focus,
.x-searchInput-searchInputInput:focus {{ border-color: var(--spice-button) !important; }}

/* progress bar: thin, accent fill */
.playback-progressbar .x-progressBar-progressBarBg,
.progress-bar__bg {{ background-color: var(--spice-misc) !important; }}
.x-progressBar-fillColor,
.progress-bar__fg {{ background-color: var(--spice-button) !important; }}

/* scrollbars */
.os-scrollbar-handle {{ background-color: rgba(var(--spice-rgb-button-disabled), 0.50) !important; }}
::selection {{ background-color: var(--ttox-select); }}
"""
    return {"apps/spicetify/TTox/color.ini": "\n".join(ini) + "\n", "apps/spicetify/TTox/user.css": css}
