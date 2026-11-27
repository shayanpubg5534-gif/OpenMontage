"""Permanent documentary animation standard (P6): narration is a voice-over, not character dialogue.

Static checks only (no rendering):
- lip sync stays available but is opt-in: Rig v4 mouths speak only through explicit `say()` ranges, and the lab's
  performance compiler applies mouth tracks only from an actor's explicit `speech` entries
- every `speech` entry in a shot is a character's own scripted line (a `lipsync.py` dialogue output for that
  character), never the narration
- the standard is written into the production skill, the production standard, the character standard and DIRECTION
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHARLAB = REPO / "epoch-ledger/charlab"
DEMOS = sorted((CHARLAB / "motion/demos").glob("*.json"))


def test_lipsync_capability_retained_and_explicit_only():
    rig4 = (REPO / "epoch-ledger/kit/rig4.js").read_text()
    assert "function say(" in rig4 and "function speakAt(" in rig4                 # retained
    assert len(re.findall(r"\.speak\.push\(", rig4)) == 1                            # filled only by say()
    elm = (CHARLAB / "motion/elmotion.js").read_text()
    assert "(C.S.speech || [])" in elm                                               # only an explicit per-actor track
    assert (CHARLAB / "lipsync.py").exists() and (CHARLAB / "splice_dialogue.py").exists()


def test_speech_tracks_are_scripted_character_dialogue_only():
    for f in DEMOS:
        d = json.loads(f.read_text())
        for actor, a in (d.get("actors") or {}).items():
            for sp in a.get("speech", []):
                m = re.search(r"/dialogue_([a-z]+)/visemes\.json$", sp.get("src", ""))
                assert m, f"{f.name}: {actor} speech must come from lipsync.py dialogue output, got {sp.get('src')}"
                assert actor.startswith(m.group(1)), f"{f.name}: {actor} lip-syncs another speaker's line ({m.group(1)})"
                assert "narrat" not in sp["src"].lower(), f"{f.name}: narration must never drive a mouth"


def test_narrated_demos_without_dialogue_have_no_speech():
    story = json.loads((CHARLAB / "motion/demos/story_loan.json").read_text())   # narrated five-shot beat, no dialogue
    assert not any(a.get("speech") for a in story["actors"].values())


def test_standard_is_documented():
    docs = {
        "skills/creative/epoch-ledger.md": "Narration and dialogue (permanent standard)",
        "epoch-ledger/STANDARD.md": "Narration is an independent voice-over",
        "epoch-ledger/charlab/CHARACTER_STANDARD.md": "No automatic lip sync to the narrator",
        "epoch-ledger/charlab/DIRECTION.md": "Characters never lip-sync to the narrator",
    }
    for path, phrase in docs.items():
        assert phrase in (REPO / path).read_text(), path
