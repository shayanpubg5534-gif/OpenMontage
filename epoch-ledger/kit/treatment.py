"""Epoch Ledger creative treatment (STANDARD §3A): the direction step before any scene plan or code.

One concise `treatment.json` per episode (template: templates/episode/treatment.json; guide:
skills/creative/epoch-ledger-director.md):

  {"episode", "thesis": {"understand", "feel"}, "arc", "through_line",
   "worlds": [{"id", "place", "role", "build", "status": "new"|"reused"}], "motifs": [...], "signature",
   "sequences": [{"id", "narration", "hero": bool, "understand", "feel",
                  "concepts": [{"name", "kind", "idea", "verdict": "chosen"|"rejected", "why"}],
                  "accuracy": [...], "human_anchor" | "human_anchor_reason", "worlds": [ids],
                  "acting": [{"who", "wants", "does", "feels"}], "transitions": [{"to", "motive"}],
                  "storyboard": [{"frame", "shows"}], "approved": bool,
                  "pace": "hook|character|illustration|diagram|mechanism|emotional|transition", "steps": [...]}]}
                  (pace and steps: STANDARD §3B; the checker warns when the narration is too short for them)

Concept kinds: literal (the baseline: always considered, chosen only with a reason), metaphor, journey, mechanism,
human, data, reconstruction, other. The checker confirms the thinking was written down. It cannot judge whether it is
good: that is the director's review of the rendered frames (QUALITY.md).

    python -m kit.treatment episodes/<slug>/treatment.json [--gate motion] [--md OUT.md]
Exit 1 on errors. Writes treatment.md beside the JSON (for reading) unless --md says otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KINDS = ("literal", "metaphor", "journey", "mechanism", "human", "data", "reconstruction", "other")
BUILDS = ("2.5d", "3d", "plate", "map", "chart", "diagram", "document", "reconstruction", "mixed")
# acting that is only these is not acting (STANDARD §3A.4)
MINOR = {"head", "heads", "turn", "turns", "turning", "nod", "nods", "nodding", "blink", "blinks", "blinking", "tilt", "tilts",
         "mouth", "mouths", "eyes", "look", "looks", "looking", "smile", "smiles", "his", "her", "their", "the", "a", "and",
         "slightly", "at", "to", "up", "down", "camera", "she", "he", "they"}
USED = Path(__file__).resolve().parents[1] / "direction" / "used_devices.json"
# STANDARD §3B: each sequence may declare its pace and the steps it must teach; a mechanism or diagram needs about
# STEP_S seconds of narration per step (a guideline: lengthen or simplify the script when the narration is shorter)
PACES = ("hook", "character", "illustration", "diagram", "mechanism", "emotional", "transition")
PACE_MIN = {"hook": 1.5, "character": 5, "illustration": 3, "diagram": 6, "mechanism": 10, "emotional": 5, "transition": 1}
STEP_S = 3.0
WPS = 2.4          # narration words per second when no timing is given


def review(t: dict, base: Path | None = None, gate: str | None = None) -> dict:
    errs, warns = [], []
    th = t.get("thesis") or {}
    for k in ("understand", "feel"):
        if not th.get(k): errs.append(f"thesis: missing '{k}' (what the audience must understand / feel)")
    for k in ("through_line", "arc"):
        if not t.get(k): errs.append(f"missing '{k}'")
    worlds = {w.get("id"): w for w in t.get("worlds", [])}
    if not worlds: errs.append("no worlds (the story places the episode happens in)")
    for w in worlds.values():
        if w.get("build") not in BUILDS: errs.append(f"world {w.get('id')}: build {w.get('build')!r} not in {BUILDS}")
        if not w.get("role"): errs.append(f"world {w.get('id')}: missing 'role' (what happens there in the story)")
    if worlds and not any(w.get("status") == "new" for w in worlds.values()):
        warns.append("no new world: every place is reused (STANDARD 'reuse without repetition' asks for at least one new set or scene)")
    seqs = t.get("sequences") or []
    if not seqs: errs.append("no sequences")
    ids = {s.get("id") for s in seqs}
    heroes = [s for s in seqs if s.get("hero")]
    if len(heroes) > 5: warns.append(f"{len(heroes)} hero sequences: more than five spreads the production investment thin")
    for s in seqs:
        sid = s.get("id", "?")
        for k in ("understand", "feel", "narration"):
            if not s.get(k): errs.append(f"{sid}: missing '{k}'")
        cs = s.get("concepts") or []
        if len(cs) < 2: errs.append(f"{sid}: consider at least two concepts (one the literal baseline)")
        if not any(c.get("kind") == "literal" for c in cs): errs.append(f"{sid}: the literal baseline must be written down as a considered concept")
        for c in cs:
            if c.get("kind") not in KINDS: errs.append(f"{sid}: concept {c.get('name')!r} kind {c.get('kind')!r} not in {KINDS}")
            if not c.get("why"): errs.append(f"{sid}: concept {c.get('name')!r} needs a 'why' (chosen or rejected)")
        chosen = [c for c in cs if c.get("verdict") == "chosen"]
        if len(chosen) != 1: errs.append(f"{sid}: exactly one concept must be chosen ({len(chosen)} are)")
        elif chosen[0].get("kind") == "literal" and len(chosen[0].get("why", "")) < 40:
            errs.append(f"{sid}: the literal baseline is chosen: say why it beats the alternatives (≥ 40 characters)")
        if any(c.get("kind") in ("metaphor", "mechanism") for c in chosen) and not s.get("accuracy"):
            errs.append(f"{sid}: a metaphor or mechanism is chosen: write its accuracy notes (what it must not imply)")
        if not (s.get("human_anchor") or s.get("human_anchor_reason")):
            errs.append(f"{sid}: name the human anchor (who this happens to) or give a reason there is none")
        for w in s.get("worlds", []):
            if w not in worlds: errs.append(f"{sid}: unknown world {w!r}")
        for a in s.get("acting", []):
            for k in ("who", "wants", "does", "feels"):
                if not a.get(k): errs.append(f"{sid}: acting for {a.get('who', '?')} needs '{k}'")
            words = set(re.findall(r"[a-z]+", a.get("does", "").lower()))
            if words and words <= MINOR:
                errs.append(f"{sid}: acting for {a.get('who')} is only head, eye or mouth movement: give a story action (hands, posture, an object, a reaction)")
        for tr in s.get("transitions", []):
            if tr.get("to") not in ids | {"end"}: errs.append(f"{sid}: transition to unknown sequence {tr.get('to')!r}")
            if len(tr.get("motive", "")) < 10: errs.append(f"{sid}: transition to {tr.get('to')} needs a motive (match cut, follow the object, …)")
        if s.get("pace") is not None:                       # §3B pacing (sequences without a pace: as before)
            if s["pace"] not in PACES: errs.append(f"{sid}: pace {s['pace']!r} not in {PACES}")
            else:
                d = (s["t"][1] - s["t"][0]) if s.get("t") else len(str(s.get("narration", "")).split()) / WPS
                steps = s.get("steps") or []
                need = max(PACE_MIN[s["pace"]], STEP_S * len(steps) if s["pace"] in ("diagram", "mechanism") else 0)
                if d < need * .8:
                    warns.append(f"{sid}: narration too compressed: {d:.1f} s for a {s['pace']} with {len(steps)} step(s) "
                                 f"(guideline ≥ {need:.0f} s): lengthen or simplify the script (STANDARD §3B.10)")
        if s.get("hero") and gate == "motion":
            fr = s.get("storyboard") or []
            if not fr: errs.append(f"{sid}: hero sequence has no storyboard key frames (storyboard gate)")
            for f in fr:
                if base is not None and not (base / f.get("frame", "")).exists(): errs.append(f"{sid}: storyboard frame missing: {f.get('frame')}")
            if not s.get("approved"): errs.append(f"{sid}: storyboard not approved yet (approve hero key frames in one batch before animation)")
    if USED.exists() and t.get("signature"):
        used = json.loads(USED.read_text())
        for ep, sig in used.get("signatures", {}).items():
            if ep != t.get("episode") and sig.strip().lower() == t["signature"].strip().lower():
                warns.append(f"signature device already used by {ep}: {sig!r}")
        for s in seqs:
            for c in s.get("concepts", []):
                if c.get("verdict") == "chosen" and c.get("kind") == "metaphor":
                    prev = [ep for ep in used.get("metaphors", {}).get(c.get("name", "").lower(), []) if ep != t.get("episode")]
                    if prev: warns.append(f"{s.get('id')}: metaphor {c['name']!r} already used in {prev}: reuse only with a reason")
    return {"errors": errs, "warnings": warns}


def find(start: Path) -> Path | None:
    """the episode's treatment.json for a path inside the episode (the file's folder or its parents, up to 3 levels)"""
    p = Path(start).resolve(); p = p if p.is_dir() else p.parent
    for d in [p, *list(p.parents)[:3]]:
        if (d / "treatment.json").exists(): return d / "treatment.json"
    return None


def require(ep_dir: Path, gate: str = "motion") -> None:
    """the storyboard gate for builds: an episode WITH a treatment.json cannot be animated until its treatment checks
    and its hero storyboard is approved. Episodes without one (made before §3A) build as before. Set
    EPOCH_STORYBOARD=1 to build stills for the storyboard itself."""
    import os
    f = Path(ep_dir) / "treatment.json"
    if not f.exists() or os.environ.get("EPOCH_STORYBOARD") == "1": return
    r = review(json.loads(f.read_text()), f.parent, gate)
    if r["errors"]:
        raise SystemExit("creative direction (STANDARD §3A): the treatment is not ready for animation\n  " + "\n  ".join(r["errors"]) +
                         "\n(write it with the epoch-ledger-director skill; storyboard stills: EPOCH_STORYBOARD=1)")


def to_markdown(t: dict) -> str:
    """the readable view of a treatment (generated: edit the JSON)"""
    L = [f"# Treatment: {t.get('episode', '')}", "", "_Generated from treatment.json by kit/treatment.py; edit the JSON._", "",
         f"**Understand:** {t['thesis'].get('understand', '')}  ", f"**Feel:** {t['thesis'].get('feel', '')}  ",
         f"**Arc:** {t.get('arc', '')}  ", f"**Through-line:** {t.get('through_line', '')}  ",
         f"**Signature device:** {t.get('signature', '')}  ", f"**Motifs:** {', '.join(t.get('motifs', []))}", "",
         "## Worlds", "", "| World | Place | Role in the story | Built as | New |", "|---|---|---|---|---|"]
    L += [f"| {w['id']} | {w.get('place', '')} | {w.get('role', '')} | {w.get('build', '')} | {'new' if w.get('status') == 'new' else 'reused'} |" for w in t.get("worlds", [])]
    for s in t.get("sequences", []):
        L += ["", f"## {s['id']}{' (hero)' if s.get('hero') else ''}: {s.get('narration', '')}", "",
              f"- **Understand:** {s.get('understand', '')}", f"- **Feel:** {s.get('feel', '')}",
              f"- **Human anchor:** {s.get('human_anchor') or s.get('human_anchor_reason', '')}", "", "| Concept | Kind | Idea | Verdict | Why |", "|---|---|---|---|---|"]
        L += [f"| {c.get('name', '')} | {c.get('kind', '')} | {c.get('idea', '')} | **{c.get('verdict', '')}** | {c.get('why', '')} |" for c in s.get("concepts", [])]
        if s.get("pace"): L += ["", f"**Pace:** {s['pace']}" + (f" · **Steps:** " + " → ".join(s.get("steps", [])) if s.get("steps") else "")]
        if s.get("acting"): L += ["", "**Acting:** " + " · ".join(f"{a['who']}: wants {a['wants']}; does {a['does']}; feels {a['feels']}" for a in s["acting"])]
        if s.get("accuracy"): L += ["", "**Accuracy:** " + " ".join(s["accuracy"])]
        if s.get("transitions"): L += ["", "**Transitions:** " + " · ".join(f"→ {x['to']}: {x['motive']}" for x in s["transitions"])]
        if s.get("storyboard"): L += ["", "**Storyboard:** " + " · ".join(f"`{f['frame']}` ({f.get('shows', '')})" for f in s["storyboard"])]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("treatment", type=Path); ap.add_argument("--gate", choices=["motion"]); ap.add_argument("--md", type=Path)
    a = ap.parse_args(argv)
    t = json.loads(a.treatment.read_text()); r = review(t, a.treatment.parent, a.gate)
    for e in r["errors"]: print("ERROR", e)
    for w in r["warnings"]: print("warn ", w)
    (a.md or a.treatment.with_suffix(".md")).write_text(to_markdown(t))
    print(json.dumps({"sequences": len(t.get("sequences", [])), "errors": len(r["errors"]), "warnings": len(r["warnings"])}))
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
