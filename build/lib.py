"""Shared helpers for generator targets. Standard library only."""
from __future__ import annotations
import colorsys
from dataclasses import dataclass, field
from typing import Callable

def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def rgb_to_hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)

def mix(a: str, b: str, t: float) -> str:
    """Blend a toward b by t (0..1)."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])

def darken(h: str, t: float) -> str: return mix(h, "#000000", t)
def lighten(h: str, t: float) -> str: return mix(h, "#ffffff", t)

def rgba(h: str, alpha: float) -> str:
    """CSS rgba() string."""
    r, g, b = hex_to_rgb(h)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"

def rgb_csv(h: str) -> str:
    """'r,g,b' as used by KDE colour schemes."""
    return ",".join(str(c) for c in hex_to_rgb(h))

def hex_alpha(h: str, alpha: float, argb: bool = False) -> str:
    """#rrggbbaa (or #aarrggbb when argb=True)."""
    a = "%02x" % max(0, min(255, int(round(alpha * 255))))
    return "#" + a + h.lstrip("#") if argb else h + a

def over(fg: str, bg: str, alpha: float) -> str:
    """Colour of fg at alpha composited over bg."""
    return mix(bg, fg, alpha)

def luminance(h: str) -> float:
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def min_opacity_for_contrast(text: str, surface: str, backdrop: str, target: float, start: float) -> float:
    """Smallest opacity >= start at which text on (surface@opacity over backdrop) meets target contrast."""
    o = start
    while o < 1.0 and contrast(text, over(surface, backdrop, o)) < target:
        o = round(o + 0.02, 2)
    return min(o, 1.0)

def shift_hue(h: str, toward: str, max_deg: float = 12, max_sat: float = 0.10) -> str:
    """Nudge colour h toward another colour's hue/saturation within limits; lightness is kept."""
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    tr, tg, tb = (c / 255 for c in hex_to_rgb(toward))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    th, _, ts = colorsys.rgb_to_hls(tr, tg, tb)
    d = ((th - hh + 0.5) % 1.0) - 0.5
    lim = max_deg / 360
    hh = (hh + max(-lim, min(lim, d))) % 1.0
    s = max(0.0, min(1.0, s + max(-max_sat, min(max_sat, ts - s))))
    return rgb_to_hex([c * 255 for c in colorsys.hls_to_rgb(hh, l, s)])

def palette_colors(p: dict) -> set[str]:
    """All literal hex colours of a palette (lower-case), for lint."""
    out = {v.lower() for v in p.values() if isinstance(v, str) and v.startswith("#")}
    out |= {c.lower() for c in p["term"]}
    return out

@dataclass
class Ctx:
    """Passed to every target's render(). One Ctx per palette."""
    name: str                      # palette key, e.g. "sterling"
    p: dict                        # palette dict (see palettes.py)
    tokens: dict                   # tokens.TOKENS
    modes: dict                    # tokens.MODES  {mode_name: {...}}
    all_palettes: dict             # every palette, for targets that emit one multi-variant file
    root: str                      # repo root (absolute), to read static files from src/
    mix: Callable = field(default=mix, repr=False)
    rgba: Callable = field(default=rgba, repr=False)

    @property
    def title(self) -> str: return self.p["title"]
    @property
    def slug(self) -> str: return f"ttox-{self.name}"
    def read_src(self, rel: str, binary: bool = False):
        import os
        with open(os.path.join(self.root, "src", rel), "rb" if binary else "r") as f:
            return f.read()
