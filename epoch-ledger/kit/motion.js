// Epoch Ledger motion library (kit/motion.js) — reusable, deterministic helpers on the master timeline `tl`.
// Original implementation of general motion-design practice (see skills/creative/epoch-ledger-motion-craft.md).
// Every helper takes absolute film times (use W(word, line) from the episode timeline) and never reads the clock.
// Guidelines encoded as defaults are flexible: pass options to override any of them when the story needs it.

const MOTION = {
  // one easing family per role (series motion language; config/production.json → motion_language)
  ease: { enter: 'expo.out', exit: 'power3.in', move: 'sine.inOut', settle: 'power3.out', camera: 'sine.inOut', data: 'power2.out' },
  dur: { quick: .25, base: .45, slow: .8, hero: 1.6 },
  stagger: { line: .08, word: .055, char: .028, item: .06, grid: .025 },
  groupCap: .9,   // a group reveal should usually settle within ~0.9 s (flexible)
  hold: { chart: 2.0, read: 1.0 },  // guideline holds (flexible)
};

function mSeed(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function mEls(sel) { return typeof sel === 'string' ? Array.from(document.querySelectorAll(sel)) : (Array.isArray(sel) ? sel : [sel]).filter(Boolean); }
function mStaggerFor(n, each, cap) { return n > 1 && each * (n - 1) > cap ? cap / (n - 1) : each; }

// ── kinetic typography ────────────────────────────────────────────────────────────────────────
// Split an element's text into masked pieces (by 'word' | 'char' | 'line'; lines = explicit '|' or <br>).
// Pre-split markup from kit/motion.py (ktext) is reused as-is, so line breaks never depend on font timing.
function mSplit(el, by) {
  if (el.querySelector('.kp')) return Array.from(el.querySelectorAll('.kp > .ki'));
  const text = el.textContent;
  const parts = by === 'char' ? Array.from(text) : by === 'line' ? text.split('|') : text.split(/(\s+)/);
  el.textContent = '';
  const out = [];
  parts.forEach(p => {
    if (/^\s+$/.test(p)) { el.appendChild(document.createTextNode(p)); return; }
    const mask = document.createElement('span'); mask.className = 'kp';
    mask.style.cssText = 'display:inline-block;overflow:hidden;vertical-align:bottom' + (by === 'line' ? ';display:block' : '');
    const inner = document.createElement('span'); inner.className = 'ki'; inner.style.display = 'inline-block'; inner.textContent = p === ' ' ? ' ' : p;
    mask.appendChild(inner); el.appendChild(mask); out.push(inner);
  });
  return out;
}
// Reveal text at t. style: 'mask' (wipe up from a hidden baseline), 'fade', 'blur' (costlier), 'wipe' (clip, glyphs still).
function mReveal(sel, t, o) {
  o = o || {}; const by = o.by || 'word', style = o.style || 'mask';
  mEls(sel).forEach(el => {
    gsap.set(el, { opacity: 1 });
    if (style === 'wipe') { tl.fromTo(el, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: o.dur || MOTION.dur.slow, ease: o.ease || MOTION.ease.enter }, t); return; }
    const pieces = mSplit(el, by), each = mStaggerFor(pieces.length, o.stagger || MOTION.stagger[by] || .05, o.cap || MOTION.groupCap);
    const from = style === 'mask' ? { yPercent: o.dir === 'down' ? -105 : 105 } : style === 'blur' ? { opacity: 0, filter: 'blur(10px)' } : { opacity: 0, y: 14 };
    const to = style === 'mask' ? { yPercent: 0 } : style === 'blur' ? { opacity: 1, filter: 'blur(0px)' } : { opacity: 1, y: 0 };
    tl.fromTo(pieces, from, Object.assign(to, { duration: o.dur || MOTION.dur.base, ease: o.ease || MOTION.ease.enter, stagger: each }), t);
  });
}
function mUnreveal(sel, t, o) {
  o = o || {}; mEls(sel).forEach(el => { const pieces = el.querySelectorAll('.ki');
    tl.to(pieces.length ? pieces : el, { yPercent: pieces.length ? -105 : 0, opacity: pieces.length ? 1 : 0, duration: o.dur || MOTION.dur.quick, ease: MOTION.ease.exit, stagger: pieces.length ? .02 : 0 }, t); });
}
// Narration-locked kinetic type: word i appears exactly at times[i] (pass W() times of the spoken words).
function mWordsAt(sel, times, o) {
  o = o || {}; const el = mEls(sel)[0]; if (!el) return; gsap.set(el, { opacity: 1 });
  const pieces = mSplit(el, 'word');
  pieces.forEach((p, i) => { const t = times[Math.min(i, times.length - 1)];
    tl.fromTo(p, { yPercent: 105, opacity: o.fade ? 0 : 1 }, { yPercent: 0, opacity: 1, duration: o.dur || .3, ease: MOTION.ease.enter }, t);
    if (o.emphasis && o.emphasis.includes(i)) tl.fromTo(p, { color: 'inherit' }, { color: o.emphasisColor || '#f2c66d', duration: .2 }, t + .1); });
}

// ── drawing: blueprint / hand-drawn / diagrams ────────────────────────────────────────────────
// Stroke draw-on in document order; fills fade in after their outline. Works for paths, lines, polylines, circles, rects.
function mDrawOn(sel, t, o) {
  o = o || {}; const els = mEls(sel), each = o.stagger === undefined ? .12 : o.stagger, dur = o.dur || MOTION.dur.slow;
  els.forEach((el, i) => {
    const n = el.getTotalLength ? el.getTotalLength() : 1000, fill = el.getAttribute('fill'), fo = o.fillAfter && fill && fill !== 'none';
    gsap.set(el, { strokeDasharray: n, strokeDashoffset: n }); if (fo) gsap.set(el, { fillOpacity: 0 });
    tl.to(el, { strokeDashoffset: 0, duration: dur, ease: o.ease || 'power1.inOut' }, t + i * each);
    if (fo) tl.to(el, { fillOpacity: 1, duration: .35 }, t + i * each + dur * .8);
  });
  return t + (els.length - 1) * each + dur;
}
// "Boiling" line for a hand-drawn look: swaps between pre-drawn variants every `every` frames (never per-frame jitter).
function mBoil(sel, t0, t1, o) {
  o = o || {}; const groups = mEls(sel), fps = o.fps || 30, every = o.every || 4, step = every / fps;
  let k = 0; for (let t = t0; t < t1; t += step, k++) groups.forEach((g, i) => tl.set(g, { opacity: (k % groups.length) === i ? 1 : 0 }, t));
}
// Diagram build: nodes → edges → labels, each at its own (narration) time.
function mDiagram(spec) {
  (spec.nodes || []).forEach(([sel, t]) => tl.fromTo(sel, { opacity: 0, scale: .86, transformOrigin: '50% 50%' }, { opacity: 1, scale: 1, duration: MOTION.dur.base, ease: MOTION.ease.settle }, t));
  (spec.edges || []).forEach(([sel, t]) => { mEls(sel).forEach(e => gsap.set(e, { opacity: 1 })); mDrawOn(sel, t, { dur: .5, stagger: 0 }); });
  (spec.labels || []).forEach(([sel, t]) => tl.fromTo(sel, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: MOTION.dur.quick, ease: MOTION.ease.enter }, t));
}
// Focus + context: light the active element(s), dim the rest; mUnfocus restores.
function mFocus(active, context, t, o) {
  o = o || {}; tl.to(context, { opacity: o.dim === undefined ? .28 : o.dim, filter: o.desat === false ? 'none' : 'saturate(.4)', duration: .35, ease: MOTION.ease.move }, t);
  tl.to(active, { opacity: 1, filter: 'saturate(1)', duration: .35, ease: MOTION.ease.move }, t);
}
function mUnfocus(context, t) { tl.to(context, { opacity: 1, filter: 'saturate(1)', duration: .35, ease: MOTION.ease.move }, t); }
// Flow along a connector: marching dash + travelling dots (data, money, power, goods). Speed in px/s.
function mFlow(pathSel, t0, t1, o) {
  o = o || {}; const p = mEls(pathSel)[0]; if (!p) return; const n = p.getTotalLength(), speed = o.speed || 220, dur = t1 - t0;
  if (o.dash !== false) { gsap.set(p, { strokeDasharray: o.pattern || '14 12' }); tl.fromTo(p, { strokeDashoffset: 0 }, { strokeDashoffset: -(speed * dur) * (o.reverse ? -1 : 1), duration: dur, ease: 'none' }, t0); }
  const k = o.dots || 0; if (!k) return; const svg = p.ownerSVGElement, NS = 'http://www.w3.org/2000/svg';
  for (let i = 0; i < k; i++) {
    const c = document.createElementNS(NS, 'circle'); c.setAttribute('r', o.r || 7); c.setAttribute('fill', o.color || '#9ff3ff'); c.setAttribute('opacity', 0); svg.appendChild(c);
    const st = { u: 0 }; const off = i / k;
    tl.set(c, { attr: { opacity: 1 } }, t0 + off * Math.min(1, dur));
    tl.fromTo(st, { u: 0 }, { u: dur * speed / n, duration: dur, ease: 'none', onUpdate: () => { let f = (st.u + off) % 1; if (o.reverse) f = 1 - f; const q = p.getPointAtLength(f * n); c.setAttribute('cx', q.x); c.setAttribute('cy', q.y); } }, t0);
    tl.set(c, { attr: { opacity: 0 } }, t1);
  }
}

// ── data ──────────────────────────────────────────────────────────────────────────────────────
// Counter that settles on the exact value; Intl formatting and tabular figures (no jittering digit widths).
function mCount(sel, from, to, t, dur, o) {
  o = o || {}; const el = mEls(sel)[0]; if (!el) return; el.style.fontVariantNumeric = 'tabular-nums';
  const fmt = new Intl.NumberFormat(o.locale || 'en-US', o.format || { maximumFractionDigits: 0 }), st = { v: from };
  const put = () => { el.textContent = (o.prefix || '') + fmt.format(st.v) + (o.suffix || ''); };
  tl.fromTo(st, { v: from }, { v: to, duration: dur, ease: o.ease || MOTION.ease.data, onUpdate: put, onComplete: () => { st.v = to; put(); } }, t);
  put();
}
// Grow SVG bars (rects) from a baseline to value heights; values in data units, scale = px per unit.
function mBars(sel, values, t, o) {
  o = o || {}; const els = mEls(sel), base = o.baseline, each = mStaggerFor(els.length, o.stagger || MOTION.stagger.item, o.cap || MOTION.groupCap);
  els.forEach((el, i) => { const h = Math.abs(values[i]) * o.scale, y0 = base !== undefined ? base : (+el.getAttribute('y') + +el.getAttribute('height'));
    gsap.set(el, { attr: { y: y0, height: 0 } });
    tl.to(el, { attr: { y: values[i] >= 0 ? y0 - h : y0, height: h }, duration: o.dur || MOTION.dur.slow, ease: MOTION.ease.data }, t + i * each); });
}
function mLine(sel, t, dur, o) { return mDrawOn(sel, t, Object.assign({ dur: dur || 1.2, stagger: 0, ease: 'none' }, o || {})); }

// ── environment and camera ────────────────────────────────────────────────────────────────────
// Subtle, non-repeating environmental life between t0 and t1: drift, breathing scale, rotation, light flicker.
function mAmbient(sel, t0, t1, o) {
  o = o || {}; mEls(sel).forEach((el, i) => {
    const r = mSeed((o.seed || 7) * 131 + i); let t = t0;
    while (t < t1 - .2) { const d = Math.min(t1 - t, (o.period || 3.2) * (.7 + r() * .6));
      const to = { duration: d, ease: 'sine.inOut' };
      if (o.drift) { to.x = (r() - .5) * 2 * o.drift[0]; to.y = (r() - .5) * 2 * o.drift[1]; }
      if (o.scale) to.scale = 1 + (r() - .5) * 2 * o.scale;
      if (o.rotate) to.rotation = (r() - .5) * 2 * o.rotate;
      if (o.flicker) to.opacity = 1 - r() * o.flicker;
      tl.to(el, to, t); t += d; }
  });
}
// One camera move across depth layers: layers = [[selector, depthFactor], …] (1 = full move, 0 = fixed background).
function mParallax(layers, t0, t1, o) {
  o = o || {}; layers.forEach(([sel, f]) => tl.fromTo(sel, { x: 0, y: 0, scale: 1 }, { x: (o.dx || -60) * f, y: (o.dy || 0) * f, scale: 1 + (o.dolly || 0) * f, duration: t1 - t0, ease: o.ease || MOTION.ease.camera }, t0));
}
function mPush(sel, t0, t1, o) {
  o = o || {}; tl.fromTo(sel, { scale: o.from || 1, x: o.x0 || 0, y: o.y0 || 0, transformOrigin: o.origin || '50% 50%' }, { scale: o.to || 1.08, x: o.x1 || 0, y: o.y1 || 0, duration: t1 - t0, ease: o.ease || MOTION.ease.camera }, t0);
}
// Editorial "stutter": a stepped tween (default 12 fps) for map overlays, routes and annotations.
function mStutter(sel, vars, t, dur, fps) { const steps = Math.max(1, Math.round(dur * (fps || 12))); tl.to(sel, Object.assign({}, vars, { duration: dur, ease: 'steps(' + steps + ')' }), t); }

// ── 2D world camera ───────────────────────────────────────────────────────────────────────────
// A large illustrated world (e.g. 3840×2160) filmed through the 1920×1080 frame. keys = [[t, x, y, s, move?], …]:
// at time t the view's top-left is world (x, y) at scale s; the move into a key takes `move` s (default 1.2) and
// ends on t (so start ~1 s before the word that names the subject). Between moves the camera keeps breathing
// (o.drift = slow push). o.layers = [[selector, depth]] — depth < 1 moves slower (distant skyline), > 1 faster;
// layers sit exactly as authored when the view is centred on o.ref (default: world centre, o.worldW × o.worldH).
function mCamera(world, keys, o) {
  o = o || {}; const W = o.w || 1920, H = o.h || 1080, P = { x: keys[0][1], y: keys[0][2], s: keys[0][3] };
  const wEl = mEls(world)[0], layers = (o.layers || []).map(([sel, d]) => [mEls(sel), d]);
  const apply = () => { gsap.set(wEl, { x: -P.x * P.s, y: -P.y * P.s, scale: P.s, transformOrigin: '0 0' });
    const rx = o.ref ? o.ref[0] : (o.worldW || 3840) / 2, ry = o.ref ? o.ref[1] : (o.worldH || 2160) / 2;   // layers sit as authored when the view is centred on ref
    layers.forEach(([els, d]) => gsap.set(els, { x: (P.x + W / P.s / 2 - rx) * (1 - d), y: (P.y + H / P.s / 2 - ry) * (1 - d) * .5 })); };
  apply();
  const drift = o.drift === undefined ? .025 : o.drift;
  keys.forEach((k, i) => {
    const [t, x, y, s, mv] = k, move = i ? (mv || 1.2) : 0;
    if (i) tl.to(P, { x, y, s, duration: move, ease: o.ease || MOTION.ease.camera, onUpdate: apply }, t - move);
    const next = keys[i + 1], holdEnd = next ? next[0] - (next[4] || 1.2) : (o.end || t + 3);
    if (drift && holdEnd - t > .3) {                     // breathing push toward the frame centre during the hold
      const cx = x + W / s / 2, cy = y + H / s / 2, s2 = s * (1 + drift);
      tl.to(P, { x: cx - W / s2 / 2, y: cy - H / s2 / 2, s: s2, duration: holdEnd - t, ease: 'sine.inOut', onUpdate: apply }, t);
    }
  });
  return P;
}

// ── series end screen (no logo intro; live film background continues) ─────────────────────────
function mEndScreen(px, t, o) {
  o = o || {}; tl.fromTo('#' + px, { opacity: 0 }, { opacity: 1, duration: .6, ease: MOTION.ease.move }, t);
  tl.fromTo('#' + px + ' .es-slot', { opacity: 0, scale: .96 }, { opacity: 1, scale: 1, duration: .5, ease: MOTION.ease.enter, stagger: .12 }, t + .3);
  mReveal('#' + px + ' .es-line', t + .2, { by: 'word' });
  if (o.ambient !== false) mAmbient('#' + px + ' .es-bg', t, t + (o.dur || 20), { drift: [12, 6], scale: .02, period: 5, seed: 11 });
}
