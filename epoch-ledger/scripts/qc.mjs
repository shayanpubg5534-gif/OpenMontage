#!/usr/bin/env node
// Epoch Ledger automated QC (STANDARD.md §2.6, §5). Objective checks only; passing them is not evidence of creative quality.
//
//   node epoch-ledger/scripts/qc.mjs <workspace>/index.html [--video out.mp4] [--start 0] [--end D] [--every 0.5]
//        [--frames 0,1.5,6.45] [--seed 7] [--no-determinism] [--json report.json] [--browser path]
//   node epoch-ledger/scripts/qc.mjs --video out.mp4            (frame scan + loudness only)
//
// 1. Determinism (composition): every sampled frame is drawn twice, once in time order and once in a shuffled order
//    from a different prior state, and the two pixel captures must be identical. A difference means a frame depends
//    on what was drawn before it: tweens fighting over one property, state set outside the timeline, Math.random or
//    clocks. The idea comes from OpenFilm's `look` check (MIT, github.com/openfilm-dev); this is an original
//    implementation for HyperFrames compositions (window.__timelines.main + data-start/data-duration clips).
//    Frame 0 and each clip start are always sampled, because start states that are not applied at t=0 show up there.
// 2. Frame scan (video, ffmpeg): black stretches, single-frame flashes (a luma spike that returns next frame, which
//    is how a missing start state looks), frozen stretches (warning: a deliberate hold can trip it), and the opening
//    frames (frame 0 must match frame 1 closely unless the film opens on a cut).
// 3. Loudness: integrated LUFS (target about −16) and true peak.
// 4. Timing study (information only): detected cut times, so they can be compared with the narration words.
// Exit 1 if a hard check fails (determinism, black, flash, opening jump, loudness far out of range).
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { writeFileSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import path from 'node:path';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const flag = k => args.includes('--' + k);
const valued = new Set(['video', 'start', 'end', 'every', 'frames', 'seed', 'json', 'browser', 'lufs']);
const file = args.find((a, i) => !a.startsWith('--') && !(i > 0 && valued.has(args[i - 1].slice(2))));
const video = opt('video');
if (!file && !video) { console.error('usage: qc.mjs index.html [--video out.mp4] [--every s] [--json out]'); process.exit(2); }

const report = { determinism: null, video: null, loudness: null, study: null, failures: [], warnings: [] };
const fail = m => { report.failures.push(m); console.log('✗', m); };
const warn = m => { report.warnings.push(m); console.log('⚠', m); };
const ok = m => console.log('✓', m);

// ---------------------------------------------------------------- 1. determinism
// State signature of everything that can paint: attributes, inline style and own text of rendered elements (inert
// GSAP identity values normalised away). Same signature + different pixels = Chromium raster noise, not a timeline bug.
const STATE = `(() => { const out = []; const N = v => (v || '').replace(/matrix\\(1,\\s*0,\\s*0,\\s*1,\\s*0,\\s*0\\)/g, '')
    .replace(/(translate|rotate|scale): none;|transform: translate\\(0px, 0px\\);|transform-origin:[^;]*;/g, '').replace(/\\s+/g, ' ').trim();
  const walk = (e, path) => { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return;
    const at = Array.from(e.attributes).filter(a => !['style', 'data-svg-origin', 'opacity'].includes(a.name)).map(a => [a.name, N(a.value)]).filter(a => a[1] !== '').map(a => a.join('=')).join(' ');
    const txt = Array.from(e.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    out.push(path + '|' + at + '|' + N(e.style.cssText.replace(/opacity:[^;]*;?/g, '')) + '|o' + (+cs.opacity).toFixed(3) + '|' + txt);
    Array.from(e.children).forEach((c, i) => walk(c, path + '.' + i)); };
  walk(document.getElementById('root'), 'r'); return out.join('\\n'); })()`;

async function determinism() {
  const { chromium } = createRequire(import.meta.url)('playwright');
  const exe = opt('browser');
  // partial raster re-rasterises only invalidated tile regions, so anti-aliasing would depend on the previous frame
  const browser = await chromium.launch({ ...(exe ? { executablePath: exe } : {}), args: ['--disable-partial-raster'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: 'load' });
  for (let k = 0; k < 120 && !(await page.evaluate(() => !!(window.__timelines && window.__timelines.main))); k++) await page.waitForTimeout(250);
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {}))); });
  const meta = await page.evaluate(() => {
    const root = document.getElementById('root');
    const starts = Array.from(document.querySelectorAll('[data-start][data-duration]'))
      .filter(c => c !== root && c.tagName !== 'AUDIO').map(c => +c.dataset.start);
    return { duration: +root.dataset.duration, starts };
  });
  const fps = 30, snap = t => Math.round(t * fps) / fps;
  const start = +opt('start', 0), end = Math.min(+opt('end', meta.duration), meta.duration - 1 / fps);
  let times;
  if (opt('frames')) times = opt('frames').split(',').map(Number);
  else {
    const every = +opt('every', 0.5);
    times = [];
    for (let t = start; t <= end + 1e-6; t += every) times.push(t);
    for (const s of meta.starts) if (s >= start && s <= end) times.push(s, s + 1 / fps);   // clip starts + 1 frame
    times.push(start);
  }
  times = [...new Set(times.map(snap).filter(t => t >= start && t <= end))].sort((a, b) => a - b);

  const draw = async t => {
    await page.evaluate(t => {
      document.querySelectorAll('[data-start][data-duration]').forEach(c => {     // emulate HyperFrames clip windows
        if (c.id === 'root' || c.tagName === 'AUDIO') return; const s = +c.dataset.start, d = +c.dataset.duration;
        c.style.visibility = t >= s && t < s + d ? 'visible' : 'hidden'; });
      window.__timelines.main.seek(t, false);
    }, t);
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    const png = await page.screenshot({ type: 'png' });
    return { h: createHash('sha1').update(png).digest('hex'), png, state: await page.evaluate(STATE) };
  };
  // where two captures differ: bounding box and pixel count (decoded in a blank page's canvas)
  const diffBox = async (a, b) => {
    const p2 = await browser.newPage();
    const r = await p2.evaluate(async ([a, b]) => {
      const load = s => new Promise(res => { const i = new Image(); i.onload = () => res(i); i.src = 'data:image/png;base64,' + s; });
      const [A, B] = await Promise.all([load(a), load(b)]);
      const px = i => { const c = document.createElement('canvas'); c.width = i.width; c.height = i.height; const x = c.getContext('2d'); x.drawImage(i, 0, 0); return x.getImageData(0, 0, i.width, i.height).data; };
      const da = px(A), db = px(B); let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1, n = 0, mx = 0;
      for (let k = 0; k < da.length; k += 4) { const d = Math.max(Math.abs(da[k] - db[k]), Math.abs(da[k + 1] - db[k + 1]), Math.abs(da[k + 2] - db[k + 2]));
        if (d > 2) { const q = k / 4, x = q % A.width, y = (q / A.width) | 0; n++; mx = Math.max(mx, d); x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); } }
      return n ? { x: x0, y: y0, w: x1 - x0 + 1, h: y1 - y0 + 1, px: n, max: mx } : { px: 0, max: 0 };
    }, [a.toString('base64'), b.toString('base64')]);
    await p2.close(); return r;
  };
  const t0 = Date.now();
  const first = new Map();
  for (const t of times) first.set(t, await draw(t));
  let seed = +opt('seed', 7);
  const rnd = () => ((seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
  const order = [...times].sort(() => rnd() - .5);
  // jump to the far end first so the second pass starts from a very different state
  await draw(end);
  const bad = [], noise = [], detail = {};
  for (const t of order) {
    const a = first.get(t), d = await draw(t);
    if (d.h === a.h) continue;
    (d.state === a.state ? noise : bad).push(t);
    if (Object.keys(detail).length < 40) {
      const A = a.state.split('\n'), D = new Set(d.state.split('\n')), Aset = new Set(A);
      const changed = A.filter(x => !D.has(x)).slice(0, 4).concat(d.state.split('\n').filter(x => !Aset.has(x)).slice(0, 4)).map(x => x.slice(0, 220));
      detail[t.toFixed(3)] = { ...(await diffBox(a.png, d.png)), state_differs: d.state !== a.state, changed };
    }
  }
  await browser.close();
  bad.sort((a, b) => a - b); noise.sort((a, b) => a - b);
  report.determinism = { frames: times.length, mismatches: bad, raster_noise: noise, regions: detail, page_errors: errors, seconds: (Date.now() - t0) / 1000 };
  const line = t => { const r = detail[t.toFixed(3)]; return `    ${t.toFixed(3)}s` + (r && r.px ? `  ${r.px} px (max Δ ${r.max}) in x ${r.x}–${r.x + r.w}, y ${r.y}–${r.y + r.h}` : r ? '  (encoding-level difference only)' : ''); };
  if (errors.length) fail(`page errors: ${errors.slice(0, 3).join(' | ')}`);
  if (bad.length) {
    fail(`determinism: ${bad.length}/${times.length} frames have a different element state when drawn out of order`);
    bad.slice(0, 12).forEach(t => { console.log(line(t)); (detail[t.toFixed(3)]?.changed || []).slice(0, 4).forEach(c => console.log('        ' + c)); });
  }
  else ok(`determinism: ${times.length} frames have identical element state in time order and shuffled order (${report.determinism.seconds.toFixed(0)} s)`);
  if (noise.length) {
    const big = noise.filter(t => (detail[t.toFixed(3)] || {}).max > 96);
    warn(`renderer: ${noise.length} frame(s) with identical state but slightly different pixels (Chromium rasterisation, not the timeline)${big.length ? '; ' + big.length + ' exceed Δ 96 — inspect' : ''}`);
    noise.slice(0, 6).forEach(t => console.log(line(t)));
  }
}

// ---------------------------------------------------------------- 2–4. video
// ffmpeg writes filter reports to stderr: capture stdout + stderr whatever the exit code
const ffe = (a) => { const r = spawnSync('ffmpeg', ['-hide_banner', '-nostats', ...a], { encoding: 'utf8', maxBuffer: 1 << 28 }); return (r.stdout || '') + (r.stderr || ''); };
const ff = ffe;

function videoScan() {
  if (!existsSync(video)) { fail(`video not found: ${video}`); return; }
  const v = { black: [], flashes: [], freezes: [], opening_jump: null, cuts: [] };
  // per-frame mean luma (one pass)
  const lum = [];
  const out = ffe(['-i', video, '-vf', 'scale=320:-1,signalstats,metadata=print:key=lavfi.signalstats.YAVG', '-an', '-f', 'null', '-']);
  for (const m of out.matchAll(/YAVG=([\d.]+)/g)) lum.push(+m[1]);
  const fps = 30;
  // black: mean luma below 18 (of 255) for ≥ 2 frames, excluding a fade at the very start/end ( ≤ 0.5 s )
  let run = null;
  lum.forEach((y, i) => {
    if (y < 18) { run = run ?? i; } else if (run !== null) { if (i - run >= 2) v.black.push([run / fps, i / fps]); run = null; }
  });
  if (run !== null && lum.length - run >= 2) v.black.push([run / fps, lum.length / fps]);
  const dur = lum.length / fps;
  v.black = v.black.filter(([a, b]) => !((a < .02 && b <= .5) || (a >= dur - .5)));
  // flash: one frame jumps ≥ 25 luma away from both neighbours, which agree with each other (|prev-next| < 6)
  for (let i = 1; i < lum.length - 1; i++) {
    const d1 = lum[i] - lum[i - 1], d2 = lum[i] - lum[i + 1];
    if (Math.abs(d1) >= 25 && Math.abs(d2) >= 25 && Math.sign(d1) === Math.sign(d2) && Math.abs(lum[i - 1] - lum[i + 1]) < 6) v.flashes.push(i / fps);
  }
  // opening: frame 0 vs frame 1 (mean absolute difference of luma, full frame)
  if (lum.length > 2) {
    const d01 = Math.abs(lum[0] - lum[1]), d12 = Math.abs(lum[1] - lum[2]);
    const diff = ffe(['-i', video, '-vf', "select='lt(n\\,2)',scale=480:-1,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG", '-an', '-frames:v', '2', '-f', 'null', '-']);
    const m = [...diff.matchAll(/YAVG=([\d.]+)/g)].map(x => +x[1]);
    v.opening_jump = { luma_0: lum[0], luma_1: lum[1], mean_abs_diff_0_1: m.length ? m[m.length - 1] : null, luma_step_1_2: d12 };
    if ((m.length && m[m.length - 1] > 12) || d01 > 15) v.opening_flag = true;
  }
  // freeze: ≥ 3 s with no visible change (captions change on words, so this is rare in narrated film)
  const fz = ff(['-i', video, '-vf', 'freezedetect=n=0.0008:d=3', '-an', '-f', 'null', '-']);
  for (const m of fz.matchAll(/freeze_start: ([\d.]+)[\s\S]*?freeze_end: ([\d.]+)/g)) v.freezes.push([+m[1], +m[2]]);
  // study: cut times
  const sc = ffe(['-i', video, '-vf', "select='gt(scene,0.32)',showinfo", '-an', '-f', 'null', '-']);
  for (const m of sc.matchAll(/pts_time:([\d.]+)/g)) v.cuts.push(+(+m[1]).toFixed(3));
  v.frames = lum.length;
  report.video = v;
  if (!lum.length) { fail('frame scan: could not read frames (is ffmpeg installed?)'); return; }
  v.black.length ? fail(`black frames at ${v.black.map(([a, b]) => `${a.toFixed(2)}–${b.toFixed(2)}s`).join(', ')}`) : ok('no black stretches');
  v.flashes.length ? fail(`single-frame flashes at ${v.flashes.slice(0, 10).map(t => t.toFixed(3) + 's').join(', ')}`) : ok('no single-frame flashes');
  v.opening_flag ? fail(`opening: frame 0 differs from frame 1 (mean |Δ| ${v.opening_jump.mean_abs_diff_0_1?.toFixed(1)}): a start state is not applied at t=0`)
                 : ok(`opening frames consistent (mean |Δ| 0→1 ${v.opening_jump?.mean_abs_diff_0_1?.toFixed(2)})`);
  v.freezes.length ? warn(`frozen ≥3 s at ${v.freezes.map(([a, b]) => `${a.toFixed(1)}–${b.toFixed(1)}s`).join(', ')} (fine if deliberate)`) : ok('no frozen stretches ≥ 3 s');
  ok(`study: ${v.cuts.length} cuts detected${v.cuts.length ? ' at ' + v.cuts.slice(0, 20).join(', ') + 's' : ''} (information only)`);
}

function loudness() {
  const out = ff(['-i', video, '-af', 'ebur128=peak=true', '-vn', '-f', 'null', '-']);
  const I = out.match(/Integrated loudness:\s+I:\s+(-?[\d.]+|-inf) LUFS/), P = out.match(/True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS/);
  if (!I) { warn('loudness: no audio stream measured'); return; }
  const lufs = +I[1], peak = P ? +P[1] : null, target = +opt('lufs', -16);
  report.loudness = { integrated_lufs: lufs, true_peak_dbfs: peak, target };
  if (!isFinite(lufs) || Math.abs(lufs - target) > 3) fail(`loudness ${I[1]} LUFS (target ${target} ±3)`);
  else if (Math.abs(lufs - target) > 1.5) warn(`loudness ${lufs} LUFS (target ${target})`);
  else ok(`loudness ${lufs} LUFS, true peak ${peak} dBFS`);
  if (peak !== null && peak > -0.5) warn(`true peak ${peak} dBFS is near clipping`);
}

if (file && !flag('no-determinism')) await determinism();
if (video) { videoScan(); loudness(); }
if (opt('json')) writeFileSync(opt('json'), JSON.stringify(report, null, 2));
console.log(report.failures.length ? `QC FAILED — ${report.failures.length} problem(s)` : `QC passed${report.warnings.length ? ` with ${report.warnings.length} warning(s)` : ''}`);
process.exit(report.failures.length ? 1 : 0);
