"""Epoch Ledger scene assembler — turns per-scene parts into a cache-friendly HyperFrames index.html.

Each Scene becomes one top-level clip; its CSS and JS are wrapped in /*scene:<id>*/ regions
so scripts/render.py re-renders only the chunks a changed scene touches. Shared layers
(theme, helpers, optional Three.js vault, optional caption layer, vignette, narration) are
added around the scenes.

    from kit.assemble import Scene, assemble, prepare_workspace
    html = assemble(title=..., duration=D, scenes=[Scene("s1", 0, 4.6, html, css, js), ...],
                    vault={"shots": [...]}, caption_pages=pages)
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .captions import caption_layer

KIT = Path(__file__).resolve().parent

# Output sizes. Scenes are always authored on a 1920x1080 design canvas; for 1440p the page and
# root are 2560x1440 and each top-level clip is CSS-zoomed by 4/3, so vectors, text and SVG re-rasterise
# crisply (HyperFrames' own --resolution upscale rejects the non-integer 1080p→1440p factor).
# 1080p is the default; 1440p is optional until it has been benchmarked on a real episode;
# 540p is for draft previews only.
RESOLUTIONS = {"1080p": (1920, 1080), "1440p": (2560, 1440), "540p": (960, 540)}
# 540p is the draft-preview size (clips zoomed 0.5): ~4x fewer pixels to rasterise per frame. Build it into
# its own workspace (e.g. projects/<slug>/draft) so draft and final caches never mix.


@dataclass
class Scene:
    id: str
    start: float
    duration: float
    html: str
    css: str = ""
    js: str = ""
    track: int | None = None


def prepare_workspace(ws: Path, vendor_dir: Path | None = None) -> None:
    """Copy kit JS into WS/vendor. Fonts + GSAP + Three.js come from scripts/vendor.sh."""
    (ws / "vendor").mkdir(parents=True, exist_ok=True)
    shutil.copy(KIT / "vault3d.js", ws / "vendor" / "vault3d.js")


def assemble(*, title: str, duration: float, scenes: list[Scene], vault: dict | None = None,
             caption_pages: list[dict] | None = None, caption_style: dict | None = None,
             extra_css: str = "", audio: str = "narration.wav", fps: int = 30, vignette: bool = True,
             resolution: str = "1080p", head_scripts: list[str] | None = None,
             layers: list[str] | None = None, shared_js: str = "", js_regions: list[tuple] | None = None) -> str:
    """head_scripts: extra <script src> paths (e.g. episode 3D engines in vendor/).
    layers: extra top-level clip markup placed under the scenes (e.g. a shared 3D canvas).
    shared_js: episode helpers that every scene may call (changing it invalidates the whole cache).
    js_regions: (id, spans, js) tuples for code that belongs to a time window but no scene clip,
    e.g. a 3D shot — wrapped as /*scene:id spans=...*/ so render.py caches it per window."""
    if resolution not in RESOLUTIONS:
        raise ValueError(f"unsupported resolution {resolution!r}; choose from {sorted(RESOLUTIONS)}")
    out_w, out_h = RESOLUTIONS[resolution]
    zoom = out_w / 1920
    theme = (KIT / "theme.css").read_text()
    helpers = "\n".join((KIT / f).read_text() for f in ("helpers.js", "rig.js", "motion.js"))
    css_parts, clips, js_parts = [theme, extra_css], list(layers or []), [shared_js] if shared_js else []
    for rid, spans, code in js_regions or []:
        sp = ",".join(f"{a}-{min(b, duration)}" for a, b in spans)
        js_parts.append(f"/*scene:{rid} spans={sp}*/\n{code}\n/*/scene:{rid}*/")
    # Non-1080p output: the root is sized to the output frame and every top-level clip (each
    # authored on the 1920x1080 design canvas) is CSS-zoomed by out/1920. Vectors, text and the 3D
    # canvas re-rasterise at the output size. Zoom must not sit on #root: HyperFrames sizes its
    # capture frame from the root's layout box, so a zoomed root paints into only part of the
    # frame (verified with calibration markers at 540p and 1440p, 2026-11-24).
    if zoom != 1:
        css_parts.append(f"html,body{{width:{out_w}px;height:{out_h}px}}"
                         f"#root{{width:{out_w}px;height:{out_h}px}}.clip{{zoom:{zoom:.10f}}}")
    if vault is not None:
        clips.append(f'<canvas id="gl" class="clip" data-start="0" data-duration="{duration}" '
                     f'data-track-index="0" width="1920" height="1080"></canvas>')
        spans = ",".join(f"{s['start']}-{min(s['end'], duration)}" for s in vault["shots"])
        opts = json.dumps({"width": out_w, "height": out_h, **vault}).replace("Infinity", "1e9")
        js_parts.append(f"/*scene:vault3d spans={spans}*/\n"
                        f"const vault=EpochVault3D.create(Object.assign({{canvas:document.getElementById('gl')}},{opts}));\n"
                        f"const P={{t:0}}; tl.to(P,{{t:{duration},duration:{duration},ease:'none',onUpdate:()=>vault.draw(P.t)}},0);\n"
                        f"/*/scene:vault3d*/")
    for i, s in enumerate(scenes, start=1):
        track = s.track if s.track is not None else i
        clips.append(f'<div id="{s.id}" class="clip" data-start="{s.start}" data-duration="{s.duration}" '
                     f'data-track-index="{track}">\n{s.html}\n</div>')
        if s.css:
            css_parts.append(f"/*scene:{s.id}*/\n{s.css}\n/*/scene:{s.id}*/")
        if s.js:
            js_parts.append(f"/*scene:{s.id}*/\n{s.js}\n/*/scene:{s.id}*/")
    if caption_pages:
        ccss, chtml, cjs = caption_layer(caption_pages, fps=fps, style=caption_style)
        css_parts.append(ccss)
        clips.append(chtml)
        js_parts.append(cjs)
    if vignette:
        clips.append(f'<div id="vig" class="clip vignette" data-start="0" data-duration="{duration}" data-track-index="90"></div>')
    if audio:
        clips.append(f'<audio id="vo" src="{audio}" data-start="0" data-duration="{duration}" data-track-index="91"></audio>')
    body = "\n".join(clips)
    script = "\n".join(js_parts)
    return f"""<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<title>{title}</title>
<script src="vendor/gsap.min.js"></script>
<script src="vendor/three.min.js"></script>
<script src="vendor/vault3d.js"></script>
{"".join(f'<script src="{src}"></script>' for src in (head_scripts or []))}
<style>
{chr(10).join(css_parts)}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="{out_w}" data-height="{out_h}">
{body}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{paused:true}});
{helpers}
{script}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""
