#!/usr/bin/env python3
"""Character lab (M2.3): assemble look-development stills into labelled evidence sheets (Pillow only).

    python3 epoch-ledger/charlab/evidence_sheets.py STILLS_DIR RIG4_DIR OUT_DIR
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(title, rows, tile=(640, 360), crop=None):
    """rows: list of lists of (label, image path or None)."""
    cols = max(len(r) for r in rows)
    W, H = cols * tile[0], 56 + len(rows) * (tile[1] + 30)
    img = Image.new("RGB", (W, H), "#101216")
    d = ImageDraw.Draw(img)
    d.text((14, 14), title, fill="#f2f2ee", font=font(24))
    for ri, row in enumerate(rows):
        for ci, (label, p) in enumerate(row):
            x, y = ci * tile[0], 56 + ri * (tile[1] + 30)
            if p and Path(p).exists():
                im = Image.open(p).convert("RGB")
                if crop:
                    w, h = im.size
                    l, t, r, b = crop
                    im = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
                im = im.resize(tile)
                img.paste(im, (x, y + 30))
            d.text((x + 8, y + 6), label, fill="#d9a520", font=font(17))
    return img


def main(st, rig4, out):
    st, rig4, out = Path(st), Path(rig4), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    S = lambda n: st / f"{n}.png"
    sheet("M2.3 · the same character, pose, light and camera in two treatments: refined toon (top) and painterly (bottom)",
          [[(f"toon · {k}", S(f"toon_{k}")) for k in ("wide", "medium", "close", "profile")],
           [(f"painterly · {k}", S(f"paint_{k}")) for k in ("wide", "medium", "close", "profile")]], tile=(480, 270)).save(out / "1_treatments.png")
    for m, nm in (("toon", "refined toon"), ("paint", "painterly")):
        sheet(f"M2.3 · turnaround, {nm}: front, three-quarter, side, back",
              [[(f"{y}°", S(f"{m}_turn_{y}")) for y in (0, 45, 90, 180)]], tile=(480, 540), crop=(.22, 0, .78, 1)).save(out / f"2_turnaround_{m}.png")
    sheet("M2.3 · expressions (shape keys on face, brows, lashes, teeth): toon (top) and painterly (bottom)",
          [[(f"toon · {k}", S(f"toon_expr_{k}")) for k in ("neutral", "concern", "smile", "surprise", "blink")],
           [(f"painterly · {k}", S(f"paint_expr_{k}")) for k in ("neutral", "concern", "smile", "surprise", "blink")]],
          tile=(384, 384), crop=(.28, 0, .72, .78)).save(out / "3_expressions.png")
    sheet("M2.3 · hands: relaxed right, relaxed left, generic grip on a folder (not yet a tuned grip: M3.2)",
          [[("relaxed · right", S("toon_hand_r")), ("relaxed · left", S("toon_hand_l")), ("grip + folder", S("toon_grip_r"))]],
          tile=(640, 360)).save(out / "4_hands.png")
    sheet("M2.3 · hair attachment: top and back of the head", [[("top", S("toon_hair_top")), ("back", S("toon_hair_back"))]],
          tile=(640, 360)).save(out / "5_hair.png")
    sheet("M2.3 · side by side in the same bank set: existing Rig v4 banker (Profitable and Broke, 30.4 s) vs. the new character",
          [[("Rig v4 (stored frame)", rig4 / "pb_30.4.png"), ("new · refined toon", S("bank_toon_medium")), ("new · painterly", S("bank_paint_medium"))],
           [("Rig v4 · BigCart (stored frame)", rig4 / "bc_9.8.png"), ("new · toon close-up", S("bank_toon_close")), ("new · painterly close-up", S("bank_paint_close"))]],
          tile=(640, 360)).save(out / "6_rig4_comparison.png")
    print("sheets →", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
