"""STANDARD §3B (viewer comprehension and visual pacing): the standard and its routing, kit/pacing.py, the relaxed
narration-to-visual checker (semantic coverage, held compositions), the treatment's compression warning, the pacing
quality gate, and the regression: the P13 pilot as delivered must be flagged. These checks are diagnostics; the film is
judged by watching it at normal speed.
"""
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / "epoch-ledger"), str(REPO / "epoch-ledger/charlab/p11")]
from kit import pacing as PC, treatment as TR  # noqa: E402
import visual_map as VM  # noqa: E402

R = REPO / "epoch-ledger/charlab/p13r"


def plan(shots, events=(), text=(), dur=None):
    return {"duration": dur or max(s["t1"] for s in shots), "shots": [{**s, "pace_given": True} for s in shots],
            "events": [{"held": False, **e} for e in events], "text": list(text), "words": []}


def test_standard_is_written_and_routed():
    std = (REPO / "epoch-ledger/STANDARD.md").read_text()
    for k in ("## 3B. Viewer comprehension and visual pacing", "Semantic coverage", "Cognitive load is the whole picture", "Preserve visual richness",
              "Pacing adapts to the sequence", "Judged at normal speed", "not proof of understanding"):
        assert k in std, k
    assert "no fixed shot lengths or cut quotas" in std                       # §3 still holds: guidelines, not quotas
    q = (REPO / "epoch-ledger/QUALITY.md").read_text()
    assert "## First viewing" in q and "kit.pacing" in q
    assert "6A. Pacing for a first viewing" in (REPO / "skills/creative/epoch-ledger-director.md").read_text()


def test_short_mechanism_and_unreadable_label_are_flagged():
    P = plan([{"id": "A", "t0": 0, "t1": 2, "pace": "mechanism"}], text=[{"text": "Payments: senior paid first", "t0": 0.5, "t1": 1.2, "role": "key"}])
    f = PC.check_plan(P)["findings"]
    assert any(x["severity"] == "high" and "mechanism" in x["msg"] for x in f)
    assert any(x["severity"] == "high" and "readable for" in x["msg"] for x in f)


def test_a_developing_composition_is_not_penalised_and_labels_with_their_visual_count_once():
    ev = [{"id": "e1", "t": 1.0, "medium": "3d"}, {"id": "e2", "t": 4.0, "medium": "3d"}, {"id": "e3", "t": 7.0, "medium": "camera"}]
    tx = [{"text": "Senior", "t0": 1.05, "t1": 12, "role": "key"}, {"text": "Equity", "t0": 4.05, "t1": 12, "role": "key"}]
    f = PC.check_plan(plan([{"id": "A", "t0": 0, "t1": 12, "pace": "mechanism"}], ev, tx))["findings"]
    assert not [x for x in f if x["severity"] == "high"] and not any("introduced within" in x["msg"] for x in f)


def test_motion_counts_toward_load():
    calm = plan([{"id": "A", "t0": 0, "t1": 12, "pace": "emotional"}], [{"id": f"c{i}", "t": i + .5, "medium": "camera"} for i in range(2)])
    busy = plan([{"id": "A", "t0": 0, "t1": 12, "pace": "emotional"}], [{"id": f"c{i}", "t": i + .5, "medium": "camera"} for i in range(10)])
    lc, lb = PC.check_plan(calm)["series"][0]["load"], PC.check_plan(busy)["series"][0]["load"]
    assert lb > lc                                                              # camera moves are not free


def test_regression_p13_as_delivered_is_flagged():
    P = PC.load_plan(R / "pacing_p13_as_delivered.json"); f = PC.check_plan(P)["findings"]
    assert sum(x["severity"] == "high" for x in f) >= 10
    msgs = " ".join(x["msg"] for x in f)
    assert "far too short to absorb" in msgs and "readable for" in msgs and "develop within a composition" in msgs
    film = json.loads((R / "pacing_report_p13_as_delivered.json").read_text())["film"]   # measured on the rendered P13 MP4
    assert film["stats"]["per_10s"] > 5 and film["stats"]["longest_hold_s"] < 3.5
    assert any(x["severity"] == "high" for x in film["findings"])


def test_p13r_plan_is_far_lighter_than_p13_and_its_map_checks():
    p13 = PC.check_plan(PC.load_plan(R / "pacing_p13_as_delivered.json"))["summary"]
    p13r = PC.check_plan(PC.load_plan(R / "map_p13r.json"))["summary"]
    assert p13r["high"] < p13["high"] / 3                                       # a comparison, not a pass mark
    m = json.loads((R / "map_p13r.json").read_text())
    assert VM.check(m, VM.load_words(REPO / m["words"]))["errors"] == []
    assert any(e.get("held") for e in m["events"]) and all(s.get("pace") for s in m["shots"])
    assert m["words"].startswith("projects/charlab_p13r/")                     # P12's narration untouched


def test_visual_map_semantic_coverage():
    words = [{"word": "Payments", "start": 0.5, "end": 0.9}, {"word": "flow.", "start": 1.0, "end": 1.4}, {"word": "Senior", "start": 3.0, "end": 3.4}, {"word": "first.", "start": 6.0, "end": 6.4}]
    m = {"duration": 8, "shots": [{"id": "S", "t0": 0, "t1": 8, "medium": "3d", "introduces": ["information"], "purpose": "p"}], "concepts": [],
         "events": [{"id": "a", "anchor": {"word": "Payments"}, "offset": 0, "shot": "S", "medium": "3d", "what": "x"},
                    {"id": "b", "anchor": {"word": "Senior"}, "offset": 0, "shot": "S", "medium": "3d", "what": "x", "held": True}]}
    r = VM.check(m, words)
    assert r["errors"] == [] and not any("without a new visual event" in w for w in r["warnings"])    # a held clause is shown
    bad = copy.deepcopy(m); bad["events"][1]["medium"] = "cut"
    assert any("held event cannot be a cut" in e for e in VM.check(bad, words)["errors"])


def test_treatment_warns_when_narration_is_too_compressed_and_stays_backward_compatible():
    p13 = json.loads((REPO / "epoch-ledger/charlab/p13/treatment.json").read_text())
    assert TR.review(p13)["warnings"] == []                                     # no pace declared: as before
    paced = copy.deepcopy(p13)
    for s in paced["sequences"]: s["pace"] = "mechanism"; s["steps"] = ["a", "b", "c"]
    assert sum("narration too compressed" in w for w in TR.review(paced)["warnings"]) >= 5
    p13r = json.loads((R / "treatment.json").read_text())
    assert not any("too compressed" in w for w in TR.review(p13r)["warnings"])
    assert TR.review(p13r, R, gate="motion")["errors"]                          # awaiting approval: the gate is closed


def test_pacing_gate_is_wired_and_advisory_for_earlier_episodes():
    qg = (REPO / "epoch-ledger/scripts/quality_gates.py").read_text()
    assert '"pacing": (("video",), gate_pacing)' in qg and "predates STANDARD §3B" in qg
    assert "pacing_plan" in (REPO / "epoch-ledger/kit/gates.py").read_text()


def test_narration_states_the_example_is_simplified():
    lines = " ".join(l["text"] for l in json.loads((R / "script.json").read_text())["lines"])
    assert "simplified example" in lines and "In the real crisis, many senior securities lost money too" in lines
    for stage in ("doesn't keep the loan", "sells it on", "single pool", "security is issued", "paid first", "losses rise from the bottom"):
        assert stage in lines
