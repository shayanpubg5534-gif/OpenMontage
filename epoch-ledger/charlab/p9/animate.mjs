// P9: render a 2.5D animated shot. Open Peeps characters (artist vector art) over a rendered, painterly-treated plate
// of the bank set, placed every frame through the plate's own camera (track.json), occluded by the desk (matte),
// with layer animation only: irregular blinks (face swap), breathing, weight shifts (rotation about the feet: no foot
// sliding), head tilts and nods (rotation about the neck), expression changes (face swaps with a 3-frame dissolve), and
// limited cut-out arm beats (a clipped piece of the drawing rotated a few degrees about the elbow). Lighting: form
// shadow and rim from the window direction, ambient tint, contact and cast shadows, depth-of-field blur, film grain.
//   node epoch-ledger/charlab/p9/animate.mjs SHOT.json PLATE_DIR TRACK_DIR OUT.mp4 [--from F --to F]
import { createRequire } from 'node:module'; import { readFileSync, writeFileSync } from 'node:fs'; import { spawn } from 'node:child_process';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2); const [shotFile, plateDir, trackDir, out] = args;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? +args[i + 1] : d; };
const shot = JSON.parse(readFileSync(shotFile, 'utf8')); const track = JSON.parse(readFileSync(path.join(trackDir, 'track.json'), 'utf8')).frames;
const N = Math.min(track.length, Math.round(shot.duration * 30)); const f0 = opt('from', 0), f1 = opt('to', N - 1);
const html = path.join(path.dirname(path.resolve(out)), path.basename(out, '.mp4') + '.html');
writeFileSync(html, `<!doctype html><html><head><meta charset=utf-8><style>
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#000}
#st{position:relative;width:1920px;height:1080px;overflow:hidden}
.full{position:absolute;left:0;top:0;width:1920px;height:1080px}
.ch{position:absolute;left:0;top:0;transform-origin:0 0}
.ch svg{overflow:visible;display:block}
.occ{position:absolute;left:0;top:0;width:1920px;height:1080px;-webkit-mask-size:1920px 1080px;mask-size:1920px 1080px;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}
#vig{background:radial-gradient(ellipse at 52% 46%,rgba(0,0,0,0) 52%,rgba(24,14,6,.45) 100%)}
</style></head><body><div id=st>
<img id=plate class=full><div id=people class=full></div>
<svg id=fg class=full viewBox="0 0 1920 1080"><defs><filter id=fgb x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur id=fgbs stdDeviation="12"/></filter></defs>
 <g id=plant filter="url(#fgb)" opacity=".95"><path d="M0 0 C -40 -180 -10 -330 30 -420 C 50 -300 40 -150 12 0 Z" fill="#1a2619"/>
 <path d="M6 0 C 60 -150 150 -230 230 -260 C 170 -190 90 -90 30 0 Z" fill="#203020"/><path d="M-4 0 C -80 -120 -180 -170 -250 -170 C -170 -120 -90 -60 -20 0 Z" fill="#172217"/>
 <path d="M10 0 C 40 -220 120 -360 190 -430 C 150 -300 90 -150 30 0 Z" fill="#1d2b1c"/></g></svg>
<svg class=full viewBox="0 0 1920 1080" style="mix-blend-mode:multiply;opacity:.10"><filter id=gr><feTurbulence id=grt type=fractalNoise baseFrequency=".85" numOctaves="2" seed="1"/><feColorMatrix type=saturate values="0"/></filter><rect width=1920 height=1080 filter="url(#gr)"/></svg>
<div id=vig class=full></div></div>
<script>
const SHOT = ${JSON.stringify(shot)}, TRACK = ${JSON.stringify(track)}, PLATE = ${JSON.stringify(path.resolve(plateDir))}, TD = ${JSON.stringify(path.resolve(trackDir))};
const NS = 'http://www.w3.org/2000/svg', clamp = (x, a, b) => Math.min(b, Math.max(a, x)), ss = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const C = {};
for (const [id, c] of Object.entries(SHOT.chars)) {
  const host = document.createElement('div'); host.className = 'occ'; document.getElementById('people').appendChild(host);   // occlusion mask applies here (untransformed)
  const w = document.createElement('div'); w.className = 'ch'; w.innerHTML = c.svg; host.appendChild(w);
  const svg = w.querySelector('svg'), vb = svg.viewBox.baseVal; svg.setAttribute('width', vb.width); svg.setAttribute('height', vb.height);
  const root = svg.querySelector('g'); root.id = 'c_' + id;
  const wrap = (el, cls) => { const g = document.createElementNS(NS, 'g'); g.setAttribute('class', cls); el.parentNode.insertBefore(g, el); g.appendChild(el); return g; };
  const body = wrap(svg.querySelector('#BODY'), 'a-body'), head = wrap(svg.querySelector('#Head'), 'a-head');
  const bb = root.getBBox(), hb = head.getBBox();
  const foot = [bb.x + bb.width * .5, bb.y + bb.height], neck = [hb.x + hb.width * .45, hb.y + hb.height * .93];
  const faces = [...svg.querySelectorAll('[data-face]')];
  let arm = null;
  if (c.arm) {                                     // limited cut-out: a clipped copy of the body drawing, rotated at the elbow
    const r = c.arm.region, R = [bb.x + bb.width * r[0], bb.y + bb.height * r[1], bb.x + bb.width * r[2], bb.y + bb.height * r[3]];
    const P = [bb.x + bb.width * c.arm.pivot[0], bb.y + bb.height * c.arm.pivot[1]];
    const defs = document.createElementNS(NS, 'defs');
    defs.innerHTML = '<clipPath id="ac_' + id + '"><rect x="' + R[0] + '" y="' + R[1] + '" width="' + (R[2] - R[0]) + '" height="' + (R[3] - R[1]) + '"/></clipPath>' +
      '<mask id="am_' + id + '" maskUnits="userSpaceOnUse" x="-5000" y="-5000" width="10000" height="10000"><rect x="-5000" y="-5000" width="10000" height="10000" fill="#fff"/><rect x="' + R[0] + '" y="' + R[1] + '" width="' + (R[2] - R[0]) + '" height="' + (R[3] - R[1]) + '" fill="#000"/></mask>';
    svg.prepend(defs);
    const orig = body.firstChild; const piece = orig.cloneNode(true); piece.removeAttribute('id');
    const ag = document.createElementNS(NS, 'g'); const cg = document.createElementNS(NS, 'g'); cg.setAttribute('clip-path', 'url(#ac_' + id + ')');
    cg.appendChild(piece); ag.appendChild(cg); body.appendChild(ag);
    const ow = document.createElementNS(NS, 'g'); body.insertBefore(ow, orig); ow.appendChild(orig); ow.setAttribute('mask', 'url(#am_' + id + ')');   // mask in character space
    arm = { g: ag, P, beats: c.arm.beats };
  }
  // lighting: silhouette-derived form shadow (side away from the window) and rim (window side), ambient tint
  const defs = document.createElementNS(NS, 'defs');
  defs.innerHTML = '<filter id="fs_' + id + '" x="-20%" y="-20%" width="140%" height="140%"><feOffset id="fso_' + id + '" in="SourceAlpha" dx="-14" dy="-4" result="o"/>' +
    '<feComposite in="SourceAlpha" in2="o" operator="out" result="b"/><feGaussianBlur in="b" stdDeviation="2.5" result="b2"/><feFlood flood-color="#2a170d" flood-opacity=".34"/><feComposite in2="b2" operator="in"/></filter>' +
    '<filter id="rl_' + id + '" x="-20%" y="-20%" width="140%" height="140%"><feOffset id="rlo_' + id + '" in="SourceAlpha" dx="5" dy="10" result="o"/>' +
    '<feComposite in="SourceAlpha" in2="o" operator="out" result="b"/><feGaussianBlur in="b" stdDeviation="1.8" result="b2"/><feFlood flood-color="#ffe2b0" flood-opacity=".32"/><feComposite in2="b2" operator="in"/></filter>' +
    '<filter id="amb_' + id + '" x="-5%" y="-5%" width="110%" height="110%"><feFlood flood-color="#c9a98a" flood-opacity=".16"/><feComposite in2="SourceAlpha" operator="in"/></filter>' +
    '<filter id="sil_' + id + '" x="-30%" y="-30%" width="160%" height="160%"><feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 .08  0 0 0 0 .05  0 0 0 0 .03  0 0 0 1 0"/><feGaussianBlur stdDeviation="7"/></filter>';
  svg.prepend(defs);
  const shadow = document.createElementNS(NS, 'g'); shadow.innerHTML = '<g class="cast" opacity=".30"><use href="#c_' + id + '" filter="url(#sil_' + id + ')"/></g>' +
    '<ellipse cx="' + foot[0] + '" cy="' + (foot[1] - 6) + '" rx="' + bb.width * .40 + '" ry="' + bb.width * .075 + '" fill="#120a05" opacity=".5" filter="url(#sil_' + id + ')"/>';
  root.parentNode.insertBefore(shadow, root);
  const over = document.createElementNS(NS, 'g'); over.style.pointerEvents = 'none';
  over.innerHTML = '<use href="#c_' + id + '" filter="url(#amb_' + id + ')" style="mix-blend-mode:multiply"/><use href="#c_' + id + '" filter="url(#fs_' + id + ')" style="mix-blend-mode:multiply"/>' +
    '<use href="#c_' + id + '" filter="url(#rl_' + id + ')" style="mix-blend-mode:screen"/>';
  root.parentNode.appendChild(over);
  C[id] = { host, c, w, svg, vb, root, body, head, foot, neck, faces, arm, bh: bb.height, cast: shadow.querySelector('.cast'), blur: (SHOT.focus_blur || {})[id] || 0, phase: id.length * 1.7 };
}
const plate = document.getElementById('plate'), dimg = new Image(), dcv = document.createElement('canvas'), mcv = document.createElement('canvas');
dcv.width = mcv.width = 1920; dcv.height = mcv.height = 1080; const dg = dcv.getContext('2d', { willReadFrequently: true }), mg = mcv.getContext('2d');
function occlude(X, depthM, D) {      // hide the character where the set is nearer the camera than the character (0.3 m tolerance: floor at the feet)
  const r = X.w.getBoundingClientRect(); const x0 = Math.max(0, Math.floor(r.left) - 4), y0 = Math.max(0, Math.floor(r.top) - 4), x1 = Math.min(1920, Math.ceil(r.right) + 4), y1 = Math.min(1080, Math.ceil(r.bottom) + 4);
  mg.globalCompositeOperation = 'copy'; mg.fillStyle = '#fff'; mg.fillRect(0, 0, 1920, 1080);
  if (x1 > x0 && y1 > y0) { const im = mg.getImageData(x0, y0, x1 - x0, y1 - y0), lim = (depthM - 0.3) * 1000; let hidden = 0;
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const i = (y * 1920 + x) * 4, mm = D[i] * 65536 + D[i + 1] * 256 + D[i + 2];
      if (mm < lim) { im.data[((y - y0) * (x1 - x0) + (x - x0)) * 4 + 3] = 0; hidden++; } }
    mg.putImageData(im, x0, y0); X.hidden = hidden; }
  const u = 'url(' + mcv.toDataURL('image/png') + ')'; X.host.style.webkitMaskImage = u; X.host.style.maskImage = u;
}
function faceAt(c, t) {           // expression schedule + blinks; returns [name, alpha of previous during a 3-frame dissolve]
  for (const [a, b] of c.blinks) if (t >= a && t < b) return ['Eyes Closed', null];
  let cur = c.faces[0][1], prev = null, since = 99;
  for (const [ts, f] of c.faces) if (t >= ts) { prev = cur; cur = f; since = t - ts; }
  return [cur, since < 0.1 ? [prev, 1 - since / 0.1] : null];
}
function headAngle(c, t) {
  let a = 0;
  for (const [t0, t1, deg] of c.tilts) a += deg * ss((t - t0) / 0.6) * (1 - ss((t - (t1 - 0.6)) / 0.6));
  for (const [tn, d] of c.nods) { const u = (t - tn) / d; if (u > 0 && u < 1) a += 6.5 * Math.sin(Math.PI * u) * (1 - 0.35 * u); }
  return a;
}
function sway(c, t, ph) {
  let a = 0.35 * Math.sin(2 * Math.PI * t / 5.3 + ph);
  for (const [ts, d, deg] of c.shifts) a += deg * ss((t - ts) / d);
  return a;
}
function armAngle(beats, t) {
  if (!beats.length || t < beats[0][0] - 0.45) return 0;
  let prev = [beats[0][0] - 0.45, 0];
  for (const b of beats) { if (t < b[0]) { const u = (t - prev[0]) / (b[0] - prev[0]); return prev[1] + (b[1] - prev[1]) * (0.5 - 0.5 * Math.cos(Math.PI * clamp(u, 0, 1))); } prev = b; }
  return prev[1];
}
window.frame = async f => {
  const t = f / 30, T = TRACK[f].pts, n = String(f).padStart(5, '0');
  plate.src = 'file://' + PLATE + '/' + n + '.jpg'; dimg.src = 'file://' + TD + '/depth_' + n + '.png';
  const win = TRACK[f].pts.window || null;
  for (const [id, X] of Object.entries(C)) {
    const feet = T[id + '_feet'], top = T[id + '_head']; X.depth = feet[2]; const _ = 0, s = (feet[1] - top[1]) / X.bh, flip = X.c.facing === 'left' ? -1 : 1;
    const br = Math.sin(2 * Math.PI * t / 3.7 + X.phase), sw = sway(X.c, t, X.phase);
    X.w.style.transform = 'translate(' + feet[0] + 'px,' + feet[1] + 'px) rotate(' + sw * flip + 'deg) scale(' + flip * s + ',' + s + ') translate(' + (-(X.foot[0] - X.vb.x)) + 'px,' + (-(X.foot[1] - X.vb.y)) + 'px)';
    X.w.style.filter = X.blur ? 'blur(' + X.blur + 'px)' : '';
    X.body.setAttribute('transform', 'translate(' + X.foot[0] + ' ' + X.foot[1] + ') scale(1 ' + (1 + 0.006 * br) + ') translate(' + (-X.foot[0]) + ' ' + (-X.foot[1]) + ')');
    const lift = -(X.foot[1] - X.neck[1]) * 0.006 * br;
    X.head.setAttribute('transform', 'translate(0 ' + lift + ') rotate(' + headAngle(X.c, t) + ' ' + X.neck[0] + ' ' + X.neck[1] + ')');
    const [fc, dis] = faceAt(X.c, t);
    for (const g of X.faces) { const nm = g.getAttribute('data-face'); const on = nm === fc || (dis && nm === dis[0]);
      g.style.display = on ? 'inline' : 'none'; g.style.opacity = dis && nm === dis[0] ? dis[1] : 1; }
    if (X.arm) X.arm.g.setAttribute('transform', 'rotate(' + armAngle(X.arm.beats, t) + ' ' + X.arm.P[0] + ' ' + X.arm.P[1] + ')');
    // light from the window: shadow on the far side, rim on the near side (screen space, flipped into the artwork)
    const lx = win ? Math.sign(win[0] - feet[0]) * flip : 1;
    document.getElementById('fso_' + id).setAttribute('dx', -14 * lx); document.getElementById('rlo_' + id).setAttribute('dx', 5 * lx);
    // cast shadow: the silhouette laid on the floor toward the camera (window behind), anchored at the feet
    X.cast.setAttribute('transform', 'translate(' + X.foot[0] + ' ' + X.foot[1] + ') matrix(1 0 ' + (-0.35 * lx) + ' -0.16 0 0) translate(' + (-X.foot[0]) + ' ' + (-X.foot[1]) + ')');
  }
  const gb = T.fg_base, gt = T.fg_top, plant = document.getElementById('plant'), ps = (gb[1] - gt[1]) / 420;
  plant.setAttribute('transform', 'translate(' + gb[0] + ' ' + gb[1] + ') scale(' + ps + ')');
  document.getElementById('fgbs').setAttribute('stdDeviation', clamp(10 * ps, 6, 26));
  document.getElementById('grt').setAttribute('seed', 1 + f % 97);
  await Promise.all([plate.decode(), dimg.decode()]);
  dg.drawImage(dimg, 0, 0); const D = dg.getImageData(0, 0, 1920, 1080).data;
  const order = Object.entries(C).sort((a, b) => b[1].depth - a[1].depth);              // far to near
  order.forEach(([id, X], k) => { X.host.style.zIndex = k; occlude(X, X.depth, D); });
  return true;
};
window.ready = true;
</script></body></html>`);
const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });   // read local depth images into a canvas
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; pg.on('pageerror', e => errs.push(String(e)));
await pg.goto('file://' + html); await pg.waitForFunction(() => window.ready);
if (errs.length) { console.error(errs); process.exit(1); }
const ENC = ['-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p'];
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', ...ENC, out], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise(r => ff.on('close', r)); const t0 = Date.now(); let fr = 0;
for (let f = f0; f <= f1; f++) {
  await pg.evaluate(f => window.frame(f), f); await pg.waitForTimeout(5);
  const png = await pg.screenshot({ type: 'png' });
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r)); fr++;
}
ff.stdin.end(); await done; await b.close();
if (errs.length) { console.error(errs); process.exit(1); }
console.log(JSON.stringify({ out, frames: fr, s_per_frame: +((Date.now() - t0) / 1000 / fr).toFixed(3) }));
