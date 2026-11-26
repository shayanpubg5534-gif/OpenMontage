# Conversion feasibility: a professional character in our runtime (Snow) — approval gate

Status: experimental. Rig v4 and the production pipeline are untouched; nothing is promoted. All work is in
`epoch-ledger/charlab/convert/` plus small opt-in runtime additions (below). No purchases, paid APIs or subscriptions.
Asset: Blender Studio's Snow, CC-BY; credit "Snow Rig (CC) Blender Foundation | studio.blender.org". Date: 2026-11-26.

**Short answer.** The conversion works. Snow converted automatically (about 1.5 minutes per character plus about 1
minute for the clip set) keeps his designed geometry, anatomy, hair, clothing, eyes and face rig. He runs in our
existing three.js runtime with the existing motion system, gaze, blinks, expressions and lip sync, and the face morphs
come from his own professional face rig. A 6.5-second speaking test renders at 1.46 s per 1080p frame on this CPU
container, the same order as M5. Remaining weaknesses: the eyes read glassier than the original, the runtime has no
skin subsurface scattering, the mocap gesture layer needs a calmer library, and Rain cannot be matured without
re-sculpting.

## 1. What the converter does (`charlab/convert/convert_char.py` + a profile)

| Step | How | Result for Snow |
|---|---|---|
| Geometry | Every render-visible mesh is evaluated at rest with its full modifier stack (mirror, masks, lattices, corrective smooth, surface deform) and one subdivision level, then baked. Quality drivers on subdivision are removed first | 107k polygons, 15 meshes, complete head, body, eyes, teeth, gums, tongue, brows, hair, clothing, shoes |
| Skeleton | A clean deform skeleton with the lab's bone names (`Root`, `pelvis`, `spine_01…`, `upperarm_l…`, `eye_l/eye_r`, fingers) built from the deform bones. Two-segment limbs merged; 200+ face bones folded into `head`; weights merged, normalised, limited to 4 | 54 bones; skin weights preserved |
| Face | The character's own pose library and face controls are posed; the fully deformed face (bones, drivers, shape keys, lattices) is evaluated and the difference from rest is stored as a morph target under the lab's expression names, split left and right | 21 morphs: mouth-open, pursing, protusion, eversion, compression, retraction, corner-puller, depression, open smile, narrow, eye closure L/R, opened-up L/R, inner brows up L/R, brows down L/R, relaxed, cocky, compressed |
| Materials | Each shader is temporarily rewired so its base colour drives an emission shader, then baked (captures metallic irises and subsurface skin correctly); UDIM tiles are laid side by side at full resolution; simple PBR materials replace the originals | 15 baked colour textures |
| Clips | `convert/add_clips.py` reuses our existing retargeting unchanged (idle, sit, talk, listen, walk) plus the finger grip reference | 5 clips, 22 bones each |
| Export | GLB with skin, morph targets and animations | 22.5 MB (24 MB with clips) |

Things that did not survive as-is, and what replaced them (visible result kept, Blender machinery dropped):
- **Cornea refraction and eye-highlight cards** depend on transparency and refraction shaders. Dropped; the iris
  magnification that refraction gives is baked into the eye texture (radial warp around the pupil); the runtime draws
  its own glint.
- **Subsurface scattering** of the skin is baked into the base colour; the runtime has none, so skin reads denser.
- **Bendy (multi-segment) bones** are merged into single bones; limb twist is slightly less smooth.
- **Particle hair** is not used by Snow; his hair is sculpted mesh, which converts fully.

Bugs found and fixed while proving the converter (all automated now): viewport-hidden but rendered meshes skipped
(Snow's eyeballs); UDIM tiles overlapping in a single bake; faces left without a material after merging slots (white
scalp); morph weights exported at 1.0; subdivision overridden by quality drivers; masks broken by over-eager driver
removal; metallic irises baking black; the jaw control (a location channel, not a rotation).

## 2. Static comparison (sheets in `projects/charlab_convert/evidence/`)

`1_native_vs_converted.png`: the same cameras (full body front, three-quarter, profile; close-ups front,
three-quarter, profile) for native Snow in Cycles, the converted GLB in Cycles (isolates conversion losses) and the
converted GLB in our three.js runtime.
- **Anatomy and completeness:** identical. Head, neck and shoulders remain one form in every view; nothing missing.
- **Hair and clothing:** match, including the shaved side and the braided bun.
- **Skin and shading:** colour matches the designed albedo; without subsurface scattering the runtime skin is denser
  and slightly darker under the same light. Cycles adds softness the runtime cannot.
- **Eyes:** irises match in colour and, after the magnification step, in size; they read glassier and starier than the
  original, which has refraction and a placed highlight.

`2_expressions_runtime.png`: ten runtime close-ups driven only by the converted morphs (neutral, smile, speaking "ah",
"oo", "f/v", "m/b/p", worried, angry, blink, open smile). Eyes, brows, cheeks and jaw all take part.

## 3. Animation test (`snow_conversion_test.mp4`, 6.5 s, 1080p30, audio)

In the bank set with the editorial look, entirely through our existing runtime: Snow says "We sold more bread than
ever. So why can't we pay the flour bill?" (Kokoro `am_michael`, Whisper timing, our viseme track) with automatic
blinks, a look at the camera, a glance aside while thinking and back, a nod, worried brows on "can't pay", a shrug, and
an open-hand gesture by IK on "why".
- **Motion analysis:** 0 acceleration spikes in the body; 11 on the gesturing hand (13–14 m/s²) during the IK reach,
  not visible as pops at normal speed.
- **QA:** foot slide 0.01 mm per frame mean (worst 1.8 mm), no floor penetration.
- **What reads well:** the face (speech shapes, brows, eye turns), head and neck coordination, posture.
- **What needs work:** the gesture's palm faces down (a palm-orientation target in the gesture setup, not a conversion
  issue); the first test with the "talk" mocap clip was far too theatrical, so the calmer "listen" clip with restraint
  is used; a proper conversational gesture library is still needed. The eyes look glassy in the editorial light.

## 4. Measured cost

| Item | Value |
|---|---|
| Conversion | 86 s (geometry 2 s, face morphs 7 s, material bake 71 s, export 5 s) + clips 55 s |
| Asset | GLB 22.5 MB (M5 character: 13.4 MB); 214k rendered triangles; 15 textures (66 Mpx, about 350 MB of GPU memory as RGBA with mipmaps) |
| Runtime load / compile | 0.5–0.6 s load; 17 ms performance compile |
| Render, three.js, 1080p, Balanced | 1.46 s per frame median (p95 1.66 s); first frame 5–6 s (shader compile). M5 bakery shot: 1.8 s per frame |
| Native Blender, for reference | Cycles 5–12 s per view at 700 px; EEVEE (software GL) 59–186 s per frame |

Optimisations available: halve the texture resolution per UDIM tile (about 90 MB GPU memory, smaller GLB); a lower
subdivision level for wide shots (LOD).

## 5. Rain: can she become a mature adult professional?

`4_rain_mature_study.png`: using only her own rig controls (lower face 8% longer, cranium 4% smaller, eyes 10%
smaller; no neck change) and styling (no hairband or scarf, recoloured top). She still reads as a young teenager. Her
youth is sculpted into the proportions (large cranium, very large eyes, small nose, round cheeks, short jaw); the
master controls only shift them by a few percent. Making her a mature professional needs anatomical re-sculpting of
the head (and new clothing), which is artist work, or exactly the kind of procedural distortion you ruled out.
Conclusion: Rain is not adaptable automatically. She converts the same way as Snow (24 face shape keys, CloudRig) if a
young character is ever needed.

## 6. Runtime changes (all opt-in; existing characters unaffected)
- `runtime.js`: an actor with `"pbr": true` keeps its baked materials; its gaze midpoint comes from its eye bones.
- `stage.js`: `addCharacter(gltf, id, null)` keeps a converted character's PBR materials.
- `elmotion.js`: bone-based eye aiming when a skeleton has `eye_l`/`eye_r` and no shader eyes; eye rest directions
  captured at construction.
- New viewers/tools: `viewer/studio.html` + `convert/studio_shots.mjs` (runtime studio matching the Blender cameras),
  `convert/glb_to_blend.py`, `convert/add_clips.py`, `convert/rain_mature.py`, profile `convert/profiles/snow.json`.

## 7. Limitations and risks
- **One character.** Snow is a single fixed design (young man, casual clothes). There is still no matching adult
  woman, older characters or period clothing among the free Blender Studio assets; Mikassa and Victor need a login.
- **Eyes** read glassier than the original; a runtime eye shader (cornea highlight, iris depth) is the next step.
- **Skin** lacks subsurface scattering in the runtime; a cheap wrap-lighting term would soften it.
- **Gestures:** the mocap clip set is not documentary-grade; a calm conversational gesture library is needed, and the
  IK gesture targets need palm orientation presets.
- **Look integration:** a professional PBR character in our flat editorial set still shows the environment gap
  recorded earlier.
- **Converter generality:** the profile (bone map, face poses, special materials) is per rig family. Snow-family CloudRig
  characters (Snow, Rain, Storm) share most of it; other rigs need their own profile (about an hour of mapping each).
- **HyperFrames:** the converted character uses the same `loadShot` path as M4/M5, but this milestone did not run a
  full `render.py` render (no expensive renders before approval).

## 8. Recommendation
1. **Adopt the conversion pipeline as the experimental standard** for bringing professionally made, CC-BY characters
   into our runtime: it preserves the craft and keeps our automation (motion, gaze, lip sync, narration-driven
   direction, deterministic rendering).
2. **Next engineering steps (automatable here):** runtime eye shader and skin wrap-lighting; texture LOD (memory);
   a calm conversational gesture library with palm-orientation presets; a HyperFrames render of the test through
   `render.py` to confirm caching and determinism with a converted character.
3. **The cast problem remains.** Conversion solves integration, not design: there is one suitable professional
   character (Snow). A documentary cast (adult women, older people, period clothing) still needs either login-gated
   Blender Studio characters (Mikassa, Victor; your decision) or new characters designed by a human artist, which this
   pipeline can then ingest automatically. Until then, characters should appear only where they serve the story, with
   documents, diagrams, maps and objects carrying the rest (as the direction principle already says).
4. **Environment upgrade** remains a separate, later milestone.

## Reproducibility
```
# 1. convert (Blender 5.3 via the lab's bpy venv)
.runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/convert_char.py epoch-ledger/charlab/convert/profiles/snow.json .runtime/charlab/convert/snow
# 2. clips (existing retargeting) → runtime character folder
M=.runtime/charlab/mocap; .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/add_clips.py \
  .runtime/charlab/convert/snow/snow_cv.glb .runtime/charlab/out_cv/snow_cv.glb --bvh idle=$M/137_28.bvh:18.9:22.4 \
  --bvh sit=$M/113_15.bvh:0.3:7.0 --bvh talk=$M/19_08.bvh:0.4:9.0 --bvh listen=$M/18_08.bvh:2.4:9.6 --bvh walk_start=$M/82_08.bvh:8.0:14.2
# 3. comparisons
node epoch-ledger/charlab/convert/studio_shots.mjs .runtime/charlab/convert/snow/snow_cv.glb .runtime/charlab/bstudio/views/snow/timings.json OUT
# 4. animation test
.venv/bin/python epoch-ledger/charlab/lipsync.py "We sold more bread than ever. So why can't we pay the flour bill?" projects/charlab_convert/dialogue_snow --voice am_michael --speed 1.0
node epoch-ledger/charlab/motion_render.mjs --demo epoch-ledger/charlab/motion/demos/cv_snow_test.json --chars .runtime/charlab/out_cv \
  --three .runtime/charlab/three/r0.186.1 --out FRAMES --quality balanced --analyze --qa
```
