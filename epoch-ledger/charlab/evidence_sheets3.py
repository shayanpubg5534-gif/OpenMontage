#!/usr/bin/env python3
"""Character lab (M2.3c): side-by-side evidence sheets, M2.3b (stock MakeHuman heads and hair) vs M2.3c (designed
geometry), both in the flat editorial treatment with identical cameras, poses, lights and sets (Pillow only).

    python3 epoch-ledger/charlab/evidence_sheets3.py M23B_STILLS M23C_STILLS OUT_DIR
"""
from __future__ import annotations

import sys
from pathlib import Path

from evidence_sheets import sheet

FACE = (.25, .13, .75, .63)       # head-and-shoulders crop of the 1920×1080 close shots (fractions; keeps 16:9)


def main(b, c, out):
    b, c, out = Path(b), Path(c), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    V = [("medium", "medium"), ("close", "close-up"), ("three", "three-quarter"), ("profile", "profile")]
    for env in ("bank", "bakery"):
        for who in ("elias", "nadia"):
            rows = [[(f"M2.3b · {lab}", b / env / f"editorial_{who}_{v}.png"), (f"M2.3c · {lab}", c / env / f"editorial_{who}_{v}.png")]
                    for v, lab in V]
            if env == "bank":
                rows.append([("M2.3b · back three-quarter", c / "m23b_back" / f"editorial_{who}_back.png"),
                             ("M2.3c · back three-quarter", c / env / f"editorial_{who}_back.png")])
            sheet(f"M2.3b → M2.3c · {who.title()} in the {env} (flat editorial; left: stock heads and hair, right: designed geometry)",
                  rows, tile=(800, 450)).save(out / f"{env}_{who}_m23b_vs_m23c.png")
        sheet(f"M2.3b → M2.3c · wide two-shot in the {env}",
              [[("M2.3b · flat editorial", b / env / "editorial_wide.png"), ("M2.3c · flat editorial", c / env / "editorial_wide.png")]],
              tile=(960, 540)).save(out / f"{env}_wide_m23b_vs_m23c.png")
    E = ["neutral", "concern", "smile", "surprise"]
    rows = []
    for who in ("elias", "nadia"):
        rows.append([(f"M2.3b · {who} · {k}", b / "expr" / f"expr_{who}_{k}.png") for k in E] + [("", None)])
        rows.append([(f"M2.3c · {who} · {k}", c / "expr" / f"expr_{who}_{k}.png") for k in E] +
                    [(f"M2.3c · {who} · blink", c / "blink" / f"expr_{who}_blink.png")])
    sheet("M2.3b → M2.3c · expressions (bank, close-up): the same shape keys now drive the designed brows and lash lines",
          rows, tile=(480, 270), crop=FACE).save(out / "expressions_m23b_vs_m23c.png")
    sheet("M2.3c · faces at a glance: close-up, three-quarter, profile, back (bank)",
          [[(f"{who} · {lab}", c / "bank" / f"editorial_{who}_{v}.png") for v, lab in
            [("close", "close-up"), ("three", "three-quarter"), ("profile", "profile"), ("back", "back")]] for who in ("elias", "nadia")],
          tile=(480, 270), crop=FACE).save(out / "m23c_faces.png")
    print("sheets →", out)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main(*sys.argv[1:4])
