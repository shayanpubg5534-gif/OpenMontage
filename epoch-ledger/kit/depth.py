"""Depth-layered environments: one scene3d set rendered as background / midground / foreground plates (cached PNGs),
composited with characters at their true depth and moved by a parallax camera (kit/depth.js).

    from kit import depth
    L = depth.layered(ws / "plates", "office", scene_js, cam, light_js, prelude_js=..., split=(2.4, 6.0),
                      blur={"fg": 5, "bg": 1.2}, haze=.18)
    L.png["bg"], L.png["mg"], L.png["fg"]           # plates/<name>-<layer>-<hash>.png (2x density, fg/mg transparent)
    html = L.html(sid, live_mid=characters_svg, live_front="")   # the layered stack for a shot
    js = L.move_js(sid, t0, d, truck=.25, dolly=.4)  # motivated camera move: layers shift / scale by 1/depth

Each layer is an ordinary cached plate (kit/plates.py), so changing a layer's contents re-renders only that layer.
Depth of field is baked into the plate (no per-frame blur cost). Characters belong to the midground: they move with
the depth of their feet and foreground objects occlude them. Original implementation.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from kit.plates import plate

KIT = Path(__file__).resolve().parent


def page_html(scene_js: str, cam_js: str, light_js: str, layer: str, split: tuple[float, float], prelude_js: str = "",
              blur: float = 0.0, background: str = "#201818", glows: bool = True) -> str:
    """A still page drawing one depth band of the set (transparent outside it except for the background band)."""
    bg = background if layer == "bg" else "transparent"
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:{bg}}}
svg{{position:absolute;inset:0;width:1920px;height:1080px}}#set,#glows{{filter:{f'blur({blur}px)' if blur else 'none'}}}</style>
<script src="scene3d.js"></script></head><body>
<svg id="set" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg"></svg>
<svg id="glows" viewBox="0 0 1920 1080" style="mix-blend-mode:screen;opacity:.8"></svg>
<script>const TEX = 'tex/';
{prelude_js}
{scene_js}
{cam_js}
{light_js}
document.getElementById('set').innerHTML = S3.render(sc, cam, L, {{ ow: 2.0, shadowBlur: 5, uid: 'd{layer}', layer: '{layer}', split: {json.dumps(list(split))} }});
if ({'true' if glows and layer == 'bg' else 'false'} && typeof GLOWS !== 'undefined') document.getElementById('glows').innerHTML = GLOWS.map(([p, r, c], i) => {{ const q = cam.project(p); if (!q) return '';
  const rr = r * Math.min(2.5, 14 / q[2]) + r * .3; return `<radialGradient id="gw${{i}}"><stop offset="0" stop-color="${{c}}" stop-opacity=".95"/><stop offset=".22" stop-color="${{c}}" stop-opacity=".4"/><stop offset="1" stop-color="${{c}}" stop-opacity="0"/></radialGradient><circle cx="${{q[0]}}" cy="${{q[1]}}" r="${{rr}}" fill="url(#gw${{i}})"/>`; }}).join('');
</script></body></html>"""


@dataclass
class Layered:
    name: str
    png: dict
    depth: dict                     # representative camera depth (m) per layer, for parallax
    focal: float                    # px per metre at 1 m (from the camera fov)
    haze: float = 0.0
    haze_color: str = "#e8d8c0"
    rel: dict = field(default_factory=dict)

    def html(self, sid: str, live_mid: str = "", live_front: str = "", live_back: str = "") -> str:
        """Stack: bg plate (+ live_back) · haze · mg plate · live_mid (characters, props) · fg plate · live_front."""
        lay = lambda k, inner: f'<div class="layer" id="{sid}-L{k}" data-depth="{self.depth[k]:.3f}">{inner}</div>'
        haze = (f'<div class="layer" style="background:linear-gradient(180deg,rgba(0,0,0,0) 20%,{self.haze_color} 70%,rgba(0,0,0,0) 100%);'
                f'opacity:{self.haze};mix-blend-mode:screen"></div>') if self.haze else ""
        img = lambda k: f'<img class="plate" src="{self.rel[k]}"/>' if k in self.rel else ""
        return (lay("bg", img("bg") + live_back) + haze + lay("mg", img("mg") + live_mid) + lay("fg", img("fg") + live_front))

    def move_js(self, sid: str, t0: float, d: float, truck: float = 0.0, dolly: float = 0.0, rise: float = 0.0,
                ease: str = "sine.inOut", focus: tuple[float, float] = (960, 540)) -> str:
        """A camera move as layer transforms: truck (m, +right), rise (m, +up), dolly (m, +forward)."""
        return (f"DL.move('{sid}', {t0:.3f}, {d:.3f}, {{ truck: {truck}, rise: {rise}, dolly: {dolly}, focal: {self.focal:.1f}, "
                f"ease: '{ease}', focus: {json.dumps(list(focus))} }});")


def layered(out_dir: Path, name: str, scene_js: str, cam, light_js: str, prelude_js: str = "",
            split: tuple[float, float] = (2.5, 6.0), blur: dict | None = None, haze: float = 0.0,
            background: str = "#201818", assets: tuple[Path, ...] = (), fov: float | None = None,
            layers: tuple[str, ...] = ("bg", "mg", "fg")) -> Layered:
    """Render the three depth bands of a set as cached plates. `cam` is a kit.camera3d.Camera (or anything with .js()
    and .fov). The plates directory must contain scene3d.js and tex/ like ordinary plates."""
    blur = blur or {}
    out_dir.mkdir(parents=True, exist_ok=True)
    if not (out_dir / "scene3d.js").exists() or (out_dir / "scene3d.js").read_text() != (KIT / "scene3d.js").read_text():
        (out_dir / "scene3d.js").write_text((KIT / "scene3d.js").read_text())
    cam_js = f"const cam = {cam.js()};"
    png, rel = {}, {}
    for layer in layers:
        html = page_html(scene_js, cam_js, light_js, layer, split, prelude_js, blur.get(layer, 0.0), background)
        p = plate(out_dir, f"{name}-{layer}", html, assets=tuple(assets) + (KIT / "scene3d.js",), transparent=layer != "bg")
        png[layer], rel[layer] = p, f"{out_dir.name}/{p.name}"
    f_ = 540 / math.tan(math.radians((fov or getattr(cam, "fov", 50)) / 2))
    near, far = split
    depth = {"fg": near * .7, "mg": (near + far) / 2, "bg": far * 1.8}
    return Layered(name, png, depth, f_, haze, rel=rel)


def foliage(w: int = 400, h: int = 640, seed: int = 7, pot: str = "#7a4a2a") -> str:
    """Illustrated potted plant for near foregrounds (deterministic): overlapping pointed leaves with midribs in
    several greens on arching stems, in a pot. Place it with sc.art(..., {layer: 'fg'}) facing the camera."""
    import random
    r = random.Random(seed)
    greens = ["#2f5f32", "#3d7a3a", "#4c8a42", "#2a5230", "#5a9a4c"]
    cx, base = w / 2, h - 150
    out = [f'<path d="M{cx - 90} {h - 150} L{cx + 90} {h - 150} L{cx + 70} {h} L{cx - 70} {h}Z" fill="{pot}" stroke="#1b1410" stroke-width="4"/>',
           f'<rect x="{cx - 98}" y="{h - 168}" width="196" height="26" rx="6" fill="{pot}" stroke="#1b1410" stroke-width="4"/>']
    leaves = []
    for i in range(34):
        ang = math.radians(-90 + r.uniform(-75, 75))
        L = r.uniform(.35, 1.0) * (h - 170)
        bend = r.uniform(-.35, .35)
        tipx, tipy = cx + math.cos(ang) * L * .55, base + math.sin(ang) * L
        midx, midy = cx + math.cos(ang + bend) * L * .3, base + math.sin(ang + bend) * L * .5
        out.append(f'<path d="M{cx:.0f} {base:.0f} Q{midx:.0f} {midy:.0f} {tipx:.0f} {tipy:.0f}" stroke="#2a3a20" stroke-width="3" fill="none"/>')
        lw, ll = r.uniform(22, 40), r.uniform(70, 130)
        a = math.atan2(tipy - midy, tipx - midx)
        leaves.append((tipy, tipx, tipy, a, lw, ll, r.choice(greens)))
    for _, x, y, a, lw, ll, g in sorted(leaves, key=lambda q: -q[0]):
        ca, sa = math.cos(a), math.sin(a)
        P = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
        p0, p1, p2, p3 = P(0, 0), P(ll * .5, lw), P(ll, 0), P(ll * .5, -lw)
        out.append(f'<path d="M{p0[0]:.0f} {p0[1]:.0f} Q{p1[0]:.0f} {p1[1]:.0f} {p2[0]:.0f} {p2[1]:.0f} Q{p3[0]:.0f} {p3[1]:.0f} {p0[0]:.0f} {p0[1]:.0f}Z" '
                   f'fill="{g}" stroke="#1b1410" stroke-width="2.5"/><path d="M{p0[0]:.0f} {p0[1]:.0f} L{p2[0]:.0f} {p2[1]:.0f}" stroke="#a8c890" stroke-width="2" opacity=".5"/>')
    return f'<g>{"".join(out)}</g>'
