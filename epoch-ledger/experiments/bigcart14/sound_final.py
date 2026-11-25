"""Original sound design for the final acceptance preview (synthesised, no samples, no music), keyed to the
final cut's actions (shots_final.CUT): spends, payments, servers, the signature, the handshake, the wire.
  python epoch-ledger/experiments/bigcart14/sound_final.py WS   → WS/sfx.wav and WS/mix.wav (narration + sfx)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sound14 as S14  # noqa: E402
import shots_final as SF  # noqa: E402

S, SR, W, C, D = S14.S, S14.SR, SF.W, SF.CUT, SF.D
rustle = S14.rustle


def events():
    r = np.random.default_rng(2026)
    ev = [(C[0], S.norm(S.bed(C[1], lo=200, hi=2200, mod=.1), -38)), (C[3], S.norm(S.bed(D - C[3], lo=200, hi=2200, mod=.1), -38)),
          (C[1], S.norm(S.bed(C[2] - C[1], lo=200, hi=1600, mod=.1), -44)),                    # the chart: quiet room tone
          (C[2], S.norm(S.bed(C[3] - C[2], lo=150, hi=900, mod=.3), -36))]                     # boardroom murmur
    for a, b in ((C[0], C[1]), (C[3], C[4])):                                                   # typing in the office
        t = a
        while t < b:
            ev.append((t, S.norm(S.tick(), -32 + r.uniform(-3, 2)))); t += r.uniform(.06, .17)
    wa, we, wi = W("advertising", "c03_04"), W("employees", "c03_04"), W("infrastructure", "c03_04")
    for t0, n in ((wa - .2, 9), (we - .25, 12), (wi - .05, 5), (W("capital", "c03_05") + .45, 14)):
        ev += [(t0 + k * .07, rustle(-30 + r.uniform(-3, 1))) for k in range(n)]
    ev.append((wa + .4, S.norm(S.pop(), -26))); ev += [(wa + .65 + k * .18, S.norm(S.chime(f)[: int(.25 * SR)], -31)) for k, f in enumerate((660, 880, 990, 1320))]
    ev += [(we + .3 + i * .14, S.norm(S.clunk(), -32)) for i in range(4)]
    ev.append((wi - 1.1, S.norm(S.chuffs(1.2, 9), -34))); ev += [(wi + .45 + k * .08, S.norm(S.chime(2400 + k * 200)[: int(.1 * SR)], -34)) for k in range(3)]
    wd, wv = W("depended", "c03_05"), W("investors", "c03_05")
    ev.append((wd + .06, S.norm(S.bed(.6, lo=3000, hi=8000, mod=.6), -34)))                    # pen on paper while she signs
    ev.append((wd + .66, S.norm(S.tick(), -30)))                                                # the pen set down
    ev.append((wv + .05, S.norm(S.clunk(), -34)))                                               # the handshake clasp
    wc = W("continuing", "c03_05")
    ev.append((wc - .05, S.norm(S.bed(.8, lo=600, hi=2400, mod=2.0), -30)))                     # fax printing
    ev.append((wc + .9, rustle(-30)))                                                           # he takes the page
    ev += [(wc + .8 + k * .03, rustle(-31)) for k in range(20)]                                 # the pile refills
    return ev


def build(ws: Path):
    n = int(D * SR)
    fx = np.zeros(n, np.float32)
    for t, snd in events():
        s = max(0, int(t * SR)); e = min(n, s + len(snd))
        if e > s:
            fx[s:e] += snd[:e - s]
    sf.write(ws / "sfx.wav", np.stack([fx, fx], 1), SR)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(ws / "narration.wav"), "-i", str(ws / "sfx.wav"), "-filter_complex",
                    "[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[o]", "-map", "[o]", "-ar", "48000", "-ac", "2", str(ws / "mix.wav")], check=True)
    print("wrote", ws / "mix.wav")


if __name__ == "__main__":
    build(Path(sys.argv[1]))
