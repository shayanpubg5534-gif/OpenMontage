"""Epoch Ledger diegetic financial graphics — data that lives *on objects in the scene*, not on floating panels.

Each builder returns SVG markup authored in its own pixel box (w × h). Map it onto a surface with
scene3d `sc.art(p0, p1, p3, w, h, markup)` (whiteboards, monitors, billboards, wall clippings, dials) or place it
in a 2.5D layer. Numbers come from the episode's research; the builders only draw. Original implementation.

  whiteboard_chart  marker-drawn bar chart with a hand-written annotation (meetings, explanations by a character)
  crt_chart         line chart on a period monitor with scanlines and a headline figure (late-night, trading desks)
  ticker_board      large LED market board with a single trend line (street, trading floor)
  gauge             analogue dial on a pipe, tank or machine (cash pressure, heat, utilisation)
  press_clip        framed newspaper clipping with a headline figure (funding rounds, bankruptcies)
All builders are deterministic; wobble uses a seeded generator so a redraw is identical.
"""
from __future__ import annotations

import math
import random

INK = "#1b1410"


def _wobble(pts, amp, seed):
    r = random.Random(seed)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def _marker_rect(x0, y0, x1, y1, fill, stroke, seed, amp=2.5):
    """Hand-drawn bar: slightly wobbly outline, translucent marker fill with hatching."""
    p = _wobble([(x0, y1), (x0, y0), (x1, y0), (x1, y1)], amp, seed)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p)
    hatch = "".join(f'<path d="M{x0 + 6} {yy:.0f} L{x1 - 6} {yy - 14:.0f}" stroke="{stroke}" stroke-width="2" opacity=".25"/>'
                    for yy in range(int(y0) + 24, int(y1), 22))
    return f'<path d="{d}" fill="{fill}" fill-opacity=".55" stroke="{stroke}" stroke-width="5" stroke-linejoin="round"/>{hatch}'


def whiteboard_chart(title: str, bars: list[tuple[str, float, str]], note: list[str] | None = None, highlight: int | None = None,
                     w: int = 1000, h: int = 560, seed: int = 4) -> str:
    """bars: (label, value, colour). The highlight bar (default: the smallest) gets a red marker arrow + note."""
    vmax = max(v for _, v, _ in bars) or 1
    base, top = h - 90, 150
    n = len(bars)
    slot = (w * .62) / n
    out = [f'<rect width="{w}" height="{h}" fill="#f6f4ee"/><rect width="{w}" height="{h}" fill="none" stroke="#9aa0a8" stroke-width="18"/>',
           f'<text x="60" y="92" font-family="Inter" font-weight="800" font-size="52" fill="#1f3a7a">{title}</text>',
           f'<path d="M60 112 C200 104 330 116 {60 + len(title) * 30} 108" stroke="#1f3a7a" stroke-width="5" fill="none"/>',
           f'<path d="M90 {base} H{w - 70}" stroke="#2a2a30" stroke-width="5"/>']
    hi = highlight if highlight is not None else min(range(n), key=lambda i: bars[i][1])
    for i, (lab, v, col) in enumerate(bars):
        x0 = 120 + i * slot + (slot * .9 if i == hi and hi == n - 1 else 0)
        x1 = x0 + slot * .72
        y0 = base - (base - top) * v / vmax
        dark = {"#e07a5f": "#b0402a", "#f2c66d": "#a07a20", "#7fd8ff": "#2a7aa0", "#5fb36a": "#2a6a2a"}.get(col, INK)
        out.append(_marker_rect(x0, y0, x1, base, col, dark, seed + i))
        out.append(f'<text x="{(x0 + x1) / 2:.0f}" y="{base + 50}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="34" '
                   f'fill="{dark if i == hi else "#2a2a30"}">{lab}</text>')
        if i == hi:
            ax = x0 - 50
            out.append(f'<path d="M{ax - 30} {top + 50} C{ax + 10} {top + 80} {ax + 20} {y0 - 120} {ax + 10} {y0 - 30}" stroke="#d9503f" stroke-width="6" fill="none"/>'
                       f'<path d="M{ax - 2} {y0 - 48} L{ax + 10} {y0 - 26} L{ax + 26} {y0 - 46}" stroke="#d9503f" stroke-width="6" fill="none"/>')
    for k, line in enumerate(note or []):
        out.append(f'<text x="{w - 230}" y="{230 + k * 52}" font-family="Inter" font-weight="800" font-size="40" fill="#d9503f">{line}</text>')
    out.append(f'<rect x="60" y="{h - 20}" width="140" height="14" rx="7" fill="#2a2a30"/><rect x="230" y="{h - 20}" width="140" height="14" rx="7" fill="#d9503f"/>')
    return "".join(out)


def crt_chart(title: str, values: list[float], label: str = "", figure: str = "", color: str = "#ff5a4a",
              w: int = 640, h: int = 480, bg: str = "#120708", uid: str = "crt") -> str:
    """Line chart on a CRT (scanlines). values are plotted left→right, scaled to the panel."""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    x0, x1, y0, y1 = 50, w - 40, 110, h - 50
    pts = [(x0 + (x1 - x0) * i / (len(values) - 1), y1 - (y1 - y0) * (v - lo) / span) for i, v in enumerate(values)]
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    grid = "".join(f'<path d="M40 {y0 + k * (y1 - y0) / 4:.0f} H{w - 30}" stroke="{color}" stroke-opacity=".14" stroke-width="2"/>' for k in range(5))
    return (f'<defs><pattern id="{uid}-scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="{bg}"/><rect width="{w}" height="56" fill="{color}" fill-opacity=".14"/>'
            f'<text x="22" y="40" font-family="Inter" font-weight="800" font-size="30" fill="{color}" fill-opacity=".85">{title}</text>{grid}'
            f'<path d="{d} L{pts[-1][0]:.0f} {y1 + 20} L{pts[0][0]:.0f} {y1 + 20}Z" fill="{color}" opacity=".16"/>'
            f'<path d="{d}" stroke="{color}" stroke-width="10" fill="none" stroke-linejoin="round"/>'
            f'<circle cx="{pts[-1][0]:.0f}" cy="{pts[-1][1]:.0f}" r="12" fill="#ffe0d8"/>'
            + (f'<text x="{w * .52:.0f}" y="112" font-family="Inter" font-weight="800" font-size="26" fill="{color}" fill-opacity=".8">{label}</text>' if label else "")
            + (f'<text x="{w * .52:.0f}" y="168" font-family="Inter" font-weight="800" font-size="54" fill="{color}">{figure}</text>' if figure else "")
            + f'<rect width="{w}" height="{h}" fill="url(#{uid}-scan)" opacity=".35"/>')


def ticker_board(title: str, values: list[float], color: str = "#7cff9b", w: int = 1400, h: int = 1000) -> str:
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    pts = [(90 + (w - 230) * i / (len(values) - 1), h - 140 - (h - 400) * (v - lo) / span) for i, v in enumerate(values)]
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    up = values[-1] >= values[0]
    return (f'<rect width="{w}" height="{h}" fill="#060d0a"/><rect x="20" y="20" width="{w - 40}" height="{h - 40}" fill="none" stroke="#1e3a2a" stroke-width="6"/>'
            + "".join(f'<path d="M80 {180 + k * 140} H{w - 80}" stroke="#12301e" stroke-width="3"/>' for k in range(6))
            + f'<text x="90" y="120" font-family="Inter" font-weight="800" font-size="72" fill="{color}" letter-spacing="8">{title}</text>'
            f'<path d="{d}" stroke="{color}" stroke-width="16" fill="none" stroke-linejoin="round"/>'
            f'<circle cx="{pts[-1][0]:.0f}" cy="{pts[-1][1]:.0f}" r="26" fill="#c8ffd8"/>'
            f'<text x="{w - 360}" y="140" font-family="Inter" font-weight="800" font-size="80" fill="{color}">{"▲" if up else "▼"}</text>')


def gauge(label: str, frac: float, w: int = 200, danger: str = "#d9503f") -> str:
    """Analogue dial; frac 0..1 sweeps the needle from left (empty) to right (full). Red zone on the low end."""
    a = math.pi * (1 - max(0.0, min(1.0, frac)))
    nx, ny = 100 + 62 * math.cos(a), 104 - 62 * math.sin(a)
    return (f'<g transform="scale({w / 200})"><circle cx="100" cy="100" r="92" fill="#f6f0dc" stroke="#6a4a20" stroke-width="12"/>'
            f'<path d="M40 130 A68 68 0 0 1 72 46" stroke="{danger}" stroke-width="14" fill="none"/><path d="M72 46 A68 68 0 0 1 160 130" stroke="#8a8a80" stroke-width="6" fill="none"/>'
            f'<path d="M100 104 L{nx:.1f} {ny:.1f}" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><circle cx="100" cy="104" r="10" fill="{INK}"/>'
            f'<text x="100" y="168" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="#3a2a18">{label}</text></g>')


def press_clip(masthead: str, headline: str, figure: str, w: int = 500, h: int = 450, figure_color: str = "#2a6a2a") -> str:
    return (f'<rect width="{w}" height="{h}" fill="#f2ead8"/><text x="{w / 2}" y="70" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="44" fill="{INK}">{masthead}</text>'
            f'<path d="M30 92 H{w - 30}" stroke="{INK}" stroke-width="4"/><text x="{w / 2}" y="170" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="50" fill="{INK}">{headline}</text>'
            f'<text x="{w / 2}" y="240" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="72" fill="{figure_color}">{figure}</text>'
            + "".join(f'<rect x="40" y="{280 + k * 26}" width="{w - 80 - (k * 37) % 120}" height="10" fill="#9a9080"/>' for k in range(6)))
