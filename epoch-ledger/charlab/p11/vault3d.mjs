// P11: a fully animated 3D shot where 3D adds meaning: the bank's vault stays sealed and the cash inside stays put.
// Procedural three.js scene (no third-party models): a steel cage gate with a lock and a red SEALED tag, steel shelves of
// banknote bundles behind it (a generic fictional note design, not real currency). The camera moves in on the lock on
// "vault" and then past it to the cash on "no cash"; nothing in the vault moves. Rendered headless (SwiftShader), frames
// piped to ffmpeg; the series' painterly pass is applied afterwards like any plate.
//   node epoch-ledger/charlab/p11/vault3d.mjs OUT.mp4 DURATION 'KEYS_JSON' [--from F --to F]
// KEYS_JSON: [[t, [px,py,pz], [lx,ly,lz], fov], ...] camera keys in shot-local seconds (eased between keys).
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync, writeFileSync } from 'node:fs'; import { spawn } from 'node:child_process'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2); const [out, durS, keysS] = args;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? +args[i + 1] : d; };
const D = +durS, KEYS = JSON.parse(keysS), N = Math.round(D * 30), f0 = opt('from', 0), f1 = Math.min(opt('to', N - 1), N - 1);
const ROOT = process.cwd(), T = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript' };
const page = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000}canvas{display:block}</style></head><body>
<script type="importmap">{"imports":{"three":"/.runtime/charlab/three/r0.186.1/package/build/three.module.js","three/addons/":"/.runtime/charlab/three/r0.186.1/package/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three'; import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const KEYS = ${JSON.stringify(KEYS)};
const R = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true }); R.setPixelRatio(${+(process.env.P11_VAULT_SCALE || 1)}); R.setSize(1920, 1080);   // internal resolution scale (1 = native 1080p)
R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFShadowMap; R.shadowMap.autoUpdate = false; R.shadowMap.needsUpdate = true;   // nothing in the vault moves: shadow maps are rendered once R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.45;
R.outputColorSpace = THREE.SRGBColorSpace; document.body.appendChild(R.domElement);
const S = new THREE.Scene(); S.background = new THREE.Color('#231e19'); S.fog = new THREE.Fog('#231e19', 4, 10);
const cam = new THREE.PerspectiveCamera(40, 16 / 9, 0.05, 50);
const pm = new THREE.PMREMGenerator(R); S.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; S.environmentIntensity = 0.45;   // reflections for the steel
// --- textures drawn here (procedural: concrete, brushed steel, a generic banknote, the paper band, the tag) ---
const tex = (w, h, draw, rep) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); } return t; };
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const concrete = tex(512, 512, (g, w, h) => { g.fillStyle = '#5a554e'; g.fillRect(0, 0, w, h); for (let i = 0; i < 9000; i++) { const v = 70 + rnd() * 40 | 0; g.fillStyle = 'rgba(' + v + ',' + (v - 4) + ',' + (v - 9) + ',.35)'; g.fillRect(rnd() * w, rnd() * h, 2 + rnd() * 3, 2 + rnd() * 3); } }, [4, 4]);
const steel = tex(256, 256, (g, w, h) => { g.fillStyle = '#8a8c8e'; g.fillRect(0, 0, w, h); for (let i = 0; i < 400; i++) { g.fillStyle = 'rgba(255,255,255,' + rnd() * .06 + ')'; g.fillRect(0, rnd() * h, w, 1); } });
const note = tex(512, 220, (g, w, h) => {            // a fictional note: no portrait, no real currency design
  g.fillStyle = '#c9d3bf'; g.fillRect(0, 0, w, h); g.strokeStyle = '#6f8466'; g.lineWidth = 10; g.strokeRect(8, 8, w - 16, h - 16);
  for (let i = 0; i < 40; i++) { g.strokeStyle = 'rgba(80,105,75,.18)'; g.lineWidth = 2; g.beginPath(); g.arc(w / 2, h / 2, 20 + i * 4, 0, 6.3); g.stroke(); }
  g.fillStyle = '#4f6349'; g.font = 'bold 54px Georgia'; g.fillText('100', 26, 76); g.fillText('100', w - 120, h - 26); g.font = 'bold 22px Georgia'; g.fillText('LEDGER RESERVE NOTE', 120, 40); });
const band = tex(256, 64, (g, w, h) => { g.fillStyle = '#c9a25a'; g.fillRect(0, 0, w, h); g.fillStyle = '#5a3f16'; g.font = 'bold 30px Georgia'; g.fillText('$10,000', 52, 44); });
const tagT = tex(512, 256, (g, w, h) => { g.fillStyle = '#9e2a22'; g.fillRect(0, 0, w, h); g.strokeStyle = '#f3e6d0'; g.lineWidth = 8; g.strokeRect(14, 14, w - 28, h - 28);
  g.fillStyle = '#f3e6d0'; g.font = 'bold 96px Georgia'; g.textAlign = 'center'; g.fillText('SEALED', w / 2, 150); g.font = 'bold 30px Georgia'; g.fillText('VAULT · DO NOT OPEN', w / 2, 210); });
const M = (o) => new THREE.MeshStandardMaterial(o);
const mConcrete = new THREE.MeshLambertMaterial({ map: concrete }), mSteel = M({ map: steel, color: '#9a9ca0', metalness: .85, roughness: .38 });
const mDark = M({ color: '#3c3e42', metalness: .7, roughness: .5 }), mBrass = M({ color: '#b08a45', metalness: .9, roughness: .3 });
// room
const floor = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), mConcrete); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; S.add(floor);
const wallM = new THREE.MeshLambertMaterial({ map: concrete, color: '#8d8579' });   // matte surfaces: Lambert looks the same, shades cheaper
const back = new THREE.Mesh(new THREE.PlaneGeometry(14, 5), wallM); back.position.set(0, 2.5, -2.4); back.receiveShadow = true; S.add(back);
for (const x of [-3.2, 3.2]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(6, 5), wallM); w.position.set(x, 2.5, -0.6); w.rotation.y = x < 0 ? Math.PI / 2 : -Math.PI / 2; S.add(w); }
// cage gate at z = 0: frame, bars, rails, the lock box and the SEALED tag
const gate = new THREE.Group(); S.add(gate);
const box = (w, h, d, m, x, y, z) => { const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); b.position.set(x, y, z); b.castShadow = b.receiveShadow = true; gate.add(b); return b; };
box(3.4, .12, .12, mDark, 0, 2.45, 0); box(3.4, .08, .1, mDark, 0, .04, 0); for (const x of [-1.7, 1.7, -0.02]) box(.1, 2.5, .12, mDark, x, 1.25, 0);
for (const y of [.35, 1.18, 2.05]) box(3.4, .05, .05, mSteel, 0, y, .02);
const barG = new THREE.CylinderGeometry(.013, .013, 2.38, 12);
for (let x = -1.62; x <= 1.62; x += .105) { if (Math.abs(x) < .06) continue; const b = new THREE.Mesh(barG, mSteel); b.position.set(x, 1.24, 0); b.castShadow = true; gate.add(b); }
box(.2, .26, .09, mSteel, .12, 1.12, .07); box(.05, .05, .02, mDark, .12, 1.1, .118);              // lock case, keyhole plate
const dial = new THREE.Mesh(new THREE.CylinderGeometry(.045, .045, .03, 32), mBrass); dial.rotation.x = Math.PI / 2; dial.position.set(.12, 1.19, .125); gate.add(dial);
const shackle = new THREE.Mesh(new THREE.TorusGeometry(.055, .012, 12, 32, Math.PI), mSteel); shackle.position.set(.12, 1.25, .07); gate.add(shackle);
const tag = new THREE.Mesh(new THREE.PlaneGeometry(.26, .13), M({ map: tagT, roughness: .8, side: THREE.DoubleSide })); tag.position.set(.12, .93, .13); tag.rotation.z = -.06; gate.add(tag);
const cord = new THREE.Mesh(new THREE.CylinderGeometry(.003, .003, .13, 6), M({ color: '#c8b89a' })); cord.position.set(.12, 1.02, .125); gate.add(cord);
// shelves of cash behind the gate (InstancedMesh bundles with a paper band)
const shelfM = M({ color: '#55585d', metalness: .6, roughness: .55 });
const bundleG = new THREE.BoxGeometry(.156, .03, .066), noteM = M({ map: note, roughness: .75 }), sideM = M({ color: '#b9c4ad', roughness: .9 });
const bandG = new THREE.BoxGeometry(.032, .031, .067), bandM = M({ map: band, roughness: .7 });
for (const sx of [-1.0, .55]) {
  for (const y of [.25, .75, 1.25, 1.75]) {
    const sh = new THREE.Mesh(new THREE.BoxGeometry(1.3, .03, .5), shelfM); sh.position.set(sx, y, -1.25); sh.receiveShadow = sh.castShadow = true; S.add(sh);
    const cols = 7, rows = 3, layers = 6, n = cols * rows * layers;
    const im = new THREE.InstancedMesh(bundleG, [sideM, sideM, noteM, sideM, sideM, sideM], n), ib = new THREE.InstancedMesh(bandG, bandM, n);
    im.castShadow = im.receiveShadow = true; let k = 0; const m4 = new THREE.Matrix4();
    for (let c = 0; c < cols; c++) for (let r = 0; r < rows; r++) for (let l = 0; l < layers; l++, k++) {
      m4.makeRotationY((rnd() - .5) * .03); m4.setPosition(sx - .55 + c * .17, y + .03 + l * .031, -1.42 + r * .075); im.setMatrixAt(k, m4); ib.setMatrixAt(k, m4); }
    S.add(im); S.add(ib);
  }
  for (const px of [-.64, .64]) { const p = new THREE.Mesh(new THREE.BoxGeometry(.03, 2.0, .5), shelfM); p.position.set(sx + px, 1.0, -1.25); S.add(p); }
}
// light: a warm spot on the cash, a cool key across the gate, low ambient
S.add(new THREE.HemisphereLight('#d9d2c5', '#3a342e', .7));
const sp = new THREE.SpotLight('#ffd9a0', 38, 7, .62, .55, 1.6); sp.position.set(-.2, 2.9, -.4); sp.target.position.set(-.2, .9, -1.3); sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); S.add(sp, sp.target);
const key = new THREE.SpotLight('#cfe0ff', 26, 8, .5, .6, 1.4); key.position.set(1.8, 2.6, 2.2); key.target.position.set(0, 1.1, 0); S.add(key, key.target);   // fill/key without shadows: one shadowed light is enough here, and halves the shading cost
const ss = x => (x = Math.min(1, Math.max(0, x)), x * x * (3 - 2 * x));
window.frame = t => {
  let a = KEYS[0], b = KEYS[KEYS.length - 1];
  for (let i = 1; i < KEYS.length; i++) if (t < KEYS[i][0]) { a = KEYS[i - 1]; b = KEYS[i]; break; }
  const u = b[0] > a[0] ? ss((t - a[0]) / (b[0] - a[0])) : 1, L = (p, q) => p.map((v, j) => v + (q[j] - v) * u);
  cam.position.set(...L(a[1], b[1])); cam.lookAt(...L(a[2], b[2])); cam.fov = a[3] + (b[3] - a[3]) * u; cam.updateProjectionMatrix();
  const t0 = performance.now(); R.render(S, cam); const px = new Uint8Array(4); const gl = R.getContext(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); return performance.now() - t0;
};
window.ready = true;
</script></body></html>`;
const srv = createServer((q, r) => { const u = decodeURIComponent(new URL(q.url, 'http://x').pathname);
  if (u === '/') { r.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); return r.end(page); }
  const p = path.join(ROOT, u); if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } }); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto(`http://127.0.0.1:${srv.address().port}/`); await pg.waitForFunction(() => window.ready || false, null, { timeout: 60000 });
if (errs.length) { console.error(errs); process.exit(1); }
const cdp = await pg.context().newCDPSession(pg);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv444p', '-threads', '1', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise(r => ff.on('close', r)); const t0 = Date.now();
for (let f = f0; f <= f1; f++) {
  const rt = await pg.evaluate(t => window.frame(t), f / 30); if (process.env.P11_PROF) console.error('render_ms', Math.round(rt));
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true });
  if (!ff.stdin.write(Buffer.from(data, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await done; await b.close(); srv.close();
if (errs.length) { console.error(errs); process.exit(1); }
console.log(JSON.stringify({ out, frames: f1 - f0 + 1, s_per_frame: +((Date.now() - t0) / 1000 / (f1 - f0 + 1)).toFixed(3) }));
