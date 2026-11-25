"""Profitable and Broke — the cast (new designs for this episode; drawn by kit/rig4.js).

Maya   — owner of the bakery: cream shirt with rolled sleeves, teal apron, hair in a bun; fuller build.
Daniel — the supermarket's buyer: navy blazer over a pale blue shirt, red lanyard and badge, chinos; tall and slim.
Okafor — the bank's business lender: charcoal suit, burgundy tie, glasses, grey hair and beard; broad build.
"""
from __future__ import annotations

import json


def _shade(hex_, k=.16):
    n = int(hex_[1:], 16)
    return "#%02x%02x%02x" % tuple(int(v * (1 - k)) for v in (n >> 16, n >> 8 & 255, n & 255))


CAST = {
    "maya": {"look": {"skin": "#c68a5e", "skinShade": "#a56b44", "skinLite": "#e3a97f", "hair": "#2a1a14", "hairHi": "#5a3a2a",
                      "hairStyle": "bun", "jacket": None, "shirt": "#efe4cf", "shirtShade": _shade("#efe4cf"), "sleeves": "rolled",
                      "apron": "#2f6f73", "trousers": "#3b3b46", "trousersShade": "#28283a", "shoes": "#3a2a20", "iris": "#3a2416",
                      "lashes": True, "lips": "#8a3a34"},
             "build": {"shW": .9, "waistW": 1.0, "hipW": 1.18, "chestD": 1.05, "head": .98, "torso": .97, "thigh": .97, "shin": .97,
                       "armR": .95, "legR": 1.05}},
    "daniel": {"look": {"skin": "#f0c8a8", "skinShade": "#d6a888", "skinLite": "#fde0c6", "hair": "#9a4a26", "hairHi": "#c87a4a",
                        "hairStyle": "parted", "jacket": "#2b3a55", "jacketShade": "#1d2840", "shirt": "#cfe0f0", "shirtShade": _shade("#cfe0f0"),
                        "tie": None, "lanyard": "#d8352a", "trousers": "#b99d73", "trousersShade": "#9a8058", "shoes": "#5a3a22", "iris": "#3a5a6a"},
               "build": {"shW": 1.0, "waistW": .92, "hipW": .95, "torso": 1.05, "thigh": 1.04, "shin": 1.04, "uarm": 1.03, "farm": 1.03}},
    "okafor": {"look": {"skin": "#6b4026", "skinShade": "#52301b", "skinLite": "#8c5a3a", "hair": "#b8b4ac", "hairHi": "#e0dcd4",
                        "hairStyle": "buzz", "jacket": "#3a3d44", "jacketShade": "#26282e", "shirt": "#f2f2ee", "shirtShade": _shade("#f2f2ee"),
                        "tie": "#6a2a3a", "trousers": "#34373e", "trousersShade": "#22242a", "shoes": "#141416", "iris": "#1e140e",
                        "glasses": True, "beard": True},
               "build": {"shW": 1.1, "waistW": 1.18, "hipW": 1.08, "chestD": 1.12, "waistD": 1.2, "head": 1.04, "armR": 1.08, "legR": 1.08}},
}


def create_js(p: str, who: str, x: float, yaw: float, ground: float = 1000, blink_seed: int = 1, t0: float = 0, t1: float = 60,
              occlude: dict | None = None, scale: float = 1.0) -> str:
    c = CAST[who]
    spec = {"look": c["look"], "build": c["build"], "x": x, "yaw": yaw, "ground": ground, "scale": scale,
            "blinkSeed": blink_seed, "t0": t0, "t1": t1}
    if occlude:
        spec["occlude"] = occlude
    return f"R4.create({json.dumps(p)}, {json.dumps(spec)});"
