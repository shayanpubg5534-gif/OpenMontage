// Character lab (M3): a deterministic performance compiler for MPFB characters (53-bone game_engine rig).
//
// A shot script (JSON) says what each character does and when: body clips (mocap, retargeted at build time),
// where the character is, what it looks at, expressions, gestures, finger poses, and what its hands hold or reach for.
// compile() turns that into per-frame data at 30 fps (bone rotations, pelvis position, morph weights, eye rotations,
// prop transforms). apply(t) then poses everything for any time t, with no state carried between calls, so frames can
// be rendered out of order, in parallel, or seeked by HyperFrames.
//
// Layers, in order, per frame:
//   1. clips: sequenced segments with eased crossfades; root motion placed in the world ('continue' from the previous
//      segment, or an explicit position and heading); walk transitions phase-matched; per-clip floor calibration
//   2. feet: plant detection on the composed motion, then two-bone leg IK that pins each planted foot (no sliding),
//      with a floor clamp
//   3. body: gesture restraint (arms eased toward the rest stance), breathing, additive gestures (nods)
//   4. attention: look-at spread over spine, neck and head with a spring (the head lags), eyes leading with saccades,
//      upper lids following the gaze; automatic and scripted blinks; eased, overlapping expression transitions
//   5. hands: finger poses (from the rig's own grip clip), arm IK onto prop sockets (reach, hold, hand-off, point),
//      props following the hand that owns them
import * as THREE from 'three';

export const FPS = 30;
const V = () => new THREE.Vector3(), Q = () => new THREE.Quaternion();
const UP = new THREE.Vector3(0, 1, 0);
const ease = x => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const ease5 = x => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * x * (x * (x * 6 - 15) + 10));
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
const FINGERS = ['thumb', 'index', 'middle', 'ring', 'pinky'];
const ARM = s => [`clavicle_${s}`, `upperarm_${s}`, `lowerarm_${s}`, `hand_${s}`];
const _qa = new THREE.Quaternion(), _qb = new THREE.Quaternion();

// ── a character's skeleton and clips ─────────────────────────────────────────────────────────────────────────────
export class Actor {
  constructor(gltf, id, cfg = {}) {
    this.id = id; this.cfg = cfg; this.root = gltf.scene; this.gltf = gltf;
    this.bones = {}; this.list = [];
    gltf.scene.traverse(o => { if (o.isBone) { this.bones[o.name] = o; this.list.push(o); } });
    this.meshes = []; gltf.scene.traverse(o => { if (o.isMesh) this.meshes.push(o); });
    this.morphMeshes = this.meshes.filter(m => m.morphTargetDictionary);
    this.morphNames = [...new Set(this.morphMeshes.flatMap(m => Object.keys(m.morphTargetDictionary)))];
    this.restQ = this.list.map(b => b.quaternion.clone()); this.restP = this.list.map(b => b.position.clone());
    this.idx = Object.fromEntries(this.list.map((b, i) => [b.name, i]));
    gltf.scene.updateMatrixWorld(true);
    const W = n => this.bones[n].getWorldPosition(V());
    this.rest = { ball: (W('ball_l').y + W('ball_r').y) / 2, ankle: (W('foot_l').y + W('foot_r').y) / 2, pelvis: W('pelvis'), head: W('head') };
    this.rootBone = this.bones.Root;
    // local frame helpers measured in the rest pose
    const wq = n => this.bones[n].getWorldQuaternion(Q());
    this.fwdIn = n => new THREE.Vector3(0, 0, 1).applyQuaternion(wq(n).invert());          // world +Z (forward) in bone space
    this.pelvisFwd = this.fwdIn('pelvis'); this.headFwd = this.fwdIn('head');
    if (this.bones.eye_l && this.bones.eye_r) this.eyeFwd = { l: this.fwdIn('eye_l').normalize(), r: this.fwdIn('eye_r').normalize() };   // converted characters
    // hands: palm normal, finger direction and thumb side in hand space; palm centre offset
    this.hand = {};
    for (const s of ['l', 'r']) {
      const h = this.bones[`hand_${s}`], hp = W(`hand_${s}`), mid = W(`middle_01_${s}`), th = W(`thumb_01_${s}`), pk = W(`pinky_01_${s}`);
      const fd = mid.clone().sub(hp).normalize(), side = th.clone().sub(pk).normalize();
      let pn = new THREE.Vector3().crossVectors(fd, side).normalize();
      if ((s === 'l' && pn.x > 0) || (s === 'r' && pn.x < 0)) pn.negate();                  // rest palms face the thighs
      const inv = wq(`hand_${s}`).invert();
      const palm = hp.clone().lerp(mid, .55).add(pn.clone().multiplyScalar(.012));
      this.hand[s] = { fd: fd.applyQuaternion(inv), pn: pn.applyQuaternion(inv), palm: h.worldToLocal(palm.clone()),
                       len: W(`upperarm_${s}`).distanceTo(W(`lowerarm_${s}`)) + W(`lowerarm_${s}`).distanceTo(hp) };
    }
    // eyes for the gaze: midpoint between the two eye pivots is set by the stage (see bindEyes)
    this.clips = {};
    for (const a of gltf.animations) this.clips[a.name] = this.prepClip(a);
    this.curl = this.fingerAxes();
  }
  // clips are baked at 30 fps, cleaned and lightly smoothed (M4): CMU data has marker pops (single-frame jumps of
  // the whole upper body) and jitter. Outlier frames (second difference far above the track's median) are replaced
  // by interpolation, then a 5-tap binomial filter removes jitter. A 'calm' copy (wide Gaussian) keeps only the
  // slow posture changes; restraint blends toward it instead of a fixed stance, so restrained arms stay alive.
  prepClip(a) {
    const n = Math.max(2, Math.round(a.duration * FPS) + 1), tracks = [];
    for (const t of a.tracks) {
      const [bn, prop] = t.name.split('.'); const i = this.idx[bn]; if (i === undefined) continue;
      const it = t.createInterpolant(), k = t.getValueSize(), raw = new Float32Array(n * k);
      for (let f = 0; f < n; f++) raw.set(it.evaluate(Math.min(a.duration, f / FPS)), f * k);
      if (prop === 'quaternion') for (let f = 1; f < n; f++) { let d = 0; for (let c = 0; c < 4; c++) d += raw[f * 4 + c] * raw[(f - 1) * 4 + c]; if (d < 0) for (let c = 0; c < 4; c++) raw[f * 4 + c] *= -1; }
      const acc = new Float32Array(n);
      for (let f = 1; f < n - 1; f++) { let e = 0; for (let c = 0; c < k; c++) e += (raw[(f + 1) * k + c] + raw[(f - 1) * k + c] - 2 * raw[f * k + c]) ** 2; acc[f] = Math.sqrt(e); }
      const med = [...acc].sort((x, y) => x - y)[n >> 1] + 1e-6, bad = new Uint8Array(n);
      let repaired = 0;
      for (let f = 1; f < n - 1; f++) if (acc[f] > Math.max(10 * med, prop === 'quaternion' ? .02 : .01)) { bad[f - 1] = bad[f] = bad[f + 1] = 1; repaired++; }
      bad[0] = bad[n - 1] = 0;
      for (let f = 1; f < n - 1; f++) if (bad[f]) { let g = f; while (g < n - 1 && bad[g]) g++; const a0 = f - 1, b0 = g;
        for (let h = f; h < g; h++) { const u = (h - a0) / (b0 - a0); for (let c = 0; c < k; c++) raw[h * k + c] = raw[a0 * k + c] * (1 - u) + raw[b0 * k + c] * u; } f = g; }
      const filt = (src, wts) => { const r = wts.length >> 1, out = new Float32Array(n * k);
        for (let f = 0; f < n; f++) for (let c = 0; c < k; c++) { let sum = 0, ws = 0;
          for (let j = -r; j <= r; j++) { const g = Math.min(n - 1, Math.max(0, f + j)); sum += src[g * k + c] * wts[j + r]; ws += wts[j + r]; } out[f * k + c] = sum / ws; }
        if (prop === 'quaternion') for (let f = 0; f < n; f++) { const l = Math.hypot(out[f * 4], out[f * 4 + 1], out[f * 4 + 2], out[f * 4 + 3]) || 1; for (let c = 0; c < 4; c++) out[f * 4 + c] /= l; }
        return out; };
      const smooth = filt(raw, [1, 4, 6, 4, 1]);
      const G = []; for (let j = -24; j <= 24; j++) G.push(Math.exp(-(j * j) / (2 * 10 * 10)));
      tracks.push({ i, prop, k, data: smooth, calm: filt(raw, G), repaired });
    }
    return { name: a.name, duration: a.duration, tracks, n };
  }
  // write a clip's pose at time t into arrays q (4×N) and p (3×N); bones without tracks keep the rest pose
  sample(clip, t, q, p, calm = false) {
    t = clamp(t, 0, clip.duration);
    for (let i = 0; i < this.list.length; i++) { this.restQ[i].toArray(q, i * 4); this.restP[i].toArray(p, i * 3); }
    const fl = Math.min(clip.n - 1, t * FPS), f0 = Math.floor(fl), f1 = Math.min(clip.n - 1, f0 + 1), u = fl - f0;
    for (const tr of clip.tracks) {
      const d = calm ? tr.calm : tr.data, k = tr.k;
      if (tr.prop === 'quaternion') { const a4 = _qa.fromArray(d, f0 * 4), b4 = _qb.fromArray(d, f1 * 4); a4.slerp(b4, u); a4.toArray(q, tr.i * 4); }
      else if (tr.prop === 'position') { const o = tr.i * 3; for (let c = 0; c < 3; c++) p[o + c] = d[f0 * k + c] * (1 - u) + d[f1 * k + c] * u; }
    }
  }
  setPose(q, p) {
    for (let i = 0; i < this.list.length; i++) { const b = this.list[i]; b.quaternion.fromArray(q, i * 4); b.position.fromArray(p, i * 3); }
    this.rootBone.updateMatrixWorld(true);
  }
  wpos(n, out = V()) { return this.bones[n].getWorldPosition(out); }
  wquat(n, out = Q()) { return this.bones[n].getWorldQuaternion(out); }
  // rotate a bone by a world-space rotation r (about its own head)
  rotWorld(n, r) {
    const b = this.bones[n], pq = b.parent.getWorldQuaternion(Q());
    b.quaternion.premultiply(pq.clone().invert().multiply(r).multiply(pq)); b.updateMatrixWorld(true);
  }
  setWorldQuat(n, wq) { const b = this.bones[n], pq = b.parent.getWorldQuaternion(Q()); b.quaternion.copy(pq.invert().multiply(wq)); b.updateMatrixWorld(true); }
  // finger curl axes from the rig's own 'grip' clip (bone space); angles in that clip are the full grip
  fingerAxes() {
    const g = this.clips.grip, out = {}; if (!g) return out;
    const q = new Float32Array(this.list.length * 4), p = new Float32Array(this.list.length * 3);
    this.sample(g, g.duration, q, p);
    for (const s of ['l', 'r']) for (const f of FINGERS) for (const j of [1, 2, 3]) {
      const n = `${f}_0${j}_${s}`, i = this.idx[n]; if (i === undefined) continue;
      const d = this.restQ[i].clone().invert().multiply(new THREE.Quaternion().fromArray(q, i * 4));
      const ang = 2 * Math.acos(clamp(d.w, -1, 1)), sn = Math.sqrt(Math.max(1e-9, 1 - d.w * d.w));
      out[n] = { axis: new THREE.Vector3(d.x / sn, d.y / sn, d.z / sn).normalize(), full: ang };
    }
    return out;
  }
}

// finger poses as fractions of the full grip curl per joint [j1, j2, j3]; thumb separately
export const HANDS = {
  // the MPFB bind pose splays the fingers: a negative spread draws them together (measured in a hand close-up test)
  rest:    { thumb: [.12, .08, .08], index: [.2, .24, .16], middle: [.25, .28, .18], ring: [.3, .33, .22], pinky: [.36, .38, .26], spread: -.11 },
  relaxed: { thumb: [.15, .1, .1], index: [.25, .3, .2], middle: [.3, .34, .22], ring: [.36, .4, .26], pinky: [.42, .44, .3], spread: -.12 },
  open:    { thumb: [.05, 0, 0], index: [.05, .05, .05], middle: [.06, .06, .05], ring: [.08, .08, .06], pinky: [.1, .1, .08], spread: -.03 },
  present: { thumb: [.1, .05, .05], index: [.1, .12, .08], middle: [.12, .14, .1], ring: [.16, .17, .12], pinky: [.2, .2, .14], spread: -.08 },
  grip:    { thumb: [.8, .8, .7], index: [.95, 1, .9], middle: [1, 1, .9], ring: [1, 1, .9], pinky: [1, 1, .9] },
  pinch:   { thumb: [.55, .45, .35], index: [.55, .6, .45], middle: [.6, .65, .5], ring: [.65, .7, .55], pinky: [.7, .7, .55], spread: -.1 },
  point:   { thumb: [.55, .5, .45], index: [0, 0, 0], middle: [1, 1, .9], ring: [1, 1, .9], pinky: [1, 1, .9] },
};

// ── two-bone IK (keeps the current bend plane unless a pole is given) ────────────────────────────────────────────
function twoBone(A, a, b, c, target, pole, endQuat) {
  const pa = A.wpos(a), pb = A.wpos(b), pc = A.wpos(c);
  const la = pa.distanceTo(pb), lb = pb.distanceTo(pc);
  const toT = target.clone().sub(pa); let d = toT.length();
  d = clamp(d, Math.abs(la - lb) + 1e-4, la + lb - 1e-4);
  const dir = toT.normalize();
  let bend = pole ? pole.clone().sub(pa) : pb.clone().sub(pa);
  bend.sub(dir.clone().multiplyScalar(bend.dot(dir)));
  if (bend.lengthSq() < 1e-10) bend = pb.clone().sub(pa).sub(dir.clone().multiplyScalar(pb.clone().sub(pa).dot(dir)));
  if (bend.lengthSq() < 1e-10) bend = dir.clone().cross(UP);
  bend.normalize();
  const cosA = clamp((la * la + d * d - lb * lb) / (2 * la * d), -1, 1), sinA = Math.sqrt(1 - cosA * cosA);
  const K = pa.clone().add(dir.clone().multiplyScalar(cosA * la)).add(bend.multiplyScalar(sinA * la));
  A.rotWorld(a, Q().setFromUnitVectors(pb.clone().sub(pa).normalize(), K.clone().sub(pa).normalize()));
  const pb2 = A.wpos(b), pc2 = A.wpos(c);
  A.rotWorld(b, Q().setFromUnitVectors(pc2.clone().sub(pb2).normalize(), target.clone().add(dir.clone().multiplyScalar(0)).sub(pb2).normalize()));
  if (endQuat) A.setWorldQuat(c, endQuat);
}

// world orientation for a hand given desired finger direction and palm normal (world)
function handQuat(A, s, fd, pn) {
  const h = A.hand[s];
  const m1 = new THREE.Matrix4().makeBasis(h.fd, h.pn, h.fd.clone().cross(h.pn).normalize());
  const f = fd.clone().normalize(), n = pn.clone().sub(f.clone().multiplyScalar(pn.dot(f))).normalize();
  const m2 = new THREE.Matrix4().makeBasis(f, n, f.clone().cross(n).normalize());
  return Q().setFromRotationMatrix(m2.multiply(m1.transpose()));
}

// ── the compiler ─────────────────────────────────────────────────────────────────────────────────────────────────
export function compile(script, actors, props = {}, opts = {}) {
  const t0 = performance.now();
  const dur = script.duration, nF = Math.round(dur * FPS) + 1;
  const out = { duration: dur, frames: nF, actors: {}, props: {}, qa: { plants: {}, timing: {} } };
  const N = a => a.list.length;
  for (const A of actors) {
    const S = script.actors[A.id] || {};
    const segs = (S.body || []).map(s => ({ ...s, clip: A.clips[s.clip] })).filter(s => s.clip);
    if (!segs.length) segs.push({ clip: A.clips.stand, at: 0, blend: 0 });
    // per-clip floor calibration and heading helper
    const q = new Float32Array(N(A) * 4), p = new Float32Array(N(A) * 3);
    const calib = {};
    const pelvisWorld = (clip, t) => { A.sample(clip, t, q, p); A.setPose(q, p); return { pos: A.wpos('pelvis'), quat: A.wquat('pelvis') }; };
    const heading = (clip, t) => { let x = 0, z = 0;
      for (let k = -4; k <= 4; k++) { const f = A.pelvisFwd.clone().applyQuaternion(pelvisWorld(clip, clamp(t + k * .12, 0, clip.duration)).quat); x += f.x; z += f.z; }
      return Math.atan2(x, z); };
    for (const s of segs) {
      const c = s.clip; if (calib[c.name] !== undefined) continue;
      const hs = [];
      for (let t = 0; t <= c.duration; t += 1 / 15) { A.sample(c, t, q, p); A.setPose(q, p); hs.push(Math.min(A.wpos('ball_l').y, A.wpos('ball_r').y)); }
      hs.sort((x, y) => x - y); calib[c.name] = A.rest.ball - hs[Math.floor(hs.length * .1)];
    }
    // segment timing, phase match and placement (sequential: each 'continue' needs the previous composition)
    segs.sort((x, y) => x.at - y.at);
    const clipTime = (s, t) => {
      const from = s.from || 0, to = s.to ?? s.clip.duration, L = to - from; let u = Math.max(0, t - s.at - (s.hold || 0)) * (s.speed || 1) + (s.offset || 0);
      if (s.loop === 'pingpong' && L > 0) { const cyc = Math.floor(u / L), r = u - cyc * L, e = (1 - Math.cos(Math.PI * r / L)) / 2; return from + (cyc % 2 ? (1 - e) : e) * L; }
      return clamp(from + u, 0, s.clip.duration);
    };
    const segPose = (s, t, qq, pp, calm = false) => {   // pose of one segment at timeline t, pelvis placed in the world
      const ct = clipTime(s, t); A.sample(s.clip, ct, qq, pp, calm || !!s.calm); A.setPose(qq, pp);   // calm: a held segment plays the slow version (no visible reversals)
      const pw = A.wpos('pelvis'), qw = A.wquat('pelvis');
      const R = Q().setFromAxisAngle(UP, s._yaw);
      const pos = pw.clone().sub(s._p0).applyQuaternion(R).add(s._anchor); pos.y = pw.y + calib[s.clip.name];
      const quat = R.clone().multiply(qw);
      // back to the pelvis's local space (parent = Root)
      const rq = A.rootBone.getWorldQuaternion(Q()), rp = A.rootBone.getWorldPosition(V()), rs = A.rootBone.getWorldScale(V());
      const lp = pos.clone().sub(rp).applyQuaternion(rq.clone().invert()).divide(rs);
      const lq = rq.invert().multiply(quat);
      const i = A.idx.pelvis; lq.toArray(qq, i * 4); lp.toArray(pp, i * 3);
    };
    const qa = new Float32Array(N(A) * 4), pa = new Float32Array(N(A) * 3), qb = new Float32Array(N(A) * 4), pb = new Float32Array(N(A) * 3);
    const compose = (t, qq, pp, upto = segs.length, calm = false) => {   // blended base pose at time t using segments [0, upto)
      let k = -1; for (let j = 0; j < upto; j++) if (segs[j].at <= t + 1e-9) k = j;
      if (k < 0) k = 0;
      const s = segs[k], w = k > 0 && s.blend ? ease((t - s.at) / s.blend) : 1;
      segPose(s, t, qq, pp, calm);
      if (w < 1) {
        segPose(segs[k - 1], t, qb, pb, calm);
        for (let i = 0; i < N(A); i++) { const a4 = Q().fromArray(qb, i * 4).slerp(Q().fromArray(qq, i * 4), w); a4.toArray(qq, i * 4); }
        for (let i = 0; i < pp.length; i++) pp[i] = pb[i] + (pp[i] - pb[i]) * w;
      }
      return k;
    };
    const placeAt = (s, ct) => { A.sample(s.clip, ct, q, p); A.setPose(q, p); return A.wpos('pelvis'); };
    if (!segs[0].place) segs[0].place = { pos: [0, 0], yaw: 0 };
    for (let k = 0; k < segs.length; k++) {
      const s = segs[k];
      if (s.match && k > 0) {                 // phase match: start the new clip where its legs best match the old pose
        compose(s.at, qa, pa, k); const prev = Array.from(qa);
        let best = 1e9, bo = 0; const legs = ['thigh_l', 'calf_l', 'thigh_r', 'calf_r', 'foot_l', 'foot_r'].map(n => A.idx[n]);
        for (let o = 0; o <= (s.matchWindow || 1.2); o += 1 / FPS) {
          A.sample(s.clip, (s.from || 0) + o, q, p);
          let e = 0; for (const i of legs) { const a4 = Q().fromArray(prev, i * 4), b4 = Q().fromArray(q, i * 4); e += 1 - Math.abs(a4.dot(b4)); }
          if (e < best) { best = e; bo = o; }
        }
        s.offset = bo; out.qa.timing[`${A.id}.${k}.phase_offset_s`] = +bo.toFixed(3);
      }
      if (s.place === 'next') continue;                                  // resolved below, once the next segment is placed
      const ct0 = s.pin !== undefined ? s.pin : clipTime(s, s.at);      // pin: this clip time lands on place.pos
      const h0 = heading(s.clip, ct0); s._p0 = placeAt(s, ct0); s._p0.y = 0;
      if (s.place && s.place.pos) {
        s._anchor = new THREE.Vector3(s.place.pos[0], 0, s.place.pos[1]); s._yaw = (s.place.yaw * Math.PI / 180) - h0;
      } else {                                // continue from the composition of the previous segments at s.at
        compose(s.at, qa, pa, k); A.setPose(qa, pa);
        const pw = A.wpos('pelvis'); s._anchor = new THREE.Vector3(pw.x, 0, pw.z);
        const fw = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis'));
        const hPrev = (s.keepHeading !== false && k > 0) ? segs[k - 1]._yaw + heading(segs[k - 1].clip, clipTime(segs[k - 1], s.at)) : Math.atan2(fw.x, fw.z);
        s._yaw = hPrev - h0;
      }
    }
    for (let k = segs.length - 2; k >= 0; k--) {
      const s = segs[k], nx = segs[k + 1]; if (s.place !== 'next') continue;
      const nct = clipTime(nx, nx.at); A.sample(nx.clip, nct, q, p); A.setPose(q, p);
      const np = A.wpos('pelvis').sub(nx._p0).applyQuaternion(Q().setFromAxisAngle(UP, nx._yaw)).add(nx._anchor);
      const nh = nx._yaw + heading(nx.clip, nct), ct = clipTime(s, nx.at);
      s._p0 = placeAt(s, ct); s._p0.y = 0; s._anchor = new THREE.Vector3(np.x, 0, np.z); s._yaw = nh - heading(s.clip, ct);
    }
    // pass A: base poses and foot trajectories
    const base = [], feet = { l: [], r: [] };
    for (let f = 0; f < nF; f++) {
      const t = f / FPS, qq = new Float32Array(N(A) * 4), pp = new Float32Array(N(A) * 3);
      const qc = new Float32Array(N(A) * 4), pc = new Float32Array(N(A) * 3); compose(t, qc, pc, segs.length, true);
      compose(t, qq, pp); A.setPose(qq, pp); base.push([qq, pp, qc]);
      for (const s of ['l', 'r']) feet[s].push({ ankle: A.wpos(`foot_${s}`), ball: A.wpos(`ball_${s}`), q: A.wquat(`foot_${s}`) });
    }
    // plant detection → locked ankle targets with eased entry and exit
    const lock = { l: new Array(nF).fill(null), r: new Array(nF).fill(null) };
    const plants = {};
    for (const s of ['l', 'r']) {
      const F = feet[s], on = F.map((x, f) => {
        const g = F[Math.min(nF - 1, f + 1)], h = F[Math.max(0, f - 1)];
        const sp = g.ball.clone().sub(h.ball).setY(0).length() * FPS / 2, spa = g.ankle.clone().sub(h.ankle).setY(0).length() * FPS / 2;
        return Math.min(sp, spa) < .35 && F[f].ball.y < A.rest.ball + .045; });
      const runs = []; let st = -1;
      for (let f = 0; f <= nF; f++) { if (f < nF && on[f]) { if (st < 0) st = f; } else if (st >= 0) { if (f - st >= 3) runs.push([st, f - 1]); st = -1; } }
      plants[s] = runs;
      for (const [a, b] of runs) {
        const m = Math.min(b, a + 2), tgt = F[m].ankle.clone();
        for (let f = a; f <= b; f++) {
          // leash: a pinned foot may differ from the animation by at most 3.5 cm; beyond that the pin follows
          // smoothly (mocap subjects shuffle their feet), so a plant never ends with a snap
          const dx = F[f].ankle.x - tgt.x, dz = F[f].ankle.z - tgt.z, dl = Math.hypot(dx, dz);
          { const k = .12 * ease((dl - .012) / .03); tgt.x += dx * k; tgt.z += dz * k; }   // soft leash: no speed jump at a threshold
          const w = Math.min(ease((f - a + 1) / 6), ease((b - f + 1) / 6));          // 0.2 s ramps: no snap into or out of a plant
          const T = F[f].ankle.clone(); T.x += (tgt.x - T.x) * w; T.z += (tgt.z - T.z) * w;
          lock[s][f] = T;
        }
      }
    }
    out.qa.plants[A.id] = plants;
    { let sum = 0, n = 0, worst = 0;                      // sliding of the raw (un-pinned) retargeted motion, same plants
      for (const s of ['l', 'r']) for (const [a, b] of plants[s]) for (let f = a + 3; f <= b - 2; f++) {
        const d = Math.hypot(feet[s][f].ankle.x - feet[s][f - 1].ankle.x, feet[s][f].ankle.z - feet[s][f - 1].ankle.z) * 1000; sum += d; n++; worst = Math.max(worst, d); }
      out.qa.rawSlide = out.qa.rawSlide || {}; out.qa.rawSlide[A.id] = { mean_mm_per_frame: +(sum / Math.max(1, n)).toFixed(2), worst_mm: +worst.toFixed(1) }; }
    // pass B: IK, body layers, attention, hands; snapshot
    const frames = new Array(nF);
    const st = { yaw: 0, pitch: 0, vy: 0, vp: 0 };
    const look = S.look || [], face = S.face || [], gest = S.gestures || [], handsT = S.hands || [], reach = S.reach || [];
    const restrain = S.restrain || [];
    const r = rng(S.seed || 7);
    const blinks = []; for (let t = .6 + r() * 1.5; t < dur; t += 2.4 + r() * 2.8) blinks.push(t);
    for (const b of (S.blinks || [])) blinks.push(b);
    // extra blink when the look target changes a lot (natural with large gaze shifts)
    for (const L of look) if (L.blink) blinks.push(L.t + .03);
    blinks.sort((x, y) => x - y);
    const morphNames = A.morphNames;
    const standClip = A.clips.stand; const qs = new Float32Array(N(A) * 4), ps = new Float32Array(N(A) * 3);
    if (standClip) A.sample(standClip, 0, qs, ps);
    out.actors[A.id] = { frames, morphNames, eyes: [] , blinks };
    out.qa.timing[`${A.id}.passA_ms`] = Math.round(performance.now() - t0);
    A._compile = { base, lock, feet, frames, st, look, face, gest, handsT, reach, restrain, blinks, qs, morphNames, S };
  }
  // pass B interleaved across actors per frame, so hand-offs and eye contact see each other's current pose
  const order = actors;
  const propState = {};
  for (const [id, P] of Object.entries(props)) propState[id] = { obj: P.obj, attach: P.attach || null, keys: P.keys || [] };
  for (let f = 0; f < nF; f++) {
    const t = f / FPS;
    for (const A of order) bodyLayers(A, f, t);
    scriptedProps(propState, t);                 // props on a scripted path: hands reach for their sockets
    for (const A of order) attention(A, f, t, actors, props);   // look-at turns the chest: before the arms, so hands stay on target
    for (const A of order) armLayers(A, f, t, propState);
    attachedProps(propState, actors);            // carried props ride on the hand
    for (const A of order) snapshot(A, f, t);
    for (const [id, s] of Object.entries(propState)) if (s.keys.length || s.attach) (out.props[id] = out.props[id] || []).push(s.obj.matrixWorld.toArray());
  }
  out.qa.timing.compile_ms = Math.round(performance.now() - t0);
  return out;
}

function bodyLayers(A, f, t) {
  const C = A._compile, [qq, pp] = C.base[f];
  A.setPose(qq, pp);
  pinFeet(A, f);
  // restraint (documentary register): arms eased toward the clip's own slow posture (calm), with a little of the
  // rest stance, so gestures are damped but the arms keep living with the body
  let rs = 0; for (const k of C.restrain.filter(k => !k.side)) if (t >= k.t) rs = k.t + (k.dur || .5) > t ? (rs + (k.v - rs) * ease((t - k.t) / (k.dur || .5))) : k.v;
  if (C.S.restrainAll !== undefined) rs = Math.max(rs, C.S.restrainAll);
  const side = {};
  for (const k of C.restrain) if (k.side && t >= k.t) side[k.side] = (side[k.side] ?? 0) + (k.v - (side[k.side] ?? 0)) * ease((t - k.t) / (k.dur || .5));
  const qc = C.base[f][2];
  for (const s of ['l', 'r']) { const v = Math.max(rs, side[s] || 0); if (v > 0) for (const n of ARM(s)) { const i = A.idx[n];
    const tgt = Q().fromArray(qc, i * 4).slerp(Q().fromArray(C.qs, i * 4), .3); A.bones[n].quaternion.slerp(tgt, v); } }
  // wrists: CMU hand data is poor (wrists bent back up to ~70°); ease free hands toward the rest stance, then let
  // them trail the forearm slightly (follow-through)
  const wr = C.S.wristRelax ?? .8;
  for (const s of ['l', 'r']) { const i = A.idx[`hand_${s}`], hb = A.bones[`hand_${s}`];
    if (wr > 0) hb.quaternion.slerp(Q().fromArray(C.qs, i * 4), wr);
    const key = 'wrist_' + s; if (C[key] && f > 0) hb.quaternion.copy(C[key].clone().slerp(hb.quaternion, .45)); C[key] = hb.quaternion.clone(); }
  A.rootBone.updateMatrixWorld(true);
  // posture (M4): a torso leaning back beyond `maxBack` degrees is brought forward over the three spine bones, so
  // seated characters sit up at a meeting instead of reclining like the mocap subject on a stool
  const up = C.S.upright ?? 0;
  if (up > 0) {
    const pel = A.wpos('pelvis'), nk = A.wpos('neck_01'), tor = nk.clone().sub(pel).normalize();
    const fw = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis')).setY(0).normalize();
    const back = Math.atan2(-tor.dot(fw), tor.y), maxB = (C.S.maxBack ?? 5) * Math.PI / 180;
    if (back > maxB) {
      const side = fw.clone().cross(UP).normalize(), corr = (back - maxB) * up;
      const want = tor.clone().applyAxisAngle(side, -corr);
      const q = Q().setFromUnitVectors(tor, want.normalize());
      for (const [n, k] of [['spine_01', .4], ['spine_02', .35], ['spine_03', .25]]) A.rotWorld(n, Q().slerp(q, k));
    }
  }
  bodyRest(A, f, t);
}

function pinFeet(A, f) {
  const C = A._compile;
  for (const s of ['l', 'r']) {
    const anim = C.feet[s][f]; let T = C.lock[s][f] ? C.lock[s][f].clone() : null;
    const probe = T || anim.ankle.clone(), ballY = probe.y + (anim.ball.y - anim.ankle.y);
    const lift = Math.max(0, A.rest.ankle - .004 - probe.y, A.rest.ball - .002 - ballY);   // floor: neither heel nor ball below it
    if (!T && lift <= 0) continue;
    T = probe; T.y += lift;
    const knee = A.wpos(`calf_${s}`), fwd = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis'));
    twoBone(A, `thigh_${s}`, `calf_${s}`, `foot_${s}`, T, knee.clone().add(fwd.multiplyScalar(.3)), anim.q);
  }
}

function bodyRest(A, f, t) {
  const C = A._compile;
  // breathing: chest and shoulders, slower and smaller while walking
  const per = A.cfg.breath || 4.0, ph = A.cfg.breathPhase || 0, b = Math.sin(2 * Math.PI * t / per + ph);
  const right = new THREE.Vector3(1, 0, 0).applyQuaternion(A.wquat('pelvis')).setY(0).normalize();
  const amp = (C.S.breath ?? 1) * Math.PI / 180;
  A.rotWorld('spine_02', Q().setFromAxisAngle(right, -.5 * amp * b));
  A.rotWorld('spine_03', Q().setFromAxisAngle(right, -.7 * amp * b));
  for (const s of ['l', 'r']) { const sg = s === 'l' ? 1 : -1, fw = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis')).setY(0).normalize();
    A.rotWorld(`clavicle_${s}`, Q().setFromAxisAngle(fw, sg * .6 * amp * Math.max(0, b))); }
  // gestures: nods (pitch dips on neck and head), small shrugs
  for (const g of C.gest) {
    const u = (t - g.t) / (g.dur || .9); if (u < 0 || u > 1) continue;
    if (g.type === 'nod') { const a = (g.amp || 7) * Math.PI / 180 * Math.sin(Math.PI * u) * (g.count === 2 ? Math.abs(Math.sin(2 * Math.PI * u)) * 1.2 : 1);
      const rgt = new THREE.Vector3(1, 0, 0).applyQuaternion(A.wquat('head')).setY(0).normalize();
      A.rotWorld('neck_01', Q().setFromAxisAngle(rgt, .4 * a)); A.rotWorld('head', Q().setFromAxisAngle(rgt, .6 * a)); }
    if (g.type === 'shrug') { const a = (g.amp || 5) * Math.PI / 180 * Math.sin(Math.PI * u);
      for (const s of ['l', 'r']) { const fw = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis')).setY(0).normalize();
        A.rotWorld(`clavicle_${s}`, Q().setFromAxisAngle(fw, (s === 'l' ? 1 : -1) * a)); } }
  }
}

// hands: reach / hold / point / present onto targets (a prop socket, a point to aim at, or a world position)
function armLayers(A, f, t, propState) {
  const C = A._compile;
  for (const R of C.reach) {
    const w = Math.min(ease5((t - R.t0) / (R.in || .6)), 1 - ease5((t - R.t1) / (R.out || .6)));
    if (w <= 0) continue;
    const s = R.side; let P, fd, pn;
    if (R.prop) { const o = propState[R.prop].obj; o.updateMatrixWorld(true);
      const sk = R.socket; P = new THREE.Vector3(...sk.pos).applyMatrix4(o.matrixWorld);
      const rq = o.getWorldQuaternion(Q()); fd = new THREE.Vector3(...sk.fd).applyQuaternion(rq); pn = new THREE.Vector3(...sk.pn).applyQuaternion(rq); }
    else if (R.point) { const sh = A.wpos(`upperarm_${s}`), dirv = new THREE.Vector3(...R.point).sub(sh).normalize();
      P = sh.clone().add(dirv.clone().multiplyScalar(A.hand[s].len * (R.extend || .8)));
      fd = dirv; pn = new THREE.Vector3(0, -1, 0); }
    else if (R.local) { const pq = A.wquat('pelvis'), fw = A.pelvisFwd.clone().applyQuaternion(pq).setY(0).normalize(), rt = fw.clone().cross(UP).normalize(), pw = A.wpos('pelvis');
      const L = (v, o) => rt.clone().multiplyScalar(v[0]).add(new THREE.Vector3(0, v[1], 0)).add(fw.clone().multiplyScalar(v[2])).add(o ? new THREE.Vector3(pw.x, 0, pw.z) : V());
      P = L(R.local, true); fd = L(R.fd || [0, 0, 1]); pn = L(R.pn || [0, 1, 0]); }
    else if (R.pos) { P = new THREE.Vector3(...R.pos); fd = new THREE.Vector3(...(R.fd || [0, -.3, 1])); pn = new THREE.Vector3(...(R.pn || [0, -1, 0])); }
    if (!P) continue;
    const hq = handQuat(A, s, fd, pn);
    // reach assist: a target beyond ~97% of the arm's reach bends the spine toward it first (picking up from a desk)
    let leaned = 0, ldir = null;
    for (let it = 0; it < 3 && (R.lean ?? !!R.prop); it++) {          // lean only for objects (or when asked)
      const sh = A.wpos(`upperarm_${s}`), to = P.clone().sub(sh), ex = to.length() - .97 * A.hand[s].len - .05;
      if (ex <= .005) break;
      const h = to.clone().setY(0); if (h.lengthSq() < 1e-6) break;
      ldir = h.normalize(); const axis = UP.clone().cross(ldir).normalize(), ang = Math.min(.75, ex / .38) * w; leaned += ang;
      for (const [n, k] of [['spine_01', .4], ['spine_02', .35], ['spine_03', .25]]) A.rotWorld(n, Q().setFromAxisAngle(axis, ang * k));
    }
    if (leaned > 0 && ldir && A.wpos('pelvis').y > .7) {          // standing only: a seated pelvis stays on its chair                 // counterbalance: hips go back as the torso leans; planted feet re-pinned
      const pb = A.bones.pelvis, wp = A.wpos('pelvis').sub(ldir.clone().multiplyScalar(.12 * leaned)).add(new THREE.Vector3(0, -.03 * leaned, 0));
      pb.position.copy(pb.parent.worldToLocal(wp)); A.rootBone.updateMatrixWorld(true); pinFeet(A, f);
    }
    const target = P.clone().sub(A.hand[s].palm.clone().applyQuaternion(hq));   // hand bone so the palm centre lands on P
    const chain = [`upperarm_${s}`, `lowerarm_${s}`, `hand_${s}`], pre = chain.map(n => A.bones[n].quaternion.clone());
    const pq = A.wquat('pelvis'), fwd = A.pelvisFwd.clone().applyQuaternion(pq).setY(0).normalize(), side = fwd.clone().cross(UP).normalize();
    // elbow pole: the current elbow, nudged down and out, so the bend plane is kept (no elbow flips at reach onset)
    const pole = A.wpos(`lowerarm_${s}`).add(side.multiplyScalar(s === 'l' ? -.08 : .08)).add(new THREE.Vector3(0, -.12, 0)).add(fwd.multiplyScalar(-.05));
    // solve fully, then blend the joint rotations by the reach weight (no elbow jump at a tiny weight)
    twoBone(A, `upperarm_${s}`, `lowerarm_${s}`, `hand_${s}`, target, pole, hq);
    if (w < 1) { chain.forEach((n, k) => A.bones[n].quaternion.copy(pre[k].clone().slerp(A.bones[n].quaternion, w))); A.rootBone.updateMatrixWorld(true); }
  }
}

function scriptedProps(propState, t) {
  for (const ps of Object.values(propState)) {
    if (!ps.keys.length) continue;
    const o = ps.obj; let a = ps.keys[0], b = a;
    for (const k of ps.keys) { if (k.t <= t) a = k; if (k.t > t) { b = k; break; } } if (b.t <= a.t) b = a;
    const u = b === a ? 0 : ease5((t - a.t) / (b.t - a.t));
    o.position.fromArray(a.pos).lerp(new THREE.Vector3(...b.pos), u);
    const qa = Q().setFromEuler(new THREE.Euler(...a.rot.map(x => x * Math.PI / 180))), qb = Q().setFromEuler(new THREE.Euler(...b.rot.map(x => x * Math.PI / 180)));
    o.quaternion.copy(qa.slerp(qb, u)); o.updateMatrixWorld(true);
  }
}

function attachedProps(propState, actors) {
  for (const ps of Object.values(propState)) {
    if (!ps.attach) continue;
    const [id, s] = ps.attach.owner.split(':'); const A = actors.find(a => a.id === id); const h = A.bones[`hand_${s}`];
    if (ps.attach.mode === 'hang') {
      const palm = h.localToWorld(A.hand[s].palm.clone()), fw = A.pelvisFwd.clone().applyQuaternion(A.wquat('pelvis')).setY(0).normalize();
      const sw = ps.swing || (ps.swing = { a: 0, v: 0, prev: null, pv: null }), dt = 1 / FPS;
      if (sw.prev) { const vel = palm.clone().sub(sw.prev).dot(fw) / dt, acc = sw.pv === null ? 0 : (vel - sw.pv) / dt;
        const om = 2 * Math.PI / .9; sw.v += (-om * om * sw.a - 2 * .25 * om * sw.v - acc / .25) * dt; sw.a = clamp(sw.a + sw.v * dt, -.35, .35); sw.pv = vel; }
      sw.prev = palm.clone();
      const o = ps.obj; o.position.copy(palm).add(new THREE.Vector3(0, ps.attach.drop ?? 0, 0));
      const yaw = Math.atan2(fw.x, fw.z) + (ps.attach.yaw || 0) * Math.PI / 180, side = fw.clone().cross(UP).normalize();
      o.quaternion.setFromAxisAngle(UP, yaw + Math.PI / 2).premultiply(Q().setFromAxisAngle(side, sw.a)); o.updateMatrixWorld(true);
      continue;
    }
    if (!ps.local) {                     // a handle in the palm: the prop hangs along -fingers, its thickness along the palm normal
      const H = A.hand[s], up = H.fd.clone().negate(), th = H.pn.clone(), wd = up.clone().cross(th).normalize();
      const m = new THREE.Matrix4().makeBasis(wd, up, th); m.setPosition(H.palm.clone().add(H.fd.clone().multiplyScalar(ps.attach.drop ?? .01)));
      ps.local = m;
    }
    const o = ps.obj; o.matrix.copy(h.matrixWorld).multiply(ps.local); o.matrix.decompose(o.position, o.quaternion, o.scale); o.updateMatrixWorld(true);
  }
}

// look-at (head, neck, chest), eyes, lids, blinks, expressions, fingers
function attention(A, f, t, actors, props) {
  const C = A._compile, st = C.st;
  // current look target and weight
  let L = null, w = 0;
  for (const k of C.look) if (k.t <= t) L = k;
  if (L) w = L.w ?? 1;
  const prevL = C.look.filter(k => k.t <= t).slice(-2)[0];
  const eyeMid = eyeWorld(A);
  let target = L ? resolveTarget(L.target, actors, props, A) : null;
  // M5 gaze model. Eye contact is not a lock: during a long look at a person, brief seeded glances away (down and to
  // the side) every 4–6 s; the eyes lead and the head follows only part of the way.
  const sd = (A.cfg.seed ?? C.S.seed ?? 7) * 1.37;
  if (target && L && typeof L.target === 'string' && L.target.startsWith('char:') && L.avert !== false) {
    const since = t - L.t, per = 4.6 + 1.2 * Math.sin(sd), ph = (since - 2.2 + per) % per;
    if (since > 2.2 && ph < .75) {
      const hfw = A.headFwd.clone().applyQuaternion(A.wquat('head')).setY(0).normalize(), rgt = hfw.clone().cross(UP).normalize();
      const k2 = Math.sin(Math.PI * ph / .75);
      target = target.clone().add(rgt.multiplyScalar((Math.sin(sd * 3 + Math.floor((since - 2.2) / per)) > 0 ? .28 : -.28) * k2)).add(new THREE.Vector3(0, -.22 * k2, 0));
    }
  }
  // head spring toward the target (yaw/pitch offsets relative to the animated head); the head turns part of the way
  let ty = 0, tp = 0;
  const hf = A.headFwd.clone().applyQuaternion(A.wquat('head'));
  if (target && w > 0) {
    const d = target.clone().sub(eyeMid).normalize();
    const yawT = Math.atan2(d.x, d.z), yawH = Math.atan2(hf.x, hf.z);
    let dy = yawT - yawH; while (dy > Math.PI) dy -= 2 * Math.PI; while (dy < -Math.PI) dy += 2 * Math.PI;
    const pitchT = Math.asin(clamp(d.y, -1, 1)), pitchH = Math.asin(clamp(hf.y, -1, 1));
    const share = L.head ?? .72;
    ty = clamp(dy, -1.3, 1.3) * w * share; tp = clamp(pitchT - pitchH, -.6, .5) * w * share;
  }
  // a living head: slow micro-motion (about a degree), different per actor
  ty += .014 * Math.sin(2 * Math.PI * t / 4.1 + sd) + .008 * Math.sin(2 * Math.PI * t / 2.3 + sd * 2);
  tp += .011 * Math.sin(2 * Math.PI * t / 3.3 + sd * 3);
  const k = 1 / FPS, om = 2 * Math.PI / (A.cfg.headLag || .55);    // critically damped spring
  const ay = om * om * (ty - st.yaw) - 2 * om * st.vy, ap = om * om * (tp - st.pitch) - 2 * om * st.vp;
  st.vy += ay * k; st.vp += ap * k; st.yaw += st.vy * k; st.pitch += st.vp * k;
  if (f === 0) { st.yaw = ty; st.pitch = tp; st.vy = st.vp = 0; }
  // spread over chest, neck and head (the neck carries more of the pitch; the head's own pitch is capped)
  for (const [n, sy, sp] of [['spine_03', .18, .12], ['neck_01', .37, .46], ['head', .45, .42]]) {
    A.rotWorld(n, Q().setFromAxisAngle(UP, st.yaw * sy));
    const rgt = new THREE.Vector3(1, 0, 0).applyQuaternion(A.wquat('head')).setY(0).normalize();
    A.rotWorld(n, Q().setFromAxisAngle(rgt, -clamp(st.pitch * sp, -.26, .26)));
  }
  // head stabilisation: people keep the head near upright when the torso tilts (mocap stools, posture correction)
  { const headUp = A.bones.head.localToWorld(new THREE.Vector3(0, 1, 0)).sub(A.wpos('head')).normalize();
    const ang = headUp.angleTo(UP);
    if (ang > .03) { const lim = Math.min(1, .17 / ang) * .4; A.rotWorld('head', Q().slerp(Q().setFromUnitVectors(headUp, UP), lim)); } }
  // head roll (M5 review): seated mocap leaves the head rolled toward a shoulder; people keep the eyes level while
  // talking. Level the roll around the face axis only (pitch and yaw stay with the gaze). cfg.levelRoll 0..1 (default .8)
  { const k = A.cfg.levelRoll ?? .8;
    if (k > 0) { const f = A.headFwd.clone().applyQuaternion(A.wquat('head')).normalize();
      const u = A.bones.head.localToWorld(new THREE.Vector3(0, 1, 0)).sub(A.wpos('head'));
      const up = UP.clone().sub(f.clone().multiplyScalar(UP.dot(f))), uu = u.sub(f.clone().multiplyScalar(u.dot(f)));
      if (up.length() > .2 && uu.length() > .2) { up.normalize(); uu.normalize();
        const ang = Math.atan2(uu.clone().cross(up).dot(f), clamp(uu.dot(up), -1, 1));
        const a = clamp(ang * k, -.3, .3); if (Math.abs(a) > .002) A.rotWorld('head', Q().setFromAxisAngle(f, a)); } } }
  // eyes: aim directly at the target (saccade over two frames), within ±30°; otherwise straight ahead with micro drift
  const eyeTgt = target ? target.clone() : A.wpos('head').add(A.headFwd.clone().applyQuaternion(A.wquat('head')).multiplyScalar(3));
  C.eyeTarget = eyeTgt;
  // blinks
  let blink = 0;
  for (const b of C.blinks) { const u = t - b; if (u < -.1 || u > .3) continue;
    blink = Math.max(blink, u < 0 ? 0 : u < .075 ? ease(u / .075) : u < .115 ? 1 : 1 - ease((u - .115) / .14)); }
  // expressions: eased keys with overlapping timing (brows lead, mouth follows)
  const E = {}; const lag = n => /eyebrows/.test(n) ? -.05 : /mouth/.test(n) ? .08 : 0;
  for (const n of C.morphNames) {
    let v = 0, prev = 0;
    for (const key of C.face) { const tt = t - lag(n); if (key.t > tt) break; const u = ease5((tt - key.t) / (key.dur || .5)); prev = v; v = prev + ((key.e[n] || 0) - prev) * u; }
    E[n] = v;
  }
  // lip sync (M5): only for lines this character actually speaks. speech: [{t, data: visemes.json}] adds mouth-unit weights
  for (const sp of (C.S.speech || [])) { const d = sp.data; if (!d) continue;
    const fi = Math.round((t - sp.t) * d.fps); if (fi < 0 || fi >= d.frames.length) continue;
    const fr = d.frames[fi], k = sp.gain ?? 1;
    for (const [u, w] of Object.entries(fr)) if (C.morphNames.includes(u)) E[u] = Math.min(1, (E[u] || 0) + w * k);
    E['mouth-corner-puller'] = (E['mouth-corner-puller'] || 0) * (1 - .5 * Math.min(1, (fr['mouth-pursing'] || 0) * 2)); }
  // lids follow the gaze pitch; blink closes completely
  const hd = eyeTgt.clone().sub(eyeMid).normalize(), hfa = A.headFwd.clone().applyQuaternion(A.wquat('head'));
  const down = clamp(Math.asin(clamp(hfa.y, -1, 1)) - Math.asin(clamp(hd.y, -1, 1)), -.5, .5);
  for (const s of ['left', 'right']) {
    const c = `eye-${s}-closure`, o = `eye-${s}-opened-up`;
    E[c] = Math.max(E[c] || 0, clamp(down * .9, 0, .45));
    E[c] = (E[c] || 0) + (1 - (E[c] || 0)) * blink;
    E[o] = (E[o] || 0) * (1 - blink) + clamp(-down * .6, 0, .3) * (1 - blink);
  }
  C.morph = E;
  // fingers
  const hp = { l: 'relaxed', r: 'relaxed' }, hfrom = { l: 'relaxed', r: 'relaxed' }, hu = { l: 1, r: 1 };
  for (const key of C.handsT) { if (key.t > t) continue; for (const s of (key.side === 'both' ? ['l', 'r'] : [key.side])) { hfrom[s] = hp[s]; hp[s] = key.pose; hu[s] = ease((t - key.t) / (key.dur || .3)); } }
  for (const s of ['l', 'r']) {
    const P0 = HANDS[hfrom[s]], P1 = HANDS[hp[s]];
    for (const fn of FINGERS) for (const j of [1, 2, 3]) {
      const n = `${fn}_0${j}_${s}`, cv = A.curl[n]; if (!cv) continue;
      const fr = P0[fn][j - 1] + (P1[fn][j - 1] - P0[fn][j - 1]) * hu[s];
      const b = A.bones[n]; b.quaternion.copy(A.restQ[A.idx[n]]).multiply(Q().setFromAxisAngle(cv.axis, cv.full * fr));
      if (j === 1 && fn !== 'thumb') { const sp = ((P0.spread || 0) + ((P1.spread || 0) - (P0.spread || 0)) * hu[s]) * ({ index: -1, middle: 0, ring: 1, pinky: 2 }[fn]);
        if (sp) b.quaternion.multiply(Q().setFromAxisAngle(cv.axis.clone().cross(new THREE.Vector3(0, 1, 0)).normalize(), sp)); }
    }
  }
  A.rootBone.updateMatrixWorld(true);
}

export function eyeWorld(A) {
  if (A.eyeLocal) return A.bones.head.localToWorld(A.eyeLocal.clone());
  return A.wpos('head').add(A.headFwd.clone().applyQuaternion(A.wquat('head')).multiplyScalar(.09));
}

export function resolveTarget(tg, actors, props, self) {
  if (!tg) return null;
  if (Array.isArray(tg)) return new THREE.Vector3(...tg);
  if (tg.startsWith('char:')) { const B = actors.find(a => a.id === tg.slice(5)); return eyeWorld(B); }
  if (tg.startsWith('prop:')) { const P = props[tg.slice(5)]; return P.obj.getWorldPosition(V()); }
  if (tg.startsWith('hand:')) { const [id, s] = tg.slice(5).split(':'); const B = actors.find(a => a.id === id); return B.wpos(`hand_${s}`); }
  return null;
}

function snapshot(A, f, t) {
  const C = A._compile, n = A.list.length, q = new Float32Array(n * 4), p = new Float32Array(3);
  for (let i = 0; i < n; i++) A.list[i].quaternion.toArray(q, i * 4);
  A.bones.pelvis.position.toArray(p, 0);
  C.frames[f] = { q, p, m: C.morphNames.map(k => C.morph[k] || 0), eye: C.eyeTarget.toArray() };
}

// ── playback: pose actors and props for time t (interpolating between compiled frames) ─────────────────────────
export function apply(compiled, actors, props, t) {
  const fl = clamp(t * FPS, 0, compiled.frames - 1), f0 = Math.floor(fl), f1 = Math.min(compiled.frames - 1, f0 + 1), u = fl - f0;
  const qa = Q(), qb = Q();
  for (const A of actors) {
    const D = compiled.actors[A.id]; if (!D) continue;
    const a = D.frames[f0], b = D.frames[f1];
    for (let i = 0; i < A.list.length; i++) { qa.fromArray(a.q, i * 4); qb.fromArray(b.q, i * 4); A.list[i].quaternion.copy(qa.slerp(qb, u)); A.list[i].position.copy(A.restP[i]); }
    A.bones.pelvis.position.set(a.p[0] + (b.p[0] - a.p[0]) * u, a.p[1] + (b.p[1] - a.p[1]) * u, a.p[2] + (b.p[2] - a.p[2]) * u);
    A.root.updateMatrixWorld(true);
    const m = D.morphNames.map((_, k) => a.m[k] + (b.m[k] - a.m[k]) * u);
    for (const mesh of A.morphMeshes) for (const [k, j] of Object.entries(mesh.morphTargetDictionary)) { const ix = D.morphNames.indexOf(k); mesh.morphTargetInfluences[j] = ix >= 0 ? m[ix] : 0; }
    A.eyeTarget = new THREE.Vector3(...a.eye).lerp(new THREE.Vector3(...b.eye), u);
  }
  for (const [id, P] of Object.entries(props)) { const M = compiled.props[id]; if (!M) continue;
    const ma = new THREE.Matrix4().fromArray(M[f0]), mb = new THREE.Matrix4().fromArray(M[f1]);
    const pa = V(), pb = V(), ra = Q(), rb = Q(), s = V(); ma.decompose(pa, ra, s); mb.decompose(pb, rb, s);
    P.obj.position.copy(pa.lerp(pb, u)); P.obj.quaternion.copy(ra.slerp(rb, u)); P.obj.updateMatrixWorld(true); }
}

// eyes: rotation of each eyeball (bind space) toward the actor's eye target, clamped
export function aimEyes(A, maxDeg = 28) {
  if (A.bones.eye_l && A.bones.eye_r && !A.meshes.some(m => m.userData.eyeU)) { aimEyeBones(A, maxDeg); return; }
  for (const m of A.meshes) {
    const U = m.userData.eyeU; if (!U) continue;
    const head = A.bones.head, sk = m.skeleton, hi = sk.bones.indexOf(head);
    const M = new THREE.Matrix4().multiplyMatrices(m.bindMatrixInverse, head.matrixWorld).multiply(sk.boneInverses[hi]).multiply(m.bindMatrix);
    const WM = new THREE.Matrix4().multiplyMatrices(m.matrixWorld, M), inv = WM.clone().invert();
    const rot = new THREE.Matrix3().setFromMatrix4(inv);
    const fwd = new THREE.Vector3(0, 0, 1).applyMatrix3(new THREE.Matrix3().setFromMatrix4(m.matrixWorld.clone().invert())).normalize();
    for (const [piv, mat] of [[U.pivL.value, U.eyeL.value], [U.pivR.value, U.eyeR.value]]) {
      const c = piv.clone().applyMatrix4(WM);
      const d = A.eyeTarget.clone().sub(c).applyMatrix3(rot).normalize();
      let q = Q().setFromUnitVectors(fwd, d); const ang = 2 * Math.acos(clamp(q.w, -1, 1)), max = maxDeg * Math.PI / 180;
      if (ang > max) q = Q().slerp(q, max / ang);
      mat.setFromMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(q));
    }
  }
}

// converted characters (charlab/convert): the eyeballs are part of the head mesh and turn with eye bones. Each eye
// bone is rotated from its rest orientation so its rest forward (character +Z) points at the gaze target, within ±maxDeg.
function aimEyeBones(A, maxDeg) {
  if (!A.eyeTarget) return;
  for (const s of ['l', 'r']) {
    const b = A.bones[`eye_${s}`], i = A.idx[`eye_${s}`];
    b.quaternion.copy(A.restQ[i]); b.updateMatrixWorld(true);
    const c = b.getWorldPosition(new THREE.Vector3());
    const d = A.eyeTarget.clone().sub(c).normalize().applyQuaternion(b.getWorldQuaternion(new THREE.Quaternion()).invert());
    let q = new THREE.Quaternion().setFromUnitVectors(A.eyeFwd[s], d);
    const ang = 2 * Math.acos(Math.min(1, Math.abs(q.w))), max = maxDeg * Math.PI / 180;
    if (ang > max) q = new THREE.Quaternion().slerp(q, max / ang);
    b.quaternion.multiply(q); b.updateMatrixWorld(true);
  }
}
