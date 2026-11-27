"""Character lab P11 (experimental, opt-in): the narration-to-visual planning method and the P11 sequence (no rendering).

- visual_map: clauses come from the narrator's punctuation; events resolve to real word times; the checker rejects an
  un-shown clause, an idea shown only far from its word, an out-of-window offset, gaps between shots and shots that
  introduce nothing
- the P11 map passes; the same checker on P10-as-delivered reports the ideas P10 left to the captions
- the sequence uses P10's narration unchanged (controlled comparison) and its shots tile the film
- narration standard (no talking faces), fictional banknotes and procedural 3D only, P10 behaviour preserved,
  restricted assets untracked
"""
import ast
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P11 = REPO / "epoch-ledger/charlab/p11"
sys.path.insert(0, str(P11))
import visual_map as VM  # noqa: E402

W = [{"word": w, "start": s, "end": s + .3} for w, s in
     [("The", 0.0), ("vault", 0.4), ("stays", 0.8), ("shut,", 1.2), ("and", 2.0), ("cash", 2.4), ("stays.", 2.8)]]


def base_map():
    return {"duration": 4.0, "sync": {}, "shots": [
        {"id": "A", "t0": 0.0, "t1": 2.0, "introduces": ["context"], "purpose": "the vault"},
        {"id": "B", "t0": 2.0, "t1": 4.0, "introduces": ["information"], "purpose": "the cash"}],
        "concepts": [{"id": "k1", "idea": "vault shut", "anchor": {"word": "vault"}}, {"id": "k2", "idea": "cash stays", "anchor": {"word": "cash"}}],
        "events": [{"id": "a", "anchor": {"word": "vault"}, "offset": -0.1, "shot": "A", "medium": "3d", "what": "vault", "depicts": ["k1"]},
                   {"id": "b", "anchor": {"word": "cash"}, "offset": 0.0, "shot": "B", "medium": "3d", "what": "cash", "depicts": ["k2"]}]}


def test_clauses_and_resolution():
    cl = VM.clauses(W)
    assert [c["text"] for c in cl] == ["The vault stays shut,", "and cash stays."]
    r = VM.resolve(base_map(), W)
    assert [(e["id"], e["t"], e["clause"]) for e in r["events"]] == [("a", 0.3, "c1"), ("b", 2.4, "c2")]
    assert VM.check(base_map(), W)["errors"] == []


def test_checker_rejects_bad_maps():
    m = base_map(); m["events"] = m["events"][:1]                               # the second clause is not shown
    errs = " ".join(VM.check(m, W)["errors"])
    assert "c2" in errs and "k2" in errs
    m = base_map(); m["events"][1]["depicts"] = []                                # the cash shown only 0.7 s after "cash"
    m["events"].append({"id": "late", "anchor": {"word": "stays", "n": 2}, "offset": 0.3, "shot": "B", "medium": "graphic", "what": "x", "depicts": ["k2"]})
    assert any("k2" in e and "away" in e for e in VM.check(m, W)["errors"])
    m = base_map(); m["events"][0]["offset"] = -0.9
    assert any("offset" in e for e in VM.check(m, W)["errors"])
    m = base_map(); m["shots"][1]["t0"] = 2.2
    assert any("contiguous" in e for e in VM.check(m, W)["errors"])
    m = base_map(); m["shots"][0]["introduces"] = []
    assert any("introduces" in e for e in VM.check(m, W)["errors"])


def test_p11_map_passes_and_p10_as_delivered_does_not():
    m11 = json.loads((P11 / "map_p11.json").read_text()); words = VM.load_words(REPO / m11["words"])
    r = VM.check(m11, words); assert r["errors"] == [] and r["warnings"] == []
    m10 = json.loads((P11 / "map_p10_as_delivered.json").read_text())
    errs = " ".join(VM.check(m10, words)["errors"])
    for k in ("k3", "k4", "k5"):                                                  # amount, vault, cash: captions only in P10
        assert k in errs


def _seq():
    sys.path.insert(0, str(REPO / "epoch-ledger"))
    spec = importlib.util.spec_from_file_location("p11seq", REPO / "epoch-ledger/charlab/sequences/p11_test.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_sequence_is_a_controlled_comparison():
    seq = _seq()
    p10 = (REPO / "epoch-ledger/charlab/sequences/p10_test.py").read_text()
    assert f'EPISODE = "{seq.EPISODE}"' in p10 and f'NARRATION_WAV = "{seq.NARRATION_WAV}"' in p10     # same narration as P10
    t = 0.0
    for s in seq.SHOTS:
        assert "video" in s and abs(s["start"] - t) < 1e-6; t += s["duration"]
    assert abs(t - seq.DURATION) < 1e-6 and len(seq.scenes({})) == 5


def test_narration_standard_and_assets():
    tree = ast.parse((P11 / "prepare.py").read_text())
    strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert not strings & {"Talking", "Explaining", "Loving Grin 1", "Loving Grin 2", "Screaming", "Shout", "Awe", "Smile Big", "Smile LOL"}
    v = (P11 / "vault3d.mjs").read_text()
    assert "GLTFLoader" not in v and ".glb" not in v and "LEDGER RESERVE NOTE" in v and "not real currency" in v


def test_p10_preserved():
    c = (REPO / "epoch-ledger/charlab/p10/compose.mjs").read_text()
    assert "amp = 6.5" in c                                                         # two-element nods behave as in P10
    import subprocess
    files = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    assert not any(f.endswith(".fig") or f.startswith((".runtime/", "projects/charlab_p11/")) for f in files)
