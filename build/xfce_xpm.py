"""Tiny XPM3 writer/reader and an anti-aliased line rasteriser. Standard library only.

Used by build/targets/xfce_xfwm4.py to draw the xfwm4 frame pieces, and by tests/xfce to read them back.
A pixel is either None (transparent, written as the XPM colour "None") or an "#rrggbb" string.
"""
from __future__ import annotations
import math
import re
from typing import List, Optional, Tuple

Pixel = Optional[str]
# XPM pixel characters: printable ASCII without the two that need escaping inside a C string.
_CHARS = "".join(chr(c) for c in range(33, 127) if chr(c) not in '"\\')


def _mix(a: str, b: str, t: float) -> str:
    ra = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    rb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(ra[i] + (rb[i] - ra[i]) * t)))) for i in range(3))


class Image:
    def __init__(self, w: int, h: int, fill: Pixel = None) -> None:
        if w < 1 or h < 1:
            raise ValueError("XPM size must be at least 1x1")
        self.w, self.h = w, h
        self.px: List[List[Pixel]] = [[fill] * w for _ in range(h)]

    def set(self, x: int, y: int, c: Pixel) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def get(self, x: int, y: int) -> Pixel:
        return self.px[y][x]

    def rect(self, x0: int, y0: int, x1: int, y1: int, c: Pixel) -> None:
        """Fill [x0,x1) x [y0,y1)."""
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.px[y][x] = c

    def blend(self, x: int, y: int, c: str, cov: float) -> None:
        """Composite colour c at coverage cov over an opaque pixel (transparent pixels stay 1-bit)."""
        if not (0 <= x < self.w and 0 <= y < self.h) or cov <= 0:
            return
        cur = self.px[y][x]
        if cur is None:
            if cov >= 0.5:
                self.px[y][x] = c
            return
        self.px[y][x] = _mix(cur, c, min(1.0, cov))

    def line(self, x0: float, y0: float, x1: float, y1: float, c: str, width: float = 1.2) -> None:
        """Anti-aliased segment in pixel-centre coordinates (coverage from distance to the segment)."""
        half = width / 2.0
        dx, dy = x1 - x0, y1 - y0
        ln2 = dx * dx + dy * dy
        for y in range(int(math.floor(min(y0, y1) - half - 1)), int(math.ceil(max(y0, y1) + half + 1)) + 1):
            for x in range(int(math.floor(min(x0, x1) - half - 1)), int(math.ceil(max(x0, x1) + half + 1)) + 1):
                t = 0.0 if ln2 == 0 else max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / ln2))
                d = math.hypot(x - (x0 + t * dx), y - (y0 + t * dy))
                self.blend(x, y, c, max(0.0, min(1.0, half + 0.5 - d)))

    def circle(self, cx: float, cy: float, r: float, c: str, width: float = 1.2, filled: bool = False) -> None:
        for y in range(int(cy - r - 2), int(cy + r + 3)):
            for x in range(int(cx - r - 2), int(cx + r + 3)):
                d = math.hypot(x - cx, y - cy)
                cov = (r + 0.5 - d) if filled else (width / 2.0 + 0.5 - abs(d - r))
                self.blend(x, y, c, max(0.0, min(1.0, cov)))

    def flip_h(self) -> "Image":
        o = Image(self.w, self.h)
        o.px = [list(reversed(row)) for row in self.px]
        return o

    def colors(self) -> List[Pixel]:
        seen = {c for row in self.px for c in row}
        return ([None] if None in seen else []) + sorted(c for c in seen if c is not None)

    def to_xpm(self, name: str) -> str:
        ident = re.sub(r"[^A-Za-z0-9_]", "_", name)
        cols = self.colors()
        cpp = 1 if len(cols) <= len(_CHARS) else 2
        if len(cols) > len(_CHARS) ** 2:
            raise ValueError("too many colours for this XPM writer")
        key = {}
        for i, c in enumerate(cols):
            key[c] = _CHARS[i] if cpp == 1 else _CHARS[i // len(_CHARS)] + _CHARS[i % len(_CHARS)]
        out = ["/* XPM */", f"static char * {ident}_xpm[] = {{", f'"{self.w} {self.h} {len(cols)} {cpp}",']
        out += [f'"{key[c]} c {"None" if c is None else c}",' for c in cols]
        rows = ['"' + "".join(key[c] for c in row) + '"' for row in self.px]
        out += [r + "," for r in rows[:-1]] + [rows[-1]]
        out.append("};")
        return "\n".join(out) + "\n"


def parse_xpm(text: str) -> Tuple[int, int, List[List[Pixel]]]:
    """Strict reader for the subset to_xpm() writes. Raises ValueError on any malformation."""
    if not text.startswith("/* XPM */\n"):
        raise ValueError("missing /* XPM */ header")
    if not re.search(r"static char \* ?[A-Za-z_][A-Za-z0-9_]*\[\] = \{", text) or not text.rstrip().endswith("};"):
        raise ValueError("missing C array wrapper")
    strings = re.findall(r'"((?:[^"\\]|\\.)*)"', text)
    if not strings:
        raise ValueError("no strings")
    try:
        w, h, n, cpp = (int(v) for v in strings[0].split())
    except ValueError as e:
        raise ValueError("bad values line") from e
    if len(strings) != 1 + n + h:
        raise ValueError(f"expected {1 + n + h} strings, found {len(strings)}")
    table = {}
    for s in strings[1:1 + n]:
        k, rest = s[:cpp], s[cpp:].split()
        if len(rest) != 2 or rest[0] != "c":
            raise ValueError(f"bad colour line {s!r}")
        if rest[1] != "None" and not re.fullmatch(r"#[0-9a-fA-F]{6}", rest[1]):
            raise ValueError(f"bad colour {rest[1]!r}")
        if k in table:
            raise ValueError("duplicate colour key")
        table[k] = None if rest[1] == "None" else rest[1].lower()
    px = []
    for s in strings[1 + n:]:
        if len(s) != w * cpp:
            raise ValueError("pixel row has wrong length")
        try:
            px.append([table[s[i:i + cpp]] for i in range(0, len(s), cpp)])
        except KeyError as e:
            raise ValueError(f"pixel uses undefined key {e}") from e
    return w, h, px
