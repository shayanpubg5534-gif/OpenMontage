"""M2.3: the asset-readiness gate (kit.assemble ready_gate) and module-aware QA serving (lib/frame_state compositionURL)."""
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


def _doc(**kw):
    return assemble(title="t", duration=2.0, scenes=[Scene("s1", 0, 2, "<p id='p'>x</p>", ".a{}", "tl.to('#p', {opacity: .5, duration: 1}, 0);")],
                    audio=None, **kw)


def test_gate_off_changes_nothing_and_on_defers_registration():
    plain = _doc()
    assert "__elReady" not in plain and plain.count('window.__timelines["main"] = tl;') == 1
    gated = _doc(ready_gate=["char"], ready_timeout=30)
    head, _, gate = gated.partition("// asset readiness gate")
    assert 'window.__timelines["main"] = tl;' not in head        # nothing registers before the gate
    assert 'const go = () =>' in gate and 'window.__timelines["main"] = tl;' in gate.split("window.__elReady")[0]
    assert "30000" in gate and "throw new Error('asset gate: '" in gate


def _need_browser():
    if not shutil.which("node"):
        pytest.skip("node not available")
    try:
        subprocess.run(["node", "-e", "require('playwright')"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("playwright not available")


PROBE = r"""
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.argv[2] + '/x.js')('playwright');
const { openComposition, compositionURL } = await import(process.argv[2] + '/epoch-ledger/scripts/lib/frame_state.mjs');
const b = await chromium.launch(); const out = {};
for (const f of process.argv.slice(3)) {
  const url = await compositionURL(f); const t0 = Date.now();
  const { page, errors } = await openComposition(b, url);
  out[f.split('/').slice(-2, -1)[0]] = { scheme: url.split(':')[0], registered: await page.evaluate(() => !!(window.__timelines && window.__timelines.main)),
    gateOpen: await page.evaluate(() => !!window.__elGateOpen), startupError: await page.evaluate(() => window.__hfStartupError || null),
    layer: await page.evaluate(() => window.__layerReadyAt || null), errors, ms: Date.now() - t0 };
  await page.close();
}
await b.close(); console.log(JSON.stringify(out));
"""


def test_gate_holds_the_timeline_until_the_module_layer_is_ready_and_fails_loudly(tmp_path):
    _need_browser()
    vendor = next((c for c in sorted((ROOT / "projects").glob("*/*/vendor")) if (c / "gsap.min.js").exists()), None)
    if vendor is None:
        pytest.skip("no vendored GSAP")
    for name, body in (("ok", "await new Promise(r => setTimeout(r, 1200)); window.__layerReadyAt = performance.now(); window.__elReady('char');"),
                       ("bad", "await new Promise(r => setTimeout(r, 300)); window.__elFail('char', 'model missing');")):
        ws = tmp_path / name
        (ws / "vendor").mkdir(parents=True)
        for f in ("gsap.min.js", "three.min.js"):
            shutil.copy(vendor / f, ws / "vendor")
        (ws / "vendor" / "vault3d.js").write_text("")
        (ws / "layer.js").write_text(f"export const ok = 1;\n{body}\n")
        layer = '<script type="module">import "./layer.js";</script>'
        (ws / "index.html").write_text(assemble(title=name, duration=2.0, scenes=[Scene("s1", 0, 2, "<p>x</p>")], audio=None,
                                                layers=[layer], ready_gate=["char"], ready_timeout=20))
    probe = tmp_path / "probe.mjs"
    probe.write_text(PROBE)
    r = subprocess.run(["node", str(probe), str(ROOT), str(tmp_path / "ok" / "index.html"), str(tmp_path / "bad" / "index.html")],
                       capture_output=True, text=True, timeout=180)
    res = json.loads(r.stdout.strip().splitlines()[-1])
    ok, bad = res["ok"], res["bad"]
    assert ok["scheme"] == "http"                              # module documents are served, not opened from file://
    assert ok["registered"] and ok["gateOpen"] and ok["layer"] and ok["startupError"] is None
    assert ok["ms"] >= 1000                                    # the timeline appeared only after the layer was ready
    assert not bad["registered"] and bad["startupError"] == "asset gate: char: model missing"
    assert any("asset gate: char: model missing" in e for e in bad["errors"])   # an uncaught page error: HyperFrames aborts


def test_plain_documents_keep_file_urls(tmp_path):
    _need_browser()
    (tmp_path / "index.html").write_text("<!doctype html><html><body><div id='root'></div></body></html>")
    probe = tmp_path / "p.mjs"
    probe.write_text(f"const {{ compositionURL }} = await import('{ROOT}/epoch-ledger/scripts/lib/frame_state.mjs');"
                     f"console.log(await compositionURL('{tmp_path / 'index.html'}'));")
    r = subprocess.run(["node", str(probe)], capture_output=True, text=True, timeout=60)
    assert r.stdout.strip().startswith("file://")
