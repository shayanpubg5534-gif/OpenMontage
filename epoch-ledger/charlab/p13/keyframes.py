"""P13 storyboard key frames in the family's kitchen (2.5D): the P10 compositor unchanged, the P12 cast identities, the
new kitchen world (sets.py). Writes one-frame shot JSONs; compose.mjs renders them.

    python3 epoch-ledger/charlab/p13/keyframes.py FIG PLATES_DIR OUT_DIR

KF1 (dusk 2006, "a family signs a mortgage they can barely afford"): he leans in over the papers with the pen cup at
hand, she holds her mug close and watches him, not the papers. KF6 (night 2008, "families stop paying … Lehman"): the
same table, the pendant off; she holds the letter, he leans away with his head down; on the table the papers have
become a single notice.

Wardrobe: the 2008 bookend proposes ONE declared change for the wife, the artist's "holding a paper" bust (a dark
sweater; its flecks take her sage), two years later. It is an extension of the P12 identity for approval, recorded in
WARDROBE_CHANGES; the head, hair and skin are unchanged and checked.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "p12"), os.path.join(HERE, "..", "p8")]
import cast as CAST  # noqa: E402
import peeps_compose as PC  # noqa: E402
from prepare import with_faces  # noqa: E402

WARDROBE_CHANGES = {"wife": {"body": "body/Paper", "when": "2008 bookend (two years later, evening)",
                             "why": "the only artist pose with a held letter: her hands carry the consequence"}}


def main(fig, plates, out):
    os.makedirs(out, exist_ok=True)
    CAST.CAST = copy.deepcopy(CAST.CAST)                       # extension in this process only; P12's cast is untouched
    for cid, w in WARDROBE_CHANGES.items(): CAST.CAST[cid]["bodies"].append(w["body"])
    C = PC.Composer(fig); errs = {k: v for k, v in CAST.validate(C).items() if v}
    if errs: raise SystemExit("continuity: " + json.dumps(errs))
    pts = lambda v: json.load(open(os.path.join(plates, "track_%s/track.json" % v)))["frames"][0]["pts"]
    light = {"match": {"tint": .14, "shadow": .24}}

    def shot(name, v, chars, cam2d, T=1.2):
        json.dump(dict(id=name, duration=T, plate=os.path.abspath(os.path.join(plates, "%s_paint.png" % v)),
                       depth=os.path.abspath(os.path.join(plates, "track_%s/depth_00000.png" % v)), pts=pts(v), window="window",
                       cam2d=cam2d, farFrom=3.6, farFactor=0.45, grade=dict(vignette=0.38, grain=4), chars=chars),
                  open(os.path.join(out, name + ".json"), "w"))

    husband = with_faces(C, "husband", "body/Button Shirt 2", ["Blank", "Concerned", "Tired"])
    wife = with_faces(C, "wife", "body/Coffee", ["Serious", "Calm"])
    wife08 = with_faces(C, "wife", "body/Paper", ["Solemn", "Concerned"])
    # KF1: he commits (leans in toward the papers, weight forward); she hesitates (mug held close, watching him)
    shot("kf1_signing", "dusk", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="left", faces=[[0, "Blank"]], tilts=[[0, 9, 7.0]],
                        shifts=[[0, .6, 2.5]], blinks=[], light=light),
        "wife": dict(svg=wife, feet="wife_base", head="wife_top", facing="right", faces=[[0, "Serious"]], tilts=[[0, 9, 3.0]], blinks=[], light=light),
    }, [[0, 1.0, 960, 560]])
    # KF6: the letter in her hands, his head down and turned away; the light left on by the sink
    light = {"match": {"tint": .3, "shadow": .42}}       # the night room: deeper form shadow, cooler tint
    shot("kf6_bookend", "night", {
        "husband": dict(svg=husband, feet="husband_base", head="husband_top", facing="right", faces=[[0, "Tired"]], tilts=[[0, 9, 6.0]],
                        shifts=[[0, .6, 2.0]], blinks=[], light=light),
        "wife": dict(svg=wife08, feet="wife_base", head="wife_top", facing="right", faces=[[0, "Solemn"]], tilts=[[0, 9, 5.0]], blinks=[], light=light),
    }, [[0, 1.0, 960, 560]])
    print(json.dumps({"shots": ["kf1_signing", "kf6_bookend"], "continuity": "ok", "wardrobe_changes": WARDROBE_CHANGES}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
