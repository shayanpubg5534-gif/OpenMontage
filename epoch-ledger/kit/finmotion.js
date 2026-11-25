// Epoch Ledger financial-mechanism motion (pairs with kit/finmech.py). Opt-in head script; uses the master timeline `tl`.
// Every effect is a pure function of timeline time (seekable, deterministic): money flows, drops, tank levels,
// valves, gauges, lamps, CRT power-on and prop pops. Craft rules: anticipation before big actions, settle without
// overshoot on financial values, follow-through on props.
const FM = {
  NS: 'http://www.w3.org/2000/svg',
  _el(id) { return typeof id === 'string' ? document.getElementById(id.replace(/^#/, '')) : id; },
  _coin(layer, r, uid) {
    const g = document.createElementNS(FM.NS, 'g'); g.setAttribute('opacity', '0');
    g.innerHTML = `<ellipse rx="${r}" ry="${r}" fill="url(#${uid}-coin)" stroke="#7a5214" stroke-width="${Math.max(1.2, r * .16)}"/><ellipse rx="${r * .55}" ry="${r * .55}" fill="none" stroke="#fff3c0" stroke-width="${Math.max(1, r * .1)}" opacity=".7"/>`;
    layer.appendChild(g); return g;
  },
  // Coins travelling along a pipe: spawn `rate` per second between t0 and t1, move at `speed` px/s along {pipe}-path.
  // o: {r, speed, rate, spin, fadeIn, tail(s after t1 to keep moving), coinUid}
  coins(pipe, t0, t1, o) {
    o = o || {}; const path = FM._el(pipe + '-path'), layer = FM._el(pipe + '-coins'); if (!path || !layer) return;
    const L = path.getTotalLength(), speed = o.speed || 520, rate = o.rate || 8, r = o.r || 13, life = L / speed;
    const n = Math.max(1, Math.round((t1 - t0) * rate)), uid = o.coinUid || pipe, coins = [];
    for (let k = 0; k < n; k++) coins.push(FM._coin(layer, r, uid));
    const P = { t: t0 }, end = t1 + life;
    const upd = () => { for (let k = 0; k < n; k++) { const s = t0 + k / rate, age = P.t - s, c = coins[k];
        if (age < 0 || age > life) { c.setAttribute('opacity', '0'); continue; }
        const q = path.getPointAtLength(Math.min(L, age * speed)), wob = ((k * 37) % 11 - 5) * r * .12, spin = Math.abs(Math.cos(age * (o.spin || 9) + k));
        c.setAttribute('transform', `translate(${q.x.toFixed(1)} ${(q.y + wob).toFixed(1)}) scale(${(.35 + .65 * spin).toFixed(3)} 1)`);
        c.setAttribute('opacity', Math.min(1, age * 12, (life - age) * 12).toFixed(2)); } };
    tl.fromTo(P, { t: t0 }, { t: end, duration: end - t0, ease: 'none', onUpdate: upd, immediateRender: false }, t0);
  },
  // Coins dropping under gravity from `from` to `to` (screen points), staggered; optional `land` callback id to pop on arrival.
  drop(layerId, from, to, t, o) {
    o = o || {}; const layer = FM._el(layerId), n = o.n || 6, dur = o.dur || .55, r = o.r || 12, spread = o.spread || 26, uid = o.coinUid || 'fm';
    const coins = Array.from({ length: n }, () => FM._coin(layer, r, uid)), P = { t: 0 }, gap = o.gap === undefined ? .06 : o.gap;
    const upd = () => coins.forEach((c, k) => { const a = (P.t - k * gap) / dur; if (a < 0 || a > 1) { c.setAttribute('opacity', a > 1 && o.stay ? '1' : '0'); if (!(a > 1 && o.stay)) return; }
      const u = Math.min(1, a), dx = ((k * 53) % 7 - 3) / 3 * spread, x = from[0] + (to[0] + dx - from[0]) * u, y = from[1] + (to[1] - from[1]) * u * u - (o.arc || 0) * Math.sin(Math.PI * u);
      c.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${(.45 + .55 * Math.abs(Math.cos(u * 9 + k))).toFixed(3)} 1)`); c.setAttribute('opacity', u >= 1 && !o.stay ? '0' : '1'); });
    tl.fromTo(P, { t: 0 }, { t: dur + n * gap, duration: dur + n * gap, ease: 'none', onUpdate: upd, immediateRender: false }, t);
  },
  // Tank level (0..1) — the fill slides; data-inner on {tank}-fill gives the glass height. Financial value: no overshoot.
  level(tank, t, dur, to, ease) {
    const fill = FM._el(tank + '-fill'), wrap = FM._el(tank + '-fillwrap'); if (!fill || !wrap) return; const H = +fill.dataset.inner;
    tl.to(wrap, { attr: { transform: `translate(0 ${((1 - to) * H).toFixed(1)})` }, duration: dur, ease: ease || 'sine.inOut' }, t);
  },
  setLevel(tank, v) { const fill = FM._el(tank + '-fill'), wrap = FM._el(tank + '-fillwrap'); wrap.setAttribute('transform', `translate(0 ${((1 - v) * +fill.dataset.inner).toFixed(1)})`); },
  // Hand wheel: anticipation (small back-turn), the turn, a settle. turns in degrees.
  valve(id, t, deg, o) { o = o || {}; const el = FM._el(id); if (!el) return; const c = el.querySelector('circle'); const cx = c.getAttribute('cx'), cy = c.getAttribute('cy');
    tl.to(el, { rotation: -(o.anti || 14) * Math.sign(deg), svgOrigin: `${cx} ${cy}`, duration: .14, ease: 'power2.out' }, t);
    tl.to(el, { rotation: deg, svgOrigin: `${cx} ${cy}`, duration: o.dur || .7, ease: 'power3.inOut' }, t + .14);
    tl.to(el, { rotation: deg - 6 * Math.sign(deg), svgOrigin: `${cx} ${cy}`, duration: .18, ease: 'sine.out' }, t + .14 + (o.dur || .7)); },
  // Needle sweep to a fraction (0 empty .. 1 full) about its pivot, with a damped wobble (mechanical follow-through).
  needle(id, cx, cy, t, dur, frac, o) { o = o || {}; const el = FM._el(id), base = o.base === undefined ? -90 : o.base, span = o.span || 180, a = base + span * frac;
    tl.to(el, { attr: { transform: `rotate(${a.toFixed(1)} ${cx} ${cy})` }, duration: dur, ease: o.ease || 'power2.inOut' }, t);
    if (o.wobble !== false) [5, -3, 1.5, 0].forEach((w, k) => tl.to(el, { attr: { transform: `rotate(${(a + w).toFixed(1)} ${cx} ${cy})` }, duration: .09, ease: 'sine.inOut' }, t + dur + k * .09)); },
  // Warning lamp blinking between a and b.
  lamp(id, a, b, period) { const p = period || .42; for (let t = a; t < b - .05; t += p) tl.fromTo(FM._el(id), { opacity: 1 }, { opacity: .1, duration: p * .5, ease: 'steps(1)', immediateRender: false }, t); },
  // CRT power-on: bright line opens vertically into the picture.
  powerOn(uid, t) {
    tl.fromTo('#' + uid + '-line', { opacity: 0, scaleX: .05, transformOrigin: '50% 50%' }, { opacity: 1, scaleX: 1, duration: .12, ease: 'power2.out', immediateRender: false }, t);
    tl.to('#' + uid + '-line', { scaleY: 40, opacity: 0, transformOrigin: '50% 50%', duration: .2, ease: 'power2.in' }, t + .12);
    tl.fromTo('#' + uid + '-ad', { opacity: 0 }, { opacity: 1, duration: .14, immediateRender: false }, t + .16);
  },
  // Prop pop-in with anticipation + overshoot + settle (for objects, not financial values).
  pop(sel, t, o) { o = o || {}; tl.fromTo(sel, { scale: 0, opacity: 0, transformOrigin: o.origin || '50% 100%' }, { scale: 1.14, opacity: 1, duration: .18, ease: 'power2.out', immediateRender: false }, t);
    tl.to(sel, { scale: .96, duration: .1, ease: 'sine.inOut' }, t + .18); tl.to(sel, { scale: 1, duration: .12, ease: 'sine.out' }, t + .28); },
  // Hard-edged label stamp (anticipation from big, slam, small shake).
  stampIn(sel, t) { tl.fromTo(sel, { scale: 2.2, opacity: 0, rotation: -14, transformOrigin: '50% 50%' }, { scale: 1, opacity: 1, rotation: -8, duration: .16, ease: 'power3.in', immediateRender: false }, t);
    tl.to(sel, { x: 3, duration: .04, yoyo: true, repeat: 3, ease: 'none' }, t + .16); },
  // Banknotes flying from `from` to `to` (screen points) on arcs, fluttering (rotation + edge-on flips), staggered.
  // Needs money.bill_defs(defsUid) in the SVG. o: {n, dur, arc, gap, size, spread, land: selector to pop on arrival}
  bills(layerId, defsUid, from, to, t, o) {
    o = o || {}; const layer = FM._el(layerId), n = o.n || 6, dur = o.dur || .7, arc = o.arc === undefined ? 160 : o.arc, gap = o.gap || .07, sz = o.size || 1, spread = o.spread || 30;
    const els = Array.from({ length: n }, (_, k) => { const u = document.createElementNS(FM.NS, 'use'); u.setAttribute('href', '#' + defsUid + '-bill'); u.setAttribute('width', 120 * sz); u.setAttribute('height', 52 * sz);
      u.setAttribute('x', -60 * sz); u.setAttribute('y', -26 * sz); const g = document.createElementNS(FM.NS, 'g'); g.setAttribute('opacity', '0'); g.appendChild(u); layer.appendChild(g); return g; });
    const P = { t: 0 }, total = dur + gap * n;
    const upd = () => els.forEach((g, k) => { const a = (P.t - k * gap) / dur; if (a < 0 || a > 1) { g.setAttribute('opacity', '0'); return; }
      const e = a < .5 ? 2 * a * a : 1 - Math.pow(-2 * a + 2, 2) / 2, j = ((k * 37) % 9 - 4) / 4 * spread;
      const x = from[0] + (to[0] - from[0]) * e + j * Math.sin(a * Math.PI), y = from[1] + (to[1] - from[1]) * e - arc * Math.sin(Math.PI * a) + j * .4;
      const rot = Math.sin(a * 9 + k) * 28, flip = .35 + .65 * Math.abs(Math.cos(a * 7 + k * 1.7));
      g.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot.toFixed(1)}) scale(1 ${flip.toFixed(3)})`);
      g.setAttribute('opacity', Math.min(1, a * 10, (1 - a) * 8).toFixed(2)); });
    tl.fromTo(P, { t: 0 }, { t: total, duration: total, ease: 'none', onUpdate: upd, immediateRender: false }, t);
    if (o.land) FM.pop(o.land, t + dur * .9, { origin: '50% 100%' });
  },
  // Cash pile (money.cash_pile): show exactly n bundles. Removed bundles lift and fade (top/front first); added ones drop in.
  pileTo(uid, t, n, o) {
    o = o || {}; const cap = +FM._el(uid).dataset.cap, cur = FM._pile[uid] === undefined ? +FM._el(uid).dataset.n : FM._pile[uid]; FM._pile[uid] = n;
    for (let k = 0; k < cap; k++) { const el = FM._el(uid + '-bd' + k);
      if (k >= n && k < cur) tl.fromTo(el, { opacity: 1, y: 0 }, { opacity: 0, y: -40, duration: .28, ease: 'power2.in', immediateRender: false }, t + (cur - 1 - k) * (o.gap || .06));
      if (k < n && k >= cur) tl.fromTo(el, { opacity: 0, y: -90 }, { opacity: 1, y: 0, duration: .3, ease: 'power2.in', immediateRender: false }, t + (k - cur) * (o.gap || .05)); }
  },
  _pile: {},
  // A money counter that changes in steps over a shot: keys [[t, value, dur], ...]; start value shown from the first frame.
  // fmt(v) → text (default "$<v>M"). One proxy per element, so successive changes chain correctly when seeking.
  count(sel, start, keys, fmt) {
    const el = document.querySelector(sel); if (!el) return; const f = fmt || (v => '$' + Math.round(v) + 'M'), P = { v: start };
    el.style.fontVariantNumeric = 'tabular-nums'; el.textContent = f(start);
    tl.set(P, { v: start, onComplete: () => { el.textContent = f(start); } }, 0);
    keys.forEach(([t, v, d]) => tl.to(P, { v, duration: d || .5, ease: 'power2.out', onUpdate: () => { el.textContent = f(P.v); } }, t));
  },
};
