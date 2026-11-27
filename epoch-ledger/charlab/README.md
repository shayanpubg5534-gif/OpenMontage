# Character lab (P2 · M2.1)

An isolated test bench for the proposed 3D character layer. It is **not** part of the production kit, and it changes
no approved asset. The 18-minute documentary, Rig v1–v4 and every existing composition are untouched.

| File | What it does |
|---|---|
| `build_character.py` | Builds a character headlessly on the CPU, run with the isolated Blender Python. Steps: spec → MPFB human → rig (default `game_engine`: 53 bones, 30 finger bones) → expression shape keys → CMU retarget → finger-grip action → GLB. Writes a timing and contents report. |
| `specs/*.json` | Character specs: MPFB macro sliders, optional named shape targets, rig and skin colour. `test_adult.json` is a neutral test body, not a cast member. |
| `viewer/index.html` | Loads a GLB in a chosen three.js release with toon shading and ink outlines. Exposes `renderAt(clip, t, framing, morphs)` and `measure(clip, t)`. |
| `build_dressed.py` | M2.3: a fully dressed character from an MPFB preset spec (`specs/elias.json`). It adds eyes, brows, lashes, teeth, hair, clothes and skin, then the rig, expression keys carried onto the brows, lashes and teeth, real (deleted) clothing masks, a standing pose and finger poses, and exports a GLB. Also checks eye alignment. |
| `inspect_character.py` | M2.3: geometric checks of an exported GLB: clothing and scalp poke-through (rays along the skin normal), the hair-to-scalp gap, and eye symmetry and spacing. |
| `viewer/lookdev.html`, `lookdev.mjs` | M2.3: look-development viewer and still renderer. Two treatments, `toon` and `paint`, with hue-shifted banded shading, interior ink lines, silhouette ink, a shadow catcher over an Epoch Ledger plate and shared paper grain; plus diagnostic modes. |
| `evidence_sheets.py` | Assembles stills into labelled evidence sheets (`evidence/`). |
| `install_assets.py` | Reproducible install of the MakeHuman system assets: SHA-256 and size check, licence check (all CC0), safe extraction, receipt. |
| `check_glb.mjs` | Drives the viewer in headless Chromium (CPU WebGL). It checks the GLB loads, then measures: bones, shape keys, clips, determinism, ms per frame, prop-socket drift, foot sliding and root travel. Writes evidence frames. |

## Environment (everything lives in `.runtime/charlab/`, which git ignores)

```
uv venv --python /usr/local/bin/python3 .runtime/charlab/venv && uv pip install --python .runtime/charlab/venv/bin/python bpy==5.3.0
# fallback, also verified: Python 3.11 + bpy 4.5.17 LTS in .runtime/charlab/venv45
git clone https://github.com/makehumancommunity/mpfb2 .runtime/charlab/mpfb2 && git -C .runtime/charlab/mpfb2 checkout v2.0.18
mkdir -p .runtime/charlab/user/extensions/user_default && ln -s $PWD/.runtime/charlab/mpfb2/src/mpfb .runtime/charlab/user/extensions/user_default/mpfb
(cd .runtime/charlab/three && mkdir r0.186.1 && cd r0.186.1 && npm pack three@0.186.1 && tar xzf three-0.186.1.tgz)
curl -O https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/002/02_01.bvh   # into .runtime/charlab/mocap

BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_character.py \
    epoch-ledger/charlab/specs/test_adult.json .runtime/charlab/out --bvh walk=.runtime/charlab/mocap/02_01.bvh
node epoch-ledger/charlab/check_glb.mjs --three .runtime/charlab/three/r0.186.1 --glb .runtime/charlab/out/test_adult.glb --out .runtime/charlab/check
```

## Asset rules (the repository is public)

**Never commit to git:**
- third-party asset files (MakeHuman asset packs, Quaternius, Mixamo);
- GLBs built from Quaternius or Mixamo assets.

The licences allow them inside finished videos, but not redistribution of the assets themselves. Keep them in
`.runtime/` and rebuild them from scripts. CMU motion capture and MPFB's bundled CC0 assets are free of that
restriction, but generated characters still stay out of git, to keep the repository small.

Results and the recommended versions: `epoch-ledger/P2_M21_M22_REPORT.md`.

## Reproducing the setup in a new session

1. **Isolated Blender Python and MPFB:** follow "Environment" above (`bpy` 5.3.0 in `.runtime/charlab/venv`, MPFB at tag `v2.0.18`).
2. **MakeHuman system assets.** Get `makehuman_system_assets_cc0.zip` (280,737,770 bytes, SHA-256
   `b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107`) from the official page,
   https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html. Its mirrors are blocked in this
   cloud environment, so either:
   - allow `files2.makehumancommunity.org` (or `files.makehumancommunity.org`) in the environment's network settings and download it; or
   - upload the ZIP, or an RAR split of it, to the session.

   Then run:
   ```
   python3 epoch-ledger/charlab/install_assets.py PATH/makehuman_system_assets_cc0.zip    # or …part01.rar (needs: apt-get install unar)
   ```
   The script refuses any file whose size or checksum differs, or any asset that isn't CC0. It extracts into the lab's MPFB
   user data and writes `receipt_makehuman_system_assets.json`. `7zip` from Ubuntu cannot unpack RAR (no RAR codec); use `unar`.
3. **three.js for the character layer:** build the pinned single-file bundle, with no import map, so `render.py --isolate`
   and the render cache see every file:
   ```
   mkdir -p .runtime/charlab/bundle/node_modules && ln -s $PWD/.runtime/charlab/three/r0.186.1/package .runtime/charlab/bundle/node_modules/three
   cp epoch-ledger/charlab/three_bundle_entry.js .runtime/charlab/bundle/entry.js
   (cd .runtime/charlab/bundle && npx --yes esbuild@0.25.0 entry.js --bundle --format=esm --minify --outfile=three186-char.js)
   ```
4. **Build and inspect the character, then render the stills:**
   ```
   BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
       epoch-ledger/charlab/specs/elias.json .runtime/charlab/out_m23 --bvh walk=.runtime/charlab/mocap/02_01.bvh
   BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/inspect_character.py \
       .runtime/charlab/out_m23/elias.glb .runtime/charlab/out_m23/inspect.json
   node epoch-ledger/charlab/lookdev.mjs --three .runtime/charlab/three/r0.186.1 --glb .runtime/charlab/out_m23/elias.glb \
       --plate projects/profitable-and-broke/hyperframes/plates/shop-bg-6302a081a386.png --shots SHOTS.json --out DIR
   ```

## Installed asset packs (licence ledger)

| Pack | File / SHA-256 | Source | Licence | Installed to |
|---|---|---|---|---|
| MakeHuman system assets | `makehuman_system_assets_cc0.zip`, 280,737,770 bytes, `b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107` | Official MakeHuman asset-pack page (`static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html`). Downloaded by the user and transferred as an 11-volume RAR5 set; extracted with `unar`. | **CC0** for all 94 assets: hair 10, eyebrows 12, eyelashes 4, eyes 11, teeth 6, tongue 1, skins 23, clothes 20, proxy meshes 7. Read from `packs/makehuman_system_assets.json` and matched 94/94 against the official page | `.runtime/charlab/user/extensions/.user/user_default/mpfb/data/` (git-ignored). MPFB reports it as installed and current. |

## M2.3b — editorial art direction (two characters, three treatments)

| File | What it does |
|---|---|
| `specs/elias.json`, `specs/nadia.json` | Male and female characters. Opt-in M2.3b fields: `face_normals` (strength of the clean-face shading normals), `lod_ratio` (wide-shot LOD export), `recolour` (palette rules, e.g. the sports socks inside the shoe asset → dark tights). |
| `build_dressed.py` | Adds `face_normals`, `export_textures` (`<id>_tex/` + manifest) and `export_lod` (`<id>_lod.glb`) when the spec asks for them. |
| `prepare_textures.py` | Build-time treated textures. `.toon.png` drops photographic detail. `.flat.png` is a controlled palette: k-means per material family; skin is one soft even tone. |
| `viewer/lookdev2.html` | Treatments `toon2`, `editorial` and `hybrid`; set presets `bakery` and `bank` (light rig, shadow colour, ink colour, grade); several characters; switches for `msaa`, `shadow`, `ink` and `lod`. |
| `evidence_sheets2.py` | The M2.3b comparison sheets. |

```
for c in elias nadia; do
  BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
      epoch-ledger/charlab/specs/$c.json .runtime/charlab/out_m23b --bvh walk=.runtime/charlab/mocap/02_01.bvh
  python3 epoch-ledger/charlab/prepare_textures.py .runtime/charlab/out_m23b/${c}_tex --spec epoch-ledger/charlab/specs/$c.json
done
node epoch-ledger/charlab/lookdev.mjs --page lookdev2.html --three .runtime/charlab/three/r0.186.1 \
    --query 'env=bank&chars=elias:-.65:0:15,nadia:.7:.1:-20&out=/.runtime/charlab/out_m23b' --shots SHOTS.json --out DIR
```

## M2.3c — bespoke character geometry (procedural, headless)

| File | What it does |
|---|---|
| `stylise.py` | Run by `build_dressed.py` only when a spec has `"design"`. It adds:<br>• face planes (Taubin smoothing of the face skin as a shape key, then the proxies are refitted);<br>• original hair (a designed hairline, a volume map, flow-aligned clump grooves, lock tips, a solid edge, an optional colour zone, an optional ponytail with clearance and a tie);<br>• designed brows;<br>• lash lines on the eyelash helper geometry.<br>The generated meshes are skinned to the head and carry the body's expression keys. |
| `specs/elias_c.json`, `specs/nadia_c.json` | Designed face targets and `"design"` settings (angles in degrees around the head: az 0 = front, +90 = the character's left). |
| `prepare_textures.py` | With `design.eyes`: an illustrated eye texture (iris found automatically, enlarged, two tones with a limbal ring). |
| `viewer/lookdev3.html` | `lookdev2.html` plus the designed mesh types (`ghair`, `gline`). |
| `verify_design.py` | Skinning, expression, blink and brow-raise measurements for the designed meshes. |
| `evidence_sheets3.py` | M2.3b vs M2.3c sheets. |

Commands: see `epoch-ledger/P2_M23C_REPORT.md`, "Reproducibility".

## M3 — motion (deterministic performance compiler, animated demos)

| File | What it does |
|---|---|
| `motion/elmotion.js` | Compiles a shot script into per-frame poses at 30 fps. Layers:<br>• mocap clip segments with eased crossfades, phase-matched walk transitions, world placement (`pos`/`yaw`, `pin`, `continue`, `next`) and floor calibration;<br>• foot-plant detection and two-bone leg IK (no sliding) with a floor clamp;<br>• arm restraint, wrist relaxation, breathing, nods;<br>• look-at spread over chest, neck and head with a lagging spring, eyes leading, lids following the gaze, automatic and scripted blinks;<br>• eased, overlapping expression transitions;<br>• finger poses from the rig's own grip clip;<br>• arm IK to prop sockets, points or targets in the actor's own frame;<br>• props on scripted paths or hanging from a hand with a damped swing.<br>`apply(t)` poses any frame with no carried state (seekable; frames can render in any order). |
| `motion/stage.js` | The M2.3c flat editorial renderer as a module, plus eye rotation (shader pivot; no rig change), cloth inflation and a skin depth bias against shallow poke-through, and flat-colour inked props. |
| `motion/demos/*.json` | Shot scripts: `d1_arrival` (walk start, carry, stop, eye contact), `d2_sit` (invite, sit, settle, stand), `d3_conversation` (restrained explanation, listening, nods), `d4_handoff` (pick up, offer, take, read, point). |
| `viewer/motion.html` | Loads a demo, builds props (desk, chair placed under the sitter, folder, bag), compiles, renders. QA functions: `qa()` (foot pinning, floor contact, knees, eye contact, raw retarget sliding), `clothQA()` (skin outside covered garment regions, CPU-skinned), `blinkTest()` (visible eyeball pixels with lids closed). |
| `motion_render.mjs` | Renders a demo frame by frame (standard or lean quality), records per-frame render and readback times, runs QA, encodes MP4 with ffmpeg. |
| `stylise.py` | Adds `cloth_follow_legs` (M3): below the hips, skirt weights blend toward the nearest leg weights so a seated skirt bends with the thighs. |

Clips used (CMU, free licence; retargeted at build time with `--bvh name=FILE:START:END`): `idle` 137_28, `walk_start`
82_08, `walk_stop` 16_34, `walk_turn_r` 16_19, `sit` 113_15, `talk` 19_08, `listen` 18_08.

## M4 — environments, storytelling and HyperFrames
| File | What it does |
|---|---|
| `motion/env.js` | Illustrated 3D set component library and builder (room shell, window with backdrop, furniture and dressing), anchors for shot scripts, chairs fitted to sitters. |
| `motion/sets/*.json` | `bank_office` (the story set), `bakery_shop` (a reuse test). |
| `motion/runtime.js` | The shot runtime shared by the lab viewer and HyperFrames; quality presets `standard`, `balanced` (FXAA + interior ink), `msaa2`, `lean`. |
| `motion/hf_entry.js`, `hf_build.py` | Single-file bundle and a HyperFrames workspace builder (production assembler, readiness gate, literal asset manifest, captions, narration). |
| `motion/demos/story_loan.json` | "The loan meeting": a narrated five-shot documentary beat. |
| `build_m4.sh` | Character builds with the M4 clip set (adds `sit_idle`). |

Motion-quality layers added in M4 (in `elmotion.js`): cleaned and smoothed clips, calm held segments, posture
(upright sitting), soft foot leash with 0.2 s ramps, IK weight blending with a bend-plane pole, counterbalance for
standing object reaches, and `window.analyze()` for acceleration spikes.

## Continuous-session rendering for cinematic 3D shots (P5, experimental, opt-in)
- **`shot_render.mjs`:** renders one shot (one demo) in a single browser session at native 1080p30. Frames are piped
  into ffmpeg in 30-frame segments (resumable), joined by stream copy, and cached under a fingerprint of every input.
- **`hf_sequence.py SEQ CHARS WS --prerender`:** composites each cached shot as a muted, timed `<video>` under
  captions and graphics. `render.py` and HyperFrames are used unchanged. Without `--prerender`, the live-canvas
  path (M4.2) is used, which stays the default and the fallback.
- **Measure:** `bench/e2e_prerender.sh`.
- **Determinism:** `bench/determinism_check.mjs`.
- **Report:** `../P5_REPORT.md`.

## Narration and dialogue (permanent standard, P6)
Narration is an independent voice-over, not character dialogue. Characters never lip-sync to the narrator; narrated
shots are acted (breathing, blinks, gaze, expressions, gestures, interaction with the set). Lip sync (`lipsync.py`,
`splice_dialogue.py`, an actor's `speech` entry) is retained but off by default, and is used only for a line the script
gives a character with their own assigned voice. See `CHARACTER_STANDARD.md` §5 and `DIRECTION.md`.

## P6 mature stylised prototype (experimental; see `../P6_REPORT.md`)
| File | What it does |
|---|---|
| `p6/build_p6.py` | Builds a variant (raw, A, B or C) from the CharMorph Reom database (`$CHARMORPH_DB`): anatomical morphs, geometric stylisation, LBS pose, wardrobe, mesh hair and brows, painted skin; writes `.blend` and measurements |
| `p6/render_p6.py` | Five comparison views in one neutral studio (Cycles) |
| `p6/ortho_p6.py` | Orthographic silhouettes at one scale |
| `p6/make_sheets.py` | Variant, overview and proportion sheets |
| `p6/export_glb.py` | Static runtime GLB (skin paint baked to a texture) |
| `p6/still.mjs` | One runtime frame of a demo to PNG |
| `motion/demos/p6_bank_still.json` | The prototype in the P4 cinematic bank set (static `glb` prop with `keepMaterials`) |

## P8 free-asset evaluation (experimental; see `../P8_REPORT.md`, provenance in `p8/ASSETS.md`)
| File | What it does |
|---|---|
| `p8/figdecode.py` | Reads Figma `.fig` files (Kiwi schema + document) without Figma |
| `p8/peeps_extract.py` | Renders Figma nodes (frames, component instances with swaps and overrides) to SVG |
| `p8/peeps_compose.py` | Builds Open Peeps characters from parts and remaps colours to a muted palette |
| `p8/compose_25d.py` | 2.5D still: characters composited into a rendered set plate, placed through its camera, with lighting |
| `p8/bm_pose.py` | Poses a Rigify character with its own controls; static posed GLB for the runtime |
| `p8/make_sheets.py`, `p8/svg_to_png.mjs` | Inspection and comparison sheets |

## P9 2.5D animation test (experimental; see `../P9_REPORT.md`)
| File | What it does |
|---|---|
| `p9/run_p9.sh` | The whole test end to end (plates, painterly pass, track, characters, assembly, QC, wardrobe), timed |
| `p9/prepare.py` | Characters with all their faces as switchable layers, and the per-shot performance timeline (seeded blinks) |
| `p9/cam_track.mjs` | Replays a demo's camera: projected world anchors per frame and a set depth pass |
| `p9/animate.mjs` | Per-frame 2.5D composite: layer animation, cut-out arm, lighting, shadows, depth occlusion, grain |
| `p9/wardrobe.mjs` | Wardrobe feasibility: recolours the artist's fills, adds collar and tie in the artist's line weight |
| `p9/sheet.mjs`, `p9/measure.py` | Labelled contact sheets; wall time and peak RSS of a command's process tree |
| `p9/points_shot{1,2}.json`, `p9/paint_filter.txt` | Character and foreground anchors in world space; the painterly ffmpeg filter |

## P10 fast 2.5D production path (experimental; see `../P10_REPORT.md`)
| File | What it does |
|---|---|
| `p10/run_p10.sh` | The narrated test end to end, cold (narration, plates, depth, paint, cast, shots, HyperFrames, QC), every step timed |
| `p10/compose.mjs` | Fast 2.5D compositor: one set still per camera, 2D camera with depth-layer parallax, characters rasterised once per shot into lit bitmap layers (body, one head per expression, rig pieces), occluders cut once from the depth pass |
| `p10/render_shot.mjs` | Renders a shot with several compositor workers (frame ranges) and joins the segments by stream copy, checking the frame count |
| `p10/rig.mjs`, `p10/rigs/*.json` | Limited cut-out rig on the artist's drawing: joints hidden under clothing (wrist under a cuff) or bridged by a joint disc in the limb's colour and line weight (elbow); pieces and cuts are masks |
| `p10/prepare.py` | Cast (formal banker, rigged baker), faces as layers, and the per-shot performance keyed to the narration's word times |
| `p10/wardrobe2.mjs` | Formal wardrobe: the artist's own fill shapes recoloured by index, a tie drawn in the artist's line weight |
| `p10/survey.py`, `p10/sheets.sh` | Art-coverage survey (every pose, bust and head) and the P10 investigation sheets |
| `p10/rig_test.mjs`, `p10/grid.mjs` | Joint inspection at several angles; coordinate grid for placing joints |
| `motion/demos/p10_cam{A,B,C}.json` | One-frame plate demos (locked cameras: two-shot, banker close-up, baker close-up) |
| `sequences/p10_test.py` | The narrated sequence: three 2.5D shots as video clips, the balance-sheet and new-money graphics, gold captions |

## P11 narration-driven storytelling (experimental; see `../P11_REPORT.md`, method in `p11/NARRATION_TO_VISUAL.md`)
| File | What it does |
|---|---|
| `p11/visual_map.py` | The reusable method: clauses from word timestamps, concepts and word-anchored events, `check` (coverage, semantic and timing rules, table) and `inspect` (when each planned change actually appears in the rendered film) |
| `p11/map_p11.json`, `p11/map_p10_as_delivered.json` | The P11 plan; P10 described with the same concepts (the comparison) |
| `p11/prepare.py` | 2.5D shots and performance keyed to the resolved events (bust characters with a laptop and a phone for story actions) |
| `p11/vault3d.mjs`, `p11/render_vault.sh` | Procedural 3D vault (sealed gate, cash inside) with the camera keyed to the narration; painterly pass to match the plates |
| `p11/run_p11.sh` | The test end to end, cold, with QC and semantic sync inspection |
| `motion/demos/p11_camD.json`, `sequences/p11_test.py` | The desk-from-above plate; the sequence with narration-synchronised graphics (one timing source) |

