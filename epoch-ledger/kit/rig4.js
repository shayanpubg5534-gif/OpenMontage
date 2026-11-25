// Epoch Ledger rig v4 — illustrated people acting in a story (opt-in head script; pairs with kit/rig4.py).
//
// A character is a small 3D skeleton seen through an orthographic camera, drawn every frame as continuous
// illustrated shapes. One model gives front, three-quarter, profile and rear views (continuous yaw). Limbs are one
// tapered outline that bends smoothly (no joint seams) and are solved with two-bone IK and a pole vector, so feet
// stay planted and hands land on what they touch. Faces sit on the head sphere and turn with it.
//
// Motion is authored as keyframes on named channels (R4.key / the action helpers) and evaluated as a pure
// function of time: a later key takes over from wherever the earlier motion was at that moment. Secondary motion
// (hair, tie, jacket hem) is a damped spring simulated over a fixed window ending at t, so it is deterministic too.
// GSAP is only the clock: R4.attach(tl) redraws every character after each timeline render. No randomness except
// seeded schedules (blinks). Original implementation.
//
// Space: character-local SVG px (the sprite's viewBox; ~980 px tall figure, feet on y = ground). x right, y down,
// z toward the viewer. Yaw 0 faces the viewer, 90 faces screen-right, 180 faces away, -90 faces screen-left.
const R4 = (() => {
  const INK = '#1b1410';
  const D2R = Math.PI / 180;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, p) => a + (b - a) * p;
  const EASE = {
    linear: p => p,
    in: p => p * p * p,
    out: p => 1 - Math.pow(1 - p, 3),
    inOut: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
    sine: p => -(Math.cos(Math.PI * p) - 1) / 2,
    back: p => { const c1 = 1.4, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  };
  // vectors
  const V = (x = 0, y = 0, z = 0) => [x, y, z];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const len = a => Math.hypot(a[0], a[1], a[2]);
  const norm = a => { const l = len(a) || 1; return mul(a, 1 / l); };
  const mix3 = (a, b, p) => [lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p)];
  const f2 = n => (Math.round(n * 10) / 10).toFixed(1);

  // ── channels: keyframed values, evaluated as a pure function of time ──────────────────────────────────────────
  class Channel {
    constructor(v0) { this.v0 = v0; this.keys = []; this.ready = false; }
    // move to `to` starting at time t over d seconds (d = 0: jump)
    key(t, to, d = 0, ease = 'inOut') { this.keys.push({ t, to, d, ease: EASE[ease] || EASE.inOut, n: this.keys.length }); this.ready = false; }
    _prep() {
      this.keys.sort((a, b) => a.t - b.t || a.n - b.n);
      let prev = null;
      for (const k of this.keys) { k.from = prev ? Channel._at(prev, k.t) : this.v0; prev = k; }
      this.ready = true;
    }
    static _at(k, t) { const p = k.d > 0 ? clamp((t - k.t) / k.d, 0, 1) : (t >= k.t ? 1 : 0); return Channel._mix(k.from, k.to, k.ease(p)); }
    static _mix(a, b, p) { return Array.isArray(a) ? a.map((x, i) => lerp(x, b[i], p)) : lerp(a, b, p); }
    at(t) {
      if (!this.ready) this._prep();
      const ks = this.keys; let lo = 0, hi = ks.length - 1, k = null;
      while (lo <= hi) { const m = (lo + hi) >> 1; if (ks[m].t <= t) { k = ks[m]; lo = m + 1; } else hi = m - 1; }
      return k ? Channel._at(k, t) : this.v0;
    }
  }

  const chars = {};
  // default body (px). Proportions of an adult at ~7.5 heads; the build multiplies them per character.
  const BODY = { head: 64, neck: 34, torso: 300, hipW: 44, shW: 76, chestD: 46, waistW: 62, waistD: 40, hipD: 44,
                 uarm: 160, farm: 148, hand: 74, thigh: 232, shin: 226, ankle: 30, foot: 92, armR: 25, legR: 36 };

  function channelSet(c) {
    const ch = (name, v) => (c.ch[name] = new Channel(v));
    const g = c.ground;
    ch('root', [c.x0, g - c.b.ankle - c.b.shin - c.b.thigh + 2.5, 0]);   // pelvis position (x, y, z)
    ch('yaw', c.yaw0); ch('twist', 0); ch('lean', 4); ch('side', 0);       // body orientation (deg)
    ch('headYaw', 0); ch('headPitch', 0); ch('headTilt', 0);
    ch('gaze', [0, 0]); ch('eyeOpen', 1); ch('brow', [0, 0]); ch('smile', .15); ch('mouth', 0); ch('jaw', 0);
    for (const s of ['L', 'R']) {
      const sg = s === 'R' ? 1 : -1;
      // hands: body-local rest target (side, y, fwd from the shoulder) blended with a world target
      ch('hand' + s, [sg * 18, c.b.uarm + c.b.farm - 34, 22]); ch('handW' + s, [0, 0, 0]); ch('handBlend' + s, 0);
      ch('handShape' + s, 0);       // 0 relaxed · 1 grip · 2 open · 3 point (blended where it makes sense)
      ch('handRoll' + s, 0);
      ch('foot' + s, [c.x0 - sg * 34 * Math.cos(c.yaw0 * D2R), g, sg * 34 * Math.sin(c.yaw0 * D2R)]);   // ankle-ground point, world
      ch('footYaw' + s, c.yaw0); ch('footPitch' + s, 0); ch('heelLift' + s, 0);
    }
  }

  // ── public: create a character inside an existing <g id=...> ──────────────────────────────────────────────────
  function create(id, spec) {
    const el = document.getElementById(id); if (!el) return null;
    const b = Object.assign({}, BODY);
    const s = spec.scale || 1;
    Object.keys(b).forEach(k => b[k] *= s * ((spec.build || {})[k] || 1));
    const c = { id, el, spec, b, ch: {}, x0: spec.x ?? 200, ground: spec.ground ?? 990, yaw0: spec.yaw ?? 30,
                blinkT: [], speak: [], props: [] };
    channelSet(c);
    // layer groups, rebuilt each frame
    el.innerHTML = `<defs id="${id}-defs"></defs><ellipse id="${id}-shadow" fill="#000" opacity=".22"/><g id="${id}-body"></g>`;
    c.defs = el.querySelector(`#${id}-defs`); c.body = el.querySelector(`#${id}-body`); c.shadow = el.querySelector(`#${id}-shadow`);
    chars[id] = c;
    if (spec.blinkSeed !== undefined) blinks(id, spec.t0 ?? 0, spec.t1 ?? 600, spec.blinkSeed);
    return c;
  }

  // ── pose: channels → 3D joints ────────────────────────────────────────────────────────────────────────────────
  function frameAxes(yaw) { const a = yaw * D2R; return { f: V(Math.sin(a), 0, Math.cos(a)), r: V(-Math.cos(a), 0, Math.sin(a)), u: V(0, -1, 0) }; }
  const local = (ax, s, y, fw) => add(add(mul(ax.r, s), mul(ax.f, fw)), V(0, y, 0));

  function ik(a, target, l1, l2, pole) {
    let d = sub(target, a), dl = len(d);
    const reach = l1 + l2 - .5; if (dl > reach) { d = mul(d, reach / dl); dl = reach; }
    dl = Math.max(dl, Math.abs(l1 - l2) + .5);
    const dir = norm(d), x = (l1 * l1 - l2 * l2 + dl * dl) / (2 * dl), h = Math.sqrt(Math.max(0, l1 * l1 - x * x));
    let pp = sub(pole, mul(dir, dot(pole, dir))); if (len(pp) < 1e-6) pp = V(0, 0, 1); pp = norm(pp);
    return { mid: add(add(a, mul(dir, x)), mul(pp, h)), end: add(a, d) };
  }

  function solve(c, t) {
    const C = n => c.ch[n].at(t), b = c.b;
    const yaw = C('yaw'), twist = C('twist'), lean = C('lean') * D2R, side = C('side') * D2R;
    const root = C('root');
    const hipAx = frameAxes(yaw), chestAx = frameAxes(yaw + twist);
    const J = { yaw, hipAx, chestAx, root };
    J.hipL = add(root, local(hipAx, -b.hipW, 0, 0)); J.hipR = add(root, local(hipAx, b.hipW, 0, 0));
    // spine: lumbar bends by half the lean, chest by the rest (a curve, not a hinge)
    const seg = (from, ax, l, ang, sd) => add(from, add(add(mul(ax.u, l * Math.cos(ang) * Math.cos(sd)), mul(ax.f, l * Math.sin(ang))), mul(ax.r, l * Math.sin(sd))));
    J.waist = seg(root, hipAx, b.torso * .42, lean * .45, side * .5);
    J.chest = seg(J.waist, chestAx, b.torso * .58, lean, side);
    J.neck = seg(J.chest, chestAx, b.neck * .5, lean * .6, side);
    const hy = yaw + twist + C('headYaw'), hp = C('headPitch') * D2R + lean * .3, ht = C('headTilt') * D2R + side;
    J.headAx = frameAxes(hy); J.headPitch = hp; J.headTilt = ht;
    J.head = seg(J.neck, J.headAx, b.neck * .5 + b.head * .95, hp, ht);
    const shY = b.torso * .06;
    J.shL = add(J.chest, add(local(chestAx, -b.shW, shY, 0), V(0, 0, 0))); J.shR = add(J.chest, local(chestAx, b.shW, shY, 0));
    // legs: two-bone IK from hip to the ankle above each planted foot point
    for (const s of ['L', 'R']) {
      const sg = s === 'R' ? 1 : -1, foot = C('foot' + s), fy = C('footYaw' + s), fax = frameAxes(fy);
      const lift = C('heelLift' + s), pitch = C('footPitch' + s) * D2R;
      const ankle = add(foot, V(0, -b.ankle - lift, 0));
      const pole = add(mul(J.hipAx.f, 1), mul(J.hipAx.r, sg * .12));
      const leg = ik(J['hip' + s], ankle, b.thigh, b.shin, add(pole, V(0, -.05, 0)));
      J['knee' + s] = leg.mid; J['ankle' + s] = leg.end;
      const toeDir = norm(add(mul(fax.f, Math.cos(pitch)), V(0, Math.sin(pitch), 0)));
      J['toe' + s] = add(leg.end, add(mul(toeDir, b.foot * .78), V(0, b.ankle * .9, 0)));
      J['heel' + s] = add(leg.end, add(mul(fax.f, -b.foot * .22), V(0, b.ankle * .95, 0)));
      J['footAx' + s] = fax;
      // arms: target = blend(body-local rest pose, world target)
      const sh = J['sh' + s], hl = C('hand' + s), hw = C('handW' + s), bl = C('handBlend' + s);
      const bodyT = add(sh, add(add(mul(chestAx.r, hl[0]), mul(V(0, 1, 0), hl[1])), mul(chestAx.f, hl[2])));
      let tgt = mix3(bodyT, hw, bl);
      if (bl > 0) { const dv = sub(tgt, sh), dl = len(dv) || 1; tgt = sub(tgt, mul(dv, (b.hand * .45 * bl) / dl)); }   // palm, not wrist, lands
      const apole = add(add(mul(chestAx.f, -.8), mul(chestAx.r, sg * .45)), V(0, .25, 0));
      const arm = ik(sh, tgt, b.uarm, b.farm, apole);
      J['elbow' + s] = arm.mid; J['wrist' + s] = arm.end;
      J['handShape' + s] = C('handShape' + s); J['handRoll' + s] = C('handRoll' + s);
    }
    return J;
  }

  // ── secondary motion: damped spring of an attachment point, simulated over [t - W, t] ───────────────────────────
  function spring(c, t, probe, k = 60, damp = 9, W = .9) {
    const dt = 1 / 60; let p = probe(t - W), v = [0, 0, 0];
    for (let s = t - W + dt; s <= t + 1e-9; s += dt) {
      const goal = probe(s), a = sub(mul(sub(goal, p), k), mul(v, damp));
      v = add(v, mul(a, dt)); p = add(p, mul(v, dt));
    }
    return sub(p, probe(t));          // lag offset (px) relative to the attachment now
  }

  // ── drawing helpers ───────────────────────────────────────────────────────────────────────────────────────────
  const P2 = p => [p[0], p[1]];
  // a limb through points with radii, as one smooth outline (Catmull-Rom on both edges, round caps)
  function tube(pts, rad, openStart) {
    const n = pts.length, L = [], R = [];
    for (let i = 0; i < n; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
      let tx = b[0] - a[0], ty = b[1] - a[1]; const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
      let r = rad[i];
      if (i > 0 && i < n - 1) {     // shrink the inner side of a sharp bend so edges never fold over
        const u = [pts[i][0] - a[0], pts[i][1] - a[1]], w = [b[0] - pts[i][0], b[1] - pts[i][1]];
        const cr = (u[0] * w[1] - u[1] * w[0]) / ((Math.hypot(...u) * Math.hypot(...w)) || 1);
        const cosb = (u[0] * w[0] + u[1] * w[1]) / ((Math.hypot(...u) * Math.hypot(...w)) || 1);
        const bend = (1 - cosb) / 2;            // 0 straight … 1 folded
        L.push([pts[i][0] - ty * r * (cr > 0 ? 1 - .45 * bend : 1 + .12 * bend), pts[i][1] + tx * r * (cr > 0 ? 1 - .45 * bend : 1 + .12 * bend)]);
        R.push([pts[i][0] + ty * r * (cr < 0 ? 1 - .45 * bend : 1 + .12 * bend), pts[i][1] - tx * r * (cr < 0 ? 1 - .45 * bend : 1 + .12 * bend)]);
        continue;
      }
      L.push([pts[i][0] - ty * r, pts[i][1] + tx * r]); R.push([pts[i][0] + ty * r, pts[i][1] - tx * r]);
    }
    const cr = (q) => { let d = `M${f2(q[0][0])} ${f2(q[0][1])}`;
      for (let i = 0; i < q.length - 1; i++) { const p0 = q[Math.max(0, i - 1)], p1 = q[i], p2 = q[i + 1], p3 = q[Math.min(q.length - 1, i + 2)];
        d += ` C${f2(p1[0] + (p2[0] - p0[0]) / 6)} ${f2(p1[1] + (p2[1] - p0[1]) / 6)} ${f2(p2[0] - (p3[0] - p1[0]) / 6)} ${f2(p2[1] - (p3[1] - p1[1]) / 6)} ${f2(p2[0])} ${f2(p2[1])}`; }
      return d; };
    const Rr = R.slice().reverse();
    // round caps as outward bulges along the end tangents (unambiguous, never concave)
    const tan = (i, j) => { const dx = pts[j][0] - pts[i][0], dy = pts[j][1] - pts[i][1], l = Math.hypot(dx, dy) || 1; return [dx / l, dy / l]; };
    const te = tan(n - 2, n - 1), ts = tan(1, 0), re = rad[n - 1] * 1.05, rs = rad[0] * 1.05;
    const capE = `C${f2(L[n - 1][0] + te[0] * re)} ${f2(L[n - 1][1] + te[1] * re)} ${f2(Rr[0][0] + te[0] * re)} ${f2(Rr[0][1] + te[1] * re)} ${f2(Rr[0][0])} ${f2(Rr[0][1])}`;
    const capS = `C${f2(R[0][0] + ts[0] * rs)} ${f2(R[0][1] + ts[1] * rs)} ${f2(L[0][0] + ts[0] * rs)} ${f2(L[0][1] + ts[1] * rs)} ${f2(L[0][0])} ${f2(L[0][1])}`;
    const body = cr(L) + ' ' + capE + ' ' + cr(Rr).replace(/^M[^C]*/, '');
    if (openStart === 'stroke') return body;
    return body + ' ' + capS + 'Z';
  }
  // smooth closed blob through points
  function blob(q) {
    const n = q.length; let d = `M${f2(q[0][0])} ${f2(q[0][1])}`;
    for (let i = 0; i < n; i++) { const p0 = q[(i - 1 + n) % n], p1 = q[i], p2 = q[(i + 1) % n], p3 = q[(i + 2) % n];
      d += ` C${f2(p1[0] + (p2[0] - p0[0]) / 6)} ${f2(p1[1] + (p2[1] - p0[1]) / 6)} ${f2(p2[0] - (p3[0] - p1[0]) / 6)} ${f2(p2[1] - (p3[1] - p1[1]) / 6)} ${f2(p2[0])} ${f2(p2[1])}`; }
    return d + 'Z';
  }
  // silhouette half-width of an elliptical cross-section (half-width w along r, half-depth d along f) seen from +z
  const halfW = (ax, w, d) => Math.hypot(w * ax.r[0], d * ax.f[0]);
  // gradient across a limb axis (lit from upper left)
  function grad(c, gid, a, b, base, shade, lite) {
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    const sgn = (nx * -.7 + ny * -.7) > 0 ? 1 : -1;          // which normal points toward the light
    const m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], w = 60;
    c.gradHTML += `<linearGradient id="${gid}" gradientUnits="userSpaceOnUse" x1="${f2(m[0] + nx * w * sgn)}" y1="${f2(m[1] + ny * w * sgn)}" x2="${f2(m[0] - nx * w * sgn)}" y2="${f2(m[1] - ny * w * sgn)}">`
      + `<stop offset="0" stop-color="${lite}"/><stop offset=".45" stop-color="${base}"/><stop offset="1" stop-color="${shade}"/></linearGradient>`;
    return `url(#${gid})`;
  }

  // ── hands (2D, drawn at the wrist along the forearm direction) ─────────────────────────────────────────────────
  function hand(c, J, s, pal) {
    const w = J['wrist' + s], e = J['elbow' + s], shape = J['handShape' + s], b = c.b;
    let ang = Math.atan2(w[1] - e[1], w[0] - e[0]) + J['handRoll' + s] * D2R;
    const k = b.hand / 74;
    // palm facing: from the side the hand is seen edge-on; thumb side depends on which hand and the view
    const facing = dot(J.chestAx.f, V(0, 0, 1));     // +1 toward viewer
    const thumbSide = (s === 'R' ? 1 : -1) * (facing >= 0 ? -1 : 1);
    const cs = Math.cos(ang), sn = Math.sin(ang);
    const T = (x, y) => [w[0] + (x * cs - y * sn * thumbSide) * k, w[1] + (x * sn + y * cs * thumbSide) * k];
    const pts = q => q.map(([x, y]) => T(x, y));
    const skin = pal.skin, ink = INK;
    let d = '';
    if (shape > .5 && shape < 1.5) {          // grip / fist: knuckles rounded, thumb wrapped
      d = `<path d="${blob(pts([[0, -15], [20, -19], [42, -17], [52, -4], [50, 13], [34, 19], [12, 18], [0, 14]]))}" fill="${skin}" stroke="${ink}" stroke-width="2.6"/>`
        + `<path d="${tube(pts([[14, -16], [30, -24], [44, -14]]), [6, 6, 5])}" fill="${skin}" stroke="${ink}" stroke-width="2.2"/>`
        + `<path d="M${T(48, -6).map(f2).join(' ')} L${T(36, -4).map(f2).join(' ')} M${T(50, 4).map(f2).join(' ')} L${T(36, 6).map(f2).join(' ')}" stroke="${ink}" stroke-width="1.6" fill="none" opacity=".55"/>`;
    } else {
      const open = shape >= 1.5 && shape < 2.5, point = shape >= 2.5;
      if (!open && !point) {          // relaxed: fingers together, softly curled; thumb along the side
        d = `<path d="${blob(pts([[0, -14], [22, -16], [46, -13], [64, -6], [70, 4], [62, 13], [40, 16], [16, 15], [0, 12]]))}" fill="${skin}" stroke="${ink}" stroke-width="2.6"/>`
          + `<path d="M${T(46, -4).map(f2).join(' ')} Q${T(58, -2).map(f2).join(' ')} ${T(66, 2).map(f2).join(' ')} M${T(44, 5).map(f2).join(' ')} Q${T(56, 7).map(f2).join(' ')} ${T(62, 10).map(f2).join(' ')}" fill="none" stroke="${ink}" stroke-width="1.6" opacity=".5"/>`
          + `<path d="${tube(pts([[12, -12], [26, -22], [40, -21]]), [7, 6, 5])}" fill="${skin}" stroke="${ink}" stroke-width="2.2"/>`;
      } else {
        const spread = open ? 1.5 : 1;
        d = `<path d="${blob(pts([[0, -14], [18, -17], [40, -14], [44, 0], [40, 14], [18, 16], [0, 13]]))}" fill="${skin}" stroke="${ink}" stroke-width="2.6"/>`;
        [[-9, 32], [-2, 38], [5, 36], [12, 29]].forEach(([dy, l], i) => {
          const curl = point && i > 0 ? .55 : .05;
          const base = [40, dy * spread * .9], mid = [40 + l * .55, dy * spread * 1.05 + l * curl * .5], tip = [40 + l * (1 - curl * .9), dy * spread * 1.1 + l * curl * 1.1];
          d += `<path d="${tube(pts([base, mid, tip]), [5.6, 5.2, 4.6])}" fill="${skin}" stroke="${ink}" stroke-width="2.1"/>`;
        });
        d += `<path d="${tube(pts([[10, -13], [24, -26 * (open ? 1.2 : 1)], [34, -30 * (open ? 1.25 : 1)]]), [7, 6, 5])}" fill="${skin}" stroke="${ink}" stroke-width="2.2"/>`;
      }
    }
    return d;
  }

  // ── head: skull, ears, face on a sphere, hair ─────────────────────────────────────────────────────────────────
  function head(c, J, t, pal) {
    const b = c.b, H = J.head, ax = J.headAx, R = b.head, C = n => c.ch[n].at(t);
    // a point on the head sphere: yaw u (deg, 0 = nose), pitch v (deg, + down) → screen
    const sp = (u, v, r = 1) => { const a = u * D2R, e = v * D2R + J.headPitch;
      const loc = add(add(mul(ax.f, Math.cos(a) * Math.cos(e) * R * r), mul(ax.r, Math.sin(a) * Math.cos(e) * R * r * .92)), V(0, Math.sin(e) * R * r * 1.12, 0));
      return add(H, loc); };
    const vis = (u, v) => dot(sub(sp(u, v), H), V(0, 0, 1)) > -R * .08;
    const tilt = J.headTilt;
    let out = '';
    // skull silhouette (slightly taller than wide), jaw toward the face direction
    const fx = ax.f[0], q = [];
    for (let i = 0; i < 24; i++) { const a = i / 24 * Math.PI * 2;
      let x = Math.cos(a) * R * .9, y = Math.sin(a) * R * 1.12;
      if (y > 0) x += fx * R * .16 * (y / (R * 1.12));                 // jaw leans toward where the face points
      if (y > R * .55) x *= .86;
      q.push([H[0] + x * Math.cos(tilt) - y * Math.sin(tilt), H[1] + x * Math.sin(tilt) + y * Math.cos(tilt)]); }
    // ears
    const ear = (u) => { if (!vis(u, 4)) return ''; const e = sp(u, 6, 1.0); return `<ellipse cx="${f2(e[0])}" cy="${f2(e[1])}" rx="${f2(R * .16 * Math.abs(Math.cos((u - 90) * D2R) * .6 + .4))}" ry="${f2(R * .24)}" fill="${pal.skinShade}" stroke="${INK}" stroke-width="2.4"/>`; };
    // hair behind the head
    out += hairBack(c, J, t, pal, H, R, ax);
    out += ear(-96) + ear(96);
    out += `<path d="${blob(q)}" fill="${grad(c, c.id + '-gh', [H[0] - R, H[1]], [H[0] + R, H[1]], pal.skin, pal.skinShade, pal.skinLite)}" stroke="${INK}" stroke-width="3"/>`;
    c.gradHTML += `<clipPath id="${c.id}-hc"><path d="${blob(q)}"/></clipPath>`;          // features stay on the face
    out += `<g clip-path="url(#${c.id}-hc)">`;
    let noseOut = '';
    const toward = dot(ax.f, V(0, 0, 1));         // face visibility
    if (toward > -.35) {
      const gz = C('gaze'), eo = C('eyeOpen') * blinkAt(c, t), br = C('brow'), sm = C('smile'), mo = Math.max(C('mouth'), speakAt(c, t)), jw = C('jaw');
      // eyes
      for (const u of [-30, 30]) { if (dot(sub(sp(u, -2), H), V(0, 0, 1)) < R * .12) continue;
        const e = sp(u, -2, .98), fore = clamp(dot(norm(sub(e, H)), V(0, 0, 1)) * 1.25, .32, 1);
        const ew = R * .19 * fore, eh = R * .13 * Math.max(.06, eo);
        out += `<ellipse cx="${f2(e[0])}" cy="${f2(e[1])}" rx="${f2(ew)}" ry="${f2(eh)}" fill="#fbf7f0" stroke="${INK}" stroke-width="2"/>`;
        if (eo > .2) out += `<circle cx="${f2(e[0] + gz[0] * ew * .45 + ax.f[0] * ew * .25)}" cy="${f2(e[1] + gz[1] * eh * .35)}" r="${f2(R * .085 * Math.min(1, eo + .2))}" fill="${pal.iris}"/>`
          + `<circle cx="${f2(e[0] + gz[0] * ew * .45 + ax.f[0] * ew * .25)}" cy="${f2(e[1] + gz[1] * eh * .35)}" r="${f2(R * .04)}" fill="#0d0a08"/>`;
        // upper lid line + brow
        out += `<path d="M${f2(e[0] - ew)} ${f2(e[1] - eh * .2)} Q${f2(e[0])} ${f2(e[1] - eh * 1.25)} ${f2(e[0] + ew)} ${f2(e[1] - eh * .2)}" fill="none" stroke="${INK}" stroke-width="${pal.lashes ? 3.6 : 2.6}"/>`;
        if (pal.lashes && eo > .3) out += `<path d="M${f2(e[0] + (u < 0 ? -ew : ew))} ${f2(e[1] - eh * .2)} l${u < 0 ? -7 : 7} -5" stroke="${INK}" stroke-width="2.4" stroke-linecap="round"/>`;
        const bi = u < 0 ? 0 : 1, raise = br[bi], bw = sp(u, -19 - raise * 6, 1.01), inner = u < 0 ? 1 : -1;
        out += `<path d="M${f2(bw[0] - ew * 1.1)} ${f2(bw[1] + raise * 2)} Q${f2(bw[0])} ${f2(bw[1] - 5 - raise * 4)} ${f2(bw[0] + ew * 1.1)} ${f2(bw[1] + raise * 2 + inner * (raise < 0 ? -raise * 6 : 0))}" fill="none" stroke="${pal.hair}" stroke-width="${f2(R * .07)}" stroke-linecap="round"/>`;
        if (pal.glasses) out += `<rect x="${f2(e[0] - ew * 1.35)}" y="${f2(e[1] - R * .19)}" width="${f2(ew * 2.7)}" height="${f2(R * .34)}" rx="${f2(R * .08)}" fill="rgba(200,220,235,.12)" stroke="#2a2a2e" stroke-width="2.4"/>`;
      }
      // nose: a profile bump at the silhouette when turned, a soft shape from the front
      // nose: grows into a silhouette bump as the head turns to profile; a soft line from the front
      const side = ax.f[0], prof = Math.abs(side);
      const nb = sp(0, 2, 1.0), nt = sp(0, 22, 1.0), nbt = sp(0, 30, 1.0);
      const tip = [nt[0] + side * R * .2 * prof, nt[1] + R * .02];
      if (prof > .35) noseOut += `<path d="M${f2(nb[0])} ${f2(nb[1])} Q${f2(tip[0])} ${f2(nt[1] - R * .06)} ${f2(tip[0])} ${f2(tip[1])} Q${f2(tip[0] - side * R * .05)} ${f2(nbt[1])} ${f2(nbt[0])} ${f2(nbt[1])} Z" fill="${pal.skin}" stroke="${INK}" stroke-width="2.4" stroke-linejoin="round"/>`
        + `<path d="M${f2(nb[0] - side * 3)} ${f2(nb[1] - 4)} L${f2(nbt[0] - side * 3)} ${f2(nbt[1] + 4)}" stroke="${pal.skin}" stroke-width="5"/>`;
      else { const n0 = sp(0, 6, 1.0), n1 = sp(0, 22, 1.04);
        out += `<path d="M${f2(n0[0])} ${f2(n0[1])} Q${f2(n1[0] + side * R * .06)} ${f2(n1[1] - R * .02)} ${f2(n1[0] - side * R * .07)} ${f2(n1[1] + R * .05)}" fill="none" stroke="${INK}" stroke-width="2.4" stroke-linecap="round"/>`; }
      // mouth
      if (vis(0, 40) || Math.abs(ax.f[0]) > .5) {
        const m = sp(0, 42, .99), mw = R * .22 * clamp(Math.abs(ax.f[2]) + .25, .35, 1);
        const curve = sm * R * .1, open = (mo + jw) * R * .16;
        out += open > 1 ? `<path d="M${f2(m[0] - mw)} ${f2(m[1] - curve * .5)} Q${f2(m[0])} ${f2(m[1] + curve)} ${f2(m[0] + mw)} ${f2(m[1] - curve * .5)} Q${f2(m[0])} ${f2(m[1] + curve + open)} ${f2(m[0] - mw)} ${f2(m[1] - curve * .5)}Z" fill="#5a2420" stroke="${INK}" stroke-width="2.2"/>`
          : `<path d="M${f2(m[0] - mw)} ${f2(m[1] - curve * .5)} Q${f2(m[0])} ${f2(m[1] + curve)} ${f2(m[0] + mw)} ${f2(m[1] - curve * .5)}" fill="none" stroke="${pal.lips || INK}" stroke-width="${pal.lips ? 3.4 : 2.6}" stroke-linecap="round"/>`;
      }
      if (pal.beard) { const ch = sp(0, 62, .97); out += `<path d="M${f2(ch[0] - R * .4)} ${f2(ch[1] - R * .25)} Q${f2(ch[0])} ${f2(ch[1] + R * .28)} ${f2(ch[0] + R * .4)} ${f2(ch[1] - R * .25)}" fill="${pal.hair}" opacity=".75"/>`; }
    }
    out += '</g>' + (typeof noseOut === 'string' ? noseOut : '');
    out += hairFront(c, J, t, pal, H, R, ax, sp, vis);
    return out;
  }

  // hair: a cap on the skull, parted / short / buzz / bun; tips lag with a spring
  function hairBack(c, J, t, pal, H, R, ax) {
    const st = pal.hairStyle;
    if (st === 'bun' || st === 'long') {
      const lag = c._hairLag || [0, 0, 0];
      const bk = add(H, add(mul(ax.f, -R * .75), V(lag[0] * .6, -R * .35 + lag[1] * .3, 0)));
      return `<circle cx="${f2(bk[0])}" cy="${f2(bk[1])}" r="${f2(R * .42)}" fill="${pal.hair}" stroke="${INK}" stroke-width="2.6"/>`;
    }
    return '';
  }
  // hairline height (pitch deg, negative = up) around the head, u = 0 at the nose
  function hairline(st, u) {
    const a = Math.abs(((u + 540) % 360) - 180);                   // 0 front … 180 back
    const front = st === 'parted' ? -44 + 9 * Math.sin((u + 20) * D2R * 1.4) : st === 'buzz' ? -50 : -47;
    const side = st === 'buzz' ? -14 : 2, back = st === 'buzz' ? 26 : st === 'short' ? 34 : 40;
    if (a < 70) return lerp(front, front + 6, a / 70);
    if (a < 105) return lerp(front + 6, side, (a - 70) / 35);      // temples down to above the ear
    return lerp(side, back, (a - 105) / 75);
  }
  function hairFront(c, J, t, pal, H, R, ax, sp, vis) {
    const st = pal.hairStyle, lag = c._hairLag || [0, 0, 0], tilt = J.headTilt;
    // head outline points, each mapped back to head-sphere coordinates (u, v); keep those above the hairline
    const N = 64, lim = [];
    for (let i = 0; i < N; i++) { const a = i / N * Math.PI * 2;
      const x = Math.cos(a) * R * .97, y = Math.sin(a) * R * 1.17;
      const sx = x * Math.cos(tilt) - y * Math.sin(tilt), sy = x * Math.sin(tilt) + y * Math.cos(tilt);
      const vec = V(sx, sy, 0);
      const u = Math.atan2(dot(vec, ax.r) / .92, dot(vec, ax.f)) / D2R;
      const v = Math.asin(clamp(sy / (R * 1.17), -1, 1)) / D2R - J.headPitch / D2R;
      lim.push({ p: [H[0] + sx, H[1] + sy], u, inside: v < hairline(st, u) }); }
    if (!lim.some(q => q.inside)) return '';
    // contiguous run of kept outline points (wrapping), start → end
    let s0 = lim.findIndex((q, i) => q.inside && !lim[(i - 1 + N) % N].inside); if (s0 < 0) s0 = 0;
    const run = []; for (let k = 0; k < N && lim[(s0 + k) % N].inside; k++) run.push(lim[(s0 + k) % N]);
    let pts = run.map(q => [q.p[0] + lag[0] * .15, q.p[1] + lag[1] * .08]);
    if (run.length < N) {      // close along the hairline from the run's end back to its start, over the visible side
      const ue = run[run.length - 1].u, us = run[0].u;
      const path = (dir) => { const out = []; let span = ((us - ue) * dir + 720) % 360; for (let k = 1; k < 12; k++) { const u = ue + dir * span * k / 12; out.push([u, sp(u, hairline(st, u), 1.035)]); } return out; };
      const A = path(1), B = path(-1);
      const zsum = q => q.reduce((m, [, p]) => m + p[2], 0);
      const best = zsum(A) > zsum(B) ? A : B;
      pts = pts.concat(best.map(([, p]) => [p[0] + lag[0] * .1, p[1]]));
    }
    let d = `<path d="${blob(pts)}" fill="${pal.hair}" stroke="${INK}" stroke-width="2.8" stroke-linejoin="round"/>`;
    if (st === 'parted' && vis(-30, -62)) {          // side part and a forelock that lags a little behind head moves
      const a0 = sp(-30, -64, 1.04), m = sp(5, -52, 1.07), e = sp(50, -44, 1.05);
      d += `<path d="M${f2(a0[0])} ${f2(a0[1])} Q${f2(m[0] + lag[0] * .4)} ${f2(m[1] + lag[1] * .3)} ${f2(e[0] + lag[0] * .6)} ${f2(e[1] + lag[1] * .4)}" fill="none" stroke="${pal.hairHi || '#8a6a44'}" stroke-width="3" stroke-linecap="round" opacity=".85"/>`;
    }
    if (vis(140, -40)) { const s0p = sp(150, -55, 1.05), s1p = sp(115, -15, 1.05);
      d += `<path d="M${f2(s0p[0])} ${f2(s0p[1])} Q${f2((s0p[0] + s1p[0]) / 2 + 6)} ${f2((s0p[1] + s1p[1]) / 2)} ${f2(s1p[0])} ${f2(s1p[1])}" stroke="${pal.hairHi || '#999'}" stroke-width="2.4" fill="none" opacity=".55"/>`; }
    return d;
  }

  // ── blinks and speech (seeded schedules; speech only when the character speaks in the story) ──────────────────
  function seeded(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function blinks(id, a, b, seed) { const c = chars[id], r = seeded(seed); for (let t = a + .4 + r() * 1.4; t < b; t += 2.2 + r() * 3.2) c.blinkT.push([t, r() < .15]); }
  function blinkAt(c, t) {
    for (const [bt, dbl] of c.blinkT) { const x = t - bt; if (x < -.01) break;
      if (x < .2) return 1 - Math.sin(clamp(x / .2, 0, 1) * Math.PI) * .95;
      if (dbl && x >= .26 && x < .44) return 1 - Math.sin(clamp((x - .26) / .18, 0, 1) * Math.PI) * .95; }
    return 1;
  }
  function say(id, a, b, seed) { chars[id].speak.push([a, b, seeded(seed || 3)]); chars[id].speak.sort((x, y) => x[0] - y[0]); }
  function speakAt(c, t) {
    for (const [a, b, r0] of c.speak) if (t >= a && t < b) {          // deterministic syllable rhythm from the seed
      const k = Math.floor((t - a) / .12), ph = ((t - a) % .12) / .12, r = seeded(Math.floor(a * 1000) + k * 7919)();
      return (.25 + r * .6) * Math.sin(ph * Math.PI);
    }
    return 0;
  }

  // ── torso and clothes ─────────────────────────────────────────────────────────────────────────────────────────
  function torso(c, J, pal) {
    const b = c.b, cx = J.chestAx, hx = J.hipAx;
    const wS = halfW(cx, b.shW + 6, b.chestD), wW = halfW(hx, b.waistW, b.waistD), wH = halfW(hx, b.hipW + 22, b.hipD);
    const sh = J.chest, wa = J.waist, hp = J.root;
    const nk = J.neck;
    const q = [[sh[0] - wS, sh[1] + 4], [sh[0] - wS * .96, sh[1] + 40], [wa[0] - wW, wa[1]], [hp[0] - wH, hp[1] + 18],
               [hp[0] + wH, hp[1] + 18], [wa[0] + wW, wa[1]], [sh[0] + wS * .96, sh[1] + 40], [sh[0] + wS, sh[1] + 4],
               [nk[0] + wS * .35, nk[1] + 2], [nk[0] - wS * .35, nk[1] + 2]];
    const top = pal.jacket || pal.shirt, topS = pal.jacketShade || pal.shirtShade;
    let d = `<path d="${blob(q)}" fill="${grad(c, c.id + '-gt', [sh[0] - wS, sh[1]], [sh[0] + wS, sh[1]], top, topS, lighten(top))}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>`;
    const toward = dot(cx.f, V(0, 0, 1));
    if (toward > -.2) {
      // shirt front / collar / tie, placed on the front of the chest (shifted toward the facing direction)
      const fx = cx.f[0] * b.chestD * .8, colW = Math.max(6, wS * .42);
      const c0 = [nk[0] + fx * .5, nk[1] + 6], c1 = [sh[0] + fx, sh[1] + 70], c2 = [wa[0] + fx * .9, wa[1] - 10];
      if (pal.jacket) {
        d += `<path d="M${f2(c0[0] - colW)} ${f2(c0[1])} L${f2(c1[0])} ${f2(c1[1] + 30)} L${f2(c0[0] + colW)} ${f2(c0[1])} Z" fill="${pal.shirt}" stroke="${INK}" stroke-width="2.4" stroke-linejoin="round"/>`;
        if (pal.tie) { const lag = c._tieLag || [0, 0, 0];
          d += `<path d="M${f2(c0[0] - 7)} ${f2(c0[1] + 4)} L${f2(c0[0] + 7)} ${f2(c0[1] + 4)} L${f2(c1[0] + 9 + lag[0] * .3)} ${f2(c1[1] + 26)} L${f2(c1[0] + lag[0] * .45)} ${f2(c1[1] + 40)} L${f2(c1[0] - 9 + lag[0] * .3)} ${f2(c1[1] + 26)}Z" fill="${pal.tie}" stroke="${INK}" stroke-width="2.2"/>`; }
        // lapels
        d += `<path d="M${f2(c0[0] - colW)} ${f2(c0[1])} L${f2(c0[0] - colW - 14)} ${f2(c0[1] + 34)} L${f2(c1[0] - 2)} ${f2(c1[1] + 30)} M${f2(c0[0] + colW)} ${f2(c0[1])} L${f2(c0[0] + colW + 14)} ${f2(c0[1] + 34)} L${f2(c1[0] + 2)} ${f2(c1[1] + 30)}" fill="none" stroke="${INK}" stroke-width="2.4" opacity=".85"/>`;
        d += `<path d="M${f2(c1[0])} ${f2(c1[1] + 34)} L${f2(c2[0])} ${f2(hp[1] + 14)}" stroke="${INK}" stroke-width="2" opacity=".6"/>`;
        d += `<circle cx="${f2(c1[0] + 6)} " cy="${f2(wa[1] - 4)}" r="3.4" fill="${INK}" opacity=".7"/>`;
      } else {
        // open-collar shirt: a V placket and two collar points
        d += `<path d="M${f2(c0[0] - colW)} ${f2(c0[1] - 2)} L${f2(c0[0])} ${f2(c0[1] + 34)} L${f2(c0[0] + colW)} ${f2(c0[1] - 2)}" fill="${pal.skin}" stroke="${INK}" stroke-width="2.4" stroke-linejoin="round"/>`
          + `<path d="M${f2(c0[0] - colW - 4)} ${f2(c0[1] - 6)} L${f2(c0[0] - 4)} ${f2(c0[1] + 30)} L${f2(c0[0] - colW - 10)} ${f2(c0[1] + 22)}Z M${f2(c0[0] + colW + 4)} ${f2(c0[1] - 6)} L${f2(c0[0] + 4)} ${f2(c0[1] + 30)} L${f2(c0[0] + colW + 10)} ${f2(c0[1] + 22)}Z" fill="${pal.shirt}" stroke="${INK}" stroke-width="2.2" stroke-linejoin="round"/>`
          + `<path d="M${f2(c0[0])} ${f2(c0[1] + 34)} L${f2(c2[0])} ${f2(hp[1] + 14)}" stroke="${INK}" stroke-width="1.8" opacity=".5"/>`;
        [0, 1, 2].forEach(i => { const y = c0[1] + 60 + i * 70, x = lerp(c0[0], c2[0], (y - c0[1]) / (hp[1] - c0[1])); d += `<circle cx="${f2(x + 5)}" cy="${f2(y)}" r="3" fill="${INK}" opacity=".45"/>`; });
      }
    }
    // apron: bib over the chest, skirt to mid-thigh, neck strap and waist tie (front); ties only from behind
    if (pal.apron) {
      const fxa = cx.f[0] * b.chestD * .75, ww = Math.max(.32, Math.abs(cx.f[2]));
      const tb = [sh[0] + fxa, sh[1] + 52], bw = wS * .62 * ww, sw = wH * 1.08 * Math.max(.4, Math.abs(hx.f[2])), hem = hp[1] + b.thigh * .55;
      if (toward > -.2) {
        d += `<path d="${blob([[tb[0] - bw, tb[1]], [tb[0] + bw, tb[1]], [wa[0] + fxa + bw * 1.05, wa[1] + 8], [hp[0] + fxa + sw, hem - 10], [hp[0] + fxa + sw * .9, hem], [hp[0] + fxa - sw * .9, hem], [hp[0] + fxa - sw, hem - 10], [wa[0] + fxa - bw * 1.05, wa[1] + 8]])}" fill="${pal.apron}" stroke="${INK}" stroke-width="2.8" stroke-linejoin="round"/>`
          + `<path d="M${f2(tb[0] - bw)} ${f2(tb[1])} L${f2(nk[0] - 6)} ${f2(nk[1] + 10)} M${f2(tb[0] + bw)} ${f2(tb[1])} L${f2(nk[0] + 6)} ${f2(nk[1] + 10)}" stroke="${pal.apron}" stroke-width="7" stroke-linecap="round"/>`
          + `<rect x="${f2(tb[0] - bw * .45)}" y="${f2(wa[1] + 26)}" width="${f2(bw * .9)}" height="34" rx="4" fill="none" stroke="${lighten(pal.apron, .25)}" stroke-width="3"/>`
          + `<path d="M${f2(wa[0] + fxa - bw * 1.05)} ${f2(wa[1] + 10)} L${f2(wa[0] + fxa + bw * 1.05)} ${f2(wa[1] + 10)}" stroke="${lighten(pal.apron, .3)}" stroke-width="4" opacity=".7"/>`;
      } else {
        d += `<path d="M${f2(wa[0] - wW)} ${f2(wa[1] + 8)} L${f2(wa[0] + wW)} ${f2(wa[1] + 8)}" stroke="${pal.apron}" stroke-width="8"/>`
          + `<path d="M${f2(wa[0] - 6)} ${f2(wa[1] + 8)} q-16 14 -10 30 M${f2(wa[0] + 6)} ${f2(wa[1] + 8)} q16 14 10 30" stroke="${pal.apron}" stroke-width="6" fill="none" stroke-linecap="round"/>`;
      }
    }
    if (pal.lanyard && toward > -.2) {
      const fxl = cx.f[0] * b.chestD * .8, bx = sh[0] + fxl + 4, by = sh[1] + 150;
      d += `<path d="M${f2(nk[0] - 14 + fxl * .5)} ${f2(nk[1] + 6)} L${f2(bx)} ${f2(by)} L${f2(nk[0] + 14 + fxl * .5)} ${f2(nk[1] + 6)}" fill="none" stroke="${pal.lanyard}" stroke-width="5"/>`
        + `<rect x="${f2(bx - 22)}" y="${f2(by)}" width="44" height="58" rx="5" fill="#f6f6f2" stroke="${INK}" stroke-width="2.4"/><rect x="${f2(bx - 22)}" y="${f2(by)}" width="44" height="14" rx="4" fill="${pal.lanyard}"/>`
        + `<rect x="${f2(bx - 14)}" y="${f2(by + 22)}" width="28" height="18" fill="#c9d4e0"/>`;
    }
    // belt
    d += `<path d="M${f2(hp[0] - wH)} ${f2(hp[1] - 6)} Q${f2(hp[0])} ${f2(hp[1] + 2)} ${f2(hp[0] + wH)} ${f2(hp[1] - 6)}" fill="none" stroke="${pal.belt || '#2a1d14'}" stroke-width="9" opacity="${pal.jacket ? 0 : .9}"/>`;
    return d;
  }
  const lighten = (hex, k = .22) => { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = n >> 8 & 255, b = n & 255;
    const L = v => Math.round(v + (255 - v) * k).toString(16).padStart(2, '0'); return '#' + L(r) + L(g) + L(b); };

  // ── draw one character at time t ──────────────────────────────────────────────────────────────────────────────
  function draw(c, t) {
    const J = solve(c, t), b = c.b, pal = c.spec.look;
    c.gradHTML = '';
    // secondary motion: hair and tie lag behind the head / chest
    c._hairLag = spring(c, t, s => { const j = solve(c, s); return j.head; }, 70, 10, .7);
    c._tieLag = spring(c, t, s => { const j = solve(c, s); return j.chest; }, 45, 7, .9);
    const parts = [];   // [z, svg]
    const zOf = p => p[2];
    // legs (trousers) and shoes
    for (const s of ['L', 'R']) {
      const hip = J['hip' + s], kn = J['knee' + s], an = J['ankle' + s];
      const z = (zOf(hip) + zOf(kn) + zOf(an)) / 3;
      const fill = grad(c, `${c.id}-gl${s}`, P2(hip), P2(an), pal.trousers, pal.trousersShade, lighten(pal.trousers, .12));
      let svg = `<path d="${tube([P2(hip), P2(kn), P2(an)], [b.legR * 1.18, b.legR * .86, b.legR * .72])}" fill="${fill}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>`;
      // shoe from the projected heel, toe and ankle: long in profile, short and round from the front
      const he = J['heel' + s], to = J['toe' + s], fwd = J['footAx' + s].f;
      const ex = Math.sign(fwd[0]) || 1, side = Math.abs(fwd[0]), w = b.legR * (.78 + (1 - side) * .32);
      const gy = Math.max(he[1], to[1]), h = gy - an[1];
      const shoe = [[an[0] - ex * w * .55, an[1] + h * .15], [he[0] - ex * w * .45, he[1] - h * .35], [he[0] - ex * w * .35, he[1] + 2],
                    [to[0] + ex * w * .15, to[1] + 2], [to[0] + ex * w * .3, to[1] - h * .45], [lerp(an[0], to[0], .45) + ex * w * .2, lerp(an[1], to[1], .45) - h * .12],
                    [an[0] + ex * w * .5, an[1] + h * .05]];
      if (side < .35) { shoe[2][0] -= w * .4; shoe[3][0] += w * .4 * (1 - side); }
      svg += `<path d="${blob(shoe)}" fill="${pal.shoes}" stroke="${INK}" stroke-width="2.8" stroke-linejoin="round"/>`
        + `<path d="M${f2(shoe[2][0])} ${f2(gy - 3)} L${f2(shoe[3][0])} ${f2(gy - 3)}" stroke="#5a4a3a" stroke-width="3" opacity=".6"/>`;
      parts.push([zOf(J.chest) - 200 + z * .01, svg]);
    }
    // torso
    parts.push([zOf(J.chest), torso(c, J, pal)]);
    // neck
    const nk = J.neck, hd = J.head;
    parts.push([zOf(J.chest) + .5, `<path d="${tube([P2(nk), P2(mix3(nk, hd, .45))], [b.head * .34, b.head * .32])}" fill="${pal.skinShade}" stroke="${INK}" stroke-width="2.6"/>`]);
    // arms (sleeves) + hands
    for (const s of ['L', 'R']) {
      const sh = J['sh' + s], el = J['elbow' + s], wr = J['wrist' + s];
      const z = (zOf(sh) + zOf(el) * 2 + zOf(wr) * 2) / 5;
      const top = pal.jacket || pal.shirt, topS = pal.jacketShade || pal.shirtShade;
      const fill = grad(c, `${c.id}-ga${s}`, P2(sh), P2(wr), top, topS, lighten(top, .18));
      const rolled = pal.sleeves === 'rolled', cuff = rolled ? mix3(el, wr, .3) : mix3(el, wr, .9);
      if (rolled)       // bare forearm from the roll to the wrist (drawn first, under the rolled cuff)
        var fore = `<path d="${tube([P2(mix3(el, wr, .25)), P2(wr)], [b.armR * .8, b.armR * .62])}" fill="${grad(c, `${c.id}-gf${s}`, P2(el), P2(wr), pal.skin, pal.skinShade, pal.skinLite)}" stroke="${INK}" stroke-width="2.6"/>`;
      // the sleeve starts inside the shoulder and its outline is open there, so the arm grows out of the torso
      const sh0 = add(add(sh, mul(J.chestAx.r, (s === 'R' ? -1 : 1) * b.armR * 1.0)), V(0, b.armR * .55, 0));
      const ap = [P2(sh0), P2(el), P2(cuff)], ar = [b.armR * 1.22, b.armR * .95, b.armR * .82];
      let svg = (rolled ? fore : '') + `<path d="${tube(ap, ar)}" fill="${fill}"/><path d="${tube(ap, ar, 'stroke')}" fill="none" stroke="${INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>`;
      if (rolled) svg += `<path d="${tube([P2(mix3(el, wr, .2)), P2(mix3(el, wr, .36))], [b.armR * 1.02, b.armR * .98])}" fill="${lighten(top, .1)}" stroke="${INK}" stroke-width="2.4"/>`;
      if (pal.jacket) svg += `<path d="${tube([P2(mix3(el, wr, .84)), P2(mix3(el, wr, .97))], [b.armR * .72, b.armR * .7])}" fill="${pal.shirt}" stroke="${INK}" stroke-width="2"/>`;
      svg += hand(c, J, s, pal);
      // a held prop follows the hand
      parts.push([z + (dot(J.chestAx.f, V(0, 0, 1)) > 0 ? .2 : -.2) + (z > zOf(J.chest) ? 40 : 0), svg, 'arm' + s]);
    }
    parts.push([zOf(hd) + 50, head(c, J, t, pal)]);
    parts.sort((a, b2) => a[0] - b2[0]);
    // foreground occlusion (e.g. a table edge in front of the character): everything below the line is clipped,
    // except an arm that is reaching for a world target (a hand on the tabletop stays visible)
    const oc = c.spec.occlude;
    if (oc) c.gradHTML += `<clipPath id="${c.id}-occ"><rect x="-20000" y="-20000" width="40000" height="${f2(20000 + oc.y)}"/></clipPath>`;
    const wrap = (p) => { if (!oc) return p[1];
      const reaching = p[2] && c.ch['handBlend' + p[2].slice(3)].at(t) > .35;
      return reaching ? p[1] : `<g clip-path="url(#${c.id}-occ)">${p[1]}</g>`; };
    c.defs.innerHTML = c.gradHTML;
    c.body.innerHTML = parts.map(wrap).join('');
    c.shadow.setAttribute('visibility', oc ? 'hidden' : 'visible');
    // contact shadow between the feet
    const fL = c.ch.footL.at(t), fR = c.ch.footR.at(t);
    c.shadow.setAttribute('cx', f2((fL[0] + fR[0]) / 2)); c.shadow.setAttribute('cy', f2(c.ground + 2));
    c.shadow.setAttribute('rx', f2(Math.max(70, Math.abs(fL[0] - fR[0]) / 2 + 60) * c.b.head / 64)); c.shadow.setAttribute('ry', f2(16 * c.b.head / 64));
    // props attached to hands
    for (const pr of c.props) {
      const on = t >= pr.a && t < pr.b, el = document.getElementById(pr.el); if (!el) continue;
      if (!on) {                    // a prop is a function of time too: at rest before the hold, put down after it
        const tr = t < pr.a ? pr.rest : (pr.after || pr.rest);
        if (tr) el.setAttribute('transform', tr); else el.removeAttribute('transform');
        continue;
      }
      const w = J['wrist' + pr.side], e = J['elbow' + pr.side];
      if (pr.rot === 'upright') {    // a sheet held up to read stays level, whatever the wrist angle
        el.setAttribute('transform', `translate(${f2(w[0])} ${f2(w[1])})`); continue;
      }
      const ang = Math.atan2(w[1] - e[1], w[0] - e[0]) / D2R + (pr.rot || 0);
      const k = b.hand / 74, gx = w[0] + Math.cos(ang * D2R) * 34 * k, gy = w[1] + Math.sin(ang * D2R) * 34 * k;
      el.setAttribute('transform', `translate(${f2(gx)} ${f2(gy)}) rotate(${f2(ang)})`);
    }
    c.J = J;
  }
  function drawAll(t) { for (const id in chars) draw(chars[id], t); }

  // ── authoring API ─────────────────────────────────────────────────────────────────────────────────────────────
  const key = (id, name, t, to, d, ease) => { const c = chars[id]; if (c && c.ch[name]) c.ch[name].key(t, to, d, ease); };
  const val = (id, name, t) => chars[id].ch[name].at(t);

  // eyes lead, head follows part of the way: look at a local point
  function look(id, t, target, d = .35) {
    const c = chars[id], J = solve(c, t);
    const dx = target[0] - J.head[0], dy = target[1] - J.head[1];
    const yaw = c.ch.yaw.at(t) + c.ch.twist.at(t);
    const want = dx >= 0 ? 90 : -90;                                     // the screen side the target is on
    const diff = ((want - yaw + 540) % 360) - 180;
    const k = clamp(Math.abs(dx) / 500, 0, 1) * .6;
    key(id, 'gaze', t, [clamp(dx / 300, -1, 1), clamp(dy / 300, -1, 1)], .12, 'out');
    key(id, 'headYaw', t + .08, clamp(diff * k, -40, 40), d, 'inOut');
    key(id, 'headPitch', t + .08, clamp(dy / 25, -14, 16), d, 'inOut');
  }
  // reach a world (local px) point with one hand; grip on contact; the body leans in when the target is far
  function reach(id, side, t, target, d = .5, o = {}) {
    const c = chars[id], s = side;
    key(id, 'handW' + s, t, target, 0);
    key(id, 'handBlend' + s, t, 1, d, 'inOut');
    if (o.shape !== undefined) key(id, 'handShape' + s, t + d * .7, o.shape, d * .3, 'inOut');
    let lean = o.lean;
    if (lean === undefined) {          // lean in from the hips only as far as the target needs
      const keep = c.ch.lean, reachL = (c.b.uarm + c.b.farm) * .97 + c.b.hand * .45;
      lean = keep.at(t);
      for (let L = Math.max(4, lean); L <= 58; L += 2) {
        c.ch.lean = { at: () => L }; const J = solve(c, t + d); c.ch.lean = keep;
        lean = L; if (len(sub(target, J['sh' + s])) <= reachL) break;
      }
      c.ch.lean = keep;
    }
    if (Math.abs(lean - c.ch.lean.at(t)) > 1) key(id, 'lean', t, lean, d * 1.1, 'inOut');
    if (o.look !== false) look(id, t - .15, target, d * .8);
  }
  function release(id, side, t, d = .5, rest) {
    key(id, 'handBlend' + side, t, 0, d, 'inOut'); key(id, 'handShape' + side, t, 0, d * .5);
    if (rest) key(id, 'hand' + side, t, rest, d, 'inOut');
  }
  // body-local arm pose (side, down, forward from the shoulder)
  const arm = (id, side, t, p, d = .45, ease = 'inOut') => key(id, 'hand' + side, t, p, d, ease);
  function turn(id, t, yaw, d = .6) {          // head leads, body follows, feet re-plant with small steps
    const c = chars[id], y0 = c.ch.yaw.at(t);
    key(id, 'headYaw', t, clamp((yaw - y0) * .45, -50, 50), d * .45, 'out');
    key(id, 'yaw', t + d * .15, yaw, d * .85, 'inOut');
    key(id, 'headYaw', t + d * .7, 0, d * .5, 'inOut');
    const r = c.ch.root.at(t), ax = frameAxes(yaw);
    ['L', 'R'].forEach((s, i) => { const sg = s === 'R' ? 1 : -1, p = c.ch['foot' + s].at(t);
      const to = [r[0] + ax.r[0] * 26 * sg, p[1], r[2] + ax.r[2] * 26 * sg], ts = t + d * (.25 + i * .3);
      step(c, s, ts, p, to, d * .3, 14); key(id, 'footYaw' + s, ts, yaw, d * .3, 'inOut'); });
  }
  function step(c, s, t, from, to, d, lift) {
    const k = 'foot' + s;
    c.ch[k].key(t, [lerp(from[0], to[0], .5), from[1] - lift, lerp(from[2], to[2], .5)], d * .5, 'out');
    c.ch[k].key(t + d * .5, to, d * .5, 'in');
    c.ch['heelLift' + s].key(t, lift * .4, d * .3, 'out'); c.ch['heelLift' + s].key(t + d * .55, 0, d * .45, 'inOut');
  }
  // walk with planted feet from the current root to x1 (local px) over [a, b]; stride px; dir = yaw while walking
  function walk(id, a, b, x1, o = {}) {
    const c = chars[id], b0 = c.b, root0 = c.ch.root.at(a), x0 = root0[0], dist = x1 - x0;
    const dirYaw = o.yaw ?? (dist >= 0 ? 90 : -90), stride = o.stride || b0.thigh * .62;
    const nSteps = Math.max(2, Math.round(Math.abs(dist) / stride) + 1);
    const T = (b - a), per = T / nSteps;
    if (Math.abs(c.ch.yaw.at(a) - dirYaw) > 5) key(id, 'yaw', a - .25, dirYaw, .45, 'inOut');
    const ax = frameAxes(dirYaw), g = c.ground, y0 = root0[1];
    const lead = o.lead || (dist >= 0 ? 'R' : 'L');
    const stepLen = dist / (nSteps - .5);
    // pelvis: forward progress with a bob (high at mid-stance, low at heel strike) and a slight side sway
    for (let i = 0; i <= nSteps * 2; i++) {
      const tt = a + i * per / 2, p = clamp((tt - a) / T, 0, 1);
      const x = x0 + dist * EASE.sine(p) * 0 + dist * (p < .08 ? p * p / .16 / .92 : p > .92 ? 1 - (1 - p) * (1 - p) / .16 / .92 : (p - .04) / .92);
      const bob = (i % 2 === 0 ? 7 : -3) * (i === 0 || i === nSteps * 2 ? 0 : 1);
      key(id, 'root', tt, [x, y0 - bob, root0[2]], per / 2, 'sine');
    }
    key(id, 'lean', a, 7, .3, 'out'); key(id, 'lean', b - .2, 3, .4, 'inOut');
    // feet: alternate, each lifts on an arc and plants ahead of the pelvis
    let fx = { L: c.ch.footL.at(a)[0], R: c.ch.footR.at(a)[0] };
    for (let i = 0; i < nSteps; i++) {
      const s = (i % 2 === 0) ? lead : (lead === 'R' ? 'L' : 'R'), sg = s === 'R' ? 1 : -1;
      const last = i === nSteps - 1;
      const tx = last ? x1 + ax.r[0] * 24 * sg : x0 + stepLen * (i + 1) + ax.r[0] * 14 * sg;
      const ts = a + i * per;
      const from = c.ch['foot' + s].at(ts);
      // swing takes ~80% of a step: both feet are down briefly at every hand-over (double support)
      step(c, s, ts, from, [tx, g, root0[2] + ax.r[2] * 20 * sg], per * .8, 34);
      c.ch['footPitch' + s].key(ts, 18, per * .25, 'out'); c.ch['footPitch' + s].key(ts + per * .38, -10, per * .25, 'inOut'); c.ch['footPitch' + s].key(ts + per * .7, 0, per * .1, 'out');
      c.ch['footYaw' + s].key(ts, dirYaw, per * .4, 'inOut');
      fx[s] = tx;
      // opposite arm swings forward
      const os = s === 'R' ? 'L' : 'R';
      arm(id, os, ts, [(os === 'R' ? 1 : -1) * 16, b0.uarm + b0.farm - 52, 115], per, 'sine');
      arm(id, s, ts, [(s === 'R' ? 1 : -1) * 16, b0.uarm + b0.farm - 44, -85], per, 'sine');
    }
    ['L', 'R'].forEach(s => arm(id, s, b, [(s === 'R' ? 1 : -1) * 18, b0.uarm + b0.farm - 34, 22], .4));
    key(id, 'twist', a, 0, .2);
  }
  // sit onto a seat (local px point of the seat surface centre) facing yaw
  function sit(id, t, seat, d = 1.0, o = {}) {
    const c = chars[id], b0 = c.b, r0 = c.ch.root.at(t);
    key(id, 'lean', t, 24, d * .45, 'inOut');                              // weight forward first (anticipation)
    key(id, 'root', t + d * .2, [seat[0], seat[1] - 6, seat[2] ?? r0[2]], d * .7, 'inOut');
    key(id, 'lean', t + d * .6, o.lean ?? 6, d * .5, 'inOut');
    const ax = frameAxes(c.ch.yaw.at(t));
    ['L', 'R'].forEach(s => { const sg = s === 'R' ? 1 : -1, f = c.ch['foot' + s].at(t);
      const kneeFwd = b0.thigh * .92;
      key(id, 'foot' + s, t + d * .1, [seat[0] + ax.f[0] * kneeFwd + ax.r[0] * 30 * sg, f[1], (seat[2] ?? r0[2]) + ax.f[2] * kneeFwd + ax.r[2] * 30 * sg], d * .5, 'inOut'); });
    ['L', 'R'].forEach(s => arm(id, s, t + d * .4, [(s === 'R' ? 1 : -1) * 10, b0.uarm * 1.22, b0.farm * .78], d * .6));   // hands rest on the thighs
  }
  function stand(id, t, to, d = 1.0) {
    const c = chars[id], b0 = c.b, r0 = c.ch.root.at(t), g = c.ground;
    key(id, 'lean', t, 28, d * .4, 'inOut');
    const ax = frameAxes(c.ch.yaw.at(t));
    ['L', 'R'].forEach(s => { const sg = s === 'R' ? 1 : -1;
      key(id, 'foot' + s, t, [r0[0] + ax.f[0] * 40 + ax.r[0] * 26 * sg, g, r0[2] + ax.f[2] * 40 + ax.r[2] * 26 * sg], d * .3, 'inOut'); });
    key(id, 'root', t + d * .3, [to ? to[0] : r0[0] + ax.f[0] * 40, g - b0.ankle - b0.shin - b0.thigh + 2.5, r0[2]], d * .6, 'out');
    key(id, 'lean', t + d * .6, 4, d * .4, 'inOut');
    ['L', 'R'].forEach(s => arm(id, s, t + d * .5, [(s === 'R' ? 1 : -1) * 18, b0.uarm + b0.farm - 34, 22], d * .5));
  }
  const express = (id, t, e, d = .35) => { for (const k in e) key(id, k, t, e[k], d, 'inOut'); };
  const nod = (id, t, n = 2, amp = 9) => { for (let i = 0; i < n; i++) { key(id, 'headPitch', t + i * .32, amp, .16, 'out'); key(id, 'headPitch', t + i * .32 + .16, 0, .16, 'inOut'); } };
  // weight shift: one deliberate shift, not a loop
  function shift(id, t, toSide = 1, d = .8) { const c = chars[id], r = c.ch.root.at(t); key(id, 'root', t, [r[0] + toSide * 10, r[1] + 3, r[2]], d, 'inOut'); key(id, 'side', t, -toSide * 3, d, 'inOut'); }
  // attach a prop (element id, in the character's local space) to a hand during [a, b); `after` = transform once put down
  function hold(id, side, el, a, b, rot, after) {
    const e = document.getElementById(el); chars[id].props.push({ side, el, a, b, rot, after, rest: e ? e.getAttribute('transform') : null });
  }
  function place(id, t, x, z = 0) {          // set the standing position (both feet under the pelvis) instantly
    const c = chars[id], ax = frameAxes(c.ch.yaw.at(t)), r = c.ch.root.at(t);
    key(id, 'root', t, [x, r[1], z]);
    ['L', 'R'].forEach(s => { const sg = s === 'R' ? 1 : -1; key(id, 'foot' + s, t, [x + ax.r[0] * 26 * sg, c.ground, z + ax.r[2] * 26 * sg]); key(id, 'footYaw' + s, t, c.ch.yaw.at(t)); });
  }

  // Drive each character from the master timeline: one driver tween per character spans [0, end] and redraws it
  // in onUpdate at the tween's exact time. Drawing is a pure function of time, so call order does not matter; and a
  // real tween both survives renderers that drive GSAP their own way (HyperFrames) and marks the frames as animated
  // for renderers that skip frames without tween activity.
  function attach(tl) {
    if (tl.__r4) return; tl.__r4 = 1;
    for (const id in chars) {
      const c = chars[id]; let b = c.spec.t1 ?? 0;
      for (const n in c.ch) for (const k of c.ch[n].keys) b = Math.max(b, k.t + k.d + 1);
      for (const [, y] of c.speak) b = Math.max(b, y);
      for (const pr of c.props) b = Math.max(b, pr.b);
      if (c.blinkT.length) b = Math.max(b, c.blinkT[c.blinkT.length - 1][0] + .5);
      b = Math.max(b, tl.duration());
      tl.fromTo(c.el, { '--r4': 0 }, { '--r4': b, duration: b, ease: 'none', immediateRender: false,      // value = seconds, whatever the document length
        onUpdate() { draw(c, this.startTime() + this.time()); } }, 0);
    }
    drawAll(tl.time());
  }
  return { create, attach, draw: drawAll, key, val, look, reach, release, arm, turn, walk, sit, stand, express, nod, shift,
           hold, place, say, blinks, chars, EASE, _solve: solve };
})();
