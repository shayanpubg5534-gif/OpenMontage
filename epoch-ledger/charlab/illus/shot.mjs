// Render an HTML/SVG file to PNG with the pre-installed Chromium (artistic-direction gate).
//   node epoch-ledger/charlab/illus/shot.mjs IN.html OUT.png [W] [H]
import { createRequire } from 'node:module';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [inp, out, W = '1920', H = '1080'] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +W, height: +H } });
await p.goto('file://' + path.resolve(inp)); await p.waitForTimeout(300);
await p.screenshot({ path: out }); await b.close();
