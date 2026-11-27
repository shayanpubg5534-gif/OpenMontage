"""P8 sheets (PIL): 2.5D (Open Peeps) inspection, 3D (Fab businessman) inspection, and the side-by-side comparison.

    python3 epoch-ledger/charlab/p8/make_sheets.py RUNTIME_DIR OUT_DIR
RUNTIME_DIR = .runtime/charlab/p8 (renders of the cast and of the 3D poses); OUT_DIR = projects/charlab_p8.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

R, O = Path(sys.argv[1]), Path(sys.argv[2])
F, FR = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
font = lambda s, b=False: ImageFont.truetype(F if b else FR, s)
GOLD, TXT, DIM, BG = "#f2c66d", "#e8e8ea", "#9a9ca3", "#15171c"


def fit(im, h):
    im = im.convert("RGB"); return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def trim(im, bg=(217, 210, 197), pad=20):
    """crop a cast render to the artwork (its background is the sheet colour)."""
    px = im.convert("RGB").load(); w, h = im.size; xs, ys = [], []
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            if sum(abs(a - b) for a, b in zip(px[x, y], bg)) > 30: xs.append(x); ys.append(y)
    return im.crop((max(0, min(xs) - pad), max(0, min(ys) - pad), min(w, max(xs) + pad), min(h, max(ys) + pad)))


def row(img, d, y, label, ims, x0=30, gap=12, sub=None):
    d.text((x0, y), label, font=font(24, True), fill=GOLD); y += 36
    x = x0
    for k, im in enumerate(ims):
        img.paste(im, (x, y))
        if sub: d.text((x + 6, y + im.height + 4), sub[k], font=font(17), fill=DIM)
        x += im.width + gap
    return y + ims[0].height + (30 if sub else 10)


def head(im, frac=0.30):
    t = trim(im); return t.crop((0, 0, t.width, int(t.height * frac)))


def peeps_sheet():
    P = R / "png"; W = 2600
    img = Image.new("RGB", (W, 2350), BG); d = ImageDraw.Draw(img)
    d.text((30, 20), "P8 · 2.5D direction — Open Peeps (Pablo Stanley, CC0): the artist's own vector parts, recombined and restyled", font=font(34, True), fill=GOLD)
    d.text((30, 66), "Decoded from the supplied Figma source (multicolour). Parts swapped by code (pose, hair, face, facial hair, glasses); flat colours remapped to a muted palette; nothing redrawn.", font=font(20), fill=TXT)
    y = 110
    cast = ["banker", "client", "lender", "clerk", "investor", "founder"]
    y = row(img, d, y, "Cast of six adults (one consistent style; ages, ethnicities, builds)", [fit(trim(Image.open(P / f"{c}.png")), 640) for c in cast], sub=cast)
    faces = ["Calm", "Eyes_Closed", "Smile", "Concerned", "Serious", "Explaining"]
    y = row(img, d, y, "Expressions = face-part swaps (blink = 'Eyes Closed'); head is a separate group (tilt and nod)",
            [fit(head(Image.open(P / f"banker_face_{f}.png"), 0.27), 300) for f in faces], sub=[f.replace("_", " ") for f in faces])
    poses = ["blazer-1", "blazer-2", "blazer-3", "pointing_finger-2", "crossed_arms-2", "walking-2"]
    ims = [fit(trim(Image.open(P / f"banker_pose_{p}.png")), 520) for p in poses] + [fit(trim(Image.open(P / "banker_sitting.png")), 400)]
    y = row(img, d, y, "Gestures and posture = whole-body pose swaps (arms are drawn into each pose; no skeletal arms)", ims, sub=poses + ["sitting/mid-1"])
    lay = ["body", "hair", "face", "glasses"]
    y = row(img, d, y, "Layer separation (rig-ready groups): BODY · HEAD · FACE · ACCESSORIES", [fit(trim(Image.open(P / f"layer_{l}.png")), 360) for l in lay], sub=["BODY (pose)", "HEAD (hair)", "FACE", "ACCESSORIES"])
    d.text((30, y + 10), "Limits seen: contemporary casual wardrobe only (no suits, ties or period dress); trousers are solid ink; sneakers by default; poses are fixed drawings (blending between them needs new art or cut-out arms).",
           font=font(19), fill=DIM)
    img.crop((0, 0, W, y + 60)).save(O / "sheet_25d_peeps.png")


def bm_sheet():
    V = O / "views_3d"; B = R / "bm"; W = 2600
    img = Image.new("RGB", (W, 2100), BG); d = ImageDraw.Draw(img)
    m = json.load(open(B / "stand.json"))
    d.text((30, 20), "P8 · 3D direction — free Fab 'Businessman' (Daydreams Creative Studios, Fab Standard License)", font=font(34, True), fill=GOLD)
    d.text((30, 66), f"Built with MPFB/MakeHuman (MakeHuman CC0 body, skin, suit, hair and shoe assets) + Rigify (1,090 bones, 209 deforming, 101 in the face). No shape keys, no animation. "
           f"Measured: {m['heads_tall']} heads, shoulders {m['shoulder_width_hh']} hh.", font=font(20), fill=TXT)
    y = 110
    y = row(img, d, y, "Native materials, Cycles, P6 studio (same lights and cameras as P6)", [fit(Image.open(V / f"{k}.png"), 560) for k in ("full_front", "full_side", "face_front", "face_34", "face_side")],
            sub=["full front", "full side", "face front", "face 3/4", "face profile"])
    ims = [fit(Image.open(B / "v_point/full_front.png"), 520), fit(Image.open(B / "v_walk/full_side.png"), 520), fit(Image.open(B / "v_sit/full_side.png"), 520)]
    hand = Image.open(V / "full_front.png"); hw, hh = hand.size; ims.append(fit(hand.crop((int(hw * 0.52), int(hh * 0.44), int(hw * 0.86), int(hh * 0.64))), 520))
    y = row(img, d, y, "Body: posed with the asset's own Rigify controls (FK arms/legs)", ims, sub=["pointing", "walking (contact)", "sitting (no chair)", "hand / wrist deformation"])
    ims = [fit(Image.open(V / "face_front.png"), 420)] + [fit(Image.open(B / f"v_face_{f}/face_front.png"), 420) for f in ("blink", "smile", "open")]
    y = row(img, d, y, "Face: bone-driven only (Rigify face controls); no blendshapes", ims, sub=["neutral", "blink (lid bones)", "smile (lip corners)", "jaw open"])
    d.text((30, y + 10), "Limits seen: realistic 'MakeHuman' face and hair-card helmet (the look rejected in M5); sit pose needs a chair; expressions are possible through bones but untuned; no animation tracks included.",
           font=font(19), fill=DIM)
    img.crop((0, 0, W, y + 60)).save(O / "sheet_3d_businessman.png")


def compare():
    a, b = Image.open(O / "bank_25d.png"), Image.open(O / "bank_3d.png")
    W = 30 + 1200 * 2 + 30 + 30; img = Image.new("RGB", (W, 1010), BG); d = ImageDraw.Draw(img)
    d.text((30, 20), "P8 · same bank set (P4 cinematic look), same camera — 2.5D vs 3D", font=font(34, True), fill=GOLD)
    img.paste(fit(a, 675), (30, 80)); img.paste(fit(b, 675), (30 + 1200 + 30, 80))
    d.text((30, 765), "2.5D: Open Peeps vector characters composited on the rendered plate (shadows, rim, shading, grain, haze, foreground)", font=font(19, True), fill=TXT)
    d.text((1260, 765), "3D: Fab businessman, posed with its own rig, static GLB in the three.js set", font=font(19, True), fill=TXT)
    lines = [("Characters available now", "6+ adults from one free library (hundreds of combinations)", "1 man"),
             ("Look", "consistent illustrated; reads as editorial animation", "realistic game-NPC face; hair cards; inconsistent with set's look"),
             ("Animation (stills only so far)", "head/face swaps, blink, pose swaps; no limb bending", "full skeleton; bone face (blink, jaw); retarget mocap"),
             ("Frame cost (this CPU)", "plate once per shot + 2D layers (estimate, not yet measured)", "full 3D frame every frame (P5 measured: 1.19 s/frame)")]
    y = 805
    for k, l, r in lines:
        d.text((30, y), k + ":", font=font(18, True), fill=DIM); d.text((330, y), l, font=font(18), fill=TXT); d.text((1260, y), r, font=font(18), fill=TXT); y += 34
    img.save(O / "sheet_comparison.png")


peeps_sheet(); bm_sheet(); compare(); print("sheets written")
