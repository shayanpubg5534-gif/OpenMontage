// Character lab (M3): the M2.3c flat editorial renderer, packaged as a module for animated shots.
// Same shading, ink, set light rigs, plate, grade and paper grain as viewer/lookdev3.html (which stays unchanged),
// plus: props with flat colours and ink, eye rotation (a pivot in the vertex shader, so the 53-bone rig is unchanged),
// and quality switches (msaa, shadow-map size, interior ink) per render.
import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';

export const ENV = {
  bakery: { plate: '/projects/profitable-and-broke/hyperframes/plates/shop-bg-6302a081a386.png', sky: '#fff0da', ground: '#6b5a48', hemi: 1.15,
            key: '#ffd7a2', keyI: 2.5, keyPos: [2.2, 4.2, 3.0], fill: '#b8cfff', fillI: .45, fillPos: [-3, 2, 1.5],
            shadow: '#3a2414', shadowA: .30, ink: '#2b1d16', grade: [1.03, 1.0, .95] },
  bank:   { plate: '/projects/profitable-and-broke/hyperframes/plates/bank-bg-b758bcbed821.png', sky: '#e8eefa', ground: '#6f7686', hemi: 1.2,
            key: '#fff3e4', keyI: 2.3, keyPos: [-2.6, 4.0, 3.0], fill: '#ffd3a6', fillI: .45, fillPos: [3, 2, 1.0],
            shadow: '#1f2633', shadowA: .28, ink: '#1e2330', grade: [.98, 1.0, 1.03] } };

const kindOf = n => { n = n.toLowerCase();
  if (/m23c_hair/.test(n)) return 'ghair'; if (/m23c_brows|m23c_lashline/.test(n)) return 'gline';
  return /eyebrow/.test(n) ? 'brow' : /eyelash/.test(n) ? 'lash' : /high-poly|low-poly/.test(n) ? 'eye' : /teeth|tongue/.test(n) ? 'mouth'
       : /bob|hair|long0|short0|ponytail|braid|afro/.test(n) ? 'hair' : /shoes/.test(n) ? 'shoes' : /suit|fedora|dress|shirt/.test(n) ? 'cloth' : 'skin'; };
const TINTS = { skin: { sh: '#dcb4a4', li: '#fff6ef' }, cloth: { sh: '#9ea7c4', li: '#fff8f0' }, shoes: { sh: '#8a90a8', li: '#ffffff' },
  ghair: { sh: '#9a8c96', li: '#fff2e4' }, mouth: { sh: '#c49a96', li: '#fff4ee' }, prop: { sh: '#a7a0b4', li: '#fff8f0' } };

export async function createStage({ env: envName = 'bank', W = 1920, H = 1080, clothInflate = .004, canvas = null } = {}) {
  const env = ENV[envName];
  const renderer = new THREE.WebGLRenderer({ canvas: canvas || undefined, antialias: false, preserveDrawingBuffer: true, alpha: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H, !canvas); renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  if (!canvas) document.body.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const hemi = new THREE.HemisphereLight(env.sky, env.ground, env.hemi); scene.add(hemi);
  const key = new THREE.DirectionalLight(env.key, env.keyI); key.position.set(...env.keyPos); key.castShadow = true;
  key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
  Object.assign(key.shadow.camera, { left: -4, right: 4, top: 3, bottom: -1.5, near: .1, far: 16 }); scene.add(key);
  const fill = new THREE.DirectionalLight(env.fill, env.fillI); fill.position.set(...env.fillPos); scene.add(fill);
  const catcher = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.ShadowMaterial({ color: env.shadow, opacity: env.shadowA }));
  catcher.rotation.x = -Math.PI / 2; catcher.receiveShadow = true; scene.add(catcher);
  const ink = new THREE.Color(env.ink), inkA = ink.toArray();
  const keyView = { value: new THREE.Vector3() };

  function shade(mat, kind) {
    const t = TINTS[kind] || TINTS.cloth, sh = new THREE.Color(t.sh), li = new THREE.Color(t.li);
    mat.onBeforeCompile = s => {
      Object.assign(s.uniforms, { tSh: { value: sh }, tLi: { value: li }, rimK: { value: kind === 'skin' ? .28 : .14 } });
      s.uniforms.keyV = keyView;
      s.fragmentShader = 'uniform vec3 tSh, tLi, keyV; uniform float rimK;\n' + s.fragmentShader.replace('#include <opaque_fragment>', `{
        vec3 alb = max(diffuseColor.rgb, vec3(1e-3));
        float L = dot(outgoingLight, vec3(.299, .587, .114)) / dot(alb, vec3(.299, .587, .114));
        float b1 = smoothstep(${kind === 'skin' ? '.34' : '.48'} - .025, ${kind === 'skin' ? '.34' : '.48'} + .025, L);
        vec3 c = mix(alb * tSh, alb * tLi, b1);
        vec3 N = normalize(normal), V = normalize(vViewPosition);
        float rim = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 3.0);
        c += vec3(1.0, .86, .7) * rim * rimK * alb * step(.4, L);
        ${kind === 'ghair' ? `vec3 Hh = normalize(normalize(keyV) + V); float hd = dot(N, Hh);
          float band = smoothstep(.86, .89, hd) * (1. - smoothstep(.95, .965, hd)) * step(.45, L);
          c = mix(c, alb * 1.75 + vec3(.012, .009, .008), band * .85);` : ''}
        outgoingLight = c; }
        #include <opaque_fragment>`); };
    mat.customProgramCacheKey = () => 'm3-' + kind;
  }
  const heavy = .0032;
  const outline = (mat, kind) => { mat.userData.outlineParameters = { thickness: ['skin', 'cloth', 'shoes', 'prop'].includes(kind) ? heavy : kind === 'ghair' ? heavy * .75 : 0,
    color: inkA, alpha: 1, visible: ['skin', 'cloth', 'shoes', 'ghair', 'prop'].includes(kind) }; };

  // ── characters ────────────────────────────────────────────────────────────────────────────────────────────────
  const texLoader = new THREE.TextureLoader();
  const cast = [];
  async function addCharacter(gltf, id, texDir) {
    const tr = await (await fetch(`${texDir}/treatments.json`)).json();
    const c = { id, root: gltf.scene, gltf, meshes: [], eyeMeshes: [] };
    gltf.scene.traverse(o => { if (o.isMesh) c.meshes.push(o); });
    for (const m of c.meshes) {
      const o = m.material, kind = kindOf(m.name), name = o.map && o.map.name;
      const entry = Object.entries(tr).find(([k]) => name && (name === k.replace('.png', '') || name.startsWith(k.replace('.png', ''))));
      let map = o.map;
      if (entry && entry[1].flat) { map = await texLoader.loadAsync(`${texDir}/${entry[1].flat}`); map.colorSpace = THREE.SRGBColorSpace; map.flipY = false; map.anisotropy = 4; }
      m.userData.kind = kind; m.frustumCulled = false;
      let mat;
      if (kind === 'gline') { mat = new THREE.MeshBasicMaterial({ color: o.color.clone().lerp(ink, m.name.includes('lower') ? 0 : .25), side: THREE.DoubleSide }); mat.userData.outlineParameters = { visible: false }; }
      else if (kind === 'eye') {
        mat = new THREE.MeshBasicMaterial({ map, alphaTest: .5, color: new THREE.Color('#f4ece6') });
        const U = { eyeL: { value: new THREE.Matrix3() }, eyeR: { value: new THREE.Matrix3() }, pivL: { value: new THREE.Vector3() }, pivR: { value: new THREE.Vector3() }, midX: { value: 0 } };
        m.userData.eyeU = U; c.eyeMeshes.push(m);
        mat.onBeforeCompile = s => { Object.assign(s.uniforms, U);
          s.vertexShader = 'uniform mat3 eyeL, eyeR; uniform vec3 pivL, pivR; uniform float midX;\nvarying vec3 vNv;\n' + s.vertexShader
            .replace('#include <begin_vertex>', `#include <begin_vertex>
              bool isL = position.x > midX;
              transformed = isL ? eyeL * (transformed - pivL) + pivL : eyeR * (transformed - pivR) + pivR;
              vec3 eyeN = isL ? eyeL * normal : eyeR * normal;`)
            .replace('#include <project_vertex>', '#include <project_vertex>\nvNv = normalize(normalMatrix * eyeN);');
          s.fragmentShader = s.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vNv;').replace('#include <opaque_fragment>',
            `float cl = smoothstep(.975, .99, dot(normalize(vNv), normalize(vec3(-.32, .42, 1.))));
             outgoingLight = mix(outgoingLight, vec3(1.), cl * .95);\n#include <opaque_fragment>`); };
        mat.customProgramCacheKey = () => 'm3-eye';
        mat.userData.outlineParameters = { visible: false };
        // pivots: the two eyeball centres in bind (object) space
        const p = m.geometry.attributes.position, sL = new THREE.Vector3(), sR = new THREE.Vector3(); let nL = 0, nR = 0;
        for (let i = 0; i < p.count; i++) { const x = p.getX(i); if (x > 0) { sL.x += x; sL.y += p.getY(i); sL.z += p.getZ(i); nL++; } else { sR.x += x; sR.y += p.getY(i); sR.z += p.getZ(i); nR++; } }
        U.pivL.value.copy(sL.multiplyScalar(1 / nL)); U.pivR.value.copy(sR.multiplyScalar(1 / nR));
        // the eyeball centre is behind the visible surface: move the pivot back by the eyeball radius estimate
        let rL = 0; for (let i = 0; i < p.count; i++) if (p.getX(i) > 0) rL = Math.max(rL, new THREE.Vector3(p.getX(i), p.getY(i), p.getZ(i)).distanceTo(U.pivL.value));
        m.userData.eyeRadius = rL;
      } else {
        mat = new THREE.MeshLambertMaterial({ map: kind === 'ghair' ? null : map, color: kind === 'ghair' ? o.color.clone() : new THREE.Color('#ffffff') });
        shade(mat, kind); outline(mat, kind);
        // clothing over skin (M3): cloth is pushed out along its skinned normal by a few millimetres, and the skin is
        // drawn with a small depth bias, so shallow skin-through-cloth contacts in bent poses stay hidden
        if (kind === 'cloth') { const prev = mat.onBeforeCompile; mat.onBeforeCompile = sh => { prev(sh);
          sh.vertexShader = sh.vertexShader.replace('#include <skinning_vertex>', '#include <skinning_vertex>\n transformed += normalize(objectNormal) * ' + (clothInflate).toFixed(4) + ';'); }; }
        if (kind === 'skin') { mat.polygonOffset = true; mat.polygonOffsetFactor = 1; mat.polygonOffsetUnits = 6; }
      }
      m.castShadow = !['gline', 'eye'].includes(kind); m.receiveShadow = ['skin', 'cloth', 'shoes'].includes(kind);
      m.material = mat;
    }
    scene.add(gltf.scene); cast.push(c); return c;
  }

  // ── props: flat-coloured, inked, shadow-casting ───────────────────────────────────────────────────────────────
  // a set may warm or cool its own shadow colour (M4.1); call before the set's materials are made
  function setPropTint(sh, li) { if (sh) TINTS.prop.sh = sh; if (li) TINTS.prop.li = li; }
  function propMaterial(color) { const m = new THREE.MeshLambertMaterial({ color: new THREE.Color(color) }); shade(m, 'prop'); outline(m, 'prop'); return m; }
  function box(w, h, d, color) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), propMaterial(color)); m.castShadow = m.receiveShadow = true; return m; }
  function addProp(obj) { obj.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } }); scene.add(obj); return obj; }

  // ── post: character + prop pass over the plate (as lookdev3) ──────────────────────────────────────────────────
  const outlineFx = new OutlineEffect(renderer);
  const mkRT = samples => new THREE.WebGLRenderTarget(W, H, { samples, colorSpace: THREE.SRGBColorSpace });
  const rts = { 4: mkRT(4), 2: mkRT(2), 0: mkRT(0) }, rtN = new THREE.WebGLRenderTarget(W, H), normalMat = new THREE.MeshNormalMaterial();
  const plateTex = await texLoader.loadAsync(env.plate); plateTex.colorSpace = THREE.SRGBColorSpace;
  const post = new THREE.ShaderMaterial({
    uniforms: { tChar: { value: null }, tNorm: { value: rtN.texture }, tPlate: { value: plateTex }, inkOn: { value: 1 }, inkCol: { value: ink.clone() },
                res: { value: new THREE.Vector2(W, H) }, blur: { value: 0 }, grade: { value: new THREE.Vector3(...env.grade) } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
    fragmentShader: `varying vec2 vUv; uniform sampler2D tChar, tNorm, tPlate; uniform float inkOn, blur; uniform vec3 inkCol, grade; uniform vec2 res;
      float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float noise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
        return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
      vec3 plate(vec2 uv){ if (blur < .5) return texture2D(tPlate, uv).rgb;
        vec3 c = vec3(0.); for (int j = -3; j <= 3; j++) for (int i = -3; i <= 3; i++) c += texture2D(tPlate, uv + vec2(float(i), float(j)) * blur / res).rgb; return c / 49.; }
      void main(){ vec4 ch = texture2D(tChar, vUv); vec3 col = ch.rgb;
        if (inkOn > .5) { vec2 px = 1. / res;
          vec3 a = texture2D(tNorm, vUv + vec2(-1,-1)*px).rgb, b = texture2D(tNorm, vUv + vec2(0,-1)*px).rgb, c = texture2D(tNorm, vUv + vec2(1,-1)*px).rgb;
          vec3 d = texture2D(tNorm, vUv + vec2(-1,0)*px).rgb, f = texture2D(tNorm, vUv + vec2(1,0)*px).rgb;
          vec3 g = texture2D(tNorm, vUv + vec2(-1,1)*px).rgb, h = texture2D(tNorm, vUv + vec2(0,1)*px).rgb, i = texture2D(tNorm, vUv + vec2(1,1)*px).rgb;
          vec3 gx = (c + 2.*f + i) - (a + 2.*d + g), gy = (g + 2.*h + i) - (a + 2.*b + c);
          float e = sqrt(dot(gx, gx) + dot(gy, gy)); col = mix(col, inkCol, smoothstep(.7, 1.3, e) * .6 * step(.5, ch.a)); }
        col *= grade; vec3 o = mix(plate(vUv), col, ch.a);
        o *= .975 + .025 * noise(vUv * res / 1.5 + 7.);
        gl_FragColor = vec4(o, 1.);
        #include <colorspace_fragment>
      }` });
  const postScene = new THREE.Scene(), postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post));
  const cam = new THREE.PerspectiveCamera(30, W / H, .05, 60);

  function render({ msaa = 4, shadow = 2048, inkPass = true, blur = 0 } = {}) {
    if (key.shadow.mapSize.x !== shadow) { key.shadow.mapSize.set(shadow, shadow); if (key.shadow.map) { key.shadow.map.dispose(); key.shadow.map = null; } }
    cam.updateMatrixWorld(); keyView.value.copy(key.position).applyMatrix3(new THREE.Matrix3().setFromMatrix4(cam.matrixWorldInverse)).normalize();
    const rt = rts[msaa] || rts[4];
    renderer.setRenderTarget(rt); renderer.setClearColor(0, 0); renderer.clear(); outlineFx.render(scene, cam);
    const catcherOn = catcher.visible;
    if (inkPass) { renderer.setRenderTarget(rtN); renderer.setClearColor(0x8080ff, 1); renderer.clear(); catcher.visible = false;
      const hid = []; scene.traverse(m => { if (m.isMesh && ['gline', 'eye', 'backdrop'].includes(m.userData.kind)) { m.visible = false; hid.push(m); } });
      scene.overrideMaterial = normalMat; renderer.render(scene, cam); scene.overrideMaterial = null; hid.forEach(m => m.visible = true); catcher.visible = catcherOn; }
    renderer.setRenderTarget(null);
    post.uniforms.tChar.value = rt.texture; post.uniforms.inkOn.value = inkPass ? 1 : 0; post.uniforms.blur.value = blur;
    renderer.render(postScene, postCam);
  }
  // a full 3D set (M4.1) brings its own floor and light rig: the shadow catcher is hidden and the lights follow the spec
  function setLights(L = {}) {
    catcher.visible = false;
    if (L.hemi) { hemi.color.set(L.hemi.sky); hemi.groundColor.set(L.hemi.ground); hemi.intensity = L.hemi.i; }
    if (L.key) { key.color.set(L.key.color); key.intensity = L.key.i; key.position.set(...L.key.pos); if (L.key.target) key.target.position.set(...L.key.target); key.target.updateMatrixWorld(); }
    if (L.fill) { fill.color.set(L.fill.color); fill.intensity = L.fill.i; fill.position.set(...L.fill.pos); }
    if (L.shadow) Object.assign(key.shadow.camera, L.shadow); key.shadow.camera.updateProjectionMatrix();
    if (L.ink) post.uniforms.inkCol.value.set(L.ink);
    if (L.grade) post.uniforms.grade.value.set(...L.grade);
  }
  return { THREE, renderer, scene, cam, env, cast, addCharacter, addProp, box, propMaterial, render, setLights, setPropTint, key, fill, hemi };
}
