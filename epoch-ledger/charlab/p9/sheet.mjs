// P9 labelled contact sheet (SVG or PNG/JPG tiles).
//   node epoch-ledger/charlab/p9/sheet.mjs OUT.png "TITLE" COLS TILE_W "label::path" ["label::path" ...]
import { createRequire } from 'node:module'; import { readFileSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [out, title, cols, tw, ...items] = process.argv.slice(2);
const tile = s => { const [label, f] = s.split('::');
  const src = f.endsWith('.svg') ? 'data:image/svg+xml;base64,' + readFileSync(f).toString('base64')
    : `data:image/${f.endsWith('.png') ? 'png' : 'jpeg'};base64,` + readFileSync(f).toString('base64');
  return `<figure><img src="${src}"><figcaption>${label}</figcaption></figure>`; };
const html = `<html><body style="margin:0;background:#e9e2d5;font:15px/1.3 Georgia,serif;color:#2a2420">
<div id=s style="display:inline-block;padding:22px"><h2 style="margin:0 0 14px;font-weight:normal">${title}</h2>
<div style="display:grid;grid-template-columns:repeat(${cols},${tw}px);gap:14px">${items.map(tile).join('')}</div></div>
<style>figure{margin:0;background:#f4efe6;padding:8px}img{width:100%;display:block}figcaption{margin-top:6px}</style></body></html>`;
const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 1, viewport: { width: 2400, height: 1200 } });
await p.setContent(html); await p.waitForLoadState('networkidle');
await (await p.$('#s')).screenshot({ path: out }); await b.close(); console.log('sheet', out);
