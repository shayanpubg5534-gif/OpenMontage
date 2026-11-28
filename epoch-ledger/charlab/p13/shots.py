"""P13 pilot: the 2.5D shots in the family's kitchen, acted from the narration's word times (P10 compositor unchanged,
P12 identities, the approved 2008 wardrobe change). Writes shot JSONs for compose.mjs.

    python3 epoch-ledger/charlab/p13/shots.py FIG RESOLVED_MAP.json PLATES_DIR OUT_DIR

Acting is story action within the art's range (STANDARD §3A.4): weight shifts and leans about the base, head direction
toward what matters (papers, letter, newspaper, each other), expression changes, held objects (her mug in 2006, the
letter in 2008). What the art cannot perform (a hand signing) is a cut on action to an insert (see the sequence).

  K1  0.00–5.94  dusk wide: he leans in to sign (cut on action to the insert), sits back relieved; she watches him,
                 then looks away toward the window; the camera follows her look to the street
  KT  2.45–5.09  dusk, the table from above (the insert's ground: the document is laid over it in the sequence)
  N1 19.15–20.99 night wide: she reads the letter again; on "stop" her head drops; he turns away and sits back
  N2 24.14–30.00 night wide: the newspaper on the table; he looks down at it on "September"; she looks to him
  NT 26.29–28.60 night, the table from above: the newspaper's front page (the insert)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "p12"), os.path.join(HERE, "..", "p8")]
import cast as CAST  # noqa: E402
import peeps_compose as PC  # noqa: E402
from keyframes import WARDROBE_CHANGES  # noqa: E402
from prepare import blinks, with_faces  # noqa: E402

SHOTS = {"K1": (0.0, 5.94, "dusk"), "KT": (2.45, 5.09, "dusk_top"), "N1": (19.15, 20.99, "night"),
         "N2": (24.14, 30.0, "night"), "NT": (26.29, 28.6, "night_top")}


def main(fig, resolved, plates, out):
    os.makedirs(out, exist_ok=True)
    R = json.load(open(resolved)); E = {e["id"]: e["t"] for e in R["events"]}
    CAST.CAST = copy.deepcopy(CAST.CAST)                       # the approved 2008 change, in this process only
    for cid, w in WARDROBE_CHANGES.items(): CAST.CAST[cid]["bodies"].append(w["body"])
    C = PC.Composer(fig); errs = {k: v for k, v in CAST.validate(C).items() if v}
    if errs: raise SystemExit("continuity: " + json.dumps(errs))
    trk = lambda v: json.load(open(os.path.join(plates, "track_%s/track.json" % v)))["frames"][0]["pts"]

    def shot(sid, chars, cam2d, light):
        t0, t1, v = SHOTS[sid]; L = lambda t: round(t - t0, 3)
        for c in chars.values():                                  # film times → shot-local
            c["faces"] = [[L(t), f] for t, f in c["faces"]]
            c["tilts"] = [[L(a), L(b), g] for a, b, g in c.get("tilts", [])]
            c["shifts"] = [[L(a), d, g] for a, d, g in c.get("shifts", [])]
            c["nods"] = [[L(n[0])] + list(n[1:]) for n in c.get("nods", [])]
            c["blinks"] = [[L(a), L(b)] for a, b in c.get("blinks", []) if t0 <= a < t1]
            c["light"] = light
        json.dump(dict(id=sid, duration=round(t1 - t0, 3), plate=os.path.abspath(os.path.join(plates, "%s_paint.png" % v)),
                       depth=os.path.abspath(os.path.join(plates, "track_%s/depth_00000.png" % v)), pts=trk(v), window="window",
                       cam2d=[[L(t), z, x, y] for t, z, x, y in cam2d], farFrom=3.6 if chars else 99, farFactor=0.45,
                       grade=dict(vignette=0.38, grain=4), chars=chars), open(os.path.join(out, "shot%s.json" % sid), "w"))

    husband = with_faces(C, "husband", "body/Button Shirt 2", ["Blank", "Calm", "Tired", "Serious"])
    wife = with_faces(C, "wife", "body/Coffee", ["Serious", "Solemn", "Calm"])
    wife08 = with_faces(C, "wife", "body/Paper", ["Serious", "Solemn", "Tired"])
    bh, bw = blinks(5, 0, 30), blinks(9, 0, 30)
    dusk = {"match": {"tint": .14, "shadow": .24}}; night = {"match": {"tint": .26, "shadow": .36}}
    W = trk("dusk")["window"]
    # K1: he commits; she hesitates. "signs": he leans in (cut on action to the insert); after it he sits back, relieved;
    # on "The lender" she turns her head away toward the window, and the camera follows her look out to the street
    shot("K1", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="left", blinks=bh,
                        faces=[[0, "Blank"], [E["e_back"], "Calm"]],
                        tilts=[[E["e_signs"] - .35, E["e_back"] - .1, 7.5]], shifts=[[E["e_signs"] - .4, .6, 2.6], [E["e_back"], .7, -3.4]]),
        "wife": dict(svg=wife, feet="wife_base", head="wife_top", facing="right", blinks=bw,
                     faces=[[0, "Serious"], [E["e_back"] + .25, "Solemn"]],
                     tilts=[[0.25, E["e_back"], 3.5], [E["e_back"] + .3, 9, -4.5]], nods=[[E["e_family"], .5, 4.0]],
                     shifts=[[E["e_back"] + .3, .8, 1.6]]),
    }, [[0, 1.0, 960, 560], [E["e_signs"], 1.045, 980, 600], [E["e_back"] + .25, 1.045, 980, 600], [5.94, 1.16, 1240, 420]], dusk)
    shot("KT", {}, [[2.45, 1.0, 960, 540], [5.09, 1.07, 980, 520]], dusk)
    # N1: two years later, the same table. She reads the letter again; on "stop" her head drops; he turns away
    shot("N1", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="right", blinks=bh,
                        faces=[[19.15, "Serious"], [E["e_stop"] + .1, "Tired"]], tilts=[[E["e_stop"], 30, 6.5]], shifts=[[E["e_stop"] + .05, .7, 2.2]]),
        "wife": dict(svg=wife08, feet="wife_base", head="wife_top", facing="right", blinks=bw,
                     faces=[[19.15, "Serious"], [E["e_stop"], "Solemn"]], tilts=[[19.15, 30, 2.0], [E["e_stop"] - .1, 30, 4.5]]),
    }, [[19.15, 1.04, 900, 600], [20.99, 1.12, 820, 640]], night)
    # N2: the newspaper lies on their table. On "September" he looks down at it; she looks up at him
    shot("N2", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="left", blinks=bh,
                        faces=[[24.14, "Tired"]], tilts=[[E["e_sept"] - .2, 30, 6.0]], shifts=[[E["e_sept"] - .2, .8, 1.8]]),
        "wife": dict(svg=wife08, feet="wife_base", head="wife_top", facing="right", blinks=bw,
                     faces=[[24.14, "Solemn"], [25.4, "Tired"]], tilts=[[24.14, 25.3, 4.5], [25.35, 31, -2.5]]),
    }, [[24.14, 1.0, 960, 560], [26.29, 1.1, 1060, 680], [28.4, 1.1, 1060, 680], [28.6, 1.0, 960, 560], [30.0, 1.03, 960, 560]], night)
    shot("NT", {}, [[26.29, 1.0, 960, 540], [28.6, 1.22, 900, 540]], night)
    print(json.dumps({"shots": list(SHOTS), "continuity": "ok"}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
