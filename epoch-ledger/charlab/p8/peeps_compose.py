"""P8: compose Open Peeps characters (CC0, Pablo Stanley) from the artist's own parts and restyle the palette.

    python3 epoch-ledger/charlab/p8/peeps_compose.py FILE.fig OUTDIR      # writes the P8 cast + variant SVGs

A character = the "a person/standing" (or sitting / bust) component with its slots swapped to chosen parts: BODY (pose),
HEAD (hair), FACE (expression), FACIAL HAIR, ACCESORIES (glasses). The vector paths are the artist's; we only choose
parts and remap flat colours to a muted documentary palette (ink, paper, skin, clothing). Groups keep their slot names
(`BODY`, `Head`, `HEAD`, `FACE`, …), so a runtime can move the head, swap faces (blink = "Eyes Closed") and swap
poses for gestures.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import peeps_extract as PX  # noqa: E402

K = PX.K
SLOTS = {"standing": {"BODY": (0, 826), "HEAD": (0, 828), "FACIAL HAIR": (0, 829), "FACE": (0, 830), "ACCESORIES": (0, 832)},
         "sitting": {"BODY": (0, 818), "HEAD": (0, 820), "FACE": (0, 821), "FACIAL HAIR": (0, 822), "ACCESORIES": (0, 824)},
         "bust": {"BODY": (0, 811), "HEAD": (0, 812), "FACE": (0, 813), "FACIAL HAIR": (0, 814), "ACCESORIES": (0, 816)}}
BASE = {"standing": (0, 825), "sitting": (0, 817), "bust": (0, 810)}

# source flat colours (from the file) → roles
INK = ("#000000", "#231f20", "#221e1f", "#22252b")
PAPER = ("#ffffff", "#f2f2f2", "#f1f1f1", "#fcf9f9", "#e5e5e5", "#d8d8d8", "#e8e1e1")
SKIN = ("#d08b5b",)
CLOTH = ("#9ddadb", "#8fa7df", "#78e185", "#ffcf77", "#9fd8e5", "#d4c44a", "#fdea6b", "#e86bbb", "#c93305", "#ec7495",
         "#4f66af", "#ecdcbf", "#e78276", "#b796e2", "#c5a9e9", "#b996e3")


class Composer:
    def __init__(s, fig):
        s.D = PX.Doc(fig)
        s.sym = {n["name"]: K(n["guid"]) for n in s.D.N if n.get("type") == "SYMBOL"}

    def svg(s, kind, parts, palette, pad=160.0):
        """parts: {slot: symbol name}; palette: {'ink','paper','skin', cloth source hex → hex, 'cloth': default}"""
        ov = []
        for slot, name in parts.items():
            sid = s.sym[name]
            ov.append({"guidPath": {"guids": [{"sessionID": SLOTS[kind][slot][0], "localID": SLOTS[kind][slot][1]}]},
                       "overriddenSymbolID": {"sessionID": sid[0], "localID": sid[1]}})
        base = s.D.ids[BASE[kind]]
        node = {"guid": {"sessionID": 99, "localID": 1}, "type": "INSTANCE", "name": "character", "size": base["size"],
                "transform": {"m00": 1, "m01": 0, "m02": 0, "m10": 0, "m11": 1, "m12": 0},
                "symbolData": {"symbolID": base["guid"], "symbolOverrides": ov}}
        body = s.D.render(node)
        def sub(m):
            c = m.group(1).lower()
            if c in INK: return 'fill="%s"' % palette["ink"]
            if c in PAPER: return 'fill="%s"' % palette.get(c, palette["paper"])
            if c in SKIN: return 'fill="%s"' % palette["skin"]
            return 'fill="%s"' % palette.get(c, palette.get("cloth", c))
        def group_span(txt, gid):                       # [start, end) of <g id="gid" ...>…</g> (nested groups counted)
            i = txt.find('<g id="%s"' % gid)
            if i < 0: return None
            depth, j = 0, i
            for m in re.finditer(r"<g[ >]|</g>", txt[i:]):
                depth += 1 if m.group(0) != "</g>" else -1
                if depth == 0: return i, i + m.end()
            return None
        sp = group_span(body, "HEAD")
        if sp and "hair" in palette:                    # hair: every non-ink, non-skin colour inside the HEAD group
            hd = re.sub(r'fill="(#[0-9a-fA-F]{6})"', lambda m: m.group(0) if m.group(1).lower() in INK + SKIN else 'fill="@HAIR"', body[sp[0]:sp[1]])
            body = body[:sp[0]] + hd + body[sp[1]:]
        body = re.sub(r'fill="(#[0-9a-fA-F]{6})"', sub, body).replace('fill="@HAIR"', 'fill="%s"' % palette.get("hair", palette["ink"]))
        w, h = base["size"]["x"], base["size"]["y"]
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f">%s</svg>'
                % (-pad, -pad, w + 2 * pad, h + 2 * pad, body))


# a muted documentary palette (no candy colours): ink, warm paper, natural skin tones, tailored clothing colours
PAL = {"ink": "#1e1b19", "paper": "#efe8dc"}
CAST = {
    "banker": dict(kind="standing", parts={"BODY": "pose/standing/blazer-3", "HEAD": "head/Gray Medium", "FACE": "face/Calm",
                                          "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/Glasses 2"},
                   palette={**PAL, "hair": "#b9b4ac", "skin": "#c8946d", "cloth": "#2f3b52", "#9ddadb": "#d9cfbd", "#ffcf77": "#2f3b52", "#e86bbb": "#2f3b52"}),
    "client": dict(kind="standing", parts={"BODY": "pose/standing/pointing_finger-1", "HEAD": "head/Short 1", "FACE": "face/Serious",
                                          "FACIAL HAIR": "facial-hair/Full 3", "ACCESORIES": "accessories/* None"},
                   palette={**PAL, "hair": "#1e1b19", "skin": "#8a5a3c", "cloth": "#6b6a45", "#78e185": "#6b6a45", "#ffcf77": "#b08a5a"}),
    "lender": dict(kind="standing", parts={"BODY": "pose/standing/crossed_arms-1", "HEAD": "head/No Hair 2", "FACE": "face/Serious",
                                          "FACIAL HAIR": "facial-hair/Moustache 3", "ACCESORIES": "accessories/* None"},
                   palette={**PAL, "hair": "#6d5a48", "skin": "#d9a582", "cloth": "#5e2c2c"}),
    "clerk": dict(kind="standing", parts={"BODY": "pose/standing/shirt-3", "HEAD": "head/Long", "FACE": "face/Calm",
                                         "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/* None"},
                  palette={**PAL, "hair": "#2a201b", "skin": "#b37650", "cloth": "#3f5566"}),
    "investor": dict(kind="standing", parts={"BODY": "pose/standing/blazer-4", "HEAD": "head/Gray Short", "FACE": "face/Solemn",
                                            "FACIAL HAIR": "facial-hair/Full 2", "ACCESORIES": "accessories/Glasses 3"},
                     palette={**PAL, "hair": "#c9c3ba", "skin": "#e0b693", "cloth": "#3a3a3c"}),
    "founder": dict(kind="standing", parts={"BODY": "pose/standing/walking-1", "HEAD": "head/Hijab", "FACE": "face/Driven",
                                           "FACIAL HAIR": "facial-hair/* None", "ACCESORIES": "accessories/* None"},
                    palette={**PAL, "hair": "#5b4636", "skin": "#a8714f", "cloth": "#4a5b4a", "#8fa7df": "#7a6650"}),
}

if __name__ == "__main__":
    fig, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    C = Composer(fig)
    for k, c in CAST.items():
        open(os.path.join(out, k + ".svg"), "w").write(C.svg(c["kind"], c["parts"], c["palette"]))
    b = CAST["banker"]                                      # variants of one character: expressions and poses
    for f in ("Calm", "Eyes Closed", "Smile", "Concerned", "Serious", "Explaining"):
        open(os.path.join(out, "banker_face_%s.svg" % f.replace(" ", "_")), "w").write(C.svg("standing", {**b["parts"], "FACE": "face/" + f}, b["palette"]))
    for p in ("blazer-1", "blazer-2", "blazer-3", "pointing_finger-2", "crossed_arms-2", "walking-2"):
        open(os.path.join(out, "banker_pose_%s.svg" % p), "w").write(C.svg("standing", {**b["parts"], "BODY": "pose/standing/" + p}, b["palette"]))
    open(os.path.join(out, "banker_sitting.svg"), "w").write(C.svg("sitting", {**b["parts"], "BODY": "pose/sitting/mid-1"}, b["palette"]))
    json.dump({k: {"parts": c["parts"], "palette": c["palette"]} for k, c in CAST.items()}, open(os.path.join(out, "cast.json"), "w"), indent=1)
    print("cast written", out)
