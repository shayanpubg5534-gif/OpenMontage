"""Creative direction layer (STANDARD §3A): the standard, the director skill and its routing, the treatment checker,
the opt-in scene-plan fields, and the references. These checks prove the thinking is written down and routed; creative
quality itself is judged on rendered frames (QUALITY.md director's review), which no test can do.
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "epoch-ledger"))
from kit import scene_plan, treatment  # noqa: E402

GOOD = {
    "episode": "test", "thesis": {"understand": "how a loan becomes a security", "feel": "the distance growing"},
    "arc": "ordinary → distant → consequence", "through_line": "the family's mortgage",
    "worlds": [{"id": "kitchen", "place": "the family's kitchen", "role": "the loan is signed", "build": "2.5d", "status": "new"}],
    "motifs": ["the porch light"], "signature": "a unique device for this test",
    "sequences": [{"id": "q1", "narration": "a family signs a mortgage", "hero": True, "understand": "a loan is made", "feel": "hope, strain",
                   "concepts": [{"name": "literal baseline", "kind": "literal", "idea": "a document", "verdict": "rejected", "why": "no stakes"},
                                {"name": "kitchen table", "kind": "human", "idea": "they sign at home", "verdict": "chosen", "why": "stakes and place"}],
                   "human_anchor": "the family", "worlds": ["kitchen"],
                   "acting": [{"who": "wife", "wants": "the house", "does": "slides the signed page across the table", "feels": "hopeful"}],
                   "transitions": [{"to": "end", "motive": "follow the document out of frame"}], "storyboard": [], "approved": False}]}


def test_standard_and_checklist_carry_creative_direction():
    std = (ROOT / "epoch-ledger/STANDARD.md").read_text()
    for phrase in ("## 3A. Creative direction", "literal baseline", "Characters act with intent", "Metaphors are exact",
                   "Human consequence", "Every sequence is directed", "Creative freedom", "Judged on the output", "Storyboard gate"):
        assert phrase in std, phrase
    q = (ROOT / "epoch-ledger/QUALITY.md").read_text()
    assert "Director's review (judged on the rendered frames" in q and "kit.treatment" in q and "--gate motion" in q


def test_director_skill_is_routed_everywhere():
    assert (ROOT / "skills/creative/epoch-ledger-director.md").exists()
    assert (ROOT / ".claude/skills/epoch-ledger-director/SKILL.md").exists()
    for f in ("AGENT_GUIDE.md", "CLAUDE.md", ".claude/commands/epoch-ledger.md", "skills/creative/epoch-ledger.md", "skills/INDEX.md"):
        assert "epoch-ledger-director" in (ROOT / f).read_text(), f
    for f in ("epoch-ledger/direction/VISUAL_LANGUAGE.md", "epoch-ledger/direction/CONCEPT_NOTES.md", "epoch-ledger/direction/used_devices.json",
              "epoch-ledger/templates/episode/treatment.json"):
        assert (ROOT / f).exists(), f
    notes = (ROOT / "epoch-ledger/direction/CONCEPT_NOTES.md").read_text()
    for stage in ("Origination", "Pooling", "Issuance", "loss allocation"):       # securitisation stages kept distinct
        assert stage in notes


def test_treatment_accepts_a_directed_sequence():
    r = treatment.review(GOOD)
    assert r["errors"] == []
    md = treatment.to_markdown(GOOD)
    assert "literal baseline" in md and "kitchen table" in md


def test_treatment_rejects_undirected_work():
    t = copy.deepcopy(GOOD); t["sequences"][0]["concepts"] = t["sequences"][0]["concepts"][1:]
    assert any("literal baseline" in e for e in treatment.review(t)["errors"])
    t = copy.deepcopy(GOOD); t["sequences"][0]["concepts"][1]["kind"] = "metaphor"
    assert any("accuracy" in e for e in treatment.review(t)["errors"])                 # a metaphor needs accuracy notes
    t = copy.deepcopy(GOOD); t["sequences"][0]["acting"][0]["does"] = "turns her head and blinks"
    assert any("head, eye or mouth" in e for e in treatment.review(t)["errors"])        # acting is not heads and blinks
    t = copy.deepcopy(GOOD); t["sequences"][0].pop("human_anchor")
    assert any("human anchor" in e for e in treatment.review(t)["errors"])
    t = copy.deepcopy(GOOD); t["sequences"][0]["transitions"][0]["motive"] = "cut"
    assert any("motive" in e for e in treatment.review(t)["errors"])
    t = copy.deepcopy(GOOD); t["sequences"][0]["concepts"][0]["verdict"] = "chosen"; t["sequences"][0]["concepts"][1]["verdict"] = "rejected"
    assert any("literal baseline is chosen" in e for e in treatment.review(t)["errors"])  # literal only with a real reason


def test_storyboard_gate_blocks_animation_until_approved(tmp_path):
    r = treatment.review(GOOD, tmp_path, gate="motion")
    assert any("storyboard" in e for e in r["errors"])
    t = copy.deepcopy(GOOD); (tmp_path / "k1.png").write_bytes(b"png"); t["sequences"][0]["storyboard"] = [{"frame": "k1.png", "shows": "x"}]
    assert any("not approved" in e for e in treatment.review(t, tmp_path, gate="motion")["errors"])
    t["sequences"][0]["approved"] = True
    assert treatment.review(t, tmp_path, gate="motion")["errors"] == []


def test_reused_signature_is_flagged():
    t = copy.deepcopy(GOOD); t["signature"] = "the double-entry ink line"
    assert any("signature device already used" in w for w in treatment.review(t)["warnings"])


def test_scene_plan_direction_fields_are_opt_in():
    shot = {"id": "s1", "beat": {"t": "0-3", "narration": "x"}, "understanding": "the viewer learns the loan is signed",
            "shot": "medium", "focal_point": "the page", "technique": ["2.5d"], "graphics": [], "rationale": "r",
            "meaning": {"what": "signing", "why": "a loan", "consequence": "a debt"}}
    assert not any("direction 2" in e for e in scene_plan.review({"shots": [shot]})["errors"])        # old plans unchanged
    errs = scene_plan.review({"direction": 2, "shots": [shot]})["errors"]
    assert any("'world'" in e for e in errs) and any("'acting'" in e for e in errs)
    ok = {**shot, "world": "the family's kitchen", "acting": [{"who": "wife", "wants": "home", "does": "signs the page", "feels": "hope"}]}
    assert not any("direction 2" in e for e in scene_plan.review({"direction": 2, "shots": [ok]})["errors"])
