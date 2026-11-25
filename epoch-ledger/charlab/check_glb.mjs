#!/usr/bin/env node
// Character lab (M2.1): load a character GLB in a given three.js release in headless Chromium (CPU WebGL) and measure
// what the production layer depends on. Writes <out>/check_<rev>.json and evidence frames.
//
//   node epoch-ledger/charlab/check_glb.mjs --three .runtime/charlab/three/r0.187.0 --glb .runtime/charlab/out/test_adult.glb --out DIR
//
// A static file server is started on the repository root (pages load the GLB and three.js modules by URL).
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';

const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const three = opt('three'), glb = opt('glb'), out = path.resolve(opt('out', '.runtime/charlab/check'));
mkdirSync(out, { recursive: true });
const rev = path.basename(three);

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.glb': 'model/gltf-binary', '.json': 'application/json', '.png': 'image/png' };
const server = createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(readFileSync(p));
}).listen(0);
const port = server.address().port;

const b = await chromium.launch();
const page = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; page.on('pageerror', e => errs.push(String(e))); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
const t0 = Date.now();
await page.goto(`http://127.0.0.1:${port}/epoch-ledger/charlab/viewer/index.html?three=/${three}&glb=/${glb}`);
await page.waitForFunction(() => window.ready || false, null, { timeout: 120000 }).catch(() => {});
const R = { three: rev, glb, load_ms: Date.now() - t0, errors: errs };
if (!(await page.evaluate(() => !!window.ready))) { R.ok = false; writeFileSync(`${out}/check_${rev}.json`, JSON.stringify(R, null, 2)); console.log(JSON.stringify(R, null, 2)); await b.close(); server.close(); process.exit(1); }
Object.assign(R, await page.evaluate(() => { const i = { ...window.info }; delete i.boneNames; return i; }));
const shot = async name => { await page.screenshot({ path: `${out}/${rev}_${name}.png` }); };
const hash = async () => createHash('sha1').update(await page.evaluate(() => document.querySelector('canvas').toDataURL('image/png'))).digest('hex');

// evidence frames: four framings mid-walk, an expression, the grip
const walk = R.clips.find(c => c[0] === 'walk') ? 'walk' : null;
for (const k of ['wide', 'medium', 'close', 'side']) { await page.evaluate(([c, k]) => window.renderAt(c, 1.2, k), [walk, k]); await shot(k); }
await page.evaluate(() => window.renderAt(null, 0, 'close', { 'eye-left-closure': 1, 'eye-right-closure': 1, 'mouth-corner-puller': .8, 'eyebrows-left-inner-up': .7, 'eyebrows-right-inner-up': .7 }));
await shot('expression');
await page.evaluate(() => window.renderAt('grip', 0, 'hand', {}, false)); await shot('hand_open');
await page.evaluate(() => window.renderAt('grip', 0.5, 'hand', {}, false)); await shot('hand_grip');

// morph targets change the face; finger action changes the hand
const px = async (fn) => { await page.evaluate(fn); return page.evaluate(() => document.querySelector('canvas').toDataURL('image/png')); };
const neutral = await px(() => window.renderAt(null, 0, 'close'));
const blink = await px(() => window.renderAt(null, 0, 'close', { 'eye-left-closure': 1, 'eye-right-closure': 1 }));
R.morph_changes_pixels = neutral !== blink;
const open = await px(() => window.renderAt('grip', 0, 'hand', {}, false)), grip = await px(() => window.renderAt('grip', .5, 'hand', {}, false));
R.grip_changes_pixels = open !== grip;

// determinism: the same time from two different seek histories (walk, wide)
if (walk) {
  await page.evaluate(([c]) => { window.renderAt(c, .3, 'wide'); window.renderAt(c, 1.4, 'wide'); }, [walk]); const a = await hash();
  await page.evaluate(([c]) => { window.renderAt(c, 2.6, 'wide'); window.renderAt(c, 1.4, 'wide'); }, [walk]); const c2 = await hash();
  R.deterministic = a === c2;
  // speed: 45 frames, render + PNG readback, medium framing
  const s = Date.now();
  for (let i = 0; i < 45; i++) await page.evaluate(([c, t]) => { window.renderAt(c, t, 'medium'); return document.querySelector('canvas').toDataURL('image/png').length; }, [walk, i / 30]);
  R.ms_per_frame_medium = Math.round((Date.now() - s) / 45);
  // prop socket and foot sliding, every frame of the walk
  const dur = R.clips.find(c => c[0] === walk)[1], frames = [];
  for (let f = 0; f / 30 <= dur - 1e-3; f++) frames.push(await page.evaluate(([c, t]) => window.measure(c, t), [walk, f / 30]));
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const off = frames.map(m => d(m.hand, m.prop)), off0 = off[0];
  R.prop_socket_drift_m = +Math.max(...off.map(o => Math.abs(o - off0))).toFixed(6);
  // foot sliding: horizontal motion of the toe joint while it is planted (within 2.5 cm of its 15th-percentile height)
  const slide = (key) => { const ys = frames.map(m => m[key][1]), lo = [...ys].sort((a, b) => a - b)[Math.floor(ys.length * .15)], thr = lo + .025; let tot = 0, n = 0, worst = 0;
    for (let i = 1; i < frames.length; i++) if (ys[i] <= thr && ys[i - 1] <= thr) { const h = Math.hypot(frames[i][key][0] - frames[i - 1][key][0], frames[i][key][2] - frames[i - 1][key][2]); tot += h; n++; worst = Math.max(worst, h); }
    return { planted_frames: n, mean_slide_mm_per_frame: n ? +(tot / n * 1000).toFixed(1) : null, worst_mm: +(worst * 1000).toFixed(1) }; };
  R.foot_sliding = { left: slide('ballL'), right: slide('ballR') };
  const ps = frames.map(m => m.pelvis); R.root_travel_m = +d(ps[0], ps[ps.length - 1]).toFixed(3);
  R.height_m = +(frames[0].head[1]).toFixed(3);
}
R.errors = errs.slice(0, 5);
R.ok = !errs.length;
writeFileSync(`${out}/check_${rev}.json`, JSON.stringify(R, null, 2));
console.log(JSON.stringify(R, null, 2));
await b.close(); server.close();
