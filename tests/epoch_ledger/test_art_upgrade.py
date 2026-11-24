"""Art-direction upgrade: scene3d engine, rig v3 (figures + close-up), lightfx, diegetic graphics, scene plans, asset licences."""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EL = ROOT / "epoch-ledger"
sys.path.insert(0, str(EL))

from kit import diegetic, lightfx, rig3, scene_plan  # noqa: E402


# ── rig v3 ──────────────────────────────────────────────────────────────────────────────────────
def test_ik_reaches_target_and_respects_bone_lengths():
    sh, tgt = (200.0, 200.0), (300.0, 330.0)
    a1, a2 = rig3.ik(sh, tgt, 120, 115, 1)[:2]
    elbow = (sh[0] + 120 * math.sin(math.radians(-a1)), sh[1] + 120 * math.cos(math.radians(-a1)))
    # reconstruct the hand position from the returned angles in the rig's convention (0° = hanging down)
    hand = (elbow[0] + 115 * math.sin(math.radians(-(a1 + a2))), elbow[1] + 115 * math.cos(math.radians(-(a1 + a2))))
    assert math.dist(hand, tgt) < 2.0


@pytest.mark.parametrize("pose", list(rig3.POSES))
def test_figure_poses_render_with_rig_parts(pose):
    svg = rig3.figure_svg("t", "suit", pose=pose)
    for part in ("t-head", "t-brows", "t-mouth"):
        assert f'id="{part}"' in svg
    assert svg == rig3.figure_svg("t", "suit", pose=pose)          # deterministic


def test_closeup_head_is_expressive_and_animatable():
    a = rig3.closeup_svg("f", expr="worried", hand="phone")
    b = rig3.closeup_svg("f", expr="smile", hand=None)
    for part in ("f-head", "f-brows", "f-mouth", "f-lids", "f-hand"):
        assert f'id="{part}"' in a
    assert 'id="f-hand"' not in b and a != b
    assert rig3.CLOSEUP_VIEWBOX in a


# ── diegetic graphics + lightfx ─────────────────────────────────────────────────────────────────
def test_diegetic_builders_are_deterministic_and_carry_their_data():
    wb = diegetic.whiteboard_chart("THIS MONTH", [("ADS", 1, "#e07a5f"), ("REVENUE", .2, "#5fb36a")], note=["GAP"])
    assert wb == diegetic.whiteboard_chart("THIS MONTH", [("ADS", 1, "#e07a5f"), ("REVENUE", .2, "#5fb36a")], note=["GAP"])
    assert "ADS" in wb and "REVENUE" in wb and "GAP" in wb
    crt = diegetic.crt_chart("CASH", [10, 5, 1], "RUNWAY", "3 MONTHS", uid="x")
    assert "3 MONTHS" in crt and 'id="x-scan"' in crt
    assert "▲" in diegetic.ticker_board("TECH", [1, 2, 3]) and "▼" in diegetic.ticker_board("TECH", [3, 2, 1])
    assert "CASH" in diegetic.gauge("CASH", .2) and "$40 million" in diegetic.press_clip("D", "raises", "$40 million")


def test_lightfx_layers():
    over, root = lightfx.grade(vignette=.5, grain=.05, seed=3)
    assert 'seed="3"' in over and root.startswith("contrast(")
    assert "lf-sky" in lightfx.sky("dusk") and "mix-blend-mode:screen" in lightfx.beams([(0, 0, 0, 100, 50)])


# ── scene plans ─────────────────────────────────────────────────────────────────────────────────
def test_styleframe_scene_plan_is_valid():
    plan = json.loads((EL / "episodes/ai-bubble-vs-dot-com/styleframes/scene_plan.json").read_text())
    assert scene_plan.validate(plan) == []
    assert {s["shot"] for s in plan["shots"]} >= {"establishing", "medium", "close-up"}


def test_scene_plan_rejects_unconsulted_or_dashboard_shots():
    shot = {"id": "x", "beat": {"t": "0:00", "narration": "n"}, "understanding": "the viewer learns a thing", "shot": "wide",
            "focal_point": "f", "camera": "c", "lighting": "l", "technique": ["scene3d"], "components": ["S3.box"],
            "graphics": [{"kind": "overlay", "what": "floating KPI panel"}], "rationale": "r", "consulted": ["epoch-ledger/QUALITY.md"]}
    errs = scene_plan.validate({"shots": [dict(shot, id=f"s{i}") for i in range(4)]})
    assert any("motion-craft" in e for e in errs)
    assert any("overlay graphic" in e for e in errs)
    assert any("consecutive" in e for e in errs)


# ── assets ──────────────────────────────────────────────────────────────────────────────────────
def test_every_texture_has_an_individual_licence_record():
    tex = EL / "kit/assets/textures"
    manifest = json.loads((tex / "manifest.json").read_text())
    register = (EL / "kit/assets/LICENSES.md").read_text()
    files = sorted(p.stem for p in tex.glob("*.jpg"))
    assert files and files == sorted(manifest)
    for key, rec in manifest.items():
        assert rec["license"].startswith("CC0") and rec["authors"] and rec["source"].startswith("https://")
        assert f"| {key} |" in register and rec["source"] in register


# ── scene3d engine (browser) ────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not shutil.which("node"), reason="node not available")
def test_scene3d_projection_and_determinism(tmp_path):
    page = tmp_path / "s.html"
    page.write_text(f'<script src="{(EL / "kit/scene3d.js").as_uri()}"></script>')
    probe = tmp_path / "p.cjs"
    probe.write_text("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2]);const r=await p.evaluate(()=>{
 const cam=S3.camera({pos:[0,1.6,10],look:[0,1.6,0],fov:60});
 const c=cam.project([0,1.6,0]), behind=cam.project([0,1.6,20]);
 const mk=()=>{const sc=S3.scene();sc.ground(-5,-10,5,5,0,2,{color:'#888'});sc.box([-1,0,-2],[1,2,0],{color:'#c33'});
   sc.sprite([2,0,-1],1.8,'<rect width="40" height="100"/>',.4,{viewBox:'0 0 40 100'});
   return S3.render(sc,cam,{sun:{dir:[.3,.6,1],color:'#fff',intensity:1},sky:'#bbd',ground:'#543',ambient:.4,fog:{color:'#ccc',near:5,far:40,max:.5}},{uid:'t'});};
 const a=mk(), b2=mk(); return {c, behind, same:a===b2, len:a.length, paths:(a.match(/<path/g)||[]).length};});
console.log(JSON.stringify(r));await b.close();})();""")
    r = subprocess.run(["node", str(probe), str(page)], capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr[-2000:]
    s = json.loads(r.stdout.strip().splitlines()[-1])
    assert abs(s["c"][0] - 960) < 1e-6 and abs(s["c"][1] - 540) < 1e-6    # look-at point lands at frame centre
    assert s["behind"] is None                                             # points behind the camera are clipped
    assert s["same"] and s["paths"] > 10


def test_component_index_lists_art_upgrade():
    idx = (EL / "COMPONENTS.md").read_text()
    for sym in ("scene3d.js", "S3.camera", "S3.facade", "S3.art", "S3.sprite", "lightfx.py", "rig3.py", "figure_svg", "closeup_svg", "ik(",
                "diegetic.py", "whiteboard_chart", "crt_chart", "ticker_board", "gauge", "press_clip", "scene_plan.py", "still.mjs", "LICENSES.md"):
        assert sym in idx, sym
