#!/usr/bin/env python3
"""Character lab (M3): contact sheets from rendered motion demos (Pillow only).

    python3 epoch-ledger/charlab/motion_sheets.py FRAMES_DIR OUT_DIR

FRAMES_DIR holds one folder of PNG frames per demo (f0000.png …), as written by motion_render.mjs. For each demo, a
sheet of 12 evenly spaced frames with their times; plus a lean-vs-standard comparison where a *_lean folder exists.
"""
from __future__ import annotations

import sys
from pathlib import Path

from evidence_sheets import sheet

TITLES = {"d1_arrival": "D1 · arrival (bakery): Nadia starts walking with a bag, stops; Elias tracks her, eye contact, nod",
          "d2_sit": "D2 · sit (bank): Elias invites; Nadia steps, turns, sits on the chair, settles, keeps eye contact, stands up",
          "d3_conversation": "D3 · conversation (bank): restrained explanation, listening, glance away and back, nods, expression shifts",
          "d4_handoff": "D4 · hand-off (bank): pick up, offer, both hold, take, read, point; eye contact and nod"}


def main(frames, out):
    frames, out = Path(frames), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for d in sorted(p for p in frames.iterdir() if p.is_dir() and not p.name.endswith("_lean")):
        fs = sorted(d.glob("f*.png"))
        if not fs:
            continue
        pick = [fs[round(i * (len(fs) - 1) / 11)] for i in range(12)]
        rows = [[(f"t = {int(p.stem[1:]) / 30:.1f} s", p) for p in pick[r * 4:(r + 1) * 4]] for r in range(3)]
        sheet(f"M3 · {TITLES.get(d.name, d.name)}", rows, tile=(640, 360)).save(out / f"{d.name}_sheet.png")
        lean = frames / f"{d.name}_lean"
        if lean.exists():
            ts = [pick[3], pick[7]]
            sheet(f"M3 · {d.name}: standard (MSAA ×4, 2048 shadow map, interior ink) vs lean (no MSAA, 1024, no interior ink)",
                  [[(f"standard · t = {int(p.stem[1:]) / 30:.1f} s", p), (f"lean · t = {int(p.stem[1:]) / 30:.1f} s", lean / p.name)] for p in ts],
                  tile=(960, 540)).save(out / f"{d.name}_standard_vs_lean.png")
    print("sheets →", out)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main(*sys.argv[1:3])
