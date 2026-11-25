"""Rig v4: cast identities, sprite markup, and runtime behaviour in a real browser (views, IK contact, planted feet,
speech only when speaking, determinism)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EL = ROOT / "epoch-ledger"
sys.path.insert(0, str(EL))
from kit import rig3, rig4  # noqa: E402


def test_cast_keeps_v3_identities():
    f, i = rig4.CAST["founder"]["look"], rig4.CAST["investor"]["look"]
    assert f["skin"] == rig3.SKINS[0][0] and f["hair"] == rig3.HAIR[2] and f["hairStyle"] == "parted" and f["jacket"] is None
    assert i["skin"] == rig3.SKINS[1][0] and i["hair"] == rig3.HAIR[5] and i["jacket"] == rig3.COSTUMES["suit"][0] and i["tie"]
    js = rig4.create_js("fd", "founder", x=300, yaw=45, blink_seed=3)
    assert js.startswith('R4.create("fd", ') and '"blinkSeed": 3' in js
    assert '<g id="fd"></g>' in rig4.sprite_svg("fd", 900)


def _vendor():
    for c in sorted((ROOT / "projects").glob("*/*/vendor")):
        if (c / "gsap.min.js").exists():
            return c
    return None


@pytest.mark.skipif(not shutil.which("node"), reason="node not available")
def test_rig4_runtime(tmp_path):
    vendor = _vendor()
    if vendor is None:
        pytest.skip("no workspace with vendor/gsap.min.js")
    shutil.copy(vendor / "gsap.min.js", tmp_path)
    shutil.copy(EL / "kit" / "rig4.js", tmp_path)
    page = tmp_path / "t.html"
    page.write_text(f"""<!doctype html><script src="gsap.min.js"></script><script src="rig4.js"></script>
<svg width="1920" height="1080" viewBox="0 0 3000 1000"><g id="a"></g><g id="b"></g></svg><script>
const tl = gsap.timeline({{paused: true}});
{rig4.create_js("a", "founder", x=300, yaw=90, ground=1000, blink_seed=1)}
{rig4.create_js("b", "investor", x=2200, yaw=-60, ground=1000, blink_seed=2)}
R4.walk('a', 0.5, 3.0, 1400);
R4.reach('b', 'R', 1.0, [1960, 560, 120], .6, {{shape: 1}});
R4.say('a', 3.2, 4.0, 4);
R4.attach(tl); tl.to({{}}, {{duration: 6}}, 0); window.__timelines = {{main: tl}};
</script>""")
    probe = tmp_path / "p.cjs"
    probe.write_text("""
const { chromium } = require('playwright'); const { pathToFileURL } = require('url');
(async () => { const b = await chromium.launch(); const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(pathToFileURL(process.argv[2]).href);
  const at = (t, f) => p.evaluate(([t, f]) => { window.__timelines.main.seek(t, false); return eval(f); }, [t, f]);
  const out = { errs };
  // every character is driven by a real timeline tween (renderers such as HyperFrames drive GSAP their own way)
  out.driver = await p.evaluate(() => ['a', 'b'].every(id => window.__timelines.main.getChildren(false, true, false)
    .some(tw => tw.targets()[0] === document.getElementById(id) && typeof tw.vars.onUpdate === 'function')));
  // walking: a foot that is planted stays put while the body moves over it
  out.walk = [];
  for (const t of [0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]) out.walk.push(await at(t, "[R4.val('a','footL',window.__timelines.main.time())[0], R4.val('a','footR',window.__timelines.main.time())[0], R4.val('a','root',window.__timelines.main.time())[0], R4.chars.a.J.kneeL[0]]"));
  out.end = await at(3.1, "R4.val('a','root',3.1)[0]");
  // reaching: the palm lands on the target (wrist within ~a hand of it) and the hand grips
  out.reach = await at(1.8, "(() => { const J = R4.chars.b.J; return [Math.hypot(J.wristR[0]-1960, J.wristR[1]-560), R4.val('b','handShapeR',1.8)]; })()");
  // speech: the mouth only moves inside the say() window
  out.mouth = [await at(2.0, "R4.chars.a.speak.length"), await at(3.5, "document.querySelector('#a-body').innerHTML.includes('#5a2420')"), await at(4.5, "document.querySelector('#a-body').innerHTML.includes('#5a2420')")];
  // determinism: same frame from different histories
  const snap = async t => at(t, "document.getElementById('a').innerHTML + document.getElementById('b').innerHTML");
  const s1 = await snap(2.2); await snap(5.0); await snap(0.3); const s2 = await snap(2.2);
  out.det = s1 === s2;
  // views: yaw sweep draws without errors and the face shows from the front only
  out.views = [];
  for (const y of [0, 45, 90, 135, 180, -90]) out.views.push(await p.evaluate(y => { R4.key('b', 'yaw', 5.5, y); R4.chars.b.ch.yaw.ready = false; R4.draw(5.6); return document.querySelector('#b-body').innerHTML.includes('#fbf7f0'); }, y));
  console.log(JSON.stringify(out)); await b.close(); })();
""")
    r = subprocess.run(["node", str(probe), str(page)], capture_output=True, text=True, timeout=120)
    s = json.loads(r.stdout.strip().splitlines()[-1])
    assert not s["errs"], s["errs"]
    assert s["driver"]
    w = s["walk"]
    assert w[-1][2] - w[0][2] > 150                                      # the body travels
    planted = [abs(w[i + 1][0] - w[i][0]) < .5 or abs(w[i + 1][1] - w[i][1]) < .5 for i in range(len(w) - 1)]
    assert all(planted)                                                  # at every moment one foot is planted
    assert abs(s["end"] - 1400) < 40                                     # arrives where asked
    assert s["reach"][0] < 60 and s["reach"][1] > .9                     # hand on target, gripping
    assert s["mouth"] == [1, True, False]                                # open mouth only while speaking
    assert s["det"]
    assert s["views"][0] and not s["views"][4]                           # eyes from the front, none from behind
