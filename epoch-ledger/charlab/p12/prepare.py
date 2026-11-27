"""P12: 2.5D shots of the mortgage passage, built ONLY from the cast identities (cast.py) and timed from the resolved
narration-to-visual map. Uses the P10 compositor unchanged, with P12's opt-in plate-matched lighting.

    python3 epoch-ledger/charlab/p12/prepare.py FIG RESOLVED_MAP.json PLATES_DIR OUT_DIR
Writes OUT_DIR/shot{S1,S2,S6,S8}.json (S3 is 3D; S4, S5, S7 are full-screen diagrams in the sequence).
"""
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "p8"))
import cast as CAST  # noqa: E402
import peeps_compose as PC  # noqa: E402


def with_faces(C, cid, body, faces):
    """the identity's figure in `body`, with every face it needs as a switchable layer; busts get a <g id="Head">"""
    base = CAST.compose(C, cid, body, faces[0])
    a, b = CAST.group_span(base, "FACE"); stack = []
    for k, f in enumerate(faces):
        s = CAST.compose(C, cid, body, f); fa, fb = CAST.group_span(s, "FACE")
        stack.append(s[fa:fb].replace('<g id="FACE"', '<g data-face="%s" style="display:%s"' % (f, "inline" if k == 0 else "none"), 1))
    svg = base[:a] + '<g id="FACE">' + "".join(stack) + "</g>" + base[b:]
    if CAST.KIND[body] == "bust":
        h0 = svg.find('<g id="HEAD"'); h1 = CAST.group_span(svg, "ACCESORIES")[1]
        svg = svg[:h0] + '<g id="Head">' + svg[h0:h1] + "</g>" + svg[h1:]
    return svg


def blinks(seed, t0, t1):
    rnd = random.Random(seed); t = t0 + rnd.uniform(0.6, 1.8); out = []
    while t < t1 - 0.3:
        d = rnd.choice((0.10, 0.12, 0.13)); out.append([round(t, 3), round(t + d, 3)]); t += rnd.uniform(2.2, 5.5)
    return out


def main(fig, resolved, plates, out):
    os.makedirs(out, exist_ok=True)
    R = json.load(open(resolved)); E = {e["id"]: e["t"] for e in R["events"]}; SH = {s["id"]: s for s in R["shots"]}
    C = PC.Composer(fig)
    errs = {k: v for k, v in CAST.validate(C).items() if v}
    if errs: raise SystemExit("continuity: " + json.dumps(errs))
    track = lambda k: json.load(open(os.path.join(plates, "track%s/track.json" % k)))["frames"][0]["pts"]

    def shot(sid, cam, chars, extra=None, cam2d=None):
        s0, s1 = SH[sid]["t0"], SH[sid]["t1"]; L = lambda t: round(t - s0, 3)
        for c in chars.values():
            c["faces"] = [[L(t), f] for t, f in c["faces"]]
            c["nods"] = [[L(n[0])] + list(n[1:]) for n in c.get("nods", [])]
            c["tilts"] = [[L(a), L(b), g] for a, b, g in c.get("tilts", [])]
            c["shifts"] = [[L(a), d, g] for a, d, g in c.get("shifts", [])]
            c["blinks"] = [[L(a), L(b)] for a, b in c.get("blinks", []) if s0 <= a < s1]
            c["light"] = {"match": {"tint": .12, "shadow": .22}}            # lit by the room it stands in
        json.dump(dict(id=sid, duration=round(s1 - s0, 3), plate=os.path.abspath(os.path.join(plates, "cam%s_paint.png" % cam)),
                       depth=os.path.abspath(os.path.join(plates, "track%s/depth_00000.png" % cam)), pts={**track(cam), **(extra or {})},
                       window="window", cam2d=cam2d or [[0, 1.0, 960, 540]], farFrom=3.4 if chars else 99, farFactor=0.45,
                       grade=dict(vignette=0.36, grain=4), chars=chars), open(os.path.join(out, "shot%s.json" % sid), "w"))

    husband = with_faces(C, "husband", "body/Button Shirt 2", ["Calm", "Serious", "Smile", "Eyes Closed"])
    wife = with_faces(C, "wife", "body/Coffee", ["Calm", "Smile", "Serious", "Solemn", "Eyes Closed"])
    bh, bw = blinks(5, 0, R["duration"]), blinks(9, 0, R["duration"])
    # S1: at the lender's office, the two of them (facing each other across the frame); 2006 on the wall calendar
    shot("S1", "B", {
        "husband": dict(svg=husband, feet="h_base", head="h_top", facing="right", blinks=bh, faces=[[0, "Serious"], [E["e03"] + .1, "Smile"]],
                        tilts=[[E["e03"] - .3, SH["S1"]["t1"] + 1, 4.0]]),
        "wife": dict(svg=wife, feet="w_base", head="w_top", facing="left", blinks=bw, faces=[[0, "Calm"], [E["e03"], "Smile"]],
                     nods=[[E["e03"] + .05, .5]]),
    }, {"h_base": [560, 1250, 1.0], "h_top": [560, 330, 1.0], "w_base": [1380, 1250, 1.05], "w_top": [1380, 320, 1.05]},
        cam2d=[[0, 1.0, 960, 540], [SH["S1"]["t1"] - SH["S1"]["t0"], 1.02, 960, 540]])
    shot("S2", "D", {})          # the desk from above (the mortgage agreement is drawn in the sequence)
    # S6: at home: she has her coffee; the overdue notice lies in front of her; her face falls on "stop"
    shot("S6", "C", {
        "wife": dict(svg=wife, feet="w_base", head="w_top", facing="right", blinks=bw, faces=[[SH["S6"]["t0"], "Calm"], [E["e20"], "Solemn"]],
                     tilts=[[E["e20"] - .1, SH["S6"]["t1"] + 1, 5.0]]),
    }, {"w_base": [640, 1250, 1.0], "w_top": [640, 250, 1.0]}, cam2d=[[0, 1.0, 960, 540], [SH["S6"]["t1"] - SH["S6"]["t0"], 1.02, 960, 600]])
    shot("S8", "D", {})          # the desk again: the newspaper is drawn in the sequence
    print(json.dumps({"shots": ["S1", "S2", "S6", "S8"], "continuity": "ok"}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
