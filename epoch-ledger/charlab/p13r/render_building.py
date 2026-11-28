"""P13R: the two long building compositions (P13's scenes/building.js and renderer, unchanged), timed from the resolved
P13R map. The camera is calm: it holds while labels are read and moves only to lead the eye to the next part.

    python3 epoch-ledger/charlab/p13r/render_building.py RESOLVED_MAP.json OUT_DIR [WORKERS] [SHOT ...]

  B1 S5 (17 s) issuance → three tranches (simplified example) → payments up the pipe → paid from the top down
  B2 S9 (14.6 s) the losses: from their red house at the foundation; equity floods on "wiped", mezzanine on "next";
     the camera tilts up to the senior floors, which stay lit (still paid in this example) while the overlay marks the
     rating cut and the fall in market value
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "p13"))
from render_building import FAM, render  # noqa: E402  (P13's renderer, unchanged)


def plan(R):
    E = {e["id"]: e["t"] for e in R["events"]}; SH = {s["id"]: s for s in R["shots"]}; out = {}
    s = SH["S5"]; t0 = s["t0"]; L = lambda t: round(t - t0, 3); D = round(s["t1"] - t0, 3)
    TOP = ([0, 6.4, 0.02], [0, 0, 0], 32); HIGH = ([2.5, 1.6, 3.3], [0, .82, 0], 38)
    PIPE = ([2.35, .9, 2.45], [.5, .8, .15], 35); UP = ([2.3, 1.15, 2.5], [.4, 1.12, .1], 35)
    out["B1"] = (D, [[0, *TOP], [L(E["e_issued"]), *TOP], [L(E["e_issued"]) + 1.7, *HIGH], [L(E["e_month"]), *HIGH], [L(E["e_month"]) + 1.4, *PIPE],
                     [L(E["e_top"]), *PIPE], [L(E["e_top"]) + .9, *UP], [D, [2.25, 1.18, 2.4], [.38, 1.1, .1], 35]],
                 {"build": [L(E["e_issued"]) + .15, L(E["e_issued"]) + 1.75], "lit": 0, "flow": L(E["e_flow"]) - .1,
                  "fill": [L(E["e_senior"]) + .1, L(E["e_below"]) + 1.3]})
    s = SH["S9"]; t0 = s["t0"]; L = lambda t: round(t - t0, 3); D = round(s["t1"] - t0, 3)
    fx, fy, fz = FAM
    C0 = ([fx + .55, .55, fz + .75], [fx, fy + .05, fz], 34); WIDE = ([2.45, 1.0, 3.1], [0, .55, 0], 38); SEN = ([2.4, 1.3, 3.0], [0, 1.0, 0], 38)
    out["B2"] = (D, [[0, *C0], [.5, *C0], [L(E["e_equity"]) - .3, *WIDE], [L(E["e_seniorup"]), *WIDE], [L(E["e_seniorup"]) + 1.0, *SEN],
                     [L(E["e_real"]), *SEN], [D, [2.55, 1.2, 3.25], [0, .9, 0], 37.5]],
                 {"flow": -2.0, "lit": 1, "red": [0.05, 1.05], "dim": [L(E["e_equity"]), L(E["e_equity"]) + .5],
                  "flood": [L(E["e_equity"]), L(E["e_equity"]) + .6, 1 / 3], "flood2": [L(E["e_mezz"]), L(E["e_mezz"]) + .6, .62]})
    return out


def main(resolved, out_dir, workers=4, *only):
    R = json.load(open(resolved)); P = plan(R); os.makedirs(out_dir, exist_ok=True)
    for sid, (D, keys, ev) in P.items():
        if only and sid not in only: continue
        print(json.dumps(render(sid, D, keys, ev, Path(out_dir) / f"shot{sid}.mp4", int(workers))))


if __name__ == "__main__":
    main(*sys.argv[1:])
