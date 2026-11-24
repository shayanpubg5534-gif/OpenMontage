"""Episode builder: Is the AI Bubble Bigger Than the Dot-Com Bubble? (Epoch Ledger flagship).

  EPOCH_RESOLUTION=540p python epoch-ledger/episodes/ai-bubble-vs-dot-com/build.py projects/ai-bubble-vs-dot-com/draft
  python epoch-ledger/episodes/ai-bubble-vs-dot-com/build.py            # 1080p → projects/<slug>/hyperframes

Scenes are authored per storyboard segment in scenes_*.py; every tween is keyed to narration line
starts or Whisper word times (script wording), never hand-typed seconds.
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[1]
sys.path.insert(0, str(KIT_ROOT))
sys.path.insert(0, str(HERE))

from kit.assemble import RESOLUTIONS, assemble, prepare_workspace  # noqa: E402

import timeline  # noqa: E402
import floor  # noqa: E402
import scenes_opening, scenes_collapse, scenes_infra, scenes_money, scenes_debt, scenes_railway  # noqa: E402,E401

WORKSPACE = Path(sys.argv[1]) if len(sys.argv) > 1 else KIT_ROOT.parent / "projects" / HERE.name / "hyperframes"
CONFIG = json.loads((KIT_ROOT / "config" / "production.json").read_text())
resolution = os.environ.get("EPOCH_RESOLUTION", CONFIG["render"]["default_resolution"])
OUT_W, OUT_H = RESOLUTIONS[resolution]

MODULES = [scenes_opening, scenes_collapse, scenes_infra, scenes_money, scenes_debt, scenes_railway]
scenes, regions, css = [], [], []
for m in MODULES:
    sc, rg, cs = m.build()
    scenes += sc
    regions += rg
    css.append(cs)

EPISODE_CSS = (HERE / "episode.css").read_text()
SHARED_JS = (
    (HERE / "js" / "episode_helpers.js").read_text() + floor.BOARD_JS
    + f"\nAI3D.init(document.getElementById('gl3d'), {{width:{OUT_W}, height:{OUT_H}}});\n"
    + "const P3={t:0}; tl.to(P3,{t:%s,duration:%s,ease:'none',onUpdate:()=>AI3D.draw(P3.t)},0);\n" % (timeline.D, timeline.D)
)
layers = [f'<canvas id="gl3d" class="clip" data-start="0" data-duration="{timeline.D}" data-track-index="0" '
          f'width="1920" height="1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px"></canvas>']

html = assemble(
    title="Is the AI Bubble Bigger Than the Dot-Com Bubble?", duration=timeline.D, scenes=scenes,
    caption_pages=timeline.PAGES,  # HyperFrames-native captions approved for this episode
    extra_css=EPISODE_CSS + "\n".join(css), resolution=resolution, head_scripts=["vendor/ai3d.js"],
    layers=layers, shared_js=SHARED_JS, js_regions=regions, audio="mix.wav",
)
prepare_workspace(WORKSPACE)
shutil.copy(HERE / "js" / "ai3d.js", WORKSPACE / "vendor" / "ai3d.js")
(WORKSPACE / "index.html").write_text(html)
print("wrote", WORKSPACE / "index.html", resolution, f"{len(scenes)} scenes, {len(regions)} 3D/JS regions")
