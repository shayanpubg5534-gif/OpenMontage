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
    return {
      scene: S, camera: cam, update(t, u) {
        moveCam(cam, s.cam, u);
        G.rotation.y = s.spin ? u * s.spin : 0;
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
          const on = s.flow ? clamp((t - s.flow[li]) / .5) : 0, mon = s.pay ? clamp((t - s.pay) / .6) : 0;
          tubes[li].material.opacity = .35 * Math.max(on, mon);
          for (let j = 0; j < PER; j++) {
            const f = (j / PER + t * .22) % 1; links[li].getPointAt(f, v); m4.makeScale(on, on, on); m4.setPosition(v.x, v.y + .05, v.z); prod.setMatrixAt(li * PER + j, m4);
            const g = (j / PER + t * .18) % 1; links[li].getPointAt(1 - g, v); m4.makeScale(mon, mon, mon); m4.setPosition(v.x, v.y + .35, v.z); money.setMatrixAt(li * PER + j, m4);
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

  const WORLDS = { dataHall, campus, chip, diorama, railway };
  function draw(t) {
    const s = shots.find(x => t >= x.start && t < x.end);
    if (!s || !R) return;
    if (!s.inst) s.inst = WORLDS[s.world](s);
    s.inst.update(t, t - s.start);
    R.render(s.inst.scene, s.inst.camera);
  }
  g.AI3D = { init, add, draw, shots };
})(window);
