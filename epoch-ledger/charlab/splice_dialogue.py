#!/usr/bin/env python3
"""Character lab (M5): put a character's spoken line between narration lines (lab only; narrate.py is used read-only).

    python3 epoch-ledger/charlab/splice_dialogue.py EPISODE_DIR DIALOGUE_DIR --before n4 --at 19.2 --gap 0.3 --ws WS

EPISODE_DIR is a narrate.py episode (artifacts/narration_timing.json, caption_phrases.json; WS/narration.wav).
DIALOGUE_DIR is a lipsync.py output (line.wav, words.json, visemes.json).
Narration from line --before onwards moves later so the dialogue plays at --at, followed by --gap seconds of breath.
Writes WS/narration.wav (mixed), EPISODE_DIR/artifacts/caption_phrases.json (dialogue pages added, later pages shifted;
the narration-only originals are kept as *.narration_only.json) and EPISODE_DIR/artifacts/timeline.json — the beat
times every visual is keyed to (narration-driven direction: the picture follows what the narrator says).
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("episode", type=Path); ap.add_argument("dialogue", type=Path)
    ap.add_argument("--before", required=True); ap.add_argument("--at", type=float, required=True)
    ap.add_argument("--gap", type=float, default=.3); ap.add_argument("--ws", type=Path, required=True)
    ap.add_argument("--speaker", default="nadia"); ap.add_argument("--tail", type=float, default=.5)
    a = ap.parse_args(argv)
    art = a.episode / "artifacts"
    timing = json.loads((art / "narration_timing.json").read_text())
    capf = art / "caption_phrases.json"; keep = art / "caption_phrases.narration_only.json"
    if not keep.exists(): shutil.copy(capf, keep)
    pages = json.loads(keep.read_text())
    wavf = a.ws / "narration.wav"; keepw = a.ws / "narration.narration_only.wav"
    if not keepw.exists(): shutil.copy(wavf, keepw)
    nar, sr = sf.read(keepw, dtype="float32")
    dl, sr2 = sf.read(a.dialogue / "line.wav", dtype="float32")
    if nar.ndim > 1: nar = nar.mean(1)
    if dl.ndim > 1: dl = dl.mean(1)
    if sr2 != sr:                                              # Kokoro writes 24 kHz; the narration mix is 48 kHz (ffmpeg resampler)
        import subprocess
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(a.dialogue / "line.wav"), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                             check=True, capture_output=True).stdout
        dl = np.frombuffer(raw, np.float32).copy()
    seg = next(s for s in timing["segments"] if s["id"] == a.before)
    cut = seg["start"] - .02                                   # split just before the line (it starts after a breath)
    d_dur = len(dl) / sr
    new_start = a.at + d_dur + a.gap
    shift = new_start - seg["start"]
    assert a.at >= max(s["end"] for s in timing["segments"] if s["end"] <= seg["start"]), "dialogue overlaps narration"
    head, tail = nar[:int(cut * sr)], nar[int(cut * sr):]
    # dialogue at a slightly lower level than narration peak, so the two voices sit together
    dl = dl * (np.abs(head).max() * .92 / max(1e-6, np.abs(dl).max()))
    out = np.zeros(int((len(nar) / sr + shift + 0) * sr) + int(a.tail * sr), np.float32)
    out[:len(head)] = head
    i0 = int(a.at * sr); out[i0:i0 + len(dl)] += dl
    j0 = int((cut + shift) * sr); out[j0:j0 + len(tail)] += tail[:len(out) - j0]
    sf.write(wavf, out, sr)
    words = json.loads((a.dialogue / "words.json").read_text())
    dpages, cur = [], []
    for w in words:                                            # one page per sentence of the spoken line
        cur.append({"word": w["word"], "start": round(a.at + w["start"], 3), "end": round(a.at + w["end"], 3)})
        if w["word"].endswith((".", "?", "!")):
            dpages.append(cur); cur = []
    if cur: dpages.append(cur)
    newp = []
    for p in pages:
        if p["start"] >= seg["start"] - .01:
            p = {**p, "start": round(p["start"] + shift, 3), "end": round(p["end"] + shift, 3),
                 "words": [{**w, "start": round(w["start"] + shift, 3), "end": round(w["end"] + shift, 3)} for w in p["words"]]}
        newp.append(p)
    for ws in dpages:
        newp.append({"start": ws[0]["start"], "end": ws[-1]["end"], "text": " ".join(w["word"] for w in ws), "words": ws, "speaker": a.speaker})
    newp.sort(key=lambda p: p["start"])
    capf.write_text(json.dumps(newp, indent=1))
    tl = {"total": round(len(out) / sr, 3), "beats": []}
    for s in timing["segments"]:
        st, en = (s["start"], s["end"]) if s["start"] < seg["start"] else (s["start"] + shift, s["end"] + shift)
        tl["beats"].append({"id": s["id"], "kind": "narration", "start": round(st, 3), "end": round(en, 3), "text": s["text"]})
    tl["beats"].append({"id": "dialogue", "kind": "dialogue", "speaker": a.speaker, "start": round(a.at, 3), "end": round(a.at + d_dur, 3),
                        "text": json.loads((a.dialogue / "visemes.json").read_text())["text"]})
    tl["beats"].sort(key=lambda b: b["start"])
    for p in newp:                                             # word times for keying visuals to specific words
        for w in p["words"]:
            tl.setdefault("words", []).append(w)
    (art / "timeline.json").write_text(json.dumps(tl, indent=1))
    print(json.dumps({"total": tl["total"], "shift": round(shift, 3), "beats": [(b["id"], b["start"], b["end"]) for b in tl["beats"]]}))


if __name__ == "__main__":
    main()
