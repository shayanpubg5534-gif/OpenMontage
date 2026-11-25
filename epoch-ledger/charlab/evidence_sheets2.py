#!/usr/bin/env python3
"""Character lab (M2.3b): labelled evidence sheets from the look-development stills (Pillow only).

    python3 epoch-ledger/charlab/evidence_sheets2.py LOOKDEV2_DIR M23_STILLS_DIR RIG4_DIR OUT_DIR
"""
from __future__ import annotations

import sys
from pathlib import Path

from evidence_sheets import sheet


def main(ld, m23, rig4, out):
    ld, m23, rig4, out = Path(ld), Path(m23), Path(rig4), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    T = {"toon2": "improved toon", "editorial": "flat editorial", "hybrid": "hybrid painterly"}
    for env in ("bakery", "bank"):
        S = lambda n: ld / env / f"{n}.png"
        for c in ("elias", "nadia"):
            sheet(f"M2.3b · {c.title()} in the {env}: three treatments (rows) × medium, close-up, three-quarter, profile",
                  [[(f"{T[m]} · {v}", S(f"{m}_{c}_{v}")) for v in ("medium", "close", "three", "profile")] for m in T],
                  tile=(480, 270)).save(out / f"{env}_{c}_treatments.png")
        sheet(f"M2.3b · both characters in the {env} (wide): improved toon / flat editorial / hybrid painterly",
              [[(T[m], S(f"{m}_wide")) for m in T]], tile=(640, 360)).save(out / f"{env}_wide.png")
    E = lambda n: ld / "expr" / f"{n}.png"
    sheet("M2.3b · expressions, flat editorial, bank set: neutral, concern, smile, surprise",
          [[(f"{c} · {k}", E(f"expr_{c}_{k}")) for k in ("neutral", "concern", "smile", "surprise")] for c in ("elias", "nadia")],
          tile=(480, 270)).save(out / "expressions.png")
    sheet("M2.3b · progression in the bank set: Rig v4 (stored) → M2.3 → M2.3b flat editorial → M2.3b hybrid",
          [[("Rig v4 · stored frame", rig4 / "pb_30.4.png"), ("M2.3 · refined toon", m23 / "bank_toon_medium.png"),
            ("M2.3b · flat editorial", ld / "bank" / "editorial_elias_medium.png"), ("M2.3b · hybrid painterly", ld / "bank" / "hybrid_elias_medium.png")],
           [("Rig v4 · BigCart stored frame", rig4 / "bc_9.8.png"), ("M2.3 · toon close-up", m23 / "bank_toon_close.png"),
            ("M2.3b · editorial close-up", ld / "bank" / "editorial_elias_close.png"), ("M2.3b · hybrid close-up", ld / "bank" / "hybrid_elias_close.png")]],
          tile=(480, 270)).save(out / "progression.png")
    print("sheets →", out)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main(*sys.argv[1:5])
