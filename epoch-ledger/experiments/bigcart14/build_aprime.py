"""A′ — the BRIEF.md shots built with OpenMontage (HyperFrames assembly, render.py, approved caption layer).
  python epoch-ledger/experiments/bigcart14/build_aprime.py [WS]   (default projects/ai-bubble-vs-dot-com/compare/aprime)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shots as S  # noqa: E402
from kit import rig3  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402
from kit.plates import plate  # noqa: E402

V2, V3 = S.V2, S.V3
CSS = (".shot{position:absolute;inset:0;overflow:hidden;background:#100c0c}.layer{position:absolute;inset:0}.full{position:absolute;inset:0;width:1920px;height:1080px}"
       ".plate{position:absolute;left:0;top:0;width:1920px;height:1080px}"
       ".tag{position:absolute;right:64px;top:56px;padding:10px 20px;border-radius:8px;background:rgba(12,14,24,.62);color:#f3e9d6;font:700 28px Inter}"
       ".counter{position:absolute;padding:14px 26px;border-radius:14px;background:rgba(14,12,10,.72);color:#f3e9d6;font-family:Inter;box-shadow:0 8px 30px rgba(0,0,0,.35)}"
       ".counter .cl{font:700 24px Inter;letter-spacing:3px;color:#c8bba0}.counter .cv{font:800 72px Fraunces;color:#9fe39a;line-height:1.05}.counter .cn{font:700 18px Inter;color:#8a8070}"
       ".step{position:absolute;left:64px;top:52px;padding:10px 22px 10px 12px;border-radius:30px;background:rgba(12,14,24,.72);color:#f3e9d6;font:700 32px Inter;opacity:0}"
       ".step .sn{display:inline-block;width:44px;height:44px;margin-right:14px;border-radius:22px;background:#f2c66d;color:#1b1410;text-align:center;line-height:44px;font:800 28px Inter}"
       "#rst{top:124px}"
       "@font-face{font-family:Inter;src:url(fonts/inter-latin-700-normal.woff2) format('woff2');font-weight:800}")


def plates(ws: Path) -> dict:
    P = V2.plates(ws)
    art5 = {"window": V2.SF2.art2_dict()["window"], "plant": V2.SF2.art2_dict()["plant"], "name": V3.NAME_SVG}
    html = V2.plate_html(ws / "plates" / "boardroom_c8.html", f"const ART5 = {json.dumps(art5)};" + V2.BOARD_SCENE + V2.BOARD_TABLE,
                         "const GLOWS = [[[-1.6,2.5,-2.7],160,'#ffd8a0'],[[1.6,2.5,-2.7],160,'#ffd8a0']];" + f"const cam = {V3.C8.js()};", V2.BOARD_LIGHT,
                         root="contrast(1.05) saturate(1.05)")
    P["boardroom_c8"] = "plates/" + plate(ws / "plates", "boardroom_c8", html, assets=tuple(sorted((V2.EL / "kit/assets/textures").glob("*.jpg"))) + (V2.EL / "kit/scene3d.js",)).name
    return P


def shared_js() -> str:
    poses = {k: rig3.pose_angles(k) for k in rig3.POSES}
    return f"const TEX = 'tex/';\nconst ART = {json.dumps(V2.common.ART)};\nR3.P = {json.dumps(poses)};"


def build(ws: Path):
    V2.prepare(ws)
    P = plates(ws)
    scenes = []
    for i, (sid, pl, dim, fn) in enumerate(S.shots()):
        t0, t1 = S.CUT[i], S.CUT[i + 1]
        layers, js, over = fn()
        scenes.append(Scene(sid, t0, round(t1 - t0, 3), V2.shot(sid, P[pl] if pl else None, layers, over, dim=dim), js="{\n" + js + "\n}"))
    html = assemble(title="BigCart 14 — A′", duration=S.D, scenes=scenes, caption_pages=V2.caption_pages(), extra_css=CSS,
                    head_scripts=["vendor/scene3d.js", "vendor/rig3.js", "vendor/finmotion.js"], vignette=False, shared_js=shared_js())
    (ws / "index.html").write_text(html)
    V2.narration(ws)
    print("wrote", ws / "index.html")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else S.ROOT / "projects/ai-bubble-vs-dot-com/compare/aprime")
