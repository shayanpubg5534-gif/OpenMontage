// P13 pilot 3D scene (three_shot.mjs module): the mortgage-backed security as an architect's miniature on a drafting
// table, animated from the narration. The storyboard still (tranches.js) is kept unchanged; this is its pilot version.
//
// Financial rules it keeps (direction/CONCEPT_NOTES.md, securitisation):
//   FOUNDATION = the pool (thousands of mortgages as small houses; the family's is gold). The pool is not the security.
//   BUILDING   = the security issued on the pool, in tranches (floors): equity at the bottom, mezzanine, senior on top.
//   PAYMENTS   rise through the servicer's pipe and are paid from the top down (priority): senior floors light first.
//   LOSSES     rise from the bottom (allocation): equity first, then mezzanine. Senior floors stay above the flood while
//              the subordination below holds; they stay lit (still paid first) and are marked down in the overlay (downgraded, market value falls).
// Payment priority (top-down, green, from the pipe) and loss allocation (bottom-up, red, from the foundation) never share
// a direction or a colour.
//
// EVENTS (shot-local seconds; omit a key for "not in this shot"):
//   build: [t0, t1]   floors rise onto the pool, bottom to top (issuance); absent = already built
//   flow:  t          payment drops climb the pipe from t (the family's gold drop first); stop: t dries the flow
//   fill:  [t0, t1]   windows light floor by floor from the top (absent = lit from the start if flow, else per `lit`)
//   lit:   0|1        windows lit at the start (a shot that opens on a paying building)
//   red:   [t0, t1]   houses in the pool turn red (defaults spread; the family's first)
//   dim:   [t0, t1]   windows go dark from the bottom as cash shrinks (equity 0, lower mezzanine 0, upper .3, senior .9)
//   flood: [t0, t1, level]  the loss level rises from the foundation to `level` × (equity + mezzanine)
//   flood2: [t0, t1, level] an optional second stage (equity first, then mezzanine on its own word)
export async function build({ THREE, scene: S, events }) {
  const E = events || {};
  S.background = new THREE.Color('#1d1814'); S.fog = new THREE.Fog('#1d1814', 7, 16);
  let seed = 23; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const tex = (w, h, draw, rep) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); } return t; };
  const M = o => new THREE.MeshStandardMaterial({ roughness: .85, ...o });
  const ss = x => (x = Math.min(1, Math.max(0, x)), x * x * (3 - 2 * x));
  const ramp = (t, r) => r ? ss((t - r[0]) / Math.max(1e-3, r[1] - r[0])) : 0;

  // ── the studio: a drafting table under a warm lamp, a soft backdrop sweep, a ruler, a pencil, a cutting mat ─────
  const desk = tex(1024, 1024, (g, w, h) => { g.fillStyle = '#e7d9bc'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { g.fillStyle = 'rgba(120,90,50,' + rnd() * .05 + ')'; g.fillRect(rnd() * w, rnd() * h, 2, 2); } }, [3, 3]);
  const table = new THREE.Mesh(new THREE.PlaneGeometry(16, 12), M({ map: desk, roughness: .95 })); table.rotation.x = -Math.PI / 2; table.receiveShadow = true; S.add(table);
  const mat = tex(1024, 1024, (g, w, h) => { g.fillStyle = '#2f4a3f'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(230,240,230,.22)'; g.lineWidth = 2;
    for (let x = 0; x <= w; x += 32) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.beginPath(); g.moveTo(0, x); g.lineTo(w, x); g.stroke(); }
    g.strokeStyle = 'rgba(240,220,150,.45)'; g.lineWidth = 3; for (let x = 0; x <= w; x += 160) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.beginPath(); g.moveTo(0, x); g.lineTo(w, x); g.stroke(); } });
  const cm = new THREE.Mesh(new THREE.BoxGeometry(5.2, .01, 3.6), M({ map: mat, roughness: .9 })); cm.position.set(0, .005, 0); cm.receiveShadow = true; S.add(cm);
  const sweep = tex(64, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#120f0c'); gr.addColorStop(.7, '#3a2e24'); gr.addColorStop(1, '#5a4634'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const back = new THREE.Mesh(new THREE.PlaneGeometry(24, 9), new THREE.MeshBasicMaterial({ map: sweep })); back.position.set(0, 4.2, -6.5); S.add(back);
  const ruler = new THREE.Mesh(new THREE.BoxGeometry(2.6, .012, .16), M({ color: '#b9bec4', metalness: .8, roughness: .35 })); ruler.position.set(-1.0, .016, 2.05); ruler.rotation.y = .18; ruler.castShadow = ruler.receiveShadow = true; S.add(ruler);
  const ticks = tex(1024, 64, (g, w, h) => { g.fillStyle = '#c3c8ce'; g.fillRect(0, 0, w, h); g.fillStyle = '#2b2b2b'; for (let i = 0; i < 100; i++) g.fillRect(8 + i * 10, 0, 2, i % 10 ? 18 : 34); });
  const tk = new THREE.Mesh(new THREE.PlaneGeometry(2.58, .14), M({ map: ticks, metalness: .6, roughness: .4 })); tk.rotation.x = -Math.PI / 2; tk.position.set(0, .0065, 0); ruler.add(tk);
  const pencil = new THREE.Mesh(new THREE.CylinderGeometry(.018, .018, .9, 6), M({ color: '#d8a233' })); pencil.rotation.z = Math.PI / 2; pencil.rotation.y = -.5; pencil.position.set(2.0, .02, 1.5); pencil.castShadow = true; S.add(pencil);
  const tip = new THREE.Mesh(new THREE.ConeGeometry(.018, .07, 6), M({ color: '#e8cfa5' })); tip.rotation.z = -Math.PI / 2; tip.position.set(.485, 0, 0); pencil.add(tip);

  // contact shadow: a soft dark pool under the model, so it sits on the table (shadow maps alone read too clean)
  const ao = tex(256, 256, (g, w, h) => { const gr = g.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, w / 2); gr.addColorStop(0, 'rgba(0,0,0,.55)'); gr.addColorStop(.6, 'rgba(0,0,0,.25)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const aoP = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 3.4), new THREE.MeshBasicMaterial({ map: ao, transparent: true, depthWrite: false })); aoP.rotation.x = -Math.PI / 2; aoP.position.y = .012; S.add(aoP);

  // ── the pool: a card plinth with a brass plaque, its top a town of small houses ────────────────────────────────
  const PW = 3.6, PD = 2.4, PH = .16;
  const card = tex(512, 128, (g, w, h) => { g.fillStyle = '#d7c6a2'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(80,60,30,.25)'; for (let y = 6; y < h; y += 8) g.fillRect(0, y, w, 1); });
  const plinth = new THREE.Mesh(new THREE.BoxGeometry(PW, PH, PD), M({ map: card })); plinth.position.y = PH / 2; plinth.castShadow = plinth.receiveShadow = true; S.add(plinth);
  const plq = tex(1024, 192, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#d9b45e'); gr.addColorStop(1, '#a77f33'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#6f5220'; g.lineWidth = 6; g.strokeRect(8, 8, w - 16, h - 16); g.fillStyle = '#3b2a10'; g.textAlign = 'center';
    g.font = 'bold 68px Georgia'; g.fillText('THE POOL', w / 2, 92); g.font = '40px Georgia'; g.fillText('thousands of mortgages (illustrative)', w / 2, 150); });
  const plaque = new THREE.Mesh(new THREE.PlaneGeometry(1.2, .14 * 1.6), M({ map: plq, metalness: .7, roughness: .35 })); plaque.scale.y = .62; plaque.position.set(-.9, PH / 2, PD / 2 + .002); S.add(plaque);
  const COLS = 44, ROWS = 28, hs = .062, gap = PW / COLS, gz = PD / ROWS, n = COLS * ROWS;
  const wallG = new THREE.BoxGeometry(hs, hs * .7, hs * .9), roofG = new THREE.ConeGeometry(hs * .62, hs * .5, 4); roofG.rotateY(Math.PI / 4);
  const walls = new THREE.InstancedMesh(wallG, M({ color: '#fff' }), n), roofs = new THREE.InstancedMesh(roofG, M({ color: '#fff' }), n);
  walls.castShadow = roofs.castShadow = true; walls.receiveShadow = roofs.receiveShadow = true;
  const FAM = { c: 30, r: ROWS - 2 }, m4 = new THREE.Matrix4(), col = new THREE.Color(), houses = [];
  for (let r = 0, k = 0; r < ROWS; r++) for (let q = 0; q < COLS; q++, k++) {
    const x = -PW / 2 + gap * (q + .5), z = -PD / 2 + gz * (r + .5), fam = q === FAM.c && r === FAM.r, sc = fam ? 1.7 : 1;
    m4.makeTranslation(x, PH + hs * .35 * sc, z).multiply(new THREE.Matrix4().makeScale(sc, sc, sc)); walls.setMatrixAt(k, m4);
    m4.makeTranslation(x, PH + hs * .95 * sc, z).multiply(new THREE.Matrix4().makeScale(sc, sc, sc)); roofs.setMatrixAt(k, m4);
    // the share that defaults in this illustration (~14%), and when each turns red within E.red; the family's first
    const bad = fam || rnd() < .14; houses.push({ k, fam, bad, at: fam ? 0 : rnd(), w: ['#efe6d3', '#e4d8bf', '#d9ccb2'][k % 3], rf: ['#7a5a46', '#6a5448', '#85664e'][k % 3] });
  }
  S.add(walls, roofs);
  const famX = -PW / 2 + gap * (FAM.c + .5), famZ = -PD / 2 + gz * (FAM.r + .5);
  const famGlow = new THREE.PointLight('#ffcf7a', 2.4, .9, 2); famGlow.position.set(famX, PH + .2, famZ); S.add(famGlow);
  const paintHouses = t => { const u = ramp(t, E.red);
    for (const h of houses) { const red = E.red && h.bad && u > h.at * .85 + (h.fam ? 0 : .1);
      walls.setColorAt(h.k, col.set(h.fam ? (red ? '#a8322a' : '#f0be4e') : red ? '#8e3a30' : h.w)); roofs.setColorAt(h.k, col.set(h.fam ? (red ? '#6e1f19' : '#b9862c') : red ? '#5e231d' : h.rf)); }
    walls.instanceColor.needsUpdate = roofs.instanceColor.needsUpdate = true; famGlow.intensity = E.red && u > 0 ? 0 : 2.4; };

  // ── the security: floors (tranches) with window bands, slab edges, a parapet and rooftop plant ───────────────────
  const BW = 1.7, BD = 1.1, FH = .2, TR = [['equity', 1, '#c98d4a'], ['mezzanine', 2, '#7f93ab'], ['senior', 5, '#efe7d6']];
  const winTex = (c) => tex(512, 64, (g, w, h) => { g.fillStyle = c; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(43,33,24,.85)'; g.fillRect(0, 0, w, 3); g.fillRect(0, h - 3, w, 3);
    for (let i = 0; i < 12; i++) { g.fillStyle = '#2c2925'; g.fillRect(10 + i * 42, 14, 26, 36); g.strokeStyle = '#2b2118'; g.lineWidth = 3; g.strokeRect(10 + i * 42, 14, 26, 36); g.fillStyle = '#2b2118'; g.fillRect(22 + i * 42, 14, 2, 36); } });
  const winMask = tex(512, 64, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); for (let i = 0; i < 12; i++) { g.fillStyle = '#fff'; g.fillRect(12 + i * 42, 16, 22, 32); } });
  const floors = []; let y = PH, fi = 0;
  for (const [name, count, c] of TR) for (let i = 0; i < count; i++, fi++) {
    const g = new THREE.Group(); S.add(g);
    const side = M({ map: winTex(c), emissive: new THREE.Color('#a6eab0'), emissiveMap: winMask, emissiveIntensity: 0, color: '#ffffff' });
    const top = M({ color: c });
    const slab = new THREE.Mesh(new THREE.BoxGeometry(BW, FH * .78, BD), [side, side, top, top, side, side]); slab.position.y = FH * .39 + .005; slab.castShadow = slab.receiveShadow = true; g.add(slab);
    const plate = new THREE.Mesh(new THREE.BoxGeometry(BW + .06, FH * .22, BD + .06), M({ color: c, roughness: .7 })); plate.position.y = FH * .89; plate.castShadow = plate.receiveShadow = true; g.add(plate);
    floors.push({ name, g, y0: y, side, idx: fi }); y += FH;
  }
  const roofY = y, NF = floors.length;
  const roof = new THREE.Group(); S.add(roof);
  const rs = new THREE.Mesh(new THREE.BoxGeometry(BW + .1, .05, BD + .1), M({ color: '#2b2118' })); rs.position.y = .025; rs.castShadow = true; roof.add(rs);
  for (const [w, d, x, z] of [[BW + .1, .03, 0, BD / 2 + .035], [BW + .1, .03, 0, -BD / 2 - .035], [.03, BD + .1, BW / 2 + .035, 0], [.03, BD + .1, -BW / 2 - .035, 0]]) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(w, .06, d), M({ color: '#3a2e24' })); p.position.set(x, .08, z); p.castShadow = true; roof.add(p); }
  for (const [x, z, w, h] of [[-.45, -.2, .32, .12], [.1, .15, .22, .1], [.5, -.25, .18, .16]]) { const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, w * .8), M({ color: '#8d8a84', metalness: .4, roughness: .5 })); b.position.set(x, .05 + h / 2, z); b.castShadow = true; roof.add(b); }
  const rules = [PH + FH, PH + 3 * FH].map(yy => { const r = new THREE.Mesh(new THREE.BoxGeometry(BW + .14, .022, BD + .14), M({ color: '#c9963a', metalness: .5, roughness: .4 })); r.position.y = yy; S.add(r); return r; });
  const canopy = new THREE.Mesh(new THREE.BoxGeometry(.5, .02, .18), M({ color: '#2b2118' })); canopy.position.set(-.3, PH + .13, BD / 2 + .09); canopy.castShadow = true; S.add(canopy);

  // ── the servicer's pipe: drops climb from the pool to the roof (the family's gold drop leads) ───────────────────
  const px = BW / 2 + .16, pz = BD / 2 - .2, pipeM = M({ color: '#6b5a48', metalness: .5, roughness: .45 });
  const pipe = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, roofY + .2 - PH, 16), pipeM); pipe.position.set(px, PH + (roofY + .2 - PH) / 2, pz); pipe.castShadow = true; S.add(pipe);
  const spout = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, .3, 16), pipeM); spout.rotation.z = Math.PI / 2; spout.position.set(px - .15, roofY + .2, pz); S.add(spout);
  const dropM = new THREE.MeshStandardMaterial({ color: '#7fd38e', emissive: '#4fb766', emissiveIntensity: 1.1 });
  const famM = new THREE.MeshStandardMaterial({ color: '#f1c45c', emissive: '#c9963a', emissiveIntensity: 1.2 });
  const drops = Array.from({ length: 10 }, (_, i) => { const d = new THREE.Mesh(new THREE.SphereGeometry(.032, 14, 10), i === 0 ? famM : dropM); d.visible = false; S.add(d); return d; });
  const H = roofY + .2 - PH, path = u => u < .82 ? [px + .06, PH + .1 + u / .82 * H, pz + .03] : [px + .06 - (u - .82) / .18 * .45, roofY + .2, pz + .03];

  // ── losses: the flood (red, from the bottom) ────────────────────────────────────────────────────────────────────
  const floodM = new THREE.MeshStandardMaterial({ color: '#b5473a', emissive: '#5a1610', emissiveIntensity: .5, transparent: true, opacity: .64, roughness: .25 });
  const flood = new THREE.Mesh(new THREE.BoxGeometry(BW + .2, 1, BD + .2), floodM); flood.visible = false; S.add(flood);
  const surf = new THREE.Mesh(new THREE.PlaneGeometry(BW + .2, BD + .2), new THREE.MeshStandardMaterial({ color: '#d0604f', roughness: .15, transparent: true, opacity: .85 })); surf.rotation.x = -Math.PI / 2; surf.visible = false; S.add(surf);

  // ── light: a warm architect's lamp (key, soft shadow), cool window fill, rim; a little of the room bounce ──────
  S.add(new THREE.HemisphereLight('#cfd6e4', '#2e241b', .22));
  const key = new THREE.SpotLight('#ffdcb0', 95, 20, .42, .75, 1.3); key.position.set(-2.6, 5.2, 3.0); key.target.position.set(.1, .7, 0); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -.0003; key.shadow.radius = 4; S.add(key, key.target);
  const fill = new THREE.DirectionalLight('#9fb4d6', .45); fill.position.set(4, 3, 2); S.add(fill);
  const rim = new THREE.DirectionalLight('#c6d4ee', .9); rim.position.set(2, 3.5, -5); S.add(rim);

  // the loss level: stage 1 (flood) fills equity; stage 2 (flood2, optional) rises into mezzanine
  const floodAt = t => (E.flood ? ramp(t, E.flood) * E.flood[2] : 0) + (E.flood2 ? ramp(t, E.flood2) * (E.flood2[2] - E.flood[2]) : 0);
  const state = t => {
    const b = E.build ? ss((t - E.build[0]) / (E.build[1] - E.build[0])) : 1;
    const flowOn = E.flow != null && t >= E.flow && (E.stop == null || t < E.stop + 1.2);
    const fl = floodAt(t);
    return [b.toFixed(3), flowOn ? (t * 30 | 0) : 'n', E.fill ? ramp(t, E.fill).toFixed(3) : '-', E.red ? ramp(t, E.red).toFixed(2) : '-', E.dim ? ramp(t, E.dim).toFixed(2) : '-', fl.toFixed(3)].join(',');
  };
  const update = t => {
    // issuance: floors arrive bottom to top, each dropping into place
    const b = E.build ? (t - E.build[0]) / (E.build[1] - E.build[0]) : 9;
    floors.forEach(f => { const u = ss(b * (NF + 2) / 1 - f.idx * 1.0); f.g.visible = u > 0; f.g.position.y = f.y0 + (1 - u) * .45; f.g.scale.setScalar(.96 + .04 * u); });
    const ub = ss(b * (NF + 2) - NF); roof.visible = ub > 0; roof.position.y = roofY + (1 - ub) * .45;
    rules.forEach((r, i) => { r.visible = ss(b * (NF + 2) - (i ? 3 : 1)) > .99; });
    pipe.visible = spout.visible = ub > .99; canopy.visible = b * (NF + 2) > 1;
    // payments: lit windows top-down (priority)
    const fillU = E.fill ? ramp(t, E.fill) : (E.lit ? 1 : 0), dimU = ramp(t, E.dim);
    floors.forEach(f => { const order = (NF - 1 - f.idx) / NF;                 // the top floor is first in line
      let lit = E.fill ? ss((fillU - order) * NF) : (E.lit ? 1 : 0);
      const stressed = f.name === 'senior' ? .9 : f.name === 'mezzanine' ? (f.idx === 1 ? 0 : .3) : 0;   // shortfalls hit the bottom first; senior is still paid
      lit = lit * (1 - dimU) + Math.min(lit, stressed) * dimU;
      f.side.emissiveIntensity = 1.15 * lit; });
    // the flow up the pipe
    const flowing = E.flow != null && t >= E.flow, fade = E.stop != null ? 1 - ss((t - E.stop) / .5) : 1;
    drops.forEach((d, i) => { if (!flowing || fade <= 0 || (E.stop != null && i > 2 && t > E.stop)) { d.visible = false; return; }
      const u = ((t - E.flow) * .9 - i * .12); d.visible = u > 0; const p = path(((u % 1) + 1) % 1); d.position.set(...p); d.scale.setScalar(fade); });
    paintHouses(t);
    // losses: the flood
    const fl = floodAt(t), top = PH + fl * 3 * FH;
    flood.visible = surf.visible = fl > .002; flood.scale.y = Math.max(.001, top - PH); flood.position.y = PH + (top - PH) / 2; surf.position.y = top + .001;
  };
  update(0);
  return { update, state, dynamicShadows: true, roofY, fam: [famX, PH, famZ] };
}
