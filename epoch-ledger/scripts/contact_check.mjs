#!/usr/bin/env node
// Epoch Ledger contact check: for every frame of every contact (a hand holding a prop), measures whether the hand is
// on the prop, whether the prop hides the whole hand, and whether the prop jumps between consecutive frames.
// Works on Rig v4 compositions today (wrist joints from R4.chars, mapped to the screen through the character's
// SVG transform); the 3D character layer will report the same quantities from bone sockets. DOM measurement of the
// built composition, every frame at the composition's frame rate: no rendering. Original implementation.
//
//   node epoch-ledger/scripts/contact_check.mjs <workspace>/index.html --contacts contacts.json [--fps 30]
//        [--json out.json] [--warn-only]
//
// contacts.json:
//   { "contacts": [ { "id": "folder-taken", "char": "maya5", "side": "L", "prop": "#folder5", "from": 30.0, "to": 30.75,
//                     "max_gap": 30 } ],
//     "props":    [ { "sel": "#folder5", "from": 28.45, "to": 30.75 } ] }
//
// Checks:
//   detached     the wrist is more than max_gap px (1920×1080) outside the prop's box while it is held.
//   hand-hidden  the prop is painted over both the wrist and the palm in more than 30 % of the held frames
//                (a grip shows fingers in front of the object; a hand that vanishes into it reads as missing).
//   prop-pop     between two consecutive frames the prop's centre moves more than 30 px and 2.5× the neighbouring
//                steps, or its box changes size by more than 35 % while neighbouring frames barely change: a jump or
//                an orientation flip, not motion.
// Limits: Rig v4 draws hands as one shape, so finger contact and object orientation are judged on the contact sheets
// (review_sheets.py), not here.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { SEEK, openComposition } from './lib/frame_state.mjs';

const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const file = args.find((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
if (!file || !opt('contacts')) { console.error('usage: contact_check.mjs index.html --contacts contacts.json [--fps 30]'); process.exit(2); }
const spec = JSON.parse(readFileSync(opt('contacts'), 'utf8'));
const fps = +opt('fps', 30);

const MEASURE = ({ chars, props }) => {
  const rb = document.getElementById('root').getBoundingClientRect(), k = 1920 / rb.width;
  const P = (x, y) => [(x - rb.left) * k, (y - rb.top) * k];
  const out = { hands: {}, props: {} };
  for (const [id, side] of chars) {
    const c = (typeof R4 !== 'undefined') && R4.chars[id], g = document.getElementById(id);
    if (!c || !c.J || !g) { out.hands[id + side] = null; continue; }
    const m = g.getScreenCTM(), tr = p => { const q = new DOMPoint(p[0], p[1]).matrixTransform(m); return [q.x, q.y]; };
    const w = c.J['wrist' + side], e = c.J['elbow' + side];
    const ws = tr(w), es = tr(e), palm = [ws[0] + (ws[0] - es[0]) * .3, ws[1] + (ws[1] - es[1]) * .3];
    let vis = true;
    for (let x = g; x && x !== document.body; x = x.parentElement) { const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < .05) vis = false; }
    out.hands[id + side] = { wrist: P(...ws), palm: P(...palm), ws, ps: palm, vis };
  }
  for (const sel of props) {
    const el = document.querySelector(sel);
    if (!el) { out.props[sel] = null; continue; }
    let vis = true;
    for (let x = el; x && x !== document.body; x = x.parentElement) { const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < .05) vis = false; }
    const r = el.getBoundingClientRect(), [x0, y0] = P(r.left, r.top), [x1, y1] = P(r.right, r.bottom);
    if (x1 < 0 || y1 < 0 || x0 > 1920 || y0 > 1080) vis = false;          // entirely off-frame
    out.props[sel] = { box: [x0, y0, x1, y1], vis };
  }
  return out;
};

const browser = await chromium.launch(opt('browser') ? { executablePath: opt('browser') } : {});
const { page, errors } = await openComposition(browser, pathToFileURL(path.resolve(file)).href);
await page.addStyleTag({ content: 'svg *, svg { pointer-events: visiblePainted !important; }' });

const results = [];
const distToBox = (p, b) => Math.hypot(Math.max(b[0] - p[0], 0, p[0] - b[2]), Math.max(b[1] - p[1], 0, p[1] - b[3]));

for (const c of spec.contacts || []) {
  const res = { id: c.id, kind: 'contact', from: c.from, to: c.to, pass: true, issues: [] };
  const maxGap = c.max_gap ?? 30;
  let n = 0, hidden = 0, worst = 0, worstT = null, missing = 0;
  for (let f = Math.ceil(c.from * fps); f / fps < c.to - 1e-6; f++) {
    const t = f / fps;
    await page.evaluate(`(${SEEK.toString()})(${t})`);
    const m = await page.evaluate(MEASURE, { chars: [[c.char, c.side]], props: [c.prop] });
    const h = m.hands[c.char + c.side], p = m.props[c.prop];
    if (!h || !p || !h.vis || !p.vis) { missing++; continue; }
    n++;
    const d = distToBox(h.wrist, p.box);
    if (d > worst) { worst = d; worstT = t; }
    const cov = await page.evaluate(([sel, pts]) => { const el = document.querySelector(sel);
      const G = new Set(['path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line', 'image', 'use', 'text']);
      // the first painted SVG shape at the point (transparent HTML layers and full-frame plates above it are skipped)
      return pts.map(([x, y]) => { const top = document.elementsFromPoint(x, y).find(e => G.has(e.tagName.toLowerCase()));
        return !!(el && top && el.contains(top)); }); }, [c.prop, [h.ws, h.ps]]);
    if (cov[0] && cov[1]) hidden++;
  }
  if (!n) res.issues.push({ check: 'not-found', detail: `the hand or prop is not on screen in [${c.from}, ${c.to})` });
  else {
    if (worst > maxGap) res.issues.push({ check: 'detached', detail: `wrist ${worst.toFixed(0)} px from the prop at ${worstT.toFixed(3)}s (limit ${maxGap})` });
    if (hidden / n > .3) res.issues.push({ check: 'hand-hidden', detail: `the prop covers wrist and palm in ${hidden}/${n} frames` });
  }
  res.frames = n; res.max_gap_px = +worst.toFixed(1); res.hidden_frames = hidden;
  res.pass = !res.issues.length; results.push(res);
}

for (const pr of spec.props || []) {
  const res = { id: pr.sel, kind: 'prop', from: pr.from, to: pr.to, pass: true, issues: [] };
  const boxes = [];
  for (let f = Math.ceil(pr.from * fps); f / fps < pr.to - 1e-6; f++) {
    await page.evaluate(`(${SEEK.toString()})(${f / fps})`);
    const p = (await page.evaluate(MEASURE, { chars: [], props: [pr.sel] })).props[pr.sel];
    boxes.push(p && p.vis ? { f, b: p.box } : { f, b: null });
  }
  const steps = [];
  for (let i = 1; i < boxes.length; i++) { const a = boxes[i - 1].b, b = boxes[i].b; if (!a || !b) continue;
    const ca = [(a[0] + a[2]) / 2, (a[1] + a[3]) / 2], cb = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
    const aa = (a[2] - a[0]) * (a[3] - a[1]), ab = (b[2] - b[0]) * (b[3] - b[1]);
    steps.push({ f: boxes[i].f, move: Math.hypot(cb[0] - ca[0], cb[1] - ca[1]), size: Math.max(aa, ab) / Math.max(1, Math.min(aa, ab)) }); }
  // a pop is a one-frame discontinuity: much larger than the steps around it (fast but smooth motion is not a pop)
  steps.forEach((s, i) => {
    const near = steps.slice(Math.max(0, i - 3), i).concat(steps.slice(i + 1, i + 4)).map(x => x.move).sort((a, b) => a - b);
    const ref = near.length ? near[near.length >> 1] : 0;
    const nearSize = steps.slice(Math.max(0, i - 2), i).concat(steps.slice(i + 1, i + 3)).map(x => x.size);
    if (s.move > 30 && s.move > 2.5 * ref) res.issues.push({ check: 'prop-pop', detail: `frame ${s.f} (${(s.f / fps).toFixed(3)}s): centre jumps ${s.move.toFixed(0)} px (neighbouring steps ≈ ${ref.toFixed(0)} px)` });
    else if (s.size > 1.35 && Math.max(1, ...nearSize) < 1.15) res.issues.push({ check: 'prop-pop', detail: `frame ${s.f} (${(s.f / fps).toFixed(3)}s): box size changes ×${s.size.toFixed(2)} in one frame` });
  });
  res.frames = boxes.length; res.pass = !res.issues.length; results.push(res);
}
await browser.close();

for (const r of results) {
  console.log(`${r.pass ? 'PASS' : 'FAIL'}  ${r.kind.padEnd(7)} ${String(r.id).padEnd(16)} ${r.from}–${r.to}s` + (r.kind === 'contact' ? `  (${r.frames} frames, max gap ${r.max_gap_px} px, hand hidden ${r.hidden_frames})` : `  (${r.frames} frames)`));
  r.issues.forEach(i => console.log(`        ${i.check}: ${i.detail}`));
}
const failed = results.filter(r => !r.pass).length;
console.log(`contact_check: ${results.length - failed}/${results.length} passed` + (errors.length ? `, ${errors.length} page error(s): ${errors[0]}` : ''));
if (opt('json')) writeFileSync(opt('json'), JSON.stringify({ fps, results, pageErrors: errors }, null, 2));
process.exit(failed && !args.includes('--warn-only') ? 1 : 0);
