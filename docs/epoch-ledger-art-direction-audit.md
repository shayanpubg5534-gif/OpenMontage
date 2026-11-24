# Epoch Ledger — art-direction assessment and motion-skills audit (2026-11-24)

Subject: redesign preview `previews/redesign/r1_cash_furnace.mp4` (film 3:29.6–4:14.1), source
`epoch-ledger/episodes/ai-bubble-vs-dot-com/scenes_burn.py` (commit 0b711a3). Nothing was re-rendered
for this audit.

## 1. Motion-skills audit (evidence)

### Used (file: scenes_burn.py)

| Helper | Line | Film time | Verdict |
|---|---|---|---|
| `mCamera` (new) | 293 | 3:29.6–4:14 | **Meaningful.** One world, eleven camera keys, depth-layer parallax. But every key is a wide or medium elevation (scale 0.5–1.75); no close-ups. |
| `mFlow` ×5 | 313–315, 319, 325 | 3:36.6–4:12.6 | **Meaningful** (coins to ads, staff, servers; revenue trickle; capital pipe). The dots are flat circles. |
| `mDrawOn` ×2 | 297, 337 | 3:30.8 / 3:58.1 | Fine (board line rises, then breaks). |
| `mAmbient` ×5 | 300–305 | whole segment | Background life (clouds, window flicker, spots, LEDs). Adequate, not distinctive. |
| `mBars` ×1 | 333 | 3:55.0 | Weak: one bar; the loss bar is a hand-written tween. |
| `mFocus` ×1 | 317 | 3:38.2 | **No effect:** called with an empty context list, so nothing is dimmed. A mistake. |

### Reused without meaningful improvement

- Character rig v2 (`rig_svg`, `place`, `ambient`, `rpose`, `rwalk`, `rexpress`, `rcycle`; lines 54,
  243–250, 308–347): the same paper-doll proportions, no hands, small on screen.
- The episode's `show` / `hide` fades (12 calls).
- **HUD panels** (`.bn-hud`, lines 213–215 and 273–281): hand-written HTML dashboard cards. These are
  the "floating software panels" you flagged. No kit component was used for them.
- Geometry: 132 SVG primitives, of which 65 are `<rect>`. No SVG filters (no shadows, blur or
  grain); 5 gradients. That explains the rectangular, simulation-game look.

### Available and relevant but not applied

| Capability | Why it would have helped | Why it wasn't used |
|---|---|---|
| `mWordsAt` / `mReveal` / `ktext` (kinetic type) | One integrated key phrase ("existential threat", "burning cash") could replace a panel | Not considered during design |
| `mDiagram` + `mFocus` / `mUnfocus` (focus and context) | Dim the rest of the building while the named outlet works | Misused (empty context) |
| `mCount` | A diegetic counter (gauge dial, ledger) | Avoided because no real figures exist. Correct to avoid invented numbers, but a qualitative dial could have been used |
| `mPush` / close-up keys in `mCamera` | Shot variety (faces, hands, the valve, the tank gauge) | Not planned; no shot list |
| Craft guide §5 "financial graphics in the world" | Diegetic graphics instead of panels | Guide not consulted (below) |
| `ELK3D` / `three_kit.js`, iso, maps | Not needed for this beat | Correctly unused |

### Was the guide or index consulted before designing?

**No.** In the design turn I did not invoke the `epoch-ledger-motion-craft` skill and did not re-read
`skills/creative/epoch-ledger-motion-craft.md` or `epoch-ledger/COMPONENTS.md`. I designed from
memory of having written them. The only part of the upgraded system that actively changed the
result was **QA**: `layout_check.mjs` found labels drifting under the captions and the tag
colliding with the billboard, and both were fixed. **Conclusion: the integrated skills are mostly
documented and available, not yet steering creative decisions.**

## 2. Art-direction assessment — why the execution falls short

1. **Authoring method:** every shape is typed as coordinates in Python strings. SVG itself can
   carry professional illustration (organic paths, gradients, masks, filters, textures). The
   bottleneck is composing organic forms by hand in code, which pushes everything toward
   rectangles and repeated patterns (windows, desks, racks).
2. **Characters:** rig v2 is a paper doll built from rounded primitives. It has stylised
   proportions (about four heads tall), no hands or fingers, one flat shade tone, and only profile
   and three-quarter views. Characters are small in frame, and there are no close-ups to carry
   emotion.
3. **No perspective:** all sets are front elevations ("dollhouse cutaway") with no vanishing
   points. That is the single biggest cause of the simulation-game look.
4. **Lighting:** flat fills, no cast shadows or ambient occlusion, no rim light, no light falloff
   or atmospheric haze. The night pass is a colour overlay, not light.
5. **Shot grammar:** eleven shots, all wide or medium; no establishing-to-detail progression, no
   foreground framing, no depth of field.
6. **Financial graphics:** dashboard cards are pinned to the frame instead of living on objects in
   the world.

## 3. Can our current stack do substantially better? Yes — mostly without new assets

| Capability (no new dependencies) | Approach |
|---|---|
| **Perspective construction kit** (`kit/persp.py`) | One- and two-point perspective projection for rooms and streets: receding floors and ceilings, windows and furniture placed in perspective, architectural detail generators (cornices, pilasters, awnings, mullions, signage) with seeded variation so nothing repeats. |
| **SVG lighting and atmosphere kit** (`kit/light.py`) | Soft cast shadows, contact and ambient-occlusion gradients, rim-light strokes, volumetric light beams (blend modes), per-layer atmospheric perspective (haze, desaturation, slight blur for depth of field), film grain, bloom and vignette. |
| **Character rig v3** | Natural proportions (about 7–7.5 heads); anatomical paths instead of boxes; hands with thumb and finger groups; clothing folds; cel shading plus highlight and rim; front, three-quarter, profile and back views; a detailed close-up head (brows, eyelids, mouth shapes). Costume sets for 1999 Wall Street, dot-com casual and 2026. This is the largest work item, and it is reusable for the whole series. |
| **Diegetic financial graphics** (`mCallout` and friends) | Gauges on the tank, a runway chalk line on the office whiteboard, a term sheet on the boardroom table, the market board, a newspaper headline, and annotations with leader lines anchored to objects. No floating cards. |
| **Shot grammar** | A planned shot list per beat: establishing, medium, close-up (faces, hands on the valve, coins in the tank), with foreground framing elements and depth-of-field layers. |
| **Illustrated 3D for selected establishing shots** | Three.js sets with toon/painted shading and outlines (`three_kit.js`), with 2D character cards placed in them. Use only where true perspective and light matter. |

Expected result: a clear step up in perspective, light, depth and character quality. Honest
limits: hand-coded illustration will still not match a human illustrator's brushwork, and filters
plus larger character counts will raise render cost (estimate +20–60 %, to be measured on one shot).

## 4. Legally reusable assets — optional, needs approval

All of these are free; none is reachable from this environment yet (network allowlist).

- **Poly Haven / ambientCG** (CC0): textures and HDRIs for 3D sets.
- **Kenney / Quaternius** (CC0): stylised 3D props and buildings.
- **Wikimedia Commons public-domain imagery** (e.g. 19th-century railway engravings, archival
  photos marked PD): historical plates animated in 2.5D. Each file's licence must be checked.
- **Open Peeps** (CC0, hand-drawn line characters): a different style; useful only as pose
  reference, not as the series look.
- *Not recommended:*
  - flat-illustration packs (generic SaaS look);
  - local Stable Diffusion: needs torch and diffusers installs, is slow on 4 CPUs (minutes per
    image), gives inconsistent style, and carries per-model licence terms;
  - any paid generation.

## 5. Deliberate skill selection during storyboarding (proposed process)

1. **Before designing any scene:** invoke the `epoch-ledger-motion-craft` skill and read
   `COMPONENTS.md`. Record in the storyboard that this was done.
2. Fill a **scene plan** per narration beat (`storyboard/scene_plan.json`):
   - beat and words;
   - what the audience must understand;
   - shot size (establishing, medium, close-up, insert);
   - technique: illustrated 2D, 2.5D layered, illustrated 3D, diagram, data visualisation,
     kinetic type, map;
   - chosen helpers and assets;
   - lighting and mood;
   - **why this technique and why not the obvious alternative**.
3. A test validates the plan: every scene has a shot size, technique and rationale; no more than
   two consecutive shots of the same size; no dashboard panel unless justified. A review step
   compares the plan with the implementation.
4. **Style frames before animation:** three still frames (establishing, medium, close-up) for
   approval. They are snapshots, so they cost no video render.
5. Use only the techniques the beat needs: no tool-demonstration effects.
