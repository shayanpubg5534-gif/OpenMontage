// Character lab (M4.1): reusable illustrated 3D environments.
//
// A set is a JSON spec (motion/sets/*.json): a room shell, a palette, a light rig and a list of furniture and dressing
// items, each built by a component from the library below in the same flat editorial look as the characters
// (flat colour, two-band shading, ink outlines, real shadows). Characters and sets share one scene, so perspective,
// occlusion (a desk in front of legs, a chair back behind a sitter) and shadows are correct by construction.
//
// Every item can expose anchors (a chair's seat, a desk's top surface, a standing mark); shot scripts refer to them
// (e.g. "place": {"anchor": "client_chair.seat"}) instead of hard-coded coordinates, so a set can be rearranged
// without rewriting the performance. Chairs can fit their seat height to the actor who sits on them.
import * as THREE from 'three';

const deg = d => d * Math.PI / 180;

export function buildEnvironment(stage, spec) {
  const root = new THREE.Group(); root.name = 'env:' + spec.id;
  const anchors = {}, items = {};
  const P = spec.palette || {};
  const col = c => (typeof c === 'string' && P[c]) ? P[c] : c;
  const M = c => stage.propMaterial(col(c));
  const box = (w, h, d, c, x = 0, y = 0, z = 0, parent = null) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), M(c)); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; (parent || root).add(m); return m; };
  const cyl = (rt, rb, h, c, seg = 20) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), M(c)); m.castShadow = m.receiveShadow = true; return m; };

  // ── room shell ──────────────────────────────────────────────────────────────────────────────────────────────────
  const R = spec.room, hw = R.w / 2, back = R.back, front = R.front ?? 3;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(R.w + 4, front - back + 4), M(R.floor)); floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, 0, (back + front) / 2); floor.receiveShadow = true; floor.userData.noOutline = true; root.add(floor);
  // back wall with an optional window opening
  const W = spec.window;
  const wallT = .12;
  if (W) {
    const x0 = W.x - W.w / 2, x1 = W.x + W.w / 2, y0 = W.sill, y1 = W.sill + W.h;
    box(x0 + hw + .4, R.h, wallT, R.wall, (-hw - .4 + x0) / 2, R.h / 2, back);
    box(hw + .4 - x1, R.h, wallT, R.wall, (x1 + hw + .4) / 2, R.h / 2, back);
    box(W.w, y0, wallT, R.wall, W.x, y0 / 2, back);
    box(W.w, R.h - y1, wallT, R.wall, W.x, (y1 + R.h) / 2, back);
    // frame and mullions
    const fc = W.frame || '#2d3340';
    box(W.w + .08, .06, .16, fc, W.x, y0, back + .02); box(W.w + .08, .06, .16, fc, W.x, y1, back + .02);
    box(.06, W.h, .16, fc, x0, (y0 + y1) / 2, back + .02); box(.06, W.h, .16, fc, x1, (y0 + y1) / 2, back + .02);
    for (let i = 1; i < (W.panes || 3); i++) box(.035, W.h, .08, fc, x0 + W.w * i / (W.panes || 3), (y0 + y1) / 2, back);
    box(.035 + W.w, .035, .08, fc, W.x, y0 + W.h * .62, back);
    box(W.w + .2, .05, .26, R.trim || fc, W.x, y0 - .02, back + .1);                          // sill
    // the view: a painted backdrop far behind the window (parallax), unlit, slightly hazed
    if (W.backdrop) {
      const tex = new THREE.TextureLoader().load(W.backdrop.image); tex.colorSpace = THREE.SRGBColorSpace;
      if (W.backdrop.crop) { const [u0, v0, u1, v1] = W.backdrop.crop; tex.offset.set(u0, 1 - v1); tex.repeat.set(u1 - u0, v1 - v0); }
      const dist = W.backdrop.distance || 4, sc = 1 + dist / 3;
      const bd = new THREE.Mesh(new THREE.PlaneGeometry(W.w * sc * 1.25, W.h * sc * 1.25), new THREE.MeshBasicMaterial({ map: tex, color: new THREE.Color(W.backdrop.tint || '#f4f6fb') }));
      bd.position.set(W.x, (y0 + y1) / 2 + (W.backdrop.lift || 0), back - dist); bd.userData.noOutline = true; bd.userData.kind = 'backdrop'; root.add(bd);
    }
  } else box(R.w + .8, R.h, wallT, R.wall, 0, R.h / 2, back);
  if (R.wainscot) { box(R.w + .8, R.wainscot.h, .03, R.wainscot.color, 0, R.wainscot.h / 2, back + .075);
    box(R.w + .8, .04, .06, R.trim, 0, R.wainscot.h, back + .09); }
  if (R.skirting !== false) box(R.w + .8, .1, .04, R.trim, 0, .05, back + .08);
  if (R.ceiling || R.beams) {                                       // opt-in (M5): a closed room never shows the plate above the walls
    if (R.ceiling) { const ce = new THREE.Mesh(new THREE.PlaneGeometry(R.w + .8, front - back + .4), new THREE.MeshBasicMaterial({ color: new THREE.Color(col(R.ceiling)), side: THREE.DoubleSide }));
      ce.rotation.x = Math.PI / 2; ce.position.set(0, R.h, (back + front) / 2); ce.userData.noOutline = true; root.add(ce); }      // unlit: casts and receives nothing
    if (R.beams) for (let z = back + .6; z < front; z += R.beams.every || 1.2) box(R.w + .8, .14, .12, R.beams.color || R.trim, 0, R.h - .07, z).castShadow = false; }
  // side walls (optional)
  for (const [side, x] of [['left', -hw], ['right', hw]]) {
    const S = R[side]; if (!S) continue;
    const len = (S.to ?? front) - back;
    box(wallT, R.h, len, S.color || R.wall, x, R.h / 2, back + len / 2);
    const sgn = x < 0 ? 1 : -1;
    if (R.wainscot) { box(.03, R.wainscot.h, len, R.wainscot.color, x + sgn * .075, R.wainscot.h / 2, back + len / 2);
      box(.06, .04, len, R.trim, x + sgn * .09, R.wainscot.h, back + len / 2); }
    if (R.skirting !== false) box(.04, .1, len, R.trim, x + sgn * .08, .05, back + len / 2);
    if (S.door) { const d = S.door, sg = x < 0 ? 1 : -1;
      box(.05, 2.1, .95, d.color || '#5a3a2a', x + sg * .06, 1.05, d.z); box(.08, 2.2, 1.07, d.frame || R.trim, x + sg * .04, 1.1, d.z).position.x = x + sg * .03;
      const knob = cyl(.025, .025, .05, '#d9b25c'); knob.rotation.z = Math.PI / 2; knob.position.set(x + sg * .1, 1.0, d.z + .35); root.add(knob);
      anchors[`${side}_door`] = { pos: [x + sg * .6, d.z], yaw: sg > 0 ? 90 : -90 }; }
  }

  // bread shapes: boule (round, cross score), loaf (oval, diagonal scores), baguette (long, slashes), rye (dark, dusted), roll, croissant
  const BREAD = { boule: '#c98a3e', loaf: '#d49a4c', baguette: '#d8a456', rye: '#7a4a2a', roll: '#d9a050', croissant: '#d79540' };
  function addBread(g, kind, color, x, y, z, rotDeg = 0, sc = 1, tilt = 0) {
    const grp = new THREE.Group(); grp.position.set(x, y, z); grp.rotation.set(tilt, deg(rotDeg), 0); grp.scale.setScalar(sc); g.add(grp);
    const c = color || BREAD[kind] || '#c98a3e', dark = new THREE.Color(c).multiplyScalar(.62).getStyle(), light = new THREE.Color(c).lerp(new THREE.Color('#f6e2b8'), .5).getStyle();
    const blob = (sx, sy, sz, col, px = 0, py = 0, pz = 0) => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), M(col)); m.scale.set(sx, sy, sz); m.position.set(px, py, pz); m.castShadow = m.receiveShadow = true; grp.add(m); return m; };
    const score = (len, px, py, pz, ry, col = light) => { const m = new THREE.Mesh(new THREE.CapsuleGeometry(.006, len, 3, 6), M(col)); m.rotation.set(Math.PI / 2, 0, ry); m.position.set(px, py, pz); m.userData.noOutline = true; grp.add(m); };
    if (kind === 'boule') { blob(.1, .065, .1, c, 0, .045); score(.1, 0, .105, 0, 0); score(.1, 0, .105, 0, Math.PI / 2); }
    else if (kind === 'loaf') { blob(.13, .06, .075, c, 0, .045); for (let i = -1; i <= 1; i++) score(.06, i * .065, .1, 0, .9); }
    else if (kind === 'rye') { blob(.11, .06, .08, c, 0, .045); blob(.07, .02, .05, '#c9b79a', 0, .095).userData.noOutline = true; }
    else if (kind === 'baguette') { blob(.3, .032, .036, c, 0, .03); for (let i = -2; i <= 2; i++) score(.05, i * .1, .058, 0, .6); }
    else if (kind === 'roll') { blob(.045, .035, .045, c, 0, .028); score(.04, 0, .06, 0, 0); }
    else if (kind === 'croissant') { const t = new THREE.Mesh(new THREE.TorusGeometry(.055, .025, 10, 18, Math.PI * 1.15), M(c)); t.rotation.set(Math.PI / 2, 0, -Math.PI * .07); t.scale.set(1, 1, .8); t.position.y = .022; t.castShadow = true; grp.add(t);
      blob(.035, .028, .03, c, 0, .025, -.045); }
    return grp; }

  // ── component library ───────────────────────────────────────────────────────────────────────────────────────────
  const C = {
    desk(it, g) { const [d, h, w] = it.size || [.8, .76, 1.6], top = it.color || '#7a4f33', body = it.body || '#5e3b26';
      box(d + .04, .045, w + .04, top, 0, h - .022, 0, g);
      box(d, h - .045, .05, body, 0, (h - .045) / 2, -w / 2 + .03, g); box(d, h - .045, .05, body, 0, (h - .045) / 2, w / 2 - .03, g);
      const ps = it.panel === 'xn' ? -1 : 1;                                                       // modesty panel on the visitor's side
      box(.03, h * .62, w - .08, body, ps * (d / 2 - .03), h - .045 - h * .31, 0, g);
      // pedestal with drawers on the owner's side
      const px = -ps * (d / 2 - .2), pz = w / 2 - .25;
      box(.38, h - .1, .42, body, px, (h - .1) / 2 + .02, pz, g);
      for (let i = 0; i < 3; i++) { box(.012, .2, .36, it.drawer || '#6d4630', px - ps * .195, .17 + i * .23, pz, g);
        const hd = box(.02, .02, .1, '#c9a24f', px - ps * .205, .2 + i * .23, pz, g); hd.castShadow = false; }
      return { top: { y: h, size: [d, w] } }; },
    chair(it, g) { const s = it.seat || .46, c = it.color || '#2f3540', leg = it.leg || '#1d2129';
      const seat = box(.46, .06, .44, c, 0, s - .03, 0, g); seat.name = 'seat';
      box(.46, .5, .05, c, 0, s + .25, -.2, g);
      for (const [x, z] of [[-.2, -.19], [.2, -.19], [-.2, .19], [.2, .19]]) box(.035, s - .06, .035, leg, x, (s - .06) / 2, z, g);
      return { seat: { y: s, back: .07 } }; },
    office_chair(it, g) { const s = it.seat || .48, c = it.color || '#3b2a24', m = it.metal || '#30343c';
      box(.5, .09, .48, c, 0, s - .045, 0, g).name = 'seat';
      box(.48, .62, .08, c, 0, s + .36, -.23, g); box(.06, .2, .3, c, -.25, s + .12, -.02, g); box(.06, .2, .3, c, .25, s + .12, -.02, g);
      const post = cyl(.03, .03, s - .14, m); post.position.y = (s - .14) / 2 + .07; g.add(post);
      for (let i = 0; i < 5; i++) { const a = i * 2 * Math.PI / 5, l = box(.3, .03, .04, m, Math.sin(a) * .15, .05, Math.cos(a) * .15, g); l.rotation.y = a + Math.PI / 2; }
      return { seat: { y: s, back: .08 } }; },
    bookshelf(it, g) { const [w, h, d] = it.size || [1.4, 2.0, .34], c = it.color || '#6a452e';
      box(w, .04, d, c, 0, h, 0, g); box(w, .06, d, c, 0, .03, 0, g); box(.04, h, d, c, -w / 2, h / 2, 0, g); box(.04, h, d, c, w / 2, h / 2, 0, g);
      box(w, h, .02, it.back || '#4f3322', 0, h / 2, -d / 2 + .01, g);
      const rows = it.rows || 4, books = it.books || ['#8c3b32', '#2f4b6e', '#c79a4a', '#3d5a45', '#e3d8c2', '#5b3b5e', '#2a2f3a'];
      let seed = it.seed || 3; const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
      for (let r = 0; r < rows; r++) { const y0 = .06 + r * (h - .06) / rows; box(w - .04, .03, d - .02, c, 0, y0, 0, g);
        let x = -w / 2 + .05; while (x < w / 2 - .12) { const bw = .025 + rnd() * .035, bh = (h / rows) * (.55 + rnd() * .3);
          if (rnd() < .12) { x += .06; continue; }
          box(bw, bh, d * .72, books[Math.floor(rnd() * books.length)], x + bw / 2, y0 + .015 + bh / 2, .02, g); x += bw + .004; } }
      return {}; },
    cabinet(it, g) { const [w, h, d] = it.size || [.5, 1.3, .55], c = it.color || '#7d8592';
      box(w, h, d, c, 0, h / 2, 0, g); for (let i = 0; i < 4; i++) { box(w * .9, .01, .01, '#5c6370', 0, .3 + i * (h - .2) / 4, d / 2 + .002, g);
        box(.12, .02, .02, '#c8ccd3', 0, .2 + i * (h - .2) / 4, d / 2 + .01, g); } return { top: { y: h } }; },
    plant(it, g) { const pot = cyl(.17, .13, .36, it.pot || '#a9573b'); pot.position.y = .18; g.add(pot);
      const lc = it.leaves || ['#2f6b45', '#3d7f52', '#285a3b']; let seed = it.seed || 7; const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
      for (let i = 0; i < (it.count || 14) * 2; i++) { const l = new THREE.Mesh(new THREE.SphereGeometry(.11, 10, 8), M(lc[i % lc.length]));
        const a = rnd() * Math.PI * 2, r = .04 + rnd() * .16, hgt = .4 + rnd() * (it.height || .9);
        l.scale.set(.32, 1.15, .14); l.position.set(Math.cos(a) * r, hgt, Math.sin(a) * r); l.rotation.set(rnd() * .8 - .4, a, (rnd() - .5) * 1.2 + (Math.cos(a) * .6));
        l.castShadow = true; g.add(l); } return {}; },
    lamp(it, g) { const base = cyl(.07, .09, .03, '#2c2f36'); base.position.y = .015; g.add(base);
      const stem = cyl(.012, .012, .36, '#c9a24f'); stem.position.y = .2; g.add(stem);
      const shade = new THREE.Mesh(new THREE.CylinderGeometry(.06, .13, .1, 24, 1, true), M(it.shade || '#2e6b4f')); shade.position.y = .4; shade.material.side = THREE.DoubleSide; shade.castShadow = true; g.add(shade);
      const glow = new THREE.Mesh(new THREE.CircleGeometry(.11, 24), new THREE.MeshBasicMaterial({ color: new THREE.Color('#fff2c4') })); glow.rotation.x = Math.PI / 2; glow.position.y = .352; glow.userData.noOutline = true; g.add(glow);
      // the lamp's point light is off by default: in two-band shading it paints a hard disc on the wall
      if (it.light === true) { const L = new THREE.PointLight(it.lightColor || '#ffd9a0', it.intensity ?? .6, 1.6, 2); L.position.set(0, .34, 0); g.add(L); }
      return {}; },
    frame(it, g) { const [w, h] = it.size || [.6, .8]; box(w, h, .03, it.color || '#3a2c22', 0, 0, 0, g);
      if (it.image) { const tex = new THREE.TextureLoader().load(it.image); tex.colorSpace = THREE.SRGBColorSpace;
        const pic = new THREE.Mesh(new THREE.PlaneGeometry(w - .08, h - .08), new THREE.MeshBasicMaterial({ map: tex })); pic.position.z = .017; pic.userData.noOutline = true; g.add(pic); }
      else { const c = document.createElement('canvas'); c.width = 256; c.height = Math.round(256 * h / w); const x = c.getContext('2d');
        x.fillStyle = it.paper || '#efe6d2'; x.fillRect(0, 0, c.width, c.height); x.strokeStyle = '#b08d4a'; x.lineWidth = 6; x.strokeRect(14, 14, c.width - 28, c.height - 28);
        const lines = (it.text || 'CERTIFICATE').split('\n'), fs = Math.min(22, Math.floor((c.height * .55) / (lines.length + .5)));
        x.fillStyle = '#3a3226'; x.font = `bold ${fs}px serif`; x.textAlign = 'center'; lines.forEach((l, i) => x.fillText(l, c.width / 2, c.height * .2 + fs + i * fs * 1.3));
        x.fillStyle = '#9b2f2a'; x.beginPath(); x.arc(c.width / 2, c.height - 34, 13, 0, 7); x.fill();
        const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
        const pic = new THREE.Mesh(new THREE.PlaneGeometry(w - .08, h - .08), new THREE.MeshBasicMaterial({ map: tex })); pic.position.z = .017; pic.userData.noOutline = true; g.add(pic); }
      return {}; },
    sign(it, g) { const [w, h] = it.size || [1.6, .32]; const c = document.createElement('canvas'); c.width = 1024; c.height = Math.round(1024 * h / w); const x = c.getContext('2d');
      x.fillStyle = it.color || '#1f2a3d'; x.fillRect(0, 0, c.width, c.height); x.fillStyle = it.textColor || '#e8d7a8'; x.textAlign = 'center'; x.textBaseline = 'middle';
      x.font = `600 ${Math.round(c.height * .38)}px Georgia, serif`; x.fillText(it.text || '', c.width / 2, c.height * .42);
      if (it.sub) { x.font = `500 ${Math.round(c.height * .16)}px sans-serif`; x.fillText(it.sub, c.width / 2, c.height * .78); }
      const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, .03), [M(it.color || '#1f2a3d'), M(it.color || '#1f2a3d'), M(it.color || '#1f2a3d'), M(it.color || '#1f2a3d'), new THREE.MeshBasicMaterial({ map: tex }), M(it.color || '#1f2a3d')]);
      m.castShadow = true; g.add(m); return {}; },
    rug(it, g) { const [w, d] = it.size || [2.6, 1.8]; const r = new THREE.Mesh(new THREE.BoxGeometry(w, .012, d), M(it.color || '#7c3b34')); r.position.y = .006; r.receiveShadow = true; g.add(r);
      const b = new THREE.Mesh(new THREE.BoxGeometry(w - .2, .014, d - .2), M(it.inner || '#8e4a40')); b.position.y = .007; b.receiveShadow = true; g.add(b); return {}; },
    papers(it, g) { for (let i = 0; i < (it.count || 3); i++) { const p = box(.21, .004, .297, i % 2 ? '#f4efe2' : '#ebe4d3', (i - 1) * .015, .002 + i * .004, (i - 1) * .02, g); p.rotation.y = deg((i - 1) * 6); } return {}; },
    mug(it, g) { const m = cyl(.04, .036, .1, it.color || '#e9e1cf'); m.position.y = .05; g.add(m); return {}; },
    nameplate(it, g) { const c = document.createElement('canvas'); c.width = 512; c.height = 96; const x = c.getContext('2d');
      x.fillStyle = '#2b2b2b'; x.fillRect(0, 0, 512, 96); x.fillStyle = '#d9b25c'; x.font = '600 48px Georgia, serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(it.text || '', 256, 50);
      const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; const m = new THREE.Mesh(new THREE.BoxGeometry(.3, .06, .05), [M('#2b2b2b'), M('#2b2b2b'), M('#2b2b2b'), M('#2b2b2b'), new THREE.MeshBasicMaterial({ map: tex }), M('#2b2b2b')]);
      m.position.y = .03; m.rotation.x = deg(-12); m.castShadow = true; g.add(m); return {}; },
    // ── bakery (M5): a bakery must read as a bakery. Breads are built from a few shaped primitives with score marks.
    bread(it, g) { addBread(g, it.kind || 'boule', it.color, 0, 0, 0, it.rot || 0, it.scale || 1); return {}; },
    basket(it, g) { const [w, d] = it.size || [.42, .3], hgt = it.h || .13, c = it.color || '#b07a42';
      box(w, .02, d, it.dark || '#8a5a2e', 0, .01, 0, g);
      for (const [x, z, sw, sd] of [[0, -d / 2, w, .02], [0, d / 2, w, .02], [-w / 2, 0, .02, d], [w / 2, 0, .02, d]]) box(sw, hgt, sd, c, x, hgt / 2, z, g);
      for (let i = 1; i < 4; i++) { box(w + .005, .012, d + .005, it.dark || '#8a5a2e', 0, hgt * i / 4, 0, g); }
      const kinds = it.breads || ['roll', 'roll', 'roll', 'roll', 'roll', 'roll']; let seed = it.seed || 5; const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
      kinds.forEach((k, i) => { const cols = Math.ceil(Math.sqrt(kinds.length * w / d)), rr = Math.floor(i / cols), cc = i % cols;
        addBread(g, k, null, (cc + .5) / cols * w - w / 2 + (rnd() - .5) * .02, hgt * .75, ((rr + .5) / Math.ceil(kinds.length / cols)) * d - d / 2, rnd() * 360, it.scale || 1); });
      return {}; },
    display_case(it, g) { const [w, h, d] = it.size || [1.6, 1.05, .6], body = it.color || '#6e4a30', trim = it.trim || '#d9b25c';
      box(w, h * .55, d, body, 0, h * .275, 0, g);                                                     // cabinet base
      box(w + .04, .04, d + .04, it.top || '#e8dcc6', 0, h * .55 + .02, 0, g);
      for (let i = 0; i < 4; i++) box(w / 4 - .05, h * .4, .012, it.panel || '#5a3a26', -w / 2 + w / 8 + i * w / 4, h * .3, d / 2 + .004, g);
      const gt = h * .45, y0 = h * .57;                                                                   // glazed part: posts, top, glass edge highlights
      for (const x of [-w / 2, w / 2]) for (const z of [-d / 2, d / 2]) box(.025, gt, .025, trim, x, y0 + gt / 2, z, g);
      box(w, .025, .025, trim, 0, y0 + gt, d / 2, g); box(w, .025, .025, trim, 0, y0 + gt, -d / 2, g);
      const glass = new THREE.Mesh(new THREE.PlaneGeometry(w, gt), new THREE.MeshBasicMaterial({ color: '#dff0ff', transparent: true, opacity: .1, depthWrite: false }));
      glass.position.set(0, y0 + gt / 2, d / 2); glass.userData.noOutline = true; glass.userData.kind = 'glass'; g.add(glass);
      for (let i = 0; i < 3; i++) { const sh = new THREE.Mesh(new THREE.PlaneGeometry(.03 + i * .02, gt * .9), new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, opacity: .22, depthWrite: false }));
        sh.position.set(-w * .3 + i * .09, y0 + gt / 2, d / 2 + .002); sh.rotation.z = .25; sh.userData.noOutline = true; sh.userData.kind = 'glass'; g.add(sh); }
      // two tiers of bread on trays
      const tiers = it.tiers || [['croissant', 'croissant', 'croissant', 'croissant', 'croissant', 'croissant', 'croissant'], ['boule', 'loaf', 'boule', 'loaf', 'boule']];
      tiers.forEach((row, ti) => { const ty = y0 + .02 + ti * gt * .45, tz = ti ? -d * .18 : d * .12;
        box(w - .1, .015, d * .42, it.tray || '#c9c3b6', 0, ty, tz, g);
        row.forEach((k, i) => addBread(g, k, null, -w / 2 + .1 + (i + .5) * (w - .2) / row.length, ty + .01, tz, (i * 37) % 60 - 30, it.scale || 1)); });
      return { top: { y: h } }; },
    bread_rack(it, g) { const [w, h, d] = it.size || [1.8, 1.9, .4], c = it.color || '#7a4f33', rows = it.rows || 4;
      box(.05, h, d, c, -w / 2, h / 2, 0, g); box(.05, h, d, c, w / 2, h / 2, 0, g); box(w, h, .02, it.back || '#5a3a26', 0, h / 2, -d / 2, g);
      const kinds = it.breads || ['boule', 'loaf', 'baguette', 'boule', 'rye']; let seed = it.seed || 11; const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
      for (let r = 0; r < rows; r++) { const y = .25 + r * (h - .35) / (rows - 1 || 1);
        const sh = box(w - .05, .03, d - .04, c, 0, y, 0, g); sh.rotation.x = deg(-8);                // slanted shelves show the loaves to the room
        box(w - .05, .06, .02, c, 0, y + .03, d / 2 - .03, g);
        const k = kinds[r % kinds.length], n = k === 'baguette' ? 0 : Math.floor((w - .1) / (k === 'roll' ? .11 : .24));
        if (k === 'baguette') { for (let i = 0; i < 9; i++) { addBread(g, 'baguette', null, -w / 2 + .15 + i * (w - .3) / 8, y + .05, -.02, 90 + (rnd() - .5) * 8, 1, deg(-62)); } }
        for (let i = 0; i < n; i++) addBread(g, k, null, -w / 2 + .12 + i * (w - .2) / n + (rnd() - .5) * .03, y + .03, (rnd() - .5) * .06, rnd() * 360, it.scale || 1); }
      return {}; },
    oven(it, g) { const [w, h, d] = it.size || [1.3, 1.8, .9], c = it.color || '#3d4148', steel = it.steel || '#9aa2ab';
      box(w, h, d, c, 0, h / 2, 0, g);
      for (let i = 0; i < 2; i++) { const y = .55 + i * .55;
        box(w * .86, .42, .03, steel, 0, y, d / 2 + .015, g);
        const win = new THREE.Mesh(new THREE.PlaneGeometry(w * .5, .14), new THREE.MeshBasicMaterial({ color: new THREE.Color(it.glow || '#ffb45c') })); win.position.set(0, y + .03, d / 2 + .032); win.userData.noOutline = true; g.add(win);
        const hd = box(w * .6, .03, .04, '#2a2c31', 0, y + .17, d / 2 + .05, g); hd.castShadow = false; }
      box(w + .04, .12, d + .04, steel, 0, h + .06, 0, g); box(.25, .5, .25, steel, w * .3, h + .35, -d * .2, g);   // hood and flue
      return {}; },
    till(it, g) { box(.32, .1, .3, it.color || '#3a3d44', 0, .05, 0, g); const s = box(.26, .14, .03, '#2a2c31', 0, .19, -.08, g); s.rotation.x = deg(-15);
      const sc = new THREE.Mesh(new THREE.PlaneGeometry(.2, .09), new THREE.MeshBasicMaterial({ color: '#bfe3c8' })); sc.position.set(0, .19, -.062); sc.rotation.x = deg(-15); sc.userData.noOutline = true; g.add(sc);
      for (let i = 0; i < 3; i++) for (let j = 0; j < 4; j++) box(.04, .012, .03, '#d8d2c4', -.09 + j * .06, .105, .04 + i * .04, g);
      return {}; },
    chalkboard(it, g) { const [w, h] = it.size || [1.0, .75]; const c = document.createElement('canvas'); c.width = 768; c.height = Math.round(768 * h / w); const x = c.getContext('2d');
      x.fillStyle = it.color || '#26302b'; x.fillRect(0, 0, c.width, c.height);
      x.fillStyle = 'rgba(255,255,255,.05)'; for (let i = 0; i < 40; i++) x.fillRect((i * 97) % c.width, (i * 53) % c.height, 120, 6);
      x.fillStyle = '#f4efe2'; x.textBaseline = 'middle'; x.font = `italic 600 ${Math.round(c.height * .12)}px Georgia, serif`; x.textAlign = 'center'; x.fillText(it.title || 'Today', c.width / 2, c.height * .13);
      const rows = it.rows || []; x.font = `500 ${Math.round(c.height * .075)}px Georgia, serif`;
      rows.forEach(([a, b], i) => { const y = c.height * (.3 + i * .66 / Math.max(rows.length, 1)); x.textAlign = 'left'; x.fillText(a, c.width * .08, y); x.textAlign = 'right'; x.fillStyle = '#f1d99a'; x.fillText(b, c.width * .92, y); x.fillStyle = '#f4efe2'; });
      const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
      box(w + .08, h + .08, .03, it.frame || '#7a4f33', 0, 0, -.01, g);
      const pic = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex })); pic.position.z = .008; pic.userData.noOutline = true; g.add(pic); return {}; },
    sacks(it, g) { (it.list || [[0, 0, 0], [.42, 0, .05], [.2, .32, 0]]).forEach(([x, y, z], i) => { const s = new THREE.Mesh(new THREE.SphereGeometry(.22, 18, 12), M(it.color || '#e6d9bd'));
        s.scale.set(1, 1.25, .72); s.position.set(x, .26 + y, z); s.rotation.z = (i % 2 ? .12 : -.08); s.castShadow = s.receiveShadow = true; g.add(s);
        const band = new THREE.Mesh(new THREE.CylinderGeometry(.2, .2, .07, 18, 1, true), M(it.band || '#2f5a4a')); band.scale.set(1, 1, .72); band.position.set(x, .26 + y, z + .0); band.rotation.z = s.rotation.z; g.add(band); });
      return {}; },
    pendant(it, g) { const L = it.drop || .9; const cord = cyl(.006, .006, L, '#1d1d1f', 6); cord.position.y = -L / 2; g.add(cord);
      const sh = new THREE.Mesh(new THREE.CylinderGeometry(.06, .2, .16, 24, 1, true), M(it.color || '#2f5a4a')); sh.material.side = THREE.DoubleSide; sh.position.y = -L - .06; sh.castShadow = false; g.add(sh);
      const bulb = new THREE.Mesh(new THREE.CircleGeometry(.17, 24), new THREE.MeshBasicMaterial({ color: '#fff0c8' })); bulb.rotation.x = Math.PI / 2; bulb.position.y = -L - .13; bulb.userData.noOutline = true; g.add(bulb);
      return {}; },
    tiles(it, g) { const [w, h] = it.size || [2, 1]; const c = document.createElement('canvas'); c.width = 512; c.height = Math.round(512 * h / w); const x = c.getContext('2d');
      x.fillStyle = it.grout || '#cfc6b6'; x.fillRect(0, 0, c.width, c.height); const tw = c.width / (w / .15), th = tw / 2;
      for (let r = 0; r * th < c.height; r++) for (let k = -1; k * tw < c.width; k++) { x.fillStyle = it.color || '#f3ede2'; x.fillRect(k * tw + (r % 2) * tw / 2 + 1.5, r * th + 1.5, tw - 3, th - 3); }
      const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), stage.propMaterial('#ffffff')); m.material = m.material.clone(); m.material.map = tex; m.receiveShadow = true; m.userData.noOutline = true; g.add(m); return {}; },
    counter(it, g) { const [w, h, d] = it.size || [2.4, 1.0, .6]; box(w, h, d, it.color || '#7a4f33', 0, h / 2, 0, g); box(w + .06, .05, d + .06, it.top || '#d9c7a3', 0, h + .025, 0, g); return { top: { y: h + .05 } }; },
  };

  for (const it of spec.items || []) {
    const g = new THREE.Group(); g.name = it.id || it.type;
    const make = C[it.type]; if (!make) { console.warn('env: unknown item', it.type); continue; }
    const a = make(it, g) || {};
    g.position.set(it.pos[0], it.pos[1] ?? 0, it.pos[2]); g.rotation.y = deg(it.rot || 0);
    if (it.y) g.position.y = it.y;
    root.add(g); items[g.name] = { group: g, spec: it };
    // anchors in world space: seat (pelvis target, facing out of the chair), top (desk surface)
    const fwd = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(0, 1, 0), deg(it.rot || 0));
    if (a.seat) anchors[`${g.name}.seat`] = { pos: [it.pos[0] + fwd.x * (a.seat.back || .07), it.pos[2] + fwd.z * (a.seat.back || .07)], yaw: (it.rot || 0), y: a.seat.y, item: g.name };
    if (a.top) anchors[`${g.name}.top`] = { y: (it.pos[1] ?? 0) + a.top.y, pos: [it.pos[0], it.pos[2]] };
    for (const [k, v] of Object.entries(it.anchors || {})) anchors[`${g.name}.${k}`] = v;
  }
  root.traverse(o => { if (o.isMesh && o.userData.noOutline && o.material) o.material.userData.outlineParameters = { visible: false }; });
  stage.scene.add(root);
  return { root, anchors, items,
    // fit a chair to its sitter: scale the seat height so the seat top meets the sitter's lowest pelvis height
    fitSeat(name, pelvisY, drop = .09) { const I = items[name]; if (!I) return null; const target = pelvisY - drop, s = I.spec.seat || .46;
      I.group.scale.y = target / s; I.group.updateMatrixWorld(true); return target; } };
}
