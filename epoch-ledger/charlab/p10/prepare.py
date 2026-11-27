"""P10: prepare the narrated 2.5D test: cast SVGs (faces as switchable layers, formal wardrobe), rig specs, and three shot
specs keyed to the narration's word timings (no lip sync: narration is voice-over).

    python3 epoch-ledger/charlab/p10/prepare.py FIG PLATES_DIR EPISODE_DIR OUT_DIR

PLATES_DIR holds cam{A,B,C}_paint.png (painterly plate), track{A,B,C}/ (depth_00000.png, track.json) from the static
plate demos. EPISODE_DIR/artifacts/words.json gives the word times. Writes OUT_DIR/shot{A,B,C}.json for compose.mjs,
OUT_DIR/rig_client.json (the elbow disc in the client's sleeve colour) and EPISODE_DIR/artifacts/timeline.json.
Deterministic (seeded blinks).
"""
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "p8"))
import peeps_compose as PC  # noqa: E402

DURATION = 16.5
CUTS = [0.0, 5.7, 11.75, DURATION]           # shot A (two-shot) | B (banker close) | C (client close)


def group_span(txt, gid):
    i = txt.find('<g id="%s"' % gid)
    depth = 0
    for m in re.finditer(r"<g[ >]|</g>", txt[i:]):
        depth += 1 if m.group(0) != "</g>" else -1
        if depth == 0: return i, i + m.end()


def character(C, kind, parts, palette, faces, pad=600.0):
    """SVG with FACE replaced by one group per expression (data-face=name; only the first visible)"""
    svg = C.svg(kind, {**parts, "FACE": "face/" + faces[0]}, palette, pad=pad)
    a, b = group_span(svg, "FACE"); stack = []
    for k, f in enumerate(faces):
        s = C.svg(kind, {**parts, "FACE": "face/" + f}, palette, pad=pad); fa, fb = group_span(s, "FACE")
        stack.append(s[fa:fb].replace('<g id="FACE"', '<g data-face="%s" style="display:%s"' % (f, "inline" if k == 0 else "none"), 1))
    return svg[:a] + '<g id="FACE">' + "".join(stack) + "</g>" + svg[b:]


def recolour(svg, body_fills):
    """formal wardrobe: recolour the artist's own BODY fill shapes by index (see wardrobe2.mjs --probe); lines untouched"""
    a, b = group_span(svg, "BODY"); body = svg[a:b]; k = [-1]
    def sub(m):
        k[0] += 1
        return m.group(0) if k[0] not in body_fills else re.sub(r'fill="#[0-9a-fA-F]{6}"', 'fill="%s"' % body_fills[k[0]], m.group(0))
    return svg[:a] + re.sub(r"<path [^>]*>", sub, body) + svg[b:]


def blinks(seed, t0, t1):
    rnd = random.Random(seed); t = t0 + rnd.uniform(0.6, 1.8); out = []
    while t < t1 - 0.3:
        d = rnd.choice((0.10, 0.12, 0.13)); out.append([round(t, 3), round(t + d, 3)])
        if rnd.random() < 0.18: out.append([round(t + d + 0.18, 3), round(t + d + 0.18 + 0.1, 3)])
        t += rnd.uniform(2.2, 5.5)
    return out


def main(fig, plates, ep, out):
    os.makedirs(out, exist_ok=True)
    W = json.load(open(os.path.join(ep, "artifacts/words.json")))
    W = W if isinstance(W, list) else W["words"]
    def at(word, after=0.0):
        """time of the first word starting with `word` at or after `after` (the performance is keyed to the narration)"""
        for w in W:
            if w["start"] >= after - 1e-6 and re.sub(r"[^a-z0-9]", "", w["word"].lower()).startswith(word): return w["start"]
        raise KeyError(word)
    tl = json.load(open(os.path.join(ep, "artifacts/narration_timing.json"))); tl["words"] = W
    json.dump(tl, open(os.path.join(ep, "artifacts/timeline.json"), "w"), indent=1)

    C = PC.Composer(fig); B, CL = PC.CAST["banker"], PC.CAST["client"]
    # banker: formal: the artist's blazer pose with a light blouse (blazer-4), dark leather shoes (fill 1)
    banker = recolour(character(C, "standing", {**B["parts"], "BODY": "pose/standing/blazer-4"}, B["palette"],
                                ["Calm", "Serious", "Smile", "Solemn", "Eyes Closed"]), {1: "#2a1a12"})
    client = character(C, "standing", CL["parts"], CL["palette"], ["Serious", "Driven", "Calm", "Smile", "Eyes Closed"])
    rig = json.load(open(os.path.join(HERE, "rigs/pointing_finger-1.json")))
    rig["pieces"][0]["disc"]["fill"] = CL["palette"]["cloth"]          # the joint disc in the client's own sleeve colour
    json.dump(rig, open(os.path.join(out, "rig_client.json"), "w"))

    loan, tenk = at("loan"), at("10000")
    rec, cred, new = at("records"), at("credits"), at("new")
    def shot(k, t0, t1, cam2d, farFrom, chars):
        tr = json.load(open(os.path.join(plates, "track%s/track.json" % k)))["frames"][0]["pts"]
        loc = lambda K: [[round(t - t0, 3)] + list(v) for t, *v in K]     # shot-local times
        for c in chars.values():
            for key in ("faces",): c[key] = [[round(t - t0, 3), f] for t, f in c[key]]
            for key in ("nods",): c[key] = [[round(t - t0, 3), d] for t, d in c.get(key, [])]
            for key in ("tilts",): c[key] = [[round(a - t0, 3), round(b - t0, 3), g] for a, b, g in c.get(key, [])]
            for key in ("shifts",): c[key] = [[round(a - t0, 3), d, g] for a, d, g in c.get(key, [])]
            c["blinks"] = [[round(a - t0, 3), round(b - t0, 3)] for a, b in c["blinks"] if t0 <= a < t1]
            if c.get("joints"): c["joints"] = {j: [[round(t - t0, 3), v] for t, v in K] for j, K in c["joints"].items()}
        s = dict(id=k, duration=round(t1 - t0, 3), plate=os.path.abspath(os.path.join(plates, "cam%s_paint.png" % k)),
                 depth=os.path.abspath(os.path.join(plates, "track%s/depth_00000.png" % k)), pts=tr, window="window",
                 cam2d=cam2d, farFrom=farFrom, farFactor=0.45, grade=dict(vignette=0.4, grain=4), chars=chars)
        json.dump(s, open(os.path.join(out, "shot%s.json" % k), "w"))

    bl_b, bl_c = blinks(11, 0, DURATION), blinks(23, 0, DURATION)
    # A: medium two-shot. The baker explains with a real elbow gesture on "loan" and "ten thousand dollars"; the banker
    # listens, nods, and answers with a small smile on "No vault is opened".
    tA0, tA1 = CUTS[0], CUTS[1]
    shot("A", tA0, tA1, [[0, 1.0, 960, 540], [tA1 - tA0, 1.03, 960, 520]], 4.4, {
        "banker": dict(svg=banker, feet="banker_feet", head="banker_head", facing="left", blinks=bl_b,
                       faces=[[0, "Calm"], [tenk + 0.5, "Serious"], [at("opened") - 0.2, "Smile"]],
                       nods=[[tenk + 0.35, 0.55], [at("opened"), 0.5]], tilts=[[0.4, 3.6, -3.5]], shifts=[[3.9, 1.1, 0.5]]),
        "client": dict(svg=client, rig=os.path.abspath(os.path.join(out, "rig_client.json")), feet="client_feet", head="client_head",
                       facing="right", blinks=bl_c, faces=[[0, "Serious"], [loan - 0.4, "Driven"], [at("vault"), "Calm"]],
                       nods=[[loan + 0.05, 0.45]], tilts=[[0.3, 2.4, 3.0]], shifts=[[2.9, 1.0, -0.5]],
                       joints={"fore": [[0, 0], [loan - 0.45, 0], [loan - 0.05, -13], [loan + 0.35, -6], [tenk - 0.2, -7], [tenk + 0.15, -16],
                                        [tenk + 0.7, -9], [tenk + 1.4, -4], [tA1, -3]]}),
    })
    # B: banker close-up: she records the loan (a deliberate nod on "records"), credits the account (a smile)
    tB0, tB1 = CUTS[1], CUTS[2]
    shot("B", tB0, tB1, [[0, 1.0, 960, 540], [tB1 - tB0, 1.02, 1000, 540]], 3.4, {
        "banker": dict(svg=banker, feet="banker_feet", head="banker_head", facing="left", blinks=bl_b,
                       faces=[[tB0, "Smile"], [tB0 + 0.8, "Calm"], [rec - 0.3, "Serious"], [cred + 0.1, "Smile"]],
                       nods=[[rec + 0.05, 0.6], [cred + 0.2, 0.5]], tilts=[[tB0 + 0.2, rec - 0.2, -3.0], [cred, tB1 + 1, 2.5]],
                       shifts=[[tB0 + 1.5, 1.2, 0.4]]),
    })
    # C: client close-up: the new money exists; he smiles and nods
    tC0, tC1 = CUTS[2], CUTS[3]
    shot("C", tC0, tC1, [[0, 1.0, 960, 540], [tC1 - tC0, 1.025, 930, 540]], 3.4, {
        "client": dict(svg=client, feet="client_feet", head="client_head", facing="right", blinks=bl_c,
                       faces=[[tC0, "Calm"], [new - 0.2, "Smile"]], nods=[[new + 0.75, 0.55]], tilts=[[tC0 + 0.3, tC1 + 1, 3.0]],
                       shifts=[[tC0 + 2.0, 1.2, -0.4]]),
    })
    print(json.dumps({"cuts": CUTS, "keys": dict(loan=loan, tenk=tenk, records=rec, credits=cred, new=new)}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
