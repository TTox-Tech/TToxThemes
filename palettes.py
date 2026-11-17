"""TToxThemes palettes: the only file edited for colour. Run `python3 build/generate.py` after changes.

Discipline: one grey ramp, one text pair, ONE accent. ok/warn/err are muted and used only for status.
Keys every palette must define: title, bg, surface, raised, line, muted, fg, fg_hi, accent, accent2,
accent_text, folder, ok, warn, err, cursor, term (16 hex).
"""

PALETTES = {
    "sterling": {  # silver primary, steel-blue details
        "title": "TTox Sterling",
        "bg": "#1b1d21", "surface": "#24272c", "raised": "#2d3137", "line": "#3a3f46",
        "muted": "#7f858e", "fg": "#c9ccd1", "fg_hi": "#eef0f3",
        "accent": "#5b8fc7", "accent2": "#3f6a99", "accent_text": "#7eaede", "folder": "#5b8fc7",
        "ok": "#7fa678", "warn": "#c7a35b", "err": "#c06a6a",
        "cursor": "Bibata-Modern-Ice",
        "term": ["#1b1d21", "#c06a6a", "#7fa678", "#c7a35b", "#5b8fc7", "#8a93a6", "#6fa3b7", "#c9ccd1",
                 "#4a5059", "#d08484", "#98bd90", "#dcbd78", "#7eaede", "#a7afc2", "#8dbfd2", "#eef0f3"],
    },
    "vino": {  # black primary, wine-red details
        "title": "TTox Vino",
        "bg": "#0f0f10", "surface": "#171718", "raised": "#202022", "line": "#2c2c2f",
        "muted": "#75716f", "fg": "#d6d2cf", "fg_hi": "#f2efec",
        "accent": "#8e2a3a", "accent2": "#5e1c27", "accent_text": "#b04a5c", "folder": "#a89aa6",
        "ok": "#7e9a6c", "warn": "#bf9a5a", "err": "#b8464f",
        "cursor": "Bibata-Modern-Classic",
        "term": ["#0f0f10", "#b8464f", "#7e9a6c", "#bf9a5a", "#8d7a8a", "#b04a5c", "#7f9a98", "#d6d2cf",
                 "#3a3a3d", "#d06670", "#9bb58a", "#d6b276", "#a89aa6", "#c8697a", "#9ab7b5", "#f2efec"],
    },
    "graphite": {  # dark grey, copper accent
        "title": "TTox Graphite",
        "bg": "#1e1f21", "surface": "#27292c", "raised": "#303236", "line": "#3d4044",
        "muted": "#86888c", "fg": "#d0d0cf", "fg_hi": "#f0efed",
        "accent": "#b9875a", "accent2": "#8a6341", "accent_text": "#d0a076", "folder": "#b9875a",
        "ok": "#8aa37a", "warn": "#c9a85e", "err": "#bd6b62",
        "cursor": "Bibata-Modern-Classic",
        "term": ["#1e1f21", "#bd6b62", "#8aa37a", "#c9a85e", "#8b98a8", "#b9875a", "#89a6a3", "#d0d0cf",
                 "#4a4c50", "#d08a80", "#a6bd96", "#dcc07a", "#a5b2c2", "#d0a076", "#a3bebb", "#f0efed"],
    },
}
