"""P13R: the 2.5D shots in the family's kitchen for the paced pilot (same compositor, plates, identities and approved 2008
wardrobe change as P13; P13's own files are unchanged). Film times come from the resolved P13R map.

    python3 epoch-ledger/charlab/p13r/shots.py FIG RESOLVED_MAP.json PLATES_DIR OUT_DIR

  K1  0.00–5.00  dusk wide: he leans in on "signs"; on "first home" she looks up and around their kitchen, warming
  KT  5.00–9.90  the table from above (the signature and the budget bar are laid over it in the sequence)
  N1 45.99–50.00 night wide: she reads the letter; on "stop" her head drops; he turns away;
                 held while "Now the losses rise from the bottom" begins
  N2 64.60–78.00 night wide: on "September" he looks down at the newspaper on their table; on "Lehman" she looks to him;
                 after the headline insert he turns back toward her; the lamp; a slow pull-out
  NT 69.60–75.20 the newspaper from above (the insert)
Motion is calm (slow pushes, one action at a time), so the viewer can watch the people while reading the captions.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "p13"), os.path.join(HERE, "..", "p12"), os.path.join(HERE, "..", "p8")]
import cast as CAST  # noqa: E402
import peeps_compose as PC  # noqa: E402
from keyframes import WARDROBE_CHANGES  # noqa: E402
from prepare import blinks, with_faces  # noqa: E402

SHOTS = {"K1": (0.0, 5.0, "dusk"), "KT": (5.0, 9.9, "dusk_top"), "N1": (45.99, 50.0, "night"),
         "N2": (64.6, 78.0, "night"), "NT": (69.6, 75.2, "night_top")}
NT_CAM = [[69.6, 1.0, 960, 540], [75.2, 1.22, 900, 540]]


def main(fig, resolved, plates, out):
    os.makedirs(out, exist_ok=True)
    E = {e["id"]: e["t"] for e in json.load(open(resolved))["events"]}
    CAST.CAST = copy.deepcopy(CAST.CAST)
    for cid, w in WARDROBE_CHANGES.items(): CAST.CAST[cid]["bodies"].append(w["body"])
    C = PC.Composer(fig); errs = {k: v for k, v in CAST.validate(C).items() if v}
    if errs: raise SystemExit("continuity: " + json.dumps(errs))
    trk = lambda v: json.load(open(os.path.join(plates, "track_%s/track.json" % v)))["frames"][0]["pts"]

    def shot(sid, chars, cam2d, light):
        t0, t1, v = SHOTS[sid]; L = lambda t: round(t - t0, 3)
        for c in chars.values():
            c["faces"] = [[L(t), f] for t, f in c["faces"]]
            c["tilts"] = [[L(a), L(b), g] for a, b, g in c.get("tilts", [])]
            c["shifts"] = [[L(a), d, g] for a, d, g in c.get("shifts", [])]
            c["blinks"] = [[L(a), L(b)] for a, b in c.get("blinks", []) if t0 <= a < t1]
            c["light"] = light
        json.dump(dict(id=sid, duration=round(t1 - t0, 3), plate=os.path.abspath(os.path.join(plates, "%s_paint.png" % v)),
                       depth=os.path.abspath(os.path.join(plates, "track_%s/depth_00000.png" % v)), pts=trk(v), window="window",
                       cam2d=[[L(t), z, x, y] for t, z, x, y in cam2d], farFrom=3.6 if chars else 99, farFactor=0.45,
                       grade=dict(vignette=0.38, grain=4), chars=chars), open(os.path.join(out, "shot%s.json" % sid), "w"))

    husband = with_faces(C, "husband", "body/Button Shirt 2", ["Blank", "Calm", "Tired", "Serious"])
    wife = with_faces(C, "wife", "body/Coffee", ["Serious", "Calm", "Solemn"])
    wife08 = with_faces(C, "wife", "body/Paper", ["Serious", "Solemn", "Tired"])
    bh, bw = blinks(5, 0, 78), blinks(9, 0, 78)
    dusk = {"match": {"tint": .14, "shadow": .24}}; night = {"match": {"tint": .26, "shadow": .36}}
    sg, hm = E["e_signs"], E["e_home"]
    shot("K1", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="left", blinks=bh, faces=[[0, "Blank"]],
                        tilts=[[sg - .3, 6.0, 7.5]], shifts=[[sg - .35, .7, 2.6]]),
        "wife": dict(svg=wife, feet="wife_base", head="wife_top", facing="right", blinks=bw, faces=[[0, "Serious"], [hm + .1, "Calm"]],
                     tilts=[[0.3, hm - .05, 3.5], [hm, 6.0, -3.0]], shifts=[[hm, .9, 1.2]]),
    }, [[0, 1.0, 960, 560], [5.0, 1.06, 980, 580]], dusk)
    shot("KT", {}, [[5.0, 1.0, 960, 540], [9.9, 1.06, 980, 520]], dusk)
    st = E["e_stop"]
    shot("N1", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="right", blinks=bh,
                        faces=[[45.99, "Serious"], [st + .1, "Tired"]], tilts=[[st + .05, 60, 6.5]], shifts=[[st + .1, .8, 2.2]]),
        "wife": dict(svg=wife08, feet="wife_base", head="wife_top", facing="right", blinks=bw,
                     faces=[[45.99, "Serious"], [st, "Solemn"]], tilts=[[45.99, 60, 2.0], [st - .1, 60, 4.5]]),
    }, [[45.99, 1.02, 900, 580], [50.0, 1.09, 840, 620]], night)
    sp, lh = E["e_sept"], E["e_lehman"]
    shot("N2", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="left", blinks=bh,
                        faces=[[64.6, "Tired"], [75.6, "Serious"]], tilts=[[sp - .1, 75.7, 6.0], [75.7, 90, -2.0]],
                        shifts=[[sp - .1, .9, 1.8], [75.7, 1.0, -1.8]]),
        "wife": dict(svg=wife08, feet="wife_base", head="wife_top", facing="right", blinks=bw,
                     faces=[[64.6, "Solemn"], [lh, "Tired"]], tilts=[[64.6, lh - .05, 4.5], [lh, 90, -2.5]]),
    }, [[64.6, 1.0, 960, 560], [lh, 1.0, 960, 560], [69.6, 1.1, 1060, 680], [75.2, 1.1, 1060, 680], [75.3, 1.04, 960, 560], [78.0, 1.0, 960, 560]], night)
    shot("NT", {}, NT_CAM, night)
    print(json.dumps({"shots": list(SHOTS), "continuity": "ok"}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
