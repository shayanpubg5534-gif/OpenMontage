"""Original synthesised sound for office sequence v2 — every on-screen action has its sound (no samples, no music).

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/sfx_office_v2.py WS   → WS/mix.wav
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

spec = importlib.util.spec_from_file_location("ov2", HERE / "office_v2.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
SR, D, C = S.SR, V.D, V.CUT


def clinks(t0, t1, rate, db, rng):
    """A stream of small coin clinks (money moving through glass pipes)."""
    out, t = [], t0
    while t < t1:
        out.append((t, S.norm(S.coin(), db + rng.uniform(-4, 1)) * float(rng.uniform(.6, 1))))
        t += rng.exponential(1 / rate)
    return out


def events():
    W, r = V.W, np.random.default_rng(2001)
    ev = []
    ev.append((0, S.norm(S.bed(D, lo=200, hi=2200, mod=.1), -38)))                                   # room tone under all
    # S1 valve: squeal + clunk, then the rush of coins into the pipe
    ev.append((.22, S.norm(S.sweep(.7, 420, 260), -30))); ev.append((.95, S.norm(S.clunk(), -26)))
    ev.append((.55, S.norm(S.bed(.95, lo=600, hi=4000), -31))); ev += clinks(.6, C[1], 14, -30, r)
    # S2 TV: power-on pop + whine, the rocket whoosh, coins in
    ev += clinks(C[1], C[2], 12, -31, r)
    w = W("advertising", "c03_04")
    ev.append((w, S.norm(S.pop(), -24))); ev.append((w + .05, S.norm(S.sweep(.3, 9000, 15000), -40)))
    ev.append((w + .2, S.norm(S.whoosh(1.0, 5000), -26))); ev.append((w + .45, S.norm(S.chime(1320), -32)))
    # S3 payroll: typing, coins dropping, envelope pats
    t = C[2]
    while t < C[3]:
        ev.append((t, S.norm(S.tick(), -30 + r.uniform(-3, 2)))); t += r.uniform(.05, .14)
    we = W("employees", "c03_04")
    for i in range(4):
        ev += clinks(we + i * .13, we + i * .13 + .3, 18, -31, r)
        ev.append((we + i * .13 + .38, S.norm(S.lowpass(S.noise(int(.06 * SR)), 1800) * np.exp(-np.arange(int(.06 * SR)) / (SR * .012)).astype(np.float32), -26)))
    # S4 servers: hum, the slide + latch, beeps as it lights
    ev.append((C[3], S.norm(S.hum(C[4] - C[3], 120), -33)))
    wi = W("infrastructure", "c03_04")
    ev.append((wi + .02, S.norm(S.bed(.22, lo=800, hi=5000), -28))); ev.append((wi + .24, S.norm(S.clunk(), -24)))
    for k in range(3):
        ev.append((wi + .35 + k * .09, S.norm(S.chime(2200 + k * 300)[: int(.12 * SR)], -34)))
    ev += clinks(C[3], C[4], 10, -32, r)
    # S5 machine: steady pipe rush; a lone coin clink for the revenue trickle
    ev.append((C[4], S.norm(S.bed(C[5] - C[4], lo=300, hi=3000, mod=.2), -32))); ev += clinks(C[4], C[5], 9, -33, r)
    wr = W("revenue", "c03_04")
    ev.append((wr + .5, S.norm(S.coin(), -24))); ev.append((wr + .95, S.norm(S.coin(), -26)))
    # S6 gauge: needle creak and the warning beeps
    ws = W("sustain", "c03_04")
    ev.append((ws, S.norm(S.sweep(.9, 300, 160), -34)))
    t = ws + .6
    while t < C[6] - .1:
        ev.append((t, S.norm(S.chime(880)[: int(.16 * SR)], -28))); t += .38
    # S7 boardroom: murmur bed, the stamp slam, the valve, the capital rush
    ev.append((C[6], S.norm(S.bed(C[9] - C[6], lo=150, hi=900, mod=.3), -36)))
    wv = W("investors", "c03_05")
    ev.append((wv, S.norm(S.clunk(), -20))); ev.append((wv, S.norm(S.pop(), -26)))
    ev.append((C[8] + .05, S.norm(S.sweep(.55, 380, 240), -30))); ev += clinks(C[8] + .35, C[9], 12, -30, r)
    # S8 refill: a big pour that swells on "capital"
    ev.append((C[9], S.norm(S.bed(D - C[9], lo=250, hi=3500, mod=.15), -30)))
    ev += clinks(C[9] + .4, D, 18, -29, r)
    return ev


def build(ws: Path):
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
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else V.ROOT / "projects/ai-bubble-vs-dot-com/office_v2")
