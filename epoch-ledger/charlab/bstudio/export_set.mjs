// node epoch-ledger/charlab/bstudio/export_set.mjs SET_JSON_URL OUT.glb
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync } from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright'); const [set, out] = process.argv.slice(2); const ROOT = process.cwd();
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch(); const pg = await b.newPage();
await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/export_set.html?three=/.runtime/charlab/three/r0.186.1&set=${set}`);
for (let i = 0; i < 240; i++) { if (await pg.evaluate(() => window.ready || window.err)) break; await new Promise(r => setTimeout(r, 500)); }
const e = await pg.evaluate(() => window.err); if (e) { console.error(e); process.exit(1); }
writeFileSync(out, Buffer.from(await pg.evaluate(() => window.glb), 'base64')); console.log('wrote', out); await b.close(); srv.close();
