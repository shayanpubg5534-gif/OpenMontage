"""Epoch Ledger motion builders (Python side of kit/motion.js). Original implementation.

- ktext:          pre-split kinetic text markup (word / char / line masks) for mReveal / mWordsAt
- iso_*:          true-isometric 2.5D construction (one fixed light, shaded faces, lift on Z)
- world_map_svg:  vector world maps from Natural Earth (kit/data/countries-110m.json, see kit/data/LICENSES.md)
- route_path, pin_xy: geographic routes (great-circle) and pins locked to the same projection
- endscreen_html: series end screen in YouTube's end-screen zone, live background, no logo intro
- diagram_*:      node/edge markup with ids for mDiagram / mFlow / mFocus
All output is deterministic SVG/HTML in 1920×1080 authoring space.
"""
from __future__ import annotations

import html
import json
import math
from functools import lru_cache
from pathlib import Path

KIT = Path(__file__).resolve().parent
OUT = "#1b1410"


# ── kinetic text ──────────────────────────────────────────────────────────────────────────────
def ktext(id_: str, text: str, by: str = "word", cls: str = "", style: str = "") -> str:
    """Pre-split text into masked pieces so line breaks are fixed at build time (lines: separate with '|')."""
    if by == "line":
        parts = text.split("|")
    elif by == "char":
        parts = list(text)
    else:
        parts = text.split(" ")
    disp = "block" if by == "line" else "inline-block"
    sep = "" if by in ("line", "char") else " "
    pieces = sep.join(
        f'<span class="kp" style="display:{disp};overflow:hidden;vertical-align:bottom">'
        f'<span class="ki" style="display:inline-block">{html.escape(p) if p != " " else "&nbsp;"}</span></span>' for p in parts)
    return f'<div id="{id_}" class="ktext {cls}" style="opacity:0;{style}">{pieces}</div>'


# ── isometric ─────────────────────────────────────────────────────────────────────────────────
COS30, SIN30 = math.cos(math.radians(30)), 0.5


def iso(x: float, y: float, z: float = 0.0, s: float = 1.0, ox: float = 960, oy: float = 540) -> tuple[float, float]:
    """World (x right-back, y left-back, z up) → screen, true isometric (ground axes at ±30°)."""
    return ox + (x - y) * COS30 * s, oy + (x + y) * SIN30 * s - z * s


def shade(hex_: str, f: float) -> str:
    """Scale a #rrggbb colour's brightness by f (one fixed light: top 1.0, left ~0.82, right ~0.64)."""
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def iso_box(id_: str, x: float, y: float, z: float, w: float, d: float, h: float, color: str, s: float = 1.0,
            ox: float = 960, oy: float = 540, stroke: str = OUT, faces: dict | None = None) -> str:
    """Extruded block with top / left / right faces shaded from one fixed light. Animate lift with
    translateY on the group (#id) — never scale, which breaks the parallel projection."""
    P = lambda a, b, c: "%.1f,%.1f" % iso(a, b, c, s, ox, oy)
    top = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    left = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    right = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    f = faces or {}
    return (f'<g id="{id_}" class="isobox">'
            f'<polygon points="{" ".join(left)}" fill="{f.get("left", shade(color, .82))}" stroke="{stroke}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<polygon points="{" ".join(right)}" fill="{f.get("right", shade(color, .64))}" stroke="{stroke}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<polygon points="{" ".join(top)}" fill="{f.get("top", color)}" stroke="{stroke}" stroke-width="2.5" stroke-linejoin="round"/></g>')


def iso_grid(n: int, step: float, s: float = 1.0, ox: float = 960, oy: float = 540, color: str = "#2a3a52") -> str:
    lines = []
    for i in range(n + 1):
        a, b = iso(i * step, 0, 0, s, ox, oy), iso(i * step, n * step, 0, s, ox, oy)
        c, e = iso(0, i * step, 0, s, ox, oy), iso(n * step, i * step, 0, s, ox, oy)
        lines.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} M{c[0]:.1f} {c[1]:.1f} L{e[0]:.1f} {e[1]:.1f}"/>')
    return f'<g class="isogrid" stroke="{color}" stroke-width="1.5">{"".join(lines)}</g>'


# ── maps (Natural Earth via world-atlas topojson) ─────────────────────────────────────────────
@lru_cache(maxsize=1)
def _topology() -> dict:
    return json.loads((KIT / "data" / "countries-110m.json").read_text())


def _arcs() -> list[list[tuple[float, float]]]:
    t = _topology()
    (kx, ky), (tx, ty) = t["transform"]["scale"], t["transform"]["translate"]
    out = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * kx + tx, y * ky + ty))
        out.append(pts)
    return out


def countries() -> dict[str, list[list[list[tuple[float, float]]]]]:
    """name → list of polygons → list of rings → (lon, lat)."""
    arcs = _arcs()

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    res = {}
    for g in _topology()["objects"]["countries"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]] if g["type"] == "Polygon" else []
        res[g["properties"].get("name", g.get("id"))] = [[ring(r) for r in p] for p in polys]
    return res


def projection(kind: str = "equirect", w: float = 1920, h: float = 1080, center: tuple[float, float] = (0, 0),
               scale: float | None = None, rotate: tuple[float, float] | None = None):
    """Return f(lon, lat) → (x, y) or None (hidden side). kinds: equirect, mercator, ortho."""
    cx, cy = w / 2, h / 2
    lon0, lat0 = center
    if kind == "equirect":
        k = scale or w / 360

        def f(lon, lat):
            return cx + (lon - lon0) * k, cy - (lat - lat0) * k
    elif kind == "mercator":
        k = scale or w / (2 * math.pi)
        y0 = math.log(math.tan(math.pi / 4 + math.radians(lat0) / 2))

        def f(lon, lat):
            lat = max(-85, min(85, lat))
            return cx + math.radians(lon - lon0) * k, cy - (math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) - y0) * k
    elif kind == "ortho":
        r = scale or min(w, h) * .45
        l0, p0 = map(math.radians, rotate or center)

        def f(lon, lat):
            l, p = math.radians(lon), math.radians(lat)
            cosc = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l - l0)
            if cosc < 0:
                return None
            return (cx + r * math.cos(p) * math.sin(l - l0),
                    cy - r * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0)))
    else:
        raise ValueError(kind)
    return f


def _path(rings, proj) -> str:
    out = []
    for ring_ in rings:
        seg, prev = [], None
        for lon, lat in ring_:
            q = proj(lon, lat)
            if q is None or (prev is not None and abs(q[0] - prev[0]) > 600):   # hidden side / dateline wrap
                if len(seg) > 2:
                    out.append("M" + " L".join("%.1f %.1f" % p for p in seg) + "Z")
                seg = []
            if q is not None:
                seg.append(q)
            prev = q
        if len(seg) > 2:
            out.append("M" + " L".join("%.1f %.1f" % p for p in seg) + "Z")
    return "".join(out)


def _slug(name: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in name.lower()).strip("-")


def world_map_svg(id_: str, proj, highlight: dict[str, str] | None = None, land: str = "#c9a56a", sea: str | None = None,
                  stroke: str = "#f3e3c3", only: list[str] | None = None) -> str:
    """Country paths with ids `{id_}-c-{slug}` (focus + context: highlight = {name: colour})."""
    hl = highlight or {}
    paths = []
    for name, polys in countries().items():
        if only and name not in only:
            continue
        d = "".join(_path(p, proj) for p in polys)
        if d:
            paths.append(f'<path id="{id_}-c-{_slug(name)}" class="country{" hl" if name in hl else ""}" d="{d}" '
                         f'fill="{hl.get(name, land)}" stroke="{stroke}" stroke-width="1"/>')
    bg = f'<rect width="1920" height="1080" fill="{sea}"/>' if sea else ""
    return f'<g id="{id_}">{bg}{"".join(paths)}</g>'


def route_path(points: list[tuple[float, float]], proj, steps: int = 48) -> str:
    """Great-circle route through (lon, lat) points, projected — draw it on with mDrawOn / mFlow."""
    def interp(a, b, f):
        l1, p1, l2, p2 = map(math.radians, (a[0], a[1], b[0], b[1]))
        dist = 2 * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2)) or 1e-9
        A, B = math.sin((1 - f) * dist) / math.sin(dist), math.sin(f * dist) / math.sin(dist)
        x = A * math.cos(p1) * math.cos(l1) + B * math.cos(p2) * math.cos(l2)
        y = A * math.cos(p1) * math.sin(l1) + B * math.cos(p2) * math.sin(l2)
        z = A * math.sin(p1) + B * math.sin(p2)
        return math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.hypot(x, y)))
    pts = []
    for a, b in zip(points, points[1:]):
        for i in range(steps):
            q = proj(*interp(a, b, i / steps))
            if q:
                pts.append(q)
    q = proj(*points[-1])
    if q:
        pts.append(q)
    return "M" + " L".join("%.1f %.1f" % p for p in pts)


def pin_xy(lon: float, lat: float, proj) -> tuple[float, float] | None:
    return proj(lon, lat)


# ── diagrams ──────────────────────────────────────────────────────────────────────────────────
def diagram_node(id_: str, x: float, y: float, w: float, h: float, label: str, fill: str = "#14243a",
                 stroke: str = "#38d6ff", color: str = "#e8f3ff", size: int = 30) -> str:
    return (f'<g id="{id_}" class="dnode" style="opacity:0"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="4"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + size * .35}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{size}" fill="{color}">{html.escape(label)}</text></g>')


def diagram_edge(id_: str, x1: float, y1: float, x2: float, y2: float, bend: float = 0.0, color: str = "#38d6ff", width: int = 5) -> str:
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - bend
    return (f'<path id="{id_}" class="dedge" d="M{x1} {y1} Q{mx} {my} {x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" style="opacity:0"/>')


# ── end screen ────────────────────────────────────────────────────────────────────────────────
END_SCREEN = {"min_s": 5, "max_s": 20, "max_elements": 4}


def endscreen_html(px: str = "es", line: str = "Next on The Epoch Ledger", background: str = "") -> str:
    """Series end screen for YouTube's end-screen window (last 5–20 s). Slots are empty framed areas
    that YouTube's own video/subscribe elements cover; a live, slowly moving film background stays
    behind them. No logo sting: the channel identity is typography and palette only."""
    slot = lambda cls, x, y, w, h: (f'<div class="es-slot {cls}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                                    'border:3px solid rgba(242,198,109,.55);border-radius:14px;background:rgba(10,8,6,.35)"></div>')
    return (f'<div id="{px}" class="fill" style="opacity:0">'
            f'<div class="es-bg fill" style="filter:brightness(.55) saturate(.9)">{background}</div>'
            f'<div class="es-line" style="position:absolute;left:0;right:0;top:140px;text-align:center;font:800 58px Fraunces;color:#f3e3c3">{html.escape(line)}</div>'
            + slot("es-video", 150, 300, 760, 428) + slot("es-video", 1010, 300, 760, 428)
            + slot("es-sub", 880, 700, 160, 160).replace("border-radius:14px", "border-radius:50%")
            + '</div>')
