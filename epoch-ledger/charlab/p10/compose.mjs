// P10 fast 2.5D compositor (experimental, opt-in; P9's animate.mjs is unchanged).
//
// Why it is fast (P9 rendered the 3D set every frame and re-rasterised vector characters, filters and masks every frame):
//   - the set is ONE still per camera set-up (plate + depth pass from the same camera), decoded once;
//   - camera motion is 2D (a slow zoom/pan of the plate) with depth-layered parallax: the far part of the room (depth
//     beyond `farFrom` metres) moves by a fraction (`farFactor`) of the near part, so the room still reads in depth;
//   - each character is rasterised ONCE per shot into bitmap layers at the scale it is shown: body, one head per
//     expression (a face swap is a bitmap swap), one per rig piece, with the window lighting baked into each layer;
//   - occluders (set geometry nearer than a character) and the near parallax layer are cut from the plate ONCE, as
//     transparent images, and drawn over the characters (no per-frame masks);
//   - per frame only CSS transforms and visibility change; capture is a fast lossless screenshot piped to ffmpeg, which
//     also adds the film grain and vignette;
//   - frame ranges (--from/--to, inclusive) let several processes render one shot in parallel (render_shot.mjs).
//
//   node epoch-ledger/charlab/p10/compose.mjs SHOT.json OUT.mp4 [--from F] [--to F] [--threads N]
//
// SHOT.json (written by prepare.py): {duration, plate, depth, pts:{name:[px,py,depth_m]}, window, cam2d:[[t, zoom, cx, cy]...],
//   farFrom, farFactor, grade:{vignette, grain}, chars:{id:{svg, rig?, feet, head, facing, faces, blinks, nods, tilts,
//   shifts, joints:{joint:[[t,deg]...]}, light?, occMargin?}}}
import { createRequire } from 'node:module'; import { readFileSync, writeFileSync } from 'node:fs'; import { spawn } from 'node:child_process';
import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { rigSVG } from './rig.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2); const [shotFile, out] = args;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? +args[i + 1] : d; };
const shot = JSON.parse(readFileSync(shotFile, 'utf8'));
const N = Math.round(shot.duration * 30), f0 = opt('from', 0), f1 = Math.min(opt('to', N - 1), N - 1);
for (const [id, c] of Object.entries(shot.chars)) {
  c.plain = c.svg;
  if (c.rig) { c.rigSpec = JSON.parse(readFileSync(path.resolve(HERE, c.rig), 'utf8')).pieces; c.svg = rigSVG(c.svg, c.rigSpec, { id: 'r_' + id }); }
}
const img64 = f => 'data:image/png;base64,' + readFileSync(f).toString('base64');
const html = path.join(path.dirname(path.resolve(out)), path.basename(out, '.mp4') + `_${f0}.html`);
const G = { vignette: 0.4, grain: 4, ...(shot.grade || {}) };
writeFileSync(html, `<!doctype html><html><head><meta charset=utf-8><style>
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#000}
#st{position:relative;width:1920px;height:1080px;overflow:hidden}
.cam{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0}
.ch{position:absolute;left:0;top:0;width:1px;height:1px;transform-origin:0 0}
.ly{position:absolute;display:block}
</style></head><body><div id=st><div id=far class=cam></div><div id=main class=cam></div></div>
<script>
const SHOT = ${JSON.stringify(shot)};
const NS = 'http://www.w3.org/2000/svg', clamp = (x, a, b) => Math.min(b, Math.max(a, x)), ss = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const kf = (K, t, d = 0) => { if (!K || !K.length) return d; if (t <= K[0][0]) return K[0][1]; for (let i = 1; i < K.length; i++) if (t < K[i][0]) {
  const u = ss((t - K[i - 1][0]) / (K[i][0] - K[i - 1][0])); return K[i - 1][1] + (K[i][1] - K[i - 1][1]) * u; } return K[K.length - 1][1]; };
const cam = t => { const K = SHOT.cam2d; if (t <= K[0][0]) return K[0].slice(1); for (let i = 1; i < K.length; i++) if (t < K[i][0]) {
  const u = ss((t - K[i - 1][0]) / (K[i][0] - K[i - 1][0])); return K[i].slice(1).map((v, j) => K[i - 1][j + 1] + (v - K[i - 1][j + 1]) * u); } return K[K.length - 1].slice(1); };
const load = src => new Promise((r, e) => { const i = new Image(); i.onload = () => r(i); i.onerror = () => e(new Error('image load failed')); i.src = src; });
const canvas = (w, h) => { const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); return c; };
const C = {};
// one bitmap of an SVG document (string) for user-space box [x0,y0,w,h] at k px per unit
async function raster(svgText, box, k) {
  const [x0, y0, w, h] = box;
  const s = svgText.replace(/^<svg([^>]*?) viewBox="[^"]*"/, '<svg$1').replace(/^<svg/, '<svg viewBox="' + [x0, y0, w, h].join(' ') + '" width="' + Math.round(w * k) + '" height="' + Math.round(h * k) + '"');
  const im = await load('data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s))));
  const cv = canvas(w * k, h * k); cv.getContext('2d').drawImage(im, 0, 0, cv.width, cv.height); return cv;
}
// the cut-out of the plate where keep(depth) holds, cropped to its bounding box: [canvas, x, y] or null
function cutout(P, dd, keep) {
  const cv = canvas(1920, 1080), g = cv.getContext('2d'); g.drawImage(P, 0, 0); const im = g.getImageData(0, 0, 1920, 1080), a = im.data;
  let x0 = 1920, y0 = 1080, x1 = -1, y1 = -1;
  for (let y = 0, i = 0; y < 1080; y++) for (let x = 0; x < 1920; x++, i += 4) {
    if (keep((dd[i] * 65536 + dd[i + 1] * 256 + dd[i + 2]) / 1000)) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; } else a[i + 3] = 0; }
  if (x1 < 0) return null;
  g.putImageData(im, 0, 0); const o = canvas(x1 - x0 + 1, y1 - y0 + 1); o.getContext('2d').drawImage(cv, -x0, -y0); return [o, x0, y0];
}
const place = (el, x, y, w, h) => { el.className = 'ly'; el.style.left = x + 'px'; el.style.top = y + 'px'; el.style.width = w + 'px'; el.style.height = h + 'px'; return el; };
async function setup(plate, depth) {
  const [P, D] = await Promise.all([load(plate), load(depth)]);
  const dc = canvas(1920, 1080), dg = dc.getContext('2d'); dg.drawImage(D, 0, 0); const dd = dg.getImageData(0, 0, 1920, 1080).data;
  const far = document.getElementById('far'), main = document.getElementById('main');
  far.appendChild(place(P.cloneNode(), 0, 0, 1920, 1080));                       // the whole plate also fills what the near layer uncovers
  const nearL = cutout(P, dd, d => d < SHOT.farFrom); if (nearL) main.appendChild(place(nearL[0], nearL[1], nearL[2], nearL[0].width, nearL[0].height));
  const zmax = Math.max(...SHOT.cam2d.map(q => q[1]));
  const order = Object.entries(SHOT.chars).sort((a, b) => SHOT.pts[b[1].feet][2] - SHOT.pts[a[1].feet][2]);   // far to near
  for (const [id, c] of order) {
    // measure the plain drawing (foot, neck, head top, extent) in root units
    const tmp = document.createElement('div'); tmp.innerHTML = c.plain; document.body.appendChild(tmp);
    const ts = tmp.querySelector('svg'), tvb = ts.viewBox.baseVal; ts.setAttribute('width', tvb.width); ts.setAttribute('height', tvb.height);
    const m0 = ts.getCTM().inverse(), pt = (el, x, y) => { const p = new DOMPoint(x, y).matrixTransform(m0.multiply(el.getCTM())); return [p.x, p.y]; };
    const BE = ts.querySelector('#BODY'), HE = ts.querySelector('#Head'), bb = BE.getBBox(), hb = HE.getBBox(), rg = ts.querySelector('g'), rb = rg.getBBox();
    const foot = pt(BE, bb.x + bb.width * 0.5, bb.y + bb.height), neck = pt(HE, hb.x + hb.width * .45, hb.y + hb.height * .93), top = pt(HE, hb.x, hb.y)[1];
    const r0 = pt(rg, rb.x, rb.y), r1 = pt(rg, rb.x + rb.width, rb.y + rb.height); tmp.remove();
    const F = SHOT.pts[c.feet], H = SHOT.pts[c.head], s = (F[1] - H[1]) / (foot[1] - top), flip = c.facing === 'left' ? -1 : 1;
    const k = s * zmax * 1.02;                                                      // px per unit of every bitmap layer
    const mg = (r1[0] - r0[0]) * 0.18, box = [r0[0] - mg, r0[1] - mg, r1[0] - r0[0] + 2 * mg, r1[1] - r0[1] + 2 * mg];
    // window light, fixed for a locked plate: which side of the drawing faces it; filter sizes in units (≈ px on screen)
    const win = SHOT.pts[SHOT.window], lx = win ? Math.sign(win[0] - F[0]) * flip : 1, u = 1.5;   // filter sizes in drawing units (scale with the figure)
    const L = { shadow: .26, rim: .30, tint: '#f3d9b0', tintA: .07, ...(c.light || {}) };
    const LIGHT = '<filter id="lt" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">' +
      '<feOffset in="SourceAlpha" dx="' + (-14 * lx * u) + '" dy="' + (4 * u) + '" result="o"/><feComposite in="SourceAlpha" in2="o" operator="out" result="b"/><feGaussianBlur in="b" stdDeviation="' + 3 * u + '" result="b2"/>' +
      '<feComposite in="b2" in2="SourceAlpha" operator="in" result="b3"/><feFlood flood-color="#2a170d" flood-opacity="' + L.shadow + '"/><feComposite in2="b3" operator="in" result="sh"/>' +
      '<feOffset in="SourceAlpha" dx="' + (5 * lx * u) + '" dy="' + (8 * u) + '" result="o2"/><feComposite in="SourceAlpha" in2="o2" operator="out" result="c"/><feGaussianBlur in="c" stdDeviation="' + 2 * u + '" result="c2"/>' +
      '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.2 2.4 0.4 0 -0.75" result="lum"/>' +   // the artist's ink lines are never lit
      '<feComposite in="c2" in2="lum" operator="in" result="c3"/><feFlood flood-color="#ffe6bd" flood-opacity="' + L.rim + '"/><feComposite in2="c3" operator="in" result="rim"/>' +
      '<feFlood flood-color="' + L.tint + '" flood-opacity="' + L.tintA + '"/><feComposite in2="SourceAlpha" operator="in" result="amb"/>' +
      '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="amb"/><feMergeNode in="sh"/><feMergeNode in="rim"/></feMerge></filter>';
    // a variant of the (rigged) drawing with only some layers kept, optionally lit, serialised
    const base = new DOMParser().parseFromString(c.svg, 'image/svg+xml').documentElement;
    const variant = (mod, lit = true) => { const d = base.cloneNode(true); const src = c.rig ? d.querySelector('defs > g') : d.querySelector('g'); mod(d, src);
      // light the drawing itself (the shared source), so rig pieces are cut from the lit figure: no light along a cut
      if (lit) { const df = document.createElementNS(NS, 'defs'); df.innerHTML = LIGHT; d.insertBefore(df, d.firstChild); const g = document.createElementNS(NS, 'g'); g.setAttribute('filter', 'url(#lt)');
        [...src.childNodes].forEach(n => g.appendChild(n)); src.appendChild(g); }
      return new XMLSerializer().serializeToString(d); };
    const hide = el => el && el.setAttribute('display', 'none');
    const pieces = c.rigSpec || [];
    const ch = document.createElement('div'); ch.className = 'ch'; main.appendChild(ch);
    const layer = async (mod, lit = true) => place(await raster(variant(mod, lit), box, k), box[0], box[1], box[2], box[3]);
    // contact shadow + a short cast shadow on the floor, from the full silhouette at rest (static)
    ch.appendChild(await layer(d => { const g = document.createElementNS(NS, 'g');
      g.innerHTML = '<defs><filter id="sil" x="-50%" y="-50%" width="200%" height="200%"><feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 .08  0 0 0 0 .05  0 0 0 0 .03  0 0 0 .22 0"/><feGaussianBlur stdDeviation="' + 9 * u + '"/></filter>' +
        '<radialGradient id="ct"><stop offset="0" stop-color="#140c06" stop-opacity=".55"/><stop offset="1" stop-color="#140c06" stop-opacity="0"/></radialGradient></defs>';
      const cast = document.createElementNS(NS, 'g'); cast.setAttribute('filter', 'url(#sil)');
      cast.setAttribute('transform', 'translate(' + foot[0] + ' ' + foot[1] + ') matrix(1 0 ' + (-0.35 * lx) + ' -0.14 0 0) translate(' + (-foot[0]) + ' ' + (-foot[1]) + ')');
      [...d.childNodes].filter(n => n.nodeName !== 'defs').forEach(n => cast.appendChild(n)); g.appendChild(cast);
      const w = (r1[0] - r0[0]) * .42; g.insertAdjacentHTML('afterbegin', '<ellipse cx="' + foot[0] + '" cy="' + foot[1] + '" rx="' + w + '" ry="' + w * .17 + '" fill="url(#ct)"/>'); d.appendChild(g); }, false));
    // keep one joint's own drawing (its descendants removed, its transform reset); discs only with the body; caps never
    const keepOnly = (d, keep) => { const kj = d.querySelector('[data-joint="' + keep + '"]');
      d.querySelectorAll('[data-joint]').forEach(n => { if (n !== kj && !n.contains(kj) && !kj.contains(n)) n.remove(); });
      d.querySelectorAll('[data-joint]').forEach(n => { if (n !== kj && n.contains(kj)) [...n.children].forEach(q => { if (!q.contains(kj) && q !== kj) q.remove(); }); });
      kj.removeAttribute('transform'); kj.querySelectorAll('[data-joint]').forEach(n => n.remove());
      d.querySelectorAll('.rig-cap').forEach(n => n.remove()); if (keep !== 'body') d.querySelectorAll('.rig-disc').forEach(n => n.remove()); };
    const JP = {};
    const pieceLayer = async sp => { const el = await layer((d, src) => { keepOnly(d, sp.id); hide(src.querySelector('#Head')); });
      const wrap = document.createElement('div'); wrap.className = 'ly'; wrap.style.left = '0px'; wrap.style.top = '0px'; wrap.style.width = '1px'; wrap.style.height = '1px';
      wrap.style.transformOrigin = sp.pivot[0] + 'px ' + sp.pivot[1] + 'px'; wrap.appendChild(el); JP[sp.id] = wrap;
      for (const kid of pieces.filter(q => q.parent === sp.id)) wrap.appendChild(await pieceLayer(kid)); return wrap; };
    // rig pieces under the body, the body (with joint discs), pieces over it, caps; heads (one per expression) on top
    for (const sp of pieces.filter(q => !q.parent && q.z === 'under')) ch.appendChild(await pieceLayer(sp));
    const body = await layer((d, src) => { if (c.rig) keepOnly(d, 'body'); hide(src.querySelector('#Head')); }); ch.appendChild(body);
    for (const sp of pieces.filter(q => !q.parent && q.z !== 'under')) ch.appendChild(await pieceLayer(sp));
    if (pieces.some(q => q.caps)) ch.appendChild(await layer(d => { d.querySelectorAll('[data-joint],.rig-disc').forEach(n => n.remove()); }, false));
    const heads = {};
    for (const f of [...new Set(c.faces.map(x => x[1]).concat(['Eyes Closed']))]) {
      const el = await layer((d, src) => { if (c.rig) { keepOnly(d, 'body'); d.querySelectorAll('.rig-disc').forEach(n => n.remove()); } hide(src.querySelector('#BODY'));
        src.querySelectorAll('[data-face]').forEach(g => g.setAttribute('style', 'display:' + (g.getAttribute('data-face') === f ? 'inline' : 'none'))); });
      el.style.transformOrigin = (neck[0] - box[0]) + 'px ' + (neck[1] - box[1]) + 'px'; el.style.visibility = 'hidden'; ch.appendChild(el); heads[f] = el; }
    body.style.transformOrigin = (foot[0] - box[0]) + 'px ' + (foot[1] - box[1]) + 'px';
    C[id] = { c, ch, body, heads, P: JP, foot, neck, s, flip, F, phase: id.length * 1.7 };
    // set geometry nearer than this character covers it: a static cut-out of the plate, above the character
    const oc = cutout(P, dd, d => d < F[2] - (c.occMargin ?? 0.3)); if (oc) main.appendChild(place(oc[0], oc[1], oc[2], oc[0].width, oc[0].height));
  }
  return true;
}
function faceAt(c, t) {
  const bl = (c.blinks || []).some(([a, b]) => t >= a && t < b); if (bl) return ['Eyes Closed', null];
  let cur = c.faces[0][1], prev = null, since = 99;
  for (const [ft, f] of c.faces) if (t >= ft) { prev = cur; cur = f; since = t - ft; }
  return since < 0.1 && prev && prev !== cur ? [cur, [prev, 1 - since / 0.1]] : [cur, null];
}
function headAngle(c, t) {
  let a = 0;
  for (const [t0, t1, deg] of c.tilts || []) a += deg * ss((t - t0) / 0.6) * (1 - ss((t - (t1 - 0.6)) / 0.6));
  for (const [tn, d] of c.nods || []) { const u = (t - tn) / d; if (u > 0 && u < 1) a += 6.5 * Math.sin(Math.PI * u) * (1 - 0.35 * u); }
  return a;
}
function sway(c, t, ph) { let a = 0.3 * Math.sin(2 * Math.PI * t / 5.3 + ph); for (const [ts, d, deg] of c.shifts || []) a += deg * ss((t - ts) / d); return a; }
let shown = [];
window.frame = f => {
  const t = f / 30, [z, cx, cy] = cam(t), ff = SHOT.farFactor, c0 = SHOT.cam2d[0];
  const tf = (zz, px, py) => 'translate(' + (960 - px * zz) + 'px,' + (540 - py * zz) + 'px) scale(' + zz + ')';
  document.getElementById('main').style.transform = tf(z, cx, cy);
  document.getElementById('far').style.transform = tf(1 + (z - 1) * ff, c0[2] + (cx - c0[2]) * ff, c0[3] + (cy - c0[3]) * ff);
  shown.forEach(e => { e.style.visibility = 'hidden'; e.style.opacity = 1; }); shown = [];
  for (const X of Object.values(C)) {
    const c = X.c, br = Math.sin(2 * Math.PI * t / 3.7 + X.phase), sw = sway(c, t, X.phase);
    X.ch.style.transform = 'translate(' + X.F[0] + 'px,' + X.F[1] + 'px) rotate(' + sw * X.flip + 'deg) scale(' + X.flip * X.s + ',' + X.s + ') translate(' + (-X.foot[0]) + 'px,' + (-X.foot[1]) + 'px)';
    X.body.style.transform = 'scale(1,' + (1 + 0.006 * br) + ')';
    const lift = -(X.foot[1] - X.neck[1]) * 0.006 * br, ha = headAngle(c, t), [fc, dis] = faceAt(c, t);
    for (const [nm, op] of [[fc, 1]].concat(dis ? [[dis[0], dis[1]]] : [])) { const e = X.heads[nm]; if (!e) continue;
      e.style.visibility = 'visible'; e.style.opacity = op; e.style.transform = 'translate(0px,' + lift + 'px) rotate(' + ha + 'deg)'; shown.push(e); }
    if (c.joints) for (const [j, K] of Object.entries(c.joints)) if (X.P[j]) X.P[j].style.transform = 'rotate(' + kf(K, t) + 'deg)';
  }
  return true;
};
</script></body></html>`);
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto('file://' + html);
const ts0 = Date.now();
await pg.evaluate(([p, d]) => setup(p, d), [img64(shot.plate), img64(shot.depth)]);
const setupS = +((Date.now() - ts0) / 1000).toFixed(2);
if (errs.length) { console.error(errs); process.exit(1); }
const cdp = await pg.context().newCDPSession(pg);
// grain and vignette in ffmpeg (cheap there; costly as full-frame SVG filters in the page)
const VF = `vignette=angle=${G.vignette.toFixed(2)},noise=alls=${G.grain}:allf=t,scale=out_color_matrix=bt709:out_range=tv`;
const ENC = ['-vf', VF, '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-threads', String(opt('threads', 2))];
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', ...ENC, out], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise(r => ff.on('close', r)); const t0 = Date.now(); let fr = 0; const prof = { frame: 0, capture: 0 };
for (let f = f0; f <= f1; f++) {
  const ta = Date.now(); await pg.evaluate(f => window.frame(f), f); const tb = Date.now();
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true }); prof.frame += tb - ta; prof.capture += Date.now() - tb;
  if (!ff.stdin.write(Buffer.from(data, 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); fr++;
}
ff.stdin.end(); await done; await b.close();
if (errs.length) { console.error(errs); process.exit(1); }
console.log(JSON.stringify({ out, frames: fr, setup_s: setupS, s_per_frame: +((Date.now() - t0) / 1000 / fr).toFixed(3), ms_update: Math.round(prof.frame / fr), ms_capture: Math.round(prof.capture / fr) }));
