// node epoch-ledger/charlab/convert/studio_shots.mjs GLB FRAME_TIMINGS_JSON OUT_DIR [morphs] — the six views of render_views.py, in the runtime
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync, mkdirSync } from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [glb, frame, out, morphs = '', suffix = ''] = process.argv.slice(2); const ROOT = process.cwd(); mkdirSync(out, { recursive: true });
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch(); const res = {};
const views = process.env.VIEWS ? process.env.VIEWS.split(',') : suffix ? ['head_front', 'head_34'] : ['body_front', 'body_34', 'body_profile', 'head_front', 'head_34', 'head_profile'];
for (const v of views) {
  const body = v.startsWith('body'), K = +(process.env.SCALE || 1), w = Math.round((body ? 434 : 700) * K), h = Math.round(700 * K);   // SCALE: pixel density for close-up checks
  const pg = await b.newPage({ viewport: { width: w, height: h } });
  const t = Date.now();
  await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/studio.html?three=/.runtime/charlab/three/r0.186.1&glb=/${glb}&frame=/${frame}&view=${v}&w=${w}&h=${h}&morphs=${morphs}&exposure=${process.env.EXPOSURE || 1}&look=${process.env.LOOK || ''}`);
  for (let i = 0; i < 600; i++) { if (await pg.evaluate(() => window.ready || window.err)) break; await new Promise(r => setTimeout(r, 250)); }
  const e = await pg.evaluate(() => window.err); if (e) { console.error(e); process.exit(1); }
  res[v] = { ...(await pg.evaluate(() => window.info)), pageMs: Date.now() - t };
  await pg.locator('canvas').screenshot({ path: `${out}/${v}${suffix}.png` }); await pg.close();
}
writeFileSync(`${out}/runtime${suffix}.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res.head_front || res.head_34)); await b.close(); srv.close();
