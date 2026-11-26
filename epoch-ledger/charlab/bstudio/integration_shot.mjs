// node epoch-ledger/charlab/bstudio/integration_shot.mjs GLB OUT_PREFIX [extra query]
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync } from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [glb, out, extra = ''] = process.argv.slice(2); const ROOT = process.cwd();
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch(); const res = {};
for (const cam of ['medium', 'close']) {
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/integration.html?three=/.runtime/charlab/three/r0.186.1&glb=/${glb}&cam=${cam}&${extra}`);
  for (let i = 0; i < 600; i++) { if (await pg.evaluate(() => window.ready || window.err)) break; await new Promise(r => setTimeout(r, 500)); }
  const e = await pg.evaluate(() => window.err); if (e) { console.error(e); process.exit(1); }
  res[cam] = await pg.evaluate(() => window.info);
  await pg.locator('canvas').screenshot({ path: `${out}_${cam}.png` }); await pg.close();
}
writeFileSync(`${out}.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res)); await b.close(); srv.close();
