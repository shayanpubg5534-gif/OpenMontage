// Character lab (P3): opt-in cinematic upgrade of an M4.1 set (stage look 'cinematic'; sets without a "cinematic" block
// and the 'cel'/'editorial' looks are untouched).
//
// What it adds over the illustrated set:
//   materials — physically based surfaces from CC0 texture sets (Poly Haven, see assets/textures_manifest.json): colour,
//               roughness and normal maps at a real-world scale (UVs rewritten in metres), matched to the set's palette;
//   detail    — architectural and dressing pieces the flat look did not need: crown moulding, raised wainscot panels,
//               ceiling, radiator, curtains, desk pad, ledgers, pen cup;
//   light     — motivated by the room: daylight through the window (the sun casts the mullions onto the floor, a soft
//               area light is the sky), warm practical lamps with visible glowing shades, a soft room bounce
//               (image-based) instead of a flat hemisphere;
//   lens      — AO, haze and depth of field come from the stage's depth pass (stage.render options).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

const deg = d => d * Math.PI / 180;

// rewrite a primitive's UVs so one UV unit is one metre (textures then tile at their real size on any box/plane/cylinder)
function metricUV(geo) {
  const P = geo.parameters || {}, uv = geo.attributes.uv; if (!uv) return geo;
  if (geo.type === 'BoxGeometry') {
    const { width: w, height: h, depth: d } = P, dims = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]];
    // indices are shared within a face, so a vertex is visited several times: scale the pristine UVs (idempotent)
    const base = new THREE.BoxGeometry(w, h, d).attributes.uv;
    for (const [gi, g] of (geo.groups || []).entries()) { const [su, sv] = dims[gi] || [1, 1];
      for (let i = g.start; i < g.start + g.count; i++) { const vi = geo.index ? geo.index.getX(i) : i; uv.setXY(vi, base.getX(vi) * su, base.getY(vi) * sv); } }
  } else if (geo.type === 'PlaneGeometry') { for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * P.width, uv.getY(i) * P.height); }
  else if (geo.type === 'CylinderGeometry') { const c = Math.PI * (P.radiusTop + P.radiusBottom); for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * c, uv.getY(i) * P.height); }
  else return geo;
  uv.needsUpdate = true; geo.userData.metric = true; return geo;
}

export async function applyCinematic(stage, SET, cfg = {}) {
  const { renderer, scene, key, fill, hemi } = stage, root = SET.root, TEX = cfg.textures || '/.runtime/charlab/textures';
  const loader = new THREE.TextureLoader(), cache = {}, report = { materials: 0, detail: 0, lights: [] };
  const tex = async (set, map, size, srgb) => { const k = `${set}/${map}/${size}`; if (cache[k]) return cache[k];
    const t = await loader.loadAsync(`${TEX}/${set}/${map}.jpg`); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / size, 1 / size);
    t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return (cache[k] = t); };
  async function pbr(rule) {
    if (!rule.set) return new THREE.MeshStandardMaterial({ color: new THREE.Color(rule.color || '#888'), roughness: rule.rough ?? .7, metalness: rule.metal ?? 0 });
    const s = rule.size || 1, diff = await tex(rule.set, 'diff', s, true);
    const m = new THREE.MeshStandardMaterial({ map: diff, roughnessMap: await tex(rule.set, 'rough', s), normalMap: await tex(rule.set, 'nor', s),
      normalScale: new THREE.Vector2(rule.normal ?? 1, rule.normal ?? 1), color: new THREE.Color(rule.tint || '#ffffff'), roughness: rule.rough ?? 1, metalness: rule.metal ?? 0,
      envMapIntensity: rule.env ?? cfg.envSpec ?? .5 });   // the room bounce is soft: no mirror-like sheen on wood or cloth
    if (rule.contrast != null) {          // calm a busy texture: pull every texel towards the texture's mean colour
      const c = document.createElement('canvas'); c.width = c.height = 1; const x = c.getContext('2d'); x.drawImage(diff.image, 0, 0, 1, 1);
      const mean = new THREE.Color().setRGB(...[...x.getImageData(0, 0, 1, 1).data].slice(0, 3).map(v => v / 255), THREE.SRGBColorSpace);
      m.onBeforeCompile = sh => { sh.uniforms.texMean = { value: mean }; sh.uniforms.texContrast = { value: rule.contrast };
        sh.fragmentShader = 'uniform vec3 texMean; uniform float texContrast;\n' + sh.fragmentShader.replace('#include <map_fragment>',
          '#include <map_fragment>\n#ifdef USE_MAP\n diffuseColor.rgb = diffuseColor.rgb / max(sampledDiffuseColor.rgb, vec3(1e-4)) * mix(texMean, sampledDiffuseColor.rgb, texContrast);\n#endif'); };
      m.customProgramCacheKey = () => 'cin-contrast';
    }
    return m;
  }
  const mats = {}; for (const [k, r] of Object.entries(cfg.materials || {})) mats[k.toLowerCase()] = await pbr(r);
  const matFor = async name => mats[name] || (mats[name] = await pbr((cfg.materials || {})[name] || { color: name }));

  // the view through the window is out of focus and a little overexposed, as a lens focused on the room would see it
  function softView(m) { const t = m.map; if (!t) return; const go = () => { const im = t.image, c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
      const x = c.getContext('2d'); x.filter = `blur(${cfg.viewBlur ?? 7}px) contrast(.78) brightness(1.08) saturate(.85)`; x.drawImage(im, 0, 0);
      const n = new THREE.CanvasTexture(c); n.colorSpace = THREE.SRGBColorSpace; n.offset.copy(t.offset); n.repeat.copy(t.repeat); m.map = n; m.needsUpdate = true; };
    if (t.image && t.image.complete !== false && t.image.width) go(); else jobs0.push(new Promise(r => { const i = setInterval(() => { if (t.image && t.image.width) { clearInterval(i); go(); r(); } }, 30); })); }
  const jobs0 = [];
  // ── 1. surfaces: palette colour → textured material ───────────────────────────────────────────────────────────
  const meshes = []; root.traverse(o => { if (o.isMesh) meshes.push(o); });
  for (const o of meshes) {
    const list = Array.isArray(o.material) ? o.material : [o.material];
    const out = list.map(m => {
      if (m.isMeshBasicMaterial) {            // pictures, signs, screens: lit like paper; the window view and lamp glow are emitters
        if (o.userData.kind === 'backdrop') { m.color.multiplyScalar(cfg.windowGlow ?? 2.2); softView(m); return m; }
        if (!m.map) { m.color.multiplyScalar(cfg.glow ?? 6); o.castShadow = false; return m; }
        const n = new THREE.MeshStandardMaterial({ map: m.map, roughness: .85 }); return n; }
      const hex = '#' + m.color.getHexString(), rule = mats[hex];
      if (!rule) return m;
      if (rule.map && !o.geometry.userData.metric) { o.geometry = metricUV(o.geometry.clone()); }
      report.materials++; return rule; });
    o.material = Array.isArray(o.material) ? out : out[0];
    o.castShadow = o.castShadow !== false; o.receiveShadow = true;
  }

  // ── 2. architectural detail and dressing ──────────────────────────────────────────────────────────────────────
  const R = SET.spec?.room || cfg.room, D = new THREE.Group(); D.name = 'cinematic-detail'; root.add(D);
  const add = (geo, matName, x, y, z, ry = 0, cast = true) => { const m = new THREE.Mesh(geo, null); m.position.set(x, y, z); m.rotation.y = ry; m.castShadow = cast; m.receiveShadow = true; D.add(m); report.detail++;
    return matFor(matName).then(mt => { if (mt.map) m.geometry = metricUV(m.geometry); m.material = mt; return m; }); };
  const jobs = [];
  if (R) {
    const hw = R.w / 2, back = R.back, front = R.front ?? 3, trim = cfg.trim || 'trim', wall = cfg.wall || 'wall';
    // ceiling and crown moulding: the room is closed, so light stays in it and the top of frame is never empty
    jobs.push(add(new THREE.BoxGeometry(R.w + .8, .06, front - back + .4), cfg.ceiling || wall, 0, R.h + .03, (back + front) / 2, 0, false));
    jobs.push(add(new THREE.BoxGeometry(R.w + .8, .12, .1), trim, 0, R.h - .06, back + .1));
    for (const sx of [-1, 1]) jobs.push(add(new THREE.BoxGeometry(.1, .12, front - back), trim, sx * (hw - .1), R.h - .06, (back + front) / 2));
    // raised panels on the wainscot of the back wall (skipping the window and furniture is unnecessary: they occlude)
    if (R.wainscot) { const ph = R.wainscot.h - .28, n = Math.floor((R.w - .4) / .62);
      for (let i = 0; i < n; i++) { const x = -hw + .3 + (i + .5) * (R.w - .6) / n;
        jobs.push(add(new THREE.BoxGeometry((R.w - .6) / n - .14, ph, .02), cfg.panel || trim, x, .14 + ph / 2 + .02, back + .1)); } }
  }
  const W = SET.spec?.window;
  if (W && cfg.curtains !== false) {           // linen curtains, gathered at both sides of the window (folds from a sine profile)
    for (const sx of [-1, 1]) { const g = new THREE.PlaneGeometry(.5, W.h + .55, 24, 1), p = g.attributes.position;
      for (let i = 0; i < p.count; i++) p.setZ(i, Math.sin(p.getX(i) * 26) * .04 + Math.sin(p.getX(i) * 61) * .01 + .045);
      g.computeVertexNormals(); const x = W.x + sx * (W.w / 2 + .18);
      jobs.push(add(g, cfg.curtain || 'curtain', x, W.sill + W.h / 2 + .2, R.back + .2).then(m => { m.material = m.material.clone(); m.material.side = THREE.DoubleSide; })); }
    jobs.push(add(new THREE.CylinderGeometry(.015, .015, W.w + 1.4, 10), 'brass', W.x, W.sill + W.h + .5, R.back + .2).then(m => { m.rotation.z = Math.PI / 2; }));
  }
  if (W && cfg.radiator !== false) { const rw = Math.min(W.w * .8, 1.6);   // a cast-iron radiator under the window
    for (let i = 0; i < Math.floor(rw / .07); i++) jobs.push(add(new THREE.BoxGeometry(.045, .55, .12), cfg.radiatorMat || 'radiator', W.x - rw / 2 + i * .07, .4, R.back + .16)); }
  for (const it of cfg.dressing || []) {          // small objects that sell the place: desk pad, ledgers, pen cup
    if (it.type === 'pad') jobs.push(add(new THREE.BoxGeometry(it.size[0], .006, it.size[1]), 'leather', it.pos[0], it.pos[1] + .003, it.pos[2], deg(it.rot || 0)));
    if (it.type === 'ledgers') it.list.forEach(([c, h, dx, dz, r], i) => jobs.push(add(new THREE.BoxGeometry(.24, h, .32), c, it.pos[0] + dx, it.pos[1] + it.list.slice(0, i).reduce((a, b) => a + b[1], 0) + h / 2, it.pos[2] + dz, deg(r))));
    if (it.type === 'pens') { jobs.push(add(new THREE.CylinderGeometry(.035, .032, .1, 16), 'brass', it.pos[0], it.pos[1] + .05, it.pos[2]));
      for (let i = 0; i < 3; i++) jobs.push(add(new THREE.CylinderGeometry(.004, .004, .15, 6), '#1d2433', it.pos[0] + (i - 1) * .012, it.pos[1] + .12, it.pos[2] + (i % 2) * .01).then(m => { m.rotation.z = (i - 1) * .12; })); }
  }
  await Promise.all([...jobs, ...jobs0]);

  // ── 3. motivated light ────────────────────────────────────────────────────────────────────────────────────────
  const L = cfg.lights || {};
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(new RoomEnvironment(), .04).texture; pm.dispose();
  scene.environmentIntensity = L.bounce ?? .35;                              // the room's soft bounce light
  if (L.bounceTint) scene.environmentRotation = new THREE.Euler(0, deg(L.bounceYaw || 0), 0);
  if (L.sun && W) {                                                          // daylight through the window: the stage key becomes the sun
    key.color.set(L.sun.color || '#fff4e6'); key.intensity = L.sun.i ?? 3;
    const wc = new THREE.Vector3(W.x, W.sill + W.h / 2, R.back);
    key.position.copy(wc).addScaledVector(new THREE.Vector3(...(L.sun.dir || [-.6, .55, -1])).normalize(), 8);   // dir: from the window towards the sun
    key.target.position.set(...(L.sun.target || [W.x + 1, 0, R.back + 2.2])); key.target.updateMatrixWorld();
    Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: .5, far: 20 }); key.shadow.camera.updateProjectionMatrix();
    report.lights.push('sun');
  }
  if (L.sky && W) {                                                          // the sky seen through the window: a soft area light facing in
    RectAreaLightUniformsLib.init();
    const a = new THREE.RectAreaLight(L.sky.color || '#dfe8f6', L.sky.i ?? 4, W.w, W.h); a.position.set(W.x, W.sill + W.h / 2, R.back + .05); a.lookAt(W.x, W.sill + W.h / 2, R.back + 5);
    scene.add(a); report.lights.push('sky');
  }
  for (const p of L.practicals || []) {                                     // practical lamps: warm, short reach, glowing shades
    const I = SET.items[p.item]; if (!I) continue;
    const pl = new THREE.PointLight(p.color || '#ffcf8f', p.i ?? 2, p.dist ?? 3, 2); pl.position.set(...(p.offset || [0, .34, 0]));
    if (p.shadow) { pl.castShadow = true; pl.shadow.mapSize.set(512, 512); pl.shadow.bias = -.002; pl.shadow.radius = 4; }
    I.group.add(pl); report.lights.push('practical:' + p.item);
    I.group.traverse(o => { if (o.isMesh && o.geometry.type === 'CylinderGeometry' && o.geometry.parameters.openEnded) {   // the shade glows from inside
      o.material = o.material.clone(); o.material.emissive = new THREE.Color(p.color || '#ffcf8f'); o.material.emissiveIntensity = p.shadeGlow ?? .35; } });
  }
  if (L.key) { const sp = new THREE.SpotLight(L.key.color || '#fff1e0', L.key.i ?? 6, L.key.dist ?? 9, deg(L.key.angle ?? 40), L.key.penumbra ?? 1, 2);
    sp.position.set(...L.key.pos); sp.target.position.set(...L.key.target); scene.add(sp, sp.target); report.lights.push('key'); }
  if (L.fill) { fill.color.set(L.fill.color); fill.intensity = L.fill.i; fill.position.set(...L.fill.pos); }
  hemi.intensity = L.hemi ?? .15;
  return report;
}
