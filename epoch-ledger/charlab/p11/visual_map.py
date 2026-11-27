"""P11: narration-to-visual map — a reusable planning method for narrator-led documentaries (any subject).

The narration is the spine. Every clause the narrator speaks must be SHOWN, at the moment it is said:

  1. split the narration into clauses from the real word timestamps (Whisper words.json; punctuation ends a clause);
  2. for each clause, decide the visual event(s) that make its meaning visible: a character's story action, a prop, an
     object close-up, a 3D environment beat, a diagram step, a camera move with a reason. A caption is never enough;
  3. anchor each event to the word that carries the idea ("vault", "$10,000", "credits") with a small offset; the event
     time is that word's real start time plus the offset, so re-recording the narration re-times every visual;
  4. group events into shots; every shot must say what it introduces (context, information, action, consequence):
     a cut alone is not progression;
  5. check the map (`check`), render, then inspect the RENDERED video (`inspect`): for each event, find when its screen
     region actually changes and compare that with the planned time.

Map file (JSON):
  {"title", "words": "path/to/words.json", "duration",
   "sync": {"lead": 0.35, "lag": 0.25, "first_event": 0.8, "max_gap": 2.6, "clause_lag": 0.6},
   "shots":  [{"id", "t0", "t1", "medium", "introduces": [...], "purpose"}],
   "concepts": [{"id", "idea", "anchor": {"word", "n"}}],
   "events": [{"id", "anchor": {"word", "n"}, "offset", "shot", "what", "medium", "depicts": [concept ids], "region": [x0, y0, x1, y1]}]}
  concepts: the ideas the narration states (the key word of each); each must be DEPICTED by an event close to its word
  (within `concept_window` s), so "the vault stays shut" is shown when "vault" is said, not merely captioned.
  region: normalised screen box where the event's change is visible (for `inspect`); "cut" events use the whole frame.

    python3 epoch-ledger/charlab/p11/visual_map.py check MAP.json [--table OUT.md] [--resolved OUT.json]
    python3 epoch-ledger/charlab/p11/visual_map.py inspect MAP.json VIDEO.mp4 [--out REPORT.json]
Exit status 1 on errors. Nothing here is specific to banking: the map is the film's data, this file is the method.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

MEDIA = ("character-action", "prop", "insert", "3d", "diagram", "graphic", "camera", "cut")
INTRODUCES = ("context", "information", "action", "consequence")
DEFAULT_SYNC = {"lead": 0.35, "lag": 0.25, "first_event": 0.8, "max_gap": 2.6, "clause_lag": 0.6, "concept_window": 0.6}


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def load_words(path) -> list[dict]:
    w = json.loads(Path(path).read_text())
    return w if isinstance(w, list) else w["words"]


def clauses(words: list[dict]) -> list[dict]:
    """clauses from timestamped words: a clause ends at . , ; : ? ! (the narrator's own phrasing)"""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r"[.,;:?!]$", w["word"].strip()) or i == len(words) - 1:
            out.append({"id": f"c{len(out) + 1}", "words": cur, "text": " ".join(words[j]["word"] for j in cur),
                        "t0": words[cur[0]]["start"], "t1": words[cur[-1]]["end"]})
            cur = []
    return out


def anchor_index(words, anchor) -> int:
    k = 0
    for i, w in enumerate(words):
        if norm(w["word"]) == norm(anchor["word"]) or (anchor.get("prefix") and norm(w["word"]).startswith(norm(anchor["word"]))):
            k += 1
            if k == anchor.get("n", 1): return i
    raise KeyError(f"anchor word {anchor['word']!r} #{anchor.get('n', 1)} not in the narration")


def resolve(m: dict, words: list[dict]) -> dict:
    """events get absolute times (anchor word start + offset) and the clause they serve"""
    cl = clauses(words); where = {i: c["id"] for c in cl for i in c["words"]}
    ev = []
    for e in m["events"]:
        i = anchor_index(words, e["anchor"])
        ev.append({**e, "t": round(words[i]["start"] + e.get("offset", 0.0), 3), "word_t": words[i]["start"], "clause": where[i]})
    return {**m, "clauses": cl, "events": sorted(ev, key=lambda x: x["t"])}


def check(m: dict, words: list[dict]) -> dict:
    """errors (objective) and warnings (judgement) for a narration-to-visual map"""
    S = {**DEFAULT_SYNC, **m.get("sync", {})}
    r = resolve(m, words); errs, warns = [], []
    shots = sorted(m["shots"], key=lambda s: s["t0"]); sid = {s["id"]: s for s in shots}
    # shots tile the film; each says what it brings
    if abs(shots[0]["t0"]) > 1e-6: errs.append("the first shot must start at 0")
    if abs(shots[-1]["t1"] - m["duration"]) > 1e-6: errs.append("the last shot must end at the film's duration")
    for a, b in zip(shots, shots[1:]):
        if abs(a["t1"] - b["t0"]) > 1e-6: errs.append(f"{a['id']}→{b['id']}: shots must be contiguous")
    for s in shots:
        if not s.get("introduces") or any(x not in INTRODUCES for x in s["introduces"]):
            errs.append(f"{s['id']}: 'introduces' must list what the shot brings ({INTRODUCES}); a cut alone is not progression")
        if not s.get("purpose"): errs.append(f"{s['id']}: missing purpose")
        if s["t1"] - s["t0"] < 1.5: warns.append(f"{s['id']}: {s['t1'] - s['t0']:.2f}s is short to absorb")
    for e in r["events"]:
        if e.get("medium") not in MEDIA: errs.append(f"{e['id']}: medium {e.get('medium')!r} not in {MEDIA}")
        if e["shot"] not in sid: errs.append(f"{e['id']}: unknown shot {e['shot']}"); continue
        s = sid[e["shot"]]
        if not (s["t0"] - 1e-6 <= e["t"] <= s["t1"] + 1e-6): errs.append(f"{e['id']}: at {e['t']:.2f}s, outside its shot {s['id']} [{s['t0']}, {s['t1']}]")
        off = e.get("offset", 0.0)
        if off < -S["lead"] or off > S["lag"]:
            errs.append(f"{e['id']}: offset {off:+.2f}s from '{e['anchor']['word']}' outside [-{S['lead']}, +{S['lag']}] (visuals land with their words)")
    # every clause is shown (not only captioned), promptly
    for c in r["clauses"]:
        ce = [e for e in r["events"] if e["clause"] == c["id"]]
        if not ce: errs.append(f"{c['id']} \"{c['text']}\": no visual event (a caption alone does not count)"); continue
        lag = min(e["t"] for e in ce) - c["t0"]
        if lag > S["clause_lag"]: warns.append(f"{c['id']} \"{c['text']}\": first visual {lag:.2f}s after the clause starts")
    # every shot opens on something and keeps progressing
    for s in shots:
        se = [e["t"] for e in r["events"] if e["shot"] == s["id"]]
        if not se: errs.append(f"{s['id']}: no events (a shot must show something happen)"); continue
        if se[0] - s["t0"] > S["first_event"]: warns.append(f"{s['id']}: first event {se[0] - s['t0']:.2f}s after the cut")
        pts = [s["t0"]] + se + [min(s["t1"], m["duration"])]
        gap = max(b - a for a, b in zip(pts, pts[1:]))
        if gap > S["max_gap"] and not s.get("hold_reason"): warns.append(f"{s['id']}: {gap:.2f}s without a new visual event")
    # every stated idea is depicted near its word (semantic sync, not only coverage)
    for k in m.get("concepts", []):
        kt = words[anchor_index(words, k["anchor"])]["start"]
        dep = [e for e in r["events"] if k["id"] in e.get("depicts", [])]
        if not dep: errs.append(f"{k['id']} \"{k['idea']}\" (at '{k['anchor']['word']}' {kt:.2f}s): not depicted by any visual event"); continue
        d = min(abs(e["t"] - kt) for e in dep)
        if d > S["concept_window"]: errs.append(f"{k['id']} \"{k['idea']}\": depicted {d:.2f}s away from '{k['anchor']['word']}' (late or early explanation)")
    cuts = len(shots) - 1
    if cuts / (m["duration"] / 10) > 4: warns.append(f"{cuts} cuts in {m['duration']}s is more than 4 per 10 s")
    return {"errors": errs, "warnings": warns, "resolved": r}


def table(r: dict) -> str:
    """the timestamped narration-to-visual mapping, as a Markdown table"""
    rows = ["| Time | Narration (clause) | Anchor word | Visual event | Shot | Medium |", "|---|---|---|---|---|---|"]
    ctext = {c["id"]: c["text"] for c in r["clauses"]}
    for e in r["events"]:
        rows.append(f"| {e['t']:.2f} s | {ctext[e['clause']]} | \"{e['anchor']['word']}\" @ {e['word_t']:.2f} s ({e.get('offset', 0):+.2f}) | {e['what']} | {e['shot']} | {e['medium']} |")
    return "\n".join(rows) + "\n"


def inspect(r: dict, video: str, fps: int = 30, w: int = 192, h: int = 108) -> list[dict]:
    """semantic sync on the RENDERED film: for each event, when does its screen region actually change, vs the plan.
    Cuts: the frame-to-frame spike at the shot boundary. Other events: within the event's own shot (cuts excluded), the
    region is compared with a reference frame just before the event; the onset is when a quarter of the full change has
    happened (robust to fades and eased moves). A change smaller than 1 grey level is reported as not observed."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32); n = len(F)
    shots = {s["id"]: s for s in r["shots"]}; out = []
    for e in r["events"]:
        x0, y0, x1, y1 = e.get("region") or [0, 0, 1, 1]
        R = (slice(int(y0 * h), max(int(y0 * h) + 1, int(y1 * h))), slice(int(x0 * w), max(int(x0 * w) + 1, int(x1 * w))))
        s = shots[e["shot"]]; a = int(round(s["t0"] * fps)); b = min(n - 1, int(round(s["t1"] * fps)) - 1)
        if e.get("medium") == "cut" and e["t"] < 1.0 / fps:    # the film's first frame: nothing before it to cut from
            onset, strength = 0.0, float(F[0][R].std())
        elif e.get("medium") == "cut":
            lo, hi = max(1, int((e["t"] - .3) * fps)), min(n - 1, int((e["t"] + .3) * fps))
            d = [float(np.abs(F[f][R] - F[f - 1][R]).mean()) for f in range(lo, hi + 1)]
            k = int(np.argmax(d)); onset, strength = (lo + k) / fps, d[k]
        else:
            ref = max(a, int((e["t"] - .25) * fps)); end = min(b, int((e["t"] + .8) * fps))
            d = [float(np.abs(F[f][R] - F[ref][R]).mean()) for f in range(ref, end + 1)]
            strength = max(d) if d else 0.0
            k = next((i for i, v in enumerate(d) if v >= .25 * strength), None) if strength >= 1.0 else None
            onset = None if k is None else (ref + k) / fps
        onset = None if onset is None else round(onset, 3)
        out.append({"id": e["id"], "planned": e["t"], "observed": onset, "offset": None if onset is None else round(onset - e["t"], 3),
                    "ok": onset is not None and abs(onset - e["t"]) <= 0.2, "strength": round(strength, 2)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0]); sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("map"); c.add_argument("--table"); c.add_argument("--resolved")
    i = sub.add_parser("inspect"); i.add_argument("map"); i.add_argument("video"); i.add_argument("--out")
    a = ap.parse_args(argv)
    m = json.loads(Path(a.map).read_text()); words = load_words(m["words"])
    res = check(m, words)
    if a.cmd == "check":
        for x in res["errors"]: print("ERROR", x)
        for x in res["warnings"]: print("warn ", x)
        if a.table: Path(a.table).write_text(table(res["resolved"]))
        if a.resolved: Path(a.resolved).write_text(json.dumps(res["resolved"], indent=1))
        print(json.dumps({"clauses": len(res["resolved"]["clauses"]), "events": len(res["resolved"]["events"]), "shots": len(m["shots"]),
                          "errors": len(res["errors"]), "warnings": len(res["warnings"])}))
        return 1 if res["errors"] else 0
    rep = inspect(res["resolved"], a.video)
    for x in rep: print(json.dumps(x))
    summ = {"events": len(rep), "in_sync": sum(x["ok"] for x in rep), "missing": [x["id"] for x in rep if x["observed"] is None],
            "late_or_early": [x["id"] for x in rep if x["observed"] is not None and not x["ok"]]}
    print(json.dumps(summ))
    if a.out: Path(a.out).write_text(json.dumps({"summary": summ, "events": rep}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
