"""P13 storyboard sheets: (1) the six key frames with their narration and what each shows; (2) P12 as delivered
against the P13 storyboard at the same narration times (the same words, two directions).

    python3 epoch-ledger/charlab/p13/sheets.py BOARD_DIR P12_VIDEO OUT_DIR
"""
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from board import FRAMES  # noqa: E402

T = json.loads((HERE / "treatment.json").read_text())
CAP = {"KF1": ("q1", "a family signs a mortgage they can barely afford"), "KF2": ("q3", "bundled with thousands of others"),
       "KF3": ("q3", "into a single security"), "KF4": ("q4", "investors around the world buy it"),
       "KF5": ("q7", "the payments dry up, the securities collapse"), "KF6": ("q8", "Lehman Brothers goes bankrupt")}
F = lambda s, b=True: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)


def main(board, p12, out):
    board, out = Path(board), Path(out); W, H = 860, 484
    seq = {s["id"]: s for s in T["sequences"]}
    # 1 storyboard sheet
    sheet = Image.new("RGB", (2 * W + 60, 3 * (H + 150) + 110), "#efe6d4"); d = ImageDraw.Draw(sheet)
    d.text((24, 24), "P13 storyboard: the mortgage passage (P12 narration), key frames for approval", fill="#2b2118", font=F(30))
    for i, (k, t, _) in enumerate(FRAMES):
        x, y = 20 + (i % 2) * (W + 20), 90 + (i // 2) * (H + 150)
        sheet.paste(Image.open(board / f"{k}.png").convert("RGB").resize((W, H)), (x, y))
        q, words = CAP[k]; c = next((c for c in seq[q]["concepts"] if c["verdict"] == "chosen"), {})
        d.text((x, y + H + 10), f"{k} · {t:.1f} s · {q}{' (hero)' if seq[q]['hero'] else ''} · “{words}”", fill="#2b2118", font=F(20))
        for j, line in enumerate(textwrap.wrap(c.get("name", "") + ": " + c.get("idea", ""), 88)[:4]):
            d.text((x, y + H + 40 + j * 24), line, fill="#4b3f33", font=F(17, False))
    sheet.save(out / "storyboard_sheet.jpg", quality=88)
    # 2 P12 against P13 at the same times
    cmp_ = Image.new("RGB", (2 * 640 + 60, len(FRAMES) * (360 + 44) + 90), "#efe6d4"); d = ImageDraw.Draw(cmp_)
    d.text((24, 20), "Same narration, same times:  P12 as delivered (left)  ·  P13 storyboard (right)", fill="#2b2118", font=F(26))
    with tempfile.TemporaryDirectory() as tmp:
        for i, (k, t, _) in enumerate(FRAMES):
            f = Path(tmp) / f"{k}.png"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", p12, "-frames:v", "1", str(f)], check=True)
            y = 70 + i * (360 + 44)
            cmp_.paste(Image.open(f).convert("RGB").resize((640, 360)), (20, y)); cmp_.paste(Image.open(board / f"{k}.png").convert("RGB").resize((640, 360)), (680, y))
            d.text((20, y + 364), f"{t:.1f} s  “{CAP[k][1]}”", fill="#2b2118", font=F(18))
    cmp_.save(out / "compare_p12_vs_p13.jpg", quality=86)
    print(json.dumps({"sheets": ["storyboard_sheet.jpg", "compare_p12_vs_p13.jpg"]}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
