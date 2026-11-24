"""Epoch Ledger cinematic light & atmosphere layers (HTML/SVG, deterministic). Original implementation.

Use around a scene3d / illustrated set, back to front:
  sky(...)            graded sky with sun glow and soft clouds (dusk, day, night, overcast presets)
  haze(...)           height/distance haze band (atmospheric perspective at the horizon)
  beams(...)          volumetric light shafts (window light, street lamps, spotlights) — screen blend
  glow(...)           bloom-like radial glows on light sources (lamps, screens, signs)
  depth_blur(px)      CSS filter for out-of-focus foreground/background layers (depth of field)
  grade(...)          final colour grade + vignette + film grain overlay (feTurbulence, seeded)
All sizes in 1920×1080 authoring pixels.
"""
from __future__ import annotations

SKIES = {
    "dusk": ("#1d2147", "#5b3a66", "#c4606a", "#f39a5e", "#ffd08a"),
    "day": ("#3d6fb0", "#6f9ed0", "#a9c8e6", "#d8e6f0", "#f2efe6"),
    "night": ("#05070f", "#0b1226", "#16203c", "#26304e", "#3a3a58"),
    "overcast": ("#6f7782", "#8a929c", "#a3aab2", "#bcc1c6", "#d0d2d2"),
}


def sky(preset: str = "dusk", sun: tuple[float, float] | None = (960, 600), sun_r: float = 520, clouds: int = 6, seed: int = 3, id_: str = "lf-sky") -> str:
    c = SKIES[preset]
    stops = "".join(f'<stop offset="{o}" stop-color="{col}"/>' for o, col in zip((0, .3, .55, .78, 1), c))
    sun_svg = ""
    if sun:
        sun_svg = (f'<radialGradient id="{id_}-sun" cx="{sun[0]}" cy="{sun[1]}" r="{sun_r}" gradientUnits="userSpaceOnUse">'
                   f'<stop offset="0" stop-color="#fff2c8" stop-opacity=".95"/><stop offset=".12" stop-color="#ffd890" stop-opacity=".7"/>'
                   f'<stop offset=".45" stop-color="#ff9a5a" stop-opacity=".22"/><stop offset="1" stop-color="#ff9a5a" stop-opacity="0"/></radialGradient>')
    import random
    r = random.Random(seed)
    cl = "".join(f'<ellipse cx="{r.uniform(-100, 2020):.0f}" cy="{r.uniform(60, 420):.0f}" rx="{r.uniform(220, 520):.0f}" ry="{r.uniform(18, 46):.0f}" '
                 f'fill="{c[3]}" opacity="{r.uniform(.18, .38):.2f}"/>' for _ in range(clouds))
    return (f'<svg id="{id_}" class="lf-layer" viewBox="0 0 1920 1080" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%">'
            f'<defs><linearGradient id="{id_}-g" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>{sun_svg}'
            f'<filter id="{id_}-cb"><feGaussianBlur stdDeviation="14"/></filter></defs>'
            f'<rect width="1920" height="1080" fill="url(#{id_}-g)"/>'
            + (f'<rect width="1920" height="1080" fill="url(#{id_}-sun)"/>' if sun else "")
            + f'<g filter="url(#{id_}-cb)">{cl}</g></svg>')


def haze(y: float = 620, height: float = 360, color: str = "#f2b48a", strength: float = .55, id_: str = "lf-haze") -> str:
    return (f'<div id="{id_}" class="lf-layer" style="position:absolute;left:0;right:0;top:{y - height / 2}px;height:{height}px;pointer-events:none;'
            f'background:linear-gradient(180deg,rgba(0,0,0,0),{color} 50%,rgba(0,0,0,0));opacity:{strength};mix-blend-mode:screen"></div>')


def beams(shafts: list[tuple[float, float, float, float, float]], color: str = "#fff1c8", opacity: float = .22, blur: float = 18, id_: str = "lf-beams") -> str:
    """shafts: (x_top, y_top, x_bottom, y_bottom, width_bottom) — a widening trapezoid per light shaft."""
    polys = "".join(f'<path d="M{xt - 10} {yt} L{xt + 10} {yt} L{xb + wb / 2} {yb} L{xb - wb / 2} {yb}Z" fill="url(#{id_}-g)"/>' for xt, yt, xb, yb, wb in shafts)
    return (f'<svg id="{id_}" class="lf-layer" viewBox="0 0 1920 1080" style="position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:screen;opacity:{opacity};pointer-events:none">'
            f'<defs><linearGradient id="{id_}-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>'
            f'<filter id="{id_}-b"><feGaussianBlur stdDeviation="{blur}"/></filter></defs><g filter="url(#{id_}-b)">{polys}</g></svg>')


def glow(points: list[tuple[float, float, float, str]], opacity: float = .8, id_: str = "lf-glow") -> str:
    """points: (x, y, radius, colour) — soft bloom around light sources."""
    grads = "".join(f'<radialGradient id="{id_}-{i}"><stop offset="0" stop-color="{c}" stop-opacity=".9"/><stop offset=".25" stop-color="{c}" stop-opacity=".35"/>'
                    f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>' for i, (_, _, _, c) in enumerate(points))
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{id_}-{i})"/>' for i, (x, y, r, _) in enumerate(points))
    return (f'<svg id="{id_}" class="lf-layer" viewBox="0 0 1920 1080" style="position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:screen;opacity:{opacity};pointer-events:none">'
            f'<defs>{grads}</defs>{dots}</svg>')


def depth_blur(px: float) -> str:
    return f"filter:blur({px}px)"


def grade(vignette: float = .55, grain: float = .07, warmth: float = 0.0, contrast: float = 1.06, saturate: float = 1.04, seed: int = 7, id_: str = "lf-grade") -> tuple[str, str]:
    """Returns (overlay_html, root_css_filter). Grain uses a seeded feTurbulence (static per frame)."""
    over = (f'<div id="{id_}-v" class="lf-layer" style="position:absolute;inset:0;pointer-events:none;'
            f'background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 55%,rgba(8,4,10,{vignette}) 100%)"></div>'
            f'<svg id="{id_}-n" class="lf-layer" viewBox="0 0 1920 1080" style="position:absolute;inset:0;width:100%;height:100%;opacity:{grain};mix-blend-mode:overlay;pointer-events:none">'
            f'<filter id="{id_}-t"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="{seed}" stitchTiles="stitch"/>'
            f'<feColorMatrix type="saturate" values="0"/></filter><rect width="1920" height="1080" filter="url(#{id_}-t)"/></svg>')
    warm = f" sepia({warmth})" if warmth else ""
    return over, f"contrast({contrast}) saturate({saturate}){warm}"
