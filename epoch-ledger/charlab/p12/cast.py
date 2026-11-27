"""P12: reusable character identities and wardrobe, with continuity validation (Open Peeps, the artist's own parts).

A character is ONE identity: head parts (hair, facial hair, glasses), skin and hair colour, and a wardrobe given by garment
ROLE (top, outer, bottom, shoes...). Each character may only use the bodies listed for it, chosen because they depict the
SAME garments (a collared shirt stays a collared shirt; a speckled knit stays a speckled knit). Each body maps its own
fill shapes (by index, from `wardrobe2.mjs --probe`) to roles, so every variant is recoloured from the identity, never by
hand. `validate()` composes every variant and checks head parts, skin, hair and each role's colour against the identity;
the artwork is never distorted (only fills are recoloured; poses come from the artist's bodies).

    python3 epoch-ledger/charlab/p12/cast.py FIG OUT_DIR      # writes every variant + continuity.json; exit 1 on a mismatch
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "p8"))
import peeps_compose as PC  # noqa: E402

INK, PAPER = "#1e1b19", "#efe8dc"
# body → {fill index: role}; "keep" leaves the artist's colour (props), ink stays ink (outlines, drawn-in black garments).
# Bodies whose garment is drawn in ink (e.g. "body/Paper": a black speckled sweater) cannot take a wardrobe colour; the
# rendered check (continuity.mjs) rejects them if they are ever listed for a character whose top is not ink.
BODIES = {
    "pose/standing/blazer-4": {0: "skin", 1: "shoes", 2: "outer", 3: "top"},
    "pose/standing/shirt-3": {0: "skin", 1: "shoes", 2: "top"},
    "body/Button Shirt 2": {0: "skin", 1: "top"},
    "body/Coffee": {0: "keep", 1: "skin", 2: "top"},
    "body/Paper": {0: "skin", 1: "keep", 2: "top"},
    "body/Device": {0: "skin", 1: "top", 2: "keep"},
}
KIND = {b: ("standing" if b.startswith("pose/standing") else "bust") for b in BODIES}

CAST = {
    # the loan officer (P10/P11's banker: the same person across the series)
    "banker": dict(head={"HEAD": "head/Gray Medium", "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/Glasses 2"},
                   skin="#c8946d", hair="#b9b4ac", wardrobe={"outer": "#2f3b52", "top": "#d9cfbd", "shoes": "#2a1a12"},
                   bodies=["pose/standing/blazer-4"], garments="navy blazer over a light blouse; dark trousers"),
    # dark hair in these heads is drawn in the artist's ink, so the identity's hair colour is ink
    "husband": dict(head={"HEAD": "head/Short 3", "FACIAL HAIR": "facial-hair/Moustache 2", "ACCESORIES": "accessories/* None"},
                    skin="#9c6644", hair=INK, wardrobe={"top": "#a9bfd3", "shoes": "#3a2a20"},
                    bodies=["pose/standing/shirt-3", "body/Button Shirt 2"], garments="light-blue collared shirt; dark trousers"),
    "wife": dict(head={"HEAD": "head/Medium Bangs", "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/* None"},
                 skin="#d7a27c", hair=INK, wardrobe={"top": "#93a582"},
                 bodies=["body/Coffee", "body/Button Shirt 2"], garments="sage collared shirt"),
}


def palette(ident):
    """the composer's palette for an identity: ink and paper fixed, skin and hair from the identity"""
    return {**PC.PAL, "skin": ident["skin"], "hair": ident["hair"], "cloth": ident.get("props", "#e4d9c6")}   # props (a mug) in warm ceramic


def group_span(txt, gid):
    i = txt.find('<g id="%s"' % gid)
    if i < 0: return None
    depth = 0
    for m in re.finditer(r"<g[ >]|</g>", txt[i:]):
        depth += 1 if m.group(0) != "</g>" else -1
        if depth == 0: return i, i + m.end()


def body_paths(svg):
    a, b = group_span(svg, "BODY")
    return a, b, list(re.finditer(r"<path [^>]*>", svg[a:b]))


def dress(svg, body, ident):
    """recolour the body's role fills from the identity's wardrobe (fills only; line work untouched)"""
    a, b, ps = body_paths(svg); roles = BODIES[body]; parts = []; last = 0; seg = svg[a:b]
    for k, m in enumerate(ps):
        role = roles.get(k)
        col = ident["skin"] if role == "skin" else ident["wardrobe"].get(role) if role not in (None, "keep") else None
        tag = m.group(0) if not col else re.sub(r'fill="#[0-9a-fA-F]{6}"', 'fill="%s"' % col, m.group(0))
        parts.append(seg[last:m.start()] + tag); last = m.end()
    return svg[:a] + "".join(parts) + seg[last:] + svg[b:]


def compose(C, cid, body, face="Calm"):
    ident = CAST[cid]
    if body not in ident["bodies"]: raise ValueError(f"{cid} may not wear {body} (allowed: {ident['bodies']})")
    svg = C.svg(KIND[body], {**ident["head"], "BODY": body, "FACE": "face/" + face}, palette(ident))
    return dress(svg, body, ident)


def check_variant(svg, cid, body):
    """continuity of one variant against its identity: head parts, skin, hair, every role's colour"""
    ident, errs = CAST[cid], []
    for slot, sym in ident["head"].items():
        if sym.endswith("* None"): continue
        if 'data-symbol="%s"' % sym not in svg: errs.append(f"{cid}/{body}: {slot} is not {sym}")
    a, b, ps = body_paths(svg)
    for k, role in BODIES[body].items():
        if role == "keep" or k >= len(ps): continue
        want = ident["skin"] if role == "skin" else ident["wardrobe"].get(role)
        got = re.search(r'fill="(#[0-9a-fA-F]{6})"', ps[k].group(0)).group(1).lower()
        if want and got != want.lower(): errs.append(f"{cid}/{body}: {role} is {got}, identity says {want}")
    h = group_span(svg, "HEAD")
    if h and ident["hair"].lower() not in svg[h[0]:h[1]].lower(): errs.append(f"{cid}/{body}: hair colour differs from {ident['hair']}")
    return errs


def validate(C):
    report = {}
    for cid, ident in CAST.items():
        for body in ident["bodies"]:
            report[f"{cid}:{body}"] = check_variant(compose(C, cid, body), cid, body)
    return report


if __name__ == "__main__":
    fig, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    C = PC.Composer(fig); rep = validate(C)
    for cid, ident in CAST.items():
        for body in ident["bodies"]:
            open(os.path.join(out, "%s__%s.svg" % (cid, body.split("/")[-1].replace(" ", "_"))), "w").write(compose(C, cid, body))
    json.dump(rep, open(os.path.join(out, "continuity.json"), "w"), indent=1)
    json.dump({"ink": INK, "variants": [{"file": "%s__%s.svg" % (cid, b.split("/")[-1].replace(" ", "_")), "character": cid,
                                         "skin": CAST[cid]["skin"], "top": CAST[cid]["wardrobe"].get("outer", CAST[cid]["wardrobe"].get("top"))}
                                        for cid in CAST for b in CAST[cid]["bodies"]]},
              open(os.path.join(out, "continuity_spec.json"), "w"), indent=1)   # for the rendered check (continuity.mjs)
    bad = {k: v for k, v in rep.items() if v}
    print(json.dumps({"variants": len(rep), "mismatches": bad}))
    sys.exit(1 if bad else 0)
