#!/usr/bin/env node
// Character lab (M3): render a motion demo with viewer/motion.html in headless Chromium (CPU WebGL), frame by frame.
//   node epoch-ledger/charlab/motion_render.mjs --demo epoch-ledger/charlab/motion/demos/d1.json --chars .runtime/charlab/out_m3 \
//        --three .runtime/charlab/three/r0.186.1 --out DIR [--quality standard|lean] [--step 1] [--from 0] [--to END] [--qa] [--mp4 FILE]
// Each frame is posed from the compiled performance (seekable, no state), rendered, and read back as PNG.
// timings.json: load, compile, per-frame render (GPU finished) and readback times. qa.json: foot pinning, floor, joints, eyes.
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const flag = k => args.includes('--' + k);
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const out = path.resolve(opt('out')); mkdirSync(out, { recursive: true });
const QUAL = { standard: { msaa: 4, shadow: 2048, inkPass: true }, lean: { msaa: 0, shadow: 1024, inkPass: false } };
const quality = QUAL[opt('quality', 'standard')];
const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png' };
const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e))); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
const t0 = Date.now();
await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/${opt('three')}&demo=/${opt('demo')}&out=/${opt('chars')}`);
for (let i = 0; i < 1200 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 500)); }
if (!(await pg.evaluate(() => !!window.ready))) { console.error('viewer failed', errs); process.exit(1); }
const info = await pg.evaluate(() => window.info); info.pageMs = Date.now() - t0;
console.log(JSON.stringify(info));
if (flag('analyze')) { const an = await pg.evaluate(() => window.analyze()); writeFileSync(`${out}/analyze.json`, JSON.stringify(an, null, 1)); console.log('ANALYZE ' + JSON.stringify(an)); }
if (flag('qa')) { const qa = await pg.evaluate(() => window.qa()); qa.cloth = await pg.evaluate(() => window.clothQA()); qa.blink = await pg.evaluate(() => window.blinkTest()); writeFileSync(`${out}/qa.json`, JSON.stringify(qa, null, 2)); console.log(JSON.stringify(qa)); }
const step = +opt('step', 1), from = +opt('from', 0), to = +opt('to', info.duration);
const times = [], reads = [];
let n = 0;
for (let f = Math.round(from * 30); f <= Math.round(to * 30); f += step) {
  const ms = await pg.evaluate(([t, qu]) => window.frame(t, qu), [f / 30, quality]);
  const r0 = Date.now();
  const data = await pg.evaluate(() => document.querySelector('canvas').toDataURL('image/png'));
  writeFileSync(`${out}/f${String(f).padStart(4, '0')}.png`, Buffer.from(data.split(',')[1], 'base64'));
  reads.push(Date.now() - r0); times.push(ms); n++;
  if (n % 30 === 0) console.log(`frame ${f}: render ${ms.toFixed(0)} ms`);
}
const st = a => { const s = [...a].sort((x, y) => x - y); return { n: s.length, mean: +(s.reduce((x, y) => x + y, 0) / s.length).toFixed(1), median: +s[s.length >> 1].toFixed(1), p95: +s[Math.floor(s.length * .95)].toFixed(1), max: +s[s.length - 1].toFixed(1) }; };
const timing = { quality: opt('quality', 'standard'), info, render_ms: st(times), readback_png_ms: st(reads), errors: errs, wall_s: (Date.now() - t0) / 1000 };
writeFileSync(`${out}/timings.json`, JSON.stringify(timing, null, 2));
console.log(JSON.stringify({ render_ms: timing.render_ms, readback_png_ms: timing.readback_png_ms, errors: errs.slice(0, 3) }));
await b.close(); srv.close();
if (opt('mp4') && step === 1) {
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-start_number', String(Math.round(from * 30)), '-i', `${out}/f%04d.png`,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', opt('mp4')]);
  console.log('mp4 →', opt('mp4'));
}
