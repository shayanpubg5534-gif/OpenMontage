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
      if (it.light === true) { const L = new THREE.PointLight(it.lightColor || '#ffd9a0', it.intensity ?? .6, 1.6, 2);   // off by default: a point light makes a hard banded disc in two-band shading L.position.set(0, .34, 0); g.add(L); }
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
