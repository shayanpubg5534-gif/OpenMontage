"""Character lab P12 (experimental, opt-in): character continuity, the visual-format library and the validation passage
(static checks and small builds; no rendering).

- cast: each character only wears its listed bodies; recolouring is by role from the identity; a variant whose role
  colour differs from the identity is reported
- the P12 map (a new subject) passes the P11 checker with no errors or warnings and uses varied media
- every format in visuals.py builds a timed scene; the sequence tiles the film with video shots and full-screen formats
- 3D scenes are procedural (no third-party models); faces are never talking faces; P10/P11 defaults are preserved
"""
import ast
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P12 = REPO / "epoch-ledger/charlab/p12"
sys.path.insert(0, str(P12)); sys.path.insert(0, str(REPO / "epoch-ledger/charlab/p11")); sys.path.insert(0, str(REPO / "epoch-ledger"))
import cast as CAST  # noqa: E402
import visual_map as VM  # noqa: E402
import visuals as V  # noqa: E402

SVG = ('<svg viewBox="0 0 10 10"><g id="character"><g id="BODY" data-symbol="body/Test"><path d="M0 0" fill="#111111"/><path d="M1 1" fill="#222222"/>'
       '<path d="M2 2" fill="#1e1b19"/></g><g id="HEAD" data-symbol="head/X"><path d="M3 3" fill="#1e1b19"/></g></g></svg>')


def test_identities_only_use_their_bodies_and_known_roles():
    for cid, ident in CAST.CAST.items():
        for b in ident["bodies"]:
            assert b in CAST.BODIES, (cid, b)
            for role in CAST.BODIES[b].values():
                assert role in ("skin", "keep") or role in ident["wardrobe"] or role in ("shoes", "outer", "bottom"), (cid, b, role)


def test_dress_recolours_by_role_and_check_reports_mismatch():
    CAST.BODIES["body/Test"] = {0: "skin", 1: "top"}; CAST.KIND["body/Test"] = "bust"
    CAST.CAST["probe"] = dict(head={"HEAD": "head/X"}, skin="#aa7755", hair="#1e1b19", wardrobe={"top": "#334455"}, bodies=["body/Test"])
    try:
        out = CAST.dress(SVG, "body/Test", CAST.CAST["probe"])
        assert 'fill="#aa7755"' in out and 'fill="#334455"' in out and out.count('fill="#1e1b19"') == 2   # ink untouched
        assert CAST.check_variant(out, "probe", "body/Test") == []
        bad = out.replace('fill="#334455"', 'fill="#999999"')
        assert any("top" in e for e in CAST.check_variant(bad, "probe", "body/Test"))
    finally:
        CAST.BODIES.pop("body/Test"); CAST.KIND.pop("body/Test"); CAST.CAST.pop("probe")


def test_p12_map_passes_and_is_varied():
    m = json.loads((P12 / "map_p12.json").read_text()); words = VM.load_words(REPO / m["words"])
    r = VM.check(m, words)
    assert r["errors"] == [] and r["warnings"] == []
    assert len(m["concepts"]) >= 12 and len({s["medium"] for s in m["shots"]}) >= 4
    assert {e["medium"] for e in m["events"]} >= {"cut", "graphic", "character-action", "prop", "insert", "3d", "diagram"}


def test_formats_build_timed_scenes():
    scenes = [V.env_card("a", 0, 2, top="MAY", big="2006", box=(0, 0, 170, 230), transform="none", t_in=.5),
              V.document("b", 0, 3, title="T", fields=[("k", "v")], box=(0, 0, 600, 800), transform="none", sign_t=1,
                         bar={"label": "x", "frac": .9, "t_fill": 1, "t_left": 1.5, "left_label": "little left"}),
              V.world_map("c", 0, 4, origin=("US", -74, 40.7), buyers=[("London", -.1, 51.5)], title="t", t_routes=1, t_buy=1.5, t_flow=2,
                          t_dry=3, panel={"label": "v", "t_before": 2.5, "t_after": 3.2}),
              V.line_chart("d", 0, 2, series=[(2000, 100), (2006, 180), (2010, 140)], turn=2006, t_fall=1, title="t", note="n", source="s"),
              V.newspaper("e", 0, 5, masthead="M", date="D", headline="A files for bankruptcy", deck="d", emph="bankruptcy", t_head=2, t_emph=3,
                          box=(0, 0, 800, 900), transform="none", timeline={"marks": [("2006", 0)], "to_frac": .9, "to_label": "Sep", "t_move": 1}),
              V.stamp("f", 0, 2, text="SOLD", box=(0, 0, 300, 90), rotate=-5, t_in=1),
              V.label("g", 0, 2, kicker="k", text="t", box=(0, 0, 400), t_in=1)]
    for s in scenes:
        assert s.duration > 0 and s.html and s.js.count("tl.") >= 1


def _seq():
    spec = importlib.util.spec_from_file_location("p12seq", REPO / "epoch-ledger/charlab/sequences/p12_test.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_sequence_tiles_the_film():
    seq = _seq(); mp = {s["id"]: s for s in json.loads((P12 / "map_p12.json").read_text())["shots"]}
    video = {s["id"] for s in seq.SHOTS}
    assert video | {"S4", "S5", "S7"} == set(mp) and not video & {"S4", "S5", "S7"}     # diagrams are full-screen formats
    assert len(seq.scenes({})) >= 9 and seq.EPISODE != "projects/charlab_p10/story"          # a new subject, a new narration


def test_procedural_3d_and_narration_standard():
    for f in (P12 / "scenes").glob("*.js"):
        src = f.read_text(); assert "GLTFLoader" not in src and ".glb" not in src
    tree = ast.parse((P12 / "prepare.py").read_text())
    strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert not strings & {"Talking", "Explaining", "Loving Grin 1", "Loving Grin 2", "Screaming", "Shout", "Awe", "Smile Big", "Smile LOL"}


def test_p10_p11_defaults_preserved():
    c = (REPO / "epoch-ledger/charlab/p10/compose.mjs").read_text()
    assert "shade: '#2a170d'" in c and "if (L.match)" in c                                  # opt-in: default lighting unchanged
    assert (REPO / "epoch-ledger/charlab/p11/vault3d.mjs").exists() and (REPO / "epoch-ledger/charlab/p11/map_p11.json").exists()
