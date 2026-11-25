"""Depth-layered environments: scene3d layer bands, layered plate cache keys, foliage, parallax overscan."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EL = ROOT / "epoch-ledger"
sys.path.insert(0, str(EL))
from kit import depth  # noqa: E402


def test_foliage_is_deterministic_and_layer_pages_differ():
    assert depth.foliage(seed=3) == depth.foliage(seed=3) != depth.foliage(seed=4)
    a = depth.page_html("const sc = S3.scene();", "const cam = S3.camera({pos:[0,1,0],look:[0,1,-1],fov:50});", "const L = {};", "fg", (2, 6))
    b = depth.page_html("const sc = S3.scene();", "const cam = S3.camera({pos:[0,1,0],look:[0,1,-1],fov:50});", "const L = {};", "bg", (2, 6))
    assert "layer: 'fg'" in a and "background:transparent" in a and "background:#201818" in b


@pytest.mark.skipif(not shutil.which("node"), reason="node not available")
def test_scene3d_layer_bands_and_parallax(tmp_path):
    vendor = next((c for c in sorted((ROOT / "projects").glob("*/*/vendor")) if (c / "gsap.min.js").exists()), None)
    if vendor is None:
        pytest.skip("no workspace with vendor/gsap.min.js")
    for f in ("scene3d.js", "depth.js"):
        shutil.copy(EL / "kit" / f, tmp_path)
    shutil.copy(vendor / "gsap.min.js", tmp_path)
    (tmp_path / "t.html").write_text("""<!doctype html><script src="gsap.min.js"></script><script src="scene3d.js"></script><script src="depth.js"></script>
<div id="d-Lbg" data-depth="8"></div><div id="d-Lfg" data-depth="1.2"></div><script>
const cam = S3.camera({ pos: [0, 1.5, 0], look: [0, 1, -6], fov: 50 }), L = { sun: { dir: [-1, .3, .2], intensity: .4 }, ambient: .8 };
const sc = S3.scene();
sc.quad([-5, 0, -9], [5, 0, -9], [5, 3, -9], [-5, 3, -9], { color: '#888' }, { bias: -3 });       // wall: architecture
sc.box([-.3, 0, -1.6], [.3, .8, -1.3], { color: '#a55' }, {});                                    // near solid → fg
sc.box([-.3, 0, -4], [.3, .8, -3.6], { color: '#5a5' }, {});                                      // mid solid → mg
sc.art([1, 0, -1.5], [1.5, 0, -1.5], [1, 1, -1.5], 100, 200, '<rect width="100" height="200"/>', { layer: 'fg' });
const n = layer => { const h = S3.render(sc, cam, L, { layer, split: [2.5, 6] }); return [(h.match(/<path/g) || []).length, h.includes('<g transform')]; };
const tl = gsap.timeline({ paused: true }); DL.move('d', 0, 1, { truck: .3, dolly: .2, focal: 1158 });
tl.seek(1);
window.out = { bg: n('bg'), mg: n('mg'), fg: n('fg'),
  xbg: gsap.getProperty('#d-Lbg', 'x'), xfg: gsap.getProperty('#d-Lfg', 'x'), sbg: gsap.getProperty('#d-Lbg', 'scale'), sfg: gsap.getProperty('#d-Lfg', 'scale') };
</script>""")
    probe = tmp_path / "p.cjs"
    probe.write_text("""const { chromium } = require('playwright'); const { pathToFileURL } = require('url');
(async () => { const b = await chromium.launch(); const p = await b.newPage(); await p.goto(pathToFileURL(process.argv[2]).href);
  console.log(JSON.stringify(await p.evaluate(() => window.out))); await b.close(); })();""")
    r = subprocess.run(["node", str(probe), str(tmp_path / "t.html")], capture_output=True, text=True, timeout=60)
    o = json.loads(r.stdout.strip().splitlines()[-1])
    assert o["bg"][0] >= 1 and o["mg"][0] >= 1 and o["fg"][0] >= 1       # wall in bg; each solid box in its depth band
    assert o["fg"][1] and not o["mg"][1] and not o["bg"][1]               # art tagged fg appears only in the fg band
    assert abs(o["xfg"]) > abs(o["xbg"]) * 5                       # near layers move much more than far ones
    assert o["sfg"] > o["sbg"] > 1                                 # push-in grows the foreground most; overscan ≥ 1
