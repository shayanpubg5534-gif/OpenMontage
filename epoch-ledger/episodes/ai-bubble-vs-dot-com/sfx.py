"""Original sound design (synthesised — no samples, no licences) mixed under the narration.

  python epoch-ledger/episodes/ai-bubble-vs-dot-com/sfx.py WORKSPACE [WORKSPACE ...]

Writes WORKSPACE/mix.wav = narration + effects. Effects are keyed to narration word times through
timeline.py, sit 18–26 dB under the voice, and are deterministic (seeded noise).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from timeline import D, L, W  # noqa: E402

SR = 48000
RNG = np.random.default_rng(1999)


def noise(n):
    return RNG.standard_normal(n).astype(np.float32)


def lowpass(x, hz):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / hz) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def highpass(x, hz):
    return x - lowpass(x, hz)


def env(n, a=.02, r=.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (n / SR - t) / max(r, 1e-4))
    return np.clip(e, 0, 1).astype(np.float32)


def norm(x, peak_db):
    p = np.max(np.abs(x)) or 1
    return x / p * 10 ** (peak_db / 20)


# ── sound primitives ────────────────────────────────────────────────
def whoosh(d=.9, hi=3000):
    n = int(d * SR); x = noise(n)
    halves = [lowpass(x[i:i + n // 8], hi * (0.2 + 0.8 * np.sin(np.pi * i / n))) for i in range(0, n, n // 8)]
    return np.concatenate(halves)[:n] * env(n, d * .45, d * .5)


def hum(d, f0=55):
    t = np.arange(int(d * SR)) / SR
    x = .5 * np.sin(2 * np.pi * f0 * t) + .3 * np.sin(2 * np.pi * 2 * f0 * t) + .15 * np.sin(2 * np.pi * 3 * f0 * t)
    x = x + .25 * lowpass(noise(len(t)), 300)
    return x.astype(np.float32) * env(len(t), .8, .8)


def tick():
    n = int(.012 * SR); return highpass(noise(n), 2000) * np.exp(-np.arange(n) / (SR * .002)).astype(np.float32)


def clunk():
    n = int(.25 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 70 * t) * np.exp(-t / .05) + .4 * lowpass(noise(n), 900) * np.exp(-t / .02)).astype(np.float32)


def pop():
    n = int(.35 * SR); t = np.arange(n) / SR
    return (lowpass(noise(n), 4000) * np.exp(-t / .03) + .8 * np.sin(2 * np.pi * 55 * t) * np.exp(-t / .08)).astype(np.float32)


def bed(d, lo=None, hi=None, mod=0.0):
    n = int(d * SR); x = noise(n)
    if hi: x = lowpass(x, hi)
    if lo: x = highpass(x, lo)
    if mod: x *= (1 + mod * np.sin(2 * np.pi * .23 * np.arange(n) / SR)).astype(np.float32)
    return x * env(n, 1.0, 1.0)


def sweep(d, f0, f1):
    t = np.arange(int(d * SR)) / SR
    f = f0 + (f1 - f0) * (t / d) ** 2
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .1, .4)).astype(np.float32)


def chime(f=1760):
    t = np.arange(int(1.2 * SR)) / SR
    return ((np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t / .35)).astype(np.float32)


def coin():
    t = np.arange(int(.4 * SR)) / SR
    return ((np.sin(2 * np.pi * 2600 * t) + .7 * np.sin(2 * np.pi * 3900 * t)) * np.exp(-t / .07)).astype(np.float32)


def chuffs(d, rate=3.0):
    n = int(d * SR); out = np.zeros(n, np.float32)
    for k in range(int(d * rate)):
        s = int(k / rate * SR); m = int(.18 * SR)
        b = lowpass(noise(m), 1200) * np.exp(-np.arange(m) / (SR * .05)).astype(np.float32)
        out[s:s + m] += b[:max(0, min(m, n - s))]
    return out * env(n, .5, .8)


def whistle(d=1.3):
    t = np.arange(int(d * SR)) / SR
    v = 1 + .004 * np.sin(2 * np.pi * 6 * t)
    return ((np.sin(2 * np.pi * 740 * v * t) + .6 * np.sin(2 * np.pi * 932 * v * t)) * env(len(t), .08, .3)).astype(np.float32)


def events():
    """(time, sound, peak dBFS) — all keyed to narration."""
    ev = []
    o3 = L("c01_03")[0]; c4 = L("c01_04"); c5 = L("c01_05")[0]; c6 = L("c01_06")[0]; c7 = L("c01_07")
    ev += [(0.0, norm(bed(o3 + .2, hi=700, mod=.4), -27), 0),            # trading-floor murmur
           *[(i * .21, norm(tick(), -32), 0) for i in range(int(o3 / .21))],  # ticker clicks
           (W("trillions", "c01_03") - .4, norm(sweep(1.4, 900, 120), -30), 0),
           (W("trillions", "c01_03") - .3, norm(whoosh(.9), -28), 0),
           *[(W("Companies", "c01_04") + .25 + i * .22, norm(clunk(), -24), 0) for i in range(6)],
           (c4[1] - 1.05, norm(pop(), -20), 0),
           (c5 - .1, norm(whoosh(1.6, 2200), -24), 0),
           (c5 + .4, norm(hum(c7[0] - c5 - .2), -28), 0),
           (c6 - .2, norm(sweep(1.6, 80, 520), -27), 0),
           (c7[0] - .25, norm(whoosh(.7), -27), 0), (W("Semiconductor", "c01_07") - .2, norm(whoosh(.6), -28), 0),
           (W("Semiconductor", "c01_07") + .4, norm(chime(1568), -30), 0), (W("Investors", "c01_07") - .25, norm(whoosh(.6), -28), 0)]
    s9 = L("c03_09")[0]; e11 = L("c03_11")[1]
    ev += [(s9 - .5, norm(bed(e11 - s9 + 1, lo=1500, hi=9000), -30), 0),       # rain
           (W("declining", "c03_09") + .2, norm(bed(2.5, hi=140), -26), 0),    # distant rumble
           *[(W("Companies", "c03_11") + .1 + i * .09, norm(clunk(), -30), 0) for i in range(0, 15, 3)],
           (L("c03_12")[0] - .45, norm(whoosh(.8), -28), 0),
           (W("bottom", "c03_12") - 1.2, norm(sweep(1.4, 600, 90), -31), 0),
           *[(W("fallen", "c03_14") + i * .24, norm(coin(), -34), 0) for i in range(8)]]
    i5 = L("c04_05")[0]
    ev += [*[(i5 + .4 + k * .09, norm(tick(), -36), 0) for k in range(24)],
           (W("physical", "c04_06") - .2, norm(whoosh(1.2, 3500), -24), 0),
           (W("physical", "c04_06") + .4, norm(hum(L("c04_10")[0] - W("physical", "c04_06")), -30), 0),
           (L("c04_08")[0] - .25, norm(whoosh(.6), -28), 0), (L("c04_09")[0], norm(bed(3.0, lo=300, hi=2500), -31), 0),
           (L("c04_10")[0] - .25, norm(whoosh(.6), -28), 0), (W("energy", "c04_10"), norm(hum(5.5, 60), -27), 0),
           *[(L("c04_11")[0] + .3 + i * .12, norm(coin(), -36), 0) for i in range(12)]]
    m = {k: L(f"c05_{k:02d}")[0] for k in range(1, 16)}
    ev += [(m[1] - .4, norm(whoosh(1.0), -28), 0), *[(m[k] + .1, norm(chime(1046 + 130 * k), -33), 0) for k in (2, 3, 4, 5)],
           *[(W("investing", "c05_13") + i * .15, norm(coin(), -32), 0) for i in range(4)],
           (W("purchases", "c05_15") + 1.0, norm(chime(1318), -30), 0)]
    d2 = L("c06_02")[0]
    ev += [(d2 - .45, norm(whoosh(.8), -29), 0), (W("$10", "c06_02"), norm(tick(), -26), 0), (W("$6", "c06_03"), norm(tick(), -26), 0),
           (W("$14", "c06_04"), norm(sweep(1.6, 300, 120), -31), 0), (L("c06_05")[0], norm(clunk(), -25), 0),
           *[(W(x, "c06_06"), norm(tick(), -27), 0) for x in ("existing", "sell", "raise", "borrow")]]
    r1, r2 = L("c07_12"), L("c07_13")
    ev += [(r1[0] - .5, norm(chuffs(r2[0] - r1[0] + .5), -27), 0), (r1[0] + 1.2, norm(whistle(), -28), 0),
           (r2[0] - .1, norm(bed(r2[1] - r2[0] + .6, hi=500, mod=.6), -29), 0)]
    return ev


def build(workspaces):
    n = int((D + 1) * SR)
    fx = np.zeros(n, np.float32)
    for t, snd, _ in events():
        s = max(0, int(t * SR)); e = min(n, s + len(snd))
        fx[s:e] += snd[:e - s]
    for ws in workspaces:
        ws = Path(ws)
        nar = ws / "narration.wav"
        if not nar.exists():
            src = HERE.parents[2] / "projects" / HERE.name / "hyperframes" / "narration.wav"
            nar.write_bytes(src.read_bytes())
        sf.write(ws / "sfx.wav", np.stack([fx, fx], 1), SR)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(nar), "-i", str(ws / "sfx.wav"), "-filter_complex",
                        "[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[o]", "-map", "[o]",
                        "-ar", "48000", "-ac", "2", str(ws / "mix.wav")], check=True)
        print("wrote", ws / "mix.wav")


if __name__ == "__main__":
    build(sys.argv[1:] or [HERE.parents[2] / "projects" / HERE.name / "hyperframes"])
