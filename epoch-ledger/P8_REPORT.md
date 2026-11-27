# P8 — Free asset integration: 2.5D vs 3D visual evaluation (visual approval gate)

**Status:** experimental and isolated (`epoch-ledger/charlab/p8/`). **Stills only; no animation rendered.**
- Rig v4, the P5 renderer, P6 Variant B, production defaults and the narration and dialogue standard are unchanged.
- Nothing purchased, no paid APIs, no artists contacted.
- Raw Fab files are not committed; provenance is in `charlab/p8/ASSETS.md`.

Date: 2026-11-27.

**Deliverables** (in `projects/charlab_p8/`; compressed copies in `charlab/evidence/p8_*.jpg`):

| File | Content |
|---|---|
| `sheet_25d_peeps.png` | 2.5D character inspection: cast, expressions, poses, layer separation |
| `sheet_3d_businessman.png` | 3D character inspection: native views, rig poses, hand, face controls |
| `bank_25d.png` | 2.5D cinematic bank still |
| `bank_3d.png` | 3D cinematic bank still |
| `sheet_comparison.png` | Side by side, same set and camera |

## 1. What the five files actually contain

### Open Peeps (CC0, Pablo Stanley)
- **Flat Assets ZIP:** intact. 358 SVG and 185 PNG (Sketch export), **monochrome** (ink #000, white fills, one blue
  accent).
  - *Separate Atoms*: bodies 30, faces 30, heads 46, facial hair 17, accessories 9, standing poses 23, sitting poses 11.
  - *Templates*: busts 105, standing 30, sitting 16.
  - SVG structure: nested `<g>` per component (pose, head, face), clean filled paths (outlines are filled shapes, not
    strokes), white regions as separate paths (recolourable).
- **Figma file:** a binary `fig-kiwi` container: Kiwi schema, document and thumbnail, raw-deflate compressed.
  - No Figma is needed: `p8/figdecode.py` (pure Python) decodes it, and `p8/peeps_extract.py` renders nodes to SVG,
    resolving component instances, instance swaps and overrides.
  - Contents: 3,712 nodes and 9,633 path blobs. The **multicolour** set: 186 components (heads 50, faces 30,
    bodies 30, standing poses 26, sitting poses 11, facial hair 17, accessories 9, masks 3) and 131 frames (variation
    sheets, compositions, comic and storyboard examples).
  - A character is the `a person/standing|sitting|bust` component with slots **BODY (pose), HEAD (hair), FACE,
    FACIAL HAIR, ACCESSORIES**. Rendering the variation frames reproduces the artist's colour sheets exactly (checked
    visually).
- **Animation potential (from the structure):**
  - Head, face and accessories are separate groups: head tilt and nod, **blink = swap to "Eyes Closed"**, 30
    expressions, glasses.
  - **Arms and legs are drawn into each pose** (no separate limbs): gestures are **pose swaps** (blazer ×4, pointing
    ×2, crossed arms ×2, walking ×3, resting, easing; 11 sitting poses).
  - Smooth limb motion would need cut-out limbs (new art or a re-split of poses).
  - Breathing, sway, head motion, blinks and pose changes on beats are all possible by code.

### Businessman (Fab, Daydreams Creative Studios, Standard License)
- **All three files are intact** (Blender 4.0 `.blend`, glTF 2.0 `.glb` with generator `fab-model-conversion`,
  FBX 7400).
- **It is an MPFB/MakeHuman character:**
  - body `Human` with a middle-aged dark-skinned male skin (2048 px);
  - MakeHuman wardrobe `toigo_male_suit_3` (diffuse, normal and spec, 2048 px), `afro01` hair cards, `shoes04`,
    eyebrows, lashes, teeth and tongue;
  - "Tiny Eye" eyeballs with procedural iris shaders.
  - This is the same asset family and look we rejected in M5.
- **Rig:** Rigify (1,090 bones, **209 deforming, 101 of them in the face**), FK/IK switches, a full face rig.
  - **No shape keys** on the body (only iris/pupil shape keys on the eyeballs) and **no animation tracks**: this
    confirms the listing.
  - The body uses mask modifiers to hide skin under clothes.
- **Quirks found:**
  - The GLB contains a stray 2 m "Icosphere" helper and bone-parented eyeballs.
  - The eye colours live in node groups, so glTF exports white eyes.
  - The FBX bakes subdivision (suit about 65k triangles) and adds leaf bones (1,667).
- **Measured** (P6 definitions): **7.16–7.21 heads**, shoulders **1.54 head heights**. Passes the standard's numbers.

## 2. 2.5D test (artist's own artwork, no redrawing)
- `p8/peeps_compose.py` builds characters by swapping the artist's parts and **remapping flat colours** to a muted
  documentary palette:
  - ink #1e1b19;
  - warm paper;
  - natural skin tones;
  - navy, olive, oxblood, slate and charcoal clothing;
  - grey hair for seniors.
- The cast is six adults: older banker, bearded client, moustached lender, clerk, senior investor, founder in a
  hijab. The result is one consistent style, with no candy colours.
- `p8/compose_25d.py` composites them onto the **P4 cinematic bank plate** (the set without characters, rendered with
  the same camera as the 3D still):
  - characters placed by projecting their floor positions and heights through that camera;
  - floor contact and cast shadows;
  - window-side rim light and diagonal shading;
  - warm top light, film grain and vignette;
  - an out-of-focus foreground plant.
- Rendered headless (HTML/SVG in Chromium, as HyperFrames scenes are).

## 3. 3D test (the supplied character, its own rig)
- `p8/bm_pose.py` uses only the asset's Rigify controls:
  - **standing, pointing, walking (contact) and sitting** (body);
  - **blink, smile and jaw open** (face bones; there are no blendshapes).
- **Result:** the rig deforms cleanly at shoulders, elbows and wrists (hand close-up on the sheet), and blink and jaw
  work. The smile is weak without tuning. Sitting needs a chair.
- **Runtime GLB:**
  - The pose is baked (skins off, modifiers applied).
  - Materials are made opaque and matte for wool, the eye colours are restored, the cornea cap is removed and the
    facing is baked.
  - Static, about 19 MB.
- **Runtime limitations seen:**
  - The suit's satin sheen needed its normal and spec maps removed.
  - The prop rotation field had no effect, so facing was baked instead.
  - MakeHuman hair cards read as a helmet.

## 4. Fair comparison (same set, same camera, same P4 look)

| | **2.5D (Open Peeps)** | **3D (Fab businessman)** |
|---|---|---|
| Visual quality | Consistent hand-drawn editorial look; restyled palette reads adult and documentary; integrates with the set through shadows, rim light and grain. The contrast between flat ink figures and a rendered set is visible, but reads as a deliberate hybrid style | Realistic MakeHuman face and skin, hair-card helmet, game-NPC feel; sits in the set technically but **clashes with our illustrated graphics and captions**. The quality is the M5 level we rejected |
| Character variety | **Six adults built here; hundreds of combinations** (50 heads × 30 faces × 26+11 poses × hair, glasses, skin and palette) | **One** man (identity changes would need MPFB rebuilds; we know that route) |
| Animation potential | Blink, expressions, head motion and pose swaps; **no limb bending** without new art | Full skeleton, retargetable mocap (M3–P5 pipeline), bone-driven face; lip sync possible through bones (scripted dialogue only) |
| Wardrobe and historical | Contemporary casual only; no suits, ties or period dress; trousers are solid ink | One modern suit; MakeHuman has a few other garments |
| Automation | Fully scriptable (Figma decode → SVG → HTML); no desktop software | Fully scriptable (Blender Python → GLB → three.js) |
| Rendering cost | Set plate once per shot + 2D layers per frame (**not yet measured** for animation) | Full 3D frame every frame (P5 measured 1.19 s per frame for a character shot) |
| Licence | CC0 (no restrictions) | Fab Standard: rendered video OK; raw asset not redistributable |

## 5. Assessment
- **2.5D with Open Peeps is the stronger direction here.**
  - It is a real artist-made system with a consistent style.
  - It is restyled into a mature palette by code, and integrated in the actual bank set.
  - It has enough parts for a 6–10-person cast today, at no cost.
- **Weaknesses:**
  - The style is still casual and contemporary (sneakers, no suits or period dress).
  - Gestures are pose swaps, not bending limbs.
  - The ink-outline figures in a rendered 3D set are a stylistic choice that you need to like.
- **The 3D businessman is technically sound** (rig, face bones, poses), but its **look fails our standard**. It is
  MakeHuman, the M5-rejected family, so it does not change the 3D conclusion from P6/P7.

**Recommendation (your decision):**
1. Approve the 2.5D direction for an **animation test** (head and blink, breathing, pose-swap gestures, camera
   parallax on the plate), still in the same bank shot.
2. In parallel, decide whether to extend the wardrobe (suits, period dress) with new parts in the Open Peeps style
   (an illustrator or our own vector work). That is the main gap for financial and historical documentaries.
3. Keep the 3D pipeline for environments and props; do not pursue this businessman as a cast member.

Stopping at the visual approval gate.

## Reproducibility
```
python3 epoch-ledger/charlab/p8/figdecode.py open-peeps.fig --list
python3 epoch-ledger/charlab/p8/peeps_extract.py open-peeps.fig OUT --frame variations-standing --each
python3 epoch-ledger/charlab/p8/peeps_compose.py open-peeps.fig .runtime/charlab/p8/cast
.runtime/charlab/venv/bin/python epoch-ledger/charlab/p8/bm_pose.py businessman.blend OUT.blend {stand|point|walk|sit} [--face blink|smile|open] [--glb OUT.glb --yaw 60]
node epoch-ledger/charlab/p6/still.mjs epoch-ledger/charlab/motion/demos/p8_bank_{plate,3d}.json projects/charlab_p8/bank_{plate,3d}.png cin_cinematic
python3 epoch-ledger/charlab/p8/compose_25d.py projects/charlab_p8/bank_plate.png .runtime/charlab/p8/cast projects/charlab_p8/bank_25d.png
python3 epoch-ledger/charlab/p8/make_sheets.py .runtime/charlab/p8 projects/charlab_p8
```
