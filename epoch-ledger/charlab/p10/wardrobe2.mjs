// P10 formal wardrobe (v2): explicit, per-pose recolouring of the artist's own fill shapes, plus optional collar and tie
// drawn in the artwork's line weight. The artist's line work is never altered.
//   node epoch-ledger/charlab/p10/wardrobe2.mjs IN.svg --probe                 list BODY paths (index, fill, fill ratio, bbox)
//   node epoch-ledger/charlab/p10/wardrobe2.mjs IN.svg OUT.svg 'i=#hex,i=#hex' [tie=#hex@x0,y0,x1,y1] [collar]
// bbox fractions are of the BODY box; the tie box is where the shirt opening is (fractions of BODY).
import { createRequire } from 'node:module'; import { readFileSync, writeFileSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [inp, out, recol = '', tie = '', collar = ''] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 1600 } });
await p.setContent(`<body style="margin:0">${readFileSync(inp, 'utf8')}</body>`);
const res = await p.evaluate(([probe, recol, tie, collar]) => {
  const svg = document.querySelector('svg'); svg.setAttribute('width', 1000); svg.setAttribute('height', 1400);
  const body = document.getElementById('BODY'), root = svg.querySelector('g'), ink = '#1e1b19';
  const toRoot = el => { const m = root.getCTM().inverse().multiply(el.getCTM()), bb = el.getBBox();
    const pts = [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]].map(([x, y]) => [m.a * x + m.c * y + m.e, m.b * x + m.d * y + m.f]);
    const xs = pts.map(q => q[0]), ys = pts.map(q => q[1]); return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) }; };
  const B = toRoot(body);
  const cv = document.createElement('canvas'); cv.width = cv.height = 160; const g = cv.getContext('2d');
  const ratio = el => { const bb = el.getBBox(); if (bb.width < 2 || bb.height < 2) return 0; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, 160, 160);
    g.setTransform(150 / bb.width, 0, 0, 150 / bb.height, 5 - bb.x * 150 / bb.width, 5 - bb.y * 150 / bb.height);
    g.fill(new Path2D(el.getAttribute('d')), el.getAttribute('fill-rule') || 'nonzero');
    const d = g.getImageData(0, 0, 160, 160).data; let n = 0; for (let i = 3; i < d.length; i += 4) n += d[i] > 128; return n / 22500; };
  const paths = [...body.querySelectorAll('path')];
  if (probe) return paths.map((el, i) => { const r = toRoot(el); return [i, el.getAttribute('fill'), +ratio(el).toFixed(2),
    ...[(r.x - B.x) / B.w, (r.y - B.y) / B.h, (r.x + r.w - B.x) / B.w, (r.y + r.h - B.y) / B.h].map(v => +v.toFixed(2))]; });
  for (const kv of recol.split(',').filter(Boolean)) { const [i, c] = kv.split('='); paths[+i].setAttribute('fill', c); }
  if (tie) {
    const [col, box] = tie.split('@'); const [x0, y0, x1, y1] = box.split(',').map(Number);
    const c = { x: B.x + x0 * B.w, y: B.y + y0 * B.h, w: (x1 - x0) * B.w, h: (y1 - y0) * B.h };
    const cx = c.x + c.w * 0.5, top = c.y, len = c.h, w = Math.min(c.w * 0.5, B.w * 0.07), sw = B.w * 0.0095;
    const j = (x, y, k) => [x + Math.sin(k * 12.9898) * sw * 0.18, y + Math.cos(k * 78.233) * sw * 0.18];
    const P = pts => 'M' + pts.map((q, k) => j(q[0], q[1], k).map(v => v.toFixed(1)).join(' ')).join(' L') + ' Z';
    const knot = [[cx - w * 0.42, top + len * 0.04], [cx + w * 0.42, top + len * 0.04], [cx + w * 0.28, top + len * 0.13], [cx - w * 0.28, top + len * 0.13]];
    const blade = [[cx - w * 0.26, top + len * 0.13], [cx + w * 0.26, top + len * 0.13], [cx + w * 0.5, top + len * 0.86], [cx, top + len * 0.98], [cx - w * 0.5, top + len * 0.86]];
    const colL = [[cx - w * 0.15, top + len * 0.02], [cx - w * 1.25, top - len * 0.02], [cx - w * 0.95, top + len * 0.13]];
    const colR = [[cx + w * 0.15, top + len * 0.02], [cx + w * 1.25, top - len * 0.02], [cx + w * 0.95, top + len * 0.13]];
    const NS = 'http://www.w3.org/2000/svg', add = document.createElementNS(NS, 'g'); add.setAttribute('id', 'WARDROBE_ADDITIONS');
    const st = `stroke="${ink}" stroke-width="${sw}" stroke-linejoin="round"`;
    add.innerHTML = (collar ? [colL, colR].map(q => `<path d="${P(q)}" fill="#efe8dc" ${st}/>`).join('') : '') +
      `<path d="${P(blade)}" fill="${col}" ${st}/><path d="${P(knot)}" fill="${col}" ${st}/>`;
    body.parentNode.insertBefore(add, body.nextSibling);   // above the body, below the head (the chin overlaps the knot)
  }
  return new XMLSerializer().serializeToString(svg).replace(/ width="1000" height="1400"/, '');
}, [out === '--probe', recol, tie, collar]);
if (out === '--probe') console.log(res.map(r => JSON.stringify(r)).join('\n')); else writeFileSync(out, res);
await b.close();
