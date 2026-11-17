"""TToxThemes design tokens: every size, opacity, font and duration. No target may hardcode these."""

MODES = {  # opacity is 0..1 (how opaque the surface colour is); blur in px; poll in seconds
    "full":     {"term": 0.50, "body": 0.62, "bar": 0.70, "popup": 0.72, "lock": 0.55,
                 "blur": 14, "blur_term": 20, "noise": 0.05, "shadows": True, "shadow_px": 24, "shadow_alpha": 0.30,
                 "animations": "full", "anim_scale": 0.8, "poll": 1, "graphs": True, "backend": "glx"},
    "balanced": {"term": 0.62, "body": 0.72, "bar": 0.76, "popup": 0.78, "lock": 0.55,
                 "blur": 8, "blur_term": 10, "noise": 0.03, "shadows": True, "shadow_px": 12, "shadow_alpha": 0.25,
                 "animations": "normal", "anim_scale": 0.6, "poll": 2, "graphs": True, "backend": "glx"},
    "lite":     {"term": 0.88, "body": 0.92, "bar": 0.92, "popup": 0.94, "lock": 0.90,
                 "blur": 0, "blur_term": 0, "noise": 0.0, "shadows": False, "shadow_px": 0, "shadow_alpha": 0.0,
                 "animations": "minimal", "anim_scale": 0.0, "poll": 5, "graphs": False, "backend": "xrender"},
}

TOKENS = {
    "radius": {"window": 12, "pill": 16, "control": 8, "wash": 6, "popup": 12, "menu": 8},
    "border": {"active_px": 2, "active_alpha": 0.60, "inactive_px": 1, "hairline_alpha": 0.12, "sep_alpha": 0.30},
    "wash": {"select_alpha": 0.28, "hover_alpha": 0.06},
    "bar": {"height": 32, "top": 6, "width_pct": 85, "gap": 10, "font_pt": 10},
    "dock": {"width": 54, "icon": 28, "gap": 14, "edge": 8},
    "titlebar": {"height": 32},
    "clock": {"font_pt": 56, "x": 28, "y": 70, "alpha": 0.85},
    "term": {"padding": 12, "font_pt": 11},
    "launcher": {"width": 560, "font_pt": 12},
    "notify": {"width": 360, "timeout_ms": 5000},
    "hud": {"width": 1200, "slide_ms": 160},
    "drawer": {"height_pct": 45},
    "grid": 8,
    "font": {"mono": "JetBrainsMono Nerd Font", "mono_fallback": "DejaVu Sans Mono",
             "ui": "Inter", "ui_fallback": "Noto Sans", "ui_pt": 10.5, "mono_pt": 11},
    "motion_ms": {"open": 180, "close": 140, "minimise": 220, "popup": 120, "workspace": 200, "hover": 100},
    "icons": "Tela-circle", "cursor_size": 24,
    "contrast_min": 4.5,
    "hotkeys": {"hud": "Super+H", "drawer": "Super+grave", "launcher": "Super+space",
                "edit": "Super+E", "cheatsheet": "Super+slash"},
}
