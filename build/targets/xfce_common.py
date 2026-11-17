"""Shared helpers for the XFCE stream targets (not a target itself: no render()).

Loaded by the xfce_*.py targets through `load_common()` because build/targets is not on sys.path.
Everything here is derived from ctx.p / ctx.tokens / ctx.modes. The few constants below are values the
SPEC states in prose (section 3) but tokens.py does not carry yet; they are listed in notes/xfce.md under
"Requests to core" so they can move into tokens.py.
"""
from __future__ import annotations
import re
import lib

# --- SPEC section 3 values without a token (see notes/xfce.md, Requests to core) -------------------
SIDEBAR_DARKEN = 0.22        # "sidebars slightly darker than body" (mock: bg @ 22 % over the body)
SIDEBAR_SEP_ALPHA = 0.40     # "1 px line @ 40 % separator"
SCROLLBAR_PX = 6             # "scrollbars 6 px transient"
SCROLLBAR_ALPHA = 0.50       # "muted @ 50 %"
DOCK_RUN_ALPHA = 0.70        # running indicator "fg @ 70 %"
DOCK_RUN_W, DOCK_RUN_H = 3, 12
LOCK_CLOCK_PT = 64           # "mono light clock 64 pt"
WS_DOT = 17                  # mock: workspace circle 17 px, active pill twice as wide
CLOCK_FORMAT = "%a %d %b %H:%M"   # "Tue 17 Nov 02:38"
BAR_PAD = 14                 # mock: bar inner horizontal padding
DISABLED_MIX = 0.45          # insensitive text = muted blended this far into the surface

MODE_OFF = "off"             # SPEC: "Mode off = compositing off" (no entry in tokens.MODES)

# Fixed xfce4-panel plugin ids, shared by the panel script and the panel CSS (#<type>-<id> widget names).
PLUGINS = {
    "launcher": 1, "overview": 2, "pager": 3, "clock": 4, "sep_l": 5, "mpris": 6, "sep_r": 7,
    "cpu": 8, "ram": 9, "net": 10, "vpn": 11, "docker": 12, "updates": 13,
    "systray": 14, "pulseaudio": 15, "power": 16, "actions": 17,
    "dock_browser": 21, "dock_files": 22, "dock_terminal": 23, "dock_editor": 24,
    "dock_tasks": 25, "dock_sep": 26, "dock_launcher": 27,
}
METRIC_MODULES = ["cpu", "ram", "net", "vpn", "docker", "updates"]


def theme_name(ctx) -> str:
    """GTK / xfwm4 theme directory name, e.g. TTox-Sterling."""
    return "TTox-" + ctx.name.capitalize()


def modes(ctx) -> list:
    return sorted(ctx.modes)


def derived(ctx) -> dict:
    """Opaque and rgba() colours every XFCE target shares, keyed by the @define-color name."""
    p, t = ctx.p, ctx.tokens
    b, w = t["border"], t["wash"]
    d = {k: p[k] for k in ("bg", "surface", "raised", "line", "muted", "fg", "fg_hi", "accent", "accent2",
                           "accent_text", "ok", "warn", "err")}
    d["sidebar"] = lib.over(p["bg"], p["surface"], SIDEBAR_DARKEN)
    d["disabled_fg"] = lib.mix(p["muted"], p["surface"], DISABLED_MIX)
    d["select_solid"] = lib.over(p["accent"], p["surface"], w["select_alpha"])
    d["hover_solid"] = lib.over(p["fg"], p["surface"], w["hover_alpha"])
    d["outline_solid"] = lib.over(p["fg"], p["surface"], b["active_alpha"])
    d["sep_solid"] = lib.over(p["line"], p["surface"], b["sep_alpha"])
    d["wash_select"] = lib.rgba(p["accent"], w["select_alpha"])
    d["wash_hover"] = lib.rgba(p["fg"], w["hover_alpha"])
    d["wash_press"] = lib.rgba(p["fg"], w["hover_alpha"] * 2)
    d["hairline"] = lib.rgba(p["fg"], b["hairline_alpha"])
    d["outline_active"] = lib.rgba(p["fg"], b["active_alpha"])
    d["sep"] = lib.rgba(p["line"], b["sep_alpha"])
    d["sidebar_sep"] = lib.rgba(p["line"], SIDEBAR_SEP_ALPHA)
    d["scroll"] = lib.rgba(p["muted"], SCROLLBAR_ALPHA)
    d["dock_run"] = lib.rgba(p["fg"], DOCK_RUN_ALPHA)
    d["clear"] = lib.rgba(p["bg"], 0.0)
    return d


def mode_colors(ctx, mode: str) -> dict:
    """Per-mode glass colours. mode 'off' = every surface opaque, no shadow."""
    p = ctx.p
    if mode == MODE_OFF:
        m = {"term": 1.0, "body": 1.0, "bar": 1.0, "popup": 1.0, "lock": 1.0, "shadow_alpha": 0.0}
    else:
        m = ctx.modes[mode]
    black = lib.darken(p["bg"], 1.0)
    return {
        "glass_term": lib.rgba(p["bg"], m["term"]), "glass_body": lib.rgba(p["surface"], m["body"]),
        "glass_bar": lib.rgba(p["bg"], m["bar"]), "glass_popup": lib.rgba(p["raised"], m["popup"]),
        "glass_lock": lib.rgba(p["bg"], m["lock"]), "shadow": lib.rgba(black, m["shadow_alpha"]),
    }


def numbers(ctx) -> dict:
    """Token numbers exposed to the CSS templates as %%name%% placeholders."""
    t = ctx.tokens
    r, f = t["radius"], t["font"]
    n = {"r_" + k: r[k] for k in sorted(r)}
    n.update({
        "font_ui": f["ui"], "font_ui_fallback": f["ui_fallback"], "font_mono": f["mono"],
        "font_mono_fallback": f["mono_fallback"], "ui_pt": f["ui_pt"], "mono_pt": f["mono_pt"],
        "bar_pt": t["bar"]["font_pt"], "bar_h": t["bar"]["height"], "bar_pad": BAR_PAD,
        "term_pad": t["term"]["padding"], "titlebar_h": t["titlebar"]["height"],
        "active_px": t["border"]["active_px"], "inactive_px": t["border"]["inactive_px"],
        "scroll_px": SCROLLBAR_PX, "lock_clock_pt": LOCK_CLOCK_PT, "ws_dot": WS_DOT, "ws_dot_r": (WS_DOT + 1) // 2,
        "run_w": DOCK_RUN_W, "hover_ms": t["motion_ms"]["hover"], "popup_ms": t["motion_ms"]["popup"],
        "pager_id": PLUGINS["pager"], "clock_id": PLUGINS["clock"], "dock_launcher_id": PLUGINS["dock_launcher"],
        "launcher_id": PLUGINS["launcher"], "dock_tasks_id": PLUGINS["dock_tasks"],
    })
    return n


_PH = re.compile(r"%%([a-z0-9_]+)%%")


def subst(text: str, mapping: dict) -> str:
    """Replace %%name%% placeholders; unknown names are an error (keeps templates honest)."""
    def rep(m):
        k = m.group(1)
        if k not in mapping:
            raise KeyError(f"template placeholder %%{k}%% has no value")
        return str(mapping[k])
    return _PH.sub(rep, text)


def define_colors(d: dict) -> str:
    return "".join(f"@define-color {k} {d[k]};\n" for k in sorted(d))


def sh_quote(s: str) -> str:
    return "'" + str(s).replace("'", "'\\''") + "'"


def load_xpm():
    import xfce_xpm  # build/ is on sys.path (generate.py)
    return xfce_xpm
