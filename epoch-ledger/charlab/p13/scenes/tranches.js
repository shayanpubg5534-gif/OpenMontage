// P13 storyboard 3D scene (three_shot.mjs module): the mortgage-backed security as a building, an architect's paper
// model on a drafting table. Built to the mechanism's real rules (direction/CONCEPT_NOTES.md, securitisation):
//   - the FOUNDATION is the pool: thousands of mortgages, each a small house; the family's house is gold. The pool is
//     not the security;
//   - the BUILDING on it is the security, issued in tranches (floors): senior at the top, mezzanine, equity at the bottom;
//   - PAYMENTS rise from the pool through the servicer's pipe to the roof and are paid top-down (the waterfall):
//     senior floors light first;
//   - LOSSES rise from the bottom (the flood): equity is lost first, then mezzanine. Senior floors stay dry while the
//     subordination below them holds; they still dim (fewer payments arriving) and are marked down in price in the
//     overlay, which is what happened to most senior pieces in 2007–08.
// EVENTS: {mode: 0 payments | 1 losses, flood: 0..1 (height of the losses through equity+mezzanine), defaults: 0..1
// (share of the pool's houses gone red)}. Procedural only.
export async function build({ THREE, scene: S, events }) {
  const E = { mode: 0, flood: 0, defaults: 0, ...events };
  S.background = new THREE.Color('#231c16'); S.fog = new THREE.Fog('#231c16', 8, 18);
  let seed = 23; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const tex = (w, h, draw) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  const M = o => new THREE.MeshStandardMaterial({ roughness: .9, ...o });
  // the drafting table: warm paper over wood, with faint ruled lines (the series' ledger line)
  const desk = tex(1024, 1024, (g, w, h) => { g.fillStyle = '#e9dcc0'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 4000; i++) { g.fillStyle = 'rgba(120,90,50,' + rnd() * .06 + ')'; g.fillRect(rnd() * w, rnd() * h, 2, 2); }
    g.strokeStyle = 'rgba(70,90,120,.18)'; g.lineWidth = 2; for (let y = 40; y < h; y += 64) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); } });
  const table = new THREE.Mesh(new THREE.PlaneGeometry(14, 10), M({ map: desk })); table.rotation.x = -Math.PI / 2; table.receiveShadow = true; S.add(table);

  // ── the pool: a plinth whose top is a town of small houses ─────────────────────────────────────────────────────
  const PW = 3.6, PD = 2.4, PH = .16;
  const plinth = new THREE.Mesh(new THREE.BoxGeometry(PW, PH, PD), M({ color: '#cbb896' })); plinth.position.y = PH / 2; plinth.castShadow = plinth.receiveShadow = true; S.add(plinth);
  const COLS = 44, ROWS = 28, hs = .062, gap = PW / COLS, gz = PD / ROWS;
  const wallG = new THREE.BoxGeometry(hs, hs * .7, hs * .9), roofG = new THREE.ConeGeometry(hs * .62, hs * .5, 4); roofG.rotateY(Math.PI / 4);
  const n = COLS * ROWS, walls = new THREE.InstancedMesh(wallG, M({ color: '#fff' }), n), roofs = new THREE.InstancedMesh(roofG, M({ color: '#fff' }), n);
  walls.castShadow = roofs.castShadow = true; walls.receiveShadow = true;
  const m4 = new THREE.Matrix4(), c = new THREE.Color(); let k = 0; const FAM = { c: 30, r: ROWS - 2 };
  const BW = 1.7, BD = 1.1;                                          // the building's footprint (houses under it are hidden)
  for (let r = 0; r < ROWS; r++) for (let q = 0; q < COLS; q++, k++) {
    const x = -PW / 2 + gap * (q + .5), z = -PD / 2 + gz * (r + .5), fam = q === FAM.c && r === FAM.r;
    const under = Math.abs(x) < BW / 2 + .02 && Math.abs(z) < BD / 2 + .02;
    const sc = fam ? 1.7 : 1;
    m4.makeTranslation(x, under ? -1 : PH + hs * .35 * sc, z).multiply(new THREE.Matrix4().makeScale(sc, sc, sc)); walls.setMatrixAt(k, m4);
    m4.makeTranslation(x, under ? -1 : PH + (hs * .7 + hs * .25) * sc, z).multiply(new THREE.Matrix4().makeScale(sc, sc, sc)); roofs.setMatrixAt(k, m4);
    const bad = !fam && rnd() < E.defaults;
    walls.setColorAt(k, c.set(fam ? (E.mode ? '#a8322a' : '#e7b74c') : bad ? '#8e3a30' : ['#efe6d3', '#e4d8bf', '#d9ccb2'][k % 3]));
    roofs.setColorAt(k, c.set(fam ? (E.mode ? '#6e1f19' : '#b9862c') : bad ? '#5e231d' : ['#7a5a46', '#6a5448', '#85664e'][k % 3]));
  }
  S.add(walls, roofs);
  const famX = -PW / 2 + gap * (FAM.c + .5), famZ = -PD / 2 + gz * (FAM.r + .5);
  if (!E.mode) { const glow = new THREE.PointLight('#ffcf7a', 2.5, .8, 2); glow.position.set(famX, PH + .18, famZ); S.add(glow); }

  // ── the security: a building of tranches ───────────────────────────────────────────────────────────────────────
  const FH = .2, TR = [['equity', 1, '#c79a55'], ['mezzanine', 2, '#8d97a3'], ['senior', 5, '#e8e1d2']];
  const floors = []; let y = PH;
  const winTex = (lit, frac, col) => tex(512, 64, (g, w, h) => { g.fillStyle = col; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(43,33,24,.85)'; g.fillRect(0, 0, w, 3); g.fillRect(0, h - 3, w, 3);
    for (let i = 0; i < 12; i++) { const on = lit && (i * 7919 % 12) / 12 < frac; g.fillStyle = on ? '#8fd39a' : '#2f2a26'; g.fillRect(10 + i * 42, 14, 26, 36); g.strokeStyle = '#2b2118'; g.lineWidth = 3; g.strokeRect(10 + i * 42, 14, 26, 36); } });
  for (const [name, count, col] of TR) for (let i = 0; i < count; i++) {
    const g = new THREE.Group(); g.position.y = y; S.add(g);
    const lit = E.mode === 0 ? 1 : name === 'senior' ? .55 : name === 'mezzanine' ? (i === 0 ? 0 : .25) : 0;
    const wt = winTex(lit > 0, lit, col), dark = M({ color: col });
    const side = M({ map: wt, emissive: new THREE.Color('#ffffff'), emissiveMap: wt, emissiveIntensity: lit > 0 ? .28 : 0 });
    const slab = new THREE.Mesh(new THREE.BoxGeometry(BW, FH * .78, BD), [side, side, dark, dark, side, side]); slab.position.y = FH * .39 + .005; slab.castShadow = slab.receiveShadow = true; g.add(slab);
    const plate = new THREE.Mesh(new THREE.BoxGeometry(BW + .06, FH * .22, BD + .06), M({ color: col })); plate.position.y = FH * .89; plate.castShadow = plate.receiveShadow = true; g.add(plate);
    floors.push({ name, g, y0: y, y1: y + FH }); y += FH;
  }
  const roofY = y;
  const roof = new THREE.Mesh(new THREE.BoxGeometry(BW + .1, .05, BD + .1), M({ color: '#2b2118' })); roof.position.y = roofY + .025; roof.castShadow = true; S.add(roof);
  // tranche dividers: an ink rule between tranches (the ledger line), so the three tranches read at a glance
  for (const yy of [PH + FH, PH + 3 * FH]) { const r = new THREE.Mesh(new THREE.BoxGeometry(BW + .14, .022, BD + .14), M({ color: '#c9963a', metalness: .3, roughness: .5 })); r.position.y = yy; S.add(r); }

  // ── the servicer's pipe: payments rise from the pool to the roof, then fall floor by floor ─────────────────────
  const px = BW / 2 + .16, pz = BD / 2 - .2, flowOn = E.mode === 0 ? 1 : .35;
  const pipeM = M({ color: '#6b5a48', metalness: .4, roughness: .5 });
  const pipe = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, roofY + .2 - PH, 16), pipeM); pipe.position.set(px, PH + (roofY + .2 - PH) / 2, pz); pipe.castShadow = true; S.add(pipe);
  const spout = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, .3, 16), pipeM); spout.rotation.z = Math.PI / 2; spout.position.set(px - .15, roofY + .2, pz); S.add(spout);
  const flowM = new THREE.MeshStandardMaterial({ color: '#7fd38e', emissive: '#4fb766', emissiveIntensity: 1.2 * flowOn, transparent: true, opacity: .25 + .7 * flowOn });
  for (let i = 0; i < 9; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.03, 12, 8), flowM); d.position.set(px + .06, PH + .2 + i * (roofY - PH) / 9, pz + .02); if (E.mode === 0 || i % 3 === 0) S.add(d); }
  for (let i = 0; i < 4; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.03, 12, 8), flowM); d.position.set(px - .05 - i * .1, roofY + .2, pz + .05); if (E.mode === 0 || i < 1) S.add(d); }

  // ── losses: a red flood rising from the bottom (equity first, then mezzanine; senior stays above it) ───────────
  if (E.mode === 1 && E.flood > 0) {
    const top = PH + E.flood * 3 * FH;
    const flood = new THREE.Mesh(new THREE.BoxGeometry(BW + .2, top - PH, BD + .2), new THREE.MeshStandardMaterial({ color: '#b5473a', emissive: '#5a1610', emissiveIntensity: .5, transparent: true, opacity: .62, roughness: .3 }));
    flood.position.y = PH + (top - PH) / 2; S.add(flood);
    const surf = new THREE.Mesh(new THREE.PlaneGeometry(BW + .2, BD + .2), new THREE.MeshStandardMaterial({ color: '#d0604f', roughness: .2, transparent: true, opacity: .85 })); surf.rotation.x = -Math.PI / 2; surf.position.y = top + .001; S.add(surf);
  }
  // light: a warm desk lamp (key, shadowed), a cool fill, a rim
  S.add(new THREE.HemisphereLight('#d6dbe6', '#3a2f24', E.mode ? .22 : .32));
  const key = new THREE.SpotLight(E.mode ? '#ffd2b0' : '#ffe0b0', 70, 20, .55, .6, 1.4); key.position.set(-3, 5.5, 3.5); key.target.position.set(0, .7, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -.0004; S.add(key, key.target);
  const rim = new THREE.DirectionalLight('#9fb4d6', .7); rim.position.set(4, 3, -4); S.add(rim);
  return { state: () => 'static', roofY, fam: [famX, PH, famZ] };
}
