// Epoch Ledger rig v2 motion library (pairs with kit/rig.py). Expects the master timeline `tl`.
// Deterministic: all variety comes from seeded generators, never Math.random().
const RIG_PIV = { neck: '150 182', sh: '150 204', el: '150 262', hip: '150 330', kn: '150 400' };
// Joint angles in degrees. Characters face +x; negative upper-arm angles swing the arm forward/up.
const RIG_POSES = {
  neutral: { uf: 0, ff: 0, ub: 0, fb: 0, head: 0, torso: 0 },
  phone:   { uf: -70, ff: -155, ub: 6, fb: -10, head: -5, torso: -2 },
  write:   { uf: -42, ff: -78, ub: -34, fb: -84, head: 8, torso: 3 },
  type:    { uf: -46, ff: -52, ub: -40, fb: -58, head: 5, torso: 4 },
  point:   { uf: -125, ff: -15, ub: 8, fb: -12, head: -9, torso: -3 },
  signal:  { uf: -96, ff: -38, ub: 4, fb: -10, head: -4, torso: -2 },
  shout:   { uf: -128, ff: -22, ub: -112, fb: -30, head: -12, torso: -4 },
  cheer:   { uf: -156, ff: -10, ub: -148, fb: -12, head: -10, torso: -3 },
  handsHead: { uf: -168, ff: -118, ub: -160, fb: -122, head: 7, torso: 5 },
  slump:   { uf: 6, ff: -6, ub: 6, fb: -6, head: 16, torso: 7 },
  shrug:   { uf: -12, ff: -96, ub: 10, fb: -92, head: -6, torso: 0 },
  hold:    { uf: -30, ff: -64, ub: 4, fb: -8, head: 4, torso: 1 },
};
function rigSeed(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function rpose(p, name, t, d, ease) {
  const q = RIG_POSES[name] || name, e = ease || 'power2.inOut', D = d === undefined ? .35 : d;
  const J = [['uarm-front', 'uf', 'sh'], ['farm-front', 'ff', 'el'], ['uarm-back', 'ub', 'sh'], ['farm-back', 'fb', 'el'], ['head', 'head', 'neck'], ['upper', 'torso', 'hip']];
  J.forEach(([part, k, piv]) => { if (q[k] === undefined) return; const el = document.getElementById(p + '-' + part); if (el) tl.to(el, { rotation: q[k], svgOrigin: RIG_PIV[piv], duration: D, ease: e }, t); });
}
// Natural walk: hip swing, knee flex on the passing leg, counter-swinging arms with bent elbows, body bob.
function rwalk(p, wrap, start, steps, stepDur, dx) {
  if (wrap) tl.fromTo(wrap, { x: 0 }, { x: dx, duration: stepDur * steps, ease: 'none' }, start);
  for (let i = 0; i < steps; i++) {
    const t = start + i * stepDur, s = i % 2 ? -1 : 1;
    [['front', s], ['back', -s]].forEach(([side, d]) => {
      tl.to('#' + p + '-thigh-' + side, { rotation: 24 * d * -1, svgOrigin: RIG_PIV.hip, duration: stepDur, ease: 'sine.inOut' }, t);
      tl.to('#' + p + '-shin-' + side, { rotation: d > 0 ? 34 : 4, svgOrigin: RIG_PIV.kn, duration: stepDur / 2, ease: 'sine.out', yoyo: true, repeat: 1 }, t);
      tl.to('#' + p + '-uarm-' + side, { rotation: 20 * d, svgOrigin: RIG_PIV.sh, duration: stepDur, ease: 'sine.inOut' }, t);
      tl.to('#' + p + '-farm-' + side, { rotation: -18 - 10 * Math.max(0, -d), svgOrigin: RIG_PIV.el, duration: stepDur, ease: 'sine.inOut' }, t);
    });
    tl.to('#' + p + '-upper', { y: -6, duration: stepDur / 2, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t);
    tl.to('#' + p + '-head', { rotation: s * 1.5, svgOrigin: RIG_PIV.neck, duration: stepDur, ease: 'sine.inOut' }, t);
  }
  const end = start + steps * stepDur;
  ['thigh-front', 'thigh-back'].forEach(j => tl.to('#' + p + '-' + j, { rotation: 0, svgOrigin: RIG_PIV.hip, duration: .3 }, end));
  ['shin-front', 'shin-back'].forEach(j => tl.to('#' + p + '-' + j, { rotation: 0, svgOrigin: RIG_PIV.kn, duration: .3 }, end));
  return end + .3;
}
// Seeded ambient acting between start and end: picks poses from `set`, holds them for varied times,
// adds weight shifts, head turns, blinks and talking — no two characters (or seconds) repeat.
function ambient(p, start, end, seed, set, opts) {
  const r = rigSeed(seed), o = opts || {};
  let t = start + r() * .5;
  while (t < end - .3) {
    const name = set[Math.floor(r() * set.length)], d = .22 + r() * .25, hold = .5 + r() * 1.3;
    rpose(p, name, t, d);
    if (name === 'phone' || name === 'shout' || o.talk) rtalk(p, t + d, Math.min(end, t + d + hold), seed + Math.floor(t * 10));
    if (name === 'type' || name === 'write') tl.to('#' + p + '-farm-front', { rotation: '+=6', svgOrigin: RIG_PIV.el, duration: .09, yoyo: true, repeat: Math.max(1, Math.floor(hold / .18)) * 2 - 1, ease: 'none' }, t + d);
    tl.to('#' + p + '-upper', { x: (r() - .5) * 8, duration: hold * .8, ease: 'sine.inOut' }, t + d);
    t += d + hold;
  }
  for (let b = start + .4 + r() * 1.5; b < end; b += 1.6 + r() * 2.4) tl.to('#' + p + ' .lid', { scaleY: 1, duration: .06, yoyo: true, repeat: 1, ease: 'none' }, b);
}
function rtalk(p, a, b, seed) {
  const r = rigSeed(seed); for (let t = a; t < b - .1; t += .1 + r() * .14) tl.to('#' + p + '-open', { opacity: r() < .6 ? 1 : 0, duration: .05, ease: 'none' }, t);
  tl.to('#' + p + '-open', { opacity: 0, duration: .05 }, b);
}
function rexpress(p, kind, t) {  // brows + mouth: 'worry' | 'shock' | 'joy' | 'calm'
  const br = { worry: { y: -5, rotation: 0 }, shock: { y: -9 }, joy: { y: -3 }, calm: { y: 0 } }[kind];
  tl.to('#' + p + '-brows', Object.assign({ duration: .25 }, br), t);
  tl.to('#' + p + '-open', { opacity: kind === 'shock' ? 1 : 0, duration: .2 }, t);
  tl.to('#' + p + '-mouth', { scaleY: kind === 'worry' ? -1 : 1, transformOrigin: '50% 50%', duration: .25 }, t);
}
