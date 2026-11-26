"""Comparison sheets for the artistic-direction gate (PIL). Each row is one character: full body front / three-quarter /
profile, head front / three-quarter / profile, and an expression close-up from the character's own pose library.

    python3 epoch-ledger/charlab/bstudio/make_sheet.py OUT.png TITLE "label|dir|note" ...
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
out, title, rows = sys.argv[1], sys.argv[2], [r.split("|") for r in sys.argv[3:]]
cell_b, cell_h, H = (230, 370), (370, 370), 370
cols = [("body_front", cell_b), ("body_34", cell_b), ("body_profile", cell_b), ("head_front", cell_h), ("head_34", cell_h),
        ("head_profile", cell_h), ("head_34_expr", cell_h)]
W = 300 + sum(c[1][0] for c in cols) + 10 * len(cols)
img = Image.new("RGB", (W, 90 + len(rows) * (H + 16)), "#15171c")
d = ImageDraw.Draw(img)
d.text((24, 22), title, font=ImageFont.truetype(F, 34), fill="#f2c66d")
x = 300
for name, (w, _) in cols:
    d.text((x + 6, 66), {"body_front": "full · front", "body_34": "full · ¾", "body_profile": "full · profile", "head_front": "close · front",
                         "head_34": "close · ¾", "head_profile": "close · profile", "head_34_expr": "expression (own library)"}[name],
           font=ImageFont.truetype(FR, 17), fill="#9aa3b2")
    x += w + 10
for i, r in enumerate(rows):
    label, folder, note = (r + ["", ""])[:3]
    y = 90 + i * (H + 16)
    d.text((24, y + 10), label, font=ImageFont.truetype(F, 26), fill="#ffffff")
    for k, line in enumerate(note.split(";")):
        d.text((24, y + 52 + k * 24), line.strip(), font=ImageFont.truetype(FR, 17), fill="#c9cfd9")
    x = 300
    for name, (w, h) in cols:
        p = Path(folder) / f"{name}.png"
        if p.exists():
            im = Image.open(p).convert("RGB")
            s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s), int(im.height * s)))
            l, t = (im.width - w) // 2, (im.height - h) // 2
            img.paste(im.crop((l, t, l + w, t + h)), (x, y))
        else:
            d.rectangle((x, y, x + w, y + h), outline="#333")
            d.text((x + 12, y + h // 2), "n/a", font=ImageFont.truetype(FR, 18), fill="#666")
        x += w + 10
img.save(out)
print("sheet", out, img.size)
