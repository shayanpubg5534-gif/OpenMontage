#!/usr/bin/env node
// Epoch Ledger layout check — samples a HyperFrames composition over time and flags text that
// collides with other text, sits in the caption band while a caption is showing, runs off-frame,
// or partially covers an element marked as a key object (data-keep). DOM measurement only: no
// rendering, no video, seconds per minute of film. Original implementation.
//
//   node epoch-ledger/scripts/layout_check.mjs <workspace>/index.html [--start 0] [--end D] [--every 0.25]
//        [--json out.json] [--min-area 64] [--browser path]
// Readable text = labels, tags, panels, captions, kinetic text, or any element with data-read; add data-deco
// to exempt decorative text. Mark key objects (faces, chart marks) with data-keep.
// Exit code 1 if any issue is found (use --warn-only to always exit 0).
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');   // pre-installed globally (NODE_PATH)
import { pathToFileURL } from 'node:url';
import { writeFileSync } from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--'));
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
if (!file) { console.error('usage: layout_check.mjs index.html [--start s] [--end s] [--every s] [--json out]'); process.exit(2); }
const every = +opt('every', 0.25), minArea = +opt('min-area', 64), warnOnly = args.includes('--warn-only');

const exe = opt('browser', undefined);   // default: Playwright's bundled Chromium
const browser = await chromium.launch(exe ? { executablePath: exe } : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
await page.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: 'load' });
for (let k = 0; k < 120 && !(await page.evaluate(() => !!(window.__timelines && window.__timelines.main))); k++) await page.waitForTimeout(250);

const meta = await page.evaluate(() => {
  const root = document.getElementById('root');
  return { duration: +root.dataset.duration, w: +root.dataset.width, h: +root.dataset.height };
});
const start = +opt('start', 0), end = Math.min(+opt('end', meta.duration), meta.duration);
const issues = [];
for (let t = start; t <= end + 1e-6; t += every) {
  const found = await page.evaluate(({ t, minArea }) => {
    const root = document.getElementById('root'), rb = root.getBoundingClientRect();
    const sx = 1920 / rb.width;                                                    // report in 1920×1080 authoring px
    document.querySelectorAll('[data-start][data-duration]').forEach(c => {       // emulate clip windows
      if (c === root || c.tagName === 'AUDIO') return; const s = +c.dataset.start, d = +c.dataset.duration;
      c.style.visibility = t >= s && t < s + d ? 'visible' : 'hidden'; });
    window.__timelines.main.seek(t, false);
    const vis = el => { for (let e = el; e && e !== document.body; e = e.parentElement) { const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < .06) return false; } return true; };
    const box = el => { const r = el.getBoundingClientRect(); return { x: (r.left - rb.left) * sx, y: (r.top - rb.top) * sx, w: r.width * sx, h: r.height * sx }; };
    // leaf text blocks: elements with their own non-empty text and no element children carrying text
    const READ = '.lbl,.tag,.src,.panel,.year,.ecap,.ktext,.mc-title,.mc-step,.es-line,[data-read]';
    const texts = [];
    document.querySelectorAll('#root *').forEach(el => {
      if (el.closest('svg') && el.tagName.toLowerCase() !== 'text') return;
      const own = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
      if (!own || !vis(el)) return;
      // measure the glyphs, not the block: union of the element's own text-node line boxes
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      Array.from(el.childNodes).filter(n => n.nodeType === 3 && n.textContent.trim()).forEach(n => { const r = document.createRange(); r.selectNodeContents(n);
        Array.from(r.getClientRects()).forEach(q => { x0 = Math.min(x0, q.left); y0 = Math.min(y0, q.top); x1 = Math.max(x1, q.right); y1 = Math.max(y1, q.bottom); }); });
      if (el.tagName.toLowerCase() === 'text') { const q = el.getBoundingClientRect(); x0 = q.left; y0 = q.top; x1 = q.right; y1 = q.bottom; }
      for (let e = el.parentElement; e && e !== root; e = e.parentElement) {          // clip to masking ancestors
        const cs = getComputedStyle(e); if (cs.overflow === 'visible' && cs.clipPath === 'none') continue;
        const q = e.getBoundingClientRect(); x0 = Math.max(x0, q.left); y0 = Math.max(y0, q.top); x1 = Math.min(x1, q.right); y1 = Math.min(y1, q.bottom); }
      const b = { x: (x0 - rb.left) * sx, y: (y0 - rb.top) * sx, w: (x1 - x0) * sx, h: (y1 - y0) * sx }; if (!(b.w >= 4 && b.h >= 4)) return;
      texts.push({ el, b, deco: !!el.closest('[data-deco]'), read: !!el.closest(READ) && !el.closest('[data-deco]'), id: el.id || (el.closest('[id]') || {}).id || el.tagName, cap: !!el.closest('.ecap'), txt: el.textContent.trim().slice(0, 40) });
    });
    const keeps = Array.from(document.querySelectorAll('[data-keep]')).filter(vis).map(el => ({ b: box(el), id: el.id || 'keep' }));
    const inter = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
    const out = [], capOn = texts.some(x => x.cap);
    for (let i = 0; i < texts.length; i++) {
      const A = texts[i];
      if (A.read && (A.b.x < -2 || A.b.y < -2 || A.b.x + A.b.w > 1922 || A.b.y + A.b.h > 1082))
        out.push({ kind: 'off-frame', a: A.id, text: A.txt });
      if (A.read && capOn && !A.cap && A.b.y + A.b.h > 880 && A.b.y < 1040 && A.b.x < 1560 && A.b.x + A.b.w > 360)
        out.push({ kind: 'caption-band', a: A.id, text: A.txt });
      for (let j = i + 1; j < texts.length; j++) { const B = texts[j];
        if (A.cap && B.cap) continue;
        if (!A.read && !B.read) continue;                                  // decorative vs decorative is art, not a collision
        if ((A.cap && B.deco) || (B.cap && A.deco)) continue;              // in-world signage passing behind a caption box
        if (A.el.contains(B.el) || B.el.contains(A.el)) continue;          // nested text (title + <small>)
        const ar = inter(A.b, B.b); if (ar >= minArea) out.push({ kind: 'text-overlap', a: A.id, b: B.id, text: A.txt + ' / ' + B.txt, area: Math.round(ar) }); }
      if (A.read) keeps.forEach(K => { const ar = inter(A.b, K.b), full = ar >= A.b.w * A.b.h * .98;
        if (ar >= minArea && !full) out.push({ kind: 'covers-key-object', a: A.id, b: K.id, text: A.txt }); });
    }
    return out.map(o => o);
  }, { t, minArea });
  found.forEach(f => issues.push(Object.assign({ t: +t.toFixed(2) }, f)));
}
await browser.close();

// collapse repeats into time ranges (same kind and elements; changing numbers don't split a range)
const groups = [], open = new Map();
for (const i of issues) { const k = [i.kind, i.a, i.b || ''].join('|'), g = open.get(k);
  if (g && i.t - g.to <= every * 1.5) { g.to = i.t; continue; }
  const n = Object.assign({ from: i.t, to: i.t }, i); open.set(k, n); groups.push(n); }
const list = groups.sort((a, b) => a.from - b.from);
for (const g of list) console.log(`${g.from.toFixed(2)}–${g.to.toFixed(2)}s  ${g.kind.padEnd(17)} ${g.a}${g.b ? ' × ' + g.b : ''}  "${g.text}"`);
console.log(`layout_check: ${list.length} issue range(s) in ${start}–${end}s (every ${every}s)` + (errors.length ? `, ${errors.length} page error(s): ${errors[0]}` : ''));
if (opt('json')) writeFileSync(opt('json'), JSON.stringify({ start, end, every, issues: list, pageErrors: errors }, null, 2));
process.exit(list.length && !warnOnly ? 1 : 0);
