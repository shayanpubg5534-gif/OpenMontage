#!/usr/bin/env python3
"""Epoch Ledger quality gates: run every P1 gate for one episode and write one report plus the visual review page.

    python epoch-ledger/scripts/quality_gates.py epoch-ledger/episodes/<slug>/gates/gates.json --out DIR [--only a,b] [--no-review]

gates.json names the inputs (paths relative to the repository root; any may be omitted, and its gate is skipped).
New episodes do not write it by hand: kit/gates.py generates it from the build (WORKSPACE/gates/gates.json).
    workspace      built HyperFrames composition (index.html)       → layout, figures, contacts
    video          rendered MP4 (read only)                          → frames (black/flash/freeze/loudness), review
    words          narration word timings (words.json)               → figures
    finance        scenario + figures shown (finance.json)           → finance
    figures        figure and chart manifest (figures.json)          → figures
    contacts       who holds what (contacts.json), or "auto": read every R4.hold from the built composition → contacts
    interactions   events and cuts for contact sheets                → review
    layout_every   layout sampling step in seconds (default 0.25)

Gates (each PASS/FAIL):
    finance   kit/finmodel.py      figures match one daily cash model; no shortfall drawn as a balance; recurring costs;
                                    loan size and financing cost
    figures   figure_check.mjs     each named figure is legible when spoken, not revealed early; charts proportional
                                    and on a shared baseline
    layout    layout_check.mjs     text overlap, text painted over, low contrast, caption band, off-frame (diagram text
                                    included)
    contacts  contact_check.mjs    hand-to-prop distance, hand hidden by the prop, one-frame prop jumps
    frames    qc.mjs --video       black, flash, opening jump, freeze, loudness on the stored video
The review page (review_sheets.py) adds consecutive-frame contact sheets around every interaction and cut, a 1-in-30
frame sample and the human checklist; it is evidence for the human review, not a gate.
Nothing is rendered. Exit 1 if any gate fails.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "epoch-ledger" / "scripts"
sys.path.insert(0, str(ROOT / "epoch-ledger"))


def run(cmd: list[str], timeout: int = 1800) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr).strip()


def gate_finance(cfg, out):
    from kit.finmodel import check_file, simulate
    sc, figs, issues = check_file(str(ROOT / cfg["finance"]))
    m, raw = simulate(sc), simulate(sc, False)
    findings = [str(i) for i in issues]
    info = (f"model: peak shortfall {raw.metric('peak_shortfall'):,.0f} before financing, {m.metric('peak_shortfall'):,.0f} after; "
            f"{len(figs)} figure(s) checked")
    return not any(i.severity == "error" for i in issues), [info] + findings


def gate_node(script, args, out_json):
    def g(cfg, out):
        code, text = run(["node", str(SCRIPTS / script), str(ROOT / cfg["workspace"])] + args(cfg) + ["--json", str(out / out_json)])
        lines = [l for l in text.splitlines() if l.strip() and not l.startswith("PASS")]
        return code == 0, lines
    return g


def gate_frames(cfg, out):
    code, text = run(["node", str(SCRIPTS / "qc.mjs"), "--video", str(ROOT / cfg["video"]), "--json", str(out / "frames.json")])
    return code == 0, [l for l in text.splitlines() if l.strip()]


GATES = {
    "finance": (("finance",), gate_finance),
    "figures": (("workspace", "figures", "words"), gate_node("figure_check.mjs", lambda c: ["--figures", str(ROOT / c["figures"]), "--words", str(ROOT / c["words"])], "figures.json")),
    "layout": (("workspace",), gate_node("layout_check.mjs", lambda c: ["--every", str(c.get("layout_every", 0.25))], "layout.json")),
    "contacts": (("workspace", "contacts"), gate_node("contact_check.mjs", lambda c: ["--auto"] if c["contacts"] == "auto" else ["--contacts", str(ROOT / c["contacts"])], "contacts.json")),
    "frames": (("video",), gate_frames),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("config", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--no-review", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    only = [x for x in a.only.split(",") if x]
    report = {"config": str(a.config), "gates": []}
    for name, (needs, fn) in GATES.items():
        if only and name not in only:
            continue
        if not all(cfg.get(k) for k in needs):
            report["gates"].append({"gate": name, "pass": True, "skipped": True, "findings": [f"skipped: needs {', '.join(needs)}"]})
            continue
        t = time.time()
        ok, findings = fn(cfg, a.out)
        report["gates"].append({"gate": name, "pass": ok, "seconds": round(time.time() - t, 1), "findings": findings})
        print(f"{'PASS' if ok else 'FAIL'}  {name:9} ({time.time() - t:.0f}s)")
        for f in findings[:60]:
            print("      " + f)
    (a.out / "gates.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    if not a.no_review and cfg.get("video"):
        cmd = [sys.executable, str(SCRIPTS / "review_sheets.py"), str(ROOT / cfg["video"]), "--out", str(a.out), "--gates", str(a.out / "gates.json")]
        manifest = json.loads((ROOT / cfg["interactions"]).read_text()) if cfg.get("interactions") else {"interactions": [], "cuts": []}
        cj = a.out / "contacts.json"
        if cfg.get("contacts") == "auto" and cj.exists():          # every discovered hold gets a contact sheet at its start
            seen = {i["id"] for i in manifest["interactions"]}
            for c in json.loads(cj.read_text()).get("contacts", []):
                if c["id"] not in seen:
                    manifest["interactions"].append({"id": c["id"].replace(":", "_").replace("@", "_").replace("#", ""),
                                                     "t": c["from"], "label": f"{c['char']} {c['side']} hand takes {c['prop']}"})
        (a.out / "interactions_merged.json").write_text(json.dumps(manifest, indent=2))
        cmd += ["--manifest", str(a.out / "interactions_merged.json")]
        code, text = run(cmd)
        print(text.splitlines()[-1] if text else f"review_sheets exit {code}")
    failed = [g["gate"] for g in report["gates"] if not g["pass"]]
    print(f"quality_gates: {len(report['gates']) - len(failed)}/{len(report['gates'])} gates passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
