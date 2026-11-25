import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [url, out] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(url); await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
for (const t of [0.5, 0.533, 0.567, 0.6, 0.633, 0.667]) { await p.evaluate(([t]) => window.renderAt(t, 'hand'), [t]); await p.screenshot({ path: `${out}/grip_${t}.png` }); }
await b.close();
