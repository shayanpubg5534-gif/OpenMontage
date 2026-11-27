"""Character lab P6 (experimental, opt-in): static checks only (no Blender, no rendering).

- the P6 prototype tools exist and compile; the three variants are ordered subtle → balanced → stronger, and the
  "raw" reference applies no stylisation
- the bank still demo is a single static prototype with no speech (narration standard) and opts into keepMaterials;
  the runtime keeps its default prop shading for every demo that does not opt in
- production files are untouched by P6 (Rig v4, render.py)
"""
import ast
import json
import py_compile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P6 = REPO / "epoch-ledger/charlab/p6"


def variants():
    src = (P6 / "build_p6.py").read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "VARIANTS" for t in node.targets):
            out = {}
            for k, v in zip(node.value.keys, node.value.values):
                kw = {a.arg: a.value for a in v.keywords}
                out[k.value] = {n: (ast.literal_eval(kw[n]) if n not in ("morphs",) else getattr(kw[n], "id", None) or ast.literal_eval(kw[n]))
                                for n in ("smooth", "accent", "head", "morphs")}
            return out
    raise AssertionError("VARIANTS not found")


def test_p6_tools_compile():
    for f in ("build_p6.py", "render_p6.py", "ortho_p6.py", "export_glb.py", "make_sheets.py"):
        py_compile.compile(str(P6 / f), doraise=True)
    assert (P6 / "still.mjs").exists()


def test_variants_are_ordered_and_raw_is_unstylised():
    V = variants()
    assert set(V) == {"raw", "A", "B", "C"}
    assert V["raw"]["accent"] == 0 and V["raw"]["smooth"] == 0 and V["raw"]["head"] == 1.0 and V["raw"]["morphs"] == {}
    assert V["A"]["accent"] < V["B"]["accent"] < V["C"]["accent"]
    assert V["A"]["smooth"] < V["B"]["smooth"] < V["C"]["smooth"]
    assert 1.0 >= V["A"]["head"] > V["B"]["head"] > V["C"]["head"] >= 0.9     # modest head scaling only (no doll heads)


def test_no_shading_only_or_particle_shortcuts():
    src = (P6 / "build_p6.py").read_text()
    assert "ParticleSystem" not in src and "particle_system" not in src          # mesh hair only
    for key in ("laplace(", "push_out(", "subdivide("):                         # stylisation and wardrobe are geometric
        assert key in src


def test_bank_still_demo_is_static_and_silent():
    d = json.loads((REPO / "epoch-ledger/charlab/motion/demos/p6_bank_still.json").read_text())
    assert d["look"] == "cinematic" and d.get("cinematicVariant") == "p4"
    assert d["actors"] == {}                                                     # no speech tracks, no lip sync
    assert d["props"]["p6"]["type"] == "glb" and d["props"]["p6"]["keepMaterials"] is True


def test_runtime_prop_shading_default_unchanged():
    rt = (REPO / "epoch-ledger/charlab/motion/runtime.js").read_text()
    assert "if (!spec.keepMaterials) root.traverse(o => { if (o.isMesh) o.material = stage.propMaterial(" in rt
    others = [p for p in (REPO / "epoch-ledger/charlab/motion/demos").glob("*.json") if p.name != "p6_bank_still.json"]
    assert not any('"keepMaterials"' in p.read_text() for p in others)


def test_production_untouched():
    for f in ("epoch-ledger/kit/rig4.js", "epoch-ledger/scripts/render.py"):
        assert "P6" not in (REPO / f).read_text()
