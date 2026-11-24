// AI3D — episode Three.js director for "Is the AI Bubble Bigger Than the Dot-Com Bubble?"
// One renderer, many worlds. Each shot = {start, end, world, ...params}; draw(t) renders the shot
// covering t (or nothing — HTML scenes cover the canvas). Worlds are built lazily per shot and are
// fully deterministic (seeded RNG, time-driven, no Date/Math.random), so any frame can be seeked.
(function (g) {
  const RNG = (a) => () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = (x) => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const lerp = (a, b, t) => a + (b - a) * t;
  const win = (t, a, b) => clamp((t - a) / (b - a));
  const V3 = (a) => new THREE.Vector3(a[0], a[1], a[2]);
  let R = null, W = 1920, H = 1080, ENV = null, DOT = null;
  function dotTex() {
    if (DOT) return DOT;
    const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.35, 'rgba(255,255,255,.8)'); r.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = r; g.fillRect(0, 0, 64, 64); DOT = new THREE.CanvasTexture(c); return DOT;
  }
  const shots = [];

  function init(canvas, o) {
    W = o.width; H = o.height;
    R = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    R.setPixelRatio(1); R.setSize(W, H, false);
    R.outputColorSpace = THREE.SRGBColorSpace; R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.0;
    R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
    const pm = new THREE.PMREMGenerator(R), es = new THREE.Scene();
    es.add(new THREE.Mesh(new THREE.BoxGeometry(30, 30, 30), new THREE.MeshBasicMaterial({ color: 0x141a26, side: THREE.BackSide })));
    [[0xdfefff, -8, 8, 6, 10, 5], [0x6fd6ff, 9, 3, 3, 5, 9], [0xffd08a, 0, -8, 7, 14, 3]].forEach(([c, x, y, z, w, h]) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: c, side: THREE.DoubleSide }));
      m.position.set(x, y, z); m.lookAt(0, 0, 0); es.add(m);
    });
    ENV = pm.fromScene(es, 0.04).texture;
  }
  // keyframed camera: keys = [[t, [px,py,pz], [lx,ly,lz], fov], ...] — eased between keys, holds at ends.
  function keyCam(cam, keys, t) {
    let i = 0; while (i < keys.length - 1 && t >= keys[i + 1][0]) i++;
    const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
    const f = b === a ? 0 : ease(clamp((t - a[0]) / (b[0] - a[0])));
    cam.position.lerpVectors(V3(a[1]), V3(b[1]), f);
    const look = new THREE.Vector3().lerpVectors(V3(a[2]), V3(b[2]), f);
    if (cam.isPerspectiveCamera) { cam.fov = lerp(a[3] || 40, b[3] || 40, f); cam.updateProjectionMatrix(); }
    cam.lookAt(look); cam.updateMatrixWorld();
  }
  function add(id, o) { shots.push(Object.assign({ id }, o)); }

  // camera move: {from:[x,y,z], to:[...], look:[...], lookTo:[...], dur}
  function moveCam(cam, m, u) {
    const p = ease(clamp(u / (m.dur || 1)));
    cam.position.lerpVectors(V3(m.from), V3(m.to), p);
    const l = V3(m.look).lerp(V3(m.lookTo || m.look), p);
    cam.lookAt(l);
  }

  // ── world: data hall ────────────────────────────────────────────────
  function dataHall(s) {
    const rnd = RNG(2026), S = new THREE.Scene();
    S.background = new THREE.Color(0x040812); S.fog = new THREE.Fog(0x040812, 10, 70); S.environment = ENV;
    const cam = new THREE.PerspectiveCamera(52, W / H, .1, 200);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 160), new THREE.MeshStandardMaterial({ color: 0x0b1322, roughness: .3, metalness: .6 }));
    floor.rotation.x = -Math.PI / 2; floor.position.z = -70; S.add(floor);
    const grid = new THREE.GridHelper(160, 266, 0x16405a, 0x0d2233); grid.position.set(0, .01, -70); S.add(grid);
    // rack front texture: 1U server slots, vents and bezels (drawn once)
    const cv = document.createElement('canvas'); cv.width = 128; cv.height = 512; const c2 = cv.getContext('2d');
    c2.fillStyle = '#18202c'; c2.fillRect(0, 0, 128, 512);
    for (let u = 0; u < 20; u++) { const y = 10 + u * 24.6; c2.fillStyle = u % 5 === 4 ? '#26303e' : '#323f52'; c2.fillRect(6, y, 116, 20);
      c2.fillStyle = '#0a0e14'; for (let v = 0; v < 9; v++) c2.fillRect(14 + v * 9, y + 5, 5, 10); c2.fillStyle = '#4a5c74'; c2.fillRect(100, y + 4, 16, 12); }
    const faceTex = new THREE.CanvasTexture(cv); faceTex.colorSpace = THREE.SRGBColorSpace;
    const N = 64, D = 1.15, rackGeo = new THREE.BoxGeometry(1.0, 2.5, D);
    const bodyM = new THREE.MeshStandardMaterial({ color: 0x10161f, metalness: .8, roughness: .35 });
    const faceM = new THREE.MeshStandardMaterial({ map: faceTex, emissiveMap: faceTex, emissive: 0x1a2a3e, emissiveIntensity: .6, metalness: .4, roughness: .5 });
    const racks = [new THREE.InstancedMesh(rackGeo, [faceM, bodyM, bodyM, bodyM, bodyM, bodyM], N), new THREE.InstancedMesh(rackGeo, [bodyM, faceM, bodyM, bodyM, bodyM, bodyM], N)];  // face toward the aisle
    const LED_ROWS = 10, LED_COLS = 3, leds = new THREE.InstancedMesh(new THREE.BoxGeometry(.015, .035, .05), new THREE.MeshBasicMaterial({ color: 0xffffff }), N * 2 * LED_ROWS * LED_COLS);
    const m4 = new THREE.Matrix4(), ledZ = [], ledBase = [];
    let k = 0;
    [-1, 1].forEach((side, si) => { for (let i = 0; i < N; i++) {
      const z = -3 - i * (D + .04), x = side * 2.0;
      m4.makeTranslation(x, 1.25, z); racks[si].setMatrixAt(i, m4);
      for (let r = 0; r < LED_ROWS; r++) for (let c = 0; c < LED_COLS; c++) {
        m4.makeTranslation(x - side * .505, .25 + r * .22, z - .35 + c * .12); leds.setMatrixAt(k, m4);
        ledZ.push(z); ledBase.push(rnd() < .12 ? .15 : .35 + rnd() * .5); k++; }
    } });
    racks.forEach(r => S.add(r)); S.add(leds);
    const col = new THREE.Color();
    for (let i = 0; i < k; i++) leds.setColorAt(i, col.setRGB(0, .4, .6));
    [-1, 1].forEach(side => {
      const tray = new THREE.Mesh(new THREE.BoxGeometry(.4, .08, 160), new THREE.MeshStandardMaterial({ color: 0x6a5a3a, metalness: .7, roughness: .5 }));
      tray.position.set(side * 2.0, 3.35, -70); S.add(tray);
    });
    const panels = new THREE.InstancedMesh(new THREE.BoxGeometry(1.1, .03, .5), new THREE.MeshBasicMaterial({ color: 0xa9cff0 }), 40);
    for (let i = 0; i < 40; i++) { m4.makeTranslation(0, 3.9, -2 - i * 3); panels.setMatrixAt(i, m4); } S.add(panels);
    for (let i = 0; i < 5; i++) { const pl = new THREE.PointLight(0x9fd0ff, 18, 16, 2); pl.position.set(0, 3.4, -4 - i * 12); S.add(pl); }
    S.add(new THREE.HemisphereLight(0x6fb6ff, 0x05070c, .6));
    const key = new THREE.PointLight(0x8fd8ff, 60, 30, 2); key.position.set(0, 3.5, -6); S.add(key);
    // gold money particles and cold airflow
    const pts = (n, color, size) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
      const p = new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: dotTex(), transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending })); S.add(p); return p; };
    const GOLD = 500, gold = pts(GOLD, 0xffc766, .05), gseed = [];
    for (let i = 0; i < GOLD; i++) gseed.push([(rnd() - .5) * 3, .4 + rnd() * 2.8, rnd()]);
    const AIR = 700, air = pts(AIR, 0x6fd8ff, .06), aseed = [];
    for (let i = 0; i < AIR; i++) aseed.push([(rnd() - .5) * 2.6, rnd(), -3 - rnd() * 40, rnd()]);
    return {
      scene: S, camera: cam, update(t, u) {
        moveCam(cam, s.cam, u);
        // LED wave: a pulse running down the aisle at s.pulse (film time)
        const pz = s.pulse ? -3 - Math.max(0, t - s.pulse) * 34 : 999;
        const heat = s.thermal ? clamp((t - s.thermal) / 1.2) : 0;
        for (let i = 0; i < k; i++) {
          const b = ledBase[i] * (0.75 + .25 * Math.sin(t * 3 + i * 1.7));
          const w = s.pulse && t > s.pulse ? Math.exp(-Math.pow(ledZ[i] - pz, 2) / 6) + (t - s.pulse > .3 && ledZ[i] > pz ? .55 : 0) : 0;
          if (heat > 0) col.setRGB(lerp(0, 1, heat) * (.6 + b), lerp(.4, .35, heat) * (.6 + b), lerp(.6, .05, heat) * b);
          else col.setRGB(.1 * b + w * .6, .55 * b + w, .8 * b + w);
          leds.setColorAt(i, col);
        }
        leds.instanceColor.needsUpdate = true;
        const gp = gold.geometry.attributes.position.array, go = s.gold ? clamp((t - s.gold[0]) / .6) * clamp((s.gold[1] - t) / .6) : 0;
        gold.material.opacity = go;
        for (let i = 0; i < GOLD; i++) { const q = gseed[i], f = (q[2] + t * .35) % 1; gp[i * 3] = q[0]; gp[i * 3 + 1] = q[1]; gp[i * 3 + 2] = -5 - f * 45; }
        gold.geometry.attributes.position.needsUpdate = true;
        air.material.opacity = heat * .8;
        const ap = air.geometry.attributes.position.array;
        for (let i = 0; i < AIR; i++) { const q = aseed[i], f = (q[3] + t * .6) % 1; ap[i * 3] = q[0] * (1 - f * .3); ap[i * 3 + 1] = f * 3.2; ap[i * 3 + 2] = q[2]; }
        air.geometry.attributes.position.needsUpdate = true;
      }
    };
  }

  // ── world: hyperscale campus at dusk ────────────────────────────────
  function campus(s) {
    const rnd = RNG(7), S = new THREE.Scene();
    S.background = new THREE.Color(0x1a2138); S.fog = new THREE.Fog(0x9a6a68, 220, 1300); S.environment = ENV;
    const cam = new THREE.PerspectiveCamera(40, W / H, .5, 4000);
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), new THREE.MeshStandardMaterial({ color: 0x45404a, roughness: .95 }));
    ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; S.add(ground);
    const sky = new THREE.Mesh(new THREE.SphereGeometry(2600, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false,
      uniforms: {}, vertexShader: 'varying vec3 v;void main(){v=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
      fragmentShader: 'varying vec3 v;void main(){float h=clamp(v.y*2.5,0.,1.);vec3 c=mix(vec3(.98,.55,.32),vec3(.07,.10,.22),pow(h,.6));gl_FragColor=vec4(c,1.);}' }));
    S.add(sky);
    const hallMat = new THREE.MeshStandardMaterial({ color: 0xd9dde4, roughness: .6, metalness: .2 });
    const halls = [];
    // site roads
    for (let r = 0; r < 3; r++) { const road = new THREE.Mesh(new THREE.BoxGeometry(220, .1, 6), new THREE.MeshStandardMaterial({ color: 0x6a6672, roughness: .9 })); road.position.set(0, .05, 22 - r * 32); S.add(road); }
    for (let i = 0; i < 8; i++) {
      const g = new THREE.Group(), body = new THREE.Mesh(new THREE.BoxGeometry(44, 9, 18), hallMat);
      body.position.y = 4.5; body.castShadow = true; body.receiveShadow = true; g.add(body);
      for (let j = 0; j < 10; j++) { const c = new THREE.Mesh(new THREE.BoxGeometry(3, 1.4, 3), new THREE.MeshStandardMaterial({ color: 0x8a95a6, metalness: .6, roughness: .4 })); c.position.set(-18 + j * 4, 9.7, 0); g.add(c); }
      const strip = new THREE.Mesh(new THREE.BoxGeometry(44.2, .3, .2), new THREE.MeshBasicMaterial({ color: 0x5fe0ff })); strip.position.set(0, 2.2, 9.05); g.add(strip);
      g.position.set((i % 4) * 52 - 78, 0, Math.floor(i / 4) * -32 + 6); S.add(g); halls.push(g);
    }
    const cranes = [];
    for (let i = 0; i < 3; i++) {
      const g = new THREE.Group(), m = new THREE.MeshStandardMaterial({ color: 0xf2b134, roughness: .6 });
      const mast = new THREE.Mesh(new THREE.BoxGeometry(1.2, 34, 1.2), m); mast.position.y = 17; g.add(mast);
      const jib = new THREE.Mesh(new THREE.BoxGeometry(30, 1, 1), m); jib.position.set(9, 33.5, 0); g.add(jib);
      const cw = new THREE.Mesh(new THREE.BoxGeometry(4, 2.5, 2), new THREE.MeshStandardMaterial({ color: 0x555b66 })); cw.position.set(-6, 32.5, 0); g.add(cw);
      const bea = new THREE.Mesh(new THREE.SphereGeometry(.5, 12, 8), new THREE.MeshBasicMaterial({ color: 0xff3b2a })); bea.position.set(0, 35, 0); g.add(bea);
      g.position.set(-40 + i * 50, 0, -62); S.add(g); cranes.push(g);
    }
    // substation + transmission line with energy pulses
    const sub = new THREE.Group();
    for (let i = 0; i < 6; i++) { const tr = new THREE.Mesh(new THREE.BoxGeometry(3, 4, 3), new THREE.MeshStandardMaterial({ color: 0x6b7484, metalness: .5, roughness: .5 })); tr.position.set((i % 3) * 5, 2, Math.floor(i / 3) * 5); sub.add(tr); }
    sub.position.set(70, 0, 25); S.add(sub);
    const pylonPos = []; for (let i = 0; i < 7; i++) pylonPos.push(new THREE.Vector3(80 + i * 40, 0, 30 - i * 35));
    const pm = new THREE.MeshStandardMaterial({ color: 0x9aa3b2, metalness: .7, roughness: .4 });
    pylonPos.forEach((p) => { const g = new THREE.Group(); const m = new THREE.Mesh(new THREE.CylinderGeometry(.4, 1.6, 26, 4), pm); m.position.y = 13; g.add(m);
      const arm = new THREE.Mesh(new THREE.BoxGeometry(12, .5, .5), pm); arm.position.y = 24; g.add(arm); g.position.copy(p); S.add(g); });
    const lines = [], pulses = [];
    for (let w = -1; w <= 1; w += 2) {
      const pts = [];
      for (let i = 0; i < pylonPos.length - 1; i++) { const a = pylonPos[i], b = pylonPos[i + 1];
        for (let j = 0; j < 10; j++) { const f = j / 10; pts.push(new THREE.Vector3(lerp(a.x, b.x, f) + w * 5.5, 24 - Math.sin(f * Math.PI) * 3, lerp(a.z, b.z, f))); } }
      pts.reverse(); pts.push(new THREE.Vector3(72 + w * 3, 6, 27));
      const curve = new THREE.CatmullRomCurve3(pts); lines.push(curve);
      S.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 200, .12, 6, false), new THREE.MeshBasicMaterial({ color: 0x5f7fa0 })));
      for (let q = 0; q < 6; q++) { const p = new THREE.Mesh(new THREE.SphereGeometry(.7, 12, 8), new THREE.MeshBasicMaterial({ color: 0x9ff3ff })); S.add(p); pulses.push([p, curve, q / 6]); }
    }
    const GP = 900, gseed = [];
    const gg = new THREE.BufferGeometry(); gg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(GP * 3), 3));
    const goldPts = new THREE.Points(gg, new THREE.PointsMaterial({ color: 0xffc766, size: 1.6, map: dotTex(), transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending })); S.add(goldPts);
    for (let i = 0; i < GP; i++) gseed.push([(rnd() - .5) * 200, 0, (rnd() - .5) * 70 - 10, rnd()]);
    S.add(new THREE.HemisphereLight(0xffc9a0, 0x30303a, 1.1));
    const sun = new THREE.DirectionalLight(0xffb27a, 2.2); sun.position.set(-120, 60, 80); sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -150, right: 150, top: 150, bottom: -150, far: 500 }); S.add(sun);
    return {
      scene: S, camera: cam, update(t, u) {
        moveCam(cam, s.cam, u);
        const build = s.build ? clamp((t - s.build[0]) / (s.build[1] - s.build[0])) : 1;
        halls.forEach((h, i) => { const f = ease(clamp(build * 1.8 - i * .1)); h.scale.set(1, Math.max(.02, f), 1); });
        const inv = s.invest ? clamp((t - s.invest[0]) / .6) * clamp((s.invest[1] - t) / .6) : 0; goldPts.material.opacity = inv;
        const gp = goldPts.geometry.attributes.position.array;
        for (let i = 0; i < GP; i++) { const q = gseed[i], f = (q[3] + t * .35) % 1; gp[i * 3] = q[0]; gp[i * 3 + 1] = 90 * (1 - f) + 2; gp[i * 3 + 2] = q[2]; }
        goldPts.geometry.attributes.position.needsUpdate = true;
        cranes.forEach((c, i) => c.rotation.y = Math.sin(t * .25 + i * 2) * .6);
        const on = s.power ? clamp((t - s.power) / .8) : 0;
        pulses.forEach(([p, c, ph]) => { p.visible = on > 0; p.position.copy(c.getPointAt((ph + t * .18) % 1)); p.scale.setScalar(.5 + on * .7); });
      }
    };
  }

  // ── world: AI accelerator chip ─────────────────────────────────────
  function chip(s) {
    const rnd = RNG(11), S = new THREE.Scene();
    S.background = new THREE.Color(0x03060c); S.environment = ENV;
    const cam = new THREE.PerspectiveCamera(34, W / H, .1, 100);
    const cv = document.createElement('canvas'); cv.width = cv.height = 512; const c2 = cv.getContext('2d');
    c2.fillStyle = '#0a1420'; c2.fillRect(0, 0, 512, 512);
    for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) {
      c2.fillStyle = `rgba(${40 + rnd() * 30},${140 + rnd() * 60},${200 + rnd() * 55},${.35 + rnd() * .4})`;
      c2.fillRect(14 + x * 61, 14 + y * 61, 52, 52);
      c2.strokeStyle = 'rgba(120,220,255,.5)'; c2.strokeRect(14 + x * 61, 14 + y * 61, 52, 52);
    }
    const dieTex = new THREE.CanvasTexture(cv); dieTex.colorSpace = THREE.SRGBColorSpace;
    const G = new THREE.Group(); S.add(G);
    const sub = new THREE.Mesh(new THREE.BoxGeometry(6, .22, 6), new THREE.MeshStandardMaterial({ color: 0x23402e, roughness: .6 })); G.add(sub);
    const pads = new THREE.InstancedMesh(new THREE.BoxGeometry(.12, .02, .3), new THREE.MeshStandardMaterial({ color: 0xd4a24c, metalness: 1, roughness: .25 }), 64);
    const m4 = new THREE.Matrix4(); for (let i = 0; i < 64; i++) { const side = i % 4, j = Math.floor(i / 4); const o = -2.6 + j * .35;
      m4.makeRotationY(side % 2 ? Math.PI / 2 : 0); m4.setPosition(side === 0 ? o : side === 2 ? o : (side === 1 ? 2.75 : -2.75), .12, side === 0 ? 2.75 : side === 2 ? -2.75 : o); pads.setMatrixAt(i, m4); }
    G.add(pads);
    const inter = new THREE.Mesh(new THREE.BoxGeometry(4.3, .12, 4.3), new THREE.MeshStandardMaterial({ color: 0x5a6270, metalness: .7, roughness: .35 })); inter.position.y = .17; G.add(inter);
    const die = new THREE.Mesh(new THREE.BoxGeometry(2.3, .1, 2.3), [0, 1, 2, 3, 4, 5].map(i => i === 2 ? new THREE.MeshStandardMaterial({ map: dieTex, emissiveMap: dieTex, emissive: 0x66ccff, emissiveIntensity: .6, metalness: .3, roughness: .3 }) : new THREE.MeshStandardMaterial({ color: 0x15202e })));
    die.position.y = .28; G.add(die);
    const hbm = [];
    [[-1.65, 0], [1.65, 0], [-1.65, 1.2], [1.65, 1.2], [-1.65, -1.2], [1.65, -1.2]].forEach(([x, z]) => {
      const st = new THREE.Group();
      for (let l = 0; l < 8; l++) { const m = new THREE.Mesh(new THREE.BoxGeometry(.8, .055, 1.0), new THREE.MeshStandardMaterial({ color: l % 2 ? 0x9aa4b4 : 0x2a313c, metalness: .8, roughness: .3 })); m.position.y = l * .06; st.add(m); }
      st.position.set(x, .26, z * .9); G.add(st); hbm.push(st);
    });
    const lid = new THREE.Mesh(new THREE.BoxGeometry(4.6, .14, 4.6), new THREE.MeshStandardMaterial({ color: 0xc9ced6, metalness: 1, roughness: .22 })); lid.position.y = .75; G.add(lid);
    const streaks = []; for (let i = 0; i < 14; i++) { const m = new THREE.Mesh(new THREE.BoxGeometry(.5, .01, .02), new THREE.MeshBasicMaterial({ color: 0x9ff3ff, transparent: true, opacity: .9 })); G.add(m); streaks.push([m, rnd(), rnd() * 2.2 - 1.1, rnd() < .5]); }
    S.add(new THREE.HemisphereLight(0x8fbfff, 0x05070c, .5));
    const k1 = new THREE.DirectionalLight(0xffffff, 2.2); k1.position.set(4, 6, 3); S.add(k1);
    const rim = new THREE.PointLight(0x38d6ff, 40, 20, 2); rim.position.set(-4, 2, -4); S.add(rim);
    const warm = new THREE.PointLight(0xffb066, 20, 20, 2); warm.position.set(5, 1, -2); S.add(warm);
    // batch mode (opening, "selling advanced processors"): finished packaged chips ride a lit conveyor into
    // shipping trays — a different action and scale from the single exploded chip used in Chapter 4.
    const line = [];
    if (s.batch) {
      const belt = new THREE.Mesh(new THREE.BoxGeometry(60, .1, 2.2), new THREE.MeshStandardMaterial({ color: 0x1a2230, metalness: .6, roughness: .4 })); belt.position.set(0, -.12, 0); S.add(belt);
      for (let r = 0; r < 30; r++) { const roll = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, 2.3, 10), new THREE.MeshStandardMaterial({ color: 0x8a95a6, metalness: .9, roughness: .25 })); roll.rotation.x = Math.PI / 2; roll.position.set(-30 + r * 2, -.2, 0); S.add(roll); }
      const rail = new THREE.Mesh(new THREE.BoxGeometry(60, .05, .05), new THREE.MeshBasicMaterial({ color: 0x38d6ff })); rail.position.set(0, -.04, 1.12); S.add(rail);
      const tray = new THREE.Group(); tray.position.set(0, -.1, -3.2); S.add(tray);
      const trayM = new THREE.MeshStandardMaterial({ color: 0x101820, metalness: .3, roughness: .6 });
      const tb = new THREE.Mesh(new THREE.BoxGeometry(12, .1, 2.6), trayM); tray.add(tb);
      for (let i = 0; i < 14; i++) { const c = G.clone(); c.scale.setScalar(.27); line.push(c); S.add(c); }
      for (let i = 0; i < 10; i++) { const c = G.clone(); c.scale.setScalar(.27); c.position.set(-5 + (i % 5) * 2.5, .02, -3.2 + (i < 5 ? -.6 : .6)); S.add(c); }
      G.visible = false;
    }
    return {
      scene: S, camera: cam, update(t, u) {
        moveCam(cam, s.cam, u);
        G.rotation.y = s.spin ? u * s.spin : 0;
        line.forEach((c, i) => { c.position.set(((i * 2.1 + t * 1.6) % 29.4) - 14.7, 0, 0); });
        const ex = s.explode ? ease(win(t, s.explode[0], s.explode[1])) : 0;
        lid.position.y = .75 + ex * 2.2; lid.material.opacity = 1;
        die.position.y = .28 + ex * .6; hbm.forEach((h, i) => h.position.y = .26 + ex * (.9 + (i % 2) * .15));
        const glow = s.glow ? clamp((t - s.glow) / .6) : 0;
        die.material[2].emissiveIntensity = .4 + glow * 1.4;
        streaks.forEach(([m, ph, off, axis]) => { const f = ((ph + t * .9) % 1) * 2.6 - 1.3; m.visible = glow > 0;
          if (axis) { m.position.set(f, die.position.y + .06, off); m.rotation.y = 0; } else { m.position.set(off, die.position.y + .06, f); m.rotation.y = Math.PI / 2; } });
      }
    };
  }


  // ── world: one server rack, macro — sled slides out, GPU boards, fans spin, liquid cooling flows ──
  function serverRack(s) {
    const rnd = RNG(77), S = new THREE.Scene();
    S.background = new THREE.Color(0x03060d); S.fog = new THREE.Fog(0x03060d, 6, 22); S.environment = ENV;
    const cam = new THREE.PerspectiveCamera(42, W / H, .05, 100);
    const M = (c, m = .7, r = .35, e) => new THREE.MeshStandardMaterial({ color: c, metalness: m, roughness: r, emissive: e || 0 });
    const B = (p, w, h, d, m, x, y, z) => { const o = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; p.add(o); return o; };
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), M(0x0a0f18, .6, .25)); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; S.add(floor);
    // neighbouring racks recede into darkness (out of focus context, not the subject)
    for (let i = -4; i <= 4; i++) if (i) { const r = B(S, 1.0, 2.4, 1.2, M(0x0d131d, .8, .4), i * 1.08, 1.2, 0);
      for (let k = 0; k < 10; k++) { const led = new THREE.Mesh(new THREE.BoxGeometry(.03, .03, .01), new THREE.MeshBasicMaterial({ color: rnd() < .8 ? 0x38d6ff : 0x6dff9b })); led.position.set(i * 1.08 + .35, .3 + k * .2, .61); S.add(led); } }
    // the hero rack: frame + 8 sleds
    const rack = new THREE.Group(); S.add(rack);
    const fm = M(0x1a2230, .85, .3);
    B(rack, .06, 2.4, 1.2, fm, -.5, 1.2, 0); B(rack, .06, 2.4, 1.2, fm, .5, 1.2, 0); B(rack, 1.06, .06, 1.2, fm, 0, 2.4, 0);
    const sleds = [], fans = [], pipes = [];
    const fanGeo = new THREE.CylinderGeometry(.075, .075, .02, 7), hub = new THREE.CylinderGeometry(.02, .02, .03, 8);
    const coolM = new THREE.MeshStandardMaterial({ color: 0x2a9bd6, emissive: 0x0d5d8c, emissiveIntensity: .4, metalness: .2, roughness: .2 });
    for (let k = 0; k < 8; k++) {
      const g = new THREE.Group(); g.position.set(0, .35 + k * .25, 0); rack.add(g); sleds.push(g);
      B(g, .92, .2, 1.1, M(0x2a3444, .8, .35), 0, 0, 0);
      const front = B(g, .92, .2, .02, M(0x323f52, .8, .3), 0, 0, .56);
      for (let v = 0; v < 6; v++) B(g, .06, .12, .005, M(0x0a0e14, .2, .8), -.36 + v * .1, 0, .572);
      const led = new THREE.Mesh(new THREE.BoxGeometry(.04, .04, .01), new THREE.MeshBasicMaterial({ color: 0x38d6ff })); led.position.set(.38, .05, .575); g.add(led);
      if (k === 4) { // hero sled interior: GPU packages under finned cold plates, supply/return coolant lines
        const tray = new THREE.Group(); tray.position.y = .11; g.add(tray);
        B(tray, .86, .01, 1.0, M(0x0f5132, .1, .6), 0, 0, 0);  // PCB
        g.userData.tray = tray;
      }
    }
    const tray = sleds[4].userData.tray, GX = [-.3, -.1, .1, .3], GZ = .1;
    // thermal map painted onto the board: heat spreads from each GPU; coolant pulls it back down
    const hc = document.createElement('canvas'); hc.width = 112; hc.height = 128; const hx = hc.getContext('2d'), himg = hx.createImageData(112, 128);
    const htex = new THREE.CanvasTexture(hc); htex.colorSpace = THREE.SRGBColorSpace;
    const hplane = new THREE.Mesh(new THREE.PlaneGeometry(.86, 1.0), new THREE.MeshBasicMaterial({ map: htex, transparent: true, opacity: 0, depthWrite: false }));
    hplane.rotation.x = -Math.PI / 2; hplane.position.y = .007; tray.add(hplane);
    const CMAP = [[20, 50, 140], [30, 160, 220], [250, 220, 60], [250, 130, 30], [220, 40, 30]];
    const cmap = (v) => { v = clamp(v) * 4; const i = Math.min(3, Math.floor(v)), f = v - i, a = CMAP[i], b = CMAP[i + 1]; return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f]; };
    function paintHeat(level) {
      const d = himg.data;
      for (let y = 0; y < 128; y++) for (let x = 0; x < 112; x++) {
        const px = x / 112 * .86 - .43, pz = y / 128 * 1.0 - .5; let h = 0;
        for (let j = 0; j < 4; j++) { const dx = px - GX[j], dz = pz - GZ; h += Math.exp(-(dx * dx + dz * dz) / .012); }
        const c = cmap(h * level), i = (y * 112 + x) * 4; d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = 170 + 80 * clamp(h);
      }
      hx.putImageData(himg, 0, 0); htex.needsUpdate = true;
    }
    const copper = M(0xc9824a, .3, .95), nickel = M(0xc8ccd4, .25, .95);
    for (let j = 0; j < 4; j++) {
      const x = GX[j]; B(tray, .14, .02, .2, M(0x1b1f27, .6, .4), x, .015, GZ);                       // GPU package
      for (let h = 0; h < 6; h++) B(tray, .02, .015, .04, M(0x222833, .3, .5), x - .06 + (h % 3) * .06, .012, GZ + (h < 3 ? -.13 : .13)); // HBM / VRM
      B(tray, .15, .022, .19, copper, x, .036, GZ);                                                       // cold plate base
      for (let f = 0; f < 7; f++) B(tray, .012, .022, .17, nickel, x - .06 + f * .02, .058, GZ);         // internal fins (cutaway top)
      [-.04, .04].forEach((dx, n) => { const c = new THREE.Mesh(new THREE.CylinderGeometry(.012, .012, .04, 10), n ? M(0xd06a2a, .4, .5) : M(0x2a7ad6, .4, .5)); c.position.set(x + dx, .07, GZ + .1); tray.add(c); });
    }
    for (let j = 0; j < 5; j++) { const f = new THREE.Group(); f.position.set(-.34 + j * .17, .07, -.42); tray.add(f);
      const blade = new THREE.Mesh(fanGeo, M(0x151a22, .4, .5)); blade.rotation.x = Math.PI / 2; f.add(blade);
      for (let b = 0; b < 5; b++) { const bl = B(f, .015, .06, .005, M(0x5b6678, .5, .4), 0, 0, .012); bl.rotation.z = b * 1.2566; bl.position.set(Math.sin(b * 1.2566) * .03, Math.cos(b * 1.2566) * .03, .012); }
      fans.push(f); }
    // supply (cold) and return (warm) lines: manifold → every cold plate → manifold → out of the sled to the rack loop
    const lineMat = (c) => new THREE.MeshStandardMaterial({ color: c, transparent: true, opacity: .45, roughness: .1, metalness: .1 });
    const supply = new THREE.CatmullRomCurve3([[-.5, .05, .52], [-.42, .08, .26], [-.3, .08, .23], [.3, .08, .23], [.36, .08, .23]].map(V3));
    const ret = new THREE.CatmullRomCurve3([[-.36, .095, .27], [.3, .095, .27], [.42, .095, .3], [.5, .06, .52]].map(V3));
    tray.add(new THREE.Mesh(new THREE.TubeGeometry(supply, 60, .014, 10, false), lineMat(0x4aa8ff)));
    tray.add(new THREE.Mesh(new THREE.TubeGeometry(ret, 60, .014, 10, false), lineMat(0xff9a5a)));
    GX.forEach(x => { [[-.04, .23, 0x4aa8ff], [.04, .27, 0xff9a5a]].forEach(([dx, z, c]) => {
      const h = new THREE.CatmullRomCurve3([[x + dx, .08, z], [x + dx, .09, GZ + .16], [x + dx, .07, GZ + .11]].map(V3));
      tray.add(new THREE.Mesh(new THREE.TubeGeometry(h, 12, .009, 8, false), lineMat(c))); }); });
    // rack-level loop: blue supply riser and orange return riser on the rack posts
    const riserS = B(S, .05, 2.3, .05, M(0x2a7ad6, .3, .6), -.53, 1.2, .55), riserR = B(S, .05, 2.3, .05, M(0xd06a2a, .3, .6), .53, 1.2, .55);
    const NT = 40, tokS = new THREE.InstancedMesh(new THREE.SphereGeometry(.0085, 8, 6), new THREE.MeshBasicMaterial({ color: 0x9fd8ff }), NT); tray.add(tokS);
    const tokR = new THREE.InstancedMesh(new THREE.SphereGeometry(.0085, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffb070 }), NT); tray.add(tokR);
    const warmLight = new THREE.PointLight(0xff6a3a, 0, 1.2); warmLight.position.set(0, .3, GZ); tray.add(warmLight);
    // lighting: cool overhead, warm rim, a soft key from the aisle
    S.add(new THREE.HemisphereLight(0x8fb4ff, 0x101622, .8));
    const key = new THREE.SpotLight(0xdfefff, 45, 14, .6, .6); key.position.set(2.2, 3.2, 3.2); key.target.position.set(0, 1.4, 0); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); S.add(key, key.target);
    const rim = new THREE.PointLight(0x38d6ff, 6, 5); rim.position.set(-1.2, 1.6, 1.4); S.add(rim);
    const warm = new THREE.PointLight(0xff7a3d, 0, 2.5); warm.position.set(0, 1.6, .4); S.add(warm);
    const m4 = new THREE.Matrix4(), v = new THREE.Vector3();
    return {
      scene: S, camera: cam, update(t, u) {
        if (s.keys) keyCam(cam, s.keys, t); else moveCam(cam, s.cam, u);
        // the hero sled slides out on s.slide = [start, end]
        const so = s.slide ? ease(clamp((t - s.slide[0]) / (s.slide[1] - s.slide[0]))) : 1; sleds[4].position.z = so * .75;
        fans.forEach((f, i) => { f.rotation.z = t * (22 + i * 1.7); });
        // thermal: servers working (s.run) heat the GPUs; coolant (s.cool) carries the heat away
        const run = s.run ? clamp((t - s.run) / (s.peak - s.run)) : 0, cl = s.cool ? clamp((t - s.cool) / 2.2) : 0;
        const level = .95 * Math.pow(run, .8) * (1 - .72 * ease(cl));
        hplane.material.opacity = Math.min(1, run * 3);
        if (run > 0) paintHeat(level);
        warmLight.intensity = 2.5 * level;
        const flow = clamp((t - (s.cool || 1e9)) / .4);
        for (let j = 0; j < NT; j++) { const f = (j / NT + t * .35) % 1;
          supply.getPointAt(f, v); m4.makeScale(flow, flow, flow); m4.setPosition(v); tokS.setMatrixAt(j, m4);
          ret.getPointAt(f, v); m4.makeScale(flow, flow, flow); m4.setPosition(v); tokR.setMatrixAt(j, m4); }
        tokS.instanceMatrix.needsUpdate = true; tokR.instanceMatrix.needsUpdate = true;
        tokR.material.color.setRGB(1, .45 + .4 * (1 - level), .25 + .5 * (1 - level));
      }
    };
  }

  // ── world: isometric money-flow diorama ─────────────────────────────
  function diorama(s) {
    const rnd = RNG(5), S = new THREE.Scene();
    S.background = new THREE.Color(0x070d1c); S.environment = ENV;
    const asp = W / H, Z = 11;
    const cam = s.keys ? new THREE.PerspectiveCamera(40, asp, .1, 400) : new THREE.OrthographicCamera(-Z * asp, Z * asp, Z, -Z, -100, 200);
    const plate = new THREE.Mesh(new THREE.BoxGeometry(26, .6, 16), new THREE.MeshStandardMaterial({ color: 0x0f1a2e, metalness: .3, roughness: .7 }));
    plate.position.y = -.3; plate.receiveShadow = true; S.add(plate);
    const grid = new THREE.GridHelper(26, 26, 0x1f3a5c, 0x13253d); grid.position.y = .01; grid.scale.z = 16 / 26; S.add(grid);
    const mat = (c, e) => new THREE.MeshStandardMaterial({ color: c, roughness: .55, metalness: .25, emissive: e || 0x000000 });
    const node = (x, z) => { const g = new THREE.Group(); g.position.set(x, 0, z); S.add(g); return g; };
    const P = { fab: [-9, -3], cloud: [-3, 3], lab: [3.5, -2.5], cust: [9, 3] };
    const fab = node(...P.fab), cloud = node(...P.cloud), lab = node(...P.lab), cust = node(...P.cust);
    const box = (g, w, h, d, c, x = 0, y = 0, z = 0, e) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(c, e)); m.position.set(x, y + h / 2, z); m.castShadow = true; m.receiveShadow = true; g.add(m); return m; };
    // chip fab: long cleanroom with saw-tooth roof and stacks
    box(fab, 4.6, 1.6, 3, 0xd7dbe3); for (let i = 0; i < 4; i++) { const r = box(fab, 1.1, .6, 3, 0x9aa8bc, -1.7 + i * 1.15, 1.6); r.rotation.z = .35; }
    box(fab, .4, 2.6, .4, 0x6b7484, 1.8, 0, -1); box(fab, .4, 2.2, .4, 0x6b7484, 1.2, 0, -1);
    const fabExt = box(fab, 2.4, 1.2, 2.6, 0xc7ccd6, -3.6, 0, 0);
    // facade detail (procedural textures): cleanroom panels + window band; louvred data-centre walls; lab floor plates
    const fabTex = canvasTex(512, 128, (g, w, h) => { g.fillStyle = '#d7dbe3'; g.fillRect(0, 0, w, h); for (let x = 0; x < w; x += 24) { g.fillStyle = x % 48 ? '#cdd2db' : '#e1e5ec'; g.fillRect(x, 0, 24, h); }
      g.fillStyle = '#5a7aa8'; g.fillRect(0, 30, w, 18); g.fillStyle = '#9ab8e0'; for (let x = 4; x < w; x += 24) g.fillRect(x, 32, 16, 14); g.fillStyle = '#8a92a0'; for (let k = 0; k < 3; k++) g.fillRect(60 + k * 170, 80, 60, 48); });
    const dcTex = canvasTex(512, 128, (g, w, h) => { g.fillStyle = '#3a4458'; g.fillRect(0, 0, w, h); g.fillStyle = '#2a3242'; for (let x = 0; x < w; x += 4) g.fillRect(x, 10, 2, 60);
      g.fillStyle = '#38d6ff'; g.fillRect(0, 84, w, 5); g.fillStyle = '#4a5468'; for (let k = 0; k < 4; k++) g.fillRect(30 + k * 130, 96, 70, 32); });
    fab.children[0].material = new THREE.MeshStandardMaterial({ map: fabTex, roughness: .55, metalness: .25 });
    fabTex.wrapS = THREE.RepeatWrapping;
    cloud.children.forEach(c => { if (c.geometry && c.geometry.parameters && c.geometry.parameters.width === 5) c.material = new THREE.MeshStandardMaterial({ map: dcTex, roughness: .5, metalness: .4 }); });
    // cloud: data centre with rooftop fans
    box(cloud, 5, 1.4, 3.2, 0x3a4458); for (let i = 0; i < 5; i++) box(cloud, .7, .3, .7, 0x7a8698, -1.9 + i * .95, 1.4, 0);
    box(cloud, 5.02, .12, .05, 0x38d6ff, 0, .5, 1.62, 0x38d6ff);
    const cloudExt = box(cloud, 5, 1.4, 2.2, 0x3a4458, 0, 0, -2.9);
    // AI lab: glass tower with glowing core
    const glass = new THREE.Mesh(new THREE.BoxGeometry(2.6, 3.4, 2.6), new THREE.MeshStandardMaterial({ color: 0x6fb6ff, transparent: true, opacity: .35, metalness: .9, roughness: .05 }));
    glass.position.y = 1.7; lab.add(glass);
    const core = new THREE.Mesh(new THREE.IcosahedronGeometry(.8, 1), new THREE.MeshStandardMaterial({ color: 0x38d6ff, emissive: 0x38d6ff, emissiveIntensity: 1.2 }));
    core.position.y = 1.7; lab.add(core);
    // customers: homes and offices that multiply with demand
    const homes = [];
    for (let i = 0; i < 12; i++) { const g = new THREE.Group(), w = .9 + rnd() * .6, h = .7 + rnd() * 1.8;
      const b = box(g, w, h, w, [0xe9dcc0, 0xc9d6e8, 0xf2c66d, 0xb9c7d8][i % 4]); const win = box(g, w * .7, .12, .02, 0xffe3a3, 0, h * .6, w / 2 + .01, 0xffc766);
      g.position.set((i % 4) * 1.5 - 2.2 + (rnd() - .5) * .3, 0, Math.floor(i / 4) * 1.6 - 1.6); cust.add(g); homes.push(g); }
    // links: product forward (cyan), money backward (gold)
    const arc = (a, b, hgt = 2.2) => new THREE.QuadraticBezierCurve3(new THREE.Vector3(a[0], .4, a[1]), new THREE.Vector3((a[0] + b[0]) / 2, hgt, (a[1] + b[1]) / 2), new THREE.Vector3(b[0], .4, b[1]));
    const links = [arc(P.fab, P.cloud), arc(P.cloud, P.lab), arc(P.lab, P.cust)];
    const loopInvest = arc(P.fab, P.lab, 5.2);
    const tubes = links.map(c => { const m = new THREE.Mesh(new THREE.TubeGeometry(c, 60, .05, 6, false), new THREE.MeshBasicMaterial({ color: 0x2a6c8c, transparent: true, opacity: 0 })); S.add(m); return m; });
    const investTube = new THREE.Mesh(new THREE.TubeGeometry(loopInvest, 80, .08, 6, false), new THREE.MeshBasicMaterial({ color: 0xffc766, transparent: true, opacity: 0 })); S.add(investTube);
    const dots = (n, color, r) => { const m = new THREE.InstancedMesh(new THREE.SphereGeometry(r, 10, 8), new THREE.MeshBasicMaterial({ color }), n); S.add(m); return m; };
    const chipTok = (n) => { const m = new THREE.InstancedMesh(new THREE.BoxGeometry(.36, .09, .36), new THREE.MeshStandardMaterial({ color: 0x7fe9ff, emissive: 0x1f8fb0, emissiveIntensity: .9, metalness: .6, roughness: .3 }), n); S.add(m); return m; };
    // platform ghost footprints shown while the narrator introduces the economy
    const rings = {}; for (const k in P) { const r = new THREE.Mesh(new THREE.RingGeometry(2.4, 2.6, 48), new THREE.MeshBasicMaterial({ color: 0x38d6ff, transparent: true, opacity: 0, side: THREE.DoubleSide }));
      r.rotation.x = -Math.PI / 2; r.position.set(P[k][0], .03, P[k][1]); S.add(r); rings[k] = r; }
    // fab output conveyor: chips leave the fab along a belt
    const belt = new THREE.Mesh(new THREE.BoxGeometry(3.2, .08, .6), mat(0x2a3446)); belt.position.set(P.fab[0] + 3.4, .05, P.fab[1] + .9); S.add(belt);
    const beltChips = chipTok(8);
    const PER = 14, prod = chipTok(PER * 3), money = dots(PER * 3, 0xffc766, .15);
    const packet = new THREE.Mesh(new THREE.BoxGeometry(.9, .5, .6), new THREE.MeshStandardMaterial({ color: 0xffc766, emissive: 0xb07a10, emissiveIntensity: .8, metalness: .6, roughness: .3 })); S.add(packet);
    S.add(new THREE.HemisphereLight(0x9fc4ff, 0x0a0d14, .8));
    const sun = new THREE.DirectionalLight(0xffffff, 2.0); sun.position.set(-10, 18, 12); sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16 }); S.add(sun);
    const nodes = { fab, cloud, lab, cust };
    const v = new THREE.Vector3();
    const ANCH = { top: 'translate(-50%,-100%)', left: 'translate(-100%,-50%) translate(-40px,0)', right: 'translate(40px,-50%)', bottom: 'translate(-50%,30px)' };
    function label(id, obj, dy, a) { const el = document.getElementById(id); if (!el) return; v.copy(obj.position); v.y += dy; v.project(cam);
      el.style.transform = `translate(${(v.x * .5 + .5) * 1920}px, ${(-v.y * .5 + .5) * 1080}px) ${ANCH[a || 'top']}`; }
    const m4 = new THREE.Matrix4();
    return {
      scene: S, camera: cam, update(t, u) {
        if (s.keys) keyCam(cam, s.keys, t);
        else {
          const a = s.orbit ? s.orbit[0] + (s.orbit[1] - s.orbit[0]) * clamp(u / s.dur) : .78;
          cam.position.set(Math.sin(a) * 30 + .5, 22, Math.cos(a) * 30 + 1); cam.lookAt(.5, -.5, 1);
          const zoom = s.zoom ? lerp(s.zoom[0], s.zoom[1], ease(clamp(u / s.dur))) : 1; cam.zoom = zoom; cam.updateProjectionMatrix();
          cam.updateMatrixWorld(); // labels are projected before render: matrices must be current for cold seeks
        }
        // platform assembles as the economy is introduced (s.platform = time of "imagine")
        const pf = s.platform !== undefined ? ease(clamp((t - s.platform) / 1.2)) : 1;
        plate.scale.set(Math.max(.01, pf), 1, Math.max(.01, pf)); grid.scale.set(Math.max(.01, pf), 1, Math.max(.01, pf) * 16 / 26); plate.visible = grid.visible = pf > .01;
        for (const k in rings) { const on = s.ghost !== undefined ? clamp((t - s.ghost - Object.keys(P).indexOf(k) * .25) / .4) : 0;
          const off = s.rise ? clamp((t - s.rise[k]) / .6) : 1; rings[k].material.opacity = .8 * on * (1 - off) * (.75 + .25 * Math.sin(t * 5 + k.length)); }
        const fr = s.rise ? clamp((t - s.rise.fab - .6) / .5) : 1; belt.visible = fr > 0;
        for (let j = 0; j < 8; j++) { const f = (j / 8 + t * .3) % 1; m4.makeScale(fr, fr, fr); m4.setPosition(P.fab[0] + 1.9 + f * 3, .18, P.fab[1] + .9); beltChips.setMatrixAt(j, m4); }
        beltChips.instanceMatrix.needsUpdate = true;
        // build-in of nodes (s.rise = {fab:t, cloud:t, lab:t, cust:t})
        for (const k in nodes) { const f = s.rise ? ease(clamp((t - s.rise[k]) / .7)) : 1; nodes[k].scale.set(1, Math.max(.01, f), 1); nodes[k].visible = f > .01; }
        // demand growth (s.grow = {cust, fab, cloud, lab})
        const gr = (k) => s.grow ? ease(clamp((t - s.grow[k]) / .8)) : 0;
        homes.forEach((h, i) => { const base = i < 6 ? 1 : gr('cust') * clamp(1.2 - (i - 6) * .1); h.scale.setScalar(Math.max(.001, base)); });
        fabExt.scale.set(1, Math.max(.01, gr('fab')), 1); cloudExt.scale.set(1, Math.max(.01, gr('cloud')), 1);
        core.scale.setScalar(1 + gr('lab') * .35 + .06 * Math.sin(t * 3)); core.rotation.y = t * .6;
        // flows: s.flow[i] = start time of product flow on link i, s.pay = start time of money flow
        for (let li = 0; li < 3; li++) {
          const payT = Array.isArray(s.pay) ? s.pay[li] : s.pay, on = s.flow ? clamp((t - s.flow[li]) / .5) : 0, mon = s.pay ? clamp((t - payT) / .6) : 0;
          // growth: after s.boost[li] the link carries more (faster, continuous phase)
          const bT = s.boost ? s.boost[li] : 1e9, ph = t + 1.2 * Math.max(0, t - bT);
          tubes[li].material.opacity = .35 * Math.max(on, mon);
          for (let j = 0; j < PER; j++) {
            const f = (j / PER + ph * .22) % 1; links[li].getPointAt(f, v); m4.makeScale(on, on, on); m4.setPosition(v.x, v.y + .05, v.z); prod.setMatrixAt(li * PER + j, m4);
            const g = (j / PER + ph * .18) % 1; links[li].getPointAt(1 - g, v); m4.makeScale(mon, mon, mon); m4.setPosition(v.x, v.y + .35, v.z); money.setMatrixAt(li * PER + j, m4);
          }
        }
        prod.instanceMatrix.needsUpdate = true; money.instanceMatrix.needsUpdate = true;
        // circular financing: investment packet fab → lab, then lab → cloud, then cloud → fab
        const L = s.loop; packet.visible = false; investTube.material.opacity = 0;
        if (L && t >= L[0]) {
          investTube.material.opacity = .55;
          let curve, f;
          if (t < L[1]) { curve = loopInvest; f = clamp((t - L[0]) / (L[1] - L[0])); }
          else if (t < L[2]) { curve = links[1]; f = clamp((t - L[1]) / (L[2] - L[1])); }
          else { curve = links[0]; f = 1 - clamp((t - L[2]) / (L[3] - L[2])); }
          curve.getPointAt(Math.min(.999, Math.max(.001, f)), v); packet.position.set(v.x, v.y + .45, v.z); packet.visible = t < L[3] + 1.2; packet.rotation.y = t;
          const el = document.getElementById(s.packetLabel); if (el) { const p = packet.position.clone().project(cam);
            el.style.opacity = packet.visible ? 1 : 0; el.style.transform = `translate(${(p.x * .5 + .5) * 1920}px, ${(-p.y * .5 + .5) * 1080 - 34}px) translate(-50%,-100%)`; }
        }
        if (s.rev) for (const k in s.rev) { const el = document.getElementById('mf-rev-' + k); if (!el) continue; const a = clamp((t - s.rev[k]) / .3), b = clamp((t - s.rev[k] - 2.4) / .4);
          v.copy(nodes[k].position); v.y += k === 'lab' ? 4.4 : k === 'cloud' ? 5.2 : 3.4; v.project(cam); el.style.opacity = a * (1 - b);
          el.style.transform = `translate(${(v.x * .5 + .5) * 1920}px, ${(-v.y * .5 + .5) * 1080 - 40 * a}px) translate(-50%,-100%)`; }
        label(s.labels.fab, fab, 3.2, 'left'); label(s.labels.cloud, cloud, 1.0, 'left'); label(s.labels.lab, lab, 2.4, 'right'); label(s.labels.cust, cust, 1.2, 'right');
      }
    };
  }

  // ── world: 19th-century railway at golden hour ───────────────────────
  function railway(s) {
    const rnd = RNG(1870), S = new THREE.Scene();
    S.background = new THREE.Color(0xe3bd7c); S.fog = new THREE.Fog(0xe3bd7c, 70, 320);
    const cam = new THREE.PerspectiveCamera(38, W / H, .5, 500);
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600, 60, 60), new THREE.MeshStandardMaterial({ color: 0xb9904c, roughness: 1 }));
    const gp = ground.geometry.attributes.position; for (let i = 0; i < gp.count; i++) gp.setZ(i, (rnd() - .5) * .6);
    ground.geometry.computeVertexNormals(); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; S.add(ground);
    const rail = new THREE.MeshStandardMaterial({ color: 0x5c4a3a, metalness: .6, roughness: .5 });
    const rust = new THREE.MeshStandardMaterial({ color: 0x7a4a2a, metalness: .3, roughness: .9 });
    const sleeperM = new THREE.MeshStandardMaterial({ color: 0x5a3e26, roughness: .9 });
    function track(x0, z0, x1, z1, m) {
      const len = Math.hypot(x1 - x0, z1 - z0), ang = Math.atan2(z1 - z0, x1 - x0), g = new THREE.Group();
      [-.75, .75].forEach(o => { const r = new THREE.Mesh(new THREE.BoxGeometry(len, .18, .14), m); r.position.set(0, .2, o); g.add(r); });
      const n = Math.floor(len / 1.1), sl = new THREE.InstancedMesh(new THREE.BoxGeometry(.4, .12, 2.4), sleeperM, n), m4 = new THREE.Matrix4();
      for (let i = 0; i < n; i++) { m4.makeTranslation(-len / 2 + i * 1.1, .06, 0); sl.setMatrixAt(i, m4); }
      g.add(sl); g.position.set((x0 + x1) / 2, 0, (z0 + z1) / 2); g.rotation.y = -ang; S.add(g);
    }
    track(-90, 0, 90, 0, rail);              // productive line A ↔ B
    track(0, 0, 40, -110, rust);             // branch to the empty plain
    function town(cx, cz, n, seed) {
      const r = RNG(seed);
      for (let i = 0; i < n; i++) {
        const w = 3 + r() * 3, h = 2.5 + r() * 4, g = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, w), new THREE.MeshStandardMaterial({ color: [0xc87d4f, 0xe3c89a, 0xa85e3c, 0xd9b27c][i % 4], roughness: .9 }));
        body.position.y = h / 2; body.castShadow = true; g.add(body);
        const roof = new THREE.Mesh(new THREE.ConeGeometry(w * .78, 1.8, 4), new THREE.MeshStandardMaterial({ color: 0x5a3626, roughness: .9 })); roof.position.y = h + .9; roof.rotation.y = Math.PI / 4; g.add(roof);
        const win = new THREE.Mesh(new THREE.BoxGeometry(w * .5, .5, .05), new THREE.MeshBasicMaterial({ color: 0xffd27a })); win.position.set(0, h * .55, w / 2 + .03); g.add(win);
        g.position.set(cx + (r() - .5) * 26, 0, cz + (r() - .5) * 18 + (r() < .5 ? -8 : 8)); S.add(g);
      }
      const stacks = [];
      for (let i = 0; i < 3; i++) { const c = new THREE.Mesh(new THREE.CylinderGeometry(.7, .9, 14, 10), new THREE.MeshStandardMaterial({ color: 0x7a3e2a })); c.position.set(cx + i * 4 - 4, 7, cz - 16); c.castShadow = true; S.add(c); stacks.push(c.position.clone().setY(14)); }
      return stacks;
    }
    const chimneys = [...town(-75, 0, 16, 1), ...town(75, 0, 16, 2)];
    const hut = new THREE.Mesh(new THREE.BoxGeometry(4, 3, 3), new THREE.MeshStandardMaterial({ color: 0x8a6a48, roughness: 1 })); hut.position.set(36, 1.5, -104); S.add(hut);
    // locomotive + wagons
    const train = new THREE.Group(); S.add(train);
    const blk = new THREE.MeshStandardMaterial({ color: 0x1e1e22, metalness: .6, roughness: .4 }), red = new THREE.MeshStandardMaterial({ color: 0x9b2f2f, roughness: .6 }), brass = new THREE.MeshStandardMaterial({ color: 0xd4a24c, metalness: .9, roughness: .3 });
    const boiler = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 6, 20), blk); boiler.rotation.z = Math.PI / 2; boiler.position.set(1.5, 2.2, 0); train.add(boiler);
    const cab = new THREE.Mesh(new THREE.BoxGeometry(2.4, 3, 2.4), red); cab.position.set(-2.4, 2.4, 0); train.add(cab);
    const stack = new THREE.Mesh(new THREE.CylinderGeometry(.5, .35, 1.6, 12), blk); stack.position.set(3.8, 3.8, 0); train.add(stack);
    const dome = new THREE.Mesh(new THREE.SphereGeometry(.45, 12, 8), brass); dome.position.set(1.6, 3.3, 0); train.add(dome);
    for (let i = 0; i < 4; i++) [-1, 1].forEach(sd => { const w = new THREE.Mesh(new THREE.CylinderGeometry(.75, .75, .25, 16), red); w.rotation.x = Math.PI / 2; w.position.set(-2 + i * 1.8, .9, sd * 1.0); train.add(w); });
    for (let k = 0; k < 4; k++) { const wg = new THREE.Mesh(new THREE.BoxGeometry(4.6, 1.8, 2.3), new THREE.MeshStandardMaterial({ color: 0x6b4a2f, roughness: .9 })); wg.position.set(-7.6 - k * 5.2, 1.6, 0); wg.castShadow = true; train.add(wg);
      const cargo = new THREE.Mesh(new THREE.BoxGeometry(3.8, 1.0, 1.8), new THREE.MeshStandardMaterial({ color: [0xd9c08a, 0x7a5a3a, 0xb0b8a0, 0xc98a4a][k] })); cargo.position.set(-7.6 - k * 5.2, 3.0, 0); train.add(cargo); }
    train.traverse(o => { if (o.isMesh) o.castShadow = true; });
    const lonely = new THREE.Mesh(new THREE.BoxGeometry(4.6, 1.8, 2.3), new THREE.MeshStandardMaterial({ color: 0x5a4632, roughness: 1 })); lonely.position.set(30, 1.6, -82); lonely.rotation.y = -Math.atan2(-110, 40); S.add(lonely);
    const weeds = []; for (let i = 0; i < 4; i++) { const w = new THREE.Mesh(new THREE.IcosahedronGeometry(.8, 0), new THREE.MeshStandardMaterial({ color: 0x8a6a3a, wireframe: true })); S.add(w); weeds.push([w, rnd()]); }
    const PUFF = 140, puffs = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 8, 6), new THREE.MeshStandardMaterial({ color: 0xf2e6d0, transparent: true, opacity: .55, roughness: 1 }), PUFF);
    S.add(puffs);
    S.add(new THREE.HemisphereLight(0xffe2b0, 0x7a5a30, .9));
    const sun = new THREE.DirectionalLight(0xffc27a, 2.4); sun.position.set(-60, 40, 50); sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -120, right: 120, top: 120, bottom: -120, far: 300 }); S.add(sun);
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), pos = new THREE.Vector3();
    return {
      scene: S, camera: cam, update(t, u) {
        // two-part camera: busy line, then pan to the empty branch at s.turn
        if (t < s.turn) moveCam(cam, s.camA, u); else moveCam(cam, s.camB, t - s.turn);
        const x = -70 + ((u * 9) % 150); train.position.set(x, 0, 0);
        let k = 0;
        for (let i = 0; i < 24; i++, k++) { const f = ((i / 24) + u * .5) % 1; pos.set(x + 3.8 - f * 16, 4.6 + f * 5, (Math.sin(i * 3.1) * .5) * f * 3); sc.setScalar(.35 + f * 1.1);
          m4.compose(pos, q, sc); puffs.setMatrixAt(k, m4); }
        chimneys.forEach((c, ci) => { for (let i = 0; i < 13; i++, k++) { const f = ((i / 13) + u * .12 + ci * .07) % 1; pos.set(c.x + f * 6, c.y + f * 14, c.z + f * 2); sc.setScalar(.6 + f * 2.6); m4.compose(pos, q, sc); puffs.setMatrixAt(k, m4); } });
        for (; k < PUFF; k++) { m4.makeScale(0, 0, 0); puffs.setMatrixAt(k, m4); }
        puffs.instanceMatrix.needsUpdate = true;
        weeds.forEach(([w, ph], i) => { const f = ((ph + u * .06) % 1); w.position.set(10 + f * 40, .8, -60 - i * 10 - f * 20); w.rotation.set(u * 2 + i, u * 3, 0); });
      }
    };
  }


  // ── world: railway analogy v2 — golden-hour main line with a detailed working locomotive, then an
  // abandoned branch line in a colder grade. Both sets live in one scene, 3000 units apart.
  function railway2(s) {
    const rnd = RNG(1870), S = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(36, W / H, .3, 1400);
    const hash = (x, z) => { const h = Math.sin(x * 127.1 + z * 311.7) * 43758.5453; return h - Math.floor(h); };
    const vnoise = (x, z) => { const xi = Math.floor(x), zi = Math.floor(z), xf = x - xi, zf = z - zi, u = xf * xf * (3 - 2 * xf), v = zf * zf * (3 - 2 * zf);
      return lerp(lerp(hash(xi, zi), hash(xi + 1, zi), u), lerp(hash(xi, zi + 1), hash(xi + 1, zi + 1), u), v); };
    const fbm = (x, z) => { let a = 0, f = 1, amp = 1; for (let o = 0; o < 4; o++) { a += amp * vnoise(x * f, z * f); f *= 2.03; amp *= .5; } return a / 1.875; };
    const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
    // terrain: flat corridor along the track, rolling hills beside it, mountains on the horizon
    function heightAt(x, z, ox) { const lx = x - ox, d = Math.abs(z);
      return fbm(lx * .018, z * .018) * 16 * smooth(9, 70, d) + Math.max(0, -z - 300) * .16 * (.4 + fbm(lx * .01, z * .01)) + (fbm(lx * .1, z * .1) - .5) * .6; }
    function terrain(ox, pal) {
      const geo = new THREE.PlaneGeometry(900, 900, 150, 150); geo.rotateX(-Math.PI / 2);
      const p = geo.attributes.position, col = new Float32Array(p.count * 3), c = new THREE.Color(), cA = new THREE.Color(pal[0]), cB = new THREE.Color(pal[1]), cC = new THREE.Color(pal[2]);
      for (let i = 0; i < p.count; i++) { const x = p.getX(i) + ox, z = p.getZ(i) - 200, h = heightAt(x, z, ox); p.setY(i, h); p.setZ(i, z);
        const k = clamp(h / 18), n = hash(x * .3, z * .3) * .12; c.copy(cA).lerp(cB, k * .9 + n).lerp(cC, clamp((h - 30) / 60)); col.set([c.r, c.g, c.b], i * 3); }
      geo.translate(ox, 0, 0); geo.setAttribute('color', new THREE.BufferAttribute(col, 3)); geo.computeVertexNormals();
      const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1 })); m.receiveShadow = true; S.add(m);
    }
    const BX = 3000; // abandoned set offset
    terrain(0, [0x7d8a3c, 0xa48c4c, 0x9a8a7a]); terrain(BX, [0x7d7a68, 0x8a8070, 0x8c8c90]);
    const M = (c, r = .8, m = 0) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: m });
    const add = (geo, mat, x, y, z, parent) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; (parent || S).add(o); return o; };
    // track: ballast, sleepers, rails (main line pristine; branch rusted with gaps)
    function track(x0, x1, rusty) {
      const len = x1 - x0, cx = (x0 + x1) / 2;
      add(new THREE.BoxGeometry(len, .35, 4.2), M(rusty ? 0x77726a : 0x8a8170, 1), cx, .1, 0);
      const n = Math.floor(len / 1.05), sl = new THREE.InstancedMesh(new THREE.BoxGeometry(.32, .16, 2.8), M(rusty ? 0x4a3d30 : 0x5a3e26, .95), n), m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
      let k = 0; for (let i = 0; i < n; i++) { if (rusty && hash(i, 3) < .14) continue; e.set(0, rusty ? (hash(i, 7) - .5) * .25 : 0, 0); q.setFromEuler(e);
        m4.compose(new THREE.Vector3(x0 + i * 1.05, .33, 0), q, new THREE.Vector3(1, 1, 1)); sl.setMatrixAt(k++, m4); }
      sl.count = k; sl.receiveShadow = true; S.add(sl);
      const rm = rusty ? M(0x7a4426, .9, .2) : M(0x8a8f98, .35, .9);
      [-.72, .72].forEach(z => add(new THREE.BoxGeometry(len, .16, .12), rm, cx, .49, z));
    }
    track(-300, 300, false); track(BX - 160, BX + 40, true);
    // trees (main: full canopies; branch: bare, dead)
    const treeTrunk = new THREE.CylinderGeometry(.18, .28, 1, 6), canopy = new THREE.ConeGeometry(1, 1, 7), crown = new THREE.IcosahedronGeometry(1, 0);
    function forest(ox, n, dead) {
      const tr = new THREE.InstancedMesh(treeTrunk, M(dead ? 0x5a514a : 0x4a3424, 1), n), cn = dead ? null : new THREE.InstancedMesh(rnd() < 2 ? crown : canopy, M(0x5f7a35, .95), n);
      const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(); let k = 0;
      for (let i = 0; k < n && i < n * 6; i++) { const x = ox + (rnd() - .5) * 700, z = (rnd() - .7) * 420; if (Math.abs(z) < 14) continue;
        const h = heightAt(x, z, ox), s = 2.5 + rnd() * 3.5;
        m4.compose(new THREE.Vector3(x, h + s * .5, z), q, new THREE.Vector3(1, s * (dead ? 1.4 : 1), 1)); tr.setMatrixAt(k, m4);
        if (cn) { m4.compose(new THREE.Vector3(x, h + s * 1.25, z), q, new THREE.Vector3(s * .7, s * .75, s * .7)); cn.setMatrixAt(k, m4); }
        k++; }
      tr.count = k; tr.castShadow = true; S.add(tr); if (cn) { cn.count = k; cn.castShadow = true; S.add(cn); }
    }
    forest(0, 520, false); forest(BX, 160, true);
    // dead trees near the camera path on the branch get branches
    for (let i = 0; i < 7; i++) { const g = new THREE.Group(), x = BX - 120 + i * 22 + rnd() * 6, z = (i % 2 ? 1 : -1) * (9 + rnd() * 10);
      add(new THREE.CylinderGeometry(.18, .35, 7, 6), M(0x5c544c, 1), 0, 3.5, 0, g);
      for (let b = 0; b < 4; b++) { const br = add(new THREE.CylinderGeometry(.05, .12, 3, 5), M(0x5c544c, 1), 0, 4 + b * .8, 0, g); br.rotation.z = (b % 2 ? 1 : -1) * (.6 + rnd() * .4); br.rotation.y = rnd() * 6; br.position.x = (b % 2 ? -.6 : .6); }
      g.position.set(x, heightAt(x, z, BX), z); S.add(g); }
    // productive towns at both ends of the main line, with factory chimneys
    const chimneyTops = [], windows = [];
    function town(cx, cz, n, seed) { const r = RNG(seed);
      for (let i = 0; i < n; i++) { const w = 4 + r() * 4, h = 3 + r() * 6, d = 4 + r() * 3, x = cx + (r() - .5) * 60, z = cz + (r() < .5 ? -1 : 1) * (14 + r() * 26);
        add(new THREE.BoxGeometry(w, h, d), M([0xb0643e, 0xd8c09a, 0x9a5a3c, 0xc9a77a][i % 4], .9), x, h / 2 + heightAt(x, z, 0), z);
        const roof = add(new THREE.ConeGeometry(Math.max(w, d) * .75, 2.2, 4), M(0x4a2e22, .9), x, h + 1.1 + heightAt(x, z, 0), z); roof.rotation.y = Math.PI / 4;
        const win = new THREE.Mesh(new THREE.PlaneGeometry(w * .6, h * .25), new THREE.MeshBasicMaterial({ color: 0xffc766, transparent: true, opacity: .25 })); win.position.set(x, h * .5 + heightAt(x, z, 0), z + (z > 0 ? -d / 2 - .02 : d / 2 + .02)); if (z > 0) win.rotation.y = Math.PI; S.add(win); windows.push(win); }
      for (let i = 0; i < 3; i++) { const x = cx - 10 + i * 9, z = cz - 48; add(new THREE.CylinderGeometry(.9, 1.3, 20, 10), M(0x7a3e2a, .9), x, 10, z); chimneyTops.push(new THREE.Vector3(x, 20.5, z)); }
    }
    town(-150, 0, 22, 1); town(80, 0, 26, 2);
    // ── locomotive (4-4-0 American type), tender and train ──
    const train = new THREE.Group(); S.add(train);
    const blk = M(0x1c1d22, .45, .6), red = M(0x8e2a26, .55, .1), brass = M(0xd4a24c, .3, .9), steel = M(0x9aa0a8, .35, .9), green = M(0x2e4a3a, .6, .1), wood = M(0x6b4a2f, .9);
    const L = new THREE.Group(); train.add(L);
    add(new THREE.CylinderGeometry(1.0, 1.0, 5.4, 24), green, 1.6, 2.5, 0, L).rotation.z = Math.PI / 2;               // boiler
    add(new THREE.CylinderGeometry(1.06, 1.06, 1.4, 24), blk, 4.6, 2.5, 0, L).rotation.z = Math.PI / 2;               // smokebox
    for (let b = 0; b < 4; b++) add(new THREE.TorusGeometry(1.02, .04, 6, 24), brass, .2 + b * 1.3, 2.5, 0, L).rotation.y = Math.PI / 2; // boiler bands
    const stackP = add(new THREE.CylinderGeometry(.75, .32, 1.8, 16, 1, true), blk, 4.7, 4.1, 0, L);                  // balloon stack
    add(new THREE.CylinderGeometry(.42, .5, .9, 14), brass, 2.6, 3.7, 0, L); add(new THREE.SphereGeometry(.42, 14, 8, 0, 6.3, 0, 1.6), brass, 2.6, 4.1, 0, L); // steam dome
    add(new THREE.CylinderGeometry(.35, .4, .7, 12), green, .8, 3.65, 0, L);                                           // sand dome
    const bell = add(new THREE.ConeGeometry(.28, .45, 12, 1, true), brass, 1.7, 3.85, 0, L);
    add(new THREE.BoxGeometry(.7, .6, .7), blk, 5.4, 3.3, 0, L); const lamp = add(new THREE.CircleGeometry(.24, 16), new THREE.MeshBasicMaterial({ color: 0xfff1c0 }), 5.76, 3.3, 0, L); lamp.rotation.y = Math.PI / 2;
    const pilot = add(new THREE.ConeGeometry(1.3, 1.4, 4), red, 6.0, .75, 0, L); pilot.rotation.set(0, Math.PI / 4, -Math.PI / 2); pilot.scale.set(1, .6, 1);  // cowcatcher
    add(new THREE.BoxGeometry(2.6, 2.7, 2.7), red, -1.9, 3.25, 0, L); add(new THREE.BoxGeometry(3.0, .2, 3.1), blk, -1.9, 4.7, 0, L);    // cab + roof
    [-1.36, 1.36].forEach(z => add(new THREE.PlaneGeometry(1.1, .9), new THREE.MeshBasicMaterial({ color: 0xffc766, side: THREE.DoubleSide }), -1.9, 3.8, z, L));
    add(new THREE.BoxGeometry(9.2, .35, 2.2), blk, 1.4, 1.35, 0, L);                                                   // frame
    // cylinders, driving wheels with spokes, pony truck
    const wheels = [], rods = [];
    const wheel = (x, r, z, spokes) => { const g = new THREE.Group(); g.position.set(x, r, z); L.add(g);
      add(new THREE.TorusGeometry(r * .92, r * .1, 8, 28), red, 0, 0, 0, g); add(new THREE.CylinderGeometry(r * .22, r * .22, .22, 14), red, 0, 0, 0, g).rotation.x = Math.PI / 2;
      add(new THREE.TorusGeometry(r * .98, r * .05, 6, 28), steel, 0, 0, z > 0 ? -.06 : .06, g);
      for (let k = 0; k < spokes; k++) { const sp = add(new THREE.BoxGeometry(.07, r * .85, .08), red, 0, 0, 0, g); sp.rotation.z = k / spokes * Math.PI * 2; sp.translateY(r * .45); }
      if (r > .8) { const cw = add(new THREE.CylinderGeometry(r * .55, r * .55, .12, 16, 1, false, 0, 1.6), red, 0, 0, 0, g); cw.rotation.x = Math.PI / 2; }
      wheels.push([g, r]); return g; };
    const DR = 1.15, D1 = -.4, D2 = 2.0;
    [-1, 1].forEach(sd => { const z = sd * 1.18;
      wheel(D1, DR, z, 14); wheel(D2, DR, z, 14); wheel(4.3, .5, z, 8); wheel(5.4, .5, z, 8);
      const cyl = add(new THREE.CylinderGeometry(.42, .42, 1.5, 14), blk, 4.85, DR + .1, sd * 1.45, L); cyl.rotation.z = Math.PI / 2;
      const side = add(new THREE.BoxGeometry(D2 - D1 + .3, .14, .08), steel, 0, 0, sd * 1.5, L);        // coupling (side) rod
      const conn = add(new THREE.BoxGeometry(1, .16, .08), steel, 0, 0, sd * 1.58, L);                  // main (connecting) rod
      const piston = add(new THREE.CylinderGeometry(.05, .05, 1.6, 8), steel, 0, 0, sd * 1.58, L); piston.rotation.z = Math.PI / 2;
      const xhead = add(new THREE.BoxGeometry(.35, .3, .14), brass, 0, 0, sd * 1.58, L);
      rods.push({ sd, side, conn, piston, xhead }); });
    // tender with coal, then freight wagons and a passenger coach
    add(new THREE.BoxGeometry(4.2, 2.2, 2.6), green, -5.6, 2.2, 0, train); add(new THREE.BoxGeometry(3.4, .7, 2.2), M(0x141414, 1), -5.4, 3.5, 0, train);
    const smallWheels = [];
    const bogie = (x, parent) => [-1, 1].forEach(sd => [-.7, .7].forEach(dx => { const g = new THREE.Group(); g.position.set(x + dx, .55, sd * 1.18); parent.add(g);
      add(new THREE.CylinderGeometry(.55, .55, .14, 14), blk, 0, 0, 0, g).rotation.x = Math.PI / 2; add(new THREE.BoxGeometry(.08, .9, .06), steel, 0, 0, sd * .08, g); smallWheels.push(g); }));
    bogie(-6.6, train); bogie(-4.6, train);
    const cargoCol = [0xd9c08a, 0x7a5a3a, 0xb0b8a0, 0xc98a4a, 0x8a9a6a];
    for (let k = 0; k < 5; k++) { const x = -10.6 - k * 5.4;
      add(new THREE.BoxGeometry(4.8, 1.6, 2.5), k === 4 ? M(0x6e2a22, .7) : wood, x, 1.9, 0, train);
      if (k === 4) { add(new THREE.BoxGeometry(4.8, 1.3, 2.5), M(0x6e2a22, .7), x, 3.3, 0, train); add(new THREE.BoxGeometry(5, .2, 2.7), blk, x, 4.05, 0, train);
        for (let w = 0; w < 4; w++) [-1.26, 1.26].forEach(z => add(new THREE.PlaneGeometry(.7, .6), new THREE.MeshBasicMaterial({ color: 0xffd27a, side: THREE.DoubleSide }), x - 1.6 + w * 1.05, 3.3, z, train)); }
      else for (let c = 0; c < 3; c++) add(new THREE.BoxGeometry(1.3, .9 + hash(k, c) * .6, 2.0), M(cargoCol[(k + c) % 5], .9), x - 1.5 + c * 1.5, 3.1, 0, train);
      bogie(x - 1.4, train); bogie(x + 1.4, train); }
    // steam: puffs emitted from the stack with every half driver revolution, drifting back and rising
    const PUFF = 90, puffs = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), new THREE.MeshStandardMaterial({ color: 0xf6efe2, transparent: true, opacity: .42, roughness: 1, depthWrite: false }), PUFF); S.add(puffs);
    const CPUFF = 60, csmoke = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), new THREE.MeshStandardMaterial({ color: 0x8a8278, transparent: true, opacity: .45, roughness: 1 }), CPUFF); S.add(csmoke);
    // ── abandoned branch: broken station, sagging fence, buffer stop, rusted wagon, rolling tumbleweed ──
    const B = new THREE.Group(); B.position.set(BX, 0, 0); S.add(B);
    add(new THREE.BoxGeometry(18, 1.0, 5), M(0x8a857c, 1), -40, .5, -5.2, B);                                           // platform
    add(new THREE.BoxGeometry(8, 4.5, 5), M(0x7a6a58, 1), -40, 3.25, -10.6, B);                                         // station house
    const roofB = add(new THREE.BoxGeometry(9.5, .3, 6.5), M(0x4a4038, 1), -40, 5.9, -10.6, B); roofB.rotation.z = .22; roofB.rotation.x = -.06;
    for (let w = 0; w < 3; w++) { add(new THREE.PlaneGeometry(1.3, 1.2), M(0x1a1714, 1), -42.6 + w * 2.6, 3.4, -8.08, B);
      for (let p = 0; p < 2; p++) { const pl = add(new THREE.BoxGeometry(1.6, .18, .05), M(0x8a7350, 1), -42.6 + w * 2.6, 3.1 + p * .55, -8.0, B); pl.rotation.z = (hash(w, p) - .5) * .7; } }
    const sign = new THREE.Group(); sign.position.set(-44, 4.6, -7.9); B.add(sign);
    add(new THREE.BoxGeometry(4.2, .9, .12), M(0xd8cdb0, 1), 2.0, -.35, 0, sign);
    for (let i = 0; i < 18; i++) { const f = add(new THREE.BoxGeometry(.14, 1.4, .14), M(0x6a5a48, 1), -70 + i * 3, .7, 6.5, B); f.rotation.z = hash(i, 9) < .3 ? (hash(i, 2) - .5) * 1.6 : (hash(i, 4) - .5) * .2; }
    add(new THREE.BoxGeometry(.6, 1.6, 3.2), M(0x7a2a22, .9), 40.5, 1.1, 0, B); add(new THREE.BoxGeometry(.3, .3, 3.6), M(0x3a2a20, 1), 40.2, 1.6, 0, B); // buffer stop
    const wreck = new THREE.Group(); wreck.position.set(-12, .2, 0); wreck.rotation.set(.04, .02, .07); B.add(wreck);
    add(new THREE.BoxGeometry(4.8, 1.6, 2.5), M(0x6a4a34, 1, .1), 0, 1.6, 0, wreck); bogie(-1.4, wreck); bogie(1.4, wreck);
    for (let i = 0; i < 40; i++) { const g = add(new THREE.ConeGeometry(.25, .9 + hash(i, 1), 4), M(0x8a7a48, 1), -80 + hash(i, 5) * 120, .55, (hash(i, 6) - .5) * 4.4, B); g.rotation.z = (hash(i, 3) - .5) * .6; }
    const tumble = add(new THREE.IcosahedronGeometry(.8, 1), new THREE.MeshStandardMaterial({ color: 0x9a8050, wireframe: true }), 0, .8, 2.5, B);
    // lighting: warm low sun (main) → cold overcast (branch), switched at s.turn
    const hemi = new THREE.HemisphereLight(0xffe2b0, 0x6a5030, .75); S.add(hemi);
    const sun = new THREE.DirectionalLight(0xffb36a, 2.6); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -.0006;
    Object.assign(sun.shadow.camera, { left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 260 }); S.add(sun, sun.target);
    const sky = new THREE.Mesh(new THREE.SphereGeometry(1200, 24, 12), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
      uniforms: { top: { value: new THREE.Color(0x6f8fb8) }, mid: { value: new THREE.Color(0xf2c27a) }, low: { value: new THREE.Color(0xffd9a0) } },
      vertexShader: 'varying vec3 p; void main(){ p = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
      fragmentShader: 'uniform vec3 top; uniform vec3 mid; uniform vec3 low; varying vec3 p; void main(){ float h=p.y; vec3 c=mix(low,mid,smoothstep(-.02,.08,h)); c=mix(c,top,smoothstep(.08,.5,h)); gl_FragColor=vec4(c,1.); }' }));
    S.add(sky); S.fog = new THREE.Fog(0xf0c88a, 90, 620);
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), pos = new THREE.Vector3(), tgt = new THREE.Vector3(), stackW = new THREE.Vector3();
    const V = 7.5, X0 = -95; // train speed (units/s) and start
    const trainX = (t) => X0 + V * (t - s.start);
    function keyed(keys, t, ox) { let i = 0; while (i < keys.length - 1 && t >= keys[i + 1][0]) i++;
      const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)], f = b === a ? 0 : ease(clamp((t - a[0]) / (b[0] - a[0])));
      cam.position.lerpVectors(V3(a[1]), V3(b[1]), f); cam.position.x += ox; tgt.lerpVectors(V3(a[2]), V3(b[2]), f); tgt.x += ox;
      cam.fov = lerp(a[3], b[3], f); cam.updateProjectionMatrix(); cam.lookAt(tgt); cam.updateMatrixWorld(); }
    return {
      scene: S, camera: cam, update(t, u) {
        const branch = t >= s.turn, tx = trainX(t);
        train.position.set(tx, .41, 0);
        // wheels roll without slipping: angle = distance / radius (driving wheels, pony and wagon wheels)
        const dist = V * (t - s.start);
        wheels.forEach(([g, r]) => { g.rotation.z = -dist / r; }); smallWheels.forEach(g => { g.rotation.z = -dist / .55; });
        const th = -dist / DR, pr = DR * .5;
        rods.forEach(({ sd, side, conn, piston, xhead }) => { const ph = th + (sd > 0 ? 0 : Math.PI / 2), px = Math.cos(ph) * pr, py = Math.sin(ph) * pr;
          side.position.set((D1 + D2) / 2 + px, DR + py, side.position.z);
          const pinX = D2 + px, pinY = DR + py, cyY = DR + .1, Lr = 2.4, xh = pinX + Math.sqrt(Lr * Lr - (pinY - cyY) * (pinY - cyY));
          conn.scale.x = Lr; conn.position.set((pinX + xh) / 2, (pinY + cyY) / 2, conn.position.z); conn.rotation.z = Math.atan2(cyY - pinY, xh - pinX);
          xhead.position.set(xh, cyY, xhead.position.z); piston.position.set(xh + .8, cyY, piston.position.z); });
        bell.rotation.x = Math.sin(t * 6) * .25;
        // steam: one puff per half revolution, emitted at the stack's world position at its birth time
        const period = Math.PI * DR / V, n0 = Math.floor((t - s.start) / period);
        for (let k = 0; k < PUFF; k++) { const n = n0 - k, tb = s.start + n * period, age = t - tb;
          if (n < 0 || age > 6) { m4.makeScale(0, 0, 0); puffs.setMatrixAt(k, m4); continue; }
          const bx = trainX(tb) + 4.7, sz = .45 + age * .62;
          pos.set(bx - age * 2.2 + Math.sin(n * 1.7) * .6, 5.2 + age * 1.9 - age * age * .08, Math.cos(n * 2.3) * .8 - age * .9);
          q.setFromAxisAngle(sc.set(0, 1, 0), n); sc.setScalar(sz * clamp(age * 4) * (1 - smooth(4.5, 6, age))); m4.compose(pos, q, sc); puffs.setMatrixAt(k, m4); }
        puffs.instanceMatrix.needsUpdate = true;
        const busy = s.returns ? .35 + .65 * clamp((t - s.returns) / 1.2) : 1;
        for (let k = 0; k < CPUFF; k++) { const c = chimneyTops[k % chimneyTops.length], ph = ((t * .25 + k / CPUFF * 3) % 1), age = ph * 8;
          pos.set(c.x + age * 2.2, c.y + age * 2.2, c.z + Math.sin(k) * age * .4); sc.setScalar((1.2 + age * .9) * busy * (1 - ph)); q.identity(); m4.compose(pos, q, sc); csmoke.setMatrixAt(k, m4); }
        csmoke.instanceMatrix.needsUpdate = true;
        windows.forEach((w, i) => { w.material.opacity = .25 + .7 * (s.returns ? clamp((t - s.returns - (i % 7) * .12) / .4) : 1); });
        // grade + light per set
        if (!branch) { sun.color.setHex(0xffb36a); sun.intensity = 2.6; hemi.intensity = .75; S.fog.color.setHex(0xf0c88a); S.fog.near = 90; S.fog.far = 620;
          sky.material.uniforms.top.value.setHex(0x6f8fb8); sky.material.uniforms.mid.value.setHex(0xf2c27a); sky.material.uniforms.low.value.setHex(0xffd9a0);
          keyed(s.keysA, t, tx); }
        else { sun.color.setHex(0xb8c4d6); sun.intensity = 1.3; hemi.intensity = .8; hemi.color.setHex(0xc0c8d4); S.fog.color.setHex(0xaab0b8); S.fog.near = 40; S.fog.far = 340;
          sky.material.uniforms.top.value.setHex(0x7c8594); sky.material.uniforms.mid.value.setHex(0xa6adb6); sky.material.uniforms.low.value.setHex(0xb8bcc2);
          keyed(s.keysB, t, BX); }
        // the sun (and its shadow frustum) follows the camera target so shadows stay crisp in every shot
        sun.target.position.copy(tgt); sun.position.copy(tgt).add(pos.set(-70, 55, 60)); sun.target.updateMatrixWorld();
        sky.position.copy(cam.position);
        // abandoned details: the station sign drops on one nail on "disaster", a tumbleweed rolls across
        const sg = s.sign ? ease(clamp((t - s.sign) / .5)) : 0; sign.rotation.z = -sg * 1.15 + (sg > .99 ? Math.sin((t - s.sign) * 5) * .06 * Math.exp(-(t - s.sign - .5) * 1.5) : 0);
        const tu = Math.max(0, t - s.turn); tumble.position.set(-60 + tu * 4.2, .8 + Math.abs(Math.sin(tu * 3)) * .4, 2.5 - tu * .3); tumble.rotation.z = -tu * 5;
      }
    };
  }


  // ── world: hyperscale campus v2 — detailed halls, cooling plant, generator yard, substation, lattice
  // transmission, a hall under construction, deliveries. Used for power (c04_10) and capex (c04_11).
  function canvasTex(w, h, draw, rep) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); } return t; }
  function campus2(s) {
    const rnd = RNG(17), S = new THREE.Scene();
    S.fog = new THREE.Fog(0xb88a78, 260, 1500); S.environment = ENV;
    const cam = new THREE.PerspectiveCamera(40, W / H, .5, 5000);
    const sky = new THREE.Mesh(new THREE.SphereGeometry(3000, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
      vertexShader: 'varying vec3 v;void main(){v=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
      fragmentShader: 'varying vec3 v;void main(){float h=clamp(v.y*2.2,0.,1.);vec3 c=mix(vec3(.99,.62,.38),vec3(.10,.14,.28),pow(h,.55));gl_FragColor=vec4(c,1.);}' })); S.add(sky);
    const M = (c, r = .7, m = .2, e) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: m, emissive: e || 0 });
    const add = (geo, mat, x, y, z, p) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; (p || S).add(o); return o; };
    // ground: grass/earth noise, gravel pads, asphalt roads with markings
    const groundTex = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#5a5a42'; g.fillRect(0, 0, w, h); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${70 + rnd() * 50},${70 + rnd() * 40},${40 + rnd() * 30},.5)`; g.fillRect(rnd() * w, rnd() * h, 2 + rnd() * 3, 2 + rnd() * 3); } }, [40, 40]);
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), new THREE.MeshStandardMaterial({ map: groundTex, roughness: 1 })); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; S.add(ground);
    const roadTex = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#3c3a40'; g.fillRect(0, 0, w, h); g.fillStyle = '#e8e2c8'; for (let x = 0; x < w; x += 64) g.fillRect(x, h / 2 - 2, 34, 4); g.fillStyle = '#8a8676'; g.fillRect(0, 2, w, 3); g.fillRect(0, h - 5, w, 3); }, [30, 1]);
    [[0, 34, 420, 10], [0, -36, 420, 10], [150, 0, 10, 150]].forEach(([x, z, w, d]) => { const r = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshStandardMaterial({ map: roadTex, roughness: .9 })); r.rotation.x = -Math.PI / 2; if (d > w) r.rotation.z = Math.PI / 2; r.position.set(x, .06, z); r.receiveShadow = true; S.add(r); });
    const pad = (x, z, w, d, c) => { const p = new THREE.Mesh(new THREE.PlaneGeometry(w, d), M(c, .95, 0)); p.rotation.x = -Math.PI / 2; p.position.set(x, .04, z); p.receiveShadow = true; S.add(p); };
    // hall facade: metal panel seams, louvre band (ventilation), loading doors, a lit window strip
    const facade = canvasTex(1024, 256, (g, w, h) => { g.fillStyle = '#c9ced6'; g.fillRect(0, 0, w, h);
      for (let x = 0; x < w; x += 16) { g.fillStyle = x % 32 ? '#bfc4cc' : '#d3d8e0'; g.fillRect(x, 0, 16, h); }
      g.fillStyle = '#5a6270'; g.fillRect(0, 34, w, 40); g.fillStyle = '#7a8492'; for (let x = 0; x < w; x += 6) g.fillRect(x, 36, 3, 36);
      for (let k = 0; k < 4; k++) { g.fillStyle = '#7a828e'; g.fillRect(90 + k * 240, 150, 90, 106); g.fillStyle = '#6a727e'; for (let y = 156; y < 256; y += 10) g.fillRect(92 + k * 240, y, 86, 3); }
      g.fillStyle = '#2a3446'; g.fillRect(0, 108, w, 14); });
    const facadeLit = canvasTex(1024, 256, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#7fe9ff'; g.fillRect(0, 110, w, 10); });
    const hallM = new THREE.MeshStandardMaterial({ map: facade, emissiveMap: facadeLit, emissive: new THREE.Color(0x000000), roughness: .55, metalness: .35 });
    const roofM = M(0x8a909a, .8, .3);
    const fanGeo = new THREE.CylinderGeometry(.9, .9, .12, 14), chillerM = M(0x9aa3b0, .45, .6), fanM = M(0x20252c, .5, .4);
    const halls = [], fans = [];
    function hall(x, z, rot) {
      const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rot || 0; S.add(g);
      const body = add(new THREE.BoxGeometry(64, 13, 28), [hallM, hallM, roofM, roofM, hallM, hallM], 0, 6.5, 0, g);
      add(new THREE.BoxGeometry(64.6, 1.0, 28.6), M(0x7a808a, .6, .4), 0, 13.3, 0, g);                       // parapet
      for (let k = 0; k < 12; k++) { const cx = -27 + k * 4.9;                                                // rooftop chillers, 2 fans each
        add(new THREE.BoxGeometry(4.2, 2.2, 8.5), chillerM, cx, 14.9, -5, g);
        for (let f = 0; f < 2; f++) { const fan = add(fanGeo, fanM, cx, 16.05, -7.2 + f * 4.4, g); fans.push(fan); }
        add(new THREE.BoxGeometry(4.2, .6, 8.5), M(0x6a7280, .6, .5), cx, 13.9, 5.5, g); }
      for (let k = 0; k < 6; k++) { add(new THREE.BoxGeometry(12, 3.4, 3.2), M(0x6e7a6a, .7, .3), -26 + k * 10.5, 1.7, 18.5, g);   // generator containers
        add(new THREE.CylinderGeometry(.35, .35, 3, 8), M(0x3a3a3a, .5, .5), -22 + k * 10.5, 4.6, 18.5, g); }
      halls.push({ g, body }); return g;
    }
    const HP = [[-80, -10], [-10, -10], [60, -10], [-80, -70], [-10, -70]];
    HP.forEach(([x, z]) => hall(x, z));
    pad(60, -70, 70, 34, 0x8a8478); // construction slab
    // cutaway of hall 1: interior racks visible through a missing wall section (servers installed)
    const cut = new THREE.Group(); cut.position.set(-10, 0, -10); S.add(cut);
    const rackTex = canvasTex(64, 256, (g, w, h) => { g.fillStyle = '#141a22'; g.fillRect(0, 0, w, h); for (let y = 6; y < h; y += 12) { g.fillStyle = '#26303e'; g.fillRect(4, y, 56, 9); g.fillStyle = '#38d6ff'; g.fillRect(50, y + 3, 4, 3); } });
    const rackG = new THREE.BoxGeometry(1.0, 2.4, 1.2), rackM = new THREE.MeshStandardMaterial({ map: rackTex, emissiveMap: rackTex, emissive: new THREE.Color(0x000000), roughness: .5, metalness: .5 });
    const racks = new THREE.InstancedMesh(rackG, rackM, 160); let ri = 0; const m4 = new THREE.Matrix4();
    for (let row = 0; row < 4; row++) for (let k = 0; k < 40; k++) { m4.makeTranslation(-29 + k * 1.45, 1.2, -9 + row * 5); racks.setMatrixAt(ri++, m4); }
    cut.add(racks);
    const cutWall = halls[1].body; // replace the front-facing faces of hall 1 with an open frame
    cutWall.material = [hallM, hallM, roofM, roofM, new THREE.MeshStandardMaterial({ transparent: true, opacity: 0 }), hallM];
    for (let k = 0; k < 9; k++) add(new THREE.BoxGeometry(.5, 13, .5), M(0x7a808a, .5, .6), -32 + k * 8, 6.5, 14, halls[1].g);
    // substation: gravel yard, fence, transformers with radiator fins and bushings, lattice gantries, busbars
    const SUB = new THREE.Group(); SUB.position.set(150, 0, -60); S.add(SUB);
    { const p = new THREE.Mesh(new THREE.PlaneGeometry(60, 44), M(0x8d8a82, 1, 0)); p.rotation.x = -Math.PI / 2; p.position.y = .05; SUB.add(p); }
    const posts = new THREE.InstancedMesh(new THREE.BoxGeometry(.15, 2.6, .15), M(0x8a8f98, .5, .7), 64); let pi = 0;
    for (let k = 0; k < 16; k++) [[-30 + k * 4, -22], [-30 + k * 4, 22], [-30, -22 + k * 2.9], [30, -22 + k * 2.9]].forEach(([x, z]) => { if (pi < 64) { m4.makeTranslation(x, 1.3, z); posts.setMatrixAt(pi++, m4); } });
    SUB.add(posts);
    const trM = M(0x6b7a6a, .6, .4), finM = M(0x5a6858, .6, .4), porc = M(0xd9d4c8, .3, .1), trGlow = [];
    for (let i = 0; i < 3; i++) { const g = new THREE.Group(); g.position.set(-14 + i * 14, 0, 4); SUB.add(g);
      add(new THREE.BoxGeometry(6, 4.6, 4.2), trM, 0, 2.6, 0, g); add(new THREE.CylinderGeometry(.6, .6, 4.6, 12), trM, 0, 6.2, -1.8, g).rotation.z = Math.PI / 2;
      for (let f = 0; f < 10; f++) { add(new THREE.BoxGeometry(.12, 3.6, 1.2), finM, -2.7 + f * .6, 2.4, 2.8, g); add(new THREE.BoxGeometry(.12, 3.6, 1.2), finM, -2.7 + f * .6, 2.4, -2.8, g); }
      for (let b = 0; b < 3; b++) { const bx = -1.8 + b * 1.8; add(new THREE.CylinderGeometry(.2, .3, 2.4, 10), porc, bx, 6.1, 1, g);
        for (let r = 0; r < 5; r++) add(new THREE.CylinderGeometry(.42, .42, .08, 12), porc, bx, 5.2 + r * .42, 1, g); }
      const glow = add(new THREE.BoxGeometry(6.1, .25, 4.3), new THREE.MeshBasicMaterial({ color: 0x38d6ff, transparent: true, opacity: 0 }), 0, .4, 0, g); trGlow.push(glow); }
    const latM = new THREE.LineBasicMaterial({ color: 0xb8c0cc });
    function lattice(h, wb, wt, arms) { const pts = []; const lvl = 8, L = (i) => ({ y: i / lvl * h, w: lerp(wb, wt, i / lvl) });
      for (let i = 0; i < lvl; i++) { const a = L(i), b = L(i + 1);
        [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([sx, sz], k, arr) => { const [tx, tz] = arr[(k + 1) % 4];
          pts.push(sx * a.w, a.y, sz * a.w, sx * b.w, b.y, sz * b.w); pts.push(sx * a.w, a.y, sz * a.w, tx * b.w, b.y, tz * b.w); pts.push(tx * a.w, a.y, tz * a.w, sx * b.w, b.y, sz * b.w); }); }
      (arms || []).forEach(([y, len]) => { pts.push(-len, y, 0, len, y, 0, -len, y, 0, 0, y + 2, 0, len, y, 0, 0, y + 2, 0); });
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3)); return new THREE.LineSegments(geo, latM); }
    for (let i = 0; i < 3; i++) { const gt = lattice(11, .9, .6, [[11, 4]]); gt.position.set(136 + i * 14, 0, -70); S.add(gt); }
    // transmission line: lattice pylons marching in from the hills, three conductors with energy pulses
    const PY = []; for (let i = 0; i < 8; i++) PY.push(new THREE.Vector3(165 + i * 48, 0, -66 - i * 52));
    PY.forEach(p => { const t = lattice(34, 3.2, .9, [[26, 9], [31, 7]]); t.position.copy(p); t.rotation.y = .74; S.add(t); });
    const cond = [], pulses = [];
    [-7, 0, 7].forEach((off, ci) => { const pts = [];
      for (let i = PY.length - 1; i > 0; i--) { const a = PY[i], b = PY[i - 1]; for (let j = 0; j < 12; j++) { const f = j / 12;
        pts.push(new THREE.Vector3(lerp(a.x, b.x, f) + off * .67, (ci === 1 ? 31 : 26) - Math.sin(f * Math.PI) * 4, lerp(a.z, b.z, f) + off * .74)); } }
      pts.push(new THREE.Vector3(150 + off, 11, -70)); pts.push(new THREE.Vector3(136 + ci * 14, 7, -56));
      const c = new THREE.CatmullRomCurve3(pts); cond.push(c);
      S.add(new THREE.Mesh(new THREE.TubeGeometry(c, 240, .1, 5, false), new THREE.MeshBasicMaterial({ color: 0x4a5560 })));
      for (let q = 0; q < 8; q++) { const p = new THREE.Mesh(new THREE.SphereGeometry(.55, 10, 8), new THREE.MeshBasicMaterial({ color: 0x9ff3ff })); S.add(p); pulses.push([p, c, q / 8]); } });
    // underground feeders: substation → each hall (light up on "energy")
    const feeders = HP.map(([x, z]) => { const c = new THREE.CatmullRomCurve3([new THREE.Vector3(140, .2, -50), new THREE.Vector3(110, .2, z + 16), new THREE.Vector3(x + 20, .2, z + 16)]);
      const m = new THREE.Mesh(new THREE.TubeGeometry(c, 40, .35, 6, false), new THREE.MeshBasicMaterial({ color: 0x38d6ff, transparent: true, opacity: 0 })); S.add(m); return m; });
    // construction: steel frame of hall 6, tower crane lifting a chiller, trucks delivering
    const frame = new THREE.Group(); frame.position.set(60, 0, -70); S.add(frame); const steel = M(0x8a5a3a, .6, .5);
    for (let i = 0; i < 9; i++) for (let j = 0; j < 4; j++) add(new THREE.BoxGeometry(.6, 13, .6), steel, -32 + i * 8, 6.5, -13 + j * 8.6, frame);
    for (let i = 0; i < 9; i++) add(new THREE.BoxGeometry(.5, .7, 26), steel, -32 + i * 8, 13, 0, frame);
    for (let j = 0; j < 4; j++) add(new THREE.BoxGeometry(64, .7, .5), steel, 0, 13, -13 + j * 8.6, frame);
    const roofPanels = []; for (let i = 0; i < 8; i++) { const p = add(new THREE.BoxGeometry(8, .3, 26), roofM, -28 + i * 8, 13.5, 0, frame); p.visible = i < 3; roofPanels.push(p); }
    const crane = new THREE.Group(); crane.position.set(40, 0, -90); S.add(crane);
    const mast = lattice(46, 1.2, 1.2, []); crane.add(mast);
    const jibG = new THREE.Group(); jibG.position.y = 46; crane.add(jibG);
    add(new THREE.BoxGeometry(44, 1.4, 1.4), M(0xf2b134, .5, .3), 14, 0, 0, jibG); add(new THREE.BoxGeometry(6, 3, 2.4), M(0x555b66, .6, .4), -8, -1.6, 0, jibG);
    add(new THREE.BoxGeometry(2.6, 2.6, 2.6), M(0xf2b134, .5, .3), 0, -2, 0, jibG);
    const hook = new THREE.Group(); jibG.add(hook);
    const cable = add(new THREE.BoxGeometry(.1, 1, .1), M(0x222222, .5, .5), 0, 0, 0, hook);
    const load = new THREE.Group(); hook.add(load); add(new THREE.BoxGeometry(4.2, 2.2, 8.5), chillerM, 0, -1.1, 0, load);
    for (let f = 0; f < 2; f++) add(fanGeo, fanM, 0, .05, -2.2 + f * 4.4, load);
    const trucks = []; for (let i = 0; i < 3; i++) { const g = new THREE.Group(); S.add(g);
      add(new THREE.BoxGeometry(3, 3, 2.6), M([0xd9503f, 0x3a6ab0, 0xe0e0e0][i], .5, .3), 7, 1.9, 0, g); add(new THREE.BoxGeometry(11, .6, 2.6), M(0x3a3a3a, .6, .4), -.5, .9, 0, g);
      for (let w = 0; w < 4; w++) [-1.3, 1.3].forEach(z => add(new THREE.CylinderGeometry(.55, .55, .4, 12), M(0x111111, .8, .1), -4 + w * 3.6, .55, z, g).rotation.x = Math.PI / 2);
      const cargo = i === 0 ? add(new THREE.BoxGeometry(5, 3.6, 2.4), trM, -1, 2.9, 0, g) : i === 1 ? add(new THREE.BoxGeometry(9, 2.8, 2.4), M(0x2a3446, .5, .5), -.5, 2.5, 0, g) : add(new THREE.BoxGeometry(8, 2.2, 2.4), chillerM, -.5, 2.2, 0, g);
      trucks.push({ g, cargo }); }
    // highlight rings for the capex items (frame, transformer delivery, chiller lift, server delivery)
    const ringM = () => new THREE.MeshBasicMaterial({ color: 0xf2c66d, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false });
    const ring = (r) => { const m = new THREE.Mesh(new THREE.RingGeometry(r, r + 1.2, 48), ringM()); m.rotation.x = -Math.PI / 2; S.add(m); return m; };
    const v3 = new THREE.Vector3();
    const rings = { frame: ring(40), power: ring(9), cooling: ring(8), servers: ring(9) };
    rings.frame.position.set(60, .3, -70);
    S.add(new THREE.HemisphereLight(0xffd2b0, 0x303038, 1.0));
    const sun = new THREE.DirectionalLight(0xffb27a, 2.4); sun.position.set(-160, 90, 120); sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -200, right: 200, top: 200, bottom: -200, far: 700 }); S.add(sun);
    return {
      scene: S, camera: cam, update(t, u) {
        keyCam(cam, s.keys, t); sky.position.copy(cam.position);
        const on = s.power ? clamp((t - s.power) / .6) : 1, sup = s.supply ? clamp((t - s.supply) / .8) : 1;
        pulses.forEach(([p, c, ph]) => { p.visible = on > 0; const f = (ph + t * .16) % 1; p.position.copy(c.getPointAt(f)); p.scale.setScalar(.4 + .8 * on); });
        trGlow.forEach((g, i) => g.material.opacity = sup * (.35 + .25 * Math.sin(t * 9 + i)));
        const en = s.energy ? clamp((t - s.energy) / 1.0) : 1; feeders.forEach((f, i) => f.material.opacity = .8 * clamp(en * 1.6 - i * .15));
        const run = s.running ? clamp((t - s.running) / 1.2) : 1;
        halls.forEach((h, i) => { const k = clamp(run * 1.6 - i * .15); h.body.material[0].emissive.setRGB(0, .55 * k, .75 * k); });
        rackM.emissive.setRGB(.35 * run, .8 * run, 1 * run);
        fans.forEach((f, i) => { f.rotation.y = t * 9 * run + i; });
        // construction + procurement on "building … substantial investment"
        const b = s.build ? t - s.build : -1;
        const swing = clamp(b / 3.2); jibG.rotation.y = -.9 + 1.5 * ease(swing);
        const lower = clamp((b - 3.0) / 1.2); hook.position.set(26, -6 - 26 * ease(lower) * .5, 0);
        cable.scale.y = 6 + 13 * ease(lower); cable.position.y = (6 + 13 * ease(lower)) / 2 - .1; load.position.y = -6 - 13 * ease(lower) + 6;
        roofPanels.forEach((p, i) => p.visible = i < 3 + Math.floor(clamp(b / 4) * 5));
        trucks.forEach(({ g }, i) => { const f = clamp((b - i * .5) / 3.4); g.position.set(230 - 120 * ease(f) + i * 20, 0, -37); g.rotation.y = Math.PI; });
        const R = s.items || {};
        const pulse = (k) => { if (R[k] === undefined) return 0; const d = t - R[k]; return d < 0 ? 0 : clamp(d / .3) * (.5 + .5 * Math.sin(d * 8)); };
        rings.frame.material.opacity = pulse('frame'); rings.power.material.opacity = pulse('power'); rings.cooling.material.opacity = pulse('cooling'); rings.servers.material.opacity = pulse('servers');
        rings.power.position.set(trucks[0].g.position.x, .3, trucks[0].g.position.z); rings.servers.position.set(trucks[1].g.position.x, .3, trucks[1].g.position.z);
        load.getWorldPosition(v3); rings.cooling.position.set(v3.x, v3.y + 2, v3.z);
      }
    };
  }

  const WORLDS = { dataHall, campus, chip, diorama, railway, serverRack, railway2, campus2 };
  function draw(t) {
    const s = shots.find(x => t >= x.start && t < x.end);
    if (!R) return;
    if (!s) { R.clear(); return; }
    if (!s.inst) s.inst = WORLDS[s.world](s);
    s.inst.update(t, t - s.start);
    R.render(s.inst.scene, s.inst.camera);
  }
  g.AI3D = { init, add, draw, shots };
})(window);
