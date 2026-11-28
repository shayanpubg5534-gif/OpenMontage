"""Character lab P13 (experimental, opt-in): the creative treatment and storyboard key frames for the P12 mortgage
passage (static checks and small builds; no rendering). Creative quality is judged on the key frames themselves
(epoch-ledger/charlab/evidence/p13/), not here.

- the treatment passes kit.treatment with no errors or warnings, and the storyboard gate blocks animation until approval
- the securitisation accuracy notes keep pooling, issuance, distribution and loss allocation distinct
- the kitchen world is built from existing set components only, in two lights of the same room
- the 3D scene and the two new formats are procedural and build timed scenes
- P12 is untouched: the identity extension (one declared wardrobe change) lives in this process only
"""
import copy
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P13 = REPO / "epoch-ledger/charlab/p13"
sys.path[:0] = [str(P13), str(REPO / "epoch-ledger/charlab/p12"), str(REPO / "epoch-ledger")]
from kit import treatment  # noqa: E402

T = json.loads((P13 / "treatment.json").read_text())


def test_treatment_is_complete_and_gated():
    r = treatment.review(T, P13)
    assert r == {"errors": [], "warnings": []}
    heroes = [s for s in T["sequences"] if s["hero"]]
    assert 3 <= len(heroes) <= 5 and all(s["storyboard"] for s in heroes)
    gate = treatment.review(T, P13, gate="motion")["errors"]
    assert gate and all("not approved" in e for e in gate)               # frames exist; only approval is missing
    for s in T["sequences"]:
        lit = next(c for c in s["concepts"] if c["kind"] == "literal")
        assert lit["verdict"] == "rejected"                              # the P12 literal picture is never the default


def test_securitisation_is_shown_accurately():
    seq = {s["id"]: s for s in T["sequences"]}
    acc = " ".join(" ".join(s.get("accuracy", [])) for s in T["sequences"]).lower()
    assert "pool is not the security" in acc and "senior first" in acc and "most junior tranche first" in acc
    assert "subordination" in acc and "downgraded" in acc and "repurchase" in acc   # lenders kept some risk
    assert seq["q7"]["hero"] and "senior floors stay dry" in seq["q7"]["concepts"][1]["idea"]


def test_kitchen_is_one_room_in_two_lights_from_existing_components():
    spec = importlib.util.spec_from_file_location("p13sets", P13 / "sets.py"); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
    env = (REPO / "epoch-ledger/charlab/motion/env.js").read_text()
    known = set(re.findall(r"^    (\w+)\(it, g\)", env, re.M))
    assert {i["type"] for i in S.ITEMS} <= known
    assert set(S.LIGHT) == {"dusk", "night"} and "practicals" in S.LIGHT["dusk"]
    for v in ("dusk", "night"):
        s = json.loads((REPO / f"epoch-ledger/charlab/motion/sets/p13_kitchen_{v}.json").read_text())
        assert [i["id"] for i in s["items"]] == [i["id"] for i in S.ITEMS]     # the same room: only light and dressing change


def test_tranche_scene_is_procedural_and_follows_the_waterfall():
    js = (P13 / "scenes/tranches.js").read_text()
    assert "GLTFLoader" not in js and ".glb" not in js
    assert "['equity', 1" in js and "['senior', 5" in js                     # equity at the bottom, senior on top
    assert "E.mode === 1 && E.flood > 0" in js and "3 * FH" in js            # losses only rise through equity + mezzanine


def test_formats_build_timed_scenes():
    import formats as F
    a = F.pool_map("t", 1.0, 2.0, kicker="k", pool_label=("THE POOL", "a trust"), lender_label="lender", family_label="their loan", t_lines=1.1, t_pool=1.5)
    b = F.frame_overlay("u", 3.0, 1.0, src="shots/x.png", kicker="k", legend=[("#fff", "Senior")], callouts=[("x", (500, 500), (600, 600), 3.1, "#c9963a")])
    assert (a.start, a.duration, b.start) == (1.0, 2.0, 3.0) and "their loan" in a.html and "mDrawOn" in a.js and "<img" in b.html


def test_p12_cast_is_untouched_and_the_extension_is_declared():
    import cast as CAST
    before = copy.deepcopy(CAST.CAST)
    src = (P13 / "keyframes.py").read_text()
    assert "CAST.CAST = copy.deepcopy(CAST.CAST)" in src and "WARDROBE_CHANGES" in src
    assert "body/Paper" not in CAST.CAST["wife"]["bodies"] and CAST.CAST == before
    faces = re.findall(r'"(Calm|Serious|Smile|Blank|Tired|Solemn|Concerned|Explaining|Smile Big|Smile LOL)"', src)
    assert faces and not {"Explaining", "Smile Big", "Smile LOL"} & set(faces)   # no talking faces (voice-over standard)


def test_devices_are_logged():
    used = json.loads((REPO / "epoch-ledger/direction/used_devices.json").read_text())
    assert used["signatures"]["p13-storyboard"] == T["signature"]
