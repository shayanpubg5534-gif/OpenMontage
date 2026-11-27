# P12 — Production-quality refinement (visual approval gate)

**Status:** experimental and opt-in (`epoch-ledger/charlab/p12/`). This phase refines the P11 system; it is not a
rebuild.

- **Preserved:** P11's method (narration-to-visual map, word-timed events, check and inspect), P10's compositor, the
  hybrid 2.5D and selective-3D approach, the captions, and all earlier versions.
- **The only change to an existing lab file:** opt-in plate-matched lighting in the P10 compositor. The default lighting
  is unchanged and a test checks it.
- **Unchanged:** production defaults, Rig v4, `render.py`, 1080p30, Kokoro narration, gold captions, and no lip sync.
- Free local tools only. Nothing was purchased or commissioned.

Date: 2026-11-27.

**Deliverables** (in `projects/charlab_p12/`; compressed copies in `charlab/evidence/p12_*.jpg`):

| File | Content |
|---|---|
| `p12_passage.mp4` | 30 s, 1920×1080, 30 fps. A new subject: "Sold on", the 2006–2008 US mortgage crisis |
| `frames/`, `frames_sheet.png` | One frame per shot (8 shots) |
| `continuity_sheet.png` | Every allowed body of each character, recoloured only from its identity |
| `compare_continuity_integration.png` | The same character in two shots; default versus plate-matched lighting |
| `narration_visual_map.md` | The timestamped mapping: 11 clauses, 16 concepts, 29 events |

## 1. The validation passage (new subject; a family that is illustrative, with historical events)

> "In 2006, a family signs a mortgage they can barely afford. The lender doesn't keep the loan; it sells it on, bundled
> with thousands of others into a single security. Investors around the world buy it, because it promises steady
> payments. Then house prices fall, and families stop paying. The payments dry up, the securities collapse, and in
> September 2008, Lehman Brothers goes bankrupt."

| Shot | Format chosen for the clause | What is shown |
|---|---|---|
| S1 2.5D | Environmental typography | The couple at the lender's office; a wall calendar reads 2006 on "2006". She smiles and nods on "family" |
| S2 insert | Document close-up + before/after bar | The mortgage agreement; a pen signs it on "signs" (the pen leaves the frame, so it reads as held). On "barely afford", the payment fills about 90% of their income and "little left" is marked |
| S3 3D | Selective 3D | Their folder is stamped SOLD on "keep". The camera pulls back on "sells", "bundled" and "thousands" to reveal thousands of strapped folders, then "One mortgage-backed security" |
| S4 map | Geographic map + flow diagram | Routes to London, Frankfurt, Hong Kong, Tokyo and Singapore on "world"; buyers light on "buy"; payments flow on "steady" |
| S5 chart | Animated financial chart | US house prices rise to a 2006 peak and fall on "fall" (indicative shape of the Case-Shiller national index) |
| S6 2.5D | Character + document prop | At home with her coffee; OVERDUE is stamped on the payment notice on "stop" and her face falls |
| S7 map | Map reprise + before/after | The flows stop and the routes go grey on "dry"; the securities' value is shown before, then collapsing on "collapse" |
| S8 insert | Newspaper close-up + historical timeline | The timeline moves to September 2008 on "September"; the front page reads "Lehman Brothers files for bankruptcy" (masthead fictional, marked illustrative), with BANKRUPTCY underlined on "bankrupt" |

- **Facts used:** US house prices peaked in 2006 and fell. Lehman Brothers (founded 1850) filed for bankruptcy on
  15 September 2008, the largest bankruptcy filing in US history.
- **Marked as illustrative:** the family, the newspaper's masthead, the chart's exact values (the shape is indicative),
  and the bundle size.

## 2. What was refined

### Character consistency (`p12/cast.py`, `p12/continuity.mjs`)
- **Identities:** each character is one identity: head parts, skin and hair, and a wardrobe by garment role (top,
  outer, shoes).
- **Allowed bodies:** each character may only use bodies that depict the **same garments**.
  - Husband: a collared shirt (standing and bust).
  - Wife: a collared shirt (two busts, one holding a mug).
  - Banker: her blazer.
- **Dressing:** each body maps its own fill shapes to roles, so every variant is dressed from the identity and never by
  hand. Poses come only from the artist's bodies; nothing is distorted.
- **Two checks:**
  - on the definitions: head parts, skin, hair and each role's colour;
  - on the **rendered pixels**: the identity's top colour must dominate the body.
- **What the pixel check is for:** it caught a real case the fill check alone would miss. The artist's "Paper" body
  draws its sweater in black ink, so a recolour is invisible; that body is therefore excluded.
- **Result:** 5 of 5 variants pass both checks, with the identity colour covering 79–96% of the body.
- **The P11 problem is fixed:** the banker no longer changes clothes between bodies, because bodies are now chosen by
  garment.

### Artistic integration (opt-in plate-matched lighting in the P10 compositor)
- Each character's ambient tint and form-shadow colour come from the plate around it. The shadow deepens slightly in
  darker rooms but never goes to black.
- The rim light never lightens the artist's ink. The original line work is untouched.
- **The effect is deliberately subtle:** the same wife reads warmer and darker in the office, cooler and brighter at
  home (`compare_continuity_integration.png`).

### Character acting and object interaction
- **Objects move only if something plausibly moves them:**
  - The pen that signs is long enough to leave the frame, so it reads as held.
  - The SOLD and OVERDUE stamps are printed states, not moving objects.
  - The 3D bundle is revealed by the camera; nothing slides on its own.
- **Framing replaces actions the art cannot perform:**
  - signing becomes an insert;
  - "families stop paying" becomes her face and the notice in front of her.
- **Reactions are timed to the words:** she smiles on "family" and her face falls on "stop".

### Visual-explanation variety (`p12/visuals.py`, reusable formats)
- **Formats:** environmental typography (`env_card`), document close-up with a signing pen and a before/after budget bar
  (`document`), geographic map with arcs, buyers, flows that can stop and a value panel (`world_map`), animated chart
  with a turning point (`line_chart`), newspaper front page with a historical timeline (`newspaper`), printed stamp
  (`stamp`), and object label (`label`).
- **Each format is chosen per clause from the map, not from a template.**
- **Mobile readability:** key text is 40 px or more at 1080p, labels are 7 words or fewer, with one idea per element.

### Selective 3D (`p12/three_shot.mjs`, `p12/scenes/stack.js`)
- **A reusable 3D shot renderer:** procedural scenes as modules, the camera keyed from the map, and **static holds
  rendered once**. In S3, 62 of 216 frames were rendered once and reused.
- **The bundle scene:**
  - manila folders with paper fibres, slight irregularity and varied tone;
  - paper-edge sides, woven straps, a timber pallet and a concrete floor;
  - a warm shadowed key light, cool fill and fog.
- **Only visible geometry is real.** The top layers are individual folders and the sides are a textured paper edge, so
  "thousands of folders" cost a few hundred boxes. That cut the frame time from 7–17 s to about 2.8 s.
- 3D is used only where scale and physical reality carry the idea ("thousands … a single security").

## 3. Performance (cold run of `run_p12.sh`; 4 vCPU, no GPU; caches cleared)

| Step | Wall time | Peak RSS |
|---|---|---|
| Narration (Kokoro + Whisper + caption pages) | 20.4 s | 1.5 GB |
| Plan, cast and continuity checks | 0.3 + 1.3 + 0.5 s | 0.2 GB |
| 3 set stills + depth (office, home, desk) | 49.8 + 12.3 s | 1.4 GB |
| Cast and performance (`prepare.py`) | 1.3 s | 0.1 GB |
| 2.5D shots S1, S2, S6, S8 (4 workers) | 11.1 + 11.3 + 8.3 + 19.7 s | 5.2 GB |
| **3D bundle S3** (216 frames, 2 workers) | **210.0 s** | 3.0 GB |
| HyperFrames build + render (6 formats, captions, narration) | 1.3 + 135.0 s | 6.7 GB |
| **Total** | **482.6 s for 30 s** | **6.7 GB** |

| | P10 | P11 | P12 |
|---|---|---|---|
| Minutes of computing per finished minute | 15.1 | 25.2 | **16.1** |
| Share taken by the 3D shot | — | 44% of the time for 23% of the screen | 44% of the time for 24% of the screen |
| Without the 3D shot | — | 14.5 | 9.1 |

- **Faster than P11 despite twice the length and far more formats.** The full-screen formats (map, chart) are almost
  free, and the 3D renderer reuses static frames.
- **Revisions are cheap:** after the cold run, two design fixes re-rendered only the changed scenes in 15–36 s, thanks to
  `render.py`'s per-scene cache.
- **Estimated compute cost:**
  - Assumption: a 4-vCPU cloud machine at about $0.15–0.25 per hour.
  - On that basis: roughly **$0.04–0.07 per finished minute**. This is an estimate, not a quote.

## 4. Quality checks
- **Technical QC (`qc.mjs`):** passed.
  - No black frames, no flashes, no freezes, consistent opening.
  - 6 cuts detected; 2 more are full-screen dissolves between diagrams.
  - Loudness −16.2 LUFS, true peak −4.5 dBFS.
- **Plan check:** 11 clauses, 16 concepts, 29 events; **0 errors, 0 warnings**.
- **Semantic sync on the rendered film:** **29 of 29 events change on screen within ±0.2 s of their words.**
  - The first cold render had 28 of 29: the chart's "fall" line started with an ease-in and showed 0.64 s late.
  - Fixed: the line now starts on its word; the stray pre-draw dot is hidden; the event region was narrowed to where
    the decline begins.
- **Continuity:** 5 of 5 variants pass both the definition check and the rendered check. The same identities appear in
  the office and at home.

## 5. Remaining limitations
1. **Art coverage is still the main limit.**
   - Characters are three-quarter only, with poses fixed per body; no hands-on actions such as typing fingers or
     handing over.
   - Framing and inserts carry those actions.
2. **The wardrobe is limited to the artist's garment families.** A character can only wear bodies drawn with the same
   garment. Busts with props (mug, phone, laptop) exist in only some families.
3. **Locations reuse the bank set** (office close-up, window, desk). A real home or exterior would need new 3D sets or
   plates.
4. **The 3D look is clean and procedural,** better than P11's vault but still simpler than photoreal or art-directed
   models. Its cost is about 1.0–1.5 s per frame of 3D (with static holds reused).
5. **Chart values are indicative,** with a sourced shape. A production episode would plot the published index from the
   series' Ledger of figures.
6. **The plate-matched lighting is subtle by design.** Characters still do not receive cast shadows from objects in the
   set.
7. **Memory peaks at 6.7 GB** in the HyperFrames stage with 4 jobs.

## 6. Recommendation (for your decision)
The system now generalises beyond the banking example: a new subject was planned, built and checked with the same tools.
Every clause is shown on its word, and continuity is enforced and verified. Explanation formats are chosen per clause,
and 3D is used selectively at about 16 minutes of computing per finished minute.

The suggested next step, with your approval, is a full-length pilot on the P12 system, together with a small art brief
for missing coverage (hands-on actions, more garment families with props).

## Reproducibility
```
epoch-ledger/charlab/p12/run_p12.sh [OUT.mp4] [WORKERS]      # cold, end to end, with QC, sync and continuity checks
python3 epoch-ledger/charlab/p12/cast.py FIG OUT && node epoch-ledger/charlab/p12/continuity.mjs OUT
python3 epoch-ledger/charlab/p11/visual_map.py check   epoch-ledger/charlab/p12/map_p12.json
python3 epoch-ledger/charlab/p11/visual_map.py inspect epoch-ledger/charlab/p12/map_p12.json projects/charlab_p12/p12_passage.mp4
.venv/bin/python -m pytest tests/epoch_ledger/test_charlab_p12.py
```
