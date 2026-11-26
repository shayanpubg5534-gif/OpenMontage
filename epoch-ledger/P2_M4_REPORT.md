# P2 report: M4.1 (environment and storytelling) and M4.2 (HyperFrames performance) — approval gate

Status: both milestones are built and measured, with a narrated documentary sequence rendered through HyperFrames.
This is an experimental baseline for your review. Rig v4 and the production pipeline are untouched (`render.py`,
`kit/assemble.py` and `narrate.py` were used read-only). M3 is kept as the conditionally accepted technical foundation.
Date: 2026-11-26.

## 0. Your visual concerns about M3 (addressed first)
You found M3 stiff, glitchy and game-like. I measured instead of guessing: `window.analyze()` lists world-space
acceleration spikes of 13 joints in every frame of a compiled performance (visible pops).

| Cause found | Evidence [M] | Fix |
|---|---|---|
| **A mocap pop** in CMU 18_08 (the listener clip): the whole upper body jumps at clip time 6.7 s | Spikes of 35–43 m/s² on both arms of both characters, in four demos | Clips are baked at 30 fps, outlier frames repaired by interpolation, then lightly smoothed |
| **Foot-lock snaps** at the start and end of each step | Calf spikes up to 67 m/s² while walking | 0.2 s lock ramps; a soft 3.5 cm leash, so a pin follows a shuffling foot instead of snapping |
| **Elbow jumps** at the start of every gesture | Forearm spikes of 40–48 m/s² exactly at reach onsets | IK solved fully, then blended by weight; an elbow pole that keeps the current bend plane |
| **Robotic restrained arms** (snapped toward one fixed stance) | Visual | Restraint now eases toward the clip's own slow posture, so damped arms keep living with the body |
| **Hand release while standing up** dragged the whole body | 290 m/s² spike (hand, foot) | Torso lean and counterbalance only for object reaches, and never while seated |
| **Ping-pong reversals** of held clips twitch the legs | Calf spikes every 1.6 s | Held segments play the clip's slow ("calm") version over a feet-down range |
| **Slouching** (the seated mocap subjects recline about 30° on a stool) | Visual, at normal speed | A posture layer: back-lean beyond 4° is corrected over the spine, so characters sit up at a meeting |
| Game-like staging: isolated actors in front of a painted plate, static side-on cameras | Visual | A real 3D set and shot coverage with cuts (below) |

**Result, same demos [M]:**
- **Worst spike:** 290 → ≤ 50 m/s².
- **Elias's spikes:** in the M3 demos, from 69–83 → 0.
- **The story:** Elias 13 spikes (largest 27 m/s², lifting the folder) and Nadia 152. Nadia's largest are about
  35 m/s² heel strikes and knee bends while she walks and sits, which is natural motion.
- **Unchanged by these fixes:** foot pinning (0.2–0.3 mm per frame), eye contact (100% within range), complete blink
  closure (0–1 eyeball pixels) and hand contact (0 mm).

## 1. M4.1 — reusable environment architecture
- **`motion/env.js`:** a component library for illustrated 3D sets. A set is a JSON spec: room shell, palette, light
  rig and items.
  - **Components:**
    - room shell with a window, a parallax city backdrop, wainscot, skirting and doors;
    - desk (pedestal, drawers, modesty panel), chair, office chair, bookshelf (seeded books), cabinet, counter;
    - plant, lamp, framed certificate or picture, sign, rug, papers, mug, nameplate.
  - **Look:** everything uses the characters' flat editorial treatment (two-band shading, ink outline, interior ink,
    real shadows) with a per-set shadow tint.
- **Anchors:** items expose anchors (`client_chair.seat`, `desk.top`, `counter.behind`, `left_door`). Shot scripts
  place actors by anchor, not coordinates, and chairs fit their seat height to the actor who sits on them.
- **Correct by construction:** characters and set share one scene, so perspective, occlusion (desk in front of legs,
  chair backs, the folder) and shadows are correct.
- **Sets built:**
  - `bank_office.json`, used in the story;
  - `bakery_shop.json`, a reuse test: a second set from the same components with no new code. It is plain: the bread
    shelves are the bookshelf component and read as books, so hero props per set are a backlog item.
- **Shared runtime:** `motion/runtime.js` is the shot runtime shared by the lab viewer and HyperFrames. It is
  pixel-identical to the viewer before the refactor (checked).

### The documentary sequence: "The loan meeting" (21.5 s, narrated, captioned)
- **Production pipeline:**
  - narration by the production `narrate.py` (Kokoro bm_george 0.95, Whisper timing, 0 pronunciation mismatches);
  - gold captions from the production caption layer;
  - assembled by the production `kit/assemble.py` with the readiness gate;
  - rendered by `render.py --isolate`.
- **The beat:** Nadia's bakery is profitable but out of cash.

| Shot | Narration | Staging |
|---|---|---|
| 1 establishing, slow dolly (0–4.6 s) | "Nadia's bakery had made a profit every month for three years." | She walks in to the client chair (walk → stop → sit, chained backwards from the chair anchor); Elias, at his desk, looks up |
| 2 two-shot (4.6–8 s) | "So why was she sitting in a bank, asking for help?" | She sits; he welcomes her with an open hand; they settle, upright, hands at rest |
| 3 over his shoulder (8–13.6 s) | "Her suppliers wanted their money in thirty days. Her customers paid in ninety." | She explains with two restrained gestures, glances down and back |
| 4 close-up (13.6–19.3 s) | "On paper, she was doing well. In the bank account, the money had run out." | He picks up her file, reads, his concern builds, he looks up at her |
| 5 wide (19.3–21.5 s) | — | Quiet hold on the two of them |

## 2. M4.2 — performance inside HyperFrames [M]
- **Setup:** whole 21.5 s story, 645 frames, 1080p30. Narration and captions included.
- **Machine:** this 4-CPU, 16 GB, GPU-less cloud machine.
- **Pipeline:** `render.py render --isolate` (2 scene chunks), HyperFrames 0.9.88.

| Preset | Settings | Jobs | Wall time | s per second of video | Peak RAM used | Quality vs standard (PSNR, whole video) |
|---|---|---|---|---|---|---|
| **Standard** | MSAA ×4, 2048 shadow map, interior ink | 2 | **801 s** | 37.3 | 3.0 GB | reference |
| MSAA ×2 (first "balanced" candidate) | MSAA ×2, 1024, ink | 2 | 791 s | 36.8 | 2.9 GB | 45.9 dB |
| MSAA ×2 | same | 1 | 1141 s | 53.1 | 2.8 GB | identical frames to jobs 2 |
| **Balanced (recommended)** | no MSAA, **FXAA-style edge pass**, 1024, interior ink on | 2 | **543 s** | **25.3** | — | **38.1 dB** |
| Lean | no MSAA, 1024, no interior ink | 2 | 411 s | 19.1 | 2.8 GB | 33.8 dB |
| Re-render, nothing changed (cache) | — | 2 | **1.1 s** | — | — | — |

**Findings:**
- **MSAA ×2 saves nothing on this CPU renderer:**
  - In HyperFrames: 791 s vs 801 s.
  - In the lab: 1.37 vs 1.42 s per frame.
  - I replaced it in the balanced preset with a single-pass FXAA-style edge filter in the existing post shader:
    **32% less time than standard.** Outlines stay smooth and interior lines are kept (sheet `presets_compare`).
- **Lean is 49% faster than standard,** but edges are visibly jagged and the face and clothing ink lines disappear:
  drafts only.
- **Parallel workers:** 2 jobs × 2 HyperFrames workers are **1.44× faster** than 1 job (HyperFrames' automatic
  workers). This shot has 2 scene chunks, so more jobs cannot help. Peak memory stays under 3 GB of 16 GB, so memory is
  not the limit; the 4 CPUs are.
- **Determinism:** the jobs 1 and jobs 2 renders decode to **identical frames** (frame MD5, both chunks: 342 + 303
  frames). Every frame is a pure function of time (compiled performance, no carried state).
- **Caching:**
  - An unchanged re-render takes 1.1 s.
  - A stray file in the workspace leaves the chunk keys unchanged.
  - Changing the shot script invalidates the chunks that use it.
  - All 27 runtime assets (bundle, GLBs, textures, set, shot, plate, fonts) are named literally in the composition,
    so they are in the cache key and in isolated chunk workspaces.
- **Overheads:**
  - HyperFrames setup is about 8 s per chunk render.
  - Loading and compiling the shot takes about 1 s.
  - The first frame compiles shaders, about 3–4 s.

**Production-relevant observations (not changed, production is untouched):**
1. **`render.py --isolate` links root-level `*.json` twice.** It links the referenced file, then again as
   HyperFrames config, and fails with `SameFileError` if a composition references a JSON file in the workspace root.
   The lab works around it (shot files in `shot/`). Suggest a one-line guard in `isolated_workspace` when production
   work resumes.
2. **`render.py range` renders whole cached chunks** containing the window (a 1 s range took 13.7 min because its
   chunk is 10 s). Expected behaviour, but worth knowing for previews.
3. **Duplicate three.js:** the assembler's head loads the classic three.js next to the bundle's own copy, which costs
   a warning and some load time. Harmless.

**Recommendation for production defaults:**
- **Final renders: balanced** (FXAA + interior ink), with 2 jobs on this machine.
- **Standard** for hero close-ups if you judge the difference visible.
- **Lean** for drafts only.
- **Throughput:** at about 25 s of compute per second of footage, an 18-minute episode would need roughly
  7.5 hours of rendering on this 4-CPU machine **[E, extrapolated from 21.5 s; not measured on an episode]**. Scenes
  without 3D characters are much cheaper. A real episode-scale measurement belongs in M5.

## 3. Honest limitations (see `charlab/BACKLOG.md`)
- **Still not hand-animated quality:**
  - The body motion is believable and calm, but mocap-driven.
  - Hands are posed rather than acted (the grip on the folder is approximate).
  - Sitting down from the wide shot still shows a deep forward bend.
  - Walk-to-chair is chained but not phase-matched.
- **Faces:** expressions transition smoothly but are subtle; there is no lip sync yet. Mouth, teeth, hair and
  facial-lighting items are unchanged in the backlog.
- **Sets:** box-built components read as illustrated furniture but simple. Hero props (chairs, lamp, bakery goods)
  would lift the bakery set most. There is no depth of field.
- **Mocap library:** small (CMU); no upright seated idle exists in it, so seated life comes from a calmed sit clip
  plus breathing, look-at and blinks.
- **Variety:** hairstyles, clothing and body types are **not** restricted by design. The generator and specs take any
  MakeHuman body, and the backlog lists the hair and wardrobe extensions.

## Decision needed (approval gate)
- **(a)** Approve the M4 baseline (environment architecture, motion fixes, balanced preset, HyperFrames path) and
  proceed to **M5**, the acceptance test (a 20–25 s scene judged against the audit's ten criteria, rendered at episode
  conditions). Production stays on Rig v4 until M5 passes.
- **(b)** One more focused pass before M5, for example hero props and set dressing, hand acting on objects, or lip sync.
- **(c)** Stop the 3D character track.

I recommend **(a)**, with lip sync and hand acting as explicit M5 criteria.

## Evidence
- **Videos** (1080p30 with narration and gold captions, not in git), in `projects/charlab_m4/`:
  - `story_loan_standard.mp4`, `story_loan_balanced.mp4`, `story_loan_lean.mp4`;
  - `story_lab_lean.mp4` (the lab renderer, no captions).
- **Sheets:**
  - `projects/charlab_m4/evidence/story_frames.png`, `presets_compare.png`, `bakery_set_reuse.png`;
  - compressed copies `epoch-ledger/charlab/evidence/m4_*.jpg`.
- **Benchmark logs:** `projects/charlab_m4/bench/results.jsonl` and per-run logs.

## Reproducibility
```
./epoch-ledger/charlab/build_m4.sh                                                     # characters with the clip set
.venv/bin/python epoch-ledger/scripts/narrate.py projects/charlab_m4/story --workspace projects/charlab_m4/hf
python3 epoch-ledger/charlab/hf_build.py epoch-ledger/charlab/motion/demos/story_loan.json .runtime/charlab/out_m4 \
    projects/charlab_m4/hf_balanced --quality balanced --narration projects/charlab_m4/story
python3 epoch-ledger/scripts/render.py render projects/charlab_m4/hf_balanced --isolate --jobs 2 -o OUT.mp4
# lab preview and QA: node epoch-ledger/charlab/motion_render.mjs --demo ... --quality balanced --analyze --qa
```
