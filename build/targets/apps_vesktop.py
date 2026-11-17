"""Vesktop / Vencord / BetterDiscord CSS theme, one file per variant.

dist/apps/vesktop/ttox-<variant>.theme.css

Discord is kept opaque (no ladder). Both the pre-2025 variable names and the 2025 "visual refresh" names are set,
because which set a given client build reads cannot be checked here.
"""
from __future__ import annotations
import lib

NAME = "apps_vesktop"; PACK = "apps"
SIDEBAR_DARKEN = 0.12  # "sidebars slightly darker than body"; no token for this


def render(ctx) -> dict:
    p, t = ctx.p, ctx.tokens
    side = lib.darken(p["bg"], SIDEBAR_DARKEN)
    sel = ctx.rgba(p["accent"], t["wash"]["select_alpha"]); hover = ctx.rgba(p["fg"], t["wash"]["hover_alpha"])
    hair = ctx.rgba(p["fg"], t["border"]["hairline_alpha"])
    v = {
        # classic names
        "background-primary": p["bg"], "background-secondary": side, "background-secondary-alt": side,
        "background-tertiary": side, "background-accent": p["line"], "background-floating": p["raised"],
        "background-nested-floating": p["raised"], "background-mobile-primary": p["bg"],
        "background-mobile-secondary": side, "background-modifier-hover": hover,
        "background-modifier-active": sel, "background-modifier-selected": sel,
        "background-modifier-accent": ctx.rgba(p["line"], 0.60), "background-mentioned": ctx.rgba(p["warn"], 0.10),
        "background-mentioned-hover": ctx.rgba(p["warn"], 0.14), "background-message-hover": hover,
        "channeltextarea-background": p["surface"], "modal-background": p["surface"],
        "modal-footer-background": p["bg"], "input-background": p["surface"],
        "text-normal": p["fg"], "text-muted": p["muted"], "text-link": p["accent_text"],
        "text-positive": p["ok"], "text-warning": p["warn"], "text-danger": p["err"],
        "header-primary": p["fg_hi"], "header-secondary": p["muted"],
        "interactive-normal": p["fg"], "interactive-hover": p["fg_hi"], "interactive-active": p["fg_hi"],
        "interactive-muted": p["line"], "channels-default": p["muted"], "channel-icon": p["muted"],
        "brand-experiment": p["accent"], "brand-500": p["accent"], "brand-560": p["accent2"],
        "brand-600": p["accent2"], "brand-260": p["accent_text"], "brand-360": p["accent_text"],
        "mention-foreground": p["accent_text"], "mention-background": sel,
        "status-positive": p["ok"], "status-warning": p["warn"], "status-danger": p["err"],
        "info-positive-foreground": p["ok"], "info-warning-foreground": p["warn"],
        "info-danger-foreground": p["err"],
        "scrollbar-thin-thumb": ctx.rgba(p["muted"], 0.50), "scrollbar-thin-track": "transparent",
        "scrollbar-auto-thumb": ctx.rgba(p["muted"], 0.50), "scrollbar-auto-track": "transparent",
        "scrollbar-auto-scrollbar-color-thumb": ctx.rgba(p["muted"], 0.50),
        "scrollbar-auto-scrollbar-color-track": "transparent",
        "elevation-stroke": f"0 0 0 1px {hair}", "focus-primary": p["accent"],
        "font-primary": f"\"{t['font']['ui']}\", \"{t['font']['ui_fallback']}\", sans-serif",
        "font-display": f"\"{t['font']['ui']}\", \"{t['font']['ui_fallback']}\", sans-serif",
        "font-code": f"\"{t['font']['mono']}\", \"{t['font']['mono_fallback']}\", monospace",
        # 2025 refresh names
        "background-base-low": p["bg"], "background-base-lower": side, "background-base-lowest": side,
        "background-surface-high": p["surface"], "background-surface-higher": p["raised"],
        "background-surface-highest": p["raised"], "bg-overlay-floating": p["raised"],
        "border-subtle": ctx.rgba(p["line"], t["border"]["sep_alpha"]), "border-normal": p["line"],
        "border-strong": p["line"], "border-faint": hair,
        "text-default": p["fg"], "text-strong": p["fg_hi"], "text-subtle": p["muted"], "text-brand": p["accent_text"],
        "text-primary": p["fg"], "text-secondary": p["muted"], "icon-default": p["fg"], "icon-muted": p["muted"],
        "chat-background-default": p["surface"], "chat-border": p["line"],
        "control-brand-foreground": p["accent"], "bg-brand": p["accent"],
        "button-filled-brand-background": p["accent"], "button-filled-brand-background-hover": p["accent"],
        "button-filled-brand-background-active": p["accent2"], "button-filled-brand-text": p["fg_hi"],
        "button-secondary-background": p["raised"], "button-secondary-background-hover": p["line"],
        "button-secondary-text": p["fg"],
        "message-reacted-background": sel, "message-reacted-text": p["fg_hi"],
    }
    r = t["radius"]
    body = "\n".join(f"  --{k}: {val} !important;" for k, val in sorted(v.items()))
    css = f"""/**
 * @name {ctx.title}
 * @author TToxThemes
 * @version 0.1.0
 * @description {ctx.title} palette for Vesktop / Vencord / BetterDiscord. Generated, do not edit.
 */

:root,
.theme-dark,
.theme-darker,
.theme-midnight,
.visual-refresh,
.visual-refresh.theme-dark {{
{body}
}}

::selection {{ background-color: {sel}; color: {p['fg_hi']}; }}

/* inputs: surface + 1 px line, accent ring on focus */
[class*="channelTextArea"] [class*="scrollableContainer"] {{
  background-color: {p['surface']} !important;
  border: 1px solid {p['line']} !important;
  border-radius: {r['control']}px !important;
}}
[class*="channelTextArea"]:focus-within [class*="scrollableContainer"] {{ border-color: {p['accent']} !important; }}

/* popups: raised + hairline */
[class*="menu_"],
[class*="popout"],
[class*="autocomplete_"] {{
  background-color: {p['raised']} !important;
  border: 1px solid {hair} !important;
  border-radius: {r['menu']}px !important;
  box-shadow: none !important;
}}
[class*="menu_"] [class*="item_"] {{ border-radius: {r['wash']}px !important; }}
[class*="menu_"] [class*="focused_"] {{ background-color: {sel} !important; color: {p['fg_hi']} !important; }}

/* code */
code,
pre,
[class*="codeBlockText"] {{
  font-family: "{t['font']['mono']}", "{t['font']['mono_fallback']}", monospace !important;
  background-color: {side} !important;
  border-color: {p['line']} !important;
  border-radius: {r['wash']}px !important;
}}

/* sidebars slightly darker, 1 px separator */
[class*="sidebar_"] {{ background-color: {side} !important; border-right: 1px solid {ctx.rgba(p['line'], 0.40)} !important; }}
"""
    return {f"apps/vesktop/{ctx.slug}.theme.css": css}
