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
                "diegetic.py", "whiteboard_chart", "crt_chart", "ticker_board", "gauge", "press_clip", "scene_plan.py", "still.mjs", "LICENSES.md",
                "finmech.py", "finmotion.js", "FM.coins", "plates.py", "camera3d.py", "reach", "office_v2.py",
                "finstate.py", "Ledger", "money.py", "cash_pile", "explain.py", "cashflow_bars", "runway_chart", "FM.bills", "office_v3.py"):
        assert sym in idx, sym


# ── motion layer (rig3.js, animatable diegetic parts, motion-test plan) ───────────────────────────
def test_pose_angles_take_the_short_arc():
    for name in rig3.POSES:
        ang = rig3.pose_angles(name)
        assert set(ang) == set(rig3.JOINTS)
        assert all(-180 <= v <= 180 for v in ang.values()), name


def test_figures_expose_animatable_joints():
    svg = rig3.figure_svg("q", "founder", pose="talk")
    for j in rig3.JOINTS + ("eyes", "mouth", "brows"):
        assert f'id="q-{j}"' in svg, j
    js = (EL / "kit/rig3.js").read_text()
    for fn in ("rot(", "pose(", "blinks(", "blink(", "breathe(", "talk(", "type(", "idle(", "walk("):
        assert fn in js, fn
    assert "Math.random" not in js


def test_whiteboard_gap_parts_have_ids():
    svg = diegetic.whiteboard_gap("T", [("A", 1, "#e07a5f"), ("B", .5, "#f2c66d")], ("REV", .3), uid="g")
    for part in ("g-seg0", "g-seg1", "g-segl0", "g-rev", "g-gap", "g-gapl", "g-dash", "g-ring", "g-coll0", "g-coll1"):
        assert f'id="{part}"' in svg, part
    assert "ILLUSTRATIVE" in svg


def test_rejected_previews_fail_and_v3_passes():
    mt = EL / "episodes/ai-bubble-vs-dot-com/motiontest"
    old = json.loads((mt / "scene_plan.json").read_text())
    assert any("holds" in e for e in scene_plan.validate(old))                 # held one composition across concepts
    v2 = scene_plan.validate(json.loads((mt / "office_v2_plan.json").read_text()))
    assert any("too short" in e for e in v2) and any("compositions start within 10 s" in e for e in v2)   # too frantic
    v3 = json.loads((mt / "office_v3_plan.json").read_text())
    assert scene_plan.validate(v3) == []
    assert all(set(s["meaning"]) == {"what", "why", "consequence"} for s in v3["shots"])


def test_ledger_keeps_every_figure_consistent():
    from kit.finstate import Ledger
    led = Ledger(start=13).spend({"ADVERTISING": 2, "PAYROLL": 1, "SERVERS": 1}).earn({"REVENUE": 1})
    assert led.total_spending == 4 and led.monthly_burn == 3 and led.balance == 10
    assert 3 <= led.runway_months < 4                                            # "about three months" (matches the close-up)
    assert led.balance_after(2) == 4 and led.balance_after(2) + 20 == 24
    pts = led.curve(10, {2: 20})
    assert pts[0] == (0.0, 10) and (2.0, 4) in pts and (2.0, 24) in pts and pts[-1][1] == 0
    assert led.fmt(-3) == "-$3M" and led.fmt(20, signed=True) == "+$20M" and led.units(13) == 13
    import importlib.util
    spec = importlib.util.spec_from_file_location("ov3", EL / "episodes/ai-bubble-vs-dot-com/motiontest/office_v3.py")
    v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)
    assert v3.LED.balance == led.balance and v3.CASH_AT_FUNDING == 4 and v3.CASH_AFTER_FUNDING == 24


def test_money_and_explain_parts():
    from kit import explain, money
    from kit.finstate import Ledger
    pile = money.cash_pile("c", 0, 500, 9, capacity=24)
    assert pile.count('id="c-bd') == 24 and pile.count('opacity="0"') >= 15
    assert "RECEIVED" in money.wire_slip("w", 0, 0, "$20,000,000", "A", "B") and 'id="w-stamp"' in money.wire_slip("w", 0, 0, "$1", "A", "B")
    assert 'id="t-sig"' in money.term_sheet("t") and 'id="c-card"' in money.commercial("c", 0, 0, 600, 400)
    led = Ledger(start=13).spend({"ADVERTISING": 2, "PAYROLL": 1, "SERVERS": 1}).earn({"REVENUE": 1})
    bars = explain.cashflow_bars("cf", 0, 0, 860, 640, led)
    for part in ("cf-seg0", "cf-seg2", "cf-in", "cf-gap", "cf-gapl", "cf-outl", "cf-inl"):
        assert f'id="{part}"' in bars, part
    assert "-$3M" in bars and "Illustrative" in bars
    rw = explain.runway_chart("rw", 0, 0, 850, 640, led, months=10, injections={2: 20})
    for part in ("rw-line", "rw-proj", "rw-runway", "rw-jump", "rw-line2", "rw-next"):
        assert f'id="{part}"' in rw, part
    js = (EL / "kit/finmotion.js").read_text()
    assert "bills(" in js and "pileTo(" in js and "count(" in js


def test_characters_look_and_hold_new_stances():
    svg = rig3.figure_svg("e", "suit", pose="stand2")
    assert svg.count('class="iris"') == 2 and "e-ec" in svg
    assert {"stand2", "hips"} <= set(rig3.POSES)
    js = (EL / "kit/rig3.js").read_text()
    assert "look(" in js and "write(" in js and "keys(" in js


# ── financial mechanisms, plates, camera twin ────────────────────────────────────────────────────
def test_finmech_parts_expose_animation_ids():
    from kit import finmech as F
    t = F.tank_svg("t", 0, 0, 400, 600, level=.5)
    for part in ("t-fill", "t-fillwrap", "t-needle", "t-lamp", "t-clip"):
        assert f'id="{part}"' in t, part
    p = F.glass_pipe("p", [(0, 0), (500, 0), (500, 300)], 40, "SPENDING")
    assert 'id="p-path"' in p and 'id="p-coins"' in p and "SPENDING" in p
    g = F.gauge_dial("g", 100, 100, 80, .3)
    assert 'id="g-needle"' in g and 'id="g-lamp"' in g
    tv = F.tv_set("v", 0, 0, 500)
    for part in ("v-off", "v-line", "v-ad", "v-fly", "v-rocket", "v-logo", "v-tag", "v-flame"):
        assert f'id="{part}"' in tv, part
    assert F.tank_svg("t", 0, 0, 400, 600) == F.tank_svg("t", 0, 0, 400, 600)


def test_finmotion_is_seekable_and_seeded():
    js = (EL / "kit/finmotion.js").read_text()
    for fn in ("coins(", "drop(", "level(", "valve(", "needle(", "lamp(", "powerOn(", "pop(", "stampIn("):
        assert fn in js, fn
    assert "Math.random" not in js and "setTimeout" not in js and "requestAnimationFrame" not in js


def test_camera_twin_matches_scene3d_convention():
    from kit.camera3d import Camera
    c = Camera(pos=[0, 1.6, 10], look=[0, 1.6, 0], fov=60)
    x, y, z = c.project([0, 1.6, 0])
    assert abs(x - 960) < 1e-6 and abs(y - 540) < 1e-6 and abs(z - 10) < 1e-6
    assert c.project([0, 1.6, 20]) is None
    assert "fov: 60" in c.js()


def test_reach_ik_lands_the_hand_and_props_attach():
    a = rig3.reach("stand", (380, 430))
    hx, hy = rig3.hand_point(a)
    assert abs(hx - 380) < 1 and abs(hy - 430) < 1
    mk = rig3.hold(rig3.figure_svg("h", "suit", inner=True), "h", "stamp")
    assert 'class="prop"' in mk.split('id="h-hand-front"')[1][:400]
    assert "rotate(" in rig3.figure_svg("h", "suit", angles=a)
