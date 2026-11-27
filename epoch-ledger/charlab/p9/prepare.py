"""P9: prepare a 2.5D animation shot: characters (Open Peeps parts, restyled) with every face they need embedded as
switchable layers, and the performance timeline (expressions, blinks, nods, tilts, weight shifts, arm beats).

    python3 epoch-ledger/charlab/p9/prepare.py FIG OUT_DIR
Writes OUT_DIR/shot{1,2}.json (characters + timeline) used by animate.mjs. Deterministic (seeded blinks).
"""
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p8"))
import peeps_compose as PC  # noqa: E402


def group_span(txt, gid):
    i = txt.find('<g id="%s"' % gid)
    depth = 0
    for m in re.finditer(r"<g[ >]|</g>", txt[i:]):
        depth += 1 if m.group(0) != "</g>" else -1
        if depth == 0: return i, i + m.end()


def character(C, base, pose, faces):
    """SVG with FACE replaced by one group per expression (data-face=name; only the first visible)."""
    parts = {**base["parts"], "BODY": "pose/standing/" + pose}
    svg = C.svg("standing", {**parts, "FACE": "face/" + faces[0]}, base["palette"])
    a, b = group_span(svg, "FACE"); stack = []
    for k, f in enumerate(faces):
        s = C.svg("standing", {**parts, "FACE": "face/" + f}, base["palette"]); fa, fb = group_span(s, "FACE")
        g = s[fa:fb].replace('<g id="FACE"', '<g data-face="%s" style="display:%s"' % (f, "inline" if k == 0 else "none"), 1)
        stack.append(g)
    return svg[:a] + '<g id="FACE">' + "".join(stack) + "</g>" + svg[b:]


def blinks(seed, t0, t1, closed="Eyes Closed"):
    """irregular blinks: 2.2–5.5 s apart, sometimes a double blink; 3–4 frames closed"""
    rnd = random.Random(seed); t = t0 + rnd.uniform(0.6, 1.8); out = []
    while t < t1 - 0.3:
        d = rnd.choice((0.10, 0.12, 0.13)); out.append([round(t, 3), round(t + d, 3)])
        if rnd.random() < 0.18: out.append([round(t + d + 0.18, 3), round(t + d + 0.18 + 0.1, 3)])
        t += rnd.uniform(2.2, 5.5)
    return out


fig, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
C = PC.Composer(fig); B, CL = PC.CAST["banker"], PC.CAST["client"]
# window (light source) in world space, for light direction per frame
WINDOW = [0.0, 1.6, -2.35]
shots = {
    1: dict(duration=9.0, plate="plate1", track="track1", behind_desk=["client"], focus_blur={},
            chars={
                "banker": dict(svg=character(C, B, "blazer-3", ["Calm", "Solemn", "Serious", "Smile", "Eyes Closed"]), height=1.66, facing="left",
                               faces=[[0, "Calm"], [2.6, "Solemn"], [5.2, "Serious"], [7.4, "Smile"]],
                               blinks=blinks(11, 0, 9), nods=[[6.0, 0.55], [6.9, 0.45]], tilts=[[1.2, 4.0, -5.0], [4.2, 7.2, 3.0]],
                               shifts=[[3.3, 1.0, -0.7], [7.6, 0.9, 0.5]], arm=None),
                "client": dict(svg=character(C, CL, "pointing_finger-1", ["Serious", "Driven", "Calm", "Eyes Closed"]), height=1.80, facing="right",
                               faces=[[0, "Serious"], [3.6, "Driven"], [6.6, "Calm"]],
                               blinks=blinks(23, 0, 9), nods=[[2.3, 0.4], [5.4, 0.45]], tilts=[[0.5, 3.0, 4.0], [5.8, 8.6, -3.0]],
                               shifts=[[1.9, 1.1, 0.6], [6.2, 1.0, -0.6]],
                               arm=dict(region=[0.70, 0.08, 1.12, 0.385], pivot=[0.725, 0.365], beats=[[1.0, 4.5], [2.6, -3.0], [4.3, 5.0], [5.9, 1.5], [7.6, 4.0]]))}),
    2: dict(duration=8.0, plate="plate2", track="track2", behind_desk=["banker"], focus_blur={"client": 2.2},
            chars={
                "banker": dict(svg=character(C, B, "blazer-3", ["Smile", "Calm", "Serious", "Eyes Closed"]), height=1.66, facing="left",
                               faces=[[0, "Smile"], [2.8, "Calm"], [5.6, "Serious"], [6.8, "Smile"]],
                               blinks=blinks(31, 0, 8), nods=[[1.4, 0.5], [4.8, 0.5]], tilts=[[0.3, 2.6, 4.0], [3.0, 6.4, -4.0]],
                               shifts=[[2.2, 1.0, 0.6], [6.0, 1.0, -0.5]], arm=None),
                "client": dict(svg=character(C, CL, "crossed_arms-1", ["Calm", "Smile", "Eyes Closed"]), height=1.80, facing="right",
                               faces=[[0, "Calm"], [3.4, "Smile"]],
                               blinks=blinks(47, 0, 8), nods=[[2.0, 0.5], [3.6, 0.4], [6.3, 0.5]], tilts=[[0.8, 5.0, 3.5]],
                               shifts=[[4.4, 1.2, -0.6]], arm=None)}),
}
for k, s in shots.items():
    s["window"] = WINDOW
    json.dump(s, open(os.path.join(out, "shot%d.json" % k), "w"))
print("prepared", out)
