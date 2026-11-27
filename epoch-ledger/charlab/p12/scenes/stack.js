// P12 3D scene: "bundled with thousands of others into a single security". One family's mortgage folder (labelled, then
// stamped SOLD on "keep") lies on top of a strapped block of thousands of mortgage folders on a pallet; the camera pulls
// back from the one folder to the whole bundle. Nothing moves except the camera and the stamp's print (a state change).
// Procedural only: manila folders with paper edges, woven straps, a timber pallet, a concrete floor, warm key light.
export async function build({ THREE, scene: S, events }) {
  S.background = new THREE.Color('#2b241d'); S.fog = new THREE.Fog('#2b241d', 9, 22);
  let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const tex = (w, h, draw, rep) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); } return t; };
  const fibres = (g, w, h, base, n, a) => { g.fillStyle = base; g.fillRect(0, 0, w, h); for (let i = 0; i < n; i++) { g.strokeStyle = 'rgba(90,60,20,' + (rnd() * a) + ')'; g.lineWidth = 1;
    const x = rnd() * w, y = rnd() * h; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (rnd() - .5) * 14, y + (rnd() - .5) * 4); g.stroke(); } };
  // manila folder top (with the tab and a faint label strip), and its edge: stacked sheets
  const top = tex(512, 384, (g, w, h) => { fibres(g, w, h, '#d2ae6c', 3500, .28); g.strokeStyle = 'rgba(120,85,35,.55)'; g.lineWidth = 4; g.strokeRect(6, 40, w - 12, h - 46);
    g.fillStyle = '#d2b06e'; g.fillRect(40, 4, 170, 40); g.strokeRect(40, 4, 170, 40); g.fillStyle = 'rgba(250,246,236,.85)'; g.fillRect(56, 10, 138, 26); });
  const edge = tex(256, 64, (g, w, h) => { g.fillStyle = '#efe7d6'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 4) { g.fillStyle = 'rgba(120,100,70,' + (.15 + rnd() * .2) + ')'; g.fillRect(0, y, w, 1); }
    g.fillStyle = '#cfae6c'; g.fillRect(0, 0, w, 6); g.fillRect(0, h - 6, w, 6); });
  const strapT = tex(64, 256, (g, w, h) => { g.fillStyle = '#7a2b22'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 6) { g.fillStyle = 'rgba(0,0,0,.18)'; g.fillRect(0, y, w, 2); }
    for (let x = 0; x < w; x += 8) { g.fillStyle = 'rgba(255,220,200,.06)'; g.fillRect(x, 0, 2, h); } }, [1, 8]);
  const wood = tex(512, 128, (g, w, h) => { g.fillStyle = '#8a6a45'; g.fillRect(0, 0, w, h); for (let i = 0; i < 60; i++) { g.strokeStyle = 'rgba(60,40,20,' + rnd() * .35 + ')'; g.lineWidth = 1 + rnd() * 2;
    g.beginPath(); const y = rnd() * h; g.moveTo(0, y); g.bezierCurveTo(w * .3, y + (rnd() - .5) * 10, w * .6, y + (rnd() - .5) * 10, w, y + (rnd() - .5) * 6); g.stroke(); } });
  const concrete = tex(512, 512, (g, w, h) => { g.fillStyle = '#6b655d'; g.fillRect(0, 0, w, h); for (let i = 0; i < 9000; i++) { const v = 80 + rnd() * 50 | 0; g.fillStyle = 'rgba(' + v + ',' + (v - 4) + ',' + (v - 9) + ',.3)'; g.fillRect(rnd() * w, rnd() * h, 2 + rnd() * 4, 2 + rnd() * 4); } }, [8, 8]);
  const label = tex(512, 256, (g, w, h) => { g.fillStyle = '#fbf8f0'; g.fillRect(0, 0, w, h); g.strokeStyle = '#2b2118'; g.lineWidth = 6; g.strokeRect(10, 10, w - 20, h - 20);
    g.fillStyle = '#2b2118'; g.font = 'bold 58px Georgia'; g.fillText('MORTGAGE', 36, 92); g.font = '36px Georgia'; g.fillText('The family · home loan', 36, 152); g.fillText('Signed 2006', 36, 204); });
  const stampT = tex(512, 256, (g, w, h) => { g.clearRect(0, 0, w, h); g.strokeStyle = 'rgba(176,40,30,.92)'; g.lineWidth = 16; g.strokeRect(30, 40, w - 60, h - 80);
    g.fillStyle = 'rgba(176,40,30,.92)'; g.font = 'bold 128px Inter, Arial'; g.textAlign = 'center'; g.fillText('SOLD', w / 2, 175); for (let i = 0; i < 600; i++) { g.clearRect(rnd() * w, rnd() * h, 3, 3); } });
  const M = o => new THREE.MeshStandardMaterial(o);
  const sideM = M({ map: edge, roughness: .9 }), topM = M({ map: top, roughness: .85 });
  // floor and pallet
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshLambertMaterial({ map: concrete })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; S.add(floor);
  const COLS = 22, ROWS = 18, LAYERS = 46, FW = .32, FD = .24, FT = .015, PAL = .14;
  const BW = COLS * FW, BD = ROWS * FD, YTOP = PAL + LAYERS * FT;
  const plankM = M({ map: wood, roughness: .85 });
  for (let i = 0; i < 9; i++) { const p = new THREE.Mesh(new THREE.BoxGeometry(BW + .2, .025, .32), plankM); p.position.set(0, PAL - .0125, -BD / 2 + i * (BD / 8)); p.castShadow = p.receiveShadow = true; S.add(p); }
  for (const x of [-BW / 2 + .1, 0, BW / 2 - .1]) { const b = new THREE.Mesh(new THREE.BoxGeometry(.14, PAL - .025, BD + .1), plankM); b.position.set(x, (PAL - .025) / 2, 0); b.castShadow = true; S.add(b); }
  // the block: only what can be seen is geometry. The top two layers are individual folders (instanced, irregular like a
  // real stack); the sides are the stack's paper edges (a texture of folder edges, layer by layer), so thousands of
  // folders cost a few hundred boxes and four planes
  const sideTex = (cols, w) => tex(2048, 512, (g, W, H) => { g.fillStyle = '#e9dfca'; g.fillRect(0, 0, W, H); const lh = H / (LAYERS - 2), cw = W / cols;
    for (let l = 0; l < LAYERS - 2; l++) for (let c = 0; c < cols; c++) { const x = c * cw + (rnd() - .5) * cw * .06, y = l * lh;
      g.fillStyle = 'hsl(' + (38 + (rnd() - .5) * 6) + ',' + (40 + rnd() * 14) + '%,' + (60 + rnd() * 10) + '%)'; g.fillRect(x, y, cw * .985, lh * .34);
      g.fillStyle = 'rgba(250,244,230,' + (.75 + rnd() * .2) + ')'; g.fillRect(x + cw * .01, y + lh * .34, cw * .96, lh * .4);
      g.fillStyle = 'rgba(90,70,40,.35)'; g.fillRect(x, y + lh * .9, cw, lh * .1); } });
  const wallH = (LAYERS - 2) * FT, wallY = PAL + wallH / 2;
  for (const [w, d, x, z, ry, cols] of [[BW, 0, 0, BD / 2, 0, COLS], [BW, 0, 0, -BD / 2, Math.PI, COLS], [BD, 0, BW / 2, 0, Math.PI / 2, ROWS], [BD, 0, -BW / 2, 0, -Math.PI / 2, ROWS]]) {
    const pl = new THREE.Mesh(new THREE.PlaneGeometry(w, wallH), M({ map: sideTex(cols, w), roughness: .92 })); pl.position.set(x, wallY, z); pl.rotation.y = ry; pl.receiveShadow = true; S.add(pl); }
  const core = new THREE.Mesh(new THREE.BoxGeometry(BW - .01, wallH, BD - .01), M({ color: '#d9c49a' })); core.position.set(0, wallY, 0); core.castShadow = true; S.add(core);
  const n = COLS * ROWS * 2, geo = new THREE.BoxGeometry(FW * .97, FT, FD * .97);
  const im = new THREE.InstancedMesh(geo, [sideM, sideM, topM, sideM, sideM, sideM], n); im.castShadow = im.receiveShadow = true;
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e3 = new THREE.Euler(), col = new THREE.Color(); let k = 0;
  for (let l = LAYERS - 2; l < LAYERS; l++) for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++, k++) {
    e3.set(0, (rnd() - .5) * .09, 0); q.setFromEuler(e3);
    m4.compose(new THREE.Vector3(-BW / 2 + FW / 2 + c * FW + (rnd() - .5) * .03, PAL + FT / 2 + l * FT, -BD / 2 + FD / 2 + r * FD + (rnd() - .5) * .03), q, new THREE.Vector3(1, 1, 1));
    im.setMatrixAt(k, m4); col.setHSL(.1 + (rnd() - .5) * .02, .26 + rnd() * .12, .64 + rnd() * .1); im.setColorAt(k, col);
  }
  S.add(im);
  // straps around the block (woven, two each way)
  const strapM = M({ map: strapT, roughness: .7 });
  for (const x of [-BW * .25, BW * .25]) { const s = new THREE.Mesh(new THREE.BoxGeometry(.06, YTOP - PAL + .02, BD + .02), strapM); s.position.set(x, (YTOP + PAL) / 2, 0); S.add(s);
    const s2 = new THREE.Mesh(new THREE.BoxGeometry(.06, .006, BD + .02), strapM); s2.position.set(x, YTOP + .004, 0); S.add(s2); }
  for (const z of [-BD * .25, BD * .25]) { const s = new THREE.Mesh(new THREE.BoxGeometry(BW + .02, YTOP - PAL + .02, .06), strapM); s.position.set(0, (YTOP + PAL) / 2, z); S.add(s);
    const s2 = new THREE.Mesh(new THREE.BoxGeometry(BW + .02, .006, .06), strapM); s2.position.set(0, YTOP + .004, z); S.add(s2); }
  // the family's folder on top: its own label, and the SOLD stamp that prints on "keep"
  const fam = new THREE.Group(); fam.position.set(.08, YTOP + FT / 2, .05); fam.rotation.y = .09; S.add(fam);
  const famBox = new THREE.Mesh(new THREE.BoxGeometry(FW * 1.02, FT, FD * 1.02), [sideM, sideM, topM, sideM, sideM, sideM]); famBox.castShadow = famBox.receiveShadow = true; fam.add(famBox);
  const lab = new THREE.Mesh(new THREE.PlaneGeometry(.2, .1), M({ map: label, roughness: .8 })); lab.rotation.x = -Math.PI / 2; lab.position.set(-.02, FT / 2 + .0006, .02); fam.add(lab);
  const stamp = new THREE.Mesh(new THREE.PlaneGeometry(.17, .085), new THREE.MeshStandardMaterial({ map: stampT, transparent: true, roughness: .9, opacity: 0 }));
  stamp.rotation.set(-Math.PI / 2, 0, .22); stamp.position.set(.03, FT / 2 + .0012, .035); fam.add(stamp);
  // light: warm key (shadowed, static), cool fill, warm rim
  S.add(new THREE.HemisphereLight('#c9d0de', '#3a2f24', .28));
  const key = new THREE.SpotLight('#ffd7a3', 130, 30, .45, .55, 1.4); key.position.set(-6, 7.5, 3.5); key.target.position.set(0, YTOP * .6, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -.0004; S.add(key, key.target);
  const rim = new THREE.DirectionalLight('#9fb4d6', .5); rim.position.set(6, 4, -6); S.add(rim);
  const op = t => { const ts = events.keep ?? 1e9; return t < ts ? 0 : Math.min(1, (t - ts) / .12); };
  return { update: t => { stamp.material.opacity = op(t); }, state: t => op(t).toFixed(2), YTOP };
}
