# P3 — Professional character runtime and cinematic integration (approval gate)

**Status:** experimental and opt-in. Nothing is promoted.
- Rig v4, the production pipeline and its defaults are untouched.
- The lab's cel and editorial looks render pixel-identically before and after P3 (checked on M4 and M5 frames, §7).
- No purchases, accounts, credentials, artists or paid APIs.
- Audio: Kokoro narration, gold captions, no music.

**Snow is used only as a technical test character.** P3.1 found his large head, large eyes and youthful proportions
are inherent in his design, so he is not a cast candidate. Credit: "Snow Rig (CC) Blender Foundation |
studio.blender.org". Date: 2026-11-26.

**Deliverables** (full-resolution files in `projects/charlab_p3/`; compressed copies in `charlab/evidence/p3_*.jpg`):

| # | File | Content |
|---|---|---|
| 1 | `evidence/1_proportions.png` | Full-body orthographic proportion comparison (sent before any animation, as requested) |
| 2 | `evidence/2_character_look.png` | Before/after character comparison: native Blender vs P2 runtime vs P3 runtime vs P3 with half-size textures; neutral, medium, close-up and eye detail views |
| 3 | `evidence/3_environment.png` | Before/after bank environment, wide and medium |
| 4 | `evidence/4_gestures_expressions.png` | Gesture and expression sheet: standing, close-up and seated |
| 5 | `p3_cinematic_test.mp4` | 13.7 s, 1080p30, narration-driven cinematic test through HyperFrames |
| — | `epoch-ledger/charlab/CAST.md` | Cast requirements and acquisition routes, including exact Mikassa and Victor terms |

## 1. Proportions (P3.1) — sheet 1
Metrics come from the evaluated meshes:
- Heads tall: crown to floor, divided by crown to chin.
- Shoulders: biacromial width from the deform skeleton, in head heights.
- Eyes: eye width as a share of head width.

| Character | Heads tall | Shoulders (head heights) | Eye width / head width |
|---|---|---|---|
| Realistic adult reference (MB-Lab male) | 7.88 | — | — |
| Einar (Blender Studio, realistic) | 6.98 | 1.64 | 21% |
| M5 Nadia (MakeHuman) | 6.66 | 1.28 | — |
| **Snow, native** | **5.89** | **1.25** | **27%** |
| **Snow, converted** | **5.90** | **1.26** | **27%** |
| Rain | 5.79 | 0.81 | 33% |

- **Conversion and animation do not distort him:** native and converted Snow match within 0.2%.
- **Camera perspective:** the P2 test camera (30°, 2.1 m) exaggerates the head-to-torso ratio by 6.9%; a long lens by
  2.2%. Perspective is a minor factor.
- **Verdict:** the large head, large eyes and narrow shoulders are Snow's design. Fixing them means re-sculpting:
  scaling body parts would break his face rig, and you ruled that out. **Snow stays a technical test character.**
  Rain is for younger roles only.

## 2. Character look (P3.2) — sheet 2
New opt-in module `motion/charlook.js`, enabled per actor with `"charlook": "enhanced"`. It is applied when a converted
character loads.

| Area | P2 problem | P3 result |
|---|---|---|
| Skin | Dark, dense, no subsurface | Wrapped diffuse with a warm scatter term past the terminator, lower specular, a faint sheen. **Skin tone now matches the native render** under the same lights |
| Eyes | Glassy; huge dark pupil; no catch-light | Four fixes, listed below the table. **Close-up eyes match the native closely** |
| Hair | Plain | Matte base with a soft sheen. Anisotropy was tried and dropped: converted meshes carry no tangents. Still slightly darker than native |
| Mouth, cloth | — | Moist but not glossy; matte cloth |

The four eye fixes:
1. **Iris:** the native iris is a *metallic* ring that a colour bake turns into a dark band. The converter now reads
   the source's metallic map as an iris mask and restores the iris's own brown detail.
2. **Pupil:** the eyeball interior shows through the open pupil. The converter gives those faces a black texel, and the
   runtime eye material is double-sided. The pupil is now black and the right size.
3. **Catch-light:** the artist's highlight cards (`eye_dots`) are kept as unlit catch-lights, so there is one natural
   highlight per eye.
4. **Cornea:** a clear-coat cornea reflects a dark room with one soft window panel.

**Remaining gaps vs native:** no true subsurface scattering (ears and nostrils lack red translucency); hair and shirt
slightly darker; cornea refraction approximated.

**Texture memory (LOD):** converted with `--tex 1024`, i.e. half-size tiles.

| | Full textures | Half-size textures |
|---|---|---|
| Pixels | 66 Mpx | 16.5 Mpx |
| GPU memory (RGBA8 + mips) | 336 MiB | **84 MiB** |
| GLB size | 22.5 MB | 20.6 MB (geometry and morphs dominate) |

- **Quality:** at a 1120 px face close-up, half vs full gives PSNR 50.2 dB (mean difference 0.3/255). The difference
  is not visible; freckles soften very slightly. The P3 test uses the half-size version.
- **Compatibility:** the same skeleton, morphs and clips are used, so motion, gaze, expressions and lip sync are
  unaffected. All of them run in the test video.

## 3. Bank environment (P3.3) — sheet 3
New opt-in stage look `"look": "cinematic"` plus `motion/cinematic.js`. It reads a `cinematic` block in the set spec,
which the cel and editorial looks ignore.

- **Materials:** CC0 physically based texture sets from Poly Haven: oak floor, plaster, dark wood, oak veneer, leather,
  linen, carpet.
  - Fetched by `charlab/assets/fetch_textures.py` into `.runtime/`, not committed; licences are in
    `assets/textures_manifest.json`.
  - UVs are rewritten in metres, so textures tile at real scale.
  - A per-material texture-contrast control calms busy scans, and wood uses low specular.
- **Architecture and dressing:** ceiling, crown moulding, raised wainscot panels, a cast-iron radiator, linen curtains
  on a brass rod, and a desk pad, ledgers and pen cup.
- **Motivated light:**
  - Daylight through the window: the sun casts the mullions onto the floor, and an area light acts as the sky.
  - Warm practical lamps with glowing shades.
  - A soft image-based room bounce.
  - A soft wide key motivated by the window wall.
- **Lens:** HDR buffers with neutral tone mapping, AO and haze from the depth pass, depth of field on medium and close
  shots. The window view is softened and slightly overexposed.
- **Look across the room:** warm walnut, plaster and brass, cool daylight, and the characters lit by the same sources.
  It reads as a lit room rather than a game set.
- **Limitations:** books, chairs and the filing cabinet are still box-built, and the window view is a painted plate.
- **Cost:** about 2× the editorial look per frame (§6).

## 4. Performance library (P3.4) — sheet 4
New `motion/perflib.js`: an actor lists `"perform": [{"do": preset, "t": …}]`. Presets expand into the compiler's
ordinary face, gaze, gesture, hand and IK tracks, so they mix with hand-written keys and lip sync.

- **Listening and reactions:** `listen` (soft brows, small nod), `nod`, `glance` (look away to think, then back).
- **Expressions:** `concern`, `uncertain` (asymmetric brows, head tilt, small shrug, glance), `relief` (shoulders settle
  on an exhale, eyes relax, slight smile), `thoughtful` (eyes narrowed, glance down, tilt), `warm`.
- **Hands:** `explain` (one palm up, near the body), `open_hands` (both palms open, low), `hands_on_desk`. Seated actors
  rest their hands on the thighs between gestures (`restHands`).
- **Direction rules built in:**
  - Small amplitudes, one idea per gesture.
  - Ease in over 0.4–0.8 s, then settle back to the resting face.
  - Hands always return to rest; nothing loops on a fixed period.

**Motion fixes for converted (T-pose) rigs** in `elmotion.js`; A-pose MakeHuman characters are unaffected:
- **Palm direction:** the palm-normal sign assumed an A-pose rest, which is why the P2 palm faced down. Palms now face
  up when asked.
- **Rest stance:** it came from a `stand` clip that converted characters lack, so restraint and wrist relaxing eased
  toward a zero quaternion; that is why seated arms floated. The stance now falls back to the idle clip.
- **Head tilt:** a new gesture, applied after the head-roll levelling, which would otherwise cancel it.

## 5. Cinematic test — `p3_cinematic_test.mp4` (13.7 s, 1080p30)
**Story** (narration-driven, "Profit is not cash"). The narrator is Kokoro `bm_george`; the baker's single line is
Kokoro `am_michael`, lip-synced from Whisper word timing.

| Time | Shot | Words | Performance |
|---|---|---|---|
| 0–3.0 | Wide, slow push over the banker's chair | "A baker brought his bank an odd problem." | Listening, then concern |
| 3.0–6.9 | Medium | "His shop made a profit. But the cash kept running out." | Palm-up explanation on "profit", uncertainty (tilt, glance, small shrug) on "running out" |
| 6.9–10.6 | Close-up | "We sell more bread than ever. So where does the money go?" | His own line, lip-synced; open hands on the question |
| 10.6–13.7 | Slow pull-back, alone at the desk | "Profit is not cash." | Thoughtful |

- **On screen:** gold word-highlighted captions; an "Illustrative reconstruction" tag and the CC-BY credit in the
  opening.
- **QA:**
  - `qc.mjs` passed: consistent opening frames, no frozen stretches, cuts found at 3.0, 6.9 and 10.6 s, −16 LUFS,
    true peak −1.4 dBFS.
  - `layout_check` found 0 issues.
- **What could be better:**
  - The credit line is hard to read over the bright window.
  - In the close-up, a tan block in the painted city plate reads oddly through the window.
  - The seated torso still comes from a looped mocap clip.

## 6. Measured performance (this CPU container, SwiftShader, no GPU)
| Measure | Value |
|---|---|
| Shot load / performance compile | 1.06 s load (character, set, textures); 0.17 s compile for 412 frames |
| Single-process frame time (motion lab, 1080p) | Cinematic Balanced 2.5–2.8 s median; Cinematic Standard 4.2 s; editorial Balanced 1.26 s for the same shot. First frame 14–17 s (shader compile) |
| **HyperFrames cold render** (`render.py --isolate --jobs 2`) | **1,690 s (28.2 min) for 411 frames**; 4 cached windows took 444 s, 756 s, 1,058 s (the Standard close-up) and 594 s, i.e. 4.9 / 6.5 / 9.5 / 6.4 s per frame per worker |
| **Cached re-render** (nothing changed) | **2.0 s wall** (0.7 s in render.py); 4/4 chunks reused; output **byte-identical** to the cold render |
| Memory | Peak system memory in use 3.5 GB (0.7 GB idle); summed RSS of the render's process tree 3.8 GB (overcounts shared pages) |
| Character asset | GLB 22.1 MB with clips; 214k triangles; 84 MiB GPU textures (half size) |
| Compared with M5 | M5: 25 s of video in 879 s. P3: 13.7 s in 1,690 s, about 3.5× the cost per second of video |

- **Watchdog:** `render.py`'s default chunk watchdog (300 s + 3 s per frame) is too short for cinematic chunks on this
  CPU. They were killed and retried until the limit was raised for this render through
  `EPOCH_RENDER_TIMEOUT_PER_FRAME=15`. That is an environment setting, not a code change; `render.py` is unchanged.
- **What it means:** cinematic shots cost 2–3× the editorial look, and Standard close-ups cost the most. On this
  container, a 10-minute documentary with even a third of its time in cinematic character shots would take many hours
  of CPU rendering. Caching makes iteration cheap once a window is rendered.
- **Ways to cut cost** (none tried yet):
  - A GPU or more cores; the biggest win.
  - Balanced for close-ups.
  - Fewer shadow casters: only the sun casts shadows now; practicals do not.
  - Ink and normal passes skipped in the cinematic look; depth only.
  - Half-resolution AO and DOF.

## 7. Safety and compatibility
- **Pixel regression:** the pre-P3 commit (`de7dbde`) vs now gives max difference 0 on all checked frames:
  - M5 bank shot, editorial look, 3 frames.
  - M4 story shot, default cel look, 1 frame.
- **Everything new is opt-in:**
  - Stage look `cinematic`; actor `charlook`; actor `perform`/`performCtx`; demo `fit` and `exposure`; set `cinematic`
    block.
  - Profile fields `dark_interior` and `iris_mask`.
  - `hf_sequence.py` copies textures only for cinematic shots and skips `treatments.json` only for converted
    characters.
- **Preserved versions:** `.runtime/charlab/out_cv` keeps the P2 character; P3 uses `.runtime/charlab/out_p3`.

## 8. Cast (summary of `charlab/CAST.md`)
No available character meets the adult-cast requirements (6.5–7.5 heads tall, adult shoulders, eyes ≤ ~24% of head
width, CloudRig/Rigify face rig, CC-BY or CC0).

**Mikassa, Victor and Storm:**
- Blender Studio, CC-BY according to their pages.
- "Login to Download": an active Blender Studio membership is needed ($17 a month, or $34.50 per three months; one
  month suffices).
- Mikassa needs Blender 4.2 LTS; Victor (Cosmos Laundromat) Blender 3.4; Storm Blender 5.0.
- Licence terms inside the downloads could not be read without logging in; verify them before production use.
- Suitability can only be measured after download; our tools are ready.

The alternative is a commissioned artist.

## 9. Recommendations
1. **Approve the P3 runtime pieces as the experimental standard for converted characters:** the look module, iris and
   pupil conversion fixes, half-size textures, performance library and T-pose motion fixes. They are opt-in and proven
   not to change existing looks.
2. **Cinematic environments:** the direction works. Before production, replace box-built props with modelled ones,
   apply the look to the bakery, and solve the cost (a GPU, or Balanced plus lighter passes).
3. **Cast — your decision:**
   - Option A (one month of membership): Mikassa, Victor and Storm through our measurement and conversion pipeline.
   - Option B: commission an artist.
   - Until then, keep characters rare and narration-driven.
4. **Render settings for cinematic work:** split shots at cuts, Balanced by default, and a raised watchdog.

## Reproducibility
```
# textures (CC0) and the P3 character (half-size textures) + clips
python3 epoch-ledger/charlab/assets/fetch_textures.py
.runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/convert_char.py epoch-ledger/charlab/convert/profiles/snow.json .runtime/charlab/convert/snow_t1k --tex 1024
M=.runtime/charlab/mocap; .runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/add_clips.py .runtime/charlab/convert/snow_t1k/snow_cv.glb \
  .runtime/charlab/out_p3/snow_cv.glb --bvh idle=$M/137_28.bvh:18.9:22.4 --bvh sit=$M/113_15.bvh:0.3:7.0 --bvh talk=$M/19_08.bvh:0.4:9.0 \
  --bvh listen=$M/18_08.bvh:2.4:9.6 --bvh walk_start=$M/82_08.bvh:8.0:14.2
# sheets
.runtime/charlab/venv/bin/python epoch-ledger/charlab/convert/measure_props.py FILE OUT --head NAME         # sheet 1 inputs
SCALE=1.6 LOOK=enhanced EXPOSURE=1.55 node epoch-ledger/charlab/convert/studio_shots.mjs GLB .runtime/charlab/bstudio/views/snow/timings.json OUT
python3 epoch-ledger/charlab/convert/p3_sheet.py OUT.png TITLE "label|dir|note" ...                          # sheet 2
node epoch-ledger/charlab/motion_render.mjs --demo epoch-ledger/charlab/motion/demos/p3_env_{editorial,cinematic}.json ...   # sheet 3
node epoch-ledger/charlab/motion_render.mjs --demo epoch-ledger/charlab/motion/demos/p3_gestures_{stand,sit}.json --from 0.8 --step 75 ...  # sheet 4
# test
.venv/bin/python epoch-ledger/scripts/narrate.py projects/charlab_p3/story --workspace projects/charlab_p3/hf
.venv/bin/python epoch-ledger/charlab/lipsync.py "We sell more bread than ever. So where does the money go?" projects/charlab_p3/dialogue_snow --voice am_michael
.venv/bin/python epoch-ledger/charlab/splice_dialogue.py projects/charlab_p3/story projects/charlab_p3/dialogue_snow --before n3 --at 7.0 --gap 0.5 --speaker snow --ws projects/charlab_p3/hf
python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/p3_cinematic.py .runtime/charlab/out_p3 projects/charlab_p3/hf_final
EPOCH_RENDER_TIMEOUT_PER_FRAME=15 epoch-ledger/charlab/bench/render_measured.sh projects/charlab_p3/hf_final OUT.mp4 LOGDIR TAG
```
