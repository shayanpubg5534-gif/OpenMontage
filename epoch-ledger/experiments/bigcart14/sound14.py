"""Shared original sound design for A′ and B (synthesised, no samples, no music) — keyed to BRIEF.md's key moments.
  python epoch-ledger/experiments/bigcart14/sound14.py WS     → WS/sfx.wav (+ WS/mix.wav = narration + sfx when WS/narration.wav exists)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import shots as SH  # noqa: E402
sys.path.insert(0, str(SH.ROOT / "epoch-ledger/episodes/ai-bubble-vs-dot-com"))
import sfx as S  # noqa: E402

SR, D, C, W = S.SR, SH.D, SH.CUT, SH.W


def rustle(db):
    n = int(.18 * SR)
    return S.norm(S.highpass(S.noise(n), 2500) * np.exp(-np.arange(n) / (SR * .05)).astype(np.float32), db)


def events():
    r = np.random.default_rng(2003)
    ev = [(0, S.norm(S.bed(C[1], lo=200, hi=2200, mod=.1), -38)), (C[3], S.norm(S.bed(D - C[3], lo=200, hi=2200, mod=.1), -38))]
    wa, we, wi, wr = W("advertising", "c03_04"), W("employees", "c03_04"), W("infrastructure", "c03_04"), W("revenue", "c03_04")
    for a, b in ((C[0], C[1]), (C[3], C[4])):            # typing in the office shots
        t = a
        while t < b:
            ev.append((t, S.norm(S.tick(), -32 + r.uniform(-3, 2)))); t += r.uniform(.06, .17)
    for t0, n in ((wa - .2, 9), (we - .25, 12), (wi - .05, 5), (W("capital", "c03_05") + .45, 14)):
        ev += [(t0 + k * .07, rustle(-30 + r.uniform(-3, 1))) for k in range(n)]
    ev.append((wa + .4, S.norm(S.pop(), -26))); ev += [(wa + .65 + k * .18, S.norm(S.chime(f)[: int(.25 * SR)], -31)) for k, f in enumerate((660, 880, 990, 1320))]
    ev += [(we + .3 + i * .14, S.norm(S.clunk(), -32)) for i in range(4)]
    ev.append((wi - 1.1, S.norm(S.chuffs(1.2, 9), -34))); ev += [(wi + .45 + k * .08, S.norm(S.chime(2400 + k * 200)[: int(.1 * SR)], -34)) for k in range(3)]
    ev.append((wr + .3, S.norm(S.clunk(), -30)))                                    # the single payment lands
    # ledger: pen scratches per line
    for t in (C[1] + .14, C[1] + .56, W("themselves", "c03_05" if False else "c03_04") - .05, W("themselves", "c03_04") + .38):
        ev.append((t, S.norm(S.bed(.4, lo=3000, hi=8000, mod=.6), -35)))
    ev.append((C[2], S.norm(S.bed(C[3] - C[2], lo=150, hi=900, mod=.3), -36)))     # boardroom murmur
    wd, wv = W("depended", "c03_05"), W("investors", "c03_05")
    ev.append((wd + .6, S.norm(S.bed(wv + .1 - wd - .6, lo=3000, hi=8000, mod=.6), -34))); ev.append((wv + .7, S.norm(S.clunk(), -30)))
    wc = W("continuing", "c03_05")
    ev.append((wc - .05, S.norm(S.bed(.8, lo=600, hi=2400, mod=2.0), -30)))          # fax printing
    ev += [(wc + .8 + k * .03, rustle(-31)) for k in range(20)]
    return ev


def build(ws: Path):
    n = int(D * SR)
    fx = np.zeros(n, np.float32)
    for t, snd in events():
        s = max(0, int(t * SR)); e = min(n, s + len(snd))
        if e <= s:
            continue
        fx[s:e] += snd[:e - s]
    sf.write(ws / "sfx.wav", np.stack([fx, fx], 1), SR)
    if (ws / "narration.wav").exists():
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(ws / "narration.wav"), "-i", str(ws / "sfx.wav"), "-filter_complex",
                        "[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[o]", "-map", "[o]", "-ar", "48000", "-ac", "2", str(ws / "mix.wav")], check=True)
    print("wrote", ws / "sfx.wav")


if __name__ == "__main__":
    build(Path(sys.argv[1]))
