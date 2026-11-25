"""Original synthesised sound for office sequence v3 — every on-screen action has its sound (no samples, no music).

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/sfx_office_v3.py WS   → WS/mix.wav
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

spec = importlib.util.spec_from_file_location("ov3", HERE / "office_v3.py")
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


def rustle(db):
    n = int(.18 * S.SR)
    return S.norm(S.highpass(S.noise(n), 2500) * np.exp(-np.arange(n) / (S.SR * .05)).astype(np.float32), db)


def events():
    W, r = V.W, np.random.default_rng(2002)
    ev = [(0, S.norm(S.bed(D, lo=200, hi=2200, mod=.1), -38))]                                  # room tone
    wa, we, wi = W("advertising", "c03_04"), W("employees", "c03_04"), W("infrastructure", "c03_04")
    # A: typing throughout; bills rustle as they fly; TV power-on + a short commercial jingle; envelope pats; rack wheels + beeps
    t = C[0]
    while t < C[1]:
        ev.append((t, S.norm(S.tick(), -31 + r.uniform(-3, 2)))); t += r.uniform(.06, .16)
    for t0, n in ((wa - .15, 9), (we - .2, 12), (wi - .05, 5)):
        for k in range(n):
            ev.append((t0 + k * .07, rustle(-30 + r.uniform(-3, 1))))
    ev.append((wa + .45, S.norm(S.pop(), -26))); ev += [(wa + .7 + k * .18, S.norm(S.chime(f)[: int(.25 * SR)], -30)) for k, f in enumerate((660, 880, 990, 1320))]
    for i in range(4):
        ev.append((we + .35 + i * .14, S.norm(S.clunk(), -32)))
    ev.append((wi - 1.1, S.norm(S.chuffs(1.2, 9), -34))); ev += [(wi + .45 + k * .08, S.norm(S.chime(2400 + k * 200)[: int(.1 * SR)], -34)) for k in range(3)]
    # B: chart builds — soft ticks per bar, a low tone for the shortfall, a falling sweep as cash heads to zero
    for k in range(3):
        ev.append((C[1] + .35 + k * .3, S.norm(S.tick(), -28)))
    wr, ws = W("revenue", "c03_04"), W("sustain", "c03_04")
    ev.append((wr, S.norm(S.tick(), -26))); ev.append((wr + .6, S.norm(S.hum(.8, 70), -30))); ev.append((ws, S.norm(S.sweep(1.1, 520, 180), -32)))
    # C1: boardroom murmur, pen scratch, handshake pat
    ev.append((C[2], S.norm(S.bed(C[3] - C[2], lo=150, hi=900, mod=.3), -36)))
    wd, wv = W("depended", "c03_05"), W("investors", "c03_05")
    ev.append((wd + .6, S.norm(S.bed(wv + .1 - wd - .6, lo=3000, hi=8000, mod=.6), -34))); ev.append((wv + .7, S.norm(S.clunk(), -30)))
    # C2: wire arrives (chime), RECEIVED stamp, bundles landing, chart jump
    wc, wcap = W("continuing", "c03_05"), W("capital", "c03_05")
    ev.append((wc + .1, S.norm(S.chime(1760), -28))); ev.append((wc + .55, S.norm(S.clunk(), -24)))
    for k in range(12):
        ev.append((wc + .9 + k * .05, rustle(-30)))
    ev.append((wcap - .3, S.norm(S.sweep(.6, 200, 640), -30)))
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
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else V.ROOT / "projects/ai-bubble-vs-dot-com/office_v3")
