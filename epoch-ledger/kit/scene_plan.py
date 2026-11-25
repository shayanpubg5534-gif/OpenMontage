"""Epoch Ledger scene plan — the mandatory design step between the script and any scene code.

Every shot is planned *before* it is built, and the plan records which guides were consulted and why each
technique was chosen, so the motion-craft skill, the component index and QUALITY.md demonstrably shape the work.

Plan file: JSON {"episode": ..., "shots": [shot, ...]}. Each shot needs:
  id, beat {t, narration}, understanding (what the viewer must grasp), shot (size), focal_point, camera (move or
  "locked" + why), lighting, technique [list], components [kit symbols reused], graphics [{kind, what, why?}],
  rationale, consulted [must include the three guides]. A beat "t" written as "a-b" (seconds) longer than MAX_HOLD
  needs a hold_reason: the narration moves through concepts, so the picture must too.
Validate with `python -m kit.scene_plan PLAN.json` (exit 1 on errors) or `validate(plan)` in tests.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SHOT_SIZES = ("establishing", "wide", "medium", "medium-close", "close-up", "insert", "chart", "map", "diagram")
TECHNIQUES = ("scene3d", "rig3", "rig", "lightfx", "diegetic", "motion.js", "three_kit", "iso", "map", "standalone-chart",
              "2.5d", "kinetic-type", "diagram", "photo-archive")
GRAPHIC_KINDS = ("diegetic", "standalone", "overlay", "caption")
REQUIRED_GUIDES = ("skills/creative/epoch-ledger-motion-craft.md", "epoch-ledger/COMPONENTS.md", "epoch-ledger/QUALITY.md")
MAX_HOLD = 6.0   # seconds one composition may carry narration before it needs a new action/shot (or a written hold_reason)
FIELDS = ("id", "beat", "understanding", "shot", "focal_point", "camera", "lighting", "technique", "components", "graphics", "rationale", "consulted")


def validate(plan: dict) -> list[str]:
    errs: list[str] = []
    shots = plan.get("shots") or []
    if not shots:
        return ["plan has no shots"]
    for s in shots:
        sid = s.get("id", "?")
        for f in FIELDS:
            if f not in s or s[f] in ("", [], None):
                errs.append(f"{sid}: missing {f}")
        if s.get("shot") not in SHOT_SIZES:
            errs.append(f"{sid}: shot size {s.get('shot')!r} not in {SHOT_SIZES}")
        for t in s.get("technique", []):
            if t not in TECHNIQUES:
                errs.append(f"{sid}: unknown technique {t!r}")
        for g in s.get("graphics", []):
            if g.get("kind") not in GRAPHIC_KINDS:
                errs.append(f"{sid}: graphic kind {g.get('kind')!r} not in {GRAPHIC_KINDS}")
            if g.get("kind") == "overlay" and len(g.get("why", "")) < 20:
                errs.append(f"{sid}: overlay graphic '{g.get('what')}' needs a 'why' (prefer diegetic or a standalone chart)")
        for guide in REQUIRED_GUIDES:
            if guide not in s.get("consulted", []):
                errs.append(f"{sid}: did not consult {guide}")
        beat = s.get("beat") or {}
        if not isinstance(beat, dict) or "narration" not in beat:
            errs.append(f"{sid}: beat must carry the narration it serves")
        t = str(beat.get("t", "")) if isinstance(beat, dict) else ""
        if "-" in t:
            try:
                a, b = (float(x) for x in t.split("-"))
                if b - a > MAX_HOLD and len(s.get("hold_reason", "")) < 20:
                    errs.append(f"{sid}: one composition holds {b - a:.1f}s of narration — give each beat its own action/shot, or write a hold_reason")
            except ValueError:
                pass
        if len(s.get("understanding", "")) < 15:
            errs.append(f"{sid}: 'understanding' must say what the viewer learns")
    # sequence rules: vary shot sizes, no long runs of the same framing
    sizes = [s.get("shot") for s in shots]
    run = 1
    for a, b in zip(sizes, sizes[1:]):
        run = run + 1 if a == b else 1
        if run > 3:
            errs.append(f"more than 3 consecutive '{b}' shots — vary the framing")
            break
    if len(shots) >= 3 and len(set(sizes)) < 2:
        errs.append("all shots share one size — plan establishing / medium / close coverage")
    return errs


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    plan = json.loads(Path(argv[0]).read_text())
    errs = validate(plan)
    for e in errs:
        print("✗", e)
    if not errs:
        print(f"✓ scene plan ok — {len(plan['shots'])} shots")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
