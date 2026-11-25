"""Epoch Ledger kit: pilot reproducibility, render planning/caching, caption parity, assembly."""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "epoch-ledger"
PILOT = KIT / "episodes" / "how-banks-create-money"
sys.path.insert(0, str(KIT))

from kit.assemble import Scene, assemble  # noqa: E402
from kit.captions import caption_layer  # noqa: E402
from kit.characters import banker_svg, maya_svg  # noqa: E402


def _render_mod():
    spec = importlib.util.spec_from_file_location("el_render", KIT / "scripts" / "render.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["el_render"] = mod  # dataclasses resolve their module at class creation
    spec.loader.exec_module(mod)
    return mod


def test_pilot_build_is_byte_identical_to_approved(tmp_path):
    subprocess.run([sys.executable, str(PILOT / "build.py"), str(tmp_path)], check=True, capture_output=True)
    digest = hashlib.sha256((tmp_path / "index.html").read_bytes()).hexdigest()
    assert digest == (PILOT / "APPROVED_INDEX_SHA256").read_text().strip()


@pytest.mark.parametrize("mode", ["walk", "bust", "phone"])
def test_maya_svg_has_rig_parts(mode):
    svg = maya_svg("t", mode)
    for part in ("t-head", "t-upper", "t-arm-front", "t-arm-back", 'class="lid"'):
        assert part in svg
    assert ("t-leg-front" in svg) == (mode == "walk")


def test_banker_svg_has_rig_parts():
    svg = banker_svg("b")
    for part in ("b-head", "b-arm-front", "b-stamp", 'class="lid"'):
        assert part in svg


def _doc(duration=10.0, s2_js="tl.to('#x',{x:1},5);"):
    return assemble(title="t", duration=duration, audio="", vignette=False, scenes=[
        Scene("s1", 0, 5.3, "<div id='a'></div>", css="#a{color:red}", js="tl.to('#a',{x:1},0);"),
        Scene("s2", 5.0, 5.0, "<div id='x'></div>", js=s2_js),
    ])


def test_render_plan_isolates_scene_edits(tmp_path):
    r = _render_mod()
    ws = tmp_path
    (ws / "index.html").write_text(_doc())
    a = r.plan(ws, r.FINAL, chunk_min=4)
    assert [c["start"] for c in a["chunks"]] == [0.0, 5.0] and a["total_frames"] == 300
    assert a["chunks"][0]["deps"] == ["region:s1", "s1"]
    (ws / "index.html").write_text(_doc(s2_js="tl.to('#x',{x:2},5);"))
    b = r.plan(ws, r.FINAL, chunk_min=4)
    assert a["chunks"][0]["key"] == b["chunks"][0]["key"]  # untouched scene stays cached
    assert a["chunks"][1]["key"] != b["chunks"][1]["key"]


def test_render_plan_keys_change_with_settings_and_assets(tmp_path):
    r = _render_mod()
    (tmp_path / "index.html").write_text(_doc().replace("vendor/vault3d.js", "vendor/x.js"))
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor" / "x.js").write_text("1")
    (tmp_path / "unreferenced.mp4").write_text("junk")
    k = r.plan(tmp_path, r.FINAL, 4)["chunks"][0]["key"]
    assert r.plan(tmp_path, r.PREVIEW, 4)["chunks"][0]["key"] != k
    (tmp_path / "unreferenced.mp4").write_text("other junk")
    assert r.plan(tmp_path, r.FINAL, 4)["chunks"][0]["key"] == k
    (tmp_path / "vendor" / "x.js").write_text("2")
    assert r.plan(tmp_path, r.FINAL, 4)["chunks"][0]["key"] != k


def test_region_spans_attach_to_their_window():
    r = _render_mod()
    html = _doc().replace("tl.seek(0);", "/*scene:fx spans=0-1*/tl.to('#a',{y:1},0);/*/scene:fx*/\ntl.seek(0);")
    comp = r.parse(html)
    assert comp.deps["region:fx"] == [(0.0, 1.0)]


def test_caption_layer_matches_remotion_page_timing():
    pages = json.loads((PILOT / "artifacts" / "caption_phrases.json").read_text())
    css, html, js = caption_layer(pages, fps=30)
    assert html.count('class="clip ecap"') == len(pages) == js.count("ecapPage(tl,'")
    # page 0: from round(0.1*30)=3 frames; until min(next start 1.8, end 1.1+0.7) → 1.7 s
    w0 = pages[0]["words"]
    start = round(w0[0]["start"] * 30) / 30
    until = min(pages[1]["words"][0]["start"], w0[-1]["end"] + 0.7)
    dur = max(1, round((int(until * 1000) - int(w0[0]["start"] * 1000)) / 1000 * 30)) / 30
    assert f'data-start="{start:.4f}" data-duration="{dur:.4f}"' in html
    assert "/*scene:cap000*/" in js and "#f2c66d" in js


def test_config_matches_approved_decisions():
    cfg = json.loads((KIT / "config" / "production.json").read_text())
    assert cfg["narration"]["voice"] == "bm_george" and cfg["narration"]["speed"] == 0.95
    r = cfg["render"]
    assert (r["width"], r["height"], r["fps"], r["default_resolution"]) == (1920, 1080, 30, "1080p")
    assert r["optional_resolutions"]["1440p"]["width"] == 2560 and "not the default" in r["optional_resolutions"]["1440p"]["status"]
    prod = cfg["production"]
    assert (prod["cadence"]["episodes_per_week_min"], prod["cadence"]["episodes_per_week_max"]) == (2, 3)
    d = prod["duration_minutes"]
    assert (d["target_min"], d["target_max"], d["extended_max"]) == (8, 10, 13) and "filler" in d["rule"]
    assert "logo" in prod["opening"] and "paid" in prod["cost_policy"]


def test_assemble_defaults_to_1080p_and_supports_1440p():
    html = _doc()
    assert 'data-width="1920" data-height="1080"' in html and "zoom" not in html
    qhd = assemble(title="t", duration=10, audio="", vignette=False, resolution="1440p",
                   vault={"shots": [{"start": 0, "end": 10, "dur": 5, "camFrom": [0, 0, 9], "camTo": [0, 0, 8],
                                     "lookAt": [0, 0, 0]}]},
                   scenes=[Scene("s1", 0, 10, "<div></div>")])
    assert 'data-width="2560" data-height="1440"' in qhd
    assert "#root{width:2560px;height:1440px}.clip{zoom:1.3333333333}" in qhd
    assert '"width": 2560, "height": 1440' in qhd  # 3D renders at full 1440p, not upscaled
    draft = assemble(title="t", duration=10, audio="", scenes=[Scene("s1", 0, 10, "<div></div>")], resolution="540p")
    assert 'data-width="960" data-height="540"' in draft and ".clip{zoom:0.5000000000}" in draft
    with pytest.raises(ValueError):
        assemble(title="t", duration=1, scenes=[], resolution="4k")


def test_render_plan_reports_output_size(tmp_path):
    r = _render_mod()
    (tmp_path / "index.html").write_text(_doc())
    assert (r.plan(tmp_path, r.FINAL, 4)["width"], r.plan(tmp_path, r.FINAL, 4)["height"]) == (1920, 1080)
    (tmp_path / "index.html").write_text(assemble(title="t", duration=10, audio="", resolution="1440p",
                                                  scenes=[Scene("s1", 0, 10, "<div></div>")]))
    p = r.plan(tmp_path, r.FINAL, 4)
    assert (p["width"], p["height"]) == (2560, 1440)


def test_quality_standard_is_wired_into_workflow():
    root = Path(__file__).resolve().parents[2]
    std = (root / "epoch-ledger" / "STANDARD.md").read_text()
    for phrase in ("Hard requirements", "Creative principles", "gold", "determinism", "Mouths move only when the character",
                   "no fixed shot lengths or cut quotas"):
        assert phrase in std, phrase
    q = (root / "epoch-ledger" / "QUALITY.md").read_text()
    assert "STANDARD.md" in q and "qc.mjs" in q
    for retired in ("Introducing something does not explain it", "Semantic visual storytelling"):   # no competing rulebooks
        assert retired not in q
    cfg = json.loads((root / "epoch-ledger" / "config" / "production.json").read_text())
    qs = cfg["production"]["quality_standard"]
    assert qs["doc"] == "epoch-ledger/STANDARD.md" and qs["checklist"] == "epoch-ledger/QUALITY.md"
    assert cfg["narration"]["voice"] == "bm_george" and cfg["narration"]["speed"] == 0.95   # machine settings preserved
    for f in ("skills/creative/epoch-ledger.md", ".claude/commands/epoch-ledger.md", "AGENT_GUIDE.md"):
        assert "STANDARD.md" in (root / f).read_text(), f


def test_rig_library_ships_with_helpers():
    root = Path(__file__).resolve().parents[2]
    js = (root / "epoch-ledger" / "kit" / "rig.js").read_text()
    for fn in ("function rpose", "function rwalk", "function ambient", "function rexpress"):
        assert fn in js


def test_component_index_matches_code():
    """COMPONENTS.md must only list symbols that exist (keeps the index trustworthy)."""
    import re
    root = Path(__file__).resolve().parents[2] / "epoch-ledger"
    idx = (root / "COMPONENTS.md").read_text()
    ep = root / "episodes" / "ai-bubble-vs-dot-com"
    checks = {
        root / "kit/rig.py": ["rig_svg", "crowd_look", "PROPS"],
        root / "kit/rig.js": ["rpose", "rwalk", "ambient", "rtalk", "rexpress", "rcycle"],
        ep / "floor.py": ["floor_scene", "place"],
        ep / "railway_sets.py": ["locomotive", "coach", "boxcar", "track", "station_building", "canopy", "derrick"],
        ep / "money_cutaways.py": ["fab", "cloud", "lab", "customers", "iris"],
        ep / "die.py": ["die_svg", "tiles_svg"],
        ep / "js/ai3d.js": ["serverRack", "campus2", "railway2", "diorama", "keyCam"],
        root / "kit/motion.js": ["mCamera", "mReveal", "mWordsAt", "mDrawOn", "mBoil", "mDiagram", "mFocus", "mFlow", "mCount", "mBars", "mAmbient", "mParallax", "mStutter", "mEndScreen"],
        root / "kit/motion.py": ["ktext", "iso_box", "iso_grid", "world_map_svg", "route_path", "endscreen_html", "diagram_node"],
        root / "kit/three_kit.js": ["keyCam", "surface", "flowAlong", "flowField", "shadowFollow"],
    }
    for f, names in checks.items():
        src = f.read_text()
        for n in names:
            assert n in idx, f"{n} missing from COMPONENTS.md"
            assert re.search(rf"\b{re.escape(n)}\b", src), f"{n} not found in {f.name}"


def test_motion_craft_is_discoverable():
    root = Path(__file__).resolve().parents[2]
    for f in ("AGENT_GUIDE.md", "skills/INDEX.md", "skills/creative/epoch-ledger.md", ".claude/commands/epoch-ledger.md", "epoch-ledger/STANDARD.md"):
        assert "motion-craft" in (root / f).read_text() or "motion_craft" in (root / f).read_text(), f
    assert (root / ".claude/skills/epoch-ledger-motion-craft/SKILL.md").exists()
    cfg = json.loads((root / "epoch-ledger/config/production.json").read_text())
    assert cfg["production"]["motion_language"]["guidelines_flexible"]["one_third_rule"] == "guideline"


def test_assets_digest_follows_nested_references(tmp_path):
    r = _render_mod()
    (tmp_path / "index.html").write_text(_doc().replace("vendor/vault3d.js", "vendor/style.css"))
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor" / "style.css").write_text("@font-face{src:url(face.woff2)}")
    (tmp_path / "vendor" / "face.woff2").write_bytes(b"1")
    (tmp_path / "vendor" / "other.woff2").write_bytes(b"1")        # not referenced by anyone
    k = r.plan(tmp_path, r.FINAL, 4)["chunks"][0]["key"]
    (tmp_path / "vendor" / "other.woff2").write_bytes(b"2")
    assert r.plan(tmp_path, r.FINAL, 4)["chunks"][0]["key"] == k   # unreferenced file: cache kept
    (tmp_path / "vendor" / "face.woff2").write_bytes(b"2")
    assert r.plan(tmp_path, r.FINAL, 4)["chunks"][0]["key"] != k   # font named only inside the CSS: invalidated


def test_render_preflight_clears_stale_and_orphaned_locks(tmp_path):
    r = _render_mod()
    locks = tmp_path / "locks"
    locks.mkdir()
    dead = subprocess.Popen(["true"])
    dead.wait()
    (locks / "render.lock").write_text(json.dumps({"pid": dead.pid, "project": str(tmp_path)}))
    (locks / f"render.lock.owner-{dead.pid}-abc").write_text("")
    notes = r.preflight_lock(tmp_path, lock_dir=locks)
    assert not (locks / "render.lock").exists() and not list(locks.glob("render.lock.owner-*")), notes
    # an orphaned "hyperframes" process (parent died → reparented) holding the lock for this workspace is stopped
    out = subprocess.run(["bash", "-c", "(exec -a hyperframes-render sleep 60) >/dev/null 2>&1 & echo $!"], capture_output=True, text=True)
    pid = int(out.stdout.strip())
    try:
        proc = r._proc(pid)
        if proc is None or proc[0] != 1:
            pytest.skip("no /proc or orphans are not reparented to pid 1 here")
        (locks / "render.lock").write_text(json.dumps({"pid": pid, "project": str(tmp_path)}))
        r.preflight_lock(tmp_path / "other", lock_dir=locks)                 # another workspace: left alone
        assert r._alive(pid) and (locks / "render.lock").exists()
        notes = r.preflight_lock(tmp_path, lock_dir=locks)
        assert not r._alive(pid) and not (locks / "render.lock").exists(), notes
    finally:
        try:
            os.kill(pid, 9)
        except ProcessLookupError:
            pass


def test_render_watchdog_kills_hung_step(tmp_path):
    r = _render_mod()
    t = time.time()
    assert r._run_guarded(["bash", "-c", "sleep 30 & sleep 30"], tmp_path, timeout=1) == 124
    assert time.time() - t < 15
