// Character lab (P3): runtime look for converted professional characters (opt-in; MakeHuman characters unaffected).
//
// The conversion bakes colour only, so the runtime has to restore what Blender's shaders did:
//   skin  — wrapped diffuse with a warm scatter term past the light terminator (cheap subsurface approximation),
//           lower specular, a faint sheen for the soft rim of skin;
//   eyes  — a clear-coat cornea that reflects a soft room environment (natural catch-lights, depth over a matte iris),
//           sclera toned down so the eyes stop reading as glassy white marbles;
//   hair  — anisotropic highlight along the strands, sheen, matte base;
//   mouth — moist but not glossy; cloth and shoes stay matte.
// Meshes are classified by name; a per-character override can be passed as opts.kinds { meshName: kind }.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

let ENV = null;
function roomEnv(renderer) {
  if (ENV) return ENV;
  const pm = new THREE.PMREMGenerator(renderer);
  ENV = pm.fromScene(new RoomEnvironment(), .04).texture; pm.dispose();
  return ENV;
}

// eyes reflect a dark room with one soft window panel: a single clean catch-light on the cornea (Blender used a placed card)
let EYE_ENV = null;
function catchEnv(renderer, dir = [-.45, .5, 1]) {
  if (EYE_ENV) return EYE_ENV;
  const sc = new THREE.Scene(); sc.background = new THREE.Color(.015, .014, .013);
  const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.1, .8), new THREE.MeshBasicMaterial({ color: new THREE.Color(9, 8.6, 8), side: THREE.DoubleSide }));
  panel.position.set(...dir).multiplyScalar(3); panel.lookAt(0, 0, 0); sc.add(panel);
  const pm = new THREE.PMREMGenerator(renderer); EYE_ENV = pm.fromScene(sc, 0).texture; pm.dispose();
  return EYE_ENV;
}

export const KIND = n => { n = n.toLowerCase();
  return /eye_?dot|highlight|glint/.test(n) ? 'glint' : /eyebrow|brow/.test(n) ? 'brow' : /eye/.test(n) ? 'eye' : /hair/.test(n) ? 'hair' : /teeth|gum|tongue/.test(n) ? 'mouth'
       : /shoe/.test(n) ? 'shoes' : /shirt|pants|jean|top|jacket|coat|scarf|skirt|dress/.test(n) ? 'cloth' : /head|body|skin/.test(n) ? 'skin' : 'cloth'; };

// skin: replace the diffuse line of the physical direct-light function (three r186) with a wrapped one plus scatter
function skinPatch(mat, wrap, scatter) {
  mat.onBeforeCompile = sh => {
    sh.uniforms.skinWrap = { value: wrap }; sh.uniforms.skinScatter = { value: new THREE.Color(...scatter) };
    const chunk = THREE.ShaderChunk.lights_physical_pars_fragment;
    const line = 'reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution ) * ( 1.0 - F );';
    if (!chunk.includes(line)) { console.warn('charlook: skin patch target not found (three.js version?)'); return; }
    const skin = `{ float nl = dot( geometryNormal, directLight.direction );
      float wNL = saturate( ( nl + skinWrap ) / ( 1.0 + skinWrap ) );
      vec3 sc = skinScatter * saturate( wNL - saturate( nl ) ) * 1.6;
      reflectedLight.directDiffuse += directLight.color * ( wNL + sc ) * BRDF_Lambert( material.diffuseContribution ) * ( 1.0 - F ); }`;
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float skinWrap; uniform vec3 skinScatter;')
      .replace('#include <lights_physical_pars_fragment>', chunk.replace(line, skin));
  };
  mat.customProgramCacheKey = () => 'charlook-skin';
}

export function enhanceCharacter(root, renderer, opts = {}) {
  const env = roomEnv(renderer), report = {};
  root.traverse(o => {
    if (!o.isMesh || !o.material) return;
    const old = o.material, kind = (opts.kinds && opts.kinds[o.name]) || KIND(o.name), map = old.map || null;
    if (map) map.anisotropy = 8;
    let m;
    if (kind === 'skin') {
      m = new THREE.MeshPhysicalMaterial({ map, roughness: .52, specularIntensity: .38, sheen: .22, sheenRoughness: .75,
        sheenColor: new THREE.Color('#f2c3a6'), envMap: env, envMapIntensity: .25 });
      skinPatch(m, opts.wrap ?? .45, opts.scatter ?? [.62, .2, .1]);
    } else if (kind === 'glint') {   // the artist's catch-light cards: unlit, never fogged or tone-mapped into grey
      m = new THREE.MeshBasicMaterial({ color: new THREE.Color(1, 1, 1), toneMapped: false, fog: false });
    } else if (kind === 'eye') {
      m = new THREE.MeshPhysicalMaterial({ map, color: new THREE.Color('#ece6df'), roughness: .6, specularIntensity: .12,
        clearcoat: 1, clearcoatRoughness: .04, envMap: catchEnv(renderer, opts.catchDir), envMapIntensity: .9, side: THREE.DoubleSide });   // the pupil is an opening onto the eyeball interior, seen from behind
    } else if (kind === 'hair' || kind === 'brow') {
      // (no anisotropy: converted meshes carry no tangents, so the strand direction would be arbitrary)
      m = new THREE.MeshPhysicalMaterial({ map, roughness: kind === 'brow' ? .85 : .62, specularIntensity: kind === 'brow' ? .1 : .3,
        sheen: kind === 'brow' ? 0 : .25, sheenRoughness: .45, sheenColor: new THREE.Color('#4a3c30'), envMap: env, envMapIntensity: .12 });
    } else if (kind === 'mouth') {
      m = new THREE.MeshPhysicalMaterial({ map, roughness: .38, specularIntensity: .45, envMap: env, envMapIntensity: .3 });
    } else {
      m = new THREE.MeshPhysicalMaterial({ map, roughness: kind === 'shoes' ? .6 : .82, specularIntensity: .25, sheen: kind === 'cloth' ? .4 : 0,
        sheenRoughness: .8, sheenColor: new THREE.Color('#888888'), envMap: env, envMapIntensity: .2 });
    }
    m.name = old.name + '_charlook'; m.userData.outlineParameters = { visible: false };
    o.material = m; report[o.name] = kind;
  });
  return report;
}
