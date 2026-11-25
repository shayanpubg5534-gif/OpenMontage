import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { createHash } from 'node:crypto';
const [url, out] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto(url); await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
console.log('gpu:', await p.evaluate(() => { const g = document.createElement('canvas').getContext('webgl'); const d = g.getExtension('WEBGL_debug_renderer_info'); return d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : '?'; }));
console.log('hand bone:', await p.evaluate(() => window.hand), '| bones:', (await p.evaluate(() => window.bones.length)));
for (const cam of ['wide', 'medium', 'close']) { await p.evaluate(([t, c]) => window.renderAt(t, c), [1.0, cam]); await p.screenshot({ path: `${out}/spike_${cam}.png` }); }
// speed: 60 frames, render + canvas readback (what a capture needs)
const t0 = Date.now();
for (let i = 0; i < 60; i++) await p.evaluate(([t]) => { window.renderAt(t, 'medium'); return document.querySelector('canvas').toDataURL('image/png').length; }, [i / 30]);
console.log('ms/frame (render + PNG readback, medium shot):', ((Date.now() - t0) / 60).toFixed(0));
// determinism: the same time from two different histories
const shot = async () => createHash('sha1').update(await p.evaluate(() => document.querySelector('canvas').toDataURL('image/png'))).digest('hex');
await p.evaluate(() => window.renderAt(.2, 'wide')); await p.evaluate(() => window.renderAt(1.4, 'wide')); const a = await shot();
await p.evaluate(() => window.renderAt(3.1, 'wide')); await p.evaluate(() => window.renderAt(1.4, 'wide')); const c = await shot();
console.log('deterministic seek:', a === c, '| errors:', errs.slice(0, 3));
await b.close();
