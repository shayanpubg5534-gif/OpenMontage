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
  msaa2: { msaa: 2, shadow: 1024, inkPass: true },
  lean: { msaa: 0, shadow: 1024, inkPass: false },
};

export async function loadShot({ demo, OUT, canvas = null }) {
  const T0 = performance.now();
  const stage = await createStage({ env: demo.env, canvas, plate: demo.plate || null, look: demo.look || 'cel' });
  // a full 3D set (M4.1): build it, take its light rig, and resolve anchor references in the script
  let SET = null;
  if (demo.set) { const spec = await (await fetch(demo.set)).json(); stage.setPropTint((spec.lights || {}).propShadow, (spec.lights || {}).propLight); SET = buildEnvironment(stage, spec); stage.setLights(spec.lights || {});
    if (stage.look === 'cinematic' && spec.cinematic) SET.cinematic = await (await import('./cinematic.js')).applyCinematic(stage, { ...SET, spec }, spec.cinematic);   // P3, opt-in
    for (const a of Object.values(demo.actors)) for (const s of a.body || []) if (s.place && typeof s.place === "object" && s.place.anchor) {
      const an = SET.anchors[s.place.anchor]; if (!an) throw new Error('unknown anchor ' + s.place.anchor); s.place = { pos: an.pos, yaw: an.yaw }; } }
  const loader = new GLTFLoader(), actors = [];
  for (const a of Object.values(demo.actors)) for (const sp of a.speech || []) if (sp.src && !sp.data) sp.data = await (await fetch(sp.src)).json();   // lip-sync tracks (M5)
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
  if (SET) for (const [name, I] of Object.entries(SET.items)) if (I.spec.fitTo) {
    const A = actors.find(a => a.id === I.spec.fitTo); if (!A) continue;
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
  const gl = stage.renderer.getContext();
  const frame = (t, quality = {}) => {
    const s = performance.now();
    EL.apply(compiled, actors, props, t);
    for (const A of actors) EL.aimEyes(A);
    const ck = camAt(t);
    stage.render({ blur: demo.blur || 0, ...ck, haze: demo.haze ?? null, ...quality });
    gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4));   // wait for the GPU (SwiftShader defers work)
    return performance.now() - s;
  };
  return { stage, demo, actors, props, compiled, SET, cam, camAt, frame, EL, THREE, loadMs, compileMs };
}
