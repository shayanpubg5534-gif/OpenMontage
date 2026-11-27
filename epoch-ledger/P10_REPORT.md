# P10 — Production optimisation and character animation (visual approval gate)

**Status:** experimental and opt-in (`epoch-ledger/charlab/p10/`). 2.5D Open Peeps is the approved primary direction
for human characters; this P10 implementation is **not** an approved production implementation.
- Preserved and unchanged:
  - P9 (`charlab/p9/`) and every earlier experiment;
  - the 3D character system, archived as an alternative;
  - Rig v4, `render.py`, the P5 renderer and production defaults.
- The only edit to an existing file is an opt-in `video` shot type in the lab's `hf_sequence.py`. Every other shot type
  builds exactly as before.
- Free local tools only. Nothing was purchased or commissioned. Restricted raw assets stay in `.runtime/`.
- Narrator-led: Kokoro voice-over and gold captions. The characters act but never lip-sync, and no open-mouth face is
  used.

Date: 2026-11-27.

**Deliverables** (in `projects/charlab_p10/`; compressed copies in `charlab/evidence/p10_*.jpg`):

| File | Content |
|---|---|
| `p10_narrated_test.mp4` | 16.5 s, 1920×1080, 30 fps. Narrated test with captions, interaction, a gesture and two financial graphics |
| `frames/t*.png`, `frames_sheet.png` | Representative frames |
| `joints_sheet.png` (`joint_elbow.png`, `joint_wrist.png`) | Jointed limbs at several angles |
| `sheet_wardrobe_v2.png` | Formal wardrobe |
| `sheet_views_poses.png`, `sheet_busts.png` | Art-coverage survey: views, and bust bodies for close-ups |

## 1. Rendering optimisation

### What changed
P9 rendered the moving 3D set for every frame and re-rasterised the vector characters, lighting filters and occlusion
masks for every frame. P10 removes each repeated cost:

1. **Cached static plates.**
   - The set is rendered as one still per camera set-up: about 19 s each, against 325–356 s for a P9 moving shot.
   - The still uses the P5 renderer and the P4 cinematic look (Balanced). The depth pass and anchor points come from
     the same camera.
2. **2D camera with depth-layered parallax.**
   - Slow zooms and pans are 2D moves of the plate.
   - The depth pass splits the plate. The part of the room beyond `farFrom` moves by a fraction (0.45) of the near part,
     so the room still reads in depth.
   - The whole plate sits underneath, so nothing ever uncovers a hole.
3. **Reusable depth masks.**
   - The occluders are the set geometry nearer than each character (desk, books, chairs).
   - They and the near parallax layer are cut from the plate once per shot, as transparent images drawn over the
     characters. There are no per-frame masks.
4. **Efficient compositing.**
   - Each character is rasterised once per shot into bitmap layers at the size it is shown: body, one head per
     expression, and one layer per rig piece.
   - The window lighting is baked into each layer. Pieces are cut from the lit figure, so no light runs along a cut.
   - Per frame, only CSS transforms and visibility change. Capture is a fast lossless screenshot.
   - Film grain and vignette moved to ffmpeg, where they are cheap.
   - Measured per frame (one worker, shot A): 1.04 s with the first P10 draft (SVG every frame) → **0.36 s**.
5. **Safe parallel rendering** (`render_shot.mjs`).
   - Each shot is split into contiguous frame ranges, rendered by independent workers, each with its own browser and
     output file.
   - The segments are joined by stream copy, and the joined frame count is checked.
   - A frame is a pure function of the shot spec and its frame number, so results do not depend on the worker count.
   - Shot A (171 frames): 2 workers 36.7 s, 3 workers 32.5 s, 4 workers 27.9 s.

Moving 3D environments remain available (the P5/P9 path) for shots that genuinely need a 3D camera move. They are no
longer the default for character shots.

### Measured (cold run of `run_p10.sh`: caches cleared; 4 vCPU Linux cloud container, no GPU, 16 GB)

| Step | Wall time | Peak RSS |
|---|---|---|
| Narration (Kokoro + Whisper words + caption pages) | 16.9 s | 1.4 GB |
| Set stills, 3 cameras | 18.7 + 19.7 + 18.4 s | 1.4 GB |
| Depth pass + anchors, 3 cameras | 4.6 + 4.8 + 4.6 s | 0.9 GB |
| Painterly pass, 3 plates | 0.8 s each | 0.3 GB |
| Cast and performance (`prepare.py`) | 1.3 s | 0.1 GB |
| 2.5D shots (4 workers): A 171 / B 182 / C 142 frames | 29.7 + 25.5 + 22.7 s | 6.5 GB |
| HyperFrames build + render (`render.py`: graphics, gold captions, narration, 4 jobs) | 1.0 + 79.6 s | 6.4 GB |
| **Total, finished narrated film** | **249.9 s for 16.5 s** | **6.5 GB** |

### Comparison with P9

| | P9 (17 s, silent) | P10 (16.5 s) | Change |
|---|---|---|---|
| Video stages only (like for like: plates, depth, paint, characters) | 1,290 s → **76 min per finished minute** | 152.4 s → **9.2 min per finished minute** | **8.3× faster (−88%)** |
| Finished film, including narration, captions and graphics | not produced | 249.9 s → **15.1 min per finished minute** | — |
| Revising the characters only (plates reused) | 436 s → 26 min per minute | 79 s → 4.8 min per minute (+80 s to re-finish) | 5.4× faster |
| Peak memory | 2.5 GB | 6.5 GB with 4 workers (about 1.6 GB per worker; 2 workers ≈ 3.2 GB) | Higher, by choice |

- **Estimated compute cost:**
  - Assumption: a comparable 4-vCPU cloud machine costs about $0.15–0.25 per hour.
  - On that basis a finished narrated minute costs roughly **$0.04–0.06**, against $0.20–0.35 for P9's silent minute.
    This is an estimate, not a quote.
- **Output:** 1080p30 is unchanged. The plate is a still from the same 3D renderer and the characters are sharper
  (rasterised at their shown size).

## 2. Character improvements

### Jointed arms on the artist's own drawing (`rig.mjs`, `joints_sheet.png`)
Clean joints are built in, using two techniques cut-out animators use:

- **Joint under clothing (wrist).**
  - The hand is cut from the drawing and placed *beneath* the body, so the artist's rolled cuff covers the joint.
  - The hand turns −12° to 0° with no visible seam. One tiny ink cap of the artist's line weight closes the corner
    where the cut meets the outline.
- **Joint disc (elbow).**
  - The forearm and hand turn about the elbow over a disc in the sleeve colour, drawn in the artist's line weight
    beneath everything.
  - At rest the disc is hidden. In a bend it fills the wedge that opens, as a rounded elbow in the artist's line.
  - Range: **−15° to +12°**. P9's cut-out showed a seam beyond about 5°.
- **Hairline fix.**
  - A clip-path anti-aliases each stacked layer of the artwork separately, so the white base under a fill bled through
    as a light line along every cut.
  - Pieces and cuts are now masks, applied to the flattened group, and the line is gone (verified at 8× zoom).
- **Proportions, line weight and identity are untouched.** Only rigid rotations of pieces of the drawing are used,
  with nothing warped or redrawn.
- **Limits:**
  - Each rig is placed by hand for one pose (about 20 minutes with `grid.mjs` and `rig_test.mjs`).
  - The shoulder cannot rotate: the drawing has nothing behind the upper arm.
  - Upper arm, forearm and hand as fully separate parts would need art drawn that way. Open Peeps poses are drawn whole.
  - Two rigs exist: `pointing_finger-1` (elbow) and `robot_dance-1` (wrist).

### Three-quarter and side views (`sheet_views_poses.png`, survey of all 26 standing poses, 11 sitting, 30 busts, 50 heads)
- **Three-quarter is the artwork's native view.** Every head, face and body is drawn three-quarter, facing right.
  Mirroring gives the other side; P10 uses this for the banker.
- **No profile, back or front-facing views exist** in the file. Turning a character on screen, or reverse and
  over-the-shoulder shots, cannot be done without new art.
- We did not distort front-facing art to fake a turn.
- **Bust bodies** (30, several with gestures) are drawn for medium shots and close-ups. They are available for
  dedicated close-up art in future, but P10's close-ups use the standing figures so that each character stays
  continuous across cuts.

### Formal business clothing (`sheet_wardrobe_v2.png`)
- `wardrobe2.mjs` recolours the artist's own fill shapes, chosen by index after a probe, rather than by guessing
  shapes. That fixes P9's mis-detections.
- The tie is drawn in the artist's line weight. Results:
  - a **dark suit with white shirt and tie** (blazer-4);
  - a **collared shirt and tie** (shirt-3, the artist's own collar);
  - the **banker's navy blazer and blouse** with leather shoes (used in the film);
  - **close-up busts** (button shirt and tie; coat, shirt and tie).
- **Limits:**
  - Trousers drawn as solid ink stay black. The suit is therefore made charcoal to match rather than navy.
  - Ties are our addition.
  - Period dress still needs new parts in the Open Peeps style.

## 3. Cinematography (applied in the test)
- **Medium two-shot and two medium close-ups**, with locked cameras and only a slow 2–3% push-in. There is no
  unnecessary camera movement.
- **Brighter:** plate exposure raised (1.12 → 1.32), haze reduced, and a gentle vignette.
- **No foreground blur.** P9's blurred plant is gone.
- **Lighting and integration:**
  - The window side drives a form shadow and a warm rim.
  - The rim never lightens the artist's ink: it is masked to non-ink pixels. P9's grey "sticker" outline is fixed.
  - A slight ambient tint, contact shadows, and the plate's own depth of field behind the close-ups.
- **No repeated poses:**
  - The baker explains and gestures twice (on "loan" and "ten thousand dollars").
  - The banker listens, nods and smiles, then records and credits with a deliberate nod.
  - The baker's close-up ends on a smile and a nod.

## 4. Validation: the narrated test (`p10_narrated_test.mp4`)
**Narration (Kokoro):**
> "A baker asks his bank for a loan of ten thousand dollars. No vault is opened. No cash changes hands. The banker
> simply records the loan, and credits his account. Ten thousand new dollars now exist."

| Requirement | Where |
|---|---|
| Character interaction | A (0–5.7 s): the baker explains, the banker listens, nods and answers with a smile |
| Meaningful gesture | A: the forearm rises at the elbow on "loan" and again on "ten thousand dollars" (jointed rig, up to −16°) |
| Cinematic framing | Medium two-shot → banker close-up (B, 5.7–11.75 s) → baker close-up (C, 11.75–16.5 s) |
| Financial motion graphic | B: the bank's balance sheet: the loan appears under *Assets* on "loan" and the deposit under *Liabilities* on "credits" ("One keystroke, two entries"). C: "New money" counts to $10,000 on "ten thousand" and turns gold on "exist" |
| Narrator-led, no lip sync | Voice-over throughout; faces change expression only, with mouths closed |
| Standards | Gold-highlight captions and narration through `render.py` (HyperFrames, unmodified); loudness −16.1 LUFS |

**QC** (`qc.mjs --video`):
- Passed: no black frames, no flashes, no freezes, consistent opening.
- Cuts detected at 5.7 s and 11.77 s, as intended.
- Loudness −16.1 LUFS, true peak −4.5 dBFS.

**Temporal stability:**
- Frame-to-frame change: median 0.56, p95 1.50 (cuts excluded).
- The largest non-cut changes, 5.3 and 3.7, are the graphic cards appearing at 8.5 s. The character regions show no
  spikes.

**Reproducibility:**
- `run_p10.sh` ran cold, from cleared caches through narration to the final QC, with exit code 0, and produced the
  delivered MP4.
- `sheets.sh` rebuilds every investigation sheet.

## 5. Remaining visual limitations
1. **Views:** three-quarter only (mirrorable). Turns, profiles, backs and reverse angles need new art. This is the
   largest remaining creative constraint.
2. **Limbs:** only rigged poses bend (elbow −15° to +12°, wrist −12° to 0°). Shoulders cannot rotate, and a new
   gesture means placing a new rig by hand. Fully separate limbs need art drawn in parts.
3. **Pose continuity:** a character keeps one pose through the film. In the close-up the baker's hand is still raised
   from his gesture. It reads as continuing to explain, but a relaxed pose would need a cut to a compatible pose.
4. **Parallax is subtle by design.** A 2D camera cannot reveal new sides of objects, so strong lateral moves still need
   the 3D path.
5. **Lighting is painted and fixed per shot.** Characters do not receive shadows from set objects such as the window
   frame.
6. **Ink-drawn trousers** cannot be recoloured, so suits are limited to charcoal or black with those poses.
7. **Memory:** 4 workers peak at 6.5 GB. Use 2 workers (≈3.2 GB, about 30% slower per shot) on smaller machines.
8. Each new camera set-up costs about 25 s of set rendering. This is cheap, but every new angle needs a plate.

## 6. Recommendation (for your decision)
The P10 path is practical for regular production on free, phone-operable cloud tooling:
- about **15 min of compute per finished narrated minute**, against P9's 76 min for silent video;
- 1080p30 kept;
- medium shots and close-ups, clean jointed gestures, formal clothing, and narrator-led graphics.

Before approving it as the production implementation, I suggest you review the clip for:
- the look of the 2D camera on locked plates;
- the joint quality in motion;
- the brightness.

The remaining limits are art coverage (views, separate limbs, period wardrobe), which can only be solved with new art
in the Open Peeps style. That would be a decision for you; nothing has been commissioned or bought.

## Reproducibility
```
epoch-ledger/charlab/p10/run_p10.sh [OUT.mp4] [WORKERS]   # cold, end to end; per-step timings in .runtime/charlab/p10/perf.jsonl
epoch-ledger/charlab/p10/sheets.sh [OUT_DIR]               # views survey, joints, wardrobe sheets
node epoch-ledger/charlab/p10/render_shot.mjs SHOT.json OUT.mp4 --workers 4
.venv/bin/python -m pytest tests/epoch_ledger/test_charlab_p10.py
```
- Needs `.runtime/charlab/p8/src/open-peeps.fig` (CC0; not committed, see `charlab/p8/ASSETS.md`).
