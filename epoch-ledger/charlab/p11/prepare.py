"""P11: prepare the 2.5D shots of the narration-driven re-direction, timed from the resolved narration-to-visual map
(every character action lands on its event's time, i.e. on the narrator's word).

    python3 epoch-ledger/charlab/p11/prepare.py FIG RESOLVED_MAP.json P10_PLATES P11_PLATES OUT_DIR

Uses the P10 compositor unchanged (compose.mjs / render_shot.mjs) and P10's cast; adds bust characters (the artist's
"Macbook" and "Device" bodies) for the story actions: the banker types the entry, the baker checks his account.
Writes OUT_DIR/shot{S1,S2,S4,S5}.json (S3 is the 3D vault, vault3d.mjs) and OUT_DIR/rig_client.json.
"""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "p8"))
import peeps_compose as PC  # noqa: E402

_s = importlib.util.spec_from_file_location("p10prep", os.path.join(HERE, "..", "p10", "prepare.py"))
P10 = importlib.util.module_from_spec(_s); _s.loader.exec_module(P10)      # character(), recolour(), blinks(), group_span()


def bust(C, parts, palette, faces, body_fills, patch=None):
    """a bust character with the head parts wrapped in one <g id="Head"> (as the standing figures have), so the
    compositor can turn the head about the neck and swap faces exactly as for standing figures"""
    svg = P10.recolour(P10.character(C, "bust", parts, palette, faces), body_fills)
    if patch:   # a plain patch in the surface's own colour (e.g. hides the comic logo drawn on the laptop lid)
        # inside BODY (so it belongs to the body layer, not the head layers), given in the figure's root coordinates
        a0 = svg.find('<g id="BODY"'); tx, ty = map(float, re.search(r'transform="matrix\([^)]* ([-\d.]+) ([-\d.]+)\)"', svg[a0:svg.find(">", a0)]).groups())
        e = P10.group_span(svg, "BODY")[1] - len("</g>")
        svg = svg[:e] + '<path transform="translate(%g %g)" d="%s" fill="%s"/>' % (-tx, -ty, *patch) + svg[e:]
    a = svg.find('<g id="HEAD"'); b = P10.group_span(svg, "ACCESORIES")[1]
    return svg[:a] + '<g id="Head">' + svg[a:b] + "</g>" + svg[b:]


def main(fig, resolved, p10plates, p11plates, out):
    os.makedirs(out, exist_ok=True)
    R = json.load(open(resolved)); E = {e["id"]: e["t"] for e in R["events"]}; SH = {s["id"]: s for s in R["shots"]}
    C = PC.Composer(fig); B, CL = PC.CAST["banker"], PC.CAST["client"]
    banker = P10.recolour(P10.character(C, "standing", {**B["parts"], "BODY": "pose/standing/blazer-4"}, B["palette"],
                                        ["Calm", "Serious", "Smile", "Eyes Closed"]), {1: "#2a1a12"})
    baker = P10.character(C, "standing", CL["parts"], CL["palette"], ["Serious", "Calm", "Smile", "Eyes Closed"])
    banker_laptop = bust(C, {**B["parts"], "BODY": "body/Macbook"}, B["palette"], ["Calm", "Serious", "Smile", "Eyes Closed"], {},
                         ("M936 958 H1046 V1062 H936 Z", B["palette"]["paper"]))   # the lid's comic logo, covered
    baker_phone = bust(C, {**CL["parts"], "BODY": "body/Device"}, CL["palette"], ["Serious", "Calm", "Smile", "Eyes Closed"], {1: CL["palette"]["cloth"]})
    rig = json.load(open(os.path.join(HERE, "..", "p10", "rigs", "pointing_finger-1.json")))
    rig["pieces"][0]["disc"]["fill"] = CL["palette"]["cloth"]; json.dump(rig, open(os.path.join(out, "rig_client.json"), "w"))
    bl_b, bl_c = P10.blinks(11, 0, R["duration"]), P10.blinks(23, 0, R["duration"])

    def track(d, k): return json.load(open(os.path.join(d, "track%s/track.json" % k)))["frames"][0]["pts"]

    def shot(sid, plate_dir, cam, cam2d, farFrom, chars, extra_pts=None):
        s0, s1 = SH[sid]["t0"], SH[sid]["t1"]; L = lambda t: round(t - s0, 3)
        for c in chars.values():
            c["faces"] = [[L(t), f] for t, f in c["faces"]]
            c["nods"] = [[L(n[0])] + list(n[1:]) for n in c.get("nods", [])]
            c["tilts"] = [[L(a), L(b), g] for a, b, g in c.get("tilts", [])]
            c["shifts"] = [[L(a), d, g] for a, d, g in c.get("shifts", [])]
            c["blinks"] = [[L(a), L(b)] for a, b in c["blinks"] if s0 <= a < s1]
            if c.get("joints"): c["joints"] = {j: [[L(t), v] for t, v in K] for j, K in c["joints"].items()}
        pts = {**track(plate_dir, cam), **(extra_pts or {})}
        json.dump(dict(id=sid, duration=round(s1 - s0, 3), plate=os.path.abspath(os.path.join(plate_dir, "cam%s_paint.png" % cam)),
                       depth=os.path.abspath(os.path.join(plate_dir, "track%s/depth_00000.png" % cam)), pts=pts, window="window",
                       cam2d=cam2d, farFrom=farFrom, farFactor=0.45, grade=dict(vignette=0.4, grain=4), chars=chars),
                  open(os.path.join(out, "shot%s.json" % sid), "w"))

    # S1 two-shot: the application slides across the desk (drawn in the sequence); the baker gestures toward it (his
    # forearm turns at the elbow, within the rig's clean range); the banker looks down at it and nods on "bank"
    d = SH["S1"]["t1"]
    shot("S1", p10plates, "A", [[0, 1.0, 960, 560], [d, 1.015, 960, 580]], 4.4, {
        "banker": dict(svg=banker, feet="banker_feet", head="banker_head", facing="left", blinks=bl_b,
                       faces=[[0, "Calm"], [E["e03"] - 0.15, "Serious"]], nods=[[E["e03"], 0.5]], tilts=[[E["e02"], d + 1, 4.0]]),
        "client": dict(svg=baker, rig=os.path.abspath(os.path.join(out, "rig_client.json")), feet="client_feet", head="client_head",
                       facing="right", blinks=bl_c, faces=[[0, "Serious"], [E["e03"], "Calm"]], tilts=[[0.1, d + 1, 3.0]],
                       joints={"fore": [[0, -4], [E["e02"] - 0.1, -4], [E["e02"] + 0.45, 11], [d, 9]]}),
    })
    # S2 insert from above: the application on the desk (the form itself is drawn in the sequence, keyed to the words)
    shot("S2", p11plates, "D", [[0, 1.0, 960, 540]], 99, {})   # locked: the sequence pushes in on plate and form together
    # S4 the banker types the entry (head down to the laptop, small typing bobs), then smiles as the account is credited
    typing = [[t, 0.22, 1.6] for t in (E["e13"] + 0.25, E["e14"] + 0.1, E["e14"] + 0.55, E["e15"] - 0.05, E["e15"] + 0.4, E["e16"] - 0.05)]
    shot("S4", p10plates, "B", [[0, 1.0, 960, 540], [SH["S4"]["t1"] - SH["S4"]["t0"], 1.02, 940, 540]], 3.4, {
        "banker": dict(svg=banker_laptop, feet="banker_base", head="banker_top", facing="left", blinks=bl_b,
                       faces=[[0, "Calm"], [E["e14"] + 0.9, "Serious"], [E["e17"], "Smile"]], nods=typing + [[E["e17"] + 0.1, 0.5]],
                       tilts=[[0, E["e16"] + 0.3, 3.0]]),
    }, {"banker_base": [1430, 1240, 1.0], "banker_top": [1430, 215, 1.0]})
    # S5 the baker checks his account on his phone; he smiles as the new money "exists"
    shot("S5", p10plates, "C", [[0, 1.0, 960, 540], [SH["S5"]["t1"] - SH["S5"]["t0"], 1.02, 980, 540]], 3.4, {
        "client": dict(svg=baker_phone, feet="client_base", head="client_top", facing="right", blinks=bl_c,
                       faces=[[0, "Serious"], [E["e23"], "Smile"]], nods=[[E["e19"] + 0.2, 0.45, 3.0], [E["e23"] + 0.15, 0.5]],
                       tilts=[[0, E["e22"], 3.5]]),
    }, {"client_base": [520, 1240, 1.0], "client_top": [520, 200, 1.0]})
    print(json.dumps({"shots": ["S1", "S2", "S4", "S5"], "out": out}))


if __name__ == "__main__":
    main(*sys.argv[1:6])
