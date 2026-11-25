"""M2.2: quality-gate settings generated from an episode build (kit/gates.py) and run end to end, with contacts
discovered from the built composition. No hand-written manifests."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EL = ROOT / "epoch-ledger"
sys.path.insert(0, str(EL))

from kit.assemble import Scene, assemble  # noqa: E402
from kit.finmodel import Loan, Recurring, Scenario  # noqa: E402
from kit.gates import Gates  # noqa: E402

WORDS = [{"word": w, "start": s, "end": s + .3} for w, s in
         (("Revenue", .4), ("is", .8), ("$40,000.", 1.0), ("Costs", 2.0), ("are", 2.4), ("30,000.", 2.6),
          ("She", 3.6), ("is", 3.8), ("18,000", 4.0), ("short.", 4.5), ("Interest", 5.2), ("costs", 5.6), ("$266.", 5.8))]


def scenario(rate=.09):
    return Scenario("one order", 12000, 60, loans=[Loan("Bridge loan", 18000, 0, 60, annual_rate=rate)],
                    recurring=[Recurring("costs", -30000, "cost", 0, 30, 1), Recurring("pay", 40000, "revenue", 60, 30, 1)])


def build(ws: Path, *, wrong_short=False, rate=.09):
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "words.json").write_text(json.dumps(WORDS))
    G = Gates(words=ws / "words.json", finance=scenario(rate))
    rev, cost = G.value("revenue_per_cycle"), G.value("cost_per_cycle")
    short = G.value("peak_shortfall", financing=False)
    interest = G.value("interest_total")
    shown_short = 9000 if wrong_short else short
    k = .01
    svg = (f'<svg viewBox="0 0 1920 1080" width="1920" height="1080" style="position:absolute;inset:0">'
           f'<g{G.chart("bars", cue="30,000", after=2, offset=.6)}>'
           f'<rect{G.mark("bars", rev)} x="300" y="{900 - rev * k}" width="200" height="{rev * k}" fill="#2f8a4a"/>'
           f'<rect{G.mark("bars", cost)} x="600" y="{900 - cost * k}" width="200" height="{cost * k}" fill="#c0442e"/></g>'
           f'<g id="lrev"{G.fig("rev", f"${rev:,.0f}", cue="$40,000", shows="revenue_per_cycle")} opacity="0"><text x="300" y="440" font-family="sans-serif" font-size="48" fill="#1b1410">${rev:,.0f}</text></g>'
           f'<g id="lcost"{G.fig("cost", f"${cost:,.0f}", cue="30,000", shows="cost_per_cycle")} opacity="0"><text x="600" y="540" font-family="sans-serif" font-size="48" fill="#1b1410">${cost:,.0f}</text></g>'
           f'<g id="lshort"{G.fig("short", f"${shown_short:,.0f} short", cue="18,000", shows="peak_shortfall", financing=False, value=shown_short)} opacity="0"><text x="1000" y="300" font-family="sans-serif" font-size="48" fill="#1b1410">${shown_short:,.0f} short</text></g>'
           f'<g id="lint"{G.fig("interest", f"${interest:,.0f}", cue="Interest", after=5, shows="interest_total")} opacity="0"><text x="1000" y="400" font-family="sans-serif" font-size="48" fill="#1b1410">Interest ${interest:,.0f}</text></g>'
           f'<g id="who"><path d="M0 0 L10 0" stroke="#000"/></g><rect id="box" x="0" y="905" width="60" height="40" fill="#8a4b2a"/></svg>')
    js = ("tl.to('#lrev', {opacity: 1, duration: .2}, .9); tl.to('#lcost', {opacity: 1, duration: .2}, 2.5);"
          "tl.to('#lshort', {opacity: 1, duration: .2}, 3.9); tl.to('#lint', {opacity: 1, duration: .2}, 5.1);"
          # a stand-in for a rig: R4.hold registers the hold exactly as rig4.js does, and the driver moves hand and prop together
          "tl.fromTo('#box', {'--d': 0}, {'--d': 7, duration: 7, ease: 'none', immediateRender: false, onUpdate() {"
          " const t = this.startTime() + this.time(), x = 200 + t * 60; R4.chars.who.J.wristL = [x, 0]; R4.chars.who.J.elbowL = [x - 50, 0];"
          " document.getElementById('box').setAttribute('x', (x - 10).toFixed(1)); }}, 0);")
    shared = ("const R4 = { chars: { who: { J: { wristL: [200, 0], elbowL: [150, 0] }, props: [] } } };"
              "R4.chars.who.props.push({ side: 'L', el: 'box', a: 1, b: 6 });"
              "document.getElementById('who').setAttribute('transform', 'translate(0 900)');")
    scenes = [Scene("s1", 0, 7.0, svg, "", js), Scene("s2", 3.5, 3.5, "", "", "")]
    html = assemble(title="gates test", duration=7.0, scenes=scenes, audio=None, vignette=False, shared_js=shared)
    vendor = next((c for c in sorted((ROOT / "projects").glob("*/*/vendor")) if (c / "gsap.min.js").exists()), None)
    if vendor is None:
        pytest.skip("no vendored GSAP")
    (ws / "vendor").mkdir(exist_ok=True)
    for f in ("gsap.min.js", "three.min.js"):
        shutil.copy(vendor / f, ws / "vendor")
    (ws / "vendor" / "vault3d.js").write_text("")
    (ws / "index.html").write_text(html)
    return G.write(ws, scenes=scenes)


def test_declarations_validate_at_build_time(tmp_path):
    (tmp_path / "w.json").write_text(json.dumps(WORDS))
    G = Gates(words=tmp_path / "w.json", finance=scenario())
    assert G.value("peak_shortfall", financing=False) == 18000
    assert 'data-gate-fig="a"' in G.fig("a", "$40,000", cue="$40,000", shows="revenue_per_cycle")
    with pytest.raises(KeyError):
        G.fig("b", "x", cue="never")                         # a cue that is not spoken fails the build
    with pytest.raises(ValueError):
        G.fig("a", "x", cue="Costs")                         # ids are unique
    G.chart("c", t=1.0)
    with pytest.raises(ValueError):
        G.write(tmp_path / "ws")                             # a chart without marks is a build error
    assert G.claims[0] == {"id": "a", "shows": "revenue_per_cycle", "value": 40000, "financing": True}


def _gates(cfg: Path, out: Path):
    r = subprocess.run([sys.executable, str(EL / "scripts" / "quality_gates.py"), str(cfg), "--out", str(out), "--no-review"],
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr, json.loads((out / "gates.json").read_text())


def _need_browser():
    if not shutil.which("node"):
        pytest.skip("node not available")
    try:
        subprocess.run(["node", "-e", "require('playwright')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("playwright not available")


def test_generated_settings_pass_end_to_end(tmp_path):
    _need_browser()
    cfg = build(tmp_path / "ws")
    c = json.loads(cfg.read_text())
    assert c["contacts"] == "auto" and c["figures"] and c["finance"] and c["interactions"]
    assert json.loads((tmp_path / "ws" / "gates" / "interactions.json").read_text())["cuts"] == [3.5]
    code, out, rep = _gates(cfg, tmp_path / "out")
    assert code == 0, out
    g = {x["gate"]: x for x in rep["gates"]}
    assert g["finance"]["pass"] and g["figures"]["pass"] and g["layout"]["pass"] and g["contacts"]["pass"]
    cc = json.loads((tmp_path / "out" / "contacts.json").read_text())
    assert cc["auto"] and [x["char"] for x in cc["contacts"]] == ["who"]   # the hold was found in the page itself


def test_generated_settings_catch_a_wrong_figure_and_a_free_loan(tmp_path):
    _need_browser()
    cfg = build(tmp_path / "ws", wrong_short=True, rate=0)
    code, out, rep = _gates(cfg, tmp_path / "out")
    assert code == 1
    fin = next(x for x in rep["gates"] if x["gate"] == "finance")
    text = "\n".join(fin["findings"])
    assert not fin["pass"] and "FIN-FIGURE" in text and "short" in text and "FIN-FIN-COST" in text
