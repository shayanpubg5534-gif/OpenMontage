"""Epoch Ledger motion kit: Python builders, JS library, demo composition and layout checker."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EL = ROOT / "epoch-ledger"
sys.path.insert(0, str(EL))

from kit import motion  # noqa: E402


def test_iso_projection_is_true_isometric():
    x0, y0 = motion.iso(0, 0)
    x1, y1 = motion.iso(100, 0)
    assert abs((y1 - y0) / (x1 - x0) - 0.57735) < 1e-3          # ground axis at 30°
    assert motion.iso(0, 0, 10)[1] == y0 - 10                       # z lifts straight up


def test_iso_box_shades_from_one_light():
    svg = motion.iso_box("b", 0, 0, 0, 10, 10, 10, "#808080")
    assert svg.count("<polygon") == 3 and motion.shade("#808080", .82) in svg and motion.shade("#808080", .64) in svg


def test_ktext_pre_splits_words_and_lines():
    assert motion.ktext("k", "a b c").count('class="ki"') == 3
    assert motion.ktext("k", "line one|line two", by="line").count("display:block") == 2


def test_world_map_and_route():
    cs = motion.countries()
    assert len(cs) >= 170 and "Japan" in cs
    p = motion.projection("equirect")
    svg = motion.world_map_svg("m", p, {"Japan": "#f00"})
    assert 'id="m-c-japan"' in svg and 'fill="#f00"' in svg
    d = motion.route_path([(-74, 40.7), (139.7, 35.7)], p)
    assert d.startswith("M") and d.count("L") > 20
    o = motion.projection("ortho", rotate=(0, 0))
    assert o(180, 0) is None and o(0, 0) == (960.0, 540.0)


def test_map_data_licence_recorded():
    lic = (EL / "kit" / "data" / "LICENSES.md").read_text()
    assert "Natural Earth" in lic and "ISC" in lic


def test_endscreen_keeps_slots_out_of_caption_band():
    h = motion.endscreen_html()
    assert h.count("es-slot") == 3 and "logo" not in h.lower()
    import re
    for top, height in re.findall(r"top:(\d+)px;width:\d+px;height:(\d+)px", h):
        assert int(top) + int(height) <= 880


def test_motion_js_is_bundled_and_parses():
    js = (EL / "kit" / "motion.js").read_text()
    for fn in ("mReveal", "mWordsAt", "mDrawOn", "mDiagram", "mFocus", "mFlow", "mCount", "mBars", "mAmbient", "mParallax", "mStutter", "mEndScreen"):
        assert f"function {fn}(" in js
    assert "Math.random" not in js and "Date.now" not in js            # deterministic
    assert '"motion.js"' in (EL / "kit" / "assemble.py").read_text()
    if shutil.which("node"):
        subprocess.run(["node", "-e", "new Function(require('fs').readFileSync(process.argv[1],'utf8'))", str(EL / "kit" / "motion.js")], check=True)


def _vendor_dir():
    for c in sorted((ROOT / "projects").glob("*/*/vendor")):
        if (c / "gsap.min.js").exists():
            return c
    return None


@pytest.mark.skipif(not shutil.which("node"), reason="node not available")
def test_demo_composition_behaves(tmp_path):
    """Build the reference composition and check helper states at exact times in a real browser."""
    vendor = _vendor_dir()
    if vendor is None:
        pytest.skip("no vendored GSAP in any workspace (run scripts/vendor.sh)")
    try:
        subprocess.run(["node", "-e", "require('playwright')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("playwright not available")
    (tmp_path / "vendor").mkdir()
    shutil.copy(vendor / "gsap.min.js", tmp_path / "vendor")
    shutil.copy(vendor / "three.min.js", tmp_path / "vendor")
    subprocess.run([sys.executable, str(EL / "scripts" / "motion_demo.py"), str(tmp_path)], check=True, capture_output=True)
    probe = tmp_path / "probe.cjs"
    probe.write_text("""
const { chromium } = require('playwright'); const { pathToFileURL } = require('url');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  for (let k = 0; k < 80 && !(await p.evaluate(() => !!(window.__timelines && window.__timelines.main))); k++) await p.waitForTimeout(250);
  const at = (t, f) => p.evaluate(([t, f]) => { window.__timelines.main.seek(t, false); return eval(f); }, [t, f]);
  const out = {
    wordHidden: await at(0.1, "+gsap.getProperty(document.querySelector('#k1-a .ki'),'yPercent')"),
    wordShown: await at(2.0, "+gsap.getProperty(document.querySelector('#k1-a .ki'),'yPercent')"),
    drawn: await at(7.5, "+getComputedStyle(document.querySelector('#b1 .bp')).strokeDashoffset.replace('px','')"),
    dimmed: await at(11.0, "+getComputedStyle(document.querySelector('#d-a')).opacity"),
    focused: await at(11.0, "+getComputedStyle(document.querySelector('#d-b')).opacity"),
    counter: await at(16.5, "document.querySelector('#c1-n').textContent"),
    counterStart: await at(13.0, "document.querySelector('#c1-n').textContent"),
    bar: await at(16.5, "+document.querySelectorAll('#c1 .bar')[4].getAttribute('height')"),
    route: await at(24.5, "+getComputedStyle(document.querySelector('#m1-r')).strokeDashoffset.replace('px','')"),
    endscreen: await at(29.5, "+getComputedStyle(document.querySelector('#es')).opacity"),
    errs };
  console.log(JSON.stringify(out)); await b.close(); })();
""")
    r = subprocess.run(["node", str(probe), str(tmp_path / "index.html")], check=True, capture_output=True, text=True, timeout=180)
    s = json.loads(r.stdout.strip().splitlines()[-1])
    assert not s["errs"], s["errs"]
    assert s["wordHidden"] > 90 and abs(s["wordShown"]) < 1          # word masked before its time, landed after
    assert abs(s["drawn"]) < 1                                        # blueprint fully drawn
    assert s["dimmed"] < .5 and s["focused"] > .95                    # focus + context
    assert s["counter"] == "$10,000" and s["counterStart"] == "$0"     # exact, formatted, settles
    assert abs(s["bar"] - 420) < 1                                    # 6 units × 70 px
    assert abs(s["route"]) < 1 and s["endscreen"] > .95
    lc = subprocess.run(["node", str(EL / "scripts" / "layout_check.mjs"), str(tmp_path / "index.html"), "--every", "1"],
                        capture_output=True, text=True, timeout=300)
    assert lc.returncode == 0, lc.stdout[-2000:]
