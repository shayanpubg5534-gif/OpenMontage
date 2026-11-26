"""P3 character-look comparison sheet (PIL): one row per render folder (studio views from render_views.py or
studio_shots.mjs); columns are neutral full-body views, a medium (waist-up) crop, close-ups and an eye-detail crop, all
from the same cameras so rows compare like for like.

    python3 epoch-ledger/charlab/convert/p3_sheet.py OUT.png TITLE "label|dir|note;note" ...
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
out, title, rows = sys.argv[1], sys.argv[2], [r.split("|") for r in sys.argv[3:]]
H = 380
# (label, source view, crop box as fractions of the source (l, t, r, b), cell width)
cols = [("neutral · front", "body_front", (0, 0, 1, 1), 236), ("neutral · ¾", "body_34", (0, 0, 1, 1), 236),
        ("medium · ¾", "body_34", (.06, .06, .94, .52), 330), ("close · front", "head_front", (0, 0, 1, 1), 380),
        ("close · ¾", "head_34", (0, 0, 1, 1), 380), ("close · profile", "head_profile", (0, 0, 1, 1), 380),
        ("eye detail", "head_front", (.24, .44, .76, .62), 520)]
W = 300 + sum(c[3] for c in cols) + 10 * len(cols)
img = Image.new("RGB", (W, 96 + len(rows) * (H + 16)), "#15171c")
d = ImageDraw.Draw(img)
d.text((24, 22), title, font=ImageFont.truetype(F, 32), fill="#f2c66d")
x = 300
for label, *_r, w in cols:
    d.text((x + 6, 68), label, font=ImageFont.truetype(FR, 17), fill="#9aa3b2"); x += w + 10
for i, r in enumerate(rows):
    label, folder, note = (r + ["", ""])[:3]
    y = 96 + i * (H + 16)
    d.text((24, y + 10), label, font=ImageFont.truetype(F, 24), fill="#ffffff")
    for k, line in enumerate(note.split(";")):
        d.text((24, y + 50 + k * 23), line.strip(), font=ImageFont.truetype(FR, 16), fill="#c9cfd9")
    x = 300
    for label_c, view, (l, t, rr, b), w in cols:
        p = Path(folder) / f"{view}.png"
        if p.exists():
            im = Image.open(p).convert("RGB"); im = im.crop((int(l * im.width), int(t * im.height), int(rr * im.width), int(b * im.height)))
            s = max(w / im.width, H / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            ox, oy = (im.width - w) // 2, (im.height - H) // 2
            img.paste(im.crop((ox, oy, ox + w, oy + H)), (x, y))
        else:
            d.rectangle((x, y, x + w, y + H), outline="#333"); d.text((x + 12, y + H // 2), "n/a", font=ImageFont.truetype(FR, 18), fill="#666")
        x += w + 10
img.save(out)
print("sheet", out, img.size)
