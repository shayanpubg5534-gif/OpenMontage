# P2 report: M2.3c bespoke character art direction (geometry, not shaders)

Status: one bounded iteration, stills only. Awaiting your visual decision. No motion work, no production migration, no
change to the production default, no full video.
Date: 2026-11-26.

## Scope and isolation
- **Foundation:** the M2.3b flat editorial treatment, unchanged.
- **New lab files** (`epoch-ledger/charlab/`):
  - `stylise.py`: the procedural geometry stage;
  - `verify_design.py`: rig and expression checks for the designed meshes;
  - `viewer/lookdev3.html`: a copy of `lookdev2.html` that knows the new mesh types;
  - `evidence_sheets3.py`;
  - specs `elias_c.json` and `nadia_c.json`.
- **Extended files, all opt-in:**
  - `build_dressed.py` runs `stylise.py` only when a spec has a `"design"` section. The M2.3b spec `elias.json`
    rebuilt today gives identical triangles, expression keys, masks, eye check and face normals.
  - `prepare_textures.py` makes an illustrated eye texture only when the spec asks for it.
  - `inspect_character.py` recognises the designed brows and lash lines.
- **Unchanged:**
  - the 53-bone `game_engine` skeleton, 30 finger bones and the 12 expression units;
  - the asset-loading safeguard and the render switches;
  - production code, Rig v1–v4 and the documentary.
- **Tools:** free and local only (`bpy` 5.3.0, MPFB 2.0.18, three.js r186.1, Pillow, NumPy). No new assets were
  downloaded; there was no manual modelling.

## What changed in the geometry (all generated from the spec, headless)
| Area | M2.3b | M2.3c |
|---|---|---|
| **Face structure** | MakeHuman macro face plus +0.3 eye scale | About 25–30 designed MakeHuman face targets per character (jaw, chin, cheekbone planes, nose bridge, tip and nostrils, cupid's bow and lip volume, eye opening and bags, temples, neck). Plus **face planes**: a volume-preserving (Taubin) smoothing of the face skin, applied as a shape key, that protects the eyelids, lips and ears. Every proxy (eyes, teeth, clothes) is refitted to the new face before baking |
| **Identity** | Two stock faces | **Elias:** a square, long jaw, strong chin, flat cheek planes, straight heavy brows, grey temples. **Nadia:** an oval face with a narrower, slightly pointed chin, high cheekbones, a small straight nose, a defined cupid's bow, upturned outer eye corners and arched fine brows |
| **Hair** | Stock alpha-card shells (`short02`, `ponytail01`) | **Original hair geometry**, generated from the scalp:<br>• a designed hairline (control points around the head);<br>• a volume map plus "bumps" for lift;<br>• clumps sculpted as grooves along a designed flow (a side part for Elias; converging at the tie for Nadia), with lock tips where wanted;<br>• a solid edge: real thickness up to a smooth, iso-cut hairline, with a short wall to the scalp;<br>• shading normals eased onto the scalp along the hairline;<br>• a second colour zone (Elias's grey temples).<br>Nadia gets a **ponytail** of 13 tapered locks that hang clear of the body and clothes, plus a tie |
| **Brows** | Stock alpha cards (thin, wispy) | **Designed brows:** a raised, tapered band along a designed curve on the brow ridge (thickness, arch and tail per character) |
| **Eyes** | Stock lash cards, photographic iris | A **lash line**, the upper lid line an illustrator draws, built on MakeHuman's eyelash helper geometry. It thickens toward the outer corner, has a short flick, and comes with a light partial lower line. **Illustrated eye texture:** iris found automatically and enlarged by 15–18%, two tones with a limbal ring, a flat sclera |
| **Lips, nose** | Stock | Shaped by the face targets (cupid's bow, volume, nostril width, tip) |

Every designed mesh is skinned to the head bone and gets the expression shape keys of its nearest body vertices, so
**the existing expressions drive it**.

## Verification [M]
| Check | Elias | Nadia |
|---|---|---|
| Bones / clips | 53 / stand, relaxed, grip, walk | same |
| Designed meshes follow the head bone (20° turn) | hair 58 mm, brows 28 mm, lash lines 20–22 mm | hair 53 mm, ponytail 86 mm, brows 25 mm |
| Blink (`eye-*-closure`): upper-to-lower lash-line gap | 12.9 → 8.7 → 4.5 mm (open, half, closed) | 12.4 → 8.1 → 3.9 mm |
| Brow raise (`eyebrows-*-inner-up`): designed brow inner end | +3.1 mm | +3.1 mm |
| Scalp through hair, standing and 5 walk poses | **0 vertices** (stock `short02` in M2.3b: 54 vertices, up to 20 mm) | **0** |
| Hair-to-scalp gap (10th percentile) | 2.9 mm | 5.3 mm (pulled-back volume) |
| Clothing poke-through | unchanged from M2.3b (same body and clothes) | unchanged (6 small blouse contacts) |
| Eye symmetry / interocular | 0.26 mm / 60.3 mm | 0.24 mm / 53.9 mm |
| Build time (whole character) | 8.9 s (design stage 1.5 s) | 15.6 s (design 8.3 s, mostly the ponytail clearance) |
| GLB size | 12.4 MB (M2.3b 15.9 MB) | 12.6 MB (M2.3b 16.6 MB) |

`check_glb.mjs` (M2.1) reports "morph changes pixels: false" for **both M2.3b and M2.3c**. For dressed characters it reads
morphs from the first skinned mesh (the tongue), so it is a checker limitation, not a regression. `verify_design.py` and
the blink and expression stills are the real check.

## Rendering cost (same session, 1080p still, including readback; median of 6; no full-episode claim)
| Shot (bank, flat editorial) | M2.3b | M2.3c |
|---|---|---|
| Medium, default | 1.13 s | 1.13 s |
| Medium, lean (no MSAA, 1024 shadow, no interior ink) | 0.35 s | 0.34 s |
| Wide two-shot | 1.21 s | 1.23 s |
| Close-up (background blur) | 2.54 s | 2.54 s |

The new geometry costs nothing measurable: pixel work still dominates. Triangles per character are about the same
(designed hair 8–12k triangles, against stock hair 3–5k triangles, while the stock brows and lashes go away).

## Honest visual assessment
**Clear improvements:**
- **Eyes:** a readable iris, a deliberate lid line and a flick; the eyes now read in medium shots.
- **Brows:** graphic, designed and character-specific.
- **Elias's face:** clear structure (jaw, chin, planes), a tidy side-parted cut with grey temples, a clean nape, and
  no scalp poking through.
- **Distinct identities:** the two characters no longer share one stock "MakeHuman" look.
- **Expressions:** all of them, plus blink, now carry the designed features.

**Not yet at premium level:**
- **Nadia's hair** reads as sleek but cap-like from the front and in profile. The ponytail is clean but thin and smooth
  next to the stock strand texture. Procedural sweeps make tidy, groomed shapes; they don't make the characterful
  silhouette shapes an artist would draw (fringe pieces, asymmetric lift, flyaways).
- **Faces under hard key light:** a single large shadow shape still crosses the face in three-quarter views. That's a
  lighting and design choice, which I didn't change in this geometry iteration.
- **Mouths:** they remain the weakest feature. Teeth and the open-mouth shapes (surprise) are stock and look tense.
- **Overall read:** stylised-3D documentary, not hand-drawn. I judge M2.3c a meaningful step on eyes, brows, face
  structure and identity, and a partial step on hair.

## Recommendation
1. **Keep the geometry pipeline** (`stylise.py`): designed face targets, face planes, designed brows, lash lines,
   illustrated eyes, and the hair generator for short and groomed styles. It is cheap (seconds), deterministic, rig-safe
   and free.
2. **Hair for longer and loose styles:** the remaining gap is a design gap that procedural rules close slowly. If those
   styles matter for the recurring cast, the efficient route is a few hand-shaped hair meshes per cast member, modelled
   once in free Blender. The rest of this pipeline (skinning, expressions, ponytail clearance, editorial shading) applies
   to them unchanged.
3. **Decision needed:**
   - **(a)** accept M2.3c as the character-look baseline (close-ups allowed for Elias-type cuts; groomed or pulled-back
     hair for women) and move to motion (M3);
   - **(b)** one more bounded pass, limited to hair silhouettes and mouth shapes, before M3;
   - **(c)** keep Rig v4 for production characters.

   I recommend **(a)**, with longer hairstyles deferred to hand-shaped meshes when a specific cast member needs one.

## Evidence
Full-size files in `projects/charlab_m23c/` (not in git):
- **Sheets:**
  - `bank_elias_m23b_vs_m23c.png`, `bank_nadia_m23b_vs_m23c.png` (medium, close-up, three-quarter, profile, back);
  - `bakery_elias_…`, `bakery_nadia_…`;
  - `bank_wide_…`, `bakery_wide_…`;
  - `expressions_m23b_vs_m23c.png` (with blink);
  - `m23c_faces.png`.
- **Stills:** `stills/{bank,bakery,expr,blink,m23b_back}/`, each with `timings.json`.

Compressed copies are in `epoch-ledger/charlab/evidence/m23c_*.jpg`.

## Reproducibility
```
for c in elias_c nadia_c; do
  BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
      epoch-ledger/charlab/specs/$c.json .runtime/charlab/out_m23c --bvh walk=.runtime/charlab/mocap/02_01.bvh
  python3 epoch-ledger/charlab/prepare_textures.py .runtime/charlab/out_m23c/${c}_tex --spec epoch-ledger/charlab/specs/$c.json
  .runtime/charlab/venv/bin/python epoch-ledger/charlab/verify_design.py .runtime/charlab/out_m23c/$c.glb OUT.json
done
node epoch-ledger/charlab/lookdev.mjs --page lookdev3.html --three .runtime/charlab/three/r0.186.1 \
    --query 'env=bank&chars=elias_c:-.65:0:15,nadia_c:.7:.1:-20&out=/.runtime/charlab/out_m23c' --shots SHOTS.json --out DIR
python3 epoch-ledger/charlab/evidence_sheets3.py projects/charlab_m23b/stills projects/charlab_m23c/stills projects/charlab_m23c
```
