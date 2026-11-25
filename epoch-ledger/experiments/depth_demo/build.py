"""Depth-layer demo: the BigCart office as background / midground / foreground plates with a parallax camera,
haze between the layers, a blurred near foreground and a Rig v4 character walking at midground depth.

  python epoch-ledger/experiments/depth_demo/build.py [WS]     (default projects/ai-bubble-vs-dot-com/depth_demo)
Not part of the episode; it proves kit/depth.py + kit/depth.js. Original implementation.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EL = HERE.parents[1]
ROOT = EL.parent
sys.path.insert(0, str(EL))
from kit import depth, rig4  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402
from kit.camera3d import Camera  # noqa: E402

spec = importlib.util.spec_from_file_location("ov3", EL / "episodes/ai-bubble-vs-dot-com/motiontest/office_v3.py")
OV3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OV3)
V2 = OV3.V2
SRC = ROOT / "projects/ai-bubble-vs-dot-com/compare/aprime"
D = 6.0
CAM = Camera(pos=[-1.4, 1.5, -0.6], look=[-1.4, 1.05, -6], fov=50)

# story-specific near foreground: the corner of a desk with a monitor back, a mug and a plant (all within ~2 m)
FG = r"""
sc.box([-0.25, .72, -2.55], [0.9, .78, -1.75], { color: '#7a5236', gloss: .2 }, { layer: 'fg' });
sc.box([0.05, .78, -2.35], [0.62, 1.18, -2.28], { color: '#2a2c34' }, { layer: 'fg' });
sc.box([0.3, .78, -2.3], [0.36, .9, -2.24], { color: '#3a3a42' }, { layer: 'fg' });
sc.box([-0.12, .78, -2.05], [-0.02, .9, -1.95], { color: '#e8e0d0' }, { layer: 'fg' });
sc.art([-2.95, 0, -2.15], [-2.25, 0, -2.15], [-2.95, 1.12, -2.15], 400, 640, FOLIAGE, { layer: 'fg' });
"""


def build(ws: Path):
    ws.mkdir(parents=True, exist_ok=True)
    for d in ("fonts", "vendor"):
        if (ws / d).exists():
            shutil.rmtree(ws / d)
        shutil.copytree(SRC / d, ws / d)
    for f in ("rig4.js", "scene3d.js", "depth.js"):
        shutil.copy(EL / "kit" / f, ws / "vendor" / f)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(SRC / f, ws / f)
    pd = ws / "plates"
    (pd / "tex").mkdir(parents=True, exist_ok=True)
    for f in (EL / "kit/assets/textures").glob("*.jpg"):
        shutil.copy(f, pd / "tex" / f.name)
    if not (pd / "fonts").exists():
        shutil.copytree(ws / "fonts", pd / "fonts")
    glows = "const GLOWS = [" + ",".join(f"[[{x},3.05,{z}],{r},'#fff2cc']" for x, z, r in ((-2.4, 1, 150), (1.6, 1, 150), (-2.4, -2.2, 110), (1.6, -2.2, 110), (-2.4, -5.4, 80), (1.6, -5.4, 80))) + "];"
    scene = f"const FOLIAGE = {json.dumps(depth.foliage(seed=11))};" + V2.office_scene(drop_desks=True) + FG
    L = depth.layered(pd, "office", scene, CAM, V2.OFFICE_LIGHT, prelude_js=f"const ART = {json.dumps(V2.common.ART)};" + glows,
                      split=(2.4, 6.5), blur={"fg": 6.0, "bg": .6}, haze=.16, assets=tuple(sorted((EL / "kit/assets/textures").glob("*.jpg"))))
    # the founder walks across the midground (feet at ~4 m): a screen-space sprite at the depth of his feet
    foot = [-1.4, 0, -4.6]
    f, h = CAM.project(foot), CAM.project([foot[0], 1.88, foot[2]])
    s = (f[1] - h[1]) / 1000
    W = 4000
    x0 = f[0] - W / 2 * s
    walker = (f'<svg class="full" viewBox="0 0 1920 1080" overflow="visible"><svg x="{x0:.1f}" y="{h[1]:.1f}" width="{W * s:.1f}" height="{1000 * s:.1f}" '
              f'viewBox="0 0 {W} 1000" overflow="visible"><g id="dw"></g></svg></svg>')
    mid = W / 2
    js = (rig4.create_js("dw", "founder", x=mid + 900, yaw=-90, ground=1000, blink_seed=4, t0=0, t1=D)
          + f"R4.walk('dw', .3, 3.4, {mid - 500});" + f"R4.turn('dw', 3.6, -15, .7);"
          + f"R4.look('dw', 4.3, [{mid - 1400}, 300]); R4.express('dw', 4.4, {{brow: [.4, .2], smile: .25}});"
          # motivated camera: it trucks with him as he crosses, then eases in as he stops (parallax shows the depth)
          + L.move_js("d", 0.2, 3.4, truck=-.35, dolly=.25) + L.move_js("d", 3.7, 2.0, truck=-.42, dolly=.55))
    layers = L.html("d", live_mid=walker)
    css = (".shot{position:absolute;inset:0;overflow:hidden;background:#100c0c}.layer{position:absolute;inset:0}"
           ".full{position:absolute;inset:0;width:1920px;height:1080px}.plate{position:absolute;left:0;top:0;width:1920px;height:1080px}"
           ".tag{position:absolute;right:64px;top:56px;padding:10px 20px;border-radius:8px;background:rgba(12,14,24,.62);color:#f3e9d6;font:700 28px Inter}")
    shot = f'<div class="shot" id="d" style="filter:contrast(1.05) saturate(1.05)">{layers}<div class="tag">Depth layers demo · BigCart.com is fictional</div></div>'
    html = assemble(title="Depth layers demo", duration=D, scenes=[Scene("d", 0, D, shot, js="{\n" + js + "\n}")], extra_css=css, audio="",
                    vignette=False, head_scripts=["vendor/rig4.js", "vendor/depth.js"])
    html = html.replace("window.__timelines[\"main\"] = tl;", "R4.attach(tl);\nwindow.__timelines[\"main\"] = tl;")
    (ws / "index.html").write_text(html)
    print("wrote", ws / "index.html", {k: v.name for k, v in L.png.items()})


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects/ai-bubble-vs-dot-com/depth_demo")
