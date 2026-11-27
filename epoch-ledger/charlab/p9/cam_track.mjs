// P9: per-frame camera track (projected world points) and a set depth pass for a 2.5D shot (occlusion of the characters).
//   node epoch-ledger/charlab/p9/cam_track.mjs DEMO.json POINTS.json OUTDIR
// POINTS.json: {"name": [x,y,z], ...} world points to project every frame (feet, heads, foreground anchors).
// Writes OUTDIR/track.json ({fps, frames:[{pts:{name:[px,py,depth]}}]}) and OUTDIR/depth_00000.png … (the set's camera-space
// depth per pixel in millimetres, 24-bit RGB), so characters are occluded by whatever set geometry is nearer the camera. The camera path is the runtime's own (SH.camAt), so the
// composite and the plate rendered by shot_render.mjs agree to the pixel.
import { createRequire } from 'node:module'; import { createServer } from 'node:http';
import { readFileSync, writeFileSync, existsSync, statSync, mkdirSync } from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [demo, ptsFile, out] = process.argv.slice(2); const ROOT = process.cwd(); mkdirSync(out, { recursive: true });
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/.runtime/charlab/three/r0.186.1&demo=/${demo}&out=/.runtime/charlab/out_p3`);
for (let i = 0; i < 1200 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 250)); }
if (errs.length) { console.error(errs); process.exit(1); }
const D = JSON.parse(readFileSync(demo, 'utf8')); const N = Math.round(D.duration * 30); const pts = JSON.parse(readFileSync(ptsFile, 'utf8'));
await pg.evaluate(() => {                     // a depth pass of the set (camera-space distance, mm, 24-bit RGB)
  const { THREE } = window.SH;
  window.__depth = new THREE.ShaderMaterial({ vertexShader: 'varying float vZ; void main(){ vec4 mv = modelViewMatrix * vec4(position,1.); vZ = -mv.z; gl_Position = projectionMatrix * mv; }',
    fragmentShader: 'varying float vZ; void main(){ float mm = clamp(vZ * 1000., 0., 16777215.); float r = floor(mm / 65536.); float g = floor((mm - r * 65536.) / 256.); float b = mm - r * 65536. - g * 256.; gl_FragColor = vec4(r / 255., g / 255., b / 255., 1.); }' });
  window.__mc = document.createElement('canvas'); window.__mc.width = 1920; window.__mc.height = 1080;
});
const track = [];
for (let f = 0; f < N; f++) {
  const r = await pg.evaluate(([t, pts]) => {
    const { THREE, stage, cam, camAt } = window.SH; camAt(t); cam.updateMatrixWorld(); cam.updateProjectionMatrix();
    const o = {};
    for (const [k, p] of Object.entries(pts)) { const v = new THREE.Vector3(...p); const d = v.clone().applyMatrix4(cam.matrixWorldInverse).z;
      v.project(cam); o[k] = [(v.x + 1) / 2 * 1920, (1 - v.y) / 2 * 1080, -d]; }
    const R = stage.renderer, sc = stage.scene; const rt = R.getRenderTarget(); R.setRenderTarget(null);
    const cc = R.getClearColor(new THREE.Color()), ca = R.getClearAlpha(), tm = R.toneMapping, om = sc.overrideMaterial, bg = sc.background, fog = sc.fog;
    R.toneMapping = THREE.NoToneMapping; sc.overrideMaterial = window.__depth; sc.background = null; sc.fog = null;
    R.setClearColor(0xffffff, 1); R.clear(); R.render(sc, cam);
    sc.overrideMaterial = om; sc.background = bg; sc.fog = fog; R.toneMapping = tm;
    const g = window.__mc.getContext('2d'); g.clearRect(0, 0, 1920, 1080); g.drawImage(R.domElement, 0, 0, 1920, 1080);
    R.setClearColor(cc, ca); R.setRenderTarget(rt);
    return { pts: o, matte: window.__mc.toDataURL('image/png') };   // 'matte' = depth image
  }, [f / 30, pts]);
  writeFileSync(path.join(out, `depth_${String(f).padStart(5, '0')}.png`), Buffer.from(r.matte.split(',')[1], 'base64'));
  track.push({ pts: r.pts });
}
writeFileSync(path.join(out, 'track.json'), JSON.stringify({ fps: 30, frames: track }));
console.log('track', N, 'frames'); await b.close(); srv.close();
