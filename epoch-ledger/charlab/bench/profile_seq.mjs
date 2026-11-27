// P4: quality-profile benchmark on consecutive frames (so environment-cache anchors are amortised as in a real render).
// For each profile and each window [from, to] renders every frame in order, records the frame time, saves sample frames
// (identical cameras, poses and lights across profiles); compare cin_balanced with cin_reference_pcf (the same profile
// without the cache, rendered in its own page) to quantify the re-projection error.
//
//   node epoch-ledger/charlab/bench/profile_seq.mjs --demo D.json --chars DIR --three DIR --out DIR
//        [--windows 0.5:2.5,3.5:5.5,7.5:9.5] [--profiles balanced,cin_fast,cin_balanced,cin_cinematic] [--samples 1.5,4.2,8.5]
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', '..');
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const out = path.resolve(opt('out')); mkdirSync(out, { recursive: true });
const windows = opt('windows', '0.5:2.5,3.5:5.5,7.5:9.5').split(',').map(w => w.split(':').map(Number));
const profiles = opt('profiles', 'balanced,cin_fast,cin_balanced,cin_cinematic').split(',');
const samples = opt('samples', '1.5,4.2,8.5').split(',').map(Number);
const b = await chromium.launch();
const res = { demo: opt('demo'), windows, profiles: {} };
for (const prof of profiles) {
  // a fresh page per profile: no shader or cache state carried over
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } }); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/${opt('three')}&demo=/${opt('demo')}&out=/${opt('chars')}`);
  for (let i = 0; i < 1200 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 500)); }
  if (errs.length) { console.error(prof, errs); process.exit(1); }
  const Q = await pg.evaluate(p => { const R = window.SH; return null; }, prof);
  const r = { windows: [], samples: {} };
  for (const [a, z] of windows) {
    const ms = await pg.evaluate(async ([a, z, prof]) => {
      const { QUALITY } = await import('../motion/runtime.js'); const q = QUALITY[prof]; const out = [];
      window.SH.frame(a, q);                                                     // first frame: shader compile, not counted
      for (let f = Math.round(a * 30) + 1; f <= Math.round(z * 30); f++) out.push(window.SH.frame(f / 30, q));
      return out;
    }, [a, z, prof]);
    const s = [...ms].sort((x, y) => x - y);
    r.windows.push({ from: a, to: z, frames: ms.length, mean_ms: Math.round(ms.reduce((x, y) => x + y, 0) / ms.length), median_ms: Math.round(s[s.length >> 1]), max_ms: Math.round(s[s.length - 1]) });
  }
  r.env = await pg.evaluate(() => window.SH.stage.envStats && window.SH.stage.envStats());
  for (const t of samples) {
    const png = await pg.evaluate(async ([t, prof]) => { const { QUALITY } = await import('../motion/runtime.js'); window.SH.frame(t, QUALITY[prof]); return document.querySelector('canvas').toDataURL('image/png'); }, [t, prof]);
    writeFileSync(`${out}/${prof}_${t}.png`, Buffer.from(png.split(',')[1], 'base64'));
  }
  res.profiles[prof] = r; console.log(prof.padEnd(14), JSON.stringify(r.windows.map(w => w.mean_ms)), JSON.stringify(r.env));
  await pg.close();
}
writeFileSync(`${out}/profiles.json`, JSON.stringify(res, null, 1));
await b.close(); srv.close();
