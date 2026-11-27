// P4 profiler: what does a cinematic frame cost, and where? Loads a demo in the motion viewer, then for identical
// frames measures the frame time and per-pass times (main incl. shadow maps, depth/normal pass, post) with one
// feature toggled at a time. Each variant: one warm-up render (shader compile), then the median of N timed renders.
//
//   node epoch-ledger/charlab/bench/profile.mjs --demo DEMO.json --chars DIR --three DIR --out OUT.json [--t 1.5,4.2,8.5] [--n 3]
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { createServer } from 'http';
import { readFileSync, existsSync, statSync, writeFileSync } from 'fs';
import path from 'path';

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', '..');
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/${opt('three')}&demo=/${opt('demo')}&out=/${opt('chars')}`);
for (let i = 0; i < 1200 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 500)); }
if (errs.length) { console.error(errs); process.exit(1); }
const times = opt('t', '1.5,4.2,8.5').split(',').map(Number), N = +opt('n', 3);
const BAL = opt('preset') ? null : { msaa: 0, shadow: 1024, inkPass: true, fxaa: true };

// variants run in the page: apply(SH) returns an undo function; q overrides the quality preset
const VARIANTS = {
  base: { q: {} },
  no_fxaa: { q: { fxaa: false } },
  post_effects_off: { q: { inkPass: false } },
  charlook_standard: { apply: `const S = []; SH.stage.cast.forEach(c => c.root.traverse(o => { if (o.isMesh && o.material && o.material.isMeshPhysicalMaterial) { const m = o.material, n = new SH.THREE.MeshStandardMaterial({ map: m.map, roughness: m.roughness, metalness: 0, envMap: m.envMap, envMapIntensity: m.envMapIntensity }); S.push([o, m]); o.material = n; } }));
    return () => S.forEach(([o, m]) => o.material = m)` },
  msaa4_standard: { q: { msaa: 4, shadow: 2048, fxaa: false } },
  no_shadows: { apply: `SH.stage.renderer.shadowMap.enabled = false; SH.stage.scene.traverse(o => { if (o.material) [].concat(o.material).forEach(m => m.needsUpdate = true); });
    return () => { SH.stage.renderer.shadowMap.enabled = true; SH.stage.scene.traverse(o => { if (o.material) [].concat(o.material).forEach(m => m.needsUpdate = true); }); }` },
  shadow_map_frozen: { apply: `SH.stage.renderer.shadowMap.autoUpdate = false; return () => { SH.stage.renderer.shadowMap.autoUpdate = true; }` },
  shadow_512: { q: { shadow: 512 } },
  shadow_2048: { q: { shadow: 2048 } },
  shadow_pcf: { apply: `const r = SH.stage.renderer; r.shadowMap.type = SH.THREE.PCFShadowMap; SH.stage.key.shadow.map?.dispose(); SH.stage.key.shadow.map = null; SH.stage.scene.traverse(o => { if (o.material) [].concat(o.material).forEach(m => m.needsUpdate = true); });
    return () => { r.shadowMap.type = SH.THREE.VSMShadowMap; SH.stage.key.shadow.map?.dispose(); SH.stage.key.shadow.map = null; SH.stage.scene.traverse(o => { if (o.material) [].concat(o.material).forEach(m => m.needsUpdate = true); }); }` },
  no_depth_pass: { q: { inkPass: false } },
  ao_off: { apply: `const u = SH.stage.post.uniforms.ao, v = u.value; u.value = 0; return () => { u.value = v; }` },
  dof_off: { q: { dof: 0 } , dofOff: true },
  haze_off: { q: { haze: 0 } },
  no_sky_area_light: { apply: `const L = []; SH.stage.scene.traverse(o => { if (o.isRectAreaLight && o.visible) { o.visible = false; L.push(o); } }); return () => L.forEach(o => o.visible = true)` },
  no_practicals: { apply: `const L = []; SH.stage.scene.traverse(o => { if (o.isPointLight && o.visible) { o.visible = false; L.push(o); } }); return () => L.forEach(o => o.visible = true)` },
  no_spot_key: { apply: `const L = []; SH.stage.scene.traverse(o => { if (o.isSpotLight && o.visible) { o.visible = false; L.push(o); } }); return () => L.forEach(o => o.visible = true)` },
  no_env_map: { apply: `const e = SH.stage.scene.environment; SH.stage.scene.environment = null; return () => { SH.stage.scene.environment = e; }` },
  flat_set_textures: { apply: `const S = []; SH.SET.root.traverse(o => { if (!o.isMesh) return; for (const m of [].concat(o.material)) if (m.map || m.normalMap || m.roughnessMap) { S.push([m, m.map, m.normalMap, m.roughnessMap]); m.map = m.normalMap = m.roughnessMap = null; m.needsUpdate = true; } });
    return () => S.forEach(([m, a, n, r]) => { m.map = a; m.normalMap = n; m.roughnessMap = r; m.needsUpdate = true; })` },
  set_hidden: { apply: `SH.SET.root.visible = false; return () => { SH.SET.root.visible = true; }` },
  character_hidden: { apply: `const A = SH.actors.map(a => a.root || a.gltf?.scene).filter(Boolean); SH.stage.cast.forEach(c => c.root.visible = false); return () => SH.stage.cast.forEach(c => c.root.visible = true)` },
};
const only = opt('variants'); const names = only ? only.split(',') : Object.keys(VARIANTS);
const res = { demo: opt('demo'), preset: opt('preset') || 'balanced', times, n: N, variants: {} };
for (const name of names) {
  const V = VARIANTS[name]; const out = {};
  for (const t of times) {
    const r = await pg.evaluate(async ([t, q, apply, N, dofOff]) => {
      const SH = window.SH; SH.THREE = SH.THREE || SH.stage.THREE;
      if (q.__preset) { const { QUALITY } = await import('../motion/runtime.js'); const { __preset, ...rest } = q; q = { ...QUALITY[__preset], ...rest }; } else delete q.__preset;
      const undo = apply ? new Function('SH', apply)(SH) : null;
      const frame = (prof) => { SH.stage.prof = prof; const ms = SH.frame(t, q); SH.stage.prof = null; return ms; };
      if (dofOff) { const camAt = SH.camAt; }
      frame(null);                                                        // warm-up (shader compile after a toggle)
      const runs = []; for (let i = 0; i < N; i++) { const p = {}; const ms = frame(p); runs.push({ ms, ...p }); }
      if (undo) undo(); frame(null);
      runs.sort((a, b) => a.ms - b.ms); const m = runs[runs.length >> 1];
      return Object.fromEntries(Object.entries(m).map(([k, v]) => [k, Math.round(v)]));
    }, [t, { ...(BAL || {}), ...(V.q || {}), __preset: opt('preset') || null }, V.apply || null, N, !!V.dofOff]);
    out[t] = r;
  }
  res.variants[name] = out; console.log(name.padEnd(20), JSON.stringify(out));
}
// readback / capture cost: PNG and JPEG encodes of the 1080p canvas
res.capture = await pg.evaluate(() => { const c = document.querySelector('canvas'), r = {};
  for (const [k, ty, qq] of [['png', 'image/png'], ['jpeg90', 'image/jpeg', .9]]) { const t0 = performance.now(); for (let i = 0; i < 3; i++) c.toDataURL(ty, qq); r[k + '_ms'] = Math.round((performance.now() - t0) / 3); }
  return r; });
console.log('capture', JSON.stringify(res.capture));
writeFileSync(opt('out'), JSON.stringify(res, null, 1));
await b.close(); srv.close();
