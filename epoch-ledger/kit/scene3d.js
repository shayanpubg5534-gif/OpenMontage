// Epoch Ledger scene3d (kit/scene3d.js) — illustrated vector 3D.
// Builds real-perspective sets (streets, rooms, furniture, architecture) and renders them as *lit SVG* so they
// share one illustrated language with the 2D characters: inked outlines that thin with distance, sun + sky +
// lamp lighting, atmospheric fog, soft cast shadows, CC0 textures mapped onto faces (subdivided affine), 2D art
// mapped onto surfaces (billboards, whiteboards, screens) and depth-sorted sprites (characters) for occlusion.
// Units: metres. Deterministic. Original implementation.
(function (g) {
  const NS = 'http://www.w3.org/2000/svg';
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const len = (a) => Math.hypot(a[0], a[1], a[2]), norm = (a) => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, t) => a + (b - a) * t;
  const hex = (h) => { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255); };
  const css = (c) => '#' + c.map(v => Math.round(clamp(v) * 255).toString(16).padStart(2, '0')).join('');
  const mixc = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
  const seed = (a) => () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

  // ── camera ────────────────────────────────────────────────────────────────────────────────
  function camera(o) {
    const w = o.w || 1920, h = o.h || 1080, pos = o.pos, f = norm(sub(o.look, pos)), up = o.up || [0, 1, 0];
    const r = norm(cross(f, up)), u = cross(r, f), focal = (h / 2) / Math.tan((o.fov || 40) * Math.PI / 360);
    const shift = o.shift || [0, 0];                       // lens shift (keeps verticals vertical for architecture)
    const toCam = (p) => { const d = sub(p, pos); return [dot(d, r), dot(d, u), dot(d, f)]; };
    const proj = (c) => [w / 2 + shift[0] + c[0] * focal / c[2], h / 2 + shift[1] - c[1] * focal / c[2], c[2]];
    return { pos, f, r, u, focal, w, h, near: o.near || .15, toCam, proj, project: (p) => { const c = toCam(p); return c[2] > .15 ? proj(c) : null; } };
  }
  // clip a camera-space polygon against the near plane (Sutherland–Hodgman)
  function clipNear(poly, near) {
    const out = [];
    for (let i = 0; i < poly.length; i++) {
      const a = poly[i], b = poly[(i + 1) % poly.length], ai = a[2] >= near, bi = b[2] >= near;
      if (ai) out.push(a);
      if (ai !== bi) { const t = (near - a[2]) / (b[2] - a[2]); out.push([lerp(a[0], b[0], t), lerp(a[1], b[1], t), near]); }
    }
    return out;
  }

  // ── scene construction ────────────────────────────────────────────────────────────────────
  function scene() {
    const items = [];
    const S = {
      items,
      // planar polygon (3D points, counter-clockwise seen from the front); uv = texture coordinates per vertex (in repeats)
      poly(pts, mat, o) { const n = norm(cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))); items.push(Object.assign({ kind: 'face', pts, n, mat }, o || {})); return S; },
      quad(p0, p1, p2, p3, mat, o) { return S.poly([p0, p1, p2, p3], mat, o); },
      // axis-aligned box; faces: subset of 'top','bottom','left','right','front','back'; texture world-scale via mat.texScale (m per repeat)
      box(min, max, mat, o) {
        o = o || {}; const [x0, y0, z0] = min, [x1, y1, z1] = max, ts = (mat && mat.texScale) || 1;
        const F = {
          top: [[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]], bottom: [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]],
          front: [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], back: [[x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0]],
          left: [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], right: [[x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1]] };
        const uvs = { top: [x1 - x0, z1 - z0], bottom: [x1 - x0, z1 - z0], front: [x1 - x0, y1 - y0], back: [x1 - x0, y1 - y0], left: [z1 - z0, y1 - y0], right: [z1 - z0, y1 - y0] };
        (o.faces || Object.keys(F)).forEach(k => { const [du, dv] = uvs[k]; const m = (o.mats && o.mats[k]) || mat;
          S.poly(F[k], m, { uv: [[0, dv / ts], [du / ts, dv / ts], [du / ts, 0], [0, 0]], name: o.name, bias: o.bias || 0, group: o.group }); });
        if (o.shadow !== false) items.push({ kind: 'caster', pts: [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], base: y0, soft: o.soft });
        return S;
      },
      // vertical cylinder approximated by facets (columns, tanks, lamp posts, pipes)
      cyl(c, r, y0, y1, mat, o) {
        o = o || {}; const n = o.seg || 16;
        for (let i = 0; i < n; i++) { const a0 = i / n * Math.PI * 2, a1 = (i + 1) / n * Math.PI * 2;
          const p = (a, y) => [c[0] + Math.cos(a) * r, y, c[2] + Math.sin(a) * r];
          S.poly([p(a0, y0), p(a0, y1), p(a1, y1), p(a1, y0)].reverse(), mat, { name: o.name, bias: o.bias || 0 }); }
        if (o.cap !== false) S.poly(Array.from({ length: n }, (_, i) => [c[0] + Math.cos(-i / n * Math.PI * 2) * r, y1, c[2] + Math.sin(-i / n * Math.PI * 2) * r]), o.capMat || mat, { bias: o.bias || 0 });
        if (o.shadow !== false) items.push({ kind: 'caster', pts: Array.from({ length: 16 }, (_, i) => [c[0] + Math.cos(i / 8 * Math.PI) * r, i < 8 ? y0 : y1, c[2] + Math.sin(i / 8 * Math.PI) * r]), base: y0, soft: o.soft });
        return S;
      },
      // horizontal pipe/tube along x or z: axis 'x'|'z', from a to b at height y, centre offset c
      tube(axis, a, b, y, c, r, mat, o) {
        o = o || {}; const n = o.seg || 10;
        for (let i = 0; i < n; i++) { const a0 = i / n * Math.PI * 2, a1 = (i + 1) / n * Math.PI * 2;
          const P = (s, ang) => axis === 'x' ? [s, y + Math.sin(ang) * r, c + Math.cos(ang) * r] : [c + Math.cos(ang) * r, y + Math.sin(ang) * r, s];
          S.poly([P(a, a0), P(b, a0), P(b, a1), P(a, a1)], mat, { bias: o.bias || 0, name: o.name }); }
        return S;
      },
      // prism from a 2D profile [[a, y], …] (counter-clockwise) swept along x (axis 'x') or z (axis 'z') — vehicles, awnings, cornices, rails
      extrude(profile, axis, s0, s1, mat, o) {
        o = o || {}; const P = (q, s) => axis === 'x' ? [s, q[1], q[0]] : [q[0], q[1], s];
        for (let i = 0; i < profile.length; i++) { const a = profile[i], b = profile[(i + 1) % profile.length];
          S.poly(axis === 'x' ? [P(a, s0), P(b, s0), P(b, s1), P(a, s1)] : [P(a, s1), P(b, s1), P(b, s0), P(a, s0)], (o.sideMats && o.sideMats[i]) || mat, { bias: o.bias || 0, name: o.name, allowBack: true }); }
        const cap0 = profile.map(q => P(q, s0)), cap1 = profile.map(q => P(q, s1)).reverse();
        S.poly(axis === 'x' ? cap0.slice().reverse() : cap0, o.capMat || mat, { bias: o.bias || 0, allowBack: true }); S.poly(axis === 'x' ? cap1.slice().reverse() : cap1, o.capMat || mat, { bias: o.bias || 0, allowBack: true });
        if (o.shadow !== false) { const ys = profile.map(q => q[1]), as = profile.map(q => q[0]); const y0 = Math.min(...ys), y1 = Math.max(...ys), a0 = Math.min(...as), a1 = Math.max(...as);
          items.push({ kind: 'caster', pts: [[a0, y0], [a1, y0], [a0, y1], [a1, y1]].flatMap(q => [P(q, s0), P(q, s1)]), base: o.base === undefined ? y0 : o.base, soft: o.soft }); }
        return S;
      },
      // wheel / disc facing along an axis ('x' or 'z'): centre c, radius r, thickness t
      wheel(c, r, t, axis, mat, o) {
        const n = (o && o.seg) || 14, prof = Array.from({ length: n }, (_, i) => [Math.cos(i / n * Math.PI * 2) * r, Math.sin(i / n * Math.PI * 2) * r]);
        const pr = prof.map(q => axis === 'x' ? [c[2] + q[0], c[1] + q[1]] : [c[0] + q[0], c[1] + q[1]]);
        return S.extrude(pr, axis, (axis === 'x' ? c[0] : c[2]) - t / 2, (axis === 'x' ? c[0] : c[2]) + t / 2, mat, { shadow: false, capMat: (o && o.capMat) || mat });
      },
      // 2D art (SVG markup in an aw×ah box) mapped onto a planar quad p0 (bottom-left), p1 (bottom-right), p3 (top-left)
      art(p0, p1, p3, aw, ah, markup, o) { items.push(Object.assign({ kind: 'art', p0, p1, p3, aw, ah, markup }, o || {})); return S; },
      // depth-sorted sprite (e.g. a character): foot position, height in metres, markup with aspect w/h
      sprite(foot, height, markup, aspect, o) { items.push(Object.assign({ kind: 'sprite', foot, height, markup, aspect }, o || {})); return S; },
      // tiled ground/floor plane (receiver) from (x0,z0) to (x1,z1) at height y; tile size in metres
      ground(x0, z0, x1, z1, y, tile, mat) {
        const ts = mat.texScale || tile;
        for (let x = x0; x < x1 - 1e-6; x += tile) for (let z = z0; z < z1 - 1e-6; z += tile) {
          const xa = Math.min(x + tile, x1), za = Math.min(z + tile, z1);
          S.poly([[x, y, za], [xa, y, za], [xa, y, z], [x, y, z]], Object.assign({ receiver: true }, mat), { uv: [[x / ts, za / ts], [xa / ts, za / ts], [xa / ts, z / ts], [x / ts, z / ts]].map(q => [q[0], -q[1]]) });
        }
        return S;
      },
      // building facade: wall quad with recessed windows (lit / dark / blinds), sills and lintels, varied by seed
      facade(o) {
        const r = seed(o.seed || 1), U = norm(o.u), Vv = [0, 1, 0], N = norm(cross(U, Vv)), O0 = o.origin;
        const P = (u, v, d) => add(add(add(O0, mul(U, u)), mul(Vv, v)), mul(N, d || 0));
        S.quad(P(0, 0), P(o.width, 0), P(o.width, o.height), P(0, o.height), o.wall, { uv: [[0, o.height / (o.wall.texScale || 1)], [o.width / (o.wall.texScale || 1), o.height / (o.wall.texScale || 1)], [o.width / (o.wall.texScale || 1), 0], [0, 0]], bias: -.05 });
        const cw = (o.width - 2 * (o.margin || .8)) / o.cols, rh = (o.height - (o.base || 1) - (o.top || 1)) / o.rows, ww = o.winW || cw * .55, wh = o.winH || rh * .62;
        for (let i = 0; i < o.cols; i++) for (let j = 0; j < o.rows; j++) {
          if (o.skip && o.skip(i, j)) continue;
          const u0 = (o.margin || .8) + i * cw + (cw - ww) / 2, v0 = (o.base || 1) + j * rh + (rh - wh) / 2, d = -(o.inset || .18);
          const lit = r() < (o.lit === undefined ? .45 : o.lit), glass = lit ? (o.litColors || ['#ffd892', '#ffe4b0', '#f9c77a'])[Math.floor(r() * 3)] : (o.dark || '#2a3448');
          const em = lit ? .45 + r() * .25 : 0;
          // reveal (inset sides) then glass
          S.quad(P(u0, v0, 0), P(u0 + ww, v0, 0), P(u0 + ww, v0, d), P(u0, v0, d), o.frame || { color: '#5a4a3a' }, { bias: .01 });
          S.quad(P(u0, v0, d), P(u0 + ww, v0, d), P(u0 + ww, v0 + wh, d), P(u0, v0 + wh, d), { color: glass, emissive: em, outline: '#1b1410', ow: .6 }, { bias: .02 });
          if (lit && r() < .4) S.quad(P(u0, v0 + wh * .55, d + .01), P(u0 + ww, v0 + wh * .55, d + .01), P(u0 + ww, v0 + wh, d + .01), P(u0, v0 + wh, d + .01), { color: '#e8d8b8', emissive: .5 }, { bias: .03 });
          { const a = P(u0 - .06, v0 - .12, 0), b = P(u0 + ww + .06, v0, .12);
            S.box(a.map((x, k) => Math.min(x, b[k])), a.map((x, k) => Math.max(x, b[k])), o.sill || { color: '#cfc6b4' }, { shadow: false, bias: .03 }); }
          if (o.lintel !== false) { const a = P(u0 - .1, v0 + wh, 0), b = P(u0 + ww + .1, v0 + wh + .16, .06);
            S.box(a.map((x, k) => Math.min(x, b[k])), a.map((x, k) => Math.max(x, b[k])), o.lintelMat || o.sill || { color: '#cfc6b4' }, { shadow: false, bias: .03 }); }
        }
        return S;
      },
    };
    return S;
  }

  // ── lighting ──────────────────────────────────────────────────────────────────────────────
  function shadeColor(face, n, cen, L) {
    const m = face.mat || {}, base = hex(m.color || '#888888');
    const sky = hex(L.sky || '#9fb6d8'), gnd = hex(L.ground || '#4a3a30'), hemi = mixc(gnd, sky, n[1] * .5 + .5);
    let c = mul(base, 0).slice(); const amb = L.ambient === undefined ? .45 : L.ambient;
    let lit = [hemi[0] * amb, hemi[1] * amb, hemi[2] * amb];
    if (L.sun) { const sd = norm(L.sun.dir), k = Math.max(0, dot(n, sd)) * (L.sun.intensity || 1), sc = hex(L.sun.color || '#fff4e0'); lit = add(lit, mul(sc, k)); }
    (L.points || []).forEach(p => { const d = sub(p.pos, cen), dist = len(d), k = Math.max(0, dot(n, norm(d))) * (p.intensity || 1) * Math.pow(clamp(1 - dist / (p.range || 6)), 2);
      lit = add(lit, mul(hex(p.color || '#ffe0a8'), k)); });
    c = [base[0] * lit[0], base[1] * lit[1], base[2] * lit[2]];
    if (m.emissive) c = add(c, mul(base, m.emissive));
    return c;
  }

  // ── render ────────────────────────────────────────────────────────────────────────────────
  // Returns SVG markup (fills a 0 0 w h viewBox). opts: {defs, outline:'#1b1410', ow: base outline px at 10 m, fog:{color,near,far,max}}
  function render(sc, cam, L, opts) {
    opts = opts || {}; const out = [], defs = [], patterns = {}; let uid = opts.uid || 's3';
    const fog = L.fog || null, fogC = fog ? hex(fog.color) : null;
    const fogAt = (z) => fog ? clamp((z - fog.near) / (fog.far - fog.near)) * (fog.max === undefined ? 1 : fog.max) : 0;
    const pattern = (url, size) => { if (!patterns[url]) { const id = uid + 'p' + Object.keys(patterns).length; patterns[url] = id;
      defs.push(`<pattern id="${id}" patternUnits="userSpaceOnUse" width="${size}" height="${size}"><image href="${url}" width="${size}" height="${size}" preserveAspectRatio="none"/></pattern>`); } return patterns[url]; };
    const items = [];
    // faces
    sc.items.forEach((it, idx) => {
      if (it.kind === 'face') {
        const camPts = it.pts.map(cam.toCam), clipped = clipNear(camPts, cam.near); if (clipped.length < 3) return;
        const cen = it.pts.reduce((a, p) => add(a, mul(p, 1 / it.pts.length)), [0, 0, 0]);
        let n = it.n; const toC = sub(cam.pos, cen); if (dot(n, toC) < 0) { if (!(it.mat && it.mat.doubleSided) && !it.allowBack) return; n = mul(n, -1); }
        const z = clipped.reduce((a, p) => a + p[2], 0) / clipped.length;
        items.push({ type: 'face', it, n, cen, z: z - (it.bias || 0), scr: clipped.map(cam.proj), camPts: clipped, recv: it.mat && it.mat.receiver, idx });
      } else if (it.kind === 'art') {
        const a = cam.project(it.p0), b = cam.project(it.p1), c = cam.project(it.p3); if (!a || !b || !c) return;
        items.push({ type: 'art', it, z: (a[2] + b[2] + c[2]) / 3 - (it.bias || .05), a, b, c, idx });
      } else if (it.kind === 'sprite') {
        const f = cam.project(it.foot), hd = cam.project(add(it.foot, [0, it.height, 0])); if (!f || !hd) return;
        items.push({ type: 'sprite', it, z: f[2] - (it.bias || 0), f, hd, idx });
      }
    });
    // shadows (projected onto the receiver plane along the sun direction)
    const shadows = [];
    if (L.sun && L.shadows !== false) {
      const d = mul(norm(L.sun.dir), -1);                         // direction light travels
      sc.items.filter(i => i.kind === 'caster').forEach(c => {
        const planeY = c.base, pts2 = c.pts.map(p => { const t = (p[1] - planeY) / -d[1]; return [p[0] + d[0] * t, p[2] + d[2] * t]; });
        const hull = convexHull(pts2); const s3 = hull.map(q => [q[0], planeY + .003, q[1]]);
        const cs = clipNear(s3.map(cam.toCam), cam.near); if (cs.length >= 3) shadows.push({ scr: cs.map(cam.proj), z: cs.reduce((a, p) => a + p[2], 0) / cs.length, soft: c.soft });
      });
    }
    const ink = opts.outline || '#1b1410', ow = opts.ow || 2.2;
    const path = (scr) => 'M' + scr.map(p => p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' L') + 'Z';
    const drawFace = (o) => {
      const it = o.it, m = it.mat || {}, c = shadeColor(it, o.n, o.cen, L), fa = fogAt(o.z), col = fogC ? mixc(c, fogC, fa) : c;
      const sw = (m.ow === undefined ? ow : m.ow) * clamp(12 / o.z, .25, 2.2), stroke = m.outline === false ? 'none' : (m.outline || ink);
      const op = m.alpha === undefined ? 1 : m.alpha;
      if (m.tex && it.uv) {
        // texture: subdivided affine tiles, then light (multiply) and fog (normal) overlays
        const pid = pattern(m.tex, m.texPx || 512), sub_ = m.sub || 4, P = it.pts, UV = it.uv;
        const bil = (arr, s, t) => { const a = arr[0], b = arr[1], c2 = arr[2], d2 = arr[3]; const ab = a.map((v, k) => lerp(v, b[k], s)), dc = d2.map((v, k) => lerp(v, c2[k], s)); return ab.map((v, k) => lerp(v, dc[k], t)); };
        let tiles = '';
        for (let i = 0; i < sub_; i++) for (let j = 0; j < sub_; j++) {
          const s0 = i / sub_, s1 = (i + 1) / sub_, t0 = j / sub_, t1 = (j + 1) / sub_;
          const w3 = [bil(P, s0, t0), bil(P, s1, t0), bil(P, s1, t1), bil(P, s0, t1)], uv = [bil(UV, s0, t0), bil(UV, s1, t0), bil(UV, s1, t1), bil(UV, s0, t1)];
          const cp = w3.map(cam.toCam); if (cp.some(q => q[2] < cam.near)) continue; const sp = cp.map(cam.proj);
          const px = m.texPx || 512, T = uv.map(q => [q[0] * px, q[1] * px]);
          const A = affine(T[0], T[1], T[3], sp[0], sp[1], sp[3]); if (!A) continue;
          // inflate the tile by ~1px in screen space to hide seams
          tiles += `<g transform="matrix(${A.map(v => v.toFixed(5)).join(' ')})"><path d="M${T[0]} L${T[1]} L${T[2]} L${T[3]}Z" fill="url(#${pid})" stroke="url(#${pid})" stroke-width="${(2 / Math.max(.0001, Math.hypot(A[0], A[1]))).toFixed(2)}"/></g>`;
        }
        const cid = uid + 'c' + o.idx + '_' + out.length; defs.push(`<clipPath id="${cid}"><path d="${path(o.scr)}"/></clipPath>`);
        const tint = m.tint ? hex(m.tint) : [1, 1, 1], lightOnly = shadeColor({ mat: Object.assign({}, m, { color: '#ffffff', emissive: m.emissive }) }, o.n, o.cen, L);
        const mulc = [lightOnly[0] * tint[0], lightOnly[1] * tint[1], lightOnly[2] * tint[2]];
        out.push(`<g clip-path="url(#${cid})" opacity="${op}">${tiles}${m.texMix !== undefined && m.texMix < 1 ? `<path d="${path(o.scr)}" fill="${m.color || '#ffffff'}" opacity="${(1 - m.texMix).toFixed(3)}"/>` : ''}<path d="${path(o.scr)}" fill="${css(mulc)}" style="mix-blend-mode:multiply"/>` +
          (Math.max(...mulc) > 1 ? `<path d="${path(o.scr)}" fill="${css(mulc.map(v => Math.max(0, v - 1)))}" style="mix-blend-mode:screen"/>` : '') +
          (fa > .01 ? `<path d="${path(o.scr)}" fill="${css(fogC)}" opacity="${fa.toFixed(3)}"/>` : '') + `</g>` +
          (stroke !== 'none' ? `<path d="${path(o.scr)}" fill="none" stroke="${stroke}" stroke-width="${sw.toFixed(2)}" stroke-linejoin="round" opacity="${(1 - fa * .8).toFixed(2)}"/>` : ''));
      } else {
        out.push(`<path d="${path(o.scr)}" fill="${css(col)}" ${op < 1 ? `fill-opacity="${op}"` : ''} stroke="${stroke}" stroke-width="${sw.toFixed(2)}" stroke-linejoin="round" stroke-opacity="${(1 - fa * .8).toFixed(2)}"/>`);
      }
      if (m.gloss) out.push(`<path d="${path(o.scr)}" fill="url(#${uid}gloss)" opacity="${m.gloss}" style="mix-blend-mode:screen"/>`);
    };
    defs.push(`<linearGradient id="${uid}gloss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".0"/><stop offset=".45" stop-color="#fff" stop-opacity=".55"/><stop offset=".55" stop-color="#fff" stop-opacity=".0"/></linearGradient>`);
    defs.push(`<filter id="${uid}soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="${opts.shadowBlur || 6}"/></filter>`);
    // 1. receivers (ground / floors) far→near, 2. shadows, 3. everything else far→near
    const recv = items.filter(o => o.type === 'face' && o.recv).sort((a, b) => b.z - a.z), rest = items.filter(o => !(o.type === 'face' && o.recv)).sort((a, b) => b.z - a.z);
    recv.forEach(drawFace);
    if (shadows.length) out.push(`<g filter="url(#${uid}soft)" opacity="${L.shadowOpacity || .42}">` + shadows.map(s => `<path d="${path(s.scr)}" fill="${L.shadowColor || '#1a1020'}"/>`).join('') + '</g>');
    rest.forEach(o => {
      if (o.type === 'face') drawFace(o);
      else if (o.type === 'art') { const it = o.it, A = affine([0, it.ah], [it.aw, it.ah], [0, 0], o.a, o.b, o.c); if (!A) return;
        out.push(`<g transform="matrix(${A.map(v => v.toFixed(5)).join(' ')})" ${it.id ? `id="${it.id}"` : ''}>${it.markup}</g>`); }
      else if (o.type === 'sprite') { const it = o.it, hpx = o.f[1] - o.hd[1], wpx = hpx * it.aspect; const fa = fogAt(o.z);
        out.push(`<svg x="${(o.f[0] - wpx * (it.anchor === undefined ? .5 : it.anchor)).toFixed(1)}" y="${o.hd[1].toFixed(1)}" width="${wpx.toFixed(1)}" height="${hpx.toFixed(1)}" viewBox="${it.viewBox || '0 0 100 100'}" overflow="visible" ${it.id ? `id="${it.id}"` : ''} style="${fa > .02 ? `filter:saturate(${1 - fa * .5}) brightness(${1 - fa * .2})` : ''}">${it.markup}</svg>`); }
    });
    return `<defs>${defs.join('')}${opts.defs || ''}</defs>${out.join('')}`;
  }
  function affine(s0, s1, s2, d0, d1, d2) {   // map source triangle → destination triangle; returns [a b c d e f]
    const den = (s1[0] - s0[0]) * (s2[1] - s0[1]) - (s2[0] - s0[0]) * (s1[1] - s0[1]); if (Math.abs(den) < 1e-9) return null;
    const a = ((d1[0] - d0[0]) * (s2[1] - s0[1]) - (d2[0] - d0[0]) * (s1[1] - s0[1])) / den, c = ((d2[0] - d0[0]) * (s1[0] - s0[0]) - (d1[0] - d0[0]) * (s2[0] - s0[0])) / den;
    const b = ((d1[1] - d0[1]) * (s2[1] - s0[1]) - (d2[1] - d0[1]) * (s1[1] - s0[1])) / den, d = ((d2[1] - d0[1]) * (s1[0] - s0[0]) - (d1[1] - d0[1]) * (s2[0] - s0[0])) / den;
    return [a, b, c, d, d0[0] - a * s0[0] - c * s0[1], d0[1] - b * s0[0] - d * s0[1]];
  }
  function convexHull(p) { p = p.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]); const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = []; p.forEach(q => { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); });
    p.slice().reverse().forEach(q => { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); });
    return lo.slice(0, -1).concat(up.slice(0, -1)); }

  g.S3 = { camera, scene, render, affine, hex, css, seed, v: { add, sub, mul, dot, cross, norm, len } };
})(typeof window !== 'undefined' ? window : globalThis);
