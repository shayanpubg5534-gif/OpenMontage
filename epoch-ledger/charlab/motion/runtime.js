// Character lab (M4): the shot runtime shared by the lab viewer (viewer/motion.html) and HyperFrames compositions.
// loadShot() builds the stage, the set (with anchors), the characters and props, compiles the performance, fits chairs
// to their sitters and returns frame(t, quality): a pure function of t (any order, any process), plus the objects the
// lab QA needs.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { createStage } from './stage.js';
import * as EL from './elmotion.js';
import { buildEnvironment } from './env.js';

export const QUALITY = {
  standard: { msaa: 4, shadow: 2048, inkPass: true },
  balanced: { msaa: 0, shadow: 1024, inkPass: true, fxaa: true },   // M4.2: MSAA ×2 saved nothing inside HyperFrames
  // P4 (experimental, cinematic look): measured profiles. All keep 1080p, every frame rendered, real animation.
  //   cin_fast     — drafts: environment cache, PCF shadows, no AO/DOF
  //   cin_balanced — environment cache (anchors re-rendered every 3 cm of camera travel), AO + DOF + haze, FXAA
  //   cin_cinematic— full re-render every frame, 4× MSAA, 2048 shadows (depth from the main pass)
  cin_fast: { msaa: 0, shadow: 1024, inkPass: true, fxaa: true, mainDepth: true, envCache: { tol: .05 }, shadowType: 'pcf', ao: 0, dof: 0 },
  cin_balanced: { msaa: 0, shadow: 1024, inkPass: true, fxaa: true, mainDepth: true, envCache: { tol: .03 }, shadowType: 'pcf' },
  cin_balanced_t5: { msaa: 0, shadow: 1024, inkPass: true, fxaa: true, mainDepth: true, envCache: { tol: .05 }, shadowType: 'pcf' },   // tolerance study
  cin_cinematic: { msaa: 4, shadow: 2048, inkPass: true, mainDepth: true },
  cin_reference_pcf: { msaa: 0, shadow: 1024, inkPass: true, fxaa: true, mainDepth: true, shadowType: 'pcf' },   // Balanced without the cache: ground truth for it
  msaa2: { msaa: 2, shadow: 1024, inkPass: true },
  lean: { msaa: 0, shadow: 1024, inkPass: false },
};

export async function loadShot({ demo, OUT, canvas = null }) {
  const T0 = performance.now();
  const stage = await createStage({ env: demo.env, canvas, plate: demo.plate || null, look: demo.look || 'cel' });
  if (demo.exposure) stage.renderer.toneMappingExposure = demo.exposure;   // P3 cinematic look (tone-mapped in the post pass)
  if (demo.dofScale) stage.post.uniforms.dofScale.value = demo.dofScale;   // P4: a real lens blur for cinematic demos (P3 dof values were sub-pixel)
  // a full 3D set (M4.1): build it, take its light rig, and resolve anchor references in the script
  let SET = null;
  if (demo.set) { const spec = await (await fetch(demo.set)).json(); stage.setPropTint((spec.lights || {}).propShadow, (spec.lights || {}).propLight); SET = buildEnvironment(stage, spec); stage.setLights(spec.lights || {});
    if (stage.look === 'cinematic' && spec.cinematic) {   // P3, opt-in; demo.cinematicVariant (P4) overlays a named variant of the set's cinematic block
      let cin = spec.cinematic; const v = demo.cinematicVariant && (spec.cinematic_variants || {})[demo.cinematicVariant];
      if (demo.cinematicVariant && !v) throw new Error('unknown cinematic variant ' + demo.cinematicVariant);
      if (v) { cin = { ...cin, ...v, materials: { ...cin.materials, ...(v.materials || {}) }, lights: { ...cin.lights, ...(v.lights || {}) } };
        for (const [k, m] of Object.entries(v.materialPatch || {})) cin.materials[k] = { ...cin.materials[k], ...m }; }
      SET.cinematic = await (await import('./cinematic.js')).applyCinematic(stage, { ...SET, spec }, cin); }
    for (const a of Object.values(demo.actors)) for (const s of a.body || []) if (s.place && typeof s.place === "object" && s.place.anchor) {
      const an = SET.anchors[s.place.anchor]; if (!an) throw new Error('unknown anchor ' + s.place.anchor); s.place = { pos: an.pos, yaw: an.yaw }; } }
  const loader = new GLTFLoader(), actors = [];
  for (const a of Object.values(demo.actors)) for (const sp of a.speech || []) if (sp.src && !sp.data) sp.data = await (await fetch(sp.src)).json();   // lip-sync tracks (M5)
  if (Object.values(demo.actors).some(a => a.perform)) { const { expandPerformance } = await import('./perflib.js'); for (const a of Object.values(demo.actors)) expandPerformance(a, { duration: demo.duration }); }   // P3 performance presets (opt-in)
  for (const [id, a] of Object.entries(demo.actors)) {
    const g = await loader.loadAsync(`${OUT}/${id}.glb`);
    await stage.addCharacter(g, id, a.pbr ? null : `${OUT}/${id}_tex`, { look: a.charlook, lookOpts: a.charlookOpts });   // pbr: a converted character keeps its baked materials
    const A = new EL.Actor(g, id, a.cfg || {});
    g.scene.updateMatrixWorld(true);
    const em = A.meshes.find(m => m.userData.eyeU);
    if (!em && A.bones.eye_l && A.bones.eye_r) {   // converted characters: eyes are bones inside the head mesh
      const mid = A.bones.eye_l.getWorldPosition(new THREE.Vector3()).add(A.bones.eye_r.getWorldPosition(new THREE.Vector3())).multiplyScalar(.5);
      mid.add(new THREE.Vector3(0, 0, .012)); A.eyeLocal = A.bones.head.worldToLocal(mid); }
    if (em) { const U = em.userData.eyeU; const mid = U.pivL.value.clone().add(U.pivR.value).multiplyScalar(.5).applyMatrix4(em.matrixWorld);
      mid.add(new THREE.Vector3(0, 0, .011)); A.eyeLocal = A.bones.head.worldToLocal(mid); }
    actors.push(A);
  }
  // props
  const props = {};
  const C = c => new THREE.Color(c);
  function makeProp(spec) {
    const g = new THREE.Group();
    if (spec.type === 'desk') { const [w, h, d] = spec.size || [1.0, .74, .62];
      const top = stage.box(w, .04, d, spec.color || '#8a5d3b'); top.position.y = h - .02; g.add(top);
      for (const sx of [-1, 1]) { const side = stage.box(.05, h - .04, d * .92, spec.leg || '#6e4a30'); side.position.set(sx * (w / 2 - .04), (h - .04) / 2, 0); g.add(side); }
      const back = stage.box(w - .1, h * .55, .03, spec.leg || '#6e4a30'); back.position.set(0, h * .55, -d / 2 + .06); g.add(back); }
    if (spec.type === 'chair') { const sh = spec.seat || .46, col = spec.color || '#2f3540';
      const seat = stage.box(.46, .06, .44, col); seat.position.y = sh - .03; g.add(seat);
      const back = stage.box(.46, .5, .05, col); back.position.set(0, sh + .25, -.2); g.add(back);
      for (const [x, z] of [[-.2, -.19], [.2, -.19], [-.2, .19], [.2, .19]]) { const l = stage.box(.035, sh - .06, .035, '#1d2129'); l.position.set(x, (sh - .06) / 2, z); g.add(l); } }
    if (spec.type === 'folder') { const f = stage.box(.31, .012, .235, spec.color || '#c8a04a'); g.add(f);
      const paper = stage.box(.29, .004, .215, '#f3efe4'); paper.position.y = .008; g.add(paper); }
    if (spec.type === 'bag') { const body = stage.box(.36, .26, .09, spec.color || '#5a3a28'); body.position.y = -.17; g.add(body);
      const h1 = stage.box(.018, .05, .018, '#3d281c'), h2 = h1.clone(); h1.position.set(-.07, -.03, 0); h2.position.set(.07, -.03, 0); g.add(h1, h2);
      const hb = stage.box(.16, .016, .018, '#3d281c'); hb.position.y = -.005; g.add(hb); }
    if (spec.pos) g.position.set(...spec.pos); if (spec.rot) g.rotation.set(...spec.rot.map(x => x * Math.PI / 180));
    stage.addProp(g); g.updateMatrixWorld(true);
    return { obj: g, keys: spec.keys || [], attach: spec.attach || null, spec };
  }
  for (const [id, spec] of Object.entries(demo.props || {})) {
    if (spec.type === 'glb') {                       // a static model (e.g. a base mesh under evaluation), shaded like the set
      const g = await loader.loadAsync(spec.url); const root = g.scene;
      root.traverse(o => { if (o.isMesh) o.material = stage.propMaterial(/eye/i.test(o.name) ? (spec.eye || '#f1ece6') : (spec.color || '#d9a68a')); });
      if (spec.pos) root.position.set(...spec.pos); if (spec.rot) root.rotation.set(...spec.rot.map(x => x * Math.PI / 180)); if (spec.scale) root.scale.setScalar(spec.scale);
      stage.addProp(root); root.updateMatrixWorld(true); props[id] = { obj: root, keys: [], attach: null, spec }; continue;
    }
    props[id] = makeProp(spec);
  }
  const loadMs = performance.now() - T0;
  // compile
  const t1 = performance.now();
  const compiled = EL.compile(demo, actors, props);
  const compileMs = performance.now() - t1;
  // set chairs fitted to their sitters (seat top meets the sitter's lowest pelvis height)
  if (SET) for (const [name, I] of Object.entries(SET.items)) if ((demo.fit || {})[name] || I.spec.fitTo) {   // demo.fit: {chair: actor} overrides the set (P3)
    const A = actors.find(a => a.id === ((demo.fit || {})[name] || I.spec.fitTo)); if (!A) continue;
    const D = compiled.actors[A.id]; let lo = 9;
    for (let f = 0; f < D.frames.length; f += 2) { EL.apply(compiled, [A], {}, f / EL.FPS); lo = Math.min(lo, A.wpos('pelvis').y); }
    I.seatTop = SET.fitSeat(name, lo, I.spec.seatDrop ?? .09); }
  // a chair whose seat should meet the sitter's pelvis
  for (const [id, P] of Object.entries(props)) if (P.spec.type === 'chair' && P.spec.seatFor) {
    const A = actors.find(a => a.id === P.spec.seatFor), D = compiled.actors[A.id];
    let lo = 9, lf = 0; for (let f = 0; f < D.frames.length; f++) { EL.apply(compiled, [A], {}, f / EL.FPS); const y = A.wpos('pelvis').y; if (y < lo) { lo = y; lf = f; } }
    EL.apply(compiled, [A], {}, lf / EL.FPS); const pw = A.wpos('pelvis'), fw = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis')).setY(0).normalize();
    P.obj.position.set(pw.x - fw.x * (P.spec.seatBack ?? .07), 0, pw.z - fw.z * (P.spec.seatBack ?? .07)); P.obj.rotation.set(0, Math.atan2(fw.x, fw.z), 0);
    const seatTop = lo - (P.spec.seatDrop ?? .085); P.obj.scale.y = seatTop / (P.spec.seat || .46); P.obj.updateMatrixWorld(true); P.seatTop = seatTop;
  }
  // camera keys
  const cam = stage.cam;
  function camAt(t) {
    const K = demo.camera; let a = K[0], b = a; for (const k of K) { if (k.t <= t) a = k; if (k.t > t) { b = k; break; } } if (b.t <= a.t || b.cut) b = a;   // a cut: no interpolation across it
    const u = b === a ? 0 : (x => x * x * x * (x * (x * 6 - 15) + 10))((t - a.t) / (b.t - a.t));
    const res = v => Array.isArray(v) ? new THREE.Vector3(...v) : (() => { const A = actors.find(x => x.id === v.char); return (v.eyes ? EL.eyeWorld(A) : A.wpos('pelvis')).add(new THREE.Vector3(...(v.off || [0, 0, 0]))); })();
    const lk = res(a.look).lerp(res(b.look), u);
    cam.position.copy(res(a.pos).lerp(res(b.pos), u)); cam.lookAt(lk); cam.fov = a.fov + ((b.fov ?? a.fov) - a.fov) * u; cam.updateProjectionMatrix();
    return { dof: (a.dof ?? 0) + ((b.dof ?? a.dof ?? 0) - (a.dof ?? 0)) * u, focus: cam.position.distanceTo(lk), focusRange: a.focusRange ?? .35 };
  }
  // environment-cache anchors (P4): a pure function of time. Each camera segment (keys up to the next cut or key) is split
  // greedily into groups of frames whose camera stays within `tol` metres of travel and within 90% of the cache's overscan
  // margin in rotation (the look target can follow a character, so rotation is measured on the real camera path); a group's
  // anchor is its first frame. Groups depend only on the camera path, never on which frames were rendered before.
  const anchorCam = cam.clone(), groupCache = {};
  const camPose = f => { EL.apply(compiled, actors, props, f / EL.FPS); for (const A of actors) EL.aimEyes(A); camAt(f / EL.FPS); return { p: cam.position.clone(), q: cam.quaternion.clone(), fov: cam.fov }; };
  function groupsFor(i, tol) {
    const ck = i + ':' + tol; if (groupCache[ck]) return groupCache[ck];
    const K = demo.camera, nF = compiled.frames, f0 = Math.round(K[i].t * EL.FPS);
    let f1 = nF - 1; for (let j = i + 1; j < K.length; j++) if (K[j].t > K[i].t) { f1 = Math.min(nF - 1, Math.round(K[j].t * EL.FPS) - 1); break; }
    const out = []; let g = null;
    for (let f = f0; f <= f1; f++) { const c = camPose(f);
      const margin = Math.atan(Math.tan(c.fov * Math.PI / 360) * (1 + 160 / 1920)) * 180 / Math.PI - c.fov / 2;   // envcache pad 80 px each side
      if (!g || c.p.distanceTo(g.p) > tol || c.q.angleTo(g.q) * 180 / Math.PI > .9 * margin) { g = { f0: f, p: c.p, q: c.q }; out.push(g); }
      g.f1 = f; }
    return (groupCache[ck] = out);
  }
  function anchorFor(t, tol) {
    const K = demo.camera; let i = 0; for (let j = 0; j < K.length; j++) if (K[j].t <= t) i = j;
    const G = groupsFor(i, tol), f = Math.round(t * EL.FPS); let k = 0; while (k < G.length - 1 && G[k + 1].f0 <= f) k++;
    return { key: `s${i}:${k}`, t: G[k].f0 / EL.FPS };
  }
  stage.layers = SET ? { env: SET.root, chars: stage.cast.map(c => c.root) } : null;
  const gl = stage.renderer.getContext();
  const frame = (t, quality = {}) => {
    const s = performance.now();
    EL.apply(compiled, actors, props, t);
    for (const A of actors) EL.aimEyes(A);
    const ck = camAt(t);
    let q = quality;
    if (quality.envCache && SET) {                              // P4: the environment layer comes from a cached anchor
      const an = anchorFor(t, quality.envCache.tol ?? .03);
      EL.apply(compiled, actors, props, an.t); for (const A of actors) EL.aimEyes(A); camAt(an.t); anchorCam.copy(cam); anchorCam.updateMatrixWorld();
      EL.apply(compiled, actors, props, t); for (const A of actors) EL.aimEyes(A); camAt(t);                 // back to this frame (groupsFor may have walked the path)
      q = { ...quality, envCache: { cam: anchorCam, key: an.key } };
    }
    stage.render({ blur: demo.blur || 0, ...ck, haze: demo.haze ?? null, ...q });
    gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4));   // wait for the GPU (SwiftShader defers work)
    return performance.now() - s;
  };
  return { stage, demo, actors, props, compiled, SET, cam, camAt, frame, EL, THREE, loadMs, compileMs, anchorFor, anchorCam };
}
