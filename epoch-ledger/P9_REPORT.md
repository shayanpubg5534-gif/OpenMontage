# P9 — 2.5D character animation test in the bank (visual approval gate)

**Status:** experimental and isolated (`epoch-ledger/charlab/p9/`). It is a provisional direction, not a production
standard.
- Rig v4, the P5 renderer, the P4 cinematic look, `render.py`/HyperFrames and production defaults are unchanged. P9 only
  *calls* the P5 renderer to make set plates without characters.
- The 3D lab is intact. The Fab businessman is archived as an evaluated alternative (section 7).
- Nothing was purchased. No paid APIs were used and no artists were contacted. Restricted raw assets stay in
  `.runtime/` (git-ignored).
- The narration standard holds: the clip is silent. Nobody speaks, there is no lip sync, and no open-mouth "talking"
  face is used.

Date: 2026-11-27.

**Deliverables** (in `projects/charlab_p9/`; compressed copies in `charlab/evidence/p9_*.jpg`):

| File | Content |
|---|---|
| `p9_bank_25d.mp4` | 17 s, 1920×1080, 30 fps, silent, 8.7 MB. Two shots: wide (9 s) and front-left (8 s) |
| `frames/t*.png` | Six representative full-resolution frames |
| `frames_sheet.png` | The six frames, labelled |
| `wardrobe_sheet.png` | Wardrobe feasibility: suit trousers, collar and tie, business shoes |

## 1. What the clip shows

| Requirement | How it is done | Where to look |
|---|---|---|
| Irregular blinking | Seeded intervals of 2.2–5.5 s, 3–4 frames closed, occasional double blink; the artist's own "Eyes Closed" face | Throughout; both characters |
| Breathing and weight shifts | The body scales ±0.6% vertically from the feet on a 3.7 s cycle, and the head rises with it. A slow idle sway (±0.35°) and eased weight shifts (0.5–0.7°) rotate the whole figure about the feet, so the feet stay planted | Banker 3.3 s, 7.6 s; client 1.9 s, 6.2 s |
| Head turns, tilts and nods | The head layer rotates about the neck: eased tilts of 3–5° and nods (a dip of up to 6.5° and return over about half a second) | Banker nods at 6.0 s and 6.9 s; client nods at 2.3 s and 5.4 s |
| Expression changes | Switches between the artist's own faces with a 3-frame dissolve: Calm → Solemn → Serious → Smile; Serious → Driven → Calm | Shot 1: 2.6 s, 3.6 s, 5.2 s, 6.6 s, 7.4 s |
| Pointing and explanatory gestures | The client's pointing arm is a limited cut-out (see 2). It beats up and down 3–5° in time with the "explanation" | Shot 1: 1.0–8.0 s |
| Two-character interaction | The client explains and points while the banker listens, then reacts (solemn, then nods and smiles). In shot 2 the roles are reversed: the client listens with crossed arms and smiles at 3.4 s | Whole clip |
| Camera movement and parallax | Slow push-in (shot 1) and lateral drift (shot 2) on the real 3D set. The characters are placed through the same camera every frame, and the blurred foreground plant moves faster than the background | Whole clip |
| No abrupt pose swaps | No pose is swapped on screen. The client's pose change (pointing → crossed arms) is hidden by the cut at 9.0 s. Everything else is layer animation on one pose | Cut at 9.0 s |
| Artwork not distorted | Only rigid rotations, the small breathing scale and fill colours are applied. The line work is never warped or redrawn | Close-ups |

## 2. Technique

1. **Set plate.**
   - The P4 cinematic bank is rendered with no characters by the P5 renderer (`cin_balanced`), from the demos
     `motion/demos/p9_shot{1,2}.json`.
   - The plate is cached. Revising the characters does not re-render it.
2. **Slightly painterly environment.**
   - An ffmpeg pass (`p9/paint_filter.txt`): edge-preserving bilateral smoothing, a warm grade and soft ink edges at
     42% multiply.
   - It is deliberately subtle, so that the set still reads as the approved environment.
3. **Camera track and depth.**
   - `cam_track.mjs` replays the same camera in the motion viewer.
   - It projects the world anchors (feet, heads, window, foreground) per frame.
   - It writes a set depth pass in millimetres.
4. **Characters** (`prepare.py`, `animate.mjs`).
   - These are the artist's Open Peeps parts (CC0), composed and recoloured as in P8.
   - Every face a shot needs is embedded as a switchable layer.
   - Each frame is laid out in HTML/SVG in headless Chromium and piped to ffmpeg.
5. **Limited cut-out arm.**
   - A clipped copy of the drawn arm rotates about the elbow.
   - The original arm under it is masked in character space.
   - This gives a real bending gesture without new art.
   - Limit: beyond about 5° a seam shows at the elbow, so beats are capped there.
6. **Integration** (requirement 2):
   - *Lighting:* light direction comes from the projected window each frame. A form shadow falls on the side away from
     the window, with a subtle rim on the window side (32%) and an ambient tint from the room.
   - *Contact and cast shadows:* a soft contact shadow under the feet and a cast shadow on the floor, directed away from
     the window.
   - *Depth:* the characters' scale and position come from the camera every frame. In shot 2 the client gets a slight
     blur (2.2 px) to follow the plate's depth of field. There is no atmospheric haze on the farther character yet.
   - *Foreground occlusion:* the set depth is compared per pixel with each character's depth. The desk, books and chair
     correctly cover legs, for example the banker's legs behind the books in shot 2.
   - *Finish:* shared film grain and vignette over set and characters, so both sit on one surface.

## 3. Performance (measured; 4 vCPU Linux cloud container, no GPU)

| Step | Wall time | Peak RSS |
|---|---|---|
| Set plate, shot 1 (270 frames) | 356.3 s | 1.75 GB |
| Set plate, shot 2 (240 frames) | 324.8 s | 1.74 GB |
| Painterly pass (1 / 2) | 38.4 s / 31.6 s | 0.45 GB |
| Camera track + depth (1 / 2) | 54.2 s / 48.4 s | 1.01 GB |
| Characters and composite (1 / 2) | 215.1 s / 203.0 s (0.79 / 0.84 s per frame) | 2.47 GB |
| Assemble | 18.0 s | 0.70 GB |
| **Total** | **1,290 s (21.5 min) for 17 s of video** | **2.5 GB peak** |

- **First render: about 76 min of wall time per finished minute** on this 4-vCPU machine. The set plate is 53% of
  that.
- **Character-only revision** (plate, paint and depth reused): 436 s for 17 s, about **26 min per finished minute**.
- **Estimated production cost:** CPU only, with no licences or API fees.
  - Assumption: a comparable 4-vCPU cloud machine costs about $0.15–0.25 per hour.
  - On that basis the compute is roughly **$0.20–0.35 per finished minute** at first render. This is an estimate, not a
    quote.
  - Shots are independent, so they can run in parallel.
- **Memory:** the peak is 2.5 GB (Chromium compositing at 1080p), well within the container.

## 4. Inspection (frame-by-frame review, automated QC, temporal statistics)

- **Automated QC** (`qc.mjs --video`):
  - Passes: no black frames, no flashes, no freezes, consistent opening, one detected cut at 9.0 s (intended).
  - Warning: no audio (intended for this test).
- **Temporal stability:**
  - Mean absolute frame-to-frame change: median 0.46, p95 0.85, max 1.37 (fades and the cut excluded).
  - No spikes, so there are no pops or jumps.

| Check | Result |
|---|---|
| Unnatural movement | Mostly natural and restrained. Nods and tilts are eased. The breathing is subtle. The client's arm beats read as emphasis, but they are small (≤5°) |
| Sliding feet | None. Sway and weight shifts pivot about the feet, and the feet are re-projected from the same world point every frame |
| Detached parts | None found. The neck stays covered through tilts and nods (checked in close-ups). The elbow seam is invisible at ≤5° |
| Abrupt pose changes | None on screen. The one pose change is hidden by the cut |
| Shadow consistency | Contact and cast shadows follow the window direction in both shots and agree with the set's own shadows. Shadows are soft and painted, not ray-traced, so they do not wrap over furniture |
| Artifacts | No haloes on the occlusion edges at 1080p. There is a slight softness where the desk covers the client in shot 1, from the depth-pass resolution |

## 5. Wardrobe feasibility (`wardrobe_sheet.png`)

- **Method:**
  - `wardrobe.mjs` recolours the artist's own fill shapes: trousers to match the jacket, shoes to dark leather.
  - It adds a shirt collar and tie as new shapes, drawn in the artwork's line weight with a slight hand-drawn wobble.
  - The artist's line work is never altered.
- **Result:**
  - Suit trousers and business shoes are convincing and in the visual language.
  - The collar and tie read well on the investor. On the banker they work, but the shirt opening had to be set by hand,
    because that drawing's shirt is part of the ink line work.
- **Limits:**
  - The investor's trousers are drawn as black ink, so they cannot be recoloured to match a grey suit without new art.
  - Jackets are the artist's casual blazers: soft lapels, no buttons or pocket squares.
  - Collars and ties are our additions. An illustrator would draw them better, and a full formal and historical
    wardrobe (waistcoats, double-breasted suits, period dress) needs new parts in the Open Peeps style.
- **Verdict:** contemporary business dress is feasible for a test cast with what we have. Period and formal dress is
  not.

## 6. Remaining limitations

1. **Front views only.**
   - The Open Peeps art has no three-quarter, profile or back views. Cameras must stay in front of the characters.
   - Reverse and over-the-shoulder shots, and characters turning, are impossible without new art. This is the largest
     constraint on cinematography.
2. **Limited limbs.** Arms and legs are drawn into poses. Bending gestures beyond small cut-out beats need limbs drawn
   as separate parts.
3. **Poses are fixed per shot.** Pose changes need a cut or compatible poses. The banker keeps one pose (`blazer-3`),
   because the other blazer poses also change the trousers or legs.
4. **Wardrobe** is casual contemporary by default (section 5).
5. **Integration ceiling.** The shading is painted, not physically lit. It holds up at documentary distances, but
   characters do not receive shadows from the set, for example from the window frame.
6. **Shot 1 composition.** The client is small and partly behind the desk, and the blurred foreground plant reads as a
   green smear. A different foreground element or framing would help.
7. **Painterly treatment** is subtle. A stronger version risks losing the approved set look and needs a separate
   decision.
8. **Render cost** is dominated by the 3D plate. A static or illustrated background would cut it substantially.
9. **No audio** in this test. A narrated test would add Kokoro narration and gold captions, with no lip sync.

## 7. Preservation

- **3D lab:** unchanged. All earlier versions are kept, and the P3–P8 demos, tools and tests are untouched.
- **Fab businessman:** archived as an **evaluated alternative** (P8). He is not developed further.
  - The raw files (GLB, `.blend`, FBX) remain only in `.runtime/` and are never committed. A test enforces this.
  - Provenance stays recorded in `charlab/p8/ASSETS.md`.
- **Restricted raw assets:** none are tracked in git. A test checks for `.fig`, GLB, `.blend` and FBX files that
  belong to the evaluated assets.

## 8. Recommendation (for your decision)

The 2.5D/hybrid direction can carry restrained, believable documentary acting with:
- blinking, breathing, nods, expressions and small gestures;
- correct depth and occlusion inside the real 3D set;
- a free, fully automated, phone-operable pipeline.

The main gaps are art coverage, not the pipeline: front-only views, limbs drawn into poses, and formal or period
wardrobe.

If you want to go further, the next step (after your approval) would be a small, scoped art brief: three-quarter views,
separate arms and hands, and formal wardrobe parts for a two- to three-person cast in the Open Peeps style. No
commission or purchase has been made or arranged.

## Reproducibility

```
epoch-ledger/charlab/p9/run_p9.sh [OUT.mp4]      # all steps, each timed into .runtime/charlab/p9/perf.jsonl
node epoch-ledger/charlab/p9/sheet.mjs OUT.png "TITLE" COLS TILE_W "label::file" ...
.venv/bin/python -m pytest tests/epoch_ledger/test_charlab_p9.py
```
- `run_p9.sh` chains the commands that were run step by step for this test, with the same arguments and data files
  (`p9/points_shot{1,2}.json`, `p9/paint_filter.txt`).
- It needs `.runtime/charlab/p8/src/open-peeps.fig` (CC0; not committed, see `charlab/p8/ASSETS.md`).
