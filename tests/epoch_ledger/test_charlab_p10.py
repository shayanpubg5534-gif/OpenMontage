"""Character lab P10 (experimental, opt-in): static checks plus one small rig build (node), no rendering.

- P10 tools exist and compile; plate demos are single-frame stills with a locked camera and no actors (no speech)
- the cut-out rig builds clean joints by construction: pieces and cuts are masks (flattened, no hairline), joint discs are
  drawn beneath everything, every rig spec is well formed
- the performance uses no open-mouth "talking" faces (narration standard); the narrated sequence is voice-over only
- hf_sequence's prerendered-video shots are opt-in (other shot types unchanged); shot cuts agree with prepare.py
- restricted raw assets are not tracked; production files and P9 are untouched
"""
import ast
import importlib.util
import json
import py_compile
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P10 = REPO / "epoch-ledger/charlab/p10"
SPEECH_FACES = {"Talking", "Explaining", "Loving Grin 1", "Loving Grin 2", "Concerned", "Old", "Screaming", "Shout", "Awe",
                "Smile Big", "Smile LOL", "Smile Teeth Gap", "Eating Happy"}


def test_tools_compile_and_exist():
    for f in ("prepare.py", "survey.py"):
        py_compile.compile(str(P10 / f), doraise=True)
    for f in ("compose.mjs", "render_shot.mjs", "rig.mjs", "rig_test.mjs", "grid.mjs", "wardrobe2.mjs", "run_p10.sh", "sheets.sh", "points.json"):
        assert (P10 / f).exists(), f
    py_compile.compile(str(REPO / "epoch-ledger/charlab/sequences/p10_test.py"), doraise=True)


def test_plate_demos_are_static_stills_without_actors():
    for k in "ABC":
        d = json.loads((REPO / f"epoch-ledger/charlab/motion/demos/p10_cam{k}.json").read_text())
        assert d["actors"] == {} and d["look"] == "cinematic" and d.get("cinematicVariant") == "p4"
        assert round(d["duration"] * 30) == 1 and len(d["camera"]) == 1          # one frame, one locked camera


def test_rig_specs_well_formed():
    for f in (P10 / "rigs").glob("*.json"):
        for p in json.loads(f.read_text())["pieces"]:
            assert p["z"] in ("under", "over") and len(p["pivot"]) == 2
            assert len(p["clip"]) >= 3 and len(p["cut"]) >= 3
            if "disc" in p: assert p["disc"]["r"] > 0


def test_rig_builds_masks_not_clips(tmp_path):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g id="character"><g id="BODY"><path d="M10 10H90V90H10Z" fill="#2f3b52"/></g>'
           '<g id="Head"><circle cx="50" cy="20" r="8"/></g></g></svg>')
    spec = [{"id": "fore", "z": "over", "pivot": [50, 50], "disc": {"r": 6, "fill": "#2f3b52"},
             "cut": [[50, 0], [100, 0], [100, 100], [50, 100]], "clip": [[49, 0], [100, 0], [100, 100], [49, 100]]}]
    js = (f"import {{ rigSVG }} from '{(P10 / 'rig.mjs').as_posix()}';"
          f"process.stdout.write(rigSVG({json.dumps(svg)}, {json.dumps(spec)}, {{ id: 't' }}));")
    out = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, check=True).stdout
    assert 'data-joint="fore"' in out and 'data-joint="body"' in out and 'data-pivot="50,50"' in out
    assert "clip-path" not in out and 'mask="url(#t_cp_fore)"' in out and 'mask="url(#t_m_body)"' in out
    assert out.index('class="rig-disc"') < out.index('data-joint="body"')      # the disc lies beneath the body and the piece


def test_no_speech_faces_in_the_performance():
    tree = ast.parse((P10 / "prepare.py").read_text())
    strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert not strings & SPEECH_FACES
    assert {"Calm", "Smile", "Serious", "Eyes Closed"} <= strings


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path); m = importlib.util.module_from_spec(spec)
    import sys; sys.path.insert(0, str(REPO / "epoch-ledger")); spec.loader.exec_module(m); return m


def test_sequence_is_voice_over_with_video_shots():
    seq = _load(REPO / "epoch-ledger/charlab/sequences/p10_test.py")
    assert all("video" in s and "demo" not in s for s in seq.SHOTS)
    assert abs(sum(s["duration"] for s in seq.SHOTS) - seq.DURATION) < 1e-6
    src = (P10 / "prepare.py").read_text()                                    # the shots are cut where the sequence cuts
    assert f"CUTS = [0.0, {seq.CUTS[1]}, {seq.CUTS[2]}, DURATION]" in src and f"DURATION = {seq.DURATION}" in src
    assert "speech" not in (REPO / "epoch-ledger/charlab/sequences/p10_test.py").read_text().lower().replace("speech_", "")


def test_hf_sequence_video_shots_are_opt_in():
    src = (REPO / "epoch-ledger/charlab/hf_sequence.py").read_text()
    assert 'if S.get("video"):' in src and 'shot = json.loads((REPO / S["demo"]).read_text())' in src


def test_restricted_assets_not_tracked_and_production_untouched():
    files = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    assert not any(f.endswith(".fig") for f in files)
    assert not any(f.lower().endswith((".fbx", ".glb", ".blend")) and "businessman" in f.lower() for f in files)
    assert not any(f.startswith((".runtime/", "projects/charlab_p10/")) for f in files)
    for f in ("epoch-ledger/kit/rig4.js", "epoch-ledger/scripts/render.py", "epoch-ledger/charlab/shot_render.mjs", "epoch-ledger/charlab/p9/animate.mjs"):
        assert "P10" not in (REPO / f).read_text() and "p10/" not in (REPO / f).read_text()
