// Epoch Ledger rig v3 motion library (pairs with kit/rig3.py). Opt-in head script; expects the master timeline `tl`.
// Joint groups carry SVG transforms "rotate(a cx cy)"; R3 tweens the angle exactly (GSAP attr interpolation), so
// pivots never drift and any frame can be seeked. All variety is seeded; no unseeded randomness.
// Poses come from Python (rig3.pose_angles) as {joint: deg}; pass them in R3.P = {...} at build time.
const R3 = {
  P: {},
  seed(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; },
  _piv(el) { const m = /rotate\(\s*([-\d.e]+)[\s,]+([-\d.e]+)[\s,]+([-\d.e]+)/.exec(el.getAttribute('transform') || ''); return m ? [m[2], m[3]] : null; },
  // rotate one joint to an absolute angle (deg) at time t
  rot(p, joint, t, deg, d, ease) {
    const el = document.getElementById(p + '-' + joint); if (!el) return; const pv = R3._piv(el); if (!pv) return;
    tl.to(el, { attr: { transform: `rotate(${(+deg).toFixed(2)} ${pv[0]} ${pv[1]})` }, duration: d === undefined ? .4 : d, ease: ease || 'sine.inOut' }, t);
  },
  // keyframed joint action: [[t, deg, dur, ease], ...] — build anticipation / action / follow-through explicitly
  keys(p, joint, ks) { ks.forEach(([t, deg, d, e]) => R3.rot(p, joint, t, deg, d, e)); },
  // eye direction: irises shift inside the eye whites (dx, dy in face px; ~±3 is a strong glance)
  look(p, t, dx, dy, d) { tl.to('#' + p + '-eyes .iris', { x: dx, y: dy || 0, duration: d === undefined ? .18 : d, ease: 'power2.out' }, t); },
  // writing / signing: small rhythmic forearm + hand strokes while the hand travels right
  write(p, a, b, base, seed) { const r = R3.seed(seed || 5); let t = a, k = 0;
    while (t < b - .06) { const d = .07 + r() * .05; R3.rot(p, 'farm-front', t, base + (k % 2 ? 5 : -4), d, 'sine.inOut'); t += d; k++; }
    R3.rot(p, 'farm-front', b, base, .12); },
  // blend to a named pose (or an angle dict); `only` limits the joints touched (e.g. ['uarm-front','farm-front'])
  pose(p, name, t, d, ease, only) {
    const q = typeof name === 'string' ? R3.P[name] : name; if (!q) return;
    Object.keys(q).forEach(j => { if (!only || only.indexOf(j) >= 0) R3.rot(p, j, t, q[j], d, ease || 'power2.inOut'); });
  },
  // natural blinks between a and b (irregular, 2-5 s apart); eyes group id: {p}-eyes (figures) or {p}-lids (close-ups)
  blinks(p, a, b, seed, origin) {
    const r = R3.seed(seed), el = document.getElementById(p + '-eyes') || document.getElementById(p + '-lids'); if (!el) return;
    for (let t = a + .3 + r() * 1.2; t < b - .2; t += 1.8 + r() * 2.8) R3.blink(p, t, origin, r() < .18);
  },
  blink(p, t, origin, dbl) {
    const el = document.getElementById(p + '-eyes') || document.getElementById(p + '-lids'); if (!el) return;
    const o = origin || '50% 50%';
    tl.to(el, { scaleY: .08, transformOrigin: o, duration: .07, ease: 'power1.in' }, t);
    tl.to(el, { scaleY: 1, transformOrigin: o, duration: .1, ease: 'power1.out' }, t + .07);
    if (dbl) { tl.to(el, { scaleY: .08, transformOrigin: o, duration: .06 }, t + .26); tl.to(el, { scaleY: 1, transformOrigin: o, duration: .09 }, t + .32); }
  },
  // breathing: slow chest rise on the upper body (and shoulders for close-ups); amplitude in px
  breathe(sel, a, b, amp, period) {
    const per = period || 3.6; for (let t = a; t < b - .1; t += per) tl.to(sel, { y: -(amp || 2), duration: per / 2, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t);
  },
  // talking mouth (scaleY flaps at speech rhythm)
  talk(p, a, b, seed) {
    const el = document.getElementById(p + '-mouth'); if (!el) return; const r = R3.seed(seed);
    for (let t = a; t < b - .12; t += .11 + r() * .12) tl.to(el, { scaleY: .35 + r() * .9, transformOrigin: '50% 50%', duration: .07, ease: 'none' }, t);
    tl.to(el, { scaleY: 1, transformOrigin: '50% 50%', duration: .1 }, b);
  },
  // typing: alternating forearm taps + small head nods, seeded rhythm
  type(p, a, b, seed) {
    const r = R3.seed(seed), base = R3.P.type || {}; let t = a, s = 1;
    while (t < b - .15) { const d = .09 + r() * .07;
      R3.rot(p, 'farm-front', t, (base['farm-front'] || -56) + 7 * s, d, 'sine.inOut');
      R3.rot(p, 'farm-back', t, (base['farm-back'] || -58) - 6 * s, d, 'sine.inOut');
      if (r() < .12) { R3.rot(p, 'neck', t, (base.neck || 6) + 4 + r() * 4, .5); t += .55; }
      t += d; s = -s; }
  },
  // idle weight shift + small head drift (secondary life for listeners)
  idle(p, a, b, seed, head0) {
    const r = R3.seed(seed); let t = a + r() * .6;
    while (t < b - .5) { const h = 1.4 + r() * 1.8; R3.rot(p, 'upper', t, (r() - .5) * 3, h * .8, 'sine.inOut'); R3.rot(p, 'neck', t + .2, (head0 || 0) + (r() - .5) * 8, .7, 'sine.inOut'); t += h; }
  },
  // walk a scene3d sprite (<svg id=..> placed by S3.render) between two 3D foot points: projects both ends with the
  // shot camera, tweens position + size (perspective scale), and cycles the legs/arms. period = one step (s).
  walk(cam, spriteId, p, foot0, foot1, height, aspect, a, b, period) {
    const el = document.getElementById(spriteId); if (!el) return;
    const box = (f) => { const q = cam.project(f), h = cam.project([f[0], f[1] + height, f[2]]); const hp = q[1] - h[1], wp = hp * aspect; return { x: q[0] - wp / 2, y: h[1], width: wp, height: hp }; };
    const A = box(foot0), B = box(foot1);
    tl.fromTo(el, { attr: A }, { attr: B, duration: b - a, ease: 'none', immediateRender: false }, a);
    const per = period || .5, W1 = R3.P.walk, W2 = R3.P.walk_l; let k = 0;
    for (let t = a; t < b - .05; t += per, k++) { R3.pose(p, k % 2 ? W2 : W1, t, per, 'sine.inOut', ['thigh-front', 'shin-front', 'thigh-back', 'shin-back', 'uarm-back', 'upper']);
      tl.to('#' + p + '-upper', { y: -5, duration: per / 2, ease: 'sine.out', yoyo: true, repeat: 1 }, t); }
    return A;     // the start box — tl.set(sprite, { attr: A }, shotStart) so the walker waits at its start mark
  },
};
