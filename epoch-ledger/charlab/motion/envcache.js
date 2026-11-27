// Character lab (P4): static environment cache for the cinematic look (opt-in render option `envCache`).
//
// Profiling (P4 report) showed the set costs ~60% of a cinematic frame and is re-rendered every frame although nothing in
// it moves. Here the set is rendered once per camera *anchor* (with an overscan margin) and re-projected per pixel to
// the current camera; only the characters are rendered per frame, depth-tested against it (a desk still hides legs).
//
// Nothing is approximated for a static camera:
//   • shadows on the characters: the key light's real shadow map is composed per frame as min(cached set depth,
//     characters' depth), so characters get the set's shadows and their own self-shadows exactly (PCF maps only)
//   • the characters' shadows on the set: each anchor stores the set with and without the key light; per frame the set
//     is (without key) + (key contribution) × (visibility from the characters' depth map), the same light, removed
//   • anchors are chosen by the caller as a pure function of time (runtime.js), so every frame renders identically
//     whatever was rendered before (HyperFrames chunks, seeks)
// For a moving camera, re-projection is per-pixel exact except where the camera now sees surfaces hidden from the
// anchor (disocclusions at depth edges); the caller bounds this by re-anchoring every few centimetres of travel.
import * as THREE from 'three';

const QUAD_VS = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }';

export function createEnvCache(stage, { env, chars, W, H, pad = 80, grid = [240, 136] }) {
  const { renderer, scene, cam, key } = stage;
  // overscan by whole pixels with the same factor on both axes (pad 80 → 2080×1170 for 1080p): texel centres stay aligned, so a
  // static camera reads the cached layer 1:1 (no resampling blur)
  const overscan = 1 + 2 * pad / W, OW = W + 2 * pad, OH = Math.round(H * overscan);
  const mkEnv = () => new THREE.WebGLRenderTarget(OW, OH, { type: THREE.HalfFloatType, colorSpace: THREE.LinearSRGBColorSpace, depthTexture: new THREE.DepthTexture(OW, OH, THREE.FloatType) });
  const envRT = mkEnv(), noKeyRT = new THREE.WebGLRenderTarget(Math.round(OW / 2), Math.round(OH / 2), { type: THREE.HalfFloatType, colorSpace: THREE.LinearSRGBColorSpace });   // only read under the characters' (soft) shadows: half resolution
  const anchor = cam.clone(); let anchorKey = null;
  const invPV = new THREE.Matrix4(), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const envMeshes = []; env.traverse(o => { if (o.isMesh || o.isLine || o.isPoints) o.isMesh && envMeshes.push(o); });
  const show = (list, v) => list.forEach(o => o.visible = v);
  const stats = { anchors: 0, frames: 0, shadowCompose: false };

  // ── shadows ──────────────────────────────────────────────────────────────────────────────────────────────────────
  let S = null;                       // { size, envRT, charRT } depth targets from the key light (PCF maps)
  const depthMat = new THREE.MeshDepthMaterial();
  const compose = new THREE.ShaderMaterial({ uniforms: { tEnv: { value: null }, tChar: { value: null } }, vertexShader: QUAD_VS,
    fragmentShader: 'uniform sampler2D tEnv, tChar; varying vec2 vUv; void main(){ gl_FragDepth = min(texture2D(tEnv, vUv).x, texture2D(tChar, vUv).x); gl_FragColor = vec4(0.); }',
    depthTest: true, depthFunc: THREE.AlwaysDepth, depthWrite: true, colorWrite: false });   // GL writes depth only with the test enabled
  const quadScene = new THREE.Scene(), quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), compose); quad.frustumCulled = false; quadScene.add(quad);
  function cacheEnvShadow() {          // the set's depth from the key light, rendered once (the light and the set are static)
    const map = key.shadow.map; if (!map || !map.depthTexture) return;
    const size = map.width; S = { size, envRT: new THREE.WebGLRenderTarget(size, size, { depthTexture: new THREE.DepthTexture(size, size, THREE.FloatType) }),
      charRT: new THREE.WebGLRenderTarget(size, size, { depthTexture: new THREE.DepthTexture(size, size, THREE.FloatType) }) };
    const cv = chars.map(o => o.visible), mv = envMeshes.map(o => o.visible); show(chars, false);
    envMeshes.forEach(o => { if (!o.castShadow) o.visible = false; });                              // casters only, as the shadow pass
    scene.overrideMaterial = depthMat; renderer.setRenderTarget(S.envRT); renderer.setClearColor(0xffffff, 1); renderer.clear(); renderer.render(scene, key.shadow.camera);
    scene.overrideMaterial = null; chars.forEach((o, i) => o.visible = cv[i]); envMeshes.forEach((o, i) => o.visible = mv[i]);
    stats.shadowCompose = true;
  }
  function composeShadow() {           // the key light's map = min(set, characters); characters' depth also kept for the set
    if (!S) return null;
    const vis = envMeshes.map(o => o.visible); show(envMeshes, false); scene.overrideMaterial = depthMat;
    renderer.setRenderTarget(S.charRT); renderer.setClearColor(0xffffff, 1); renderer.clear(); renderer.render(scene, key.shadow.camera);
    scene.overrideMaterial = null; envMeshes.forEach((o, i) => o.visible = vis[i]);
    compose.uniforms.tEnv.value = S.envRT.depthTexture; compose.uniforms.tChar.value = S.charRT.depthTexture;
    renderer.setRenderTarget(key.shadow.map); renderer.clearDepth(); quad.material = compose; renderer.render(quadScene, ortho);
    return S.charRT.depthTexture;
  }

  // ── the cached set, re-projected; the key light's share is put back only where the characters don't block it ─────────
  const rp = new THREE.ShaderMaterial({
    uniforms: { tCol: { value: envRT.texture }, tNoKey: { value: noKeyRT.texture }, tDep: { value: envRT.depthTexture }, invPV: { value: invPV },
                curPV: { value: new THREE.Matrix4() }, tSh: { value: null }, shM: { value: new THREE.Matrix4() }, shOn: { value: 0 }, shTexel: { value: 1 / 1024 } },
    vertexShader: `uniform sampler2D tDep; uniform mat4 invPV, curPV; varying vec2 vUv;
      void main() { vUv = uv; float d = texture2D(tDep, uv).x;
        vec4 w = invPV * vec4(uv * 2. - 1., min(d, .99999) * 2. - 1., 1.); w /= w.w; gl_Position = curPV * vec4(w.xyz, 1.); }`,
    fragmentShader: `uniform sampler2D tCol, tNoKey, tDep, tSh; uniform mat4 invPV, curPV, shM; uniform float shOn, shTexel; varying vec2 vUv;
      void main() {
        float d = texture2D(tDep, vUv).x; vec4 w = invPV * vec4(vUv * 2. - 1., min(d, .99999) * 2. - 1., 1.); w /= w.w;
        vec4 c = curPV * vec4(w.xyz, 1.); gl_FragDepth = clamp(c.z / c.w * .5 + .5, 0., 1.);       // per-pixel depth: exact occlusion
        vec4 full = texture2D(tCol, vUv); vec3 col = full.rgb;
        if (shOn > .5) { vec4 s = shM * vec4(w.xyz, 1.); s.xyz /= s.w;
          if (s.x > 0. && s.x < 1. && s.y > 0. && s.y < 1. && s.z < 1.) { float v = 0.;          // 3×3 PCF, as soft as the map's own
            for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) v += step(s.z - .0012, texture2D(tSh, s.xy + vec2(i, j) * shTexel).x);
            vec3 nk = texture2D(tNoKey, vUv).rgb; col = nk + (col - nk) * v / 9.; } }
        gl_FragColor = vec4(col, full.a); }`,
    depthTest: true, depthWrite: true });
  const rpScene = new THREE.Scene(), rpMesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2, grid[0], grid[1]), rp); rpMesh.frustumCulled = false; rpScene.add(rpMesh);

  function buildAnchor(acam) {
    anchor.copy(acam); anchor.fov = THREE.MathUtils.radToDeg(2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(acam.fov) / 2) * overscan));
    anchor.aspect = OW / OH; anchor.updateProjectionMatrix(); anchor.updateMatrixWorld();
    invPV.copy(anchor.matrixWorld).multiply(anchor.projectionMatrixInverse);
    const cv = chars.map(o => o.visible); show(chars, false);
    const pcf = renderer.shadowMap.type === THREE.PCFShadowMap || renderer.shadowMap.type === THREE.PCFSoftShadowMap;
    renderer.shadowMap.autoUpdate = false; if (!S || !pcf) renderer.shadowMap.needsUpdate = true;    // set-only shadow map
    if (S && pcf) {   // after the first anchor the key light's map holds min(set, characters at the PREVIOUS frame): restore the set-only
      compose.uniforms.tEnv.value = S.envRT.depthTexture; compose.uniforms.tChar.value = S.envRT.depthTexture;   // depth, or that frame's
      renderer.setRenderTarget(key.shadow.map); renderer.clearDepth(); quad.material = compose; renderer.render(quadScene, ortho); }   // character shadow is baked into the cache (history-dependent)
    renderer.setRenderTarget(envRT); renderer.setClearColor(0, 0); renderer.clear(); renderer.render(scene, anchor);
    if (pcf && !S) cacheEnvShadow();
    const ki = key.intensity; key.intensity = 0;                                                   // the set without the key light
    renderer.setRenderTarget(noKeyRT); renderer.clear(); renderer.render(scene, anchor); key.intensity = ki;
    chars.forEach((o, i) => o.visible = cv[i]); stats.anchors++;
  }
  // render the frame's colour + depth into rt (the stage's main target); acam: this frame's anchor camera, akey: its id
  function render(rt, acam, akey) {
    const P = stage.prof, gl = renderer.getContext(); let t0 = P ? (gl.finish(), performance.now()) : 0;
    const tick = k => { if (!P) return; gl.finish(); const t = performance.now(); P[k] = (P[k] || 0) + t - t0; t0 = t; };   // opt-in profiling
    if (akey !== anchorKey) { buildAnchor(acam); anchorKey = akey; }
    tick('ec_anchor');
    const charDepth = composeShadow();
    tick('ec_shadow');
    rp.uniforms.shOn.value = charDepth ? 1 : 0;
    if (charDepth) { rp.uniforms.tSh.value = charDepth; rp.uniforms.shM.value.copy(key.shadow.matrix); rp.uniforms.shTexel.value = 1 / S.size; }
    cam.updateMatrixWorld(); rp.uniforms.curPV.value.copy(cam.projectionMatrix).multiply(cam.matrixWorldInverse);
    renderer.setRenderTarget(rt); renderer.setClearColor(0, 0); renderer.clear(); renderer.render(rpScene, cam);
    tick('ec_reproject');
    const vis = envMeshes.map(o => o.visible); show(envMeshes, false);
    const ac = renderer.autoClear; renderer.autoClear = false; renderer.render(scene, cam); renderer.autoClear = ac;
    envMeshes.forEach((o, i) => o.visible = vis[i]); stats.frames++;
    tick('ec_chars');
  }
  return { render, stats, envRT, invalidate: () => { anchorKey = null; S = null; } };
}
