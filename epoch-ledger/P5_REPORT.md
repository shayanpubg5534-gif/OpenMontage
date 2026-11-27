# P5 — Continuous-session rendering and mature character development (approval gate)

**Status:** experimental and opt-in. Nothing is promoted.
- Rig v4, the production renderer (`render.py`, unchanged), HyperFrames, production defaults and the M4/M5
  workflows are untouched. The live-canvas path stays the default and the fallback.
- No purchases, accounts or artists.
- **Snow appears only to validate rendering performance.** He is a technical test character, not a cast member.

**Approvals recorded:**
- P4's cinematic look, main-pass depth, environment cache and the three profiles: experimental and opt-in.
- `CHARACTER_STANDARD.md` with 7.5 heads preferred and 7–8 accepted.

Date: 2026-11-27.

**Deliverables:**

| File | Content |
|---|---|
| `projects/charlab_p5/p5_test.mp4` | 9.97 s, 1080p30, with audio |
| `projects/charlab_p5/characters/1_candidates_views.png` | Front, three-quarter, side and full-body views; native vs illustrated test |
| `projects/charlab_p5/characters/2_proportions.png` | Measured proportions |
| `epoch-ledger/charlab/MATURE_CAST_RESEARCH.md` | Character research findings |

Compressed copies are in `charlab/evidence/p5_*`.

## 1. Continuous-session rendering architecture (implemented)

| Piece | What it does |
|---|---|
| `charlab/shot_render.mjs` | Loads a shot **once** (characters, textures, set, shaders, cache anchors) and renders every frame at native 1080p30 in order, in one browser session. Frames go straight from the canvas (PNG) into ffmpeg in 30-frame segments: x264 CRF 8, BT.709 matrix and tags, closed GOP per segment. Segments are joined by **stream copy**, so there is no second encode of the shot |
| Shot cache | Keyed by a **fingerprint** of every input: demo, set, textures, character GLB, lip-sync tracks, all runtime modules, the motion viewer, the renderer itself, the three.js build, the profile, the frame range and the encoder settings. A changed shot re-renders only that shot |
| Interrupted renders | Each finished segment persists. A re-run renders only the missing segments |
| `hf_sequence.py --prerender` (opt-in) | Calls the shot renderer per shot and places the cached MP4 as a muted, timed `<video>` clip beneath captions, labels and graphics. HyperFrames composites, `render.py` renders, and both are unmodified. Without the flag, the M4.2 live-canvas path is used, unchanged |
| `bench/e2e_prerender.sh` | Measured end-to-end run with memory sampling |
| `bench/determinism_check.mjs` | Frame N rendered directly vs after frames 1..N−1 must be bit-identical |

**Revision granularity:** shots are revised per demo file, so a documentary should use one demo per shot. Any change
to a demo re-renders that shot only.

## 2. Measured results (9.96 s test, P4 look, Balanced profile, this 4-core CPU container)
**Cold end-to-end** (`e2e_prerender.sh`; nothing cached; includes initialisation, rendering, capture, encoding,
workspace build and HyperFrames compositing):

| Phase | Wall time |
|---|---|
| Browser and shot initialisation | 1.4 s |
| Shader warm-up (first frame) | 15.2 s |
| Rendering 299 frames | 354.9 s (1.19 s per frame) |
| PNG capture | 23.3 s (0.08 s per frame) |
| Page and pipe overhead, encoding overlap | 32.7 s |
| Segment join (stream copy) | 0.6 s |
| **Shot render total** | **428.2 s** |
| Workspace build | 5.0 s |
| HyperFrames compositing through `render.py` (video layer, captions, labels, audio, final encode) | 72.3 s |
| **End-to-end total** | **505.5 s (8.4 min)** for 9.96 s; peak memory 2.3 GB (0.6 GB idle) |

**Repeatability:** three independent cold runs took 506.9 s, 504.0 s and 505.5 s. The first two predate the fixes in
§3.

**Warm re-render** (nothing changed): **1.6 s**, and the output is **byte-identical** to the cold render.

**Against previous architectures, per 10 s of video:**

| Architecture | Time per 10 s |
|---|---|
| P3 (live canvas through `render.py`) | About 20.6 min (1,690 s for 13.7 s) |
| P4 Balanced through `render.py` | About 19 min (3.8 s per frame, from a 3 s benchmark) |
| **P5 continuous session** | **About 8.5 min** |

**Against the 3–5 min target: not met.** It's about 2.4× faster than P3, but rendering itself (1.19 s per frame)
dominates, and that is a CPU-rasterisation limit on this machine. Shot choice changes it (P4: locked-off wide shots
render at about 0.6 s per frame).

**Quality inspection:**
- **QC** (`qc.mjs`): passed. No single-frame flashes; opening frames consistent; no frozen stretches; cuts found at
  3.0 and 6.87 s as designed; −15.8 LUFS, true peak −1.2 dBFS.
- **Layout** (`layout_check.mjs`): 0 issues.
- **Captions:** keyed to Whisper word timings, highlighting word by word in sync. Checked on frames across the
  narration and the dialogue.
- **Lip sync:** mouth shapes follow the dialogue (checked frames 3.5–5.8 s); the viseme track is unchanged from P3.
- **Temporal stability:** frame-to-frame change median 1.51 and 95th percentile 3.31 grey levels. **No spikes** apart
  from the two cuts, so no edge shimmer or anchor pops were measured. The test uses a slow push, a locked-off shot and
  a slow pull-back.
- **Shadow consistency and determinism:**
  - Frame 45 renders bit-identically directly or after frames 1–44.
  - A render interrupted after one segment and resumed is **frame-identical** to an uninterrupted render (decoded-frame
    MD5).
- **Encoding loss:** the final video vs the intermediate shot, centre region, is 43.4 dB median, with a mean colour
  offset of 0.11 / 0.03 / 0.17 out of 255. The edges differ by design: the composition's vignette.

## 3. Defects found and fixed during P5
1. **Environment cache baked a stale character shadow into anchors.** It affected the P4 Balanced profile. After the
   first anchor, the key light's shadow map holds min(set, character at the *previous* frame), and later anchor
   rebuilds baked that shadow into the cached set. Results depended on render history (seen as 0.3–0.8 grey-level
   differences across sessions). **Fixed:** the set-only shadow depth is restored before every rebuild. Verified with
   the determinism check. The P4 Balanced sample frames and timings were made before this fix; the timings are
   unaffected, but some sample frames may show a faint stale shadow.
2. **Colour shift in the intermediate video.** An untagged file was converted with the BT.601 matrix and read back as
   BT.709: red +2.5, blue −1.7. **Fixed:** an explicit BT.709 matrix and tags. The offset is now ≤ 0.17.
3. **Fingerprint path normalisation:** the same file could be listed under two names. **Fixed**, and covered by a test.

## 4. Mature character research (summary of `charlab/MATURE_CAST_RESEARCH.md`)
**Measured** (sheet 2):

| Candidate | Heads tall |
|---|---|
| CharMorph MB-Lab male | 7.88 |
| CharMorph Antonia | 7.57 |
| CharMorph Reom | 7.41 |
| Einar | 6.98 |
| M5 Nadia (MPFB) | 6.66 |
| Snow | 5.89 |
| Rain | 5.79 |

| Approach | Finding |
|---|---|
| 1. Parametric adult bases | **MPFB:** consistent generation is proven in M2–M5, and its output is CC0, but it is aesthetically rejected. **CharMorph:** the CC-BY bases have correct adult anatomy, but they are realistic, nude and their hair is broken. The MB-Lab base is AGPL, so avoid it |
| 2. Usable adult meshes with rigs | **Mikassa** (paid membership) is the closest. Einar is free but realistic and costumed. Marketplace models are mostly not CC |
| 3. Adult base with controlled stylisation | The CC0 **Human Base Meshes** are a sculptor's start (no rig, hair or materials). **The shading-only stylisation test failed** for every candidate (sheet 1) |
| 4. Adapting Einar | The licence allows it, and his rig is convertible (profile not built). But his realistic sculpt, costume, prosthetic arm and age niche mean sculpting and wardrobe work. **Not adaptable automatically** |
| 5. Procedural Blender cast | Consistency is achievable (MPFB), the aesthetic is not. **Speculative hybrid:** an artist-made stylised "style kit" on a parametric base, then procedural variants |

**Conclusion:** no free or automatic route reaches the approved premium stylised adult aesthetic. Proportions are
solvable; form, hair and wardrobe need a person. Snow and Rain stay test-only.

## 5. Limitations
- **Speed:** 8.4 min per 10 s on this CPU-only container. Rendering is the bottleneck (SwiftShader), not
  architecture.
- **Measured on one shot only:** the test is one 3-camera shot of one character; multi-character scenes cost more per
  frame.
- **Disk use:** about 13 MB per 10 s of near-lossless intermediate.
- **Revision granularity:** per demo file (shot), not per camera cut within a demo.
- **Characters:** no mature adult cast exists. CharMorph bases are unrigged in our exports; Rigify face-rig generation
  wasn't re-verified.
- **P4 Balanced sample images** predate the shadow fix (§3.1).

## 6. Recommended next steps (your decisions)
1. **Adopt the continuous-session renderer as the experimental path for cinematic 3D shots**, with `--prerender` and
   one demo per shot. The live-canvas path remains the fallback.
2. **Render speed:** a GPU or many-core machine for the 3–5 min target. On this container, prefer locked-off and slow,
   motivated moves where the story allows.
3. **Cast:**
   - (a) Approve one month of Blender Studio membership to download and measure **Mikassa**.
   - (b) Commission a character artist for a **stylised adult style kit on a parametric base** (MPFB topology or a
     CloudRig base). That gives a consistent, reusable cast, which our converter, performance library and renderer
     already support.
4. Next gate: the first mature character through the full pipeline (static sheets first), then a cinematic test.

## Reproducibility
```
.venv/bin/python epoch-ledger/scripts/narrate.py projects/charlab_p5/story --workspace projects/charlab_p5/hf
.venv/bin/python epoch-ledger/charlab/splice_dialogue.py projects/charlab_p5/story projects/charlab_p3/dialogue_snow --before n3 --at 3.2 --gap 0.55 --speaker snow --ws projects/charlab_p5/hf
epoch-ledger/charlab/bench/e2e_prerender.sh epoch-ledger/charlab/sequences/p5_test.py .runtime/charlab/out_p3 projects/charlab_p5/hf_final OUT.mp4 LOGDIR
node epoch-ledger/charlab/shot_render.mjs --demo D.json --chars DIR --three .runtime/charlab/three/r0.186.1 --quality cin_balanced [--from A --to B] [--fingerprint-only]
node epoch-ledger/charlab/bench/determinism_check.mjs DEMO PROFILE direct|seq [N]
.runtime/charlab/venv/bin/python epoch-ledger/charlab/bstudio/render_views.py FILE.blend OUT --illustrated --res 700
.venv/bin/python -m pytest tests/epoch_ledger/test_charlab_p5.py
```
