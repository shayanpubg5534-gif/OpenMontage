#!/usr/bin/env node
// Character lab (M2.3): render look-development stills with viewer/lookdev.html in headless Chromium (CPU WebGL).
//   node epoch-ledger/charlab/lookdev.mjs --three DIR --glb FILE --plate FILE --shots shots.json --out DIR
// shots.json: [{ "name": "toon_medium", "mode": "toon", "shot": "medium", "e": {...}, "yaw": 0, ... }, ...]
// Prints the render time of every still; also writes timings.json.
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import path from 'node:path';

const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const out = path.resolve(opt('out')); mkdirSync(out, { recursive: true });
const shots = JSON.parse(readFileSync(opt('shots'), 'utf8'));
const T = { '.html': 'text/html', '.js': 'text/javascript', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e))); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
const url = `http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/lookdev.html?three=/${opt('three')}&glb=/${opt('glb')}` + (opt('plate') ? `&plate=/${opt('plate')}` : '');
await pg.goto(url); await pg.waitForFunction(() => window.ready || false, null, { timeout: 180000 }).catch(() => {});
if (!(await pg.evaluate(() => !!window.ready))) { console.error('viewer failed', errs); process.exit(1); }
console.log(JSON.stringify(await pg.evaluate(() => window.info)));
const times = {};
for (const s of shots) {
  const t0 = Date.now();
  await pg.evaluate(s => { window.render(s); return document.querySelector('canvas').toDataURL('image/png').length; }, s);
  times[s.name] = Date.now() - t0;
  await pg.screenshot({ path: `${out}/${s.name}.png` });
  console.log(s.name, times[s.name] + ' ms');
}
writeFileSync(`${out}/timings.json`, JSON.stringify({ times, errors: errs }, null, 2));
if (errs.length) console.error('errors:', errs.slice(0, 5));
await b.close(); srv.close();
