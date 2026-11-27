# P4 — Mature character standards, cinematic quality and CPU rendering optimisation (approval gate)

**Status:** experimental and opt-in. Nothing is promoted.
- Rig v4, production defaults and the production pipeline (`render.py`, HyperFrames) are untouched.
- No purchases, no accounts, no animation render.
- Every P3 capability is preserved: conversion pipeline, eyes, skin, half-size textures, performance library, seated
  poses, gaze, blinks, expressions, lip sync.
- **Regression:** current code vs the P3 commit (`30dd38c`) gives max pixel difference 0 for M4 (cel look), M5
  (editorial look) and the P3 cinematic shot.

Snow appears only as a technical test character. Date: 2026-11-27.

**Evidence** (full-resolution files in `projects/charlab_p4/`; compressed copies in `charlab/evidence/p4_*.jpg`):

| # | File | Content |
|---|---|---|
| 1 | `1_profiles.png` | Quality profiles on identical frames, with measured ms/frame and PSNR |
| 2 | `2_look.png` | P3 vs P4 look (Cinematic and Balanced), label and credit |
| 5 | `5_candidates.png` | Character candidates against the new standard |

Profiling data: `projects/charlab_p4/profile/*.json`, `profiles*/profiles.json`, `bench/`.

## 1. Profiling: where a cinematic frame's CPU time goes
**Setup:** this container has 4 CPU cores and no GPU. Chrome renders WebGL through SwiftShader, a multi-threaded CPU
rasteriser. Tools: `bench/profile.mjs` toggles one feature at a time on identical frames; `bench/profile_seq.mjs`
renders consecutive frames per quality profile.

**P3 Balanced frame:** 2.7–2.9 s at 1080p. Removing each feature saves, in seconds (wide / medium / close):

| Feature removed | Saving (s) | Note |
|---|---|---|
| **The whole static environment** | **1.81 / 1.75 / 1.55** | The set is about 60% of every frame and does not move |
| **Image-based room light (env map)** | **0.98 / 0.90 / 0.86** | Sampled on every PBR surface |
| Set textures (colour, roughness, normal) | 0.79 / 0.63 / 0.58 | |
| The character | 0.67 / 0.65 / 0.86 | |
| Separate depth pass (for AO/DOF) | 0.63 / 0.57 / 0.64 | A second full scene render, including a second shadow render |
| Shadow-map updates (frozen map) | 0.66 / 0.56 / 0.73 | The maps were rendered twice per frame |
| Sky area light | 0.41 / 0.42 / 0.47 | |
| Practical lamps / spot key | 0.31–0.37 / 0.13–0.37 | |
| AO / DOF / haze | 0.07–0.29 / 0.22–0.38 / 0.01–0.19 | |
| PCF instead of VSM shadows | 0.28–0.40 | |

Adding cost instead (s per frame):

| Change | Extra cost (s) |
|---|---|
| 4× MSAA | +1.5–1.7 |
| 2048 shadow map | +0.8–1.0 |

Other costs:
- Frame capture: PNG encode 57–69 ms in the page, 167 ms including readback to disk.
- Geometry and textures are not the bottleneck by themselves; per-pixel shading of the static set is.

**HyperFrames overhead (the largest single finding):**

| Measurement | Result |
|---|---|
| P3 test through `render.py` | 1,690 s for 411 frames (4.1 s per frame wall) |
| Same frames in one lab session | about 2.7 s per frame |
| 3-second benchmark through `render.py`, P4 Balanced | 341 s for 90 frames (3.8 s per frame) |
| Same frames in one lab session | 1.17 s per frame |

- **Cause:** HyperFrames' local render planner splits every render into many chunks of about 10 frames (up to 16
  parallel chunks, 10 frames minimum). Each chunk is a new page, so a cinematic shot pays a full cold start every
  10 frames: GLB, set, textures, about 14 s of shader compilation, and cache anchors. `--workers 1` doesn't change
  this (298 s), and render.py's `--jobs 2` doesn't either (345 s).
- **No parallel gain:** two concurrent single-session renderers are no faster than one (66 s vs 66 s for 46 frames).
  SwiftShader already uses all 4 cores, so parallel workers only add cold starts and contention.

## 2. Optimisations implemented (all opt-in)
1. **Depth from the main pass** (`mainDepth`). AO, DOF and haze read the main render's depth: no second scene
   render, no second shadow render, and no visual change.
2. **Static environment cache** (`motion/envcache.js`, `envCache`). The set is rendered once per camera *anchor* into
   colour and depth, with an exact-pixel overscan, then re-projected per pixel to each frame's camera. Only the
   characters are rendered per frame, depth-tested against the cached set (a desk still hides legs). The parts that
   are kept exact:
   - **Shadows on the character:** the key light's real shadow map is composed per frame as min(cached set depth,
     character depth). Characters get the set's shadows and their own self-shadows.
   - **The character's shadow on the set:** each anchor stores the set with and without the key light; per frame the
     key light's contribution is removed where the character blocks it.
   - **Determinism:** anchors are a pure function of time. Each camera segment is grouped greedily so the camera stays
     within 3 cm of travel and 90% of the overscan margin in rotation (the look target can follow a face). HyperFrames
     chunks and seeks therefore render identically.
   - A static camera reads the cache 1:1.
3. **Half-resolution no-key layer:** it is only read under the characters' soft shadows.
4. **Profiles** (`runtime.js` QUALITY; all 1080p, every frame rendered, real animation, no duplicated frames):

| Profile | What it is |
|---|---|
| `cin_fast` | Drafts: environment cache, PCF shadows, no AO or DOF, FXAA |
| `cin_balanced` | Environment cache, PCF shadows, AO, DOF, haze, FXAA |
| `cin_cinematic` | Full re-render every frame, VSM 2048 shadows, 4× MSAA, depth from the main pass |
| `cin_reference_pcf` | Balanced without the cache, used as ground truth for the cache |

## 3. Measured results (sheet 1; single browser session; mean ms per 1080p frame over 45 consecutive frames)
| Profile (P3 look, P3 test cameras) | Wide (push-in) | Medium | Close-up | PSNR vs Cinematic |
|---|---|---|---|---|
| P3 Balanced (before) | 2,502 | 2,777 | 2,665 | 36.4–38.6 dB |
| **P4 Fast** | 1,005 | 1,029 | 1,325 | 26.7–30.5 dB |
| **P4 Balanced** | 1,169 | 1,155 | 1,437 | 26.8–31.1 dB |
| P4 Cinematic | 3,280 | 3,771 | 3,523 | reference |

- **P4 Balanced vs its uncached ground truth** (`cin_reference_pcf`): 27.0–32.0 dB on these moving shots. The rest
  of the gap to Cinematic is PCF vs VSM shadow edges and FXAA vs MSAA, not the cache.
- **Camera style matters as much as the profile.** P4 Balanced, same shots:

| Camera style | Wide | Medium | Close-up | Anchors (138 frames) |
|---|---|---|---|---|
| P3 cameras (push-ins that track the face) | 1,169 | 1,155 | 1,437 | 28 |
| Same moves, fixed look point | 1,164 | 1,072 | 1,075 | 18 |
| Locked-off | **622** | **900** | **1,025** | 3 |

**Against the target** (3–5 minutes of cold rendering per 10 s at 1080p30 = 300 frames, Balanced):
- These numbers come from measured per-frame means, plus the measured 0.17 s capture and about 0.5 min of startup.
  No full render was made.
- Locked-off wide shots: about **4.4 min per 10 s, within the target**.
- Locked-off medium: about 5.8 min. Locked-off close-up: about 6.5 min.
- Moving or face-tracking cameras: about 6.7–8.6 min.
- **So the target is met only for some shot types.** It is not met in general on this 4-core CPU container.
- **Through `render.py` today, none of these speeds is reachable**, because of the per-10-frame cold starts (§1). The
  3-second benchmark through `render.py` ran at 3.8 s per frame.
- The P4 look (§4) adds cost under Balanced: 1,542 / 1,365 / 1,676 ms vs 1,169 / 1,155 / 1,437 ms for the P3 look.
  The extra comes from two more lights on the character, bevelled geometry and the 3D street in each anchor rebuild.

**Quality honesty:**
- **Static cameras:** the cache is exact.
- **Moving cameras:** the cached set is resampled. Each anchor switch (every 4–6 frames in the slow push-in) adds
  0.2–0.6 grey levels of mean frame-to-frame change, concentrated on high-contrast edges. For scale, the camera move
  itself produces about 2.1. This could show as a faint edge shimmer.
- **Balanced uses PCF shadows,** which are harder-edged than Cinematic's VSM.
- Disocclusions at depth edges are possible for larger moves; the 3 cm and rotation bounds keep them small.

## 4. Cinematic visual quality (sheet 2; opt-in set variant `"cinematicVariant": "p4"`)

| Issue | Fix |
|---|---|
| Character too dark against the bright window | A soft face key (from the room) and a cool window rim for separation; the sky and window view toned down; the street hazed |
| Desk reflections and glare | The pale area was mostly the sun patch landing on the desk. The sun is now steeper so it falls near the window wall; wood specular and environment reflection are lowered |
| Box furniture | Box geometry becomes bevelled boxes (furniture, panels, books, radiator; UVs in metres by box projection), so edges catch the light |
| Background buildings and the "tan block" | The tan block was the stage's old 2D bank plate showing through where the window backdrop plane didn't reach at oblique angles. The painted plate is retired: a 3D street of procedural facades (windows, cornices, aerial-perspective wash) under a sky dome covers every view |
| Lens | **The P3 depth of field was effectively sub-pixel** (`dof` 0.55–0.75 px); the P3 window only looked soft because the plate was pre-blurred. An opt-in `dofScale` now gives a real lens blur in medium and close shots |
| Reconstruction label and credit | Dark backing, larger type; verified in a HyperFrames still |

**Still weak:** books and chairs are simple shapes; the rim light is subtle; Snow's stylised design remains a test
character's.

## 5. Mature character standard (`charlab/CHARACTER_STANDARD.md`; sheet 5)
**Criteria:** 7.0–8.0 heads tall; shoulders at least 1.5 head heights (men) or 1.3 (women); eye width at most 24% of
head width; an integrated neck; an adult skull and face; a full face rig; separate hair and clothing; CC0/CC-BY or
commissioned work. Snow (5.9 / 1.25 / 27%) and Rain (5.8 / 0.81 / 33%) fail and remain test-only; no resizing.

**Candidates** (official public previews only; licence CC-BY per page; Mikassa, Victor, Vincent and Storm need a paid
Blender Studio membership, $17 a month):
- **Mikassa:** the closest. Adult woman with a mature face and small eyes, about 7.3 heads by preview estimate,
  CloudRig. Needs a documentary wardrobe. Measure after download before any decision.
- **Victor and Vincent:** caricatures that fail the standard.
- **Storm:** a child.
- **Einar** (free): passes the proportions but is realistic in style.
- **Other free marketplace models:** mostly not CC and rarely face-rigged.

## 6. Recommendations (your decisions)
1. **Approve the P4 renderer pieces as experimental:** main-pass depth, environment cache, profiles, and the `p4` look
   variant. All are opt-in and regression-proven.
2. **Rendering architecture for cinematic 3D:** render each 3D shot in **one** browser session (the lab renderer),
   cached per shot like render.py's chunks. HyperFrames then composites it as a video layer under the captions and
   2D graphics. This is the only way the measured single-session speeds reach the final video without modifying
   HyperFrames or `render.py`. It is not built yet; I'd build it on your approval.
3. **Cinematography for Balanced:** prefer locked-off shots, or slow moves with fixed look points. The camera should
   not follow every head movement: it is cheaper and reads as more mature camera work.
4. **For the 3–5 min target everywhere:** a GPU or a many-core machine. On this 4-core CPU, close-ups and moving
   shots stay at about 6–8.6 min per 10 s in Balanced.
5. **Cast:** approve one month of Blender Studio membership to measure Mikassa, and/or commission an artist (§5).

**Next approval gate:** a cinematic animation test with the P4 look, rendered through the single-session path,
together with a full measured cold render. Not started.

## 7. Limitations
- Measurements come from this 4-core SwiftShader container; GPUs would change every number.
- The target is met only for locked-off wide shots; the env cache helps moving shots less.
- Moving-camera anchor switches can show a faint edge shimmer.
- PCF shadows in Balanced are harder than VSM.
- No full animation was rendered in P4. The speed path through HyperFrames (§6.2) is a proposal, not a measured
  pipeline.
- P4 look: simple books and chairs; subtle rim light; a procedural street, not a designed one.
- No adult cast member exists yet.

## Reproducibility
```
node epoch-ledger/charlab/bench/profile.mjs --demo D.json --chars .runtime/charlab/out_p3 --three .runtime/charlab/three/r0.186.1 --out OUT.json [--preset cin_balanced] [--variants ...]
node epoch-ledger/charlab/bench/profile_seq.mjs --demo D.json --chars ... --three ... --out DIR --windows 0.6:2.1,3.6:5.1,7.6:9.1 --profiles balanced,cin_fast,cin_balanced,cin_reference_pcf,cin_cinematic
node epoch-ledger/charlab/motion_render.mjs --demo D.json ... --quality cin_balanced --from A --to B        # single-session frames
JOBS=1 EPOCH_RENDER_TIMEOUT_PER_FRAME=15 epoch-ledger/charlab/bench/render_measured.sh WS OUT.mp4 LOGDIR TAG   # through render.py
demos: motion/demos/p4_cinematic_test.json (look 'p4'), p4_bench_push.json, p4_bench_locked.json; sequences/p4_cinematic.py (prepared, not rendered)
```
