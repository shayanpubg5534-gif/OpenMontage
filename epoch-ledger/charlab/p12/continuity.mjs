// P12: rendered continuity check. A fill can be recoloured and still be hidden under the artist's ink (a garment drawn
// in black), so the identity must be checked on the PIXELS: for every variant of a character, rasterise it and require
// the identity's top colour to be a dominant colour of the body (≥ 12 % of the body's non-ink, non-skin pixels), and the
// same colour across all of that character's variants.
//   node epoch-ledger/charlab/p12/continuity.mjs CAST_DIR      (reads CAST_DIR/continuity_spec.json written by cast.py)
import { createRequire } from 'node:module'; import { readFileSync, writeFileSync } from 'node:fs'; import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const dir = process.argv[2]; const spec = JSON.parse(readFileSync(path.join(dir, 'continuity_spec.json'), 'utf8'));
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)), dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const b = await chromium.launch(); const p = await b.newPage(); const out = {}; let fail = 0;
for (const v of spec.variants) {
  const svg = readFileSync(path.join(dir, v.file), 'utf8');
  const px = await p.evaluate(async svg => {
    const doc = new DOMParser().parseFromString(svg, 'image/svg+xml').documentElement; doc.querySelector('[id="HEAD"]')?.setAttribute('display', 'none');
    doc.querySelectorAll('[id="FACE"],[id="FACIAL HAIR"],[id="ACCESORIES"]').forEach(n => n.setAttribute('display', 'none'));
    const vb = doc.getAttribute('viewBox').split(/\s+/).map(Number), W = 400, H = Math.round(400 * vb[3] / vb[2]);
    doc.setAttribute('width', W); doc.setAttribute('height', H);
    const im = new Image(); im.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(new XMLSerializer().serializeToString(doc)))); await im.decode();
    const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d'); g.drawImage(im, 0, 0);
    const d = g.getImageData(0, 0, W, H).data, hist = {};
    for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 250) { const k = [d[i], d[i + 1], d[i + 2]].map(x => x >> 3 << 3).join(','); hist[k] = (hist[k] || 0) + 1; }
    return hist;
  }, svg);
  const ink = hex(spec.ink), skin = hex(v.skin), top = hex(v.top);
  let tot = 0, hit = 0;
  for (const [k, n] of Object.entries(px)) { const c = k.split(',').map(Number); if (dist(c, ink) < 40 || dist(c, skin) < 40) continue; tot += n; if (dist(c, top) < 30) hit += n; }
  const share = tot ? hit / tot : 0, ok = share >= 0.12; if (!ok) fail++;
  out[v.file] = { character: v.character, top: v.top, top_share: +share.toFixed(3), ok };
}
await b.close(); writeFileSync(path.join(dir, 'continuity_rendered.json'), JSON.stringify(out, null, 1));
console.log(JSON.stringify({ variants: spec.variants.length, failed: fail, detail: out })); process.exit(fail ? 1 : 0);
