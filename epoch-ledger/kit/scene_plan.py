"""Epoch Ledger scene plan — the design step between the brief and any scene code (STANDARD.md §5).

Plan file: JSON {"episode": ..., "shots": [shot, ...]}. Each shot needs (errors if missing):
  id, beat {t, narration}, understanding (what the viewer must grasp), shot (size), focal_point, technique [list],
  graphics [{kind, what, why?}], rationale. Timed shots (beat "t" written "a-b") also need meaning {what, why,
  consequence}. Overlay graphics need a why. Recommended (warnings): camera, lighting, components; "consulted" is
  optional.
Pacing and framing numbers (MAX_HOLD, MIN_SHOT, MAX_CUTS_PER_10S, runs of one size) are *warnings*: pacing serves
comprehension, so the director may exceed them with a hold_reason / insert_reason or accept them knowingly.
With "direction": 2 (STANDARD §3A, opt-in) every shot also names its `world`, a `transition_in` with a motive, and
`acting` (who / wants / does / feels) when characters are on screen. `python -m kit.scene_plan PLAN.json` exits 1 on errors only. In code: validate(plan) -> errors; review(plan) ->
{"errors", "warnings"}.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SHOT_SIZES = ("establishing", "wide", "medium", "medium-close", "close-up", "insert", "chart", "map", "diagram")
TECHNIQUES = ("scene3d", "rig3", "rig", "lightfx", "diegetic", "motion.js", "three_kit", "iso", "map", "standalone-chart",
              "2.5d", "kinetic-type", "diagram", "photo-archive")
GRAPHIC_KINDS = ("diegetic", "standalone", "overlay", "caption")
REQUIRED_GUIDES = ("skills/creative/epoch-ledger-motion-craft.md", "epoch-ledger/COMPONENTS.md", "epoch-ledger/QUALITY.md")
MAX_HOLD = 6.0   # seconds one composition carries narration before the checker asks for a hold_reason
MIN_SHOT = 2.0   # seconds a composition needs to be recognised and understood (inserts: 0.5 s, with insert_reason)
MAX_CUTS_PER_10S = 4   # pacing hint: more composition changes than this in any 10 s window often reads as frantic
FIELDS = ("id", "beat", "understanding", "shot", "focal_point", "technique", "graphics", "rationale")        # required (errors)
MINOR_ACTING = {"head", "turns", "turn", "nods", "nod", "blinks", "blink", "tilts", "tilt", "mouth", "eyes", "looks", "look",
                "smiles", "smile", "his", "her", "their", "the", "a", "and", "slightly", "at", "to", "she", "he", "they"}
ADVISED = ("camera", "lighting", "components")                                                              # recommended (warnings)


def validate(plan: dict) -> list[str]:
    """Errors only (objective problems) — backward compatible. Use review() for errors and pacing warnings."""
    return review(plan)["errors"]


def review(plan: dict) -> dict:
    """{'errors': [...], 'warnings': [...]}. Errors: missing meaning / fields, unknown kinds, unexplained overlays.
    Warnings: pacing and framing heuristics (STANDARD §3 — the director may exceed them with a reason)."""
    errs: list[str] = []
    warns: list[str] = []
    timed: list[tuple[float, float]] = []
    shots = plan.get("shots") or []
    if not shots:
        return {"errors": ["plan has no shots"], "warnings": []}
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
        for f in ADVISED:
            if not s.get(f):
                warns.append(f"{sid}: no {f} noted")
        beat = s.get("beat") or {}
        if not isinstance(beat, dict) or "narration" not in beat:
            errs.append(f"{sid}: beat must carry the narration it serves")
        t = str(beat.get("t", "")) if isinstance(beat, dict) else ""
        if "-" in t:
            try:
                a, b = (float(x) for x in t.split("-"))
            except ValueError:
                a = b = None
            if a is not None:
                timed.append((a, b))
                if b - a > MAX_HOLD and len(s.get("hold_reason", "")) < 20:
                    warns.append(f"{sid}: one composition holds {b - a:.1f}s of narration — give each concept its own action or progressive build, or write a hold_reason")
                short = MIN_SHOT if s.get("shot") != "insert" else .5
                if b - a < short and len(s.get("hold_reason", "") + s.get("insert_reason", "")) < 15:
                    warns.append(f"{sid}: {b - a:.2f}s on screen is too short to recognise and absorb (min {short}s) — merge related ideas into one connected composition")
                if s.get("shot") == "insert" and len(s.get("insert_reason", "")) < 15:
                    warns.append(f"{sid}: an insert needs an insert_reason (what small decisive action it makes legible)")
                m = s.get("meaning") or {}
                for k in ("what", "why", "consequence"):
                    if len(str(m.get(k, ""))) < 6:
                        errs.append(f"{sid}: meaning.{k} missing — say what happens, why, and what follows before designing visuals")
        if len(s.get("understanding", "")) < 15:
            errs.append(f"{sid}: 'understanding' must say what the viewer learns")
    # creative direction (STANDARD §3A), opt-in with "direction": 2 so earlier plans are unchanged: every shot says
    # where it happens, how it is entered, and what any character physically does
    if plan.get("direction", 1) >= 2:
        for s in shots:
            sid = s.get("id", "?")
            if not s.get("world"): errs.append(f"{sid}: direction 2: name the 'world' (the story place) or 'abstract: <reason>'")
            tr = s.get("transition_in") or {}
            if s is not shots[0] and len(str(tr.get("motive", ""))) < 10:
                errs.append(f"{sid}: direction 2: 'transition_in' needs a motive (match cut, follow the object, reveal, …)")
            people = {"rig", "rig3", "2.5d"} & set(s.get("technique", []))
            if people and not s.get("acting"):
                errs.append(f"{sid}: direction 2: a shot with characters needs 'acting' (who wants / does / feels)")
            for a in s.get("acting", []):
                words = set(re.findall(r"[a-z]+", str(a.get("does", "")).lower()))
                if words and words <= MINOR_ACTING:
                    warns.append(f"{sid}: acting for {a.get('who', '?')} is only head, eye or mouth movement: add a story action or frame an insert")
    # pacing: composition changes per 10 s window
    starts = sorted(a for a, _ in timed)
    for a in starts:
        n = sum(1 for x in starts if a <= x < a + 10)
        if n > MAX_CUTS_PER_10S:
            warns.append(f"{n} compositions start within 10 s from {a:.1f}s — too many changes; combine related concepts with progressive animation")
            break
    # sequence rules: vary shot sizes, no long runs of the same framing
    sizes = [s.get("shot") for s in shots]
    run = 1
    for a, b in zip(sizes, sizes[1:]):
        run = run + 1 if a == b else 1
        if run > 3:
            warns.append(f"more than 3 consecutive '{b}' shots — vary the framing")
            break
    if len(shots) >= 3 and len(set(sizes)) < 2:
        warns.append("all shots share one size — consider establishing / medium / close coverage")
    return {"errors": errs, "warnings": warns}


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    plan = json.loads(Path(argv[0]).read_text())
    r = review(plan)
    errs, warns = r["errors"], r["warnings"]
    for e in errs:
        print("✗", e)
    for w in warns:
        print("⚠", w)
    if not errs:
        print(f"✓ scene plan ok — {len(plan['shots'])} shots, {len(warns)} warning(s) (answer with a reason or accept knowingly)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
