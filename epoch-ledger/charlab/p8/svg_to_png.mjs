// P8: render SVG files to PNG (headless Chromium): node svg_to_png.mjs HEIGHT in1.svg out1.png [in2.svg out2.png ...]
import { createRequire } from 'node:module'; import { readFileSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [h, ...pairs] = process.argv.slice(2); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: +h + 20 } });
for (let i = 0; i < pairs.length; i += 2) {
  await p.setContent(`<body style="margin:0;background:#d9d2c5"><img id=i style="height:${h}px" src="data:image/svg+xml;base64,${readFileSync(pairs[i]).toString('base64')}"></body>`);
  await p.waitForTimeout(150); await (await p.$('#i')).screenshot({ path: pairs[i + 1] }); }
await b.close();
