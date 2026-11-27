// P10 helper: render an SVG with a labelled coordinate grid in its own user units (for placing joints and regions).
//   node epoch-ledger/charlab/p10/grid.mjs IN.svg OUT.png [STEP=20] [x0,y0,x1,y1 crop in user units]
import { createRequire } from 'node:module'; import { readFileSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [inp, out, step = '20', crop] = process.argv.slice(2); const S = +step;
let svg = readFileSync(inp, 'utf8'); const vb = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
const [x0, y0, x1, y1] = crop ? crop.split(',').map(Number) : [vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3]];
let g = ''; for (let x = Math.ceil(x0 / S) * S; x <= x1; x += S) g += `<line x1="${x}" y1="${y0}" x2="${x}" y2="${y1}" stroke="${x % (S * 5) ? '#0a8' : '#d22'}" stroke-width="${x % (S * 5) ? .3 : .6}"/>` + (x % (S * 5) ? '' : `<text x="${x + 1}" y="${y0 + 6}" font-size="6" fill="#d22">${x}</text>`);
for (let y = Math.ceil(y0 / S) * S; y <= y1; y += S) g += `<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="${y % (S * 5) ? '#0a8' : '#d22'}" stroke-width="${y % (S * 5) ? .3 : .6}"/>` + (y % (S * 5) ? '' : `<text x="${x0 + 1}" y="${y - 1}" font-size="6" fill="#d22">${y}</text>`);
svg = svg.replace(/viewBox="[^"]+"/, `viewBox="${x0} ${y0} ${x1 - x0} ${y1 - y0}" width="${Math.round(1200 * (x1 - x0) / Math.max(x1 - x0, y1 - y0))}" height="${Math.round(1200 * (y1 - y0) / Math.max(x1 - x0, y1 - y0))}"`).replace(/<\/svg>\s*$/, g + '</svg>');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 1300 } });
await p.setContent(`<body style="margin:0;background:#fff">${svg}</body>`); await (await p.$('svg')).screenshot({ path: out }); await b.close();
