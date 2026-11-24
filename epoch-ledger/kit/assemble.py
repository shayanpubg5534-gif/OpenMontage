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
             extra_css: str = "", audio: str = "narration.wav", fps: int = 30, vignette: bool = True) -> str:
    theme = (KIT / "theme.css").read_text()
    helpers = (KIT / "helpers.js").read_text()
    css_parts, clips, js_parts = [theme, extra_css], [], []
    if vault is not None:
        clips.append(f'<canvas id="gl" class="clip" data-start="0" data-duration="{duration}" '
                     f'data-track-index="0" width="1920" height="1080"></canvas>')
        spans = ",".join(f"{s['start']}-{min(s['end'], duration)}" for s in vault["shots"])
        opts = json.dumps({k: v for k, v in vault.items()}).replace("Infinity", "1e9")
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
<style>
{chr(10).join(css_parts)}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080">
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
