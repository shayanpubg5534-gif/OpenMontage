#!/usr/bin/env node
// Render an HTML style frame (or any composition time) to a PNG still at exact pixel size.
//   node epoch-ledger/scripts/still.mjs page.html out.png [--w 1920 --h 1080] [--t seconds]
// Waits for fonts and images; if the page exposes window.__timelines.main, seeks it to --t.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const a = process.argv.slice(2), opt = (k, d) => { const i = a.indexOf('--' + k); return i >= 0 ? a[i + 1] : d; };
const [file, out] = a.filter(x => !x.startsWith('--') && !a[a.indexOf(x) - 1]?.startsWith('--'));
const w = +opt('w', 1920), h = +opt('h', 1080), t = opt('t', null);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
const errs = []; p.on('pageerror', e => errs.push(String(e)));
await p.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: 'load' });
await p.evaluate(async () => { await document.fonts.ready; await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {}))); });
if (t !== null) await p.evaluate(t => window.__timelines && window.__timelines.main && window.__timelines.main.seek(+t, false), t);
await p.waitForTimeout(+opt("wait", 1500));   // SVG <image> textures decode asynchronously
await p.screenshot({ path: out, clip: { x: 0, y: 0, width: w, height: h } });
await b.close();
console.log('wrote', out, `${w}x${h}`, errs.length ? 'page errors: ' + errs.join(' | ') : '');
process.exit(errs.length ? 1 : 0);
