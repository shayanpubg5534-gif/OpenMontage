"""Epoch Ledger narrate.py: content-addressed voicing, spoken-text overrides, caption reconciliation."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "epoch-ledger" / "episodes" / "how-banks-create-money" / "artifacts"


def _mod():
    spec = importlib.util.spec_from_file_location("el_narrate", ROOT / "epoch-ledger" / "scripts" / "narrate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["el_narrate"] = mod
    spec.loader.exec_module(mod)
    return mod


n = _mod()
CFG = {"tool": "kokoro_tts", "voice": "bm_george", "speed": 0.95}


def test_line_key_depends_on_spoken_text_and_voice_only():
    a = n._line_key("Hello there.", CFG)
    assert a == n._line_key("Hello there.", dict(CFG))
    assert a != n._line_key("Hello there!", CFG)
    assert a != n._line_key("Hello there.", {**CFG, "speed": 1.0})


def test_spoken_override_keeps_caption_text():
    line = {"id": "x", "text": "In November 2026, the ECB", "tts": "In November twenty twenty-six, the ECB"}
    assert n.spoken_text(line).startswith("In November twenty")
    assert n.spoken_text({"id": "y", "text": "Plain."}) == "Plain."


def _w(*items):
    return [{"word": w, "start": a, "end": b} for w, a, b in items]


def test_reconcile_uses_script_spelling_and_keeps_numerals():
    segs = [{"id": "l1", "text": "Huge data centres cost ten billion dollars.", "start": 0.0, "end": 3.0}]
    heard = _w(("Huge", 0.0, 0.3), ("data", 0.3, 0.6), ("centers", 0.6, 1.0), ("cost", 1.0, 1.3),
               ("$10", 1.3, 1.8), ("billion.", 1.8, 2.4))
    words = [w["word"] for w in n.reconcile(heard, segs)[0]["words"]]
    assert words == ["Huge", "data", "centres", "cost", "$10", "billion."]


def test_reconcile_fills_words_whisper_missed_inside_their_line():
    segs = [{"id": "a", "text": "Artificial intelligence.", "start": 0.0, "end": 1.5},
            {"id": "b", "text": "It costs money.", "start": 2.0, "end": 3.0}]
    heard = _w(("It", 2.0, 2.2), ("costs", 2.2, 2.6), ("money.", 2.6, 3.0))
    lines = n.reconcile(heard, segs)
    assert [w["word"] for w in lines[0]["words"]] == ["Artificial", "intelligence."]
    assert all(0.0 <= w["start"] <= w["end"] <= 1.5 for w in lines[0]["words"])


def test_caption_pages_never_split_number_from_unit():
    ws = [{"word": w, "start": i, "end": i + 0.5} for i, w in
          enumerate("Imagine a chip manufacturer investing $1 billion in a developer.".split())]
    pages = n.caption_pages([{"id": "x", "words": ws}], 6)
    assert pages[0]["text"].endswith("$1 billion")


def test_merge_numbers_rejoins_whisper_fragments():
    raw = _w((" 86", 0, 1), ("%", 1, 1.1), (" $5", 2, 2.5), (".5", 2.5, 3), (" $10", 4, 4.5), (",000", 4.5, 5))
    assert [w["word"] for w in n._merge_numbers(raw)] == ["86%", "$5.5", "$10,000"]


def test_pilot_caption_pages_reproduce_with_new_alignment():
    t = json.loads((PILOT / "narration_timing.json").read_text())
    words = n._merge_numbers(json.loads((PILOT / "words.json").read_text()))
    pages = n.caption_pages(n.reconcile(words, t["segments"]), 6)
    approved = json.loads((PILOT / "caption_phrases.json").read_text())
    assert [round(p["start"], 2) for p in pages] == [round(p["start"], 2) for p in approved]
    # only difference allowed: script punctuation ("an asset:" where Whisper heard a comma)
    diffs = [(a["text"], b["text"]) for a, b in zip(pages, approved) if a["text"] != b["text"]]
    assert diffs == [("an asset:", "an asset,")]
