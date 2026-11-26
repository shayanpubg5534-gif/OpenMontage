# P2 report: M3 motion (M3.1 single actions + M3.2 hands and contact) — Motion gate

Status: the experimental motion system is built. Four rendered motion demos use both characters. This report is the
checkpoint for the **Motion gate**. Nothing in production has changed: Rig v4 is still the production character system,
and no episode was migrated or rendered.
Date: 2026-11-26.

## What was built (lab only, `epoch-ledger/charlab/`)
- **`motion/elmotion.js`: a deterministic performance compiler.**
  - **Input and output:** it takes a shot script (JSON) and computes every frame at 30 fps.
  - **Seeking:** `apply(t)` poses any frame with no carried state, so frames can be rendered in any order or in
    parallel, and HyperFrames can seek them. Compiling an 8 s two-character shot takes 0.1–0.15 s.
  - **Layers:**
    - mocap clip segments with eased crossfades;
    - phase-matched walk transitions;
    - world placement;
    - floor calibration;
    - foot-plant pinning with two-bone leg IK;
    - gesture restraint and wrist relaxation;
    - breathing and nods;
    - look-at spread over chest, neck and head, with a lagging spring;
    - eyes that lead, and lids that follow the gaze;
    - blinks (automatic, plus extra ones on large gaze shifts);
    - eased, overlapping expression transitions;
    - finger poses;
    - arm IK to prop sockets, points or body-relative targets, with a torso lean when a target is out of reach;
    - props on scripted paths, or hanging from a hand with a damped swing.
- **`motion/stage.js`:** the M2.3c flat editorial look as a module, plus:
  - eye rotation through a pivot in the eye shader (the 53-bone rig is unchanged);
  - a 4 mm cloth push-out with a skin depth bias, against shallow skin-through-cloth contact;
  - inked, flat-colour props: desk, chair, folder and bag.
- **`viewer/motion.html` and `motion_render.mjs`:** a frame-by-frame renderer with QA, timing and MP4 output.
- **`stylise.py`, `cloth_follow_legs`:** opt-in per spec; used for Nadia. Below the hips, the skirt's skin weights
  blend toward the leg weights, so the skirt bends with the thighs when she sits.
- **Kept:**
  - the 53-bone `game_engine` rig, finger bones, expression keys and the asset-loading safeguard;
  - the M2.3b and M2.3c specs and viewers (frozen);
  - the version register, `charlab/VERSIONS.md`.

**Motion sources:** CMU motion capture (free licence), retargeted at build time:
- `idle` 137_28 ("normal wait");
- `walk_start` 82_08 (stand still, then walk);
- `walk_stop` 16_34 (slow walk, stop);
- `walk_turn_r` 16_19;
- `sit` 113_15 (sit in a chair and get up);
- `listen` 18_08;
- `talk` 19_08.

## The demos (1920×1080, 30 fps, both characters)
| Demo | What it shows |
|---|---|
| **D1 arrival** (bakery, 8.0 s) | Nadia starts from standing, walks in carrying a bag (the bag hangs from her hand and swings), and stops with a phase-matched transition. Elias tracks her with his eyes, then his head; on her arrival they make eye contact, he nods, and both expressions soften |
| **D2 sit** (bank, 7.5 s) | Elias invites her with an open hand. Nadia steps to the chair, turns and sits; the chair is placed under her pelvis from the compiled motion. She settles with her hands on her lap, keeps eye contact, nods and stands up again |
| **D3 conversation** (bank, 8.0 s) | Elias explains with restrained, authored gestures: an open palm, a small two-handed frame, a gesture toward her, a hand to the chest. Nadia listens, glances down and back with a blink, nods twice and moves from concern to a slight smile |
| **D4 hand-off** (bank, 7.5 s) | Elias leans to pick a folder off the desk, lifts it and offers it. Nadia reaches, both hold it for a moment, he lets go, and she brings it up to read. He points at it, then they make eye contact and nod |

## Measurements [M]
| Check | Result |
|---|---|
| **Foot sliding while a foot is planted** | **Pinned motion:** 0 mm per frame in D2–D4. D1 walk: 0.21 mm per frame on average, with a worst frame of 5.1 mm at plant entry and exit.<br>**Raw retargeted mocap on the same plants:** 0.4–1.5 mm per frame, worst 12.8 mm.<br>The M2.1 checker measured the raw walk at about 11.6 mm per frame, with spikes up to 147 mm |
| **Feet in the floor** | Worst case 4 mm below the rest foot height (the clamp tolerance) in all demos. No floating while planted |
| **Knees bending backwards** | 0 frames. Smallest knee angle: 72° (seated) |
| **Eye contact** | During "look at the other character" beats, after a 0.6 s settling time, the eyes reach the partner's eyes within the ±28° eye range in **96–100%** of samples. D2: 96% and 99%, while Nadia is turning to sit |
| **Blink closure** (eyeballs painted magenta, pixels counted in an eye close-up) | Open about 2,800 px, half-closed about 1,000–1,150 px, **closed 0 px**, for both characters in every demo: **closure is complete** |
| **Hand contact with the folder** (palm centre to socket, while the grip is engaged) | Nadia **0 mm** throughout the hand-off and reading. Elias 0 mm from lifting through to the hand-off; **22 mm at the pick-up from the desk** (the torso-lean limit). Before the fixes the gaps were 172 mm and 41 mm; see "Problems found" |
| **Clothing penetration** (CPU-skinned skin more than 4 mm outside covered garment regions; visible skin such as head, neck, hands and lower legs excluded) | **Nadia:** mean 0.7–2.6 vertices per frame, max 9 (seated D2: thighs, after the skirt fix).<br>**Elias:** a constant 6–7 vertices at the back of the collar (spine_03), present at rest too, so a static contact; up to 26 when he gestures (forearm at the cuff).<br>Nothing of this showed in review at 1080p |
| **Skirt when seated** | Before `cloth_follow_legs`, the thighs tore through the skirt (clearly visible). After it, the skirt is clean in every seated frame |

**How the measurements were made:** all are written by the viewer's QA (`qa()`, `clothQA()`, `blinkTest()`) to
`projects/charlab_m3/qa/*.json`.

## Rendering performance [M] (1080p, this 4-CPU machine, CPU WebGL, no GPU)
| | Standard (MSAA ×4, 2048 shadow map, interior ink) | Lean (no MSAA, 1024 shadow map, no interior ink) |
|---|---|---|
| Render per frame, median (D1 / D3) | **1.08 s / 1.06 s** (all four demos: 1.06–1.11 s; p95 ≤ 1.24 s) | **0.22 s / 0.24 s** (p95 ≤ 0.28 s) |
| PNG readback per frame | 0.13–0.15 s | 0.14 s |
| Wall time for an 8 s clip (241 frames, including load and encode) | 294–306 s | 91–96 s |
| First frame (shader compilation) | about 3 s | about 2.7 s |
| Scene load / compile | 0.5–0.6 s / 0.1–0.15 s | same |

**Quality of the lean setting** (sheets `*_standard_vs_lean`): outlines and hair edges are visibly jagged at 1080p, and
the light interior ink lines (face and clothing folds) are gone. Lean is **4.5–4.9× faster**. Standard costs about
37 s of compute per second of footage. Lean costs about 11 s, but at visibly lower quality.

**Recommendation for production defaults: not yet.** Standard is the quality reference, and I don't recommend lean
for final frames. Before any default is set, M4.2 must measure the next step: a middle setting (MSAA ×2, interior ink
on, 1024 shadow map), and rendering with HyperFrames capture and parallel workers. No episode-level or
weekly-throughput claim is made.

## Problems found and fixed during the milestone
| Problem (seen in review or QA) | Fix |
|---|---|
| Conversation mocap (19_08) gestures flail far too much for a documentary, and the clip turns Elias away from Nadia | His gestures are authored with arm IK at body-relative targets, timed like speech beats. His base motion is the stable listener clip |
| Thighs tore through the skirt when seated | `cloth_follow_legs` (skirt weights follow the thighs) |
| The chair stayed at the origin while Nadia sat in the air | Static props are no longer overwritten by the compiled prop track. The chair is placed from the sitter's lowest pelvis frame |
| Retargeted CMU wrists were bent back about 70° (claw hands), and the bind pose splays the fingers | Wrist relaxation toward the rest stance, and a negative finger spread (set from a hand close-up test) |
| Arms hung oddly while seated (mocap) | Hands placed on the lap with IK while she is seated |
| At the hand-off, Nadia's hand stopped 10 cm short of the folder, and the desk pick-up was out of reach | Closer staging; a torso lean toward out-of-reach targets; look-at now runs before the arm IK, so turning the chest no longer drags the hands off their targets |
| A carried bag was glued to the wrist angle | The bag hangs from the palm, oriented by heading, with a damped swing |

## Honest assessment against your priorities
| Priority | Status |
|---|---|
| Natural walking: weight transfer, knee bend, foot planting, arm movement | **Good** (mocap plus pinning). The walk starts from standing and stops with a phase-matched blend. Walking with a turn was only retargeted, not demonstrated |
| Smooth transitions: standing, walking, stopping, sitting | **Good** for stand → walk → stop and stand → sit → stand (from near the chair). **Not automated:** a long walk that ends exactly on the chair |
| Head turns, eye direction, blinking, breathing | **Good.** The head lags the eyes, the lids follow the gaze, blinks close completely, breathing is subtle |
| Restrained documentary body language | **Good** with authored gestures. Raw conversation mocap is not suitable. Restraint and wrist relaxation are on by default |
| Hand and finger gestures | **Acceptable:** open, present, pinch, grip, point and relaxed read correctly at medium shot. Fingers are posed (CMU has no finger data); close-up hand acting would need authored poses per prop |
| Reach, hold, carry, point, exchange | **Demonstrated:** reach and lift with a torso lean, a two-hand exchange with measured contact, carrying a hanging bag, pointing |
| Character interaction, eye contact, spacing | **Good:** 96–100% eye contact within range; staging is scripted per shot |
| No clothing penetration, foot sliding, floating limbs, bad joints | Foot sliding solved; no floating; no backward knees. Clothing: small residual contacts, invisible at 1080p, plus a known static collar contact. Elbows reach 46–52° in gestures and reading, which is natural, with no candy-wrapper twisting seen in review |
| Natural expression transitions | **Good:** eased, with brows leading and the mouth lagging. Mouth shapes remain weak (backlog) |
| Complete eyelid closure | **Verified** (0 eyeball pixels when closed) |

**Remaining weaknesses:**
- Hands are the weakest part in close-ups.
- The desk pick-up leaves a 22 mm palm gap. The fingers still touch the folder in the render, but the bend is deep.
- The talk mocap is unusable for this register.
- Turning in place and walk-to-chair path planning are not built.
- Render cost at standard quality is about 37 s per second of footage on this machine.

All of these are recorded in `charlab/BACKLOG.md`, together with the hairstyle, mouth, teeth, hair-rendering and
facial-lighting items. Female characters are **not** restricted to pulled-back hair; it is only what the current
generator produces.

## Decision needed (Motion gate)
- **(a)** Approve these motion capabilities and proceed to **M4.1 (one set)** and **M4.2 (performance proof inside
  HyperFrames)**, keeping production on Rig v4 until the M5 acceptance test.
- **(b)** One more motion pass first, for example on hands in close-up, turning in place, or walk-to-chair.
- **(c)** Stop the 3D character track.

I recommend **(a)**.

## Evidence
- **Videos** (full size, 1920×1080, not in git), in `projects/charlab_m3/`:
  - `d1_arrival.mp4`, `d2_sit.mp4`, `d3_conversation.mp4`, `d4_handoff.mp4`;
  - lean versions `d1_arrival_lean.mp4`, `d3_conversation_lean.mp4`.
- **Sheets:** `projects/charlab_m3/sheets/` (12 frames per demo, plus standard vs lean). Compressed copies are in
  `epoch-ledger/charlab/evidence/m3_*.jpg`.
- **QA and timing JSON:** `projects/charlab_m3/qa/`. Every frame is in `.runtime/charlab/m3frames/`.

## Reproducibility
```
M=.runtime/charlab/mocap   # CMU BVH files from the cmu-mocap mirror (see charlab/README.md)
for c in elias_c nadia_c; do
  BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
    epoch-ledger/charlab/specs/$c.json .runtime/charlab/out_m3 --bvh idle=$M/137_28.bvh:18.9:22.4 --bvh walk_start=$M/82_08.bvh:8.0:14.2 \
    --bvh walk_stop=$M/16_34.bvh:0:2.9 --bvh walk_turn_r=$M/16_19.bvh:0:3.4 --bvh sit=$M/113_15.bvh:0.3:7.0 \
    --bvh talk=$M/19_08.bvh:0.4:9.0 --bvh listen=$M/18_08.bvh:2.4:9.6
  python3 epoch-ledger/charlab/prepare_textures.py .runtime/charlab/out_m3/${c}_tex --spec epoch-ledger/charlab/specs/$c.json
done
node epoch-ledger/charlab/motion_render.mjs --demo epoch-ledger/charlab/motion/demos/d4_handoff.json --chars .runtime/charlab/out_m3 \
  --three .runtime/charlab/three/r0.186.1 --out OUT --qa --mp4 OUT/d4_handoff.mp4 [--quality lean]
python3 epoch-ledger/charlab/motion_sheets.py .runtime/charlab/m3frames projects/charlab_m3/sheets
```
