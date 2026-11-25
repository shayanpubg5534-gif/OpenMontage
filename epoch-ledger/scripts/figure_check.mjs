#!/usr/bin/env node
// Epoch Ledger figure check: every on-screen figure is legible when the narration says it, is not revealed long
// before it is said, and every chart's marks are proportional to their values on a shared baseline.
// DOM measurement of the built composition (no rendering, no video). Original implementation.
//
//   node epoch-ledger/scripts/figure_check.mjs <workspace>/index.html --figures figures.json --words words.json
//        [--json out.json] [--browser path] [--warn-only]
//
// figures.json:
//   { "figures": [ { "id": "wages", "sel": "#pb-wal" (or a list of selectors), "text": "−$12,000", "cue": ["wages"], "after": 7,
//                    "settle": 0.6, "hold": 1.2, "lead": 0.75 } ],
//     "charts":  [ { "id": "profit-bars", "at": {"cue": ["profit"], "after": 14, "offset": 0.6},
//                    "measure": "height", "baseline": "bottom",
//                    "marks": [ { "sel": "#pb-r2", "value": 18000 }, { "sel": "#pb-r1", "value": 12000 } ] } ] }
//
// Checks per figure (cue = start of the first spoken word matching any of `cue` at or after `after` seconds):
//   label-missing   the element is not legible for at least 80 % of [cue + settle, cue + settle + hold]. Legible means:
//                   inside its clip window, effective opacity ≥ 0.6, inside the frame, containing `text` (if given),
//                   not painted over by a later SVG mark, and contrast against the mark beneath it ≥ 1.6.
//   early-reveal    the element is already legible more than `lead` seconds before the cue (searched back 8 s).
// Checks per chart (at the cue time + offset):
//   not-proportional  size / value differs between marks by more than 3 % (plus 6 px for strokes).
//   off-baseline      marks do not share a baseline (bottom, top, left or right edge) within 4 px.
// Exit 1 on any failure unless --warn-only.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { SEEK, openComposition } from './lib/frame_state.mjs';

const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const file = args.find((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
if (!file || !opt('figures') || !opt('words')) { console.error('usage: figure_check.mjs index.html --figures f.json --words words.json'); process.exit(2); }
const spec = JSON.parse(readFileSync(opt('figures'), 'utf8'));
const words = JSON.parse(readFileSync(opt('words'), 'utf8'));

const norm = s => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
export function cueTime(cue, after = 0) {
  const want = (Array.isArray(cue) ? cue : [cue]).map(norm);
  const w = words.find(w => w.start >= after - 1e-6 && want.includes(norm(w.word)));
  if (!w) throw new Error(`cue ${JSON.stringify(cue)} not spoken after ${after}s`);
  return w.start;
}

// In-page: legibility of one element at the current time.
const LEGIBLE = ({ sel, text }) => {
  const root = document.getElementById('root'), rb = root.getBoundingClientRect();
  const el = document.querySelector(sel);
  if (!el) return { ok: false, why: 'no such element' };
  let op = 1;
  for (let e = el; e && e !== document.body; e = e.parentElement) {
    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden') return { ok: false, why: 'hidden' };
    op *= +cs.opacity;
  }
  if (op < .6) return { ok: false, why: `opacity ${op.toFixed(2)}` };
  const content = (el.textContent || '').replace(/\s+/g, ' ');
  if (text && !content.includes(text)) return { ok: false, why: `text is "${content.trim().slice(0, 40)}"` };
  const texts = el.tagName.toLowerCase() === 'text' ? [el] : Array.from(el.querySelectorAll('text, div, span, b, small, p')).filter(t =>
    Array.from(t.childNodes).some(n => n.nodeType === 3 && n.textContent.trim()));
  const SHAPES = new Set(['path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line', 'image', 'use']);
  const rgb = c => { const m = (c || '').match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(Number); return v.length > 3 && v[3] === 0 ? null : v; };
  const lum = v => { const f = x => { x /= 255; return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; }; return .2126 * f(v[0]) + .7152 * f(v[1]) + .0722 * f(v[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
  const effOp = e => { let o = 1; for (; e && e !== document.body; e = e.parentElement) o *= +getComputedStyle(e).opacity; return o; };
  for (const t of texts) {
    const r = t.getBoundingClientRect();
    if (r.width < 2) continue;
    if (r.left < rb.left - 2 || r.top < rb.top - 2 || r.right > rb.right + 2 || r.bottom > rb.bottom + 2) return { ok: false, why: 'off-frame' };
    const cs = getComputedStyle(t), fg = rgb(t.namespaceURI.includes('svg') ? cs.fill : cs.color);
    let n = 0, covered = 0; const rs = [];
    for (let gx = 1; gx <= 5; gx++) for (let gy = 1; gy <= 3; gy++) {
      const px = r.left + r.width * gx / 6, py = r.top + r.height * (.25 + .5 * gy / 4), stack = document.elementsFromPoint(px, py);
      const i = stack.findIndex(e => e === t || t.contains(e)); if (i < 0) continue; n++;
      if (stack.slice(0, i).some(e => SHAPES.has(e.tagName.toLowerCase()) && !e.contains(t) && effOp(e) >= .3 && !e.closest('.ecap'))) covered++;
      const under = stack.slice(i + 1).find(e => SHAPES.has(e.tagName.toLowerCase()) && effOp(e) >= .3 && rgb(getComputedStyle(e).fill));
      if (fg && under) rs.push(ratio(fg, rgb(getComputedStyle(under).fill)));
    }
    if (n && covered / n >= .2) return { ok: false, why: `"${t.textContent.trim().slice(0, 24)}" painted over` };
    rs.sort((a, b) => a - b);
    if (rs.length >= 5 && rs[rs.length >> 1] < 1.6) return { ok: false, why: `"${t.textContent.trim().slice(0, 24)}" contrast ${rs[rs.length >> 1].toFixed(2)}` };
  }
  return { ok: true, op: +op.toFixed(2) };
};

const GEOM = (marks) => marks.map(m => { const e = document.querySelector(m.sel); if (!e) return null;
  const r = e.getBoundingClientRect(), rb = document.getElementById('root').getBoundingClientRect(), k = 1920 / rb.width;
  return { sel: m.sel, value: m.value, x0: (r.left - rb.left) * k, x1: (r.right - rb.left) * k, y0: (r.top - rb.top) * k, y1: (r.bottom - rb.top) * k }; });

const browser = await chromium.launch(opt('browser') ? { executablePath: opt('browser') } : {});
const { page, errors } = await openComposition(browser, pathToFileURL(path.resolve(file)).href);
await page.addStyleTag({ content: 'svg *, svg { pointer-events: visiblePainted !important; }' });
const seek = t => page.evaluate(`(${SEEK.toString()})(${t})`);
// `sel` may list several elements (a figure that carries over into the next shot): legible if any of them is.
const legible = async (t, f) => { await seek(t); let last;
  for (const sel of [].concat(f.sel)) { last = await page.evaluate(LEGIBLE, { sel, text: f.text || '' }); if (last.ok) return last; }
  return last; };

const results = [];
for (const f of spec.figures || []) {
  const cue = cueTime(f.cue, f.after || 0), settle = f.settle ?? .6, hold = f.hold ?? 1.2, lead = f.lead ?? .75;
  const res = { id: f.id, kind: 'figure', cue: +cue.toFixed(2), pass: true, issues: [] };
  let good = 0, n = 0, why = '';
  for (let t = cue + settle; t <= cue + settle + hold + 1e-6; t += .1) { n++; const r = await legible(t, f); if (r.ok) good++; else why = why || `${t.toFixed(2)}s: ${r.why}`; }
  if (good / n < .8) res.issues.push({ check: 'label-missing', detail: `legible in ${good}/${n} samples after the cue; ${why}` });
  let first = null;
  for (let t = Math.max(0, cue - 8); t < cue; t += .1) { if ((await legible(t, f)).ok) { first = t; break; } }
  if (first !== null && first < cue - lead) res.issues.push({ check: 'early-reveal', detail: `legible at ${first.toFixed(2)}s, ${(cue - first).toFixed(2)}s before the cue (lead ${lead}s)` });
  res.pass = !res.issues.length; results.push(res);
}
for (const c of spec.charts || []) {
  const t = c.at.t ?? cueTime(c.at.cue, c.at.after || 0) + (c.at.offset || 0);
  await seek(t);
  const g = await page.evaluate(GEOM, c.marks);
  const res = { id: c.id, kind: 'chart', t: +t.toFixed(2), pass: true, issues: [], marks: g };
  if (g.some(m => !m)) res.issues.push({ check: 'missing-mark', detail: c.marks.filter((m, i) => !g[i]).map(m => m.sel).join(', ') });
  else {
    const size = m => c.measure === 'width' ? m.x1 - m.x0 : m.y1 - m.y0;
    const per = g.map(m => size(m) / m.value), ref = per.reduce((a, b) => a + b) / per.length;
    g.forEach(m => { const want = m.value * ref, got = size(m); if (Math.abs(got - want) > want * .03 + 6)
      res.issues.push({ check: 'not-proportional', detail: `${m.sel}: ${got.toFixed(0)} px for ${m.value} (expected ≈ ${want.toFixed(0)} px)` }); });
    const base = 'baseline' in c ? c.baseline : 'bottom', edge = { bottom: 'y1', top: 'y0', left: 'x0', right: 'x1' }[base];
    if (edge) { const v = g.map(m => m[edge]), med = [...v].sort((a, b) => a - b)[v.length >> 1];
      g.forEach((m, i) => { if (Math.abs(v[i] - med) > 4) res.issues.push({ check: 'off-baseline', detail: `${m.sel}: ${base} edge at ${v[i].toFixed(0)} px, others at ${med.toFixed(0)} px` }); }); }
  }
  res.pass = !res.issues.length; results.push(res);
}
await browser.close();

for (const r of results) {
  console.log(`${r.pass ? 'PASS' : 'FAIL'}  ${r.kind.padEnd(6)} ${r.id.padEnd(18)} ${r.kind === 'figure' ? 'cue ' + r.cue + 's' : 'at ' + r.t + 's'}`);
  r.issues.forEach(i => console.log(`        ${i.check}: ${i.detail}`));
}
const failed = results.filter(r => !r.pass).length;
console.log(`figure_check: ${results.length - failed}/${results.length} passed` + (errors.length ? `, ${errors.length} page error(s): ${errors[0]}` : ''));
if (opt('json')) writeFileSync(opt('json'), JSON.stringify({ results, pageErrors: errors }, null, 2));
process.exit(failed && !args.includes('--warn-only') ? 1 : 0);
