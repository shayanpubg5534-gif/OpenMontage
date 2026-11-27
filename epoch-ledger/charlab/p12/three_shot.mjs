// P12: reusable renderer for selective 3D shots (procedural three.js scenes, no third-party models). A scene is an ES
// module exporting build({THREE, scene, renderer, addons, events}) → {update(t)} (optional); the camera follows keyed
// positions (eased), so camera moves are written from the narration-to-visual map like every other visual.
//   node epoch-ledger/charlab/p12/three_shot.mjs SCENE.js OUT.mp4 DURATION 'KEYS_JSON' ['EVENTS_JSON'] [--from F --to F]
// KEYS: [[t, [px,py,pz], [lx,ly,lz], fov], ...] shot-local seconds. EVENTS: {name: t} shot-local (scene state changes,
// e.g. a stamp appearing). Internal render scale P12_SCALE (default 0.75; output 1080p). SwiftShader WebGL, PNG → ffmpeg.
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync } from 'node:fs'; import { spawn } from 'node:child_process'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2); const [sceneFile, out, durS, keysS, evS] = args;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? +args[i + 1] : d; };
const D = +durS, N = Math.round(D * 30), f0 = opt('from', 0), f1 = Math.min(opt('to', N - 1), N - 1);
const ROOT = process.cwd(), T = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png' };
const sceneUrl = '/' + path.relative(ROOT, path.resolve(sceneFile));
const page = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000}canvas{display:block}</style></head><body>
<script type="importmap">{"imports":{"three":"/.runtime/charlab/three/r0.186.1/package/build/three.module.js","three/addons/":"/.runtime/charlab/three/r0.186.1/package/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three'; import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const KEYS = ${keysS}, EVENTS = ${evS || '{}'};
const R = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true }); R.setPixelRatio(${+(process.env.P12_SCALE || 0.75)}); R.setSize(1920, 1080);
R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap; R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.0;
R.outputColorSpace = THREE.SRGBColorSpace; document.body.appendChild(R.domElement);
const S = new THREE.Scene(); const cam = new THREE.PerspectiveCamera(40, 16 / 9, 0.03, 80);
const pm = new THREE.PMREMGenerator(R); S.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; S.environmentIntensity = 0.3;
const mod = await import('${sceneUrl}'); const sc = (await mod.build({ THREE, scene: S, renderer: R, events: EVENTS })) || {};
if (!sc.dynamicShadows) { R.shadowMap.autoUpdate = false; R.shadowMap.needsUpdate = true; }   // static scenes: shadow maps once
const ss = x => (x = Math.min(1, Math.max(0, x)), x * x * (3 - 2 * x));
window.frame = t => {
  let a = KEYS[0], b = KEYS[KEYS.length - 1];
  for (let i = 1; i < KEYS.length; i++) if (t < KEYS[i][0]) { a = KEYS[i - 1]; b = KEYS[i]; break; }
  const u = b[0] > a[0] ? ss((t - a[0]) / (b[0] - a[0])) : 1, L = (p, q) => p.map((v, j) => v + (q[j] - v) * u);
  cam.position.set(...L(a[1], b[1])); cam.lookAt(...L(a[2], b[2])); cam.fov = a[3] + (b[3] - a[3]) * u; cam.updateProjectionMatrix();
  const sig = [cam.position.toArray(), cam.quaternion.toArray(), cam.fov, sc.state ? sc.state(t) : ''].map(String).join('|');
  if (sig === window.__last) return false;          // nothing changed since the last frame: reuse it (a static hold costs one render)
  window.__last = sig; if (sc.update) sc.update(t); R.render(S, cam); return true;
};
window.ready = true;
</script></body></html>`;
const srv = createServer((q, r) => { const u = decodeURIComponent(new URL(q.url, 'http://x').pathname);
  if (u === '/') { r.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); return r.end(page); }
  const p = path.join(ROOT, u); if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } }); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto(`http://127.0.0.1:${srv.address().port}/`);
for (let i = 0; i < 240 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 250)); }
if (errs.length) { console.error(errs); process.exit(1); }
const cdp = await pg.context().newCDPSession(pg);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv444p', '-threads', '1', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise(r => ff.on('close', r)); const t0 = Date.now(); let last = null, rendered = 0;
for (let f = f0; f <= f1; f++) {
  const changed = await pg.evaluate(t => window.frame(t), f / 30);
  if (changed || !last) { const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true }); last = Buffer.from(data, 'base64'); rendered++; }
  if (!ff.stdin.write(last)) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await done; await b.close(); srv.close();
if (errs.length) { console.error(errs); process.exit(1); }
console.log(JSON.stringify({ out, frames: f1 - f0 + 1, rendered, s_per_frame: +((Date.now() - t0) / 1000 / (f1 - f0 + 1)).toFixed(3) }));
