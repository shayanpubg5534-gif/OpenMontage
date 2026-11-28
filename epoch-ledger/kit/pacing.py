"""Epoch Ledger pacing diagnostics (STANDARD §3B: viewer comprehension and visual pacing).

Diagnostics, not proof: the film is judged by watching it once at normal speed (QUALITY.md, "First viewing"). Every
threshold below is a guideline from §3B, fixed before any film was tuned against it, and adapts to each shot's `pace`.

    python -m kit.pacing plan MAP.json [--out DIR]           # before building: load, reading time, focal points
    python -m kit.pacing film MAP.json VIDEO.mp4 [--out DIR] # on the render: picture changes, holds, motion
Exit 1 when a finding is "high" (very likely too dense to follow on a first viewing).

PLAN (a narration-to-visual map, charlab/p11/visual_map.py format; or a scene_plan.json with beat "t": "a-b"):
  shots [{id, t0, t1, pace}]     pace ∈ PACE (default "illustration" when missing, reported)
  events [{anchor|t, medium, held?}]   cut = a new composition; camera = motion; others = a new element
  text [{text, t0, t1, role}]    on-screen text; t0/t1 seconds or anchors {word, n, offset}; role key | support
  words: path to words.json      (anchors and the captions the viewer is also reading)

What is measured (cognitive load = everything that asks for attention, motion included, §3B.4):
  - composition duration against its pace;
  - text on screen against a minimum reading time while captions run: 0.5 s + words ÷ 3 after it is revealed
    (support text: 70 % of that);
  - focal competition: three or more introductions within 0.6 s (a label arriving with the visual it names counts
    once);
  - load per 10 s window (sliding, 1 s step): new compositions × 3, new elements × 1, camera moves × 0.5, on-screen
    text words ÷ 5, caption words ÷ 10, against a budget set by the window's pace;
  - new compositions per 10 s against the pace's budget;
  - on the film: major picture changes per 10 s, motion energy where the viewer must read, holds.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# §3B.7 — typical composition durations (s) per pace, and the budgets they imply per 10 s
PACE = {"hook": (1.5, 4), "character": (5, 8), "illustration": (3, 5), "diagram": (6, 12), "mechanism": (10, 20),
        "emotional": (5, 10), "transition": (1, 2)}
LOAD_BUDGET = {"hook": 14, "transition": 14, "character": 9, "illustration": 9, "diagram": 10, "mechanism": 10, "emotional": 6}
COMP_BUDGET = {"hook": 4, "transition": 4, "character": 2, "illustration": 2, "diagram": 2, "mechanism": 1.5, "emotional": 1.5}
FILM_CHANGE_BUDGET = {"hook": 6, "transition": 6, "character": 3, "illustration": 3, "diagram": 3, "mechanism": 3, "emotional": 2}
READ_PACES = ("diagram", "mechanism", "illustration")         # where calm motion matters most for reading
MOTION_BUSY = 9.0                                              # mean |Δ| (0–255, 10 fps, 160×90) that reads as busy
MAJOR = 12.0                                                   # one frame step this large reads as a new picture


def _norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())


def _words(path):
    if not path: return []
    w = json.loads((ROOT / path).read_text()) if not Path(path).is_absolute() else json.loads(Path(path).read_text())
    return w if isinstance(w, list) else w["words"]


def _at(words, a):
    """seconds for a number or an anchor {word, n, offset}"""
    if isinstance(a, (int, float)): return float(a)
    k, n = _norm(a["word"]), a.get("n", 1)
    hits = [i for i, w in enumerate(words) if _norm(w["word"]) == k]
    if len(hits) < n: raise ValueError(f"anchor {a} not in the narration")
    return words[hits[n - 1]]["start"] + a.get("offset", 0.0)


def load_plan(path: Path) -> dict:
    """a visual map or a scene plan, normalised to {duration, shots, events, text, words}"""
    m = json.loads(Path(path).read_text()); words = _words(m.get("words"))
    shots = []
    for s in m["shots"]:
        if "t0" in s: a, b = s["t0"], s["t1"]
        else: a, b = (float(x) for x in str(s.get("beat", {}).get("t", "0-0")).split("-"))
        shots.append({"id": s["id"], "t0": a, "t1": b, "pace": s.get("pace"), "pace_given": "pace" in s})
    ev = []
    for e in m.get("events", []):
        t = e["t"] if "t" in e else _at(words, {**e["anchor"], "offset": e.get("offset", 0.0)})
        ev.append({"id": e.get("id"), "t": t, "medium": e.get("medium"), "held": bool(e.get("held"))})
    text = [{"text": x["text"], "t0": _at(words, x["t0"]), "t1": _at(words, x["t1"]), "role": x.get("role", "key")} for x in m.get("text", [])]
    dur = m.get("duration") or max(s["t1"] for s in shots)
    return {"duration": dur, "shots": sorted(shots, key=lambda s: s["t0"]), "events": sorted(ev, key=lambda e: e["t"]), "text": text, "words": words}


def _pace_at(P, t):
    for s in P["shots"]:
        if s["t0"] <= t < s["t1"]: return s["pace"] or "illustration"
    return "illustration"


def _window_budget(P, a, table):
    """time-weighted budget of the paces inside [a, a+10)"""
    tot = 0.0
    for k in range(10): tot += table[_pace_at(P, a + k + .5)]
    return tot / 10


def _ranges(items):
    """merge consecutive window findings ({a, value, budget}) into ranges"""
    out = []
    for it in items:
        if out and it["a"] - out[-1]["b"] <= 1.0: out[-1]["b"] = it["a"]; out[-1]["peak"] = max(out[-1]["peak"], it["ratio"])
        else: out.append({"a": it["a"], "b": it["a"], "peak": it["ratio"], "budget": it["budget"]})
    return out


def check_plan(P: dict) -> dict:
    F = []
    add = lambda sev, where, msg: F.append({"severity": sev, "where": where, "msg": msg})
    for s in P["shots"]:
        if not s["pace_given"]: add("info", s["id"], "no pace declared; judged as 'illustration'")
        p = s["pace"] or "illustration"; lo, hi = PACE[p]; d = s["t1"] - s["t0"]
        if p not in ("transition", "hook") and d < .4 * lo: add("high", s["id"], f"{d:.1f} s for {('an' if p[0] in 'aeiou' else 'a')} {p} composition (guideline {lo}–{hi} s): far too short to absorb")
        elif d < .75 * lo: add("medium", s["id"], f"{d:.1f} s for {('an' if p[0] in 'aeiou' else 'a')} {p} composition (guideline {lo}–{hi} s)")
    for x in P["text"]:
        n = len(x["text"].split()); need = (0.5 + n / 3) * (0.7 if x["role"] == "support" else 1.0); vis = x["t1"] - x["t0"] - 0.3
        if vis < .6 * need: add("high", f"{x['t0']:.1f}s", f"\"{x['text']}\" readable for {max(0, vis):.1f} s; minimum ≈ {need:.1f} s with captions running")
        elif vis < need: add("medium", f"{x['t0']:.1f}s", f"\"{x['text']}\" readable for {vis:.1f} s; minimum ≈ {need:.1f} s")
    # a label that arrives with the visual it names (within 0.15 s) is one introduction, not two
    ev_t = [e["t"] for e in P["events"] if not e["held"] and e["medium"] not in ("camera",)]
    intro = [(e["t"], e["id"]) for e in P["events"] if not e["held"] and e["medium"] not in ("camera",)] + \
            [(x["t0"], x["text"][:24]) for x in P["text"] if not any(abs(x["t0"] - t) <= .15 for t in ev_t)]
    intro.sort()
    for i in range(len(intro)):
        grp = [b for t, b in intro[i:] if t - intro[i][0] <= 0.6]
        if len(grp) >= 3 and (i == 0 or intro[i][0] - intro[i - 1][0] > .6):
            add("medium", f"{intro[i][0]:.1f}s", f"{len(grp)} things introduced within 0.6 s ({', '.join(map(str, grp[:4]))}): one focal point at a time")
    cw = P["words"]
    over_load, over_comp, series = [], [], []
    for a in range(0, max(1, int(P["duration"] - 9))):
        b = a + 10
        comps = sum((1.5 if (s["pace"] == "transition") else 3) for s in P["shots"] if a <= s["t0"] < b and s["t0"] > 0)
        elem = sum(0.5 if e["medium"] == "camera" else 1 for e in P["events"] if a <= e["t"] < b and not e["held"] and e["medium"] != "cut")
        txt = sum(len(x["text"].split()) / 5 for x in P["text"] if a <= x["t0"] < b)
        cap = sum(1 for w in cw if a <= w["start"] < b) / 10
        load = comps + elem + txt + cap; bud = _window_budget(P, a, LOAD_BUDGET)
        ncomp = sum(1 for s in P["shots"] if a <= s["t0"] < b and s["t0"] > 0); cb = _window_budget(P, a, COMP_BUDGET)
        series.append({"a": a, "load": round(load, 1), "budget": round(bud, 1), "compositions": ncomp, "comp_budget": round(cb, 1)})
        if load > bud: over_load.append({"a": a, "ratio": load / bud, "budget": bud})
        if ncomp > cb: over_comp.append({"a": a, "ratio": ncomp / cb, "budget": cb})
    for r in _ranges(over_load):
        add("high" if r["peak"] > 1.5 else "medium", f"{r['a']}–{r['b'] + 10}s", f"cognitive load {r['peak']:.1f}× the budget for its pace (compositions, elements, motion, text and captions together)")
    for r in _ranges(over_comp):
        add("high" if r["peak"] > 2 else "medium", f"{r['a']}–{r['b'] + 10}s", f"new compositions {r['peak']:.1f}× the budget for its pace: develop within a composition instead of replacing it")
    return {"findings": F, "series": series, "summary": _summary(F)}


def _summary(F):
    return {k: sum(1 for f in F if f["severity"] == k) for k in ("high", "medium", "info")}


def film_signal(video: str, fps: int = 10, w: int = 160, h: int = 90):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(video), "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)
    return np.abs(np.diff(f, axis=0)).mean(axis=(1, 2)), fps


def check_film(P: dict, video: str) -> dict:
    d, fps = film_signal(video)
    big = [i / fps for i in range(len(d)) if d[i] > MAJOR]; changes = []; last = -9.0
    for t in big:                       # one continuous episode (a cut, a dissolve, one camera move) is one change
        if t - last > 0.3: changes.append(t)
        last = t
    dur = len(d) / fps; F = []
    add = lambda sev, where, msg: F.append({"severity": sev, "where": where, "msg": msg})
    over, busy, series = [], [], []
    for a in range(0, max(1, int(dur - 9))):
        n = sum(1 for t in changes if a <= t < a + 10); bud = _window_budget(P, a, FILM_CHANGE_BUDGET)
        energy = float(d[a * fps:(a + 10) * fps].mean())
        series.append({"a": a, "changes": n, "budget": round(bud, 1), "motion": round(energy, 1)})
        if n > bud: over.append({"a": a, "ratio": n / bud, "budget": bud})
        reading = sum(1 for k in range(10) if _pace_at(P, a + k + .5) in READ_PACES) >= 6
        if reading and energy > MOTION_BUSY: busy.append({"a": a, "ratio": energy / MOTION_BUSY, "budget": MOTION_BUSY})
    for r in _ranges(over):
        add("high" if r["peak"] > 2 else "medium", f"{r['a']}–{r['b'] + 10}s", f"{r['peak']:.2f}× the picture changes a first-time viewer can follow at this pace")
    for r in _ranges(busy):
        add("medium", f"{r['a']}–{r['b'] + 10}s", f"busy motion ({r['peak']:.1f}× the calm level) while the viewer must read or think")
    gaps = [b - a for a, b in zip([0.0] + changes, changes + [dur])]
    gaps_sorted = sorted(gaps)
    stats = {"picture_changes": len(changes), "per_10s": round(len(changes) / dur * 10, 1), "longest_hold_s": round(max(gaps), 1),
             "median_hold_s": round(gaps_sorted[len(gaps_sorted) // 2], 1), "mean_motion": round(float(d.mean()), 1), "changes_at": [round(t, 1) for t in changes]}
    return {"findings": F, "series": series, "stats": stats, "summary": _summary(F)}


def strip(P, plan_r, film_r, out_png):
    """a pacing strip for the report: shots coloured by pace, the load against its budget, picture changes"""
    from PIL import Image, ImageDraw
    W, H, D = 1600, 300, P["duration"]; X = lambda t: 40 + t / D * (W - 80)
    col = {"hook": "#c9963a", "character": "#3d7a52", "illustration": "#7f93ab", "diagram": "#2f3b52", "mechanism": "#5b3b5e",
           "emotional": "#b5473a", "transition": "#9a8f80"}
    im = Image.new("RGB", (W, H), "#f5eedf"); g = ImageDraw.Draw(im)
    for s in P["shots"]:
        g.rectangle([X(s["t0"]), 30, X(s["t1"]) - 2, 70], fill=col.get(s["pace"] or "illustration")); g.text((X(s["t0"]) + 3, 34), s["id"], fill="#fff")
    if plan_r:
        mx = max(40, max(max(p["load"], p["budget"]) for p in plan_r["series"]))   # one absolute scale, so strips compare
        for p in plan_r["series"]:
            x = X(p["a"] + 5); g.rectangle([x - 4, 220 - p["load"] / mx * 120, x + 4, 220], fill="#b5473a" if p["load"] > p["budget"] else "#7f93ab")
            g.line([x - 6, 220 - p["budget"] / mx * 120, x + 6, 220 - p["budget"] / mx * 120], fill="#2b2118", width=2)
        g.text((40, 230), "load per 10 s (bars; red = over its pace's budget, line = budget)", fill="#2b2118")
    if film_r:
        for t in film_r["stats"]["changes_at"]: g.line([X(t), 80, X(t), 96], fill="#2b2118", width=2)
        g.text((40, 100), f"picture changes: {film_r['stats']['picture_changes']} ({film_r['stats']['per_10s']} per 10 s), longest hold {film_r['stats']['longest_hold_s']} s", fill="#2b2118")
    for t in range(0, int(D) + 1, 5): g.text((X(t) - 6, 270), f"{t}s", fill="#6b5a48")
    im.save(out_png)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("plan"); a1.add_argument("map"); a1.add_argument("--out")
    a2 = sub.add_parser("film"); a2.add_argument("map"); a2.add_argument("video"); a2.add_argument("--out")
    a = ap.parse_args(argv)
    P = load_plan(Path(a.map)); pr = check_plan(P); fr = check_film(P, a.video) if a.cmd == "film" else None
    rep = {"plan": pr, **({"film": fr} if fr else {})}
    for name, r in rep.items():
        for f in r["findings"]:
            if f["severity"] != "info": print(f"{f['severity'].upper():6} {name:4} {f['where']:>12}  {f['msg']}")
    if fr: print("film:", json.dumps(fr["stats"] | {"changes_at": "…"}))
    summ = {k: sum(r["summary"][k] for r in rep.values()) for k in ("high", "medium", "info")}
    print(json.dumps({"pacing": summ}))
    if a.out:
        o = Path(a.out); o.mkdir(parents=True, exist_ok=True)
        (o / "pacing.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False)); strip(P, pr, fr, o / "pacing_strip.png")
    return 1 if summ["high"] else 0


if __name__ == "__main__":
    sys.exit(main())
