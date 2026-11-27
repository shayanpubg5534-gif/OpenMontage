"""Character lab P4/P5 (experimental, opt-in): fast static checks.

- the continuous-session shot renderer's fingerprint is stable and changes when any input of the shot changes
  (so the shot cache can never serve a stale shot)
- the quality profiles and the opt-in cinematic variant exist; approved M4/M5 demos do not opt into anything new
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CHARLAB = REPO / "epoch-ledger/charlab"
THREE = ".runtime/charlab/three/r0.186.1"
CHARS = ".runtime/charlab/out_p3"

needs_runtime = pytest.mark.skipif(not (REPO / THREE).exists() or not (REPO / CHARS / "snow_cv.glb").exists() or shutil.which("node") is None,
                                   reason="charlab runtime assets (.runtime) not present")


def fingerprint(demo_rel: str) -> dict:
    r = subprocess.run(["node", str(CHARLAB / "shot_render.mjs"), "--demo", demo_rel, "--chars", CHARS, "--three", THREE,
                        "--quality", "cin_balanced", "--fingerprint-only"], cwd=REPO, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@needs_runtime
def test_shot_fingerprint_stable_and_sensitive(tmp_path):
    demo = "epoch-ledger/charlab/motion/demos/p5_test.json"
    a, b = fingerprint(demo), fingerprint(demo)
    assert a["fingerprint"] == b["fingerprint"]
    ins = set(a["inputs"])
    # everything the shot depends on is hashed: demo, set, character, lip-sync track, runtime code, the renderer itself
    for must in (demo, "epoch-ledger/charlab/motion/sets/bank_office.json", f"{CHARS}/snow_cv.glb",
                 "projects/charlab_p3/dialogue_snow/visemes.json", "epoch-ledger/charlab/motion/runtime.js",
                 "epoch-ledger/charlab/motion/envcache.js", "epoch-ledger/charlab/shot_render.mjs"):
        assert must in ins, must
    # a revision of the shot (one camera key) changes the fingerprint
    d = json.loads((REPO / demo).read_text()); d["camera"][0]["fov"] += 1
    rev = REPO / "epoch-ledger/charlab/motion/demos/_test_p5_rev.json"
    try:
        rev.write_text(json.dumps(d)); c = fingerprint(str(rev.relative_to(REPO)))
    finally:
        rev.unlink(missing_ok=True)
    assert c["fingerprint"] != a["fingerprint"]


def test_profiles_and_variants_are_opt_in():
    rt = (CHARLAB / "motion/runtime.js").read_text()
    for p in ("cin_fast:", "cin_balanced:", "cin_cinematic:", "standard:", "balanced:", "lean:"):
        assert p in rt, p
    bank = json.loads((CHARLAB / "motion/sets/bank_office.json").read_text())
    assert "p4" in bank.get("cinematic_variants", {})
    # approved baselines keep their looks and never opt into the P4/P5 options
    for demo in ("m5_bank.json", "story_loan.json", "m5_bakery.json"):
        d = json.loads((CHARLAB / "motion/demos" / demo).read_text())
        assert d.get("look", "cel") in ("cel", "editorial")
        for k in ("cinematicVariant", "dofScale", "exposure"):
            assert k not in d, (demo, k)


def test_hf_sequence_prerender_is_opt_in():
    src = (CHARLAB / "hf_sequence.py").read_text()
    assert '"--prerender", action="store_true"' in src      # off unless asked: the live-canvas path stays the default
