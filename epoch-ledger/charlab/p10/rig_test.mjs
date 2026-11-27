// P10: render a rig at several poses side by side (inspection of joints).
//   node epoch-ledger/charlab/p10/rig_test.mjs IN.svg RIG.json OUT.png 'joint=deg,joint=deg;...' [x0,y0,x1,y1 crop]
import { createRequire } from 'node:module'; import { readFileSync } from 'node:fs';
import { rigSVG, POSE_JS } from './rig.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [inp, rigf, out, poses, crop] = process.argv.slice(2);
const spec = JSON.parse(readFileSync(rigf, 'utf8')).pieces;
let svg = rigSVG(readFileSync(inp, 'utf8'), spec);
if (crop) { const [a, b, c, d] = crop.split(',').map(Number); svg = svg.replace(/viewBox="[^"]+"/, `viewBox="${a} ${b} ${c - a} ${d - b}"`); }
const P = poses.split(';').map(s => Object.fromEntries(s.split(',').filter(Boolean).map(kv => { const [k, v] = kv.split('='); return [k, +v]; })));
const html = `<body style="margin:0;background:#e9e2d5;font:14px Georgia"><div id=s style="display:inline-flex;gap:10px;padding:10px">${P.map(p =>
  `<figure style="margin:0;background:#f4efe6;width:340px">${svg.replace('<svg ', '<svg style="width:340px;height:auto;display:block" ')}<figcaption>${JSON.stringify(p)}</figcaption></figure>`).join('')}</div>
<script>${POSE_JS}; const P = ${JSON.stringify(P)}; document.querySelectorAll('figure').forEach((f, i) => poseRig(f.querySelector('svg'), P[i]));</script></body>`;
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2000, height: 1200 } });
await p.setContent(html); await (await p.$('#s')).screenshot({ path: out }); await b.close();
