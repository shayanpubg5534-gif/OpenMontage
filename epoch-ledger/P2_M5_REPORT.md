# P2 report: M5, the acceptance sequence — approval gate

Status: a 25 s narration-driven documentary sequence, rendered at 1080p30 through HyperFrames with Kokoro narration,
gold captions and no music. It is judged below against the audit's ten criteria and your eight M5 criteria. All work is
experimental. Rig v4 and the production pipeline are untouched (`render.py`, `kit/assemble.py` and `narrate.py` were
used read-only). The experimental character system is not promoted. M4.1 and M4.2 stay the approved technical baseline.
Date: 2026-11-26.

**Video:** `projects/charlab_m5/m5_acceptance.mp4` (not in git; sent with this report).

## 0. What I changed in response to your M5 notes

| Your note | What I found | What changed |
|---|---|---|
| Elias's head looks unnaturally positioned and stuck in place | The gaze turned only the head bone and locked it onto the other person's eyes. Neck and spine stayed still, so the head looked bolted to a fixed target. The seated mocap also leaves the head rolled toward one shoulder (about 10° in Nadia's bank shot) | The gaze now spreads over spine (18%), neck (37%) and head (45%), with pitch limits. It holds eye contact with seeded short aversions (every ~4.6 s, 0.75 s, aside and down) and slow micro-motion. The head is pulled back toward upright when the torso tilts. A new roll levelling keeps the eyes level while pitch and yaw stay with the gaze (`levelRoll`, default 0.8) |
| Characters look like low-budget NPCs | The MakeHuman heads had wide skulls, short thick necks, small eyes and blotchy skin. Hair, clothes and hands are stock proxies | Redesigned **D** characters (below). A rendering look built for illustration instead of cel shading (below). The meshes still limit the result: see §3 |
| Do the base meshes limit quality? Evaluate free alternatives | Blender's **Human Base Meshes v1.4.1** (CC0) have better-designed heads and necks. They are bare sculpt bases: no clothes, hair, expressions or compatibility with our rig, and the stylised heads have cartoon-sized eyes | Not adopted as a drop-in (it would mean rebuilding everything and still needs an artist). Recommended as the starting sculpt for an artist pass |
| A character-design comparison before expensive renders | — | Medium shots, close-ups, three-quarter and profile views of C, D and the CC0 base meshes, rendered with the same lighting (evidence below). I adopted D before rendering any animation |
| Narration-driven visuals as a permanent principle | M4 cut between camera angles of one meeting while the narrator explained payment terms | Recorded in `epoch-ledger/charlab/DIRECTION.md` (to be merged into production after approval). The sequence is built on it: every beat is keyed to the words |
| A bakery must read as a bakery | The M4 bakery reused office pieces (a bookshelf of "bread") | New bakery components and a rebuilt set (below) |
| Lip sync only for spoken lines | — | A `speech` track per character. Nadia speaks one line in her own voice; the narration never moves a mouth |

## 1. The sequence: "Profitable, and broke" (25.0 s)

| Time | Words | Picture |
|---|---|---|
| 0.0–3.4 s | "Every morning, Nadia's bakery sold out." | 3D bakery in warm morning light. The camera pushes in toward Nadia behind a full display case. She looks up at a customer by the door, nods and smiles |
| 2.9–6.2 s | "On paper, it made a profit every month." | Document close-up: her monthly profit-and-loss sheet on the wooden counter. The PROFIT column lights on "profit"; twelve green profits and ticks land in rhythm across "every month" |
| 5.8–14.2 s | "Her flour supplier wanted payment in thirty days. Her biggest customer, a café chain, paid in ninety." | Payment timeline. A flour sack appears on "flour". A day marker travels to day 30 as "thirty days" is said, and £9,000 goes out. A café cup appears on "café". The marker travels on to day 90, £11,000 comes in, and the 60-day wait is marked in red |
| 13.7–19.3 s | "So each month, more cash went out than came in, until the account ran dry." | Bank balance. Monthly cash out (red) and in (green) bars grow month by month. The balance line and counter fall from £12,000 and reach £0 on "dry", where the zero line turns red and "account empty" appears |
| 18.6–22.8 s | Nadia: "We're busy every day. I just can't pay my suppliers." | The bank. Close-up of Nadia across the desk, lip-synced, with an open-hand gesture on "busy every day". She looks down on "can't pay", then back to Elias |
| 22.8–25.0 s | "Profitable, and broke." | Wide shot: the two of them at the desk. She looks down, he lowers his eyes to the papers. Narration only, so no mouth movement |

Transitions carry the story: the push into the bakery hands over to the ledger on the counter. The ledger lifts away
into the timeline. The timeline zooms into its red gap, which becomes the cash chart. The chart dissolves into the
bank meeting.

## 2. Assessment against the criteria

### Your M5 criteria
| # | Criterion | Result | Notes |
|---|---|---|---|
| 1 | Premium editorial illustration, not cel-shaded game | **Improved, not yet premium** | New `editorial` look: soft variance shadows, painterly two-band light with a warm skin terminator, coloured outlines per material, crease ambient occlusion, haze and depth of field per camera key. The 2D scenes use the same paper, ink and palette. The 3D still reads as illustrated 3D rather than painted illustration |
| 2 | Character acting (weight, sitting, gestures, gripping, expressions, posture; no glitches or robotic poses) | **Mostly met for this scene** | Seated posture is upright; the gesture rises and settles over about 10 frames without a pop; gaze and expressions follow the line. The analysis flags forearm accelerations in Nadia's two hand moves (≤ 23 m/s²); frame-by-frame review shows no visible pop. This sequence has no sitting transition or grip; those were covered in M4 |
| 3 | Character appearance (facial shading, hair, clothing folds, hands, facial details; not photorealistic) | **Not met to a premium standard** | D is a clear step up from C: smaller skull, longer neck, larger eyes, refined nose and mouth, smoother skin. Hair is still a helmet-like proxy, the jacket's texture is blotchy, the hands are thick and the teeth are flat grey. This is the largest remaining gap (§3) |
| 4 | Environment quality (geometry, set dressing, materials, props; a bakery reads as a bakery) | **Met for the bakery; adequate for the bank** | Bakery: glazed display case with tiers of boules, loaves and croissants; slanted bread rack with baguettes; deck oven with a warm window; chalkboard menu; till; baskets of rolls; flour sacks; pendant lamps; subway tiles; beamed ceiling. Props are still built from primitives |
| 5 | Cinematic lighting (soft directional light, contact shadows, depth, DOF) | **Met** | Soft key with variance shadows and contact shading; light through the beams; haze for depth; DOF on the close-ups |
| 6 | Documentary storytelling (close-ups, financial diagrams, documents, timelines synced to narration) | **Met** | Three 2D beats (document, timeline, chart) between two 3D scenes, every value revealed on the word that says it |
| 7 | Lip sync only where a character speaks | **Met** | Only Nadia's own line drives her mouth (Kokoro `bf_emma`, Whisper word timing, six mouth units, loudness envelope). The narration over the bakery and the wide bank shot moves no mouth |
| 8 | Performance (caching, determinism, parallel rendering; Balanced mostly, Standard where useful, Lean for drafts) | **Met, but slow** | See §2b. Lean was used for the draft, Balanced for the bakery and the wide, Standard for the lip-sync close-up |

### The audit's ten criteria
The audit's scenario was "The Invoice"; this sequence is the M5 story you specified, so the contact-heavy checks apply
only partly.

| # | Criterion | Result |
|---|---|---|
| 1 | Hand-to-socket ≤ 3 px, no penetration | **Not exercised**: no held props in this sequence (M4: 0 mm hand contact). Hands rest on the desk by IK; no penetration seen in review |
| 2 | No prop without an owner | **Pass** (no loose props) |
| 3 | Joint limits; nothing hidden during contact | **Pass** in review |
| 4 | Determinism | QC_DET |
| 5 | Diagram values labelled when spoken and match the model; no negative balance without an overdraft | **Partly met.** Timing passes: day 30 and 90 land on "thirty" and "ninety"; the twelve profits land on "every month"; the balance reaches exactly £0 on "dry" (the first draft dipped to −£500 and was corrected). But the numbers are illustrative values written into the scene (sales £11,360–12,240 a month, costs £10,180–10,620, £9,000 out at day 30, £11,000 in at day 90, monthly cash out £9,000 vs in £6,500). They are not generated from a financial model file, which the audit requires for production |
| 6 | No text collision or cropping; captions in their band | LAYOUT |
| 7 | Frame scan: no black, flash, freeze or opening jump; loudness on target | QC_SCAN |
| 8 | At least four shot sizes; no clip repeated within 8 s | **Pass**: wide, medium push-in, close-up, insert (document) and graphic frames; no repeated clip |
| 9 | ≤ 0.6 s per frame for character shots | **Fail**: see §2b |
| 10 | Human review | Done at normal speed on the draft and the final: 2 fps strips, frame-by-frame strips around the gesture, full-resolution frames. It found eight problems, all fixed before the final: icons displaced, chart bars showing early, area under the curve showing early, ledger ticks visible as dots, a row under the captions, the gap label barely on screen, the head roll, and the negative balance |

### 2b. Performance [M] (4-core CPU container, no GPU; 2 render workers)
| Run | Wall time | Peak memory | Notes |
|---|---|---|---|
| PERF_TABLE |

Per-chunk times of the full render: bakery (Balanced, 3D) CHUNK_BAKERY; ledger, timeline and chart (2D) CHUNK_2D; bank close-up
(Standard) CHUNK_CLOSE; bank wide (Balanced) CHUNK_WIDE. The Standard close-up alone costs about 5 s per frame, and
character shots in Balanced cost 1.8–3 s per frame, so criterion 9 (≤ 0.6 s) fails on this machine. The draft (Lean
throughout) took 422 s.
Splitting the bank shot at its cut into two cached windows saved 60 s (939 → 879 s) and lets the expensive close-up be
re-rendered without the wide. Options if speed matters more than close-up quality: Balanced for the close-up too (about
−250 s), or more workers on a larger machine (chunks are independent).

## 3. Honest limitations (see `charlab/BACKLOG.md`)
- **Characters are still the weakest part.** D fixes proportions and the face reads better, but the stock MakeHuman
  hair, clothing and hands remain. Premium hero characters need an artist pass: a sculpted head (the CC0 Blender base
  meshes are a good start), modelled hair, tailored clothes with real folds, hand-painted textures. The rig, motion and
  rendering stack can stay; the meshes would be replaced.
- **Lip sync** is letter-based (not phoneme-based), so some consonants are soft. The teeth read flat grey and the mouth
  has no dark interior.
- **Hands** are thick and the finger poses are stiff.
- **Props** are built from primitives; they read correctly but are simple.
- **Speed** fails the audit's per-frame target on this CPU container (above).
- **Audio:** no sound effects yet (the audit scenario asked for original SFX); narration and dialogue only.
- **A closed ceiling** darkened the room through the stage's shadow path even with shadow casting off; worked around
  with an unlit ceiling plane (backlog).

## Decision needed (approval gate)
- **(a)** Accept M5 as the experimental acceptance baseline (look, gaze, lip sync, direction, sequence tooling) and plan
  an artist-led character pass (heads, hair, clothes, hands) on the same rig before production use. **Recommended.**
- **(b)** Ask for another procedural iteration of the characters first (more targets, hair and clothing work). This will
  improve them only modestly; the meshes are the limit.
- **(c)** Change direction (for example, keep characters for wide and medium shots only, and carry close storytelling with
  documents and diagrams).

## Evidence
- **Videos** (1080p30, narration, gold captions; not in git), in `projects/charlab_m5/`:
  - `m5_acceptance.mp4` (final);
  - `draft_lean.mp4` (the Lean draft that was reviewed);
  - `evidence/lipsync_test.mp4` (lip-sync close-up test).
- **Frames** at full resolution: `projects/charlab_m5/evidence/frames/`.
- **Character-design comparison:** `evidence/design_C_vs_D.png` (C and D, front and three-quarter),
  `design_compare_elias_vs_hbm.png` and `design_compare_nadia_vs_hbm.png` (medium, close-ups, three-quarter and profile
  views next to the CC0 base meshes).
- **Look comparison:** `look_cel_vs_editorial.png` and `look_cel_vs_editorial_close.png`.
- **Other sheets:** `bakery_set.png`, `lipsync_mouth_strip.png`.
- **QA:** `evidence/qc.json`, `qc.log`, `layout.json`.
- **Benchmarks:** `projects/charlab_m5/bench/results.jsonl` and logs; render cache log
  `hf_final/.render-cache/render-log.jsonl`.
- **Compressed copies in git:** `epoch-ledger/charlab/evidence/m5_*.jpg`.

## Reproducibility
```
CHARS="elias_d nadia_d" ./epoch-ledger/charlab/build_m4.sh .runtime/charlab/out_m5                   # D characters + clips
.venv/bin/python epoch-ledger/scripts/narrate.py projects/charlab_m5/story --workspace projects/charlab_m5/hf
.venv/bin/python epoch-ledger/charlab/lipsync.py "We're busy every day. I just can't pay my suppliers." \
    projects/charlab_m5/dialogue_nadia --voice bf_emma
.venv/bin/python epoch-ledger/charlab/splice_dialogue.py projects/charlab_m5/story projects/charlab_m5/dialogue_nadia \
    --before n4 --at 19.2 --gap 0.35 --ws projects/charlab_m5/hf
python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/m5_acceptance.py .runtime/charlab/out_m5 \
    projects/charlab_m5/hf_final                          # add --force-quality lean for a draft
python3 epoch-ledger/scripts/render.py render projects/charlab_m5/hf_final --isolate --jobs 2 -o OUT.mp4
node epoch-ledger/scripts/qc.mjs projects/charlab_m5/hf_final/index.html --video OUT.mp4 --every 1
node epoch-ledger/scripts/layout_check.mjs projects/charlab_m5/hf_final/index.html --every 0.25
```
