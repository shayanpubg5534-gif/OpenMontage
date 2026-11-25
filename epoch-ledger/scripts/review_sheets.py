#!/usr/bin/env python3
"""Epoch Ledger visual review: contact sheets of consecutive frames around every interaction, a 1-in-N frame
sample, and one HTML review page with the human checklist. Reads an already rendered MP4: it never renders.

    python epoch-ledger/scripts/review_sheets.py VIDEO --manifest interactions.json --out DIR
        [--before 5] [--after 10] [--every 30] [--gates gates.json]

interactions.json:
    {"interactions": [{"id": "folder-handoff", "t": 30.0, "label": "Okafor slides the folder; Maya grips it",
                       "box": [700, 380, 640, 360]}],          # optional crop (1920×1080 px) shown enlarged
     "cuts": [7.0, 15.85]}                                       # optional: each cut gets a sheet too (continuity)

Automated gates find objective defects; this page is for what they cannot judge: visible grips and finger contact,
object orientation, natural posture, intersections, foot sliding and continuity across consecutive frames.
Original implementation (ffmpeg + Pillow).
"""
from __future__ import annotations

import argparse
import html
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CHECKLIST = [
    "Hands stay attached and visible through every contact; fingers visibly close on what they hold",
    "Held objects keep a plausible orientation and never float, drift or pass through a hand or body",
    "Elbows, shoulders, spine and knees bend naturally; no mechanical joints or broken limbs",
    "No mesh or shape intersections (hands through props, legs through furniture)",
    "Feet do not slide while planted; weight shifts are believable",
    "Identity, clothing and proportions are consistent across cuts",
    "Every number and label is complete, legible and on screen when the narration says it",
    "Charts are proportional and start from a shared baseline; a shortfall is not drawn as a negative balance",
    "No overlapping text, no unintended cropping, captions clear of key content",
    "No abrupt jumps, freezes or flashes; every action supports the narration",
]


def probe(video: Path) -> tuple[float, int, int, int]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate,nb_frames,width,height", "-of", "json", str(video)],
                         check=True, capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = (int(x) for x in s["r_frame_rate"].split("/"))
    return num / den, int(s.get("nb_frames") or 0), int(s["width"]), int(s["height"])


def grab(video: Path, frames: list[int], fps: float, tmp: Path) -> dict[int, Path]:
    """Decode exactly the requested frame numbers (one pass per contiguous run)."""
    got: dict[int, Path] = {}
    runs, cur = [], []
    for f in sorted(set(frames)):
        if cur and f != cur[-1] + 1:
            runs.append(cur)
            cur = []
        cur.append(f)
    if cur:
        runs.append(cur)
    for run in runs:
        a, b = run[0], run[-1]
        pat = tmp / f"r{a}_%05d.png"
        ss = max(0.0, a / fps - 1.0)                 # seek a little before, then select by frame number
        first = round(ss * fps)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.4f}", "-i", str(video), "-vf",
                        f"select='between(n\\,{a - first}\\,{b - first})'", "-vsync", "0", str(pat)], check=True)
        for i, f in enumerate(run):
            p = tmp / f"r{a}_{i + 1:05d}.png"
            if p.exists():
                got[f] = p
    return got


def font(size: int):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(paths: list[tuple[int, Path]], fps: float, cols: int, tile_w: int, mark: int | None, box=None, title="") -> Image.Image:
    tile_h = round(tile_w * 9 / 16)
    rows = (len(paths) + cols - 1) // cols
    head = 44 if title else 0
    img = Image.new("RGB", (cols * tile_w, head + rows * (tile_h + 24)), "#15171c")
    d = ImageDraw.Draw(img)
    if title:
        d.text((10, 10), title, fill="#f2f2ee", font=font(22))
    for i, (f, p) in enumerate(paths):
        im = Image.open(p).convert("RGB")
        if box:
            x, y, w, h = box
            sx = im.width / 1920
            im = im.crop((round(x * sx), round(y * sx), round((x + w) * sx), round((y + h) * sx)))
        im = im.resize((tile_w, tile_h))
        x0, y0 = (i % cols) * tile_w, head + (i // cols) * (tile_h + 24)
        img.paste(im, (x0, y0 + 24))
        hot = f == mark
        d.rectangle([x0, y0, x0 + tile_w - 1, y0 + 23], fill="#d9a520" if hot else "#2a2e36")
        d.text((x0 + 6, y0 + 3), f"#{f}  {f / fps:.3f}s", fill="#15171c" if hot else "#e8e8e8", font=font(16))
    return img


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--before", type=int, default=5)
    ap.add_argument("--after", type=int, default=10)
    ap.add_argument("--every", type=int, default=30)
    ap.add_argument("--gates", type=Path, help="gates.json from quality_gates.py, summarised on the page")
    a = ap.parse_args(argv)
    fps, n, W, H = probe(a.video)
    if not n:
        n = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(a.video)],
                                       capture_output=True, text=True).stdout) * fps)
    man = json.loads(a.manifest.read_text()) if a.manifest else {}
    a.out.mkdir(parents=True, exist_ok=True)
    items = [dict(i, kind="interaction") for i in man.get("interactions", [])]
    items += [{"id": f"cut-{c:.2f}", "t": c, "label": "Cut: continuity of identity, position and props", "kind": "cut"} for c in man.get("cuts", [])]
    sections = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for it in items:
            f0 = round(it["t"] * fps)
            fr = [f for f in range(f0 - a.before, f0 + a.after + 1) if 0 <= f < n]
            got = grab(a.video, fr, fps, tmp)
            paths = [(f, got[f]) for f in fr if f in got]
            name = f"sheet_{it['id']}.png"
            sheet(paths, fps, 4, 480, f0, title=f"{it['id']}: {it['label']}").save(a.out / name)
            crop = None
            if it.get("box"):
                crop = f"crop_{it['id']}.png"
                sheet(paths, fps, 4, 480, f0, box=it["box"], title=f"{it['id']} (enlarged)").save(a.out / crop)
            sections.append((it, name, crop, len(paths)))
            for p in tmp.glob("*.png"):
                p.unlink()
        samples = list(range(0, n, a.every))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a.video), "-vf", f"select='not(mod(n\\,{a.every}))',scale=640:-1",
                        "-vsync", "0", str(tmp / "s_%05d.png")], check=True)                  # one decode pass
        got = {f: tmp / f"s_{i + 1:05d}.png" for i, f in enumerate(samples) if (tmp / f"s_{i + 1:05d}.png").exists()}
        sample_sheets = []
        for k in range(0, len(samples), 24):
            chunk = [(f, got[f]) for f in samples[k:k + 24] if f in got]
            name = f"samples_{k // 24 + 1}.png"
            sheet(chunk, fps, 6, 320, None, title=f"1 in {a.every} frames ({k + 1}–{k + len(chunk)} of {len(samples)})").save(a.out / name)
            sample_sheets.append(name)

    gates_html = ""
    if a.gates and a.gates.exists():
        g = json.loads(a.gates.read_text())
        rows = "".join(f"<tr class='{'ok' if s['pass'] else 'bad'}'><td>{html.escape(s['gate'])}</td><td>{'PASS' if s['pass'] else 'FAIL'}</td>"
                       f"<td><pre>{html.escape(chr(10).join(s.get('findings', [])[:40]))}</pre></td></tr>" for s in g.get("gates", []))
        gates_html = f"<h2>Automated gates</h2><table>{rows}</table>"
    checks = "".join(f"<li><label><input type='checkbox'> {html.escape(c)}</label></li>" for c in CHECKLIST)
    secs = "".join(f"<section><h3>{html.escape(it['id'])} · {it['t']:.2f}s · {html.escape(it['kind'])}</h3><p>{html.escape(it['label'])}</p>"
                   f"<p class='small'>{cnt} consecutive frames, −{a.before}…+{a.after}; the gold frame is the event.</p>"
                   f"<img src='{name}'>" + (f"<img src='{crop}'>" if crop else "") + "</section>" for it, name, crop, cnt in sections)
    samp = "".join(f"<img src='{s}'>" for s in sample_sheets)
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Review · {html.escape(a.video.name)}</title>
<style>body{{background:#101216;color:#e8e8e8;font:16px/1.45 system-ui,sans-serif;margin:24px;max-width:1960px}}
img{{max-width:100%;display:block;margin:8px 0 18px}}h1,h2,h3{{font-family:Georgia,serif}}.small{{color:#9aa}}
table{{border-collapse:collapse}}td{{border:1px solid #333;padding:6px 10px;vertical-align:top}}tr.bad td:nth-child(2){{color:#ff7b6b;font-weight:700}}
tr.ok td:nth-child(2){{color:#7bd88f;font-weight:700}}pre{{margin:0;white-space:pre-wrap;font-size:13px}}li{{margin:4px 0}}</style></head><body>
<h1>Visual review · {html.escape(a.video.name)}</h1><p class="small">{W}×{H}, {fps:g} fps, {n} frames. Generated from the stored video; nothing was rendered.</p>
{gates_html}<h2>Human checklist</h2><ol>{checks}</ol><h2>Interactions and cuts</h2>{secs}<h2>Frame sample</h2>{samp}</body></html>"""
    (a.out / "review.html").write_text(page, encoding="utf-8")
    print(f"review_sheets: {len(sections)} contact sheet(s), {len(sample_sheets)} sample sheet(s) → {a.out / 'review.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
