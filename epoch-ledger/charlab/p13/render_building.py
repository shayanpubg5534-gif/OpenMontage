"""P13 pilot: the three shots of the security building (scenes/building.js), timed from the resolved narration map,
rendered with three_shot.mjs in parallel frame ranges (static holds rendered once), joined, and given the series'
painterly pass (as P12's render_3d.sh).

    python3 epoch-ledger/charlab/p13/render_building.py RESOLVED_MAP.json OUT_DIR [WORKERS] [SHOT ...]

  B1 S5  issuance   from above, the pool (a match on the map's pool); floors rise on it as the camera lifts to 3/4
  B2 S7  payments   along the pipe: drops climb (the family's gold first), then windows light from the top down
  B3 S10 losses     close on the family's house as the pool turns red; the flow stops; the camera pulls back as the
                    flood rises through equity into mezzanine; senior stays above it, dimmed
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
FAM = [0.695, 0.16, 1.07]          # the family's house in the pool (scenes/building.js FAM)


def plan(R):
    E = {e["id"]: e["t"] for e in R["events"]}; SH = {s["id"]: s for s in R["shots"]}
    out = {}
    s = SH["S5"]; t0 = s["t0"]; L = lambda t: round(t - t0, 3); D = round(s["t1"] - t0, 3)
    out["B1"] = (D, [[0, [0, 6.4, 0.02], [0, 0, 0], 32], [L(E["e_floors"]), [0, 6.3, 0.1], [0, 0, 0], 32], [L(E["e_floors"]) + .6, [2.2, 2.3, 3.4], [0, .55, 0], 38],
                     [D, [2.55, 1.5, 3.3], [0, .82, 0], 38]],
                 {"build": [L(E["e_floors"]) + .2, L(E["e_floors"]) + 1.3], "lit": 0})
    s = SH["S7"]; t0 = s["t0"]; L = lambda t: round(t - t0, 3); D = round(s["t1"] - t0, 3)
    A, B = [2.3, .78, 2.3], [2.05, 1.1, 2.7]
    out["B2"] = (D, [[0, A, [.5, .8, .15], 35], [L(E["e_mezz"]) + .5, A, [.5, .8, .15], 35], [D, B, [.3, .92, 0], 36]],
                 {"flow": L(E["e_steady"]) - .05, "fill": [L(E["e_steady"]) + .15, L(E["e_steady"]) + 1.35]})
    s = SH["S10"]; t0 = s["t0"]; L = lambda t: round(t - t0, 3); D = round(s["t1"] - t0, 3)
    fx, fy, fz = FAM
    C0, C1 = ([fx + .55, .55, fz + .75], [fx, fy + .05, fz]), ([2.45, 1.0, 3.1], [0, .55, 0])
    out["B3"] = (D, [[0, *C0, 34], [L(E["e_dry"]) + .5, *C0, 34], [L(E["e_secs"]) - .25, *C1, 38], [L(E["e_collapse"]) + .7, *C1, 38], [D, [2.55, 1.12, 3.25], [0, .62, 0], 37.5]],
                 {"flow": -2.0, "stop": L(E["e_dry"]), "lit": 1, "red": [L(E["e_red"]), L(E["e_red"]) + 1.0],
                  "dim": [L(E["e_dry"]), L(E["e_dry"]) + .4], "flood": [L(E["e_secs"]), L(E["e_secs"]) + .4, 1 / 3],
                  "flood2": [L(E["e_collapse"]), L(E["e_collapse"]) + .45, .62]})
    return out


def render(sid, D, keys, ev, out, workers):
    N = round(D * 30); per = -(-N // workers); tmp = Path(tempfile.mkdtemp()); procs, parts = [], []
    for w in range(workers):
        a, b = w * per, min(N - 1, w * per + per - 1)
        if a >= N: break
        p = tmp / f"p{w}.mp4"; parts.append(p)
        procs.append(subprocess.Popen(["node", str(ROOT / "epoch-ledger/charlab/p12/three_shot.mjs"), str(HERE / "scenes/building.js"), str(p), str(D),
                                       json.dumps(keys), json.dumps(ev), "--from", str(a), "--to", str(b)], cwd=ROOT, stdout=subprocess.PIPE, text=True))
    logs = [json.loads(p.communicate()[0].strip().splitlines()[-1]) for p in procs]
    if any(p.returncode for p in procs): raise SystemExit(f"{sid}: a worker failed")
    (tmp / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(tmp / "raw.mp4")], check=True)
    paint = (ROOT / "epoch-ledger/charlab/p9/paint_filter.txt").read_text().strip()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp / "raw.mp4"), "-filter_complex", f"{paint},vignette=angle=0.4,noise=alls=4:allf=t,format=yuv420p",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:v", "libx264", "-preset", "medium", "-crf", "16", str(out)], check=True)
    return {"shot": sid, "frames": N, "rendered": sum(l["rendered"] for l in logs)}


def main(resolved, out_dir, workers=4, *only):
    R = json.load(open(resolved)); P = plan(R); os.makedirs(out_dir, exist_ok=True)
    for sid, (D, keys, ev) in P.items():
        if only and sid not in only: continue
        print(json.dumps(render(sid, D, keys, ev, Path(out_dir) / f"shot{sid}.mp4", int(workers))))


if __name__ == "__main__":
    main(*sys.argv[1:])
