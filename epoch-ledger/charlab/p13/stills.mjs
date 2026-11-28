// P13: several stills of one HyperFrames composition in one browser session (storyboard key frames). Seeks the main
// timeline and applies the renderer's clip visibility rule (a clip shows while data-start ≤ t < data-start+duration),
// which a plain browser page does not do by itself (scripts/still.mjs is for single-scene style frames).
//   node epoch-ledger/charlab/p13/stills.mjs WS/index.html OUT_DIR NAME=T [NAME=T …]
import { createRequire } from 'node:module'; import { pathToFileURL } from 'node:url'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [file, out, ...shots] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; p.on('pageerror', e => errs.push(String(e)));
await p.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: 'load' });
await p.evaluate(async () => { await document.fonts.ready; await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {}))); });
for (const s of shots) {
  const [name, t] = s.split('=');
  await p.evaluate(t => { window.__timelines.main.seek(t, false);
    for (const c of document.querySelectorAll('#root > .clip, #root > [data-start]')) { const a = +c.dataset.start, d = +c.dataset.duration;
      c.style.visibility = (t >= a && t < a + d) ? 'visible' : 'hidden'; } }, +t);
  await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(out, name + '.png'), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
}
await b.close(); if (errs.length) { console.error(errs.join('\n')); process.exit(1); }
console.log('stills', shots.join(' '));
