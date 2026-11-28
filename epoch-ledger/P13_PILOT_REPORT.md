# P13 animated pilot: the mortgage passage, re-directed (awaiting your review)

**Status:** rendered, checked and awaiting your review. **Not promoted to the production baseline.** P12 remains the
approved baseline and is untouched: its narration, words, captions, scripts, assets and film are read only.

**Files:**
- **Film:** `projects/charlab_p13/p13_pilot.mp4` (1080p30, 30.0 s, H.264 and AAC, 49 MB; not committed, like P12's film).
- **Evidence:**
  - `charlab/evidence/p13/pilot_contact_sheet.jpg`: 24 frames across the film.
  - `charlab/evidence/p13/compare_p12_vs_p13_pilot.jpg`: P12 on the left and P13 on the right, at the same nine
    narration times.
- **Reproduce cold:** `epoch-ledger/charlab/p13/run_p13.sh`.

## 1. What the film does (the approved treatment, animated)

| Time | Narration | On screen |
|---|---|---|
| 0.0–2.45 | In 2006, a family signs… | Their kitchen at dusk, with the street of similar houses through the window and a "2006" super. On "family" she nods; on "signs" he leans in over the papers. |
| 2.45–5.09 | …a mortgage they can barely afford. | Cut on action to the table from above: the pen signs, with the hand out of frame. The payment bar fills nearly all their income, and "little left" is marked in red. |
| 5.09–5.94 | The lender… | Back at the table he sits back, relieved, and she looks away to the window. The camera drifts after her look. |
| 5.94–10.84 | …doesn't keep the loan; it sells it on, bundled with thousands of others… | The street dissolves into the town seen from above, with their house in gold. Their loan runs to "their lender", which sells it on into the pool as the camera pulls back. Then the whole town's loans follow, and the pool fills ("thousands of loans"). |
| 10.84–12.54 | …into a single security. | Match cut: the pool becomes the plinth of an architect's miniature. Floors rise onto it: one security in three tranches. |
| 12.54–15.44 | Investors around the world buy it… | World map: routes from Wall Street, with each buyer labelled by the tranche it holds. Labelled "illustrative". |
| 15.44–17.24 | …because it promises steady payments. | The building: payment drops climb the servicer's pipe (their gold drop first) and windows light from the top down. The legend builds one line at a time: "Payments: senior paid first ↓". |
| 17.24–19.15 | Then house prices fall, | Their town again. FOR SALE signs go up, and the price line (indicative shape) peaks in 2006 and turns red and down on "fall". The camera pushes in on their gold house. |
| 19.15–20.99 | and families stop paying. | Dissolve to the same kitchen in 2008, at night. She reads the letter; on "stop" her head drops and he turns away. |
| 20.99–24.14 | The payments dry up, the securities collapse, | Close on their house in the pool, which turns red ("their loan stops paying"). The pipe dries up and the lower windows go dark. The flood then rises from the bottom: equity on "securities", mezzanine on "collapse". Senior floors stay dry and lit. The legend builds: "Losses: equity hit first ↑", then "Senior: downgraded, value falls". |
| 24.14–30.0 | and in September 2008, Lehman Brothers goes bankrupt. | The kitchen at night with the newspaper on their table (a sheet in the 3D set, lit by the room) and a "September 2008" super; he looks down at it. Insert from above: the front page, labelled a reconstruction, with a red mark drawn under "bankruptcy". Back to the two of them and the lamp by the sink, then fade. |

### How each refinement was met
1. **Character performance:**
   - Story actions within the art's range: weight shifts and leans, head direction toward what matters (papers,
     window, letter, newspaper, each other), expression changes, and held objects (her mug, then the letter).
   - What the art cannot do (a hand signing) is a cut on action to an insert.
   - The character system was not rebuilt.
   - No talking faces, keeping to the voice-over standard.
2. **Premium 3D:**
   - The model sits on a drafting table with a cutting mat, a steel ruler and a pencil.
   - Light comes from a warm architect's lamp with soft shadows, a cool fill and a rim, with a contact-shadow pool
     under the model.
   - The plinth has a brass plaque, and the building has slab edges, mullions, a parapet, rooftop plant and an entrance
     canopy.
   - The camera is motivated: it lifts off the pool as the floors rise, holds on the pipe for the payments, starts
     close on their house for the losses, then pulls back.
3. **Progressive explanation:**
   - Pooling, issuance, payment priority and loss allocation each have their own beat.
   - Labels arrive one line at a time on their words, at most four lines, each ≥ 36 px.
   - Payments are green and run top-down from the pipe. Losses are red and rise from the foundation.
   - Senior stays lit (still paid first) and is shown "downgraded, value falls", not destroyed.
   - Buyers, tranche structure, town, family and the price shape are labelled illustrative.
4. **Human consequence:**
   - Their gold house is tracked through the street, the lender, the pool, the plinth and the losses.
   - The final kitchen was re-lit: brighter sink lamp, a warm fill on the faces, stronger cool street light, and night
     character matching. The faces, the letter and the newspaper read clearly while the room stays dark and dramatic.
5. **The two missing sequences:** the sale onward (street → map → lender → pool) and the price fall (their town, FOR
   SALE signs, the price line over the rooftops) are both implemented.
6. **Permanent creative intelligence:**
   - The director's guide and the concept notes now say that approved examples (this building included) are examples,
     not templates.
   - `used_devices.json` flags reuse.
   - The workflow applies automatically (§4).

## 2. Validation on the rendered film

- **Technical QC** (`qc.mjs`) passed:
  - no black, flash or freeze;
  - consistent opening;
  - loudness −16.2 LUFS, true peak −4.5 dBFS.
- **Narration sync** (`visual_map.py inspect`): **36 of 41 events within ±0.2 s**; 0 missing.
  - The other five are within 0.35 s: e_family −0.21, e_bundled −0.23, e_steady −0.25, e_secs −0.23, e_dry +0.34.
  - All five fall inside continuous camera moves or the 3D shots' film grain, where onset measurement is least sharp.
    Each visual still lands on its clause.
  - The first cold render had 34 of 41. Holding the camera on "sells", "dry up" and "collapse", and staging the flood
    in two steps, fixed two of the misses and moved others into tolerance.
- **The plan** (`visual_map.py check`): 0 errors; 11 clauses and 16 concepts, all depicted on their words. One
  warning: the 0.85 s reaction beat before the map, which is intentional.
- **Director's review** (QUALITY.md, on the frames): issues found and fixed during the build:
  - the window push that framed his face;
  - an SVG camera origin that missed the family's house;
  - white windows that hid paid versus unpaid;
  - a top-down issuance that read as a slab;
  - senior dimming that implied senior was paid less;
  - a cropped headline;
  - a see-through chart.
- **Tests:** 156 passed, including `test_charlab_p13.py` and `test_creative_direction.py`.

## 3. Rendering time (cold, 4 vCPU, no GPU, caches cleared)

| Stage | P13 | P12 |
|---|---|---|
| Narration | reused (P12's, read only) | 20.4 s |
| Plates + depth (4 kitchen plates; P12 had 3 bank plates) | 59.4 s | 62.1 s |
| 2.5D shots (5) | 82.9 s | 50.4 s |
| 3D (P13: 6.6 s of building in 3 shots; P12: one 7.2 s stack) | 321.9 s | 210.0 s |
| HyperFrames build + render | 175.4 s | 136.3 s |
| **Total for 30 s** | **643.1 s (10.7 min)** | **482.6 s** |
| **Minutes of computing per finished minute** | **21.4** | **16.1** (15.4 without narration) |
| Peak memory | 6.0 GB | 6.7 GB |

- The increase (about 6 min per finished minute) is mostly the animated building. Its floors rise and its shadows
  update while they do, and the flood and windows change state, so fewer frames are static holds than in P12's stack.
- **Revisions stay cheap:**
  - one 2.5D shot re-renders in 9–26 s;
  - one building shot in 80–160 s;
  - the HyperFrames render re-renders only changed scenes.

## 4. The creative workflow now applies automatically (backward compatible)

- **New episodes** get `treatment.json` from the template.
- **Builds:** `templates/episode/build.py` refuses to build an episode whose treatment does not pass, or whose hero
  storyboard is not approved (`kit.treatment.require`). `EPOCH_STORYBOARD=1` builds storyboard stills.
- **Quality gates:** `kit/gates.py` records the treatment in `gates.json`, and `quality_gates.py` runs a new
  `direction` gate.
- **Scene plans:** `python -m kit.scene_plan` checks a plan beside a treatment with the direction fields (world, acting,
  transitions) automatically.
- **Earlier episodes** have no `treatment.json`. They build and gate exactly as before, and the tests cover this.

## 5. Limitations

- **Hands:** the free art still has no hands on papers at a table. Signing is an insert with a cut on action, and the
  acting is posture, head direction, expression and held objects. Head turns are drawing rotations, not true
  three-quarter turns.
- **The 3D building** is a deliberate miniature, not photoreal. Its lighting is CPU-rendered (SwiftShader) with the
  series' painterly pass.
- **Illustrative content:** buyers, tranche sizes, the share of defaults and the price-curve shape are illustrative and
  labelled. Historical: the 2006 house-price peak and Lehman's 15 September 2008 filing.
- **Sync:** five events read 0.21–0.34 s off their words by the automatic measure (see §2).
- **Length:** at 30 s the passage is dense; the legends were cut to the minimum. An 8–10 minute episode would give
  these mechanisms more room.

## 6. Production overhead for 2–3 episodes a week

- **Treatment:** about 30–45 min per episode, plus one batched storyboard approval by you.
- **New worlds:** the kitchen, built from existing components, took about 1 min of renders. Worlds are reused and
  re-lit.
- **Rendering:** at 21 min of computing per finished minute (3D-heavy), a 9-minute episode is about 3.2 hours of
  computing on this 4-vCPU machine. Episodes with less 3D are nearer 15–16 min per minute.
- **Reusable from this pilot:**
  - `pool_journey`, `price_town`, `steps` (progressive legends), `follow` (overlays locked to a 2.5D camera), `super_`
    and `xfade`;
  - the building scene for any tranche or seniority idea, when reuse is justified.

## 7. Compatibility

- **Unchanged:** Rig v4, the P5 renderer, `render.py`, HyperFrames, production defaults and P12.
- **New files only:**
  - `charlab/p13/*`, `charlab/sequences/p13_pilot.py`;
  - `motion/sets` and `motion/demos` `p13_kitchen_*`;
  - textures and runtime files in `.runtime/` (generated, git-ignored).
- **Kit changes are additive and opt-in by presence of a treatment:** `kit/treatment.py` (`find`, `require`),
  `kit/scene_plan.py`, `kit/gates.py`, `scripts/quality_gates.py` and the episode template.
