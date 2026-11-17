"""Shared helpers for the KDE targets (no render(): generate.py skips this module).

Everything here is a pure function of the palette / tokens. Stream 1 (KDE) owns this file.
"""
from __future__ import annotations
import os
import sys
from typing import Iterable, Optional, Sequence

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib  # noqa: E402

BLACK = "#000000"   # only as a mix endpoint for lib.darken-style derivations and shadows
MODE_ORDER = ("full", "balanced", "lite")


def modes(ctx) -> list:
    """(mode name, mode dict) in a fixed order."""
    known = [m for m in MODE_ORDER if m in ctx.modes]
    return [(m, ctx.modes[m]) for m in known + sorted(set(ctx.modes) - set(known))]


def cap(name: str) -> str:
    return name[:1].upper() + name[1:]


# ---------------------------------------------------------------- names (one place, used by targets + tests)
def scheme_name(variant: str) -> str: return f"ttox-{variant}"
def kv_name(variant: str, mode: str) -> str: return f"ttox-{variant}-{mode}"
def konsole_name(variant: str, mode: str) -> str: return f"ttox-{variant}-{mode}"
def aurorae_name(variant: str, mode: str) -> str: return f"ttox-glass-{variant}-{mode}"
def plasma_name(variant: str, mode: str) -> str: return f"ttox-{variant}-{mode}"
def lnf_name(variant: str, mode: str) -> str: return f"org.ttox.{variant}.{mode}"
def sddm_name(variant: str) -> str: return f"ttox-{variant}"
def icon_theme(ctx) -> str: return f"{ctx.tokens['icons']}-ttox-{ctx.name}"


# ---------------------------------------------------------------- derived colours
def derived(p: dict, t: dict) -> dict:
    """Opaque derived shades used across the KDE files. Every value is a lib.mix of palette colours."""
    sel = t["wash"]["select_alpha"]
    hov = t["wash"]["hover_alpha"]
    return {
        "deep": lib.darken(p["bg"], 0.40),                       # below bg: shadows-in-widgets, grooves
        "view": lib.mix(p["bg"], p["surface"], 0.5),             # views/sidebars: slightly darker than body
        "wash": lib.over(p["accent"], p["surface"], sel),        # selection wash composited on body
        "wash_view": lib.over(p["accent"], lib.mix(p["bg"], p["surface"], 0.5), sel),
        "wash_inactive": lib.over(p["accent2"], p["surface"], sel),
        "wash_press": lib.over(p["accent"], p["surface"], min(1.0, sel + 2 * hov)),
        "hover": lib.over(p["fg"], p["raised"], hov),            # hover wash on a raised control
        "hover_body": lib.over(p["fg"], p["surface"], hov),
        "hair_popup": lib.over(p["fg"], p["raised"], t["border"]["hairline_alpha"]),
        "sep": lib.over(p["line"], p["surface"], t["border"]["sep_alpha"]),
        "visited": lib.mix(p["accent_text"], p["muted"], 0.5),
        "disabled": lib.mix(p["muted"], p["surface"], 0.35),
    }


# ---------------------------------------------------------------- INI
def ini(sections: Sequence, header: Optional[str] = None, space: bool = False) -> str:
    """sections: [(name, [(key, value), ...]), ...] -> KConfig-style INI text. Order is the caller's."""
    out = []
    if header:
        out += ["# " + line for line in header.split("\n")] + [""]
    eq = " = " if space else "="
    for name, items in sections:
        out.append(f"[{name}]")
        for k, v in items:
            if isinstance(v, bool):
                v = "true" if v else "false"
            out.append(f"{k}{eq}{v}")
        out.append("")
    return "\n".join(out)


def qfont(family: str, pt: float, weight: int = 50, mono: bool = False) -> str:
    """QFont::toString() in the 10-field Qt5 form (Qt6 QFont::fromString also accepts it)."""
    size = ("%g" % pt)
    return f"{family},{size},-1,{2 if mono else 5},{weight},0,0,0,{1 if mono else 0},0"


# ---------------------------------------------------------------- SVG nine-slice frames
def _n(v: float) -> str:
    return ("%.3f" % v).rstrip("0").rstrip(".")


class Frame:
    """Builds the nine elements of a Plasma FrameSvg (<prefix>-topleft ... <prefix>-center).

    Pieces are laid out touching each other so the document is also a readable picture of the frame.
    No transforms are used (QSvgRenderer::boundsOnElement ignores parent transforms on older Qt), and
    every piece carries an invisible rect that pins its bounding box to the cell.
    radius: (top, bottom) corner radii; bw: border width; pad: extra transparent/shadow margin outside.
    """

    def __init__(self, prefix: str, x: float, y: float, radius: Sequence, bw: float, fill: Optional[str],
                 fill_a: float, stroke: Optional[str], stroke_a: float, pad: float = 0, stretch: float = 8,
                 shadow: Optional[str] = None, shadow_a: float = 0.0, gid: str = "g"):
        self.prefix, self.x, self.y, self.bw, self.pad, self.s = prefix, x, y, bw, pad, stretch
        self.rt, self.rb = max(radius[0], bw), max(radius[1], bw)
        self.fill, self.fill_a, self.stroke, self.stroke_a = fill, fill_a, stroke, stroke_a
        self.shadow, self.shadow_a, self.gid = shadow, shadow_a, gid
        self.cell = pad + max(self.rt, self.rb)          # corner cells are square and equal
        self.size = 2 * self.cell + stretch

    def _id(self, part: str) -> str:
        return f"{self.prefix}-{part}" if self.prefix else part

    def _pin(self, x: float, y: float, w: float, h: float) -> str:
        return f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" fill="{BLACK}" fill-opacity="0"/>'

    def _paint(self, color: Optional[str], alpha: float) -> Optional[str]:
        if not color or alpha <= 0:
            return None
        return f'fill="{color}" fill-opacity="{_n(alpha)}"'

    def _corner(self, part: str, dx: int, dy: int) -> str:
        c, pad, bw = self.cell, self.pad, self.bw
        r = self.rt if dy > 0 else self.rb
        # outer corner of the visible frame, and the cell origin
        ox = self.x + (pad if dx > 0 else self.size - pad)
        oy = self.y + (pad if dy > 0 else self.size - pad)
        cx0 = self.x if dx > 0 else self.x + self.size - c
        cy0 = self.y if dy > 0 else self.y + self.size - c
        ix, iy = ox + dx * (c - pad), oy + dy * (c - pad)      # inner corner of the cell
        sw = 1 if dx * dy > 0 else 0
        ax, ay, bx, by = ox, oy + dy * r, ox + dx * r, oy
        body = [self._pin(cx0, cy0, c, c)]
        f = self._paint(self.fill, self.fill_a)
        if f:   # rounded quarter + the rest of the cell toward the inside
            body.append(f'<path {f} d="M{_n(ax)},{_n(ay)} A{_n(r)},{_n(r)} 0 0 {sw} {_n(bx)},{_n(by)} '
                        f'L{_n(ix)},{_n(by)} L{_n(ix)},{_n(iy)} L{_n(ax)},{_n(iy)} Z"/>')
        s = self._paint(self.stroke, self.stroke_a)
        if s and bw > 0:
            ri = r - bw
            d = f'M{_n(ax)},{_n(ay)} A{_n(r)},{_n(r)} 0 0 {sw} {_n(bx)},{_n(by)} '
            if ri > 0:
                d += (f'L{_n(bx)},{_n(oy + dy * bw)} A{_n(ri)},{_n(ri)} 0 0 {1 - sw} {_n(ox + dx * bw)},{_n(ay)} Z')
            else:
                d += f'L{_n(bx)},{_n(ay)} Z'
            body.append(f'<path {s} d="{d}"/>')
            # straight border runs between the arc and the cell's inner edges
            if abs(ix - bx) > 0:
                body.append(f'<rect {s} x="{_n(min(bx, ix))}" y="{_n(min(oy, oy + dy * bw))}" '
                            f'width="{_n(abs(ix - bx))}" height="{_n(bw)}"/>')
            if abs(iy - ay) > 0:
                body.append(f'<rect {s} x="{_n(min(ox, ox + dx * bw))}" y="{_n(min(ay, iy))}" '
                            f'width="{_n(bw)}" height="{_n(abs(iy - ay))}"/>')
        if self.shadow and self.shadow_a > 0 and pad > 0:
            px, py = ox - dx * pad, oy - dy * pad
            gid = f"{self.gid}-{part}"
            body.insert(0, f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{_n(bx)}" cy="{_n(ay)}" '
                           f'r="{_n(r + pad)}"><stop offset="{_n(r / (r + pad))}" stop-color="{self.shadow}" '
                           f'stop-opacity="{_n(self.shadow_a)}"/><stop offset="1" stop-color="{self.shadow}" '
                           f'stop-opacity="0"/></radialGradient>')
            body.append(f'<path fill="url(#{gid})" d="M{_n(px)},{_n(ay)} L{_n(px)},{_n(py)} L{_n(bx)},{_n(py)} '
                        f'L{_n(bx)},{_n(by)} A{_n(r)},{_n(r)} 0 0 {1 - sw} {_n(ax)},{_n(ay)} Z"/>')
            # shadow beside the straight parts of the cell (when the cell is larger than this corner's radius)
            if abs(ix - bx) > 0:
                body.append(self._edge_shadow(f"{gid}-h", min(bx, ix), min(py, oy), abs(ix - bx), pad, 0, -dy))
            if abs(iy - ay) > 0:
                body.append(self._edge_shadow(f"{gid}-v", min(px, ox), min(ay, iy), pad, abs(iy - ay), -dx, 0))
        return f'<g id="{self._id(part)}">' + "".join(body) + "</g>"

    def _edge_shadow(self, gid: str, x: float, y: float, w: float, h: float, ux: int, uy: int) -> str:
        """Linear shadow fading in direction (ux, uy) (pointing away from the frame) over rect x,y,w,h."""
        x1 = x + w if ux < 0 else x
        y1 = y + h if uy < 0 else y
        x2 = x1 + ux * w if ux else x1
        y2 = y1 + uy * h if uy else y1
        return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{_n(x1)}" y1="{_n(y1)}" '
                f'x2="{_n(x2)}" y2="{_n(y2)}"><stop offset="0" stop-color="{self.shadow}" '
                f'stop-opacity="{_n(self.shadow_a)}"/><stop offset="1" stop-color="{self.shadow}" '
                f'stop-opacity="0"/></linearGradient>'
                f'<rect fill="url(#{gid})" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"/>')

    def _side(self, part: str) -> str:
        """Edge piece: as thick as the corner cell (FrameSvg margins come from the corners)."""
        c, s, pad, bw = self.cell, self.s, self.pad, self.bw
        X, Y, S = self.x, self.y, self.size
        if part == "top":
            cell = (X + c, Y, s, c); fill = (X + c, Y + pad, s, c - pad); line = (X + c, Y + pad, s, bw)
            sh = (X + c, Y, s, pad, 0, -1)
        elif part == "bottom":
            cell = (X + c, Y + S - c, s, c); fill = (X + c, Y + S - c, s, c - pad)
            line = (X + c, Y + S - pad - bw, s, bw); sh = (X + c, Y + S - pad, s, pad, 0, 1)
        elif part == "left":
            cell = (X, Y + c, c, s); fill = (X + pad, Y + c, c - pad, s); line = (X + pad, Y + c, bw, s)
            sh = (X, Y + c, pad, s, -1, 0)
        else:
            cell = (X + S - c, Y + c, c, s); fill = (X + S - c, Y + c, c - pad, s)
            line = (X + S - pad - bw, Y + c, bw, s); sh = (X + S - pad, Y + c, pad, s, 1, 0)
        body = [self._pin(*cell)]
        if self.shadow and self.shadow_a > 0 and pad > 0:
            body.append(self._edge_shadow(f"{self.gid}-{part}", *sh))
        f = self._paint(self.fill, self.fill_a)
        if f:
            body.append(f'<rect {f} x="{_n(fill[0])}" y="{_n(fill[1])}" width="{_n(fill[2])}" height="{_n(fill[3])}"/>')
        st = self._paint(self.stroke, self.stroke_a)
        if st and bw > 0:
            body.append(f'<rect {st} x="{_n(line[0])}" y="{_n(line[1])}" width="{_n(line[2])}" height="{_n(line[3])}"/>')
        return f'<g id="{self._id(part)}">' + "".join(body) + "</g>"

    def _center(self) -> str:
        c, s = self.cell, self.s
        x, y = self.x + c, self.y + c
        body = [self._pin(x, y, s, s)]
        f = self._paint(self.fill, self.fill_a)
        if f:
            body.append(f'<rect {f} x="{_n(x)}" y="{_n(y)}" width="{_n(s)}" height="{_n(s)}"/>')
        return f'<g id="{self._id("center")}">' + "".join(body) + "</g>"

    def elements(self) -> list:
        out = [self._corner("topleft", 1, 1), self._side("top"), self._corner("topright", -1, 1),
               self._side("left"), self._center(), self._side("right"),
               self._corner("bottomleft", 1, -1), self._side("bottom"), self._corner("bottomright", -1, -1)]
        return out


FRAME_PARTS = ("topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright")


def hint(elem_id: str, x: float, y: float, w: float, h: float) -> str:
    """Invisible sizing element (Plasma 'hint-*' conventions)."""
    return (f'<rect id="{elem_id}" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" '
            f'fill="{BLACK}" fill-opacity="0"/>')


def svg_doc(width: float, height: float, body: Iterable, comment: str = "") -> str:
    head = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{_n(width)}" height="{_n(height)}" ' \
           f'viewBox="0 0 {_n(width)} {_n(height)}">'
    c = f"<!-- {comment} -->\n" if comment else ""
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + c + head + "\n" + "\n".join(body) + "\n</svg>\n"
