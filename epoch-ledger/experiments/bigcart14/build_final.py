"""BigCart 14 s — final acceptance preview (Phase 4). See shots_final.py for the shot list.
  python epoch-ledger/experiments/bigcart14/build_final.py [WS]   (default projects/ai-bubble-vs-dot-com/final14)
Render:  python epoch-ledger/scripts/render.py render WS --isolate -o WS/final14.mp4 --audio WS/mix.wav
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_aprime as A  # noqa: E402
import shots_final as SF  # noqa: E402
from kit.assemble import Scene, assemble  # noqa: E402

S, V2, V3 = SF.S, SF.V2, SF.V3
SRC = S.ROOT / "projects/ai-bubble-vs-dot-com/compare/aprime"


def build(ws: Path):
    V2.prepare(ws)
    for f in ("rig4.js", "depth.js", "scene3d.js"):
        shutil.copy(V2.EL / "kit" / f, ws / "vendor" / f)
    # approved plates are reused from the A′ workspace when present (unchanged sets are never re-drawn)
    (ws / "plates").mkdir(exist_ok=True)
    P = {}
    for name in ("office_floor", "office_tank", "boardroom_c8"):
        got = sorted((SRC / "plates").glob(name + "-*.png"))
        if got:
            shutil.copy(got[0], ws / "plates" / got[0].name)
            P[name] = "plates/" + got[0].name
    if len(P) < 3:
        P = A.plates(ws)
    pd = ws / "plates"
    (pd / "tex").mkdir(exist_ok=True)
    for f in (V2.EL / "kit/assets/textures").glob("*.jpg"):
        shutil.copy(f, pd / "tex" / f.name)
    if not (pd / "fonts").exists():
        shutil.copytree(ws / "fonts", pd / "fonts")
    fg_office = SF.env(ws, "office_fg", SF.FG_OFFICE, S.C3, V2.OFFICE_LIGHT).rel["fg"]
    fg_board = SF.env(ws, "board_fg", SF.FG_BOARD, V3.C8, V2.BOARD_LIGHT).rel["fg"]
    C = SF.CUT
    shots = [("s1", lambda: SF.office("s1", "a", C[0], C[1], "burn", P["office_floor"], fg_office), None, 0),
             ("s2", lambda: SF.chart("s2", C[1], C[2]), P["office_tank"], .58),
             ("s3", lambda: SF.boardroom("s3", C[2], C[3], P["boardroom_c8"], fg_board), None, 0),
             ("s4", lambda: SF.office("s4", "r", C[3], C[4], "refill", P["office_floor"], fg_office), None, 0)]
    scenes = []
    for i, (sid, fn, plate_png, dim) in enumerate(shots):
        t0, t1 = C[i], C[i + 1]
        layers, js, over = fn()
        scenes.append(Scene(sid, t0, round(t1 - t0, 3), V2.shot(sid, plate_png, layers, over, dim=dim), js="{\n" + js + "\n}"))
    html = assemble(title="BigCart 14 — final acceptance preview", duration=SF.D, scenes=scenes, caption_pages=V2.caption_pages(),
                    extra_css=A.CSS, head_scripts=["vendor/scene3d.js", "vendor/rig3.js", "vendor/finmotion.js", "vendor/rig4.js", "vendor/depth.js"],
                    vignette=False, shared_js=A.shared_js())
    html = html.replace('window.__timelines["main"] = tl;', 'R4.attach(tl);\nwindow.__timelines["main"] = tl;')
    (ws / "index.html").write_text(html)
    # narration (approved Kokoro track, unchanged) + original sound design keyed to this cut (no music)
    V2.narration(ws)
    import sound_final
    sound_final.build(ws)
    print("wrote", ws / "index.html")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else S.ROOT / "projects/ai-bubble-vs-dot-com/final14")
