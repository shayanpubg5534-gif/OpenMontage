"""Original synthesised sound for the motion test (no samples, no music), keyed to the test's word times.

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/sfx_motiontest.py WS   → WS/mix.wav (narration + effects)
Reuses the episode's primitives (sfx.py). Effects sit well under the voice (-24 to -34 dBFS peaks).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parents[2])]
import sfx as S  # noqa: E402

spec = importlib.util.spec_from_file_location("mt", HERE / "make_motiontest.py")
MT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MT)
SR, D = S.SR, MT.D


def events():
    W = MT.W
    r = np.random.default_rng(2000)
    ev = []
    # shot 1: dusk street bed, distant traffic swell, the furnace roar thickening on "struggling"
    ev.append((0.0, S.norm(S.bed(MT.CUT1 + .3, lo=80, hi=900, mod=.3), -30)))
    ev.append((W("struggling", "c03_03") - .2, S.norm(S.bed(1.6, lo=40, hi=320), -27)))
    # shot 2: office room tone, keyboards, a marker stroke per drawn part, coins as the gap fills with investor cash
    ev.append((MT.CUT1, S.norm(S.bed(MT.CUT2 - MT.CUT1, lo=300, hi=2500, mod=.1), -36)))
    t = MT.CUT1 + .2
    while t < MT.CUT2 - .3:
        ev.append((t, S.norm(S.tick(), -32 + r.uniform(-3, 2))))
        t += r.uniform(.08, .22) if r.random() > .1 else r.uniform(.5, .9)
    for w, line in (("advertising", "c03_04"), ("employees", "c03_04"), ("infrastructure", "c03_04"), ("revenue", "c03_04"), ("sustain", "c03_04")):
        ev.append((W(w, line), S.norm(S.bed(.32, lo=1800, hi=6000) * np.linspace(1, .3, int(.32 * SR), dtype=np.float32), -30)))
    for k in range(6):
        ev.append((W("investors", "c03_05") + .1 + k * .13, S.norm(S.coin(), -31 - k)))
    # shot 3: CRT hum, the phone set down, relay clicks as the office lights go out
    ev.append((MT.CUT2, S.norm(S.hum(D - MT.CUT2, 60), -34)))
    ev.append((W("finance", "c03_10") + .9, S.norm(S.clunk(), -28)))
    for k in range(4):
        ev.append((W("operations", "c03_10") - .1 + k * .22, S.norm(S.pop(), -33)))
    return ev


def build(ws: Path) -> None:
    n = int(D * SR)
    fx = np.zeros(n, np.float32)
    for t, snd in events():
        s = max(0, int(t * SR)); e = min(n, s + len(snd))
        fx[s:e] += snd[:e - s]
    sf.write(ws / "sfx.wav", np.stack([fx, fx], 1), SR)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(ws / "narration.wav"), "-i", str(ws / "sfx.wav"), "-filter_complex",
                    "[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[o]", "-map", "[o]", "-ar", "48000", "-ac", "2",
                    str(ws / "mix.wav")], check=True)
    print("wrote", ws / "mix.wav")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else MT.ROOT / "projects/ai-bubble-vs-dot-com/motiontest")
