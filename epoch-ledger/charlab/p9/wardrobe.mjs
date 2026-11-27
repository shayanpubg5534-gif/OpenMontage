// P9 wardrobe feasibility: can the artist's own Open Peeps drawings carry professional clothing?
//   node epoch-ledger/charlab/p9/wardrobe.mjs IN.svg OUT_PREFIX SUIT_HEX TIE_HEX SHOE_HEX
// Writes OUT_PREFIX_{0..3}.svg: 0 original · 1 matching suit trousers (the artist's trouser fill shapes recoloured, outlines
// untouched) · 2 + shirt collar and tie (new shapes drawn in the artwork's ink weight, on the shirt opening) · 3 + dark
// leather shoes (the artist's shoe fills recoloured). Only fills are changed; the artist's line work is never altered.
import { createRequire } from 'node:module'; import { readFileSync, writeFileSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [inp, pre, SUIT, TIE, SHOE, CHEST] = process.argv.slice(2);   // CHEST (optional): 'x0,y0,x1,y1' shirt opening in body fractions,
// for drawings whose shirt is part of the ink line work and so cannot be found as a separate fill
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 1600 } });
await p.setContent(`<body style="margin:0">${readFileSync(inp, 'utf8')}</body>`);
const outs = await p.evaluate(([SUIT, TIE, SHOE, CHEST]) => {
  const svg = document.querySelector('svg'); svg.setAttribute('width', 1000); svg.setAttribute('height', 1400);
  const body = document.getElementById('BODY'); const root = svg.querySelector('g');
  const RB = body.getBBox();
  const toRoot = el => { const m = root.getCTM().inverse().multiply(el.getCTM()); const bb = el.getBBox();
    const pts = [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]].map(([x, y]) => [m.a * x + m.c * y + m.e, m.b * x + m.d * y + m.f]);
    const xs = pts.map(q => q[0]), ys = pts.map(q => q[1]); return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) }; };
  const bm = root.getCTM().inverse().multiply(body.getCTM());
  const B = toRoot(body); const ink = '#1e1b19';
  // fill area ratio by rasterising each path alone (outlines are thin rings: low ratio; fills are solid: high ratio)
  const cv = document.createElement('canvas'); cv.width = cv.height = 160; const g = cv.getContext('2d');
  const ratio = el => { const bb = el.getBBox(); if (bb.width < 2 || bb.height < 2) return 0; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, 160, 160);
    g.setTransform(150 / bb.width, 0, 0, 150 / bb.height, 5 - bb.x * 150 / bb.width, 5 - bb.y * 150 / bb.height);
    try { g.fill(new Path2D(el.getAttribute('d')), el.getAttribute('fill-rule') || 'nonzero'); } catch (e) { return 0; }
    const d = g.getImageData(0, 0, 160, 160).data; let n = 0; for (let i = 3; i < d.length; i += 4) n += d[i] > 128; return n / (150 * 150); };
  const paths = [...body.querySelectorAll('path')].map(el => ({ el, f: (el.getAttribute('fill') || '').toLowerCase(), r: toRoot(el), a: ratio(el) }));
  const lower = q => (q.r.y + q.r.h / 2 - B.y) / B.h;
  const isOutline = q => q.f === ink && q.a < 0.45;
  const trousers = paths.filter(q => !isOutline(q) && lower(q) > 0.55 && lower(q) < 0.9 && q.r.h > B.h * 0.18);
  const shoes = paths.filter(q => !isOutline(q) && q.f === '#efe8dc' && (q.r.y - B.y) / B.h > 0.82);   // the white shoe shapes only (not skin, not trousers)
  const ser = () => new XMLSerializer().serializeToString(svg);
  const res = [ser()];
  trousers.forEach(q => q.el.setAttribute('fill', SUIT)); res.push(ser());
  // the shirt opening: the lightest large fill in the chest band (between the blazer lapels)
  let chest = paths.filter(q => !isOutline(q) && q.f !== SUIT && (q.r.y - B.y) / B.h < 0.32 && (q.r.y + q.r.h - B.y) / B.h > 0.18 && q.r.w < B.w * 0.5)
    .sort((a, b) => b.r.w * b.r.h - a.r.w * a.r.h)[0];
  if (CHEST) { const [x0, y0, x1, y1] = CHEST.split(',').map(Number); chest = { manual: true, r: { x: B.x + x0 * B.w, y: B.y + y0 * B.h, w: (x1 - x0) * B.w, h: (y1 - y0) * B.h } }; }
  if (chest) {
    const c = chest.r, cx = c.x + c.w * 0.5, top = c.y + c.h * 0.02, len = c.h * 0.78, w = Math.min(c.w * 0.28, B.w * 0.07);
    const sw = B.w * 0.0095;                         // ink weight of the artwork's outlines
    const NS = 'http://www.w3.org/2000/svg'; const add = document.createElementNS(NS, 'g'); add.setAttribute('id', 'WARDROBE_ADDITIONS');
    const j = (x, y, k) => [x + Math.sin(k * 12.9898) * sw * 0.18, y + Math.cos(k * 78.233) * sw * 0.18];   // a slight hand-drawn wobble
    const P = pts => 'M' + pts.map((q, k) => j(q[0], q[1], k).map(v => v.toFixed(1)).join(' ')).join(' L') + ' Z';
    const knot = [[cx - w * 0.42, top + len * 0.04], [cx + w * 0.42, top + len * 0.04], [cx + w * 0.28, top + len * 0.13], [cx - w * 0.28, top + len * 0.13]];
    const blade = [[cx - w * 0.26, top + len * 0.13], [cx + w * 0.26, top + len * 0.13], [cx + w * 0.5, top + len * 0.86], [cx, top + len * 0.98], [cx - w * 0.5, top + len * 0.86]];
    const colL = [[cx - w * 0.15, top + len * 0.02], [cx - w * 1.25, top - len * 0.02], [cx - w * 0.95, top + len * 0.13]];
    const colR = [[cx + w * 0.15, top + len * 0.02], [cx + w * 1.25, top - len * 0.02], [cx + w * 0.95, top + len * 0.13]];
    add.innerHTML = [colL, colR].map(q => `<path d="${P(q)}" fill="#efe8dc" stroke="${ink}" stroke-width="${sw}" stroke-linejoin="round"/>`).join('') +
      `<path d="${P(blade)}" fill="${TIE}" stroke="${ink}" stroke-width="${sw}" stroke-linejoin="round"/><path d="${P(knot)}" fill="${TIE}" stroke="${ink}" stroke-width="${sw}" stroke-linejoin="round"/>`;
    root.appendChild(add);
  }
  res.push(ser());
  shoes.forEach(q => q.el.setAttribute('fill', SHOE)); res.push(ser());
  return { res, n: { trousers: trousers.length, shoes: shoes.length, chest: chest ? (chest.manual ? 'manual' : 'auto') : false } };
}, [SUIT, TIE, SHOE, CHEST]);
outs.res.forEach((s, k) => writeFileSync(`${pre}_${k}.svg`, s.replace(/ width="1000" height="1400"/, '')));
console.log(JSON.stringify(outs.n)); await b.close();
