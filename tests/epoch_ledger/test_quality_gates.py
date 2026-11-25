"""P1 quality gates: the financial model and validator, and the browser gates (figure, layout, contact) on a small
synthetic composition with known defects, plus the review-sheet tool on a generated clip."""
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

from kit.finmodel import Loan, Recurring, Scenario, simulate, validate  # noqa: E402


def rules(issues, severity="error"):
    return sorted({i.rule for i in issues if i.severity == severity})


# ── financial model ──────────────────────────────────────────────────────────────────────────────────────────────
def test_balance_never_below_overdraft_and_shortfall_is_tracked():
    sc = Scenario("t", 12000, 60, recurring=[Recurring("costs", -30000, "cost", 0, 30, 1), Recurring("pay", 40000, "revenue", 60, 30, 1)])
    m = simulate(sc)
    assert min(m.balance) == 0
    assert m.unpaid[0] == 18000 and m.metric("peak_shortfall") == 18000
    assert m.balance[60] == 22000 and m.unpaid[60] == 0          # the payment settles the unpaid bills first


def test_overdraft_allows_a_negative_balance():
    sc = Scenario("t", 12000, 60, overdraft_limit=20000, flows=[])
    sc.recurring = [Recurring("costs", -30000, "cost", 0, 30, 1)]
    m = simulate(sc)
    assert m.balance[0] == -18000 and m.unpaid[0] == 0
    assert "FIN-NEG-BALANCE" not in rules(validate(sc, [{"id": "b", "shows": "balance", "day": 0, "value": -18000, "financing": False}]))


def test_profitable_and_broke_as_narrated_fails_for_the_known_reasons():
    d = json.loads((EL / "episodes/profitable-and-broke/gates/finance.json").read_text())
    sc = Scenario.from_dict(d["scenario"])
    issues = validate(sc, d["figures"])
    assert rules(issues) == ["FIN-FIGURE", "FIN-FIN-COST", "FIN-LOAN-SIZE", "FIN-NEG-BALANCE"]
    assert simulate(sc, False).metric("peak_shortfall") == 48000   # second month's costs fall due before the first payment


def test_a_correct_single_order_scenario_passes():
    loan = Loan("Bridge loan", 18000, 0, 60, annual_rate=0.09)
    sc = Scenario("one order", 12000, 60, deal_recurs=False, loans=[loan],
                  recurring=[Recurring("costs", -30000, "cost", 0, 30, 1), Recurring("pay", 40000, "revenue", 60, 30, 1)])
    figs = [{"id": "rev", "shows": "revenue_per_cycle", "value": 40000}, {"id": "profit", "shows": "profit_per_cycle", "value": 10000},
            {"id": "short", "shows": "peak_shortfall", "value": 18000, "financing": False},
            {"id": "loan", "shows": "loan_principal", "value": 18000}, {"id": "interest", "shows": "interest_total", "value": loan.interest},
            {"id": "end", "shows": "balance", "day": 60, "value": 22000 - loan.interest}]
    assert loan.interest == pytest.approx(266.30, abs=.01)
    assert validate(sc, figs) == []


def test_recurring_deal_needs_recurring_costs_and_unshown_interest_warns():
    sc = Scenario("t", 0, 90, deal_recurs=True, recurring=[Recurring("pay", 40000, "revenue", 60, 30, 2)],
                  loans=[Loan("L", 30000, 0, 60, annual_rate=.1)])
    issues = validate(sc, [{"id": "p", "shows": "profit_per_cycle", "value": 99}])
    assert "FIN-RECURRING" in rules(issues) and "FIN-ARITH" in rules(issues)
    assert "FIN-COST-SHOWN" in rules(issues, "warning")


# ── browser gates on a synthetic composition ────────────────────────────────────────────────────────────────────
PAGE = """<!DOCTYPE html><html><head><style>body{margin:0}</style></head><body>
<div id="root" data-duration="4" data-width="1920" data-height="1080" style="position:relative;width:1920px;height:1080px;background:#f7f1e4">
 <div id="s1-Lboard" data-start="0" data-duration="4" style="position:absolute;inset:0">
  <svg viewBox="0 0 1920 1080" width="1920" height="1080" style="position:absolute;inset:0">
   <rect id="b1" x="100" y="500" width="100" height="400" fill="#2f8a4a"/>
   <rect id="b2" x="300" y="700" width="100" height="200" fill="#2f8a4a"/>
   <rect id="b3" x="500" y="600" width="100" height="100" fill="#2f8a4a"/>
   <g id="lab" opacity="0"><text x="300" y="670" font-family="sans-serif" font-size="40" fill="#1b1410">$20</text></g>
   <g id="early"><text x="700" y="300" font-family="sans-serif" font-size="40" fill="#1b1410">Early 99</text></g>
   <g id="same"><rect x="1000" y="300" width="400" height="100" fill="#c0442e"/><text x="1020" y="370" font-family="sans-serif" font-size="40" fill="#c0442e">Invisible</text></g>
   <text id="t1" x="100" y="200" font-family="sans-serif" font-size="40" fill="#1b1410">Overlap one</text>
   <text id="t2" x="130" y="215" font-family="sans-serif" font-size="40" fill="#1b1410">Overlap two</text>
   <g id="cov"><text x="1500" y="700" font-family="sans-serif" font-size="40" fill="#1b1410">Covered</text></g>
   <rect id="cover" x="1480" y="650" width="300" height="80" fill="#333"/>
   <g id="h1" transform="translate(0 900)"><path d="M0 0 L10 0" stroke="#000"/></g>
   <rect id="p1" x="0" y="905" width="60" height="40" fill="#8a4b2a"/>
  </svg>
 </div>
</div>
<script>
const R4 = { chars: { h1: { J: { wristL: [200, 0], elbowL: [150, 0] } } } };
window.__timelines = { main: { seek(t) {
  document.getElementById('lab').setAttribute('opacity', t >= 1.0 ? 1 : 0);
  const x = 200 + t * 100; R4.chars.h1.J.wristL = [x, 0]; R4.chars.h1.J.elbowL = [x - 50, 0];
  document.getElementById('p1').setAttribute('x', (t < 2 ? x - 10 : x + 290).toFixed(1));     // jumps away at t = 2
} } };
</script></body></html>"""

WORDS = [{"word": "twenty", "start": 1.0, "end": 1.4}, {"word": "early", "start": 3.0, "end": 3.3}]


def _need_browser():
    if not shutil.which("node"):
        pytest.skip("node not available")
    try:
        subprocess.run(["node", "-e", "require('playwright')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("playwright not available")


@pytest.fixture
def comp(tmp_path):
    _need_browser()
    (tmp_path / "index.html").write_text(PAGE)
    (tmp_path / "words.json").write_text(json.dumps(WORDS))
    return tmp_path


def _node(script, *args, cwd):
    r = subprocess.run(["node", str(EL / "scripts" / script), *map(str, args)], cwd=cwd, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def test_figure_check_finds_missing_early_and_off_baseline(comp):
    (comp / "figures.json").write_text(json.dumps({
        "figures": [{"id": "ok", "sel": "#lab", "text": "$20", "cue": ["twenty"], "settle": .3, "hold": .8},
                    {"id": "early", "sel": "#early", "cue": ["early"], "after": 2, "settle": .2, "hold": .5},
                    {"id": "red-on-red", "sel": "#same", "cue": ["twenty"]},
                    {"id": "covered", "sel": "#cov", "cue": ["twenty"]}],
        "charts": [{"id": "good", "at": {"t": 1.5}, "marks": [{"sel": "#b1", "value": 40}, {"sel": "#b2", "value": 20}]},
                   {"id": "floating", "at": {"t": 1.5}, "marks": [{"sel": "#b1", "value": 40}, {"sel": "#b3", "value": 10}]}]}))
    code, out = _node("figure_check.mjs", "index.html", "--figures", "figures.json", "--words", "words.json", "--json", "f.json", cwd=comp)
    assert code == 1, out
    res = {r["id"]: r for r in json.loads((comp / "f.json").read_text())["results"]}
    assert res["ok"]["pass"] and res["good"]["pass"]
    assert [i["check"] for i in res["early"]["issues"]] == ["early-reveal"]
    assert "contrast" in res["red-on-red"]["issues"][0]["detail"]
    assert "painted over" in res["covered"]["issues"][0]["detail"]
    assert any(i["check"] == "off-baseline" for i in res["floating"]["issues"])


def test_layout_check_reads_diagram_text(comp):
    code, out = _node("layout_check.mjs", "index.html", "--every", "1", "--json", "l.json", cwd=comp)
    kinds = {(i["kind"], i["a"]) for i in json.loads((comp / "l.json").read_text())["issues"]}
    assert code == 1
    assert ("text-overlap", "t1") in kinds
    assert ("text-low-contrast", "same") in kinds
    assert ("text-occluded", "cov") in kinds


def test_contact_check_finds_detached_and_popping_prop(comp):
    (comp / "contacts.json").write_text(json.dumps({
        "contacts": [{"id": "held", "char": "h1", "side": "L", "prop": "#p1", "from": 0, "to": 1.9},
                     {"id": "lost", "char": "h1", "side": "L", "prop": "#p1", "from": 1.9, "to": 3}],
        "props": [{"sel": "#p1", "from": 0, "to": 3}]}))
    code, out = _node("contact_check.mjs", "index.html", "--contacts", "contacts.json", "--json", "c.json", cwd=comp)
    res = {r["id"]: r for r in json.loads((comp / "c.json").read_text())["results"]}
    assert code == 1, out
    assert res["held"]["pass"], res["held"]
    assert [i["check"] for i in res["lost"]["issues"]] == ["detached"]
    assert any(i["check"] == "prop-pop" and "frame 60" in i["detail"] for i in res["#p1"]["issues"])


def test_review_sheets_on_a_generated_clip(tmp_path):
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg not available")
    vid = tmp_path / "clip.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=30:duration=2", "-pix_fmt", "yuv420p", str(vid)], check=True)
    (tmp_path / "m.json").write_text(json.dumps({"interactions": [{"id": "a", "t": 1.0, "label": "test", "box": [0, 0, 960, 540]}], "cuts": [0.5]}))
    subprocess.run([sys.executable, str(EL / "scripts" / "review_sheets.py"), str(vid), "--manifest", str(tmp_path / "m.json"),
                    "--out", str(tmp_path / "rev")], check=True, capture_output=True, timeout=300)
    names = {p.name for p in (tmp_path / "rev").iterdir()}
    assert {"review.html", "sheet_a.png", "crop_a.png", "sheet_cut-0.50.png", "samples_1.png"} <= names
    page = (tmp_path / "rev" / "review.html").read_text()
    assert "Feet do not slide" in page and "sheet_a.png" in page
