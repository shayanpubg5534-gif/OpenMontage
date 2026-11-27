"""Character lab P9 (experimental 2.5D animation test): static checks only (no rendering, no third-party files needed).

- P9 tools compile; the P9 demos are set plates with no actors (no speech tracks, no lip sync)
- the performance timeline uses no open-mouth "talking" faces (narration standard: characters never speak to narration)
- blinks are irregular; arm beats stay within the cut-out limit
- restricted raw assets (Fab files, the Open Peeps .fig) are not tracked; production files are untouched
"""
import ast
import json
import py_compile
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P9 = REPO / "epoch-ledger/charlab/p9"
SPEECH_FACES = {"Talking", "Explaining", "Loving Grin 1", "Loving Grin 2", "Concerned", "Old", "Screaming", "Shout", "Awe"}


def lit(node):
    """literal_eval that also accepts dict(k=v, ...) calls"""
    if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "dict":
        return {a.arg: lit(a.value) for a in node.keywords}
    return ast.literal_eval(node)


def shots():
    """the `shots` dict in prepare.py, with character() calls replaced by their face lists"""
    tree = ast.parse((P9 / "prepare.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "shots":
            out = {}
            for k, v in zip(node.value.keys, node.value.values):
                kw = {a.arg: a.value for a in v.keywords}
                chars = {}
                items = [(ast.literal_eval(ck), cv) for ck, cv in zip(kw["chars"].keys, kw["chars"].values)]   # chars={"banker": dict(...)}
                for ck, cv in items:
                    ckw = {a.arg: a.value for a in cv.keywords}
                    call = ckw["svg"]
                    chars[ck] = dict(pose=ast.literal_eval(call.args[2]), embedded=ast.literal_eval(call.args[3]),
                                           faces=ast.literal_eval(ckw["faces"]), arm=lit(ckw["arm"]),
                                           duration=ast.literal_eval(kw["duration"]))
                out[ast.literal_eval(k)] = chars
            return out
    raise AssertionError("shots not found")


def test_tools_compile_and_exist():
    for f in ("prepare.py", "measure.py"):
        py_compile.compile(str(P9 / f), doraise=True)
    for f in ("animate.mjs", "cam_track.mjs", "wardrobe.mjs", "sheet.mjs", "run_p9.sh", "paint_filter.txt"):
        assert (P9 / f).exists(), f
    for k in (1, 2):
        pts = json.loads((P9 / f"points_shot{k}.json").read_text())
        assert {"banker_feet", "banker_head", "client_feet", "client_head", "window"} <= set(pts)
        for c in ("banker", "client"):
            assert pts[c + "_feet"][1] == 0 and pts[c + "_head"][1] > 1.5          # standing on the floor, adult height


def test_demos_are_plates_without_actors():
    for k in (1, 2):
        d = json.loads((REPO / f"epoch-ledger/charlab/motion/demos/p9_shot{k}.json").read_text())
        assert d["actors"] == {} and d["look"] == "cinematic" and d.get("cinematicVariant") == "p4"


def test_no_speech_faces_and_blinks_present():
    S = shots()
    assert set(S) == {1, 2}
    for chars in S.values():
        for c in chars.values():
            used = {f for _, f in c["faces"]}
            assert not used & SPEECH_FACES                                   # narration is voice-over: nobody talks
            assert used <= set(c["embedded"]) and "Eyes Closed" in c["embedded"]
            assert all(0 <= t < c["duration"] for t, _ in c["faces"])
            if c["arm"]:
                assert all(abs(deg) <= 5.0 for _, deg in c["arm"]["beats"])  # cut-out seam limit


def test_blinks_are_irregular():
    import random
    src = (P9 / "prepare.py").read_text()
    fn = ast.parse(src).body
    mod = ast.Module(body=[n for n in fn if isinstance(n, ast.FunctionDef) and n.name == "blinks"], type_ignores=[])
    ns = {"random": random}
    exec(compile(mod, "prepare_blinks", "exec"), ns)
    b = ns["blinks"](11, 0, 30)
    gaps = [b2[0] - b1[0] for b1, b2 in zip(b, b[1:])]
    assert len(b) >= 6 and len({round(g, 2) for g in gaps}) > 3 and all(0.09 <= e - s <= 0.14 for s, e in b)


def test_restricted_assets_not_tracked_and_production_untouched():
    files = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    assert not any(f.endswith(".fig") for f in files)
    assert not any(f.lower().endswith((".fbx", ".glb", ".blend")) and "businessman" in f.lower() for f in files)
    for f in ("epoch-ledger/kit/rig4.js", "epoch-ledger/scripts/render.py", "epoch-ledger/charlab/shot_render.mjs"):
        assert "P9" not in (REPO / f).read_text() and "p9/" not in (REPO / f).read_text()
