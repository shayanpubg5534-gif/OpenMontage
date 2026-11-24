"""Narration timing for scene authoring: line windows and Whisper word times (script wording)."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
_T = json.loads((HERE / "artifacts" / "narration_timing.json").read_text())
PAGES = json.loads((HERE / "artifacts" / "caption_phrases.json").read_text())
D = _T["total"]
SEG = {s["id"]: s for s in _T["segments"]}
WORDS = [w for p in PAGES for w in p["words"]]


def _n(s):
    return re.sub(r"[^a-z0-9$]", "", s.lower())


def L(line_id):
    """(start, end) of a narration line, film seconds."""
    s = SEG[line_id]
    return s["start"], s["end"]


def W(text, line_id=None, after=None):
    """Start time of the first word matching `text` (prefix match, script wording) inside a line
    (or after a time). Raises if absent, so a script change can never silently desync a beat."""
    lo, hi = (L(line_id) if line_id else (after or 0.0, D))
    if after is not None:
        lo = max(lo, after)
    key = _n(text)
    for w in WORDS:
        if lo - 0.02 <= w["start"] <= hi + 0.02 and _n(w["word"]).startswith(key):
            return round(w["start"], 3)
    raise KeyError(f"word {text!r} not found in {line_id or (lo, hi)}")


def WE(text, line_id=None, after=None):
    """End time of the matching word."""
    t = W(text, line_id, after)
    return round(next(w["end"] for w in WORDS if abs(w["start"] - t) < 1e-6), 3)
