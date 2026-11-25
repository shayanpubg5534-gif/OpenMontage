# Hybrid illustrated animation architecture: investigation and recommendation

Status: proposal, awaiting approval. Nothing here is implemented in the production kit yet.
Date: 2026-11-25.

## 1. Why change

BigCart (Rig v3/v4) and *Profitable and Broke* (Rig v4) are kept as development references. The failures you
identified are structural, not tuning problems:

| Failure | Root cause in the current architecture |
|---|---|
| Hands disappear behind props; no convincing grip | Characters are flat SVG drawn per frame. A prop is a separate SVG placed near the wrist; nothing models fingers closing around it, and there is no depth between the hand and the prop. |
| Unnatural arms, elbows and shoulders during interactions | A hand-written 2-bone IK with drawn tubes. No joint limits, no shoulder or clavicle motion, no anatomical skinning. |
| Awkward folder posture; floating crate | Props follow a computed wrist point through a screen-space "bridge" that crosses layers. Contact is approximate by construction. |
| Simplistic proportions, faces, hands, clothing | Every shape is procedural code. Detail costs code, and the result stays geometric. |
| Flat, inactive environments | Static cached plates. Parallax gives depth cues, but nothing in the world moves. |
| Too many wide shots | The 2.5D sprites hold up only near one camera distance. Close-ups expose the geometry, and true over-the-shoulder shots need real 3D occlusion. |

Another iteration of the geometric rig would raise the ceiling slowly, without removing these root causes.

## 2. Options investigated

All options keep the parts that work: narration, gold captions, financial diagrams (SVG/GSAP), sound, scene cache and
`render.py --isolate`.

| | A. Procedural SVG rig (Rig v4) | B. Layered illustrated 2D cut-out + mesh deformation | C. 2D skeletal tools (Synfig / OpenToonz) | D. Hybrid: skinned 3D characters, illustrated (toon) presentation | E. Local AI image/video generation |
|---|---|---|---|---|---|
| Look | Geometric, simplistic | Closest to hand-illustrated, but only with professional art | Depends entirely on the art | Cel-shaded "illustrated 3D". Quality depends on the models | Unpredictable |
| Anatomy and limbs | Drawn tubes; seams hidden by tricks | Mesh deformation bends limbs, but each view is separate art | Bone deformation, same art limits | Skinned meshes: connected by construction, real joints | Inconsistent between frames |
| Object contact and grip | Approximate (wrist point) | Attachment slots per bone; still 2D layering | Similar to B | Props parented to hand bones; finger poses; IK to targets | Not controllable |
| Occlusion | Clip-line tricks | Manual draw order per pose | Manual | Depth buffer: correct for any camera | n/a |
| Turning and shot sizes | One model, many views, geometric | One art set per view; turns are cuts | Same | Any angle, close-up to wide, over-the-shoulder | n/a |
| Automation from Python | Very high | Medium (rig authoring is manual, in a GUI) | Medium (Synfig XML) / low (OpenToonz) | High: clips, IK, cameras and props all scriptable; deterministic | Low |
| Free and local | Yes | Runtimes yes (pixi.js MIT; DragonBones runtime MIT). The editor (DragonBones Pro) is unmaintained freeware for Windows/macOS. Spine and Live2D are excluded (paid licences) | GPL / BSD, but neither is installable from this environment's package sources | three.js MIT; Blender GPL (headless `bpy` wheel available); CC0 characters and animations | Open weights exist, but CPU-only generation is impractical (minutes per image; video infeasible) |
| CPU performance | 0.2–0.4 s/frame (measured) | Fast (2D WebGL) | Offline, fast | **0.17 s/frame measured** for a test scene with shadows and outlines; estimated 0.3–0.6 s for rich scenes | Impractical |
| Fit with OpenMontage | Native | New runtime layer inside HyperFrames | External renderer; alpha-video compositing | **Native**: a WebGL layer inside HyperFrames, as the documentary's 3D worlds already are | Poor |
| Biggest risk | Quality ceiling reached | Needs a professional illustrator per character and view | Same as B, plus integration | Characters look "3D game", not premium illustration, unless the models and shading are well made | Quality and consistency |

## 3. Evidence gathered (feasibility test, `experiments/hybrid_spike/`)

Measured on this container (4 CPUs, no GPU), headless Chromium, three.js r160:

- **WebGL runs on the CPU.** The SwiftShader driver is in use.
- **Speed:** 168 ms per 1080p frame including soft shadows, ink outlines and PNG readback. The current pipeline
  takes 0.22–0.38 s per frame.
- **Deterministic:** the same time gives identical pixels from different seek histories (`AnimationMixer.setTime`).
  This is the property our cache, `--isolate` and `qc.mjs` depend on.
- **Occlusion:** a table hides a character's lower body through the depth buffer, with no clip lines.
- **Attachment:** a prop parented to the hand bone stays locked to the hand across six consecutive walk frames,
  casts a shadow and is occluded by the leg. The fingers did not close on it, because the test model has no finger
  poses; that is an asset requirement.
- **Shots:** wide, medium and close-up framings are just camera placements.

**Not demonstrated:** professional character quality. The test used a CC0 robot and a Khronos sample figure with a
placeholder texture. Section 5 makes the art pipeline the first gate.

## 4. Recommended architecture: option D, the hybrid

```
narration (Kokoro) ─ words ─┐
                            ▼
financial model (Python) ── one source of truth for every figure; daily cash simulation; validators
        │                          │
        ▼                          ▼
SVG/GSAP diagrams, captions     shot script (Python): cameras, character actions, props, contacts, timed to words
        │                          │
        │               three.js layer inside HyperFrames (deterministic, seeked by the master timeline)
        │                 ├─ characters: glTF, standard humanoid rig + fingers + face shape keys, toon materials, ink outlines
        │                 ├─ motion: retargeted clips (walk, sit, stand, gesture, type, carry) + procedural IK for contact
        │                 ├─ props: grip sockets on hand bones; pick-up / hand-off / place as reparenting events
        │                 └─ sets: CC0 3D kits + our own models; animated extras and props; real lights and shadows
        ▼                          ▼
             composited in HyperFrames → render.py --isolate → qc.mjs + interaction QA → MP4
```

**Characters.** Each character is a glTF on one standard humanoid rig: spine, clavicles, 2-bone limbs, all five
fingers, and face shape keys (blink, brows, smile, mouth shapes for scenes where they speak). Sources, in order
of preference:
1. **MakeHuman / MPFB2 inside Blender.** The program is AGPL/GPL, but the models it exports are CC0. It gives
   natural, varied adult proportions and faces, with clothing assets. It can be scripted through `bpy`, so the cast
   is generated and versioned as code, keeping identity consistent.
2. **Quaternius CC0 humanoid packs** (animated, 24 clips). These are stylised and lower-poly, and are fine for
   background extras. They download from Google Drive, which needs one manual download.
3. **Commissioned character models** later, if you want a signature look. They would drop into the same rig.

**Look.** Toon (cel) shading with three flat bands and ink outlines, in the series palette. This keeps the
established full-colour illustrated identity better than realistic 3D. It *will* look different from the current
flat SVG characters, so it must be approved on a style frame.

**Motion.** Retargeted clips give the body mechanics: weight, gait and sitting. CC0 or free sources include the
Quaternius animation library and the CMU motion-capture database. Mixamo is free, but needs an Adobe account;
that's your decision. A procedural layer adds what clips can't: reach to a target with joint limits, look-at,
finger grip poses and contact holds. Hand-offs become a parenting event at a frame where both hands' grip sockets
coincide. This removes floating props by construction.

**Environments.** three.js sets built from CC0 kits (Poly Haven, Quaternius, ambientCG) plus our own models.
Background life comes from looping extras (customers, staff, traffic outside the window) and functional props (an
oven glow, a till, a printer). Lights and shadows are consistent because they are real.

**Cameras.** Shot grammar presets (wide, medium, close-up, over-the-shoulder, insert), with motivated moves.
Depth of field through a CPU post-process only where needed. It is expensive, so it will be measured before use.

**Unchanged:** financial diagrams, captions, narration, sound, `render.py --isolate`, the cache, `qc.mjs`.

## 5. Quality gates (made permanent)

1. **Financial model validator.** Every figure on screen comes from one Python cash-flow simulation (daily, with
   recurring revenue and costs, payment terms, financing cost). The validator checks:
   - every chart value has a visible label at the moment it is shown;
   - bar and line geometry is proportional to its values;
   - a *funding gap* (unpaid obligations) is never drawn as a negative bank balance unless the scenario includes
     an overdraft;
   - recurring examples include the expenses that recur during the payment delay, or the narration says it is a
     single order;
   - financing costs are shown when a loan appears.
2. **Diagram layout lint.** All diagram text is registered with `layout_check` automatically. *Profitable and
   Broke*'s overlapping timeline markers escaped it because diagram text was not marked readable.
3. **Interaction QA.** Every contact event (grip, hand-off, place, sit) records its sockets. The automated check
   measures hand-to-socket distance and penetration every frame and fails above tolerance. The render step also
   exports contact sheets of consecutive frames (−5…+10 frames) around every interaction, plus 1-in-30 frame
   samples. These go into a review page, and a human visual check is part of approval.
4. **Existing gates stay:** determinism, frame scan (black, flash, freeze, jumps), loudness, caption-band and
   cropping checks.

## 6. Capacity estimate (unmeasured beyond the test scene; to be confirmed in the pilot)

- 10-minute episode = 18,000 frames. At 0.3–0.6 s/frame with two parallel jobs on 4 CPUs, that is about
  1.5–3 h of rendering, so 2–3 episodes a week is feasible on render time.
- **The real limit is authoring time:** the cast, sets, and a reusable motion and interaction library. Once those
  exist, episodes reuse them. The plan front-loads them.

## 7. Proposed next step (after approval)

A two-week pilot with a go/no-go review. No full-video renders.
1. **Cast:** generate two characters with MPFB2 (CC0) via `bpy`, rig them with fingers and face shape keys, and
   apply toon materials.
2. **Library:** retarget walk, sit, stand, gesture and carry clips. Build reach / grip / hand-off / place with
   sockets.
3. **Style frames:** one bakery-like set with background activity, in four shot sizes, for your style approval.
4. **Interaction test:** a 10–12 s test covering a hand-off, picking up and carrying a box, sitting at a desk and
   a close-up reaction. Rendered with `--isolate`, plus the consecutive-frame contact sheets.
5. **Measurements and report:** CPU time per frame, automation effort per character, and the remaining
   limitations, before any episode work.
