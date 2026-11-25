"""Epoch Ledger character rig v4 — Python side: cast looks, sprite markup and creation JS for kit/rig4.js.

Rig v4 draws each character at runtime from a small 3D skeleton (see rig4.js), so the markup here is only an empty
group inside a sprite <svg>; looks (skin, hair, clothes) and build live in CAST and are passed to R4.create.
The cast keeps the v3 identities (same skin, hair and costume colours), so a character looks the same in either rig.
Rig v3 (kit/rig3.py, kit/rig3.js) remains available as the fallback. Original implementation.

  sprite_svg("fd", w=900)              → '<g id="fd"></g>' for a sprite whose viewBox is 0 0 900 1000
  create_js("fd", "founder", x=300, yaw=30) → "R4.create('fd', {...});"
"""
from __future__ import annotations

import json

from kit import rig3

# rig v3 palettes, reused so identities carry over
_S = rig3.SKINS
_H = rig3.HAIR


def _look(skin: int, hair: int, style: str, costume: str, **extra) -> dict:
    jacket, jacket_sh, shirt, tie, trousers, trousers_sh, shoes, _kind = rig3.COSTUMES[costume]
    s = _S[skin]
    look = {"skin": s[0], "skinShade": s[1], "skinLite": s[2], "hair": _H[hair], "hairStyle": style,
            "jacket": jacket, "jacketShade": jacket_sh, "shirt": shirt, "shirtShade": _shade(shirt), "tie": tie,
            "trousers": trousers, "trousersShade": trousers_sh, "shoes": shoes, "iris": "#3a2a1e"}
    look.update(extra)
    return look


def _shade(hex_: str, k: float = .16) -> str:
    n = int(hex_[1:], 16)
    r, g, b = n >> 16, n >> 8 & 255, n & 255
    return "#%02x%02x%02x" % tuple(int(v * (1 - k)) for v in (r, g, b))


# The proving cast: the founder (open-collar shirt, parted brown hair) and the investor (navy suit, red tie, grey hair).
CAST = {
    "founder": {"look": _look(0, 2, "parted", "founder", hairHi="#8a6a44", iris="#4a3524"),
                "build": {"shW": .95, "waistW": .92, "torso": 1.0}},
    "investor": {"look": _look(1, 5, "short", "suit", hairHi="#9a9a9a", iris="#2a1e16"),
                 "build": {"shW": 1.06, "waistW": 1.08, "head": 1.02, "torso": 1.02}},
}


def sprite_svg(p: str, w: int = 400, h: int = 1000) -> str:
    """Markup for a scene3d sprite (viewBox 0 0 w h): an empty group that R4 draws into every frame."""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" overflow="visible"><g id="{p}"></g></svg>'


def create_js(p: str, who: str, x: float = 200, yaw: float = 30, ground: float = 990, scale: float = 1.0,
              blink_seed: int | None = None, t0: float = 0, t1: float = 600) -> str:
    c = CAST[who]
    spec = {"look": c["look"], "build": c.get("build", {}), "x": x, "yaw": yaw, "ground": ground, "scale": scale}
    if blink_seed is not None:
        spec.update(blinkSeed=blink_seed, t0=t0, t1=t1)
    return f"R4.create({json.dumps(p)}, {json.dumps(spec)});"
