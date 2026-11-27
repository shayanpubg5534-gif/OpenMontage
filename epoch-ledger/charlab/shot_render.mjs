// Character lab (P5): continuous-session renderer for cinematic 3D shots (experimental, opt-in).
//
// HyperFrames' local planner splits a render into ~10-frame chunks, each a fresh page; a cinematic 3D shot then pays a
// full cold start (character, set, textures, ~14 s of shader compilation, cache anchors) every 10 frames (P4 report).
// This renderer loads a shot ONCE and renders every frame of it in order, at native 1080p30, in one browser session:
//
//   • frames go straight from the canvas (PNG) into ffmpeg through a pipe, in segments of --seg frames; each finished
//     segment is kept, so an interrupted render resumes at the first missing segment (frames are deterministic: the
//     animation is compiled, and the environment-cache anchors are a pure function of time)
//   • segments are joined by stream copy (no second encode); the shot is encoded once, near-losslessly (x264 CRF 8,
//     closed GOP per segment), and HyperFrames composites it once more into the final video
//   • the result is cached under a fingerprint of everything the shot depends on (demo, set, textures, characters,
//     lip-sync tracks, runtime code, three.js build, quality profile, frame range, encoder settings); a revision of one
//     shot re-renders only that shot
//
//   node epoch-ledger/charlab/shot_render.mjs --demo D.json --chars DIR --three DIR --quality cin_balanced
//        [--from 0] [--to DUR] [--seg 30] [--cache .runtime/charlab/shotcache] [--out shot.mp4] [--force]
// prints one JSON line: { mp4, fingerprint, cached, timings }
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync, readdirSync, copyFileSync, renameSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { spawn, execFileSync } from 'node:child_process';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; }, flag = k => args.includes('--' + k);
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const HERE = path.join(ROOT, 'epoch-ledger/charlab');
const FPS = 30, SEG = +opt('seg', 30), CRF = 8, QUALITY = opt('quality', 'cin_balanced');
// BT.709 matrix + tags: an untagged intermediate is converted with BT.601 by default and read back as BT.709 (a colour shift)
const ENC = ['-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', String(CRF), '-pix_fmt', 'yuv420p', '-g', String(SEG), '-keyint_min', String(SEG), '-sc_threshold', '0', '-bf', '0'];
const t0 = Date.now();
const rel = p => p.replace(/^\//, ''), abs = p => path.join(ROOT, rel(p));

// ── fingerprint ─────────────────────────────────────────────────────────────────────────────────────────────────────
const demoPath = opt('demo'), demo = JSON.parse(readFileSync(abs(demoPath), 'utf8'));
const files = new Set([path.normalize(rel(demoPath))]);
const add = p => { if (p && existsSync(abs(p)) && !statSync(abs(p)).isDirectory()) files.add(path.normalize(rel(p))); };   // one canonical repo-relative name per file
const addDir = d => { if (existsSync(abs(d))) for (const f of readdirSync(abs(d), { recursive: true })) { const p = path.join(rel(d), String(f)); if (!statSync(abs(p)).isDirectory()) files.add(p); } };
if (demo.set) { add(demo.set); const st = JSON.parse(readFileSync(abs(demo.set), 'utf8'));
  if (st.window?.backdrop?.image) add(st.window.backdrop.image);
  for (const it of st.items || []) add(it.image);
  if (demo.look === 'cinematic' && st.cinematic) { const tex = st.cinematic.textures || '/.runtime/charlab/textures';
    for (const r of Object.values(st.cinematic.materials || {})) if (r.set) addDir(path.join(tex, r.set)); } }
if (demo.plate) add(demo.plate);
for (const [id, a] of Object.entries(demo.actors || {})) { add(path.join(opt('chars'), id + '.glb')); if (!a.pbr) addDir(path.join(opt('chars'), id + '_tex'));
  for (const sp of a.speech || []) add(sp.src); }
for (const f of readdirSync(path.join(HERE, 'motion'))) if (f.endsWith('.js')) files.add(path.join('epoch-ledger/charlab/motion', f));
files.add('epoch-ledger/charlab/viewer/motion.html'); files.add('epoch-ledger/charlab/shot_render.mjs'); files.add(path.join(rel(opt('three')), 'package/package.json'));
const from = +opt('from', 0), to = +opt('to', demo.duration), f0 = Math.round(from * FPS), f1 = Math.ceil(to * FPS - 1e-6) - 1;   // [from, to): every frame the composition samples
const h = createHash('sha256');
for (const p of [...files].sort()) { h.update(p + '\0'); h.update(readFileSync(abs(p))); }
h.update(JSON.stringify({ QUALITY, f0, f1, FPS, SEG, ENC }));
const fp = h.digest('hex').slice(0, 24);
if (flag('fingerprint-only')) { console.log(JSON.stringify({ fingerprint: fp, inputs: [...files].sort() })); process.exit(0); }
const cacheRoot = path.resolve(opt('cache', path.join(ROOT, '.runtime/charlab/shotcache'))), dir = path.join(cacheRoot, fp), final = path.join(dir, 'shot.mp4');
mkdirSync(dir, { recursive: true });
const done = (cached, timings) => { const out = opt('out'); if (out) { mkdirSync(path.dirname(path.resolve(out)), { recursive: true }); copyFileSync(final, path.resolve(out)); }
  console.log(JSON.stringify({ mp4: out ? path.resolve(out) : final, fingerprint: fp, cached, frames: f1 - f0 + 1, inputs: files.size, timings })); };
if (existsSync(final) && !flag('force')) { done(true, { wall_s: (Date.now() - t0) / 1000 }); process.exit(0); }
writeFileSync(path.join(dir, 'inputs.json'), JSON.stringify({ demo: demoPath, quality: QUALITY, from, to, files: [...files].sort() }, null, 1));

// ── segments still to render (resume) ───────────────────────────────────────────────────────────────────────────────
const segs = []; for (let s = f0; s <= f1; s += SEG) segs.push([s, Math.min(f1, s + SEG - 1)]);
const segFile = ([a]) => path.join(dir, `seg_${String(a).padStart(5, '0')}.mp4`);
const nFrames = f => { try { return +execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', f]).toString().trim(); } catch { return -1; } };
const todo = segs.filter(s => !(existsSync(segFile(s)) && nFrames(segFile(s)) === s[1] - s[0] + 1));
const timings = { segments: segs.length, resumed_segments: segs.length - todo.length, frames_rendered: todo.reduce((n, [a, b]) => n + b - a + 1, 0) };

if (todo.length) {
  const T = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg' };
  const srv = createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
    if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': T[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); }).listen(0);
  const tb = Date.now(); const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto(`http://127.0.0.1:${srv.address().port}/epoch-ledger/charlab/viewer/motion.html?three=/${rel(opt('three'))}&demo=/${rel(demoPath)}&out=/${rel(opt('chars'))}`);
  for (let i = 0; i < 1200 && !errs.length; i++) { if (await pg.evaluate(() => !!window.ready)) break; await new Promise(r => setTimeout(r, 250)); }
  if (errs.length || !(await pg.evaluate(() => !!window.ready))) { console.error('shot load failed', errs); process.exit(1); }
  timings.init_s = (Date.now() - tb) / 1000;                                        // browser + load + compile
  const tw = Date.now();
  await pg.evaluate(async q => { const { QUALITY } = await import('../motion/runtime.js'); window.__q = QUALITY[q]; window.frame(0, window.__q); }, QUALITY);   // shader warm-up
  timings.warmup_s = (Date.now() - tw) / 1000;
  let rMs = 0, cMs = 0;
  for (const s of todo) {
    const tmp = segFile(s) + '.part.mp4';
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-', ...ENC, tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    const closed = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
    for (let f = s[0]; f <= s[1]; f++) {
      const r = await pg.evaluate(f => { const t0 = performance.now(); window.frame(f / 30, window.__q); const t1 = performance.now();
        const png = document.querySelector('canvas').toDataURL('image/png'); return { png, r: t1 - t0, c: performance.now() - t1 }; }, f);
      rMs += r.r; cMs += r.c;
      if (!ff.stdin.write(Buffer.from(r.png.slice(r.png.indexOf(',') + 1), 'base64'))) await new Promise(res => ff.stdin.once('drain', res));
    }
    ff.stdin.end(); await closed; renameSync(tmp, segFile(s));                         // a segment exists only once complete
  }
  timings.render_frames_s = rMs / 1000; timings.png_capture_s = cMs / 1000; timings.loop_s = (Date.now() - tw) / 1000 - timings.warmup_s;
  await b.close(); srv.close();
  if (errs.length) { console.error('page errors', errs); process.exit(1); }
}
// ── join (stream copy) ──────────────────────────────────────────────────────────────────────────────────────────────
const tj = Date.now();
writeFileSync(path.join(dir, 'list.txt'), segs.map(s => `file '${path.basename(segFile(s))}'`).join('\n') + '\n');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'), '-c', 'copy', '-movflags', '+faststart', final + '.part.mp4']);
renameSync(final + '.part.mp4', final);
timings.join_s = (Date.now() - tj) / 1000; timings.wall_s = (Date.now() - t0) / 1000;
writeFileSync(path.join(dir, 'timings.json'), JSON.stringify(timings, null, 1));
if (nFrames(final) !== f1 - f0 + 1) { console.error('frame count mismatch', nFrames(final), f1 - f0 + 1); process.exit(1); }
for (const s of segs) rmSync(segFile(s), { force: true });                             // the joined shot is the cache entry
done(false, timings);
