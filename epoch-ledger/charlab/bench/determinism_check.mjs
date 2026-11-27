// P5 determinism check: frame N rendered directly after load vs after rendering frames 1..N-1 must be bit-identical.
//   node epoch-ledger/charlab/bench/determinism_check.mjs DEMO PROFILE direct|seq [N]   (prints pixel/pose/morph hashes)
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync } from 'node:fs';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', '..'), demo = process.argv[2] || 'epoch-ledger/charlab/motion/demos/p5_test.json', prof = process.argv[3] || 'cin_reference_pcf';
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': p.endsWith('.js') ? 'text/javascript' : p.endsWith('.html') ? 'text/html' : 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/.runtime/charlab/three/r0.186.1&demo=/${demo}&out=/.runtime/charlab/out_p3`);
for (let i = 0; i < 600; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 300)); }
const mode = process.argv[4] || 'direct', F_AT = +(process.argv[5] || 45);
console.log(mode, await pg.evaluate(async ([prof, mode, fAt]) => {
  const { QUALITY } = await import('../motion/runtime.js'); const q = QUALITY[prof], c = document.querySelector('canvas'), gl = c.getContext('webgl2');
  const F = f => window.SH.frame(f / 30, q);
  F(0); if (mode === 'seq') for (let f = 1; f < fAt; f++) F(f); F(fAt);
  const a = new Uint8Array(1920 * 1080 * 4); gl.readPixels(0, 0, 1920, 1080, gl.RGBA, gl.UNSIGNED_BYTE, a);
  const h = await crypto.subtle.digest('SHA-256', a); const A2 = window.SH.actors[0];
  const pose = A2.list.map(b => b.matrixWorld.elements.map(x => x.toFixed(5)).join(',')).join('|');
  const ph = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(pose));
  const mi = A2.meshes.filter(m => m.morphTargetInfluences).map(m => m.morphTargetInfluences.map(x => x.toFixed(4)).join(',')).join('|');
  const mh = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(mi));
  const hex = b => [...new Uint8Array(b)].slice(0, 6).map(x => x.toString(16).padStart(2, '0')).join('');
  return { pixels: hex(h), pose: hex(ph), morphs: hex(mh), cam: window.SH.cam.position.toArray().map(x => x.toFixed(5)).join(',') };
}, [prof, mode, F_AT]));
await b.close(); srv.close();
