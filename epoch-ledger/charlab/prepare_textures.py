#!/usr/bin/env python3
"""Character lab (M2.3b): build-time texture treatments for the look-development viewer (Pillow only).

    python3 epoch-ledger/charlab/prepare_textures.py TEX_DIR [--spec SPEC.json] [--size 1024]

TEX_DIR is the <id>_tex folder written by build_dressed.py (PNG per image + manifest.json). For every colour texture it
writes, next to the original:
  <name>.toon.png   photographic detail removed (pores, weave), colour regions kept — for the refined toon treatment
  <name>.flat.png   controlled flat colour: median-filtered, then quantised to a small k-means palette per material
                    family (skin 5, cloth 7, shoes 4) — for the flat editorial and hybrid treatments
Alpha textures (hair, brows, lashes) keep their alpha; hair is reduced to 3 tones so strand clumps read as shapes.
Spec "recolour" rules (optional) replace palette colours, e.g. the sports socks inside the shoe assets → dark tights.
Writes treatments.json (texture → treated files, palettes) and prints the time taken. Doing this at build time keeps
the browser from re-processing images on every page load (reusable assets).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from PIL import Image, ImageFilter

FAMILY = [("eyebrow", "brow"), ("eyelash", "lash"), ("_eye", "eye"), ("teeth", "mouth"), ("tongue", "mouth"),
          ("shoes", "shoes"), ("suit", "cloth"), ("dress", "cloth"), ("shirt", "cloth"), ("skinned", "skin"), ("skin", "skin"),
          ("bob", "hair"), ("short0", "hair"), ("long0", "hair"), ("ponytail", "hair"), ("braid", "hair"), ("afro", "hair")]
K = {"skin": 5, "cloth": 7, "shoes": 4, "hair": 3, "brow": 2, "lash": 2, "mouth": 3}


def family(name: str) -> str:
    n = name.lower()
    return next((f for k, f in FAMILY if k in n), "other")


def toon(im: Image.Image, fam: str, size: int) -> Image.Image:
    small = {"skin": 160, "cloth": 128, "shoes": 96}.get(fam, 256)
    rgb = im.convert("RGB").resize((small, small), Image.LANCZOS).resize((size, size), Image.BICUBIC)
    return rgb


def soft_flat_skin(im: Image.Image, size: int) -> tuple[Image.Image, list]:
    """Skin for the editorial treatments: one even tone with only the broad, soft variation kept (lips, cheek warmth,
    brow shadow) — no palette islands, which read as patchy make-up on a face."""
    rgb = im.convert("RGB")
    mean = rgb.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    soft = rgb.resize((48, 48), Image.LANCZOS).resize((size, size), Image.BICUBIC)
    out = Image.blend(soft, Image.new("RGB", (size, size), mean), .55)
    return out, [list(mean)]


def flat(im: Image.Image, fam: str, size: int, recolour: list) -> tuple[Image.Image, list]:
    if fam == "skin":
        return soft_flat_skin(im, size)
    k = K.get(fam, 6)
    rgb = im.convert("RGB").resize((512, 512), Image.LANCZOS).filter(ImageFilter.MedianFilter(7))
    q = rgb.quantize(colors=k, method=Image.Quantize.MEDIANCUT, kmeans=4, dither=Image.Dither.NONE)
    pal = q.getpalette()[: 3 * k]
    cols = [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]
    for rule in recolour:                                   # {"near": [r,g,b], "to": [r,g,b], "within": 90}
        for i, c in enumerate(cols):
            if sum(abs(a - b) for a, b in zip(c, rule["near"])) <= rule.get("within", 90):
                cols[i] = tuple(rule["to"])
    q.putpalette([v for c in cols for v in c] + [0] * (768 - 3 * len(cols)))
    out = q.convert("RGB").resize((size, size), Image.NEAREST).filter(ImageFilter.ModeFilter(5))
    return out, cols


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tex_dir", type=Path)
    ap.add_argument("--spec", type=Path)
    ap.add_argument("--size", type=int, default=1024)
    a = ap.parse_args(argv)
    t0 = time.time()
    spec = json.loads(a.spec.read_text()) if a.spec else {}
    rules = spec.get("recolour", {})
    result = {}
    for png in sorted(a.tex_dir.glob("*.png")):
        if png.name.count(".") > 1:
            continue                                         # already a treated file
        fam = family(png.stem)
        im = Image.open(png)
        entry = {"family": fam}
        has_alpha = im.mode in ("RGBA", "LA") and im.getextrema()[-1][0] < 250
        if fam in ("eye", "other") or "normal" in png.stem or "_ao" in png.stem:
            result[png.name] = entry
            continue
        tn, fn = png.with_suffix(".toon.png"), png.with_suffix(".flat.png")
        t_im, (f_im, cols) = toon(im, fam, a.size), flat(im, fam, a.size, [r for key, rs in rules.items() if key in png.stem for r in rs])
        if has_alpha:                                        # hair, brows, lashes: keep the alpha shapes
            alpha = im.getchannel("A").resize((a.size, a.size), Image.LANCZOS)
            t_im = t_im.convert("RGBA"); t_im.putalpha(alpha)
            f_im = f_im.convert("RGBA"); f_im.putalpha(alpha)
        t_im.save(tn)
        f_im.save(fn)
        entry.update(toon=tn.name, flat=fn.name, palette=[list(c) for c in cols], alpha=has_alpha)
        result[png.name] = entry
    (a.tex_dir / "treatments.json").write_text(json.dumps(result, indent=1))
    print(f"prepared {sum(1 for v in result.values() if 'flat' in v)} textures in {time.time() - t0:.1f}s → {a.tex_dir / 'treatments.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
