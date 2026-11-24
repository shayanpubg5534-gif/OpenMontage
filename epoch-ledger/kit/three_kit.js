// Epoch Ledger Three.js kit (kit/three_kit.js) — reusable, deterministic helpers for episode 3D worlds.
// Load with assemble(head_scripts=["vendor/three_kit.js"]) after three.min.js (prepare_workspace copies it).
// CPU-only rendering (software WebGL) guidance, encoded as defaults:
//  • prefer emissive/material animation and baked canvas textures over many real-time lights;
//  • one shadow-casting light whose frustum follows the shot (shadowFollow), 1024–2048 px maps;
//  • instance anything repeated (racks, trees, fans, tokens); reuse geometries and materials;
//  • particles carry meaning (coolant, money, data, air) and are pure functions of time.
(function (g) {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = (x) => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const lerp = (a, b, t) => a + (b - a) * t;
  const V3 = (a) => new THREE.Vector3(a[0], a[1], a[2]);
  const seed = (a) => () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

  // Keyframed camera: keys = [[t, [px,py,pz], [lx,ly,lz], fov], …]; eased between keys, holds at ends.
  // Start a move ~1 s before the word that names the subject so it is framed when spoken.
  function keyCam(cam, keys, t, offset) {
    let i = 0; while (i < keys.length - 1 && t >= keys[i + 1][0]) i++;
    const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)], f = b === a ? 0 : ease(clamp((t - a[0]) / (b[0] - a[0])));
    cam.position.lerpVectors(V3(a[1]), V3(b[1]), f); const look = new THREE.Vector3().lerpVectors(V3(a[2]), V3(b[2]), f);
    if (offset) { cam.position.add(offset); look.add(offset); }
    if (cam.isPerspectiveCamera && a[3]) { cam.fov = lerp(a[3], b[3] || a[3], f); cam.updateProjectionMatrix(); }
    cam.lookAt(look); cam.updateMatrixWorld(); return look;
  }
  // Procedural canvas texture (brick, panels, louvres, signage…) — detail without downloads.
  function canvasTex(w, h, draw, repeat) {
    const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); } return t;
  }
  // Material library of common surfaces (procedural): 'brick', 'panel', 'louvre', 'concrete', 'asphalt', 'rust', 'wood'.
  const SURF = {
    brick: (g, w, h) => { g.fillStyle = '#9a4e36'; g.fillRect(0, 0, w, h); g.strokeStyle = '#6e3424'; g.lineWidth = 2; for (let y = 0; y < h; y += 16) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); for (let x = (y / 16) % 2 ? 16 : 0; x < w; x += 32) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 16); g.stroke(); } } },
    panel: (g, w, h) => { g.fillStyle = '#c9ced6'; g.fillRect(0, 0, w, h); for (let x = 0; x < w; x += 16) { g.fillStyle = x % 32 ? '#bfc4cc' : '#d3d8e0'; g.fillRect(x, 0, 16, h); } },
    louvre: (g, w, h) => { g.fillStyle = '#5a6270'; g.fillRect(0, 0, w, h); g.fillStyle = '#7a8492'; for (let y = 0; y < h; y += 6) g.fillRect(0, y, w, 3); },
    concrete: (g, w, h) => { const r = seed(3); g.fillStyle = '#8d8a82'; g.fillRect(0, 0, w, h); for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(${90 + r() * 60},${88 + r() * 60},${84 + r() * 60},.35)`; g.fillRect(r() * w, r() * h, 2, 2); } },
    asphalt: (g, w, h) => { const r = seed(5); g.fillStyle = '#3c3a40'; g.fillRect(0, 0, w, h); for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(${70 + r() * 40},${70 + r() * 40},${76 + r() * 40},.4)`; g.fillRect(r() * w, r() * h, 1.5, 1.5); } },
    rust: (g, w, h) => { const r = seed(9); g.fillStyle = '#7a4426'; g.fillRect(0, 0, w, h); for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(${120 + r() * 60},${60 + r() * 30},${30 + r() * 20},.5)`; g.beginPath(); g.arc(r() * w, r() * h, 1 + r() * 4, 0, 7); g.fill(); } },
    wood: (g, w, h) => { const r = seed(4); g.fillStyle = '#7a5230'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(60,36,20,.5)'; for (let y = 0; y < h; y += 4 + r() * 6) { g.beginPath(); g.moveTo(0, y); g.bezierCurveTo(w * .3, y + r() * 4, w * .7, y - r() * 4, w, y); g.stroke(); } },
  };
  function surface(kind, repeat, size) { return canvasTex(size || 256, size || 256, SURF[kind], repeat); }

  // Tokens flowing along a curve (InstancedMesh): position = pure function of time; scale fades in at `on`.
  function flowAlong(mesh, curve, t, o) {
    o = o || {}; const n = mesh.count, m4 = new THREE.Matrix4(), v = new THREE.Vector3(), s = o.on === undefined ? 1 : clamp((t - o.on) / (o.fade || .4));
    for (let j = 0; j < n; j++) { let f = (j / n + t * (o.speed || .2)) % 1; if (o.reverse) f = 1 - f; curve.getPointAt(f, v);
      if (o.lift) v.y += o.lift; m4.makeScale(s, s, s); m4.setPosition(v); mesh.setMatrixAt(j, m4); }
    mesh.instanceMatrix.needsUpdate = true;
  }
  // Deterministic flow field (smooth pseudo-curl) for air/smoke/heat: returns positions for particle i at time t.
  function flowField(i, t, o) {
    o = o || {}; const r = seed(i * 9973 + (o.seed || 1)), x0 = (r() - .5) * (o.w || 10), y0 = r() * (o.h || 4), z0 = (r() - .5) * (o.d || 10), ph = r() * 6.28;
    const life = o.life || 4, a = ((t / life) + r()) % 1, s = (o.speed || 1) * a * life;
    return [x0 + Math.sin(ph + s * .7) * .6 * (o.swirl || 1) + (o.dir ? o.dir[0] * s : 0), y0 + (o.rise || .4) * s + Math.cos(ph + s * .9) * .3, z0 + Math.cos(ph + s * .6) * .6 * (o.swirl || 1) + (o.dir ? o.dir[2] * s : 0), a];
  }
  // One shadow-casting sun whose frustum follows the camera target (crisp shadows in every shot).
  function shadowFollow(sun, target, offset) { sun.target.position.copy(target); sun.position.copy(target).add(offset || new THREE.Vector3(-70, 55, 60)); sun.target.updateMatrixWorld(); }
  g.ELK3D = { keyCam, canvasTex, surface, SURF, flowAlong, flowField, shadowFollow, clamp, ease, lerp, seed };
})(window);
