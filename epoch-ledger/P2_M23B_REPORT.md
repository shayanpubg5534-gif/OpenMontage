# P2 report: M2.3b premium editorial character art direction

Status: one art-direction iteration completed (stills only). Awaiting your decision. No motion work, no production
migration, no full video.
Date: 2026-11-25.

## Scope and isolation
- **Unchanged:** production code, production rigs, approved assets, the 18-minute documentary and its caches.
- **New lab files** (all in `epoch-ledger/charlab/`):
  - `viewer/lookdev2.html` (the M2.3 viewer is kept);
  - `prepare_textures.py`, `evidence_sheets2.py`;
  - specs `elias.json` and `nadia.json`.
- **Extended lab files:**
  - `build_dressed.py`: optional face-normal smoothing, texture export and an LOD export, all opt-in per spec, so the
    M2.3 specs behave as before;
  - `lookdev.mjs`: `--page` and `--query` options.
- **Tools:** free and local only (Blender `bpy` 5.3.0, MPFB 2.0.18, three.js r186.1, Pillow). No asset packs were
  downloaded; both characters use only the installed MakeHuman system assets (CC0).
- **Kept from M2.3:** the 53-bone `game_engine` skeleton, 30 finger bones, expression shape keys and the asset-loading
  safeguard.

## 1. Two characters from one system
| | Elias | Nadia |
|---|---|---|
| Role (fictional, not cast) | Banker, late forties | Business owner, about forty |
| Phenotype | Male, mixed ancestry, average build | Female, East-Asian-weighted, slimmer, shorter |
| Hair | `short02` | `ponytail01` (replaced `bob01`, whose fringe hid one eye) |
| Clothing | `male_elegantsuit01` (jacket, shirt, tie, trousers) + `shoes04` | `female_elegantsuit01` (blouse, skirt) + `shoes03`, with the sports socks recoloured to dark tights at build time |
| Build time [M] | about 14 s, then 9–12 s texture preparation | same |

The pack's wardrobe is the limit **[V]**: it has one professional women's outfit, and every shoe comes with sports socks.

## 2. What changed in the art direction
| Problem in M2.3 | M2.3b change |
|---|---|
| Patchy, mask-like face shadows | **Face-normal smoothing** at build time: the head's shading normals are blended toward a heavily smoothed copy (strength 0.95, weighted by the head bone), so bands follow the broad form of the head. Skin gets a lower shadow threshold and a lighter, warm shadow tint |
| Photographic skin under cel shading | Editorial skin is **one even tone** that keeps only broad variation (lips, cheek warmth). An earlier attempt with a 5-colour skin palette produced "make-up islands" and was dropped |
| Flat, crushed clothing | **Controlled flat colour:** each garment is median-filtered and quantised to a small palette at build time, so jacket, shirt, tie, seams, lapels and buttons stay distinct |
| Helmet hair | Hair reduced to 3 tones with its strand-clump alpha kept, plus a **shaped highlight band** broken by the clumps, and a thinner hair outline |
| Small, blank eyes; smudged lashes | A **controlled catchlight** placed in view space, readable from any camera angle; lighter, thinner lashes and brows |
| Default face reads as a frown | A pleasant, attentive neutral for stills (slight smile, brows relaxed, eyes open) |
| Characters not matching the set | **Per-set light rigs** (bakery: warm key from the right; bank: daylight key from the window side, warm lamp fill), set-coloured contact shadows, set-matched ink colour, a shared colour grade and shared paper grain |
| Uniform outlines | **Variable weight:** a heavy silhouette, thinner hair outline, and light interior lines that fade on soft creases |

## 3. The three treatments (identical characters, poses, lights, cameras and sets)
| | Improved toon | Flat editorial | Hybrid painterly |
|---|---|---|---|
| Shading | Three crisp bands | Two crisp bands | Two soft bands, light brush filter (Kuwahara R=2, 60% mix), warm and cool split toning, pigment grain |
| Textures | Simplified photo textures | Palette-flat textures | Palette-flat textures |
| Read | Closest to M2.3; faces still slightly "3D" | Cleanest; closest to the flat vector sets; decisive single face shadow | Softer, more "painted"; slightly blurs the ink the sets use |
| Medium shot, 1080p [M] | 1.1–1.2 s | **1.0–1.1 s** | 1.7 s |
| Close-up, 3/4, profile [M] | about 2.5 s | about 2.4–2.6 s | about 3.0–3.2 s |

**My ranking for the series: flat editorial first, hybrid second, improved toon third.**

## 4. Inspection [M]
| Check | Elias | Nadia |
|---|---|---|
| Clothing poke-through, standing | 0 vertices | First pose: fingertips 26 vertices inside the skirt (the hands hung too close), so the arms were angled further out. After the fix: 6 blouse vertices at the upper back and neck, ≤6.6 mm, not visible in any still |
| Clothing, walking (6 poses) | 26–40 at the sleeve cuff (wrist), as in M2.3 | 10–14 at cuffs and upper back, ≤20 mm |
| Hair-to-scalp gap (10th percentile) | 0.6 mm | 3.1 mm |
| Eye symmetry / interocular distance | 0.27 mm / 60.3 mm | 0.24 mm / 55.1 mm |
| Expressions (neutral, concern, smile, surprise) | All read | All read. Surprise looks tense (mouth-open target too strong for her face) |

## 5. Efficiency investigation [M]
Times per still at 1080p, including the PNG readback a capture needs, on this 4-CPU machine without a GPU. These are
not frame times inside a full video render.

| Variant (flat editorial, medium shot) | Bakery | Bank | vs. default |
|---|---|---|---|
| Default (MSAA ×4, 2048 shadow map, interior ink) | 1.01–1.11 s | 1.08 s | – |
| No MSAA | 0.67 s | 0.69 s | −37% |
| Shadow map 1024 | 1.08 s | 1.06 s | ≈0 |
| No interior-ink pass | 0.97 s | 1.05 s | −5% |
| **Lean (no MSAA + 1024 shadow + no interior ink)** | **0.32 s** | **0.36 s** | **−68%** |

| Variant (flat editorial, wide two-shot) | Time |
|---|---|
| Full models, repeat | 1.06–1.24 s |
| **LOD models** (decimated to 35%: 47k → 16k triangles per character), repeat | 1.08 s: **no gain** |
| LOD + lean | 0.48 s |

**Findings:**
- **Pixel and post-processing work dominate**, not geometry. LOD gives no measurable benefit here and isn't worth
  maintaining.
- **MSAA is the biggest single cost.** The lean setting needs a quality check: edges without MSAA show some aliasing at
  1080p.
- **Close-ups cost about 2.5 s,** mostly the 49-tap background-blur pass. A pre-blurred plate per shot would remove
  most of that **[E]**.
- **Reusable assets:**
  - textures are prepared once at build time, not in the browser, at about 10 s per character;
  - a character GLB is about 16 MB, mostly 2048-pixel textures; halving them to 1024 is the obvious next saving
    **[U]**;
  - the first still in a session pays about 2–3 s for shader compilation.

**No full-episode performance claim is made.**

## 6. Verdict against the brief
| Requirement | Status |
|---|---|
| Controlled flat colour, 2–3 bands | **Met** (editorial and toon) |
| Clean, variable-weight outlines | **Met** |
| Natural skin without patchy, mask-like shadows | **Largely met:** one decisive face shadow instead of patches. Some cheek and jaw shadow shapes are still arbitrary in three-quarter views |
| Expressive eyes with controlled highlights | **Met** for highlights; the eyes remain small in wide and medium shots |
| Stylised hair with shapes and highlights | **Partly:** strand clumps and highlights read, but the stock hair meshes are still simple shells |
| Readable folds, lapels, collars, seams | **Met** for lapels, collars, seams and buttons; fold detail is modest |
| Natural adult proportions, no cartoon exaggeration | **Met** |
| Cinematic lighting, cohesive set shadows | **Met** for light colour and shadows. In the bank the characters stand in front of the painted desk: occluding them behind painted furniture needs 3D proxies of the set (environment work) |
| Not plastic, not video-game, not childish, not uncanny | **Mostly:** clearly not plastic or uncanny. Faces still read as generic stock 3D faces in close-ups, the main remaining gap |
| Male and female, different builds, hair, clothing | **Met** |

## 7. Recommendation
1. **Adopt the flat editorial treatment** as the character-rendering standard (shading, palette textures, ink, set
   light rigs, catchlights). It's the cleanest, fits the vector sets best, and is the fastest (about 1.0 s per medium
   shot, 0.3 s lean).
2. **Be clear about the ceiling of stock assets.** The remaining distance to "premium hand-drawn" lies in the **face and
   hair designs themselves**: MakeHuman's stock heads and hair shells are generic. Shading can't fully hide that in
   close-ups. Closing it needs **bespoke character art**: stylised head sculpts and hand-shaped hair meshes per cast
   member, modelled in Blender (free) by someone with character-art skill, reusing this exact rig, pipeline and
   treatment. I can automate everything around that work, but not replace an artist's design judgement **[E]**.
3. **Decision needed:**
   - **(a)** accept this level for medium and wide shots and keep close-ups sparse;
   - **(b)** plan a bespoke head and hair art pass for the recurring cast before motion work;
   - **(c)** stop at this point and keep Rig v4 for production characters.

   I recommend **(b)** if premium close-ups are essential, otherwise **(a)**. In either case, motion work (M3) can then
   start with the editorial treatment.

## Evidence
Full-size files in `projects/charlab_m23b/` (not in git):
- **Sheets:**
  - `bakery_wide.png`, `bank_wide.png`;
  - `bakery_elias_treatments.png`, `bakery_nadia_treatments.png`, `bank_elias_treatments.png`, `bank_nadia_treatments.png`;
  - `expressions.png`, `progression.png` (Rig v4 → M2.3 → M2.3b).
- **Every individual 1920×1080 still:** `stills/bakery/`, `stills/bank/`, `stills/expr/`, `stills/lod/`, with
  `timings.json` in each folder.

Compressed copies of the sheets are in `epoch-ledger/charlab/evidence/m23b_*.jpg`.

## Reproducibility
See `epoch-ledger/charlab/README.md`, "M2.3b". For each spec in `specs/{elias,nadia}.json`:
1. `build_dressed.py`
2. `prepare_textures.py <id>_tex --spec`
3. `lookdev.mjs --page lookdev2.html --query 'env=bank|bakery&chars=…&out=…'`
4. `evidence_sheets2.py`

Dependencies are unchanged from M2.3, plus Pillow (already present).
