#!/usr/bin/env python3
"""Character lab (M5): lip sync for lines a character actually speaks (never for third-person narration).

    .venv/bin/python epoch-ledger/charlab/lipsync.py "We're busy every day." OUT_DIR --voice bf_emma [--speed 0.95]

1. Voices the line locally with Kokoro (free, offline) → OUT_DIR/line.wav
2. Times every word with faster-whisper (local) → OUT_DIR/words.json
3. Builds a viseme track at 30 fps → OUT_DIR/visemes.json: per frame, weights for MakeHuman mouth units
   (mouth-open, mouth-retraction, mouth-pursing, mouth-protusion, mouth-compression, mouth-eversion).
   Each word's letters are mapped to visemes (vowel shapes, closed lips for m/b/p, lip under teeth for f/v, rounded
   for o/u/w), spread over the word's spoken duration, eased between shapes (co-articulation) and scaled by the
   audio's loudness, so the mouth closes in pauses and opens with stressed syllables.
Deterministic for a given text, voice and speed.

Permanent standard: narration is a voice-over, not dialogue. Run this only for an explicit scripted line with the
character's own assigned voice; never on the narration track. The result is used only where a shot opts in with an
actor `speech` entry (off by default).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

FPS = 30
UNITS = ["mouth-open", "mouth-retraction", "mouth-pursing", "mouth-protusion", "mouth-compression", "mouth-eversion"]
SHAPES = {   # viseme → unit weights (M5 review: jaw opening carries speech; retraction kept light, or it reads as a grimace)
    "A": {"mouth-open": .85, "mouth-retraction": .05},
    "E": {"mouth-open": .5, "mouth-retraction": .22},
    "I": {"mouth-open": .32, "mouth-retraction": .28},
    "O": {"mouth-open": .6, "mouth-pursing": .45},
    "U": {"mouth-open": .25, "mouth-pursing": .65, "mouth-protusion": .3},
    "MBP": {"mouth-compression": .7},
    "FV": {"mouth-open": .1, "mouth-eversion": .5, "mouth-compression": .15},
    "C": {"mouth-open": .38, "mouth-retraction": .08},           # most consonants
    "REST": {},
}


def letters_to_visemes(word: str) -> list[str]:
    w = word.lower()
    out, i = [], 0
    while i < len(w):
        ch, nx = w[i], w[i + 1:i + 2]
        if not ch.isalpha():
            i += 1; continue
        if ch in "mbp": out.append("MBP")
        elif ch in "fv": out.append("FV")
        elif ch == "w" or (ch == "o" and nx in ("o", "u")) or ch == "u": out.append("U")
        elif ch == "o": out.append("O")
        elif ch == "a": out.append("A")
        elif ch == "e" and i == len(w) - 1 and len(w) > 2: pass          # silent final e
        elif ch == "e": out.append("E")
        elif ch in "iy": out.append("I")
        else: out.append("C")
        i += 1
    dedup = [v for k, v in enumerate(out) if k == 0 or v != out[k - 1]]
    return dedup or ["C"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("text"); ap.add_argument("out", type=Path)
    ap.add_argument("--voice", default="bf_emma"); ap.add_argument("--speed", type=float, default=.95)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    from kokoro_onnx import Kokoro
    k = Kokoro(str(Path.home() / ".cache/kokoro/kokoro-v1.0.onnx"), str(Path.home() / ".cache/kokoro/voices-v1.0.bin"))
    audio, sr = k.create(a.text, voice=a.voice, speed=a.speed, lang="en-gb" if a.voice.startswith("b") else "en-us")
    nz = np.nonzero(np.abs(audio) > 1e-3)[0]                       # trim edge silence, keep 60 ms margins
    audio = audio[max(0, nz[0] - int(.06 * sr)): nz[-1] + int(.06 * sr)] if len(nz) else audio
    wav = a.out / "line.wav"; sf.write(wav, audio, sr)
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(str(wav), word_timestamps=True, beam_size=5)
    words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in s.words]
    (a.out / "words.json").write_text(json.dumps(words, indent=1))
    dur = len(audio) / sr; n = int(np.ceil(dur * FPS)) + 1
    # loudness per frame (RMS, normalised)
    hop = sr // FPS
    rms = np.array([np.sqrt(np.mean(audio[f * hop:(f + 1) * hop] ** 2)) if f * hop < len(audio) else 0 for f in range(n)])
    env = np.clip(rms / (np.percentile(rms[rms > 0], 90) + 1e-6), 0, 1.2) if rms.max() > 0 else rms
    # viseme keys: (time, shape)
    keys = [(0.0, "REST")]
    for w in words:
        vs = letters_to_visemes(w["word"]); span = max(.06, w["end"] - w["start"])
        for j, v in enumerate(vs):
            keys.append((w["start"] + span * j / len(vs), v))
        keys.append((w["end"], "REST"))
    keys.sort()
    frames = []
    for f in range(n):
        t = f / FPS
        # co-articulation: blend the two nearest keys with a smooth ramp (shapes anticipate by ~40 ms)
        tt = t + .04
        a0 = max((k for k in keys if k[0] <= tt), default=keys[0]); later = [k for k in keys if k[0] > tt]
        b0 = later[0] if later else a0
        u = 0 if b0 is a0 else (tt - a0[0]) / max(1e-3, b0[0] - a0[0]); u = u * u * (3 - 2 * u)
        wts = {un: (1 - u) * SHAPES[a0[1]].get(un, 0) + u * SHAPES[b0[1]].get(un, 0) for un in UNITS}
        g = .35 + .65 * min(1, env[f] * 1.1)                       # louder → bigger shapes; silence → near rest
        frames.append({un: round(wts[un] * (g if un != "mouth-compression" else 1), 3) for un in UNITS})
    (a.out / "visemes.json").write_text(json.dumps({"fps": FPS, "duration": round(dur, 3), "units": UNITS, "frames": frames, "words": words, "voice": a.voice, "text": a.text}))
    print(json.dumps({"wav": str(wav), "duration": round(dur, 2), "words": len(words), "frames": n}))


if __name__ == "__main__":
    main()
