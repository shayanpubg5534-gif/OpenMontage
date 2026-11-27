// P6: render one frame of a demo in the runtime (motion viewer) at 1080p and save a PNG (no video, no audio).
//   node epoch-ledger/charlab/p6/still.mjs DEMO.json OUT.png [quality=cin_cinematic] [t=0]
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync } from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [demo, out, Q = 'cin_cinematic', T = '0'] = process.argv.slice(2); const ROOT = process.cwd();
const TY = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': TY[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/.runtime/charlab/three/r0.186.1&demo=/${demo}&out=/.runtime/charlab/out_p3`);
for (let i = 0; i < 1200 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 250)); }
if (errs.length) { console.error(errs); process.exit(1); }
const t0 = Date.now();
const png = await pg.evaluate(async ([q, t]) => { const { QUALITY } = await import('../motion/runtime.js'); window.frame(+t, QUALITY[q]); window.frame(+t, QUALITY[q]);
  return document.querySelector('canvas').toDataURL('image/png'); }, [Q, T]);
writeFileSync(out, Buffer.from(png.slice(png.indexOf(',') + 1), 'base64')); console.log('wrote', out, (Date.now() - t0) / 1000, 's');
await b.close(); srv.close();
