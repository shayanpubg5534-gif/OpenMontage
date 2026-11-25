# P2 report: M2.3 character look development

Status: M2.3 complete as a look study; **not yet approved as the production look**. Motion development has not
started.
Date: 2026-11-25.

Scope:
- One fully dressed character was built from the MakeHuman system assets (all CC0) in the isolated lab. Only stills were
  rendered, plus 4-second test clips for the loading safeguard.
- Production rigs, approved assets and caches are untouched. The 18-minute documentary was not rendered.
- Tools: free and local only. Two small extractors were installed (`unar`, `7zip`); `esbuild` ran once via npx.

Evidence labels: **[M]** measured, **[V]** verified in source or licence text, **[E]** estimate, **[U]** untested.

Evidence images are in `epoch-ledger/charlab/evidence/`:
- `m23_1_treatments.jpg`: toon against painterly, in wide, medium, close-up and profile;
- `m23_2_turnaround_toon.jpg`, `m23_2_turnaround_paint.jpg`;
- `m23_3_expressions.jpg`;
- `m23_4_hands.jpg`;
- `m23_5_hair.jpg`;
- `m23_6_rig4_comparison.jpg`.

Full-size stills are in `projects/charlab_m23/`.

## 1. The character

"Elias", a fictional banker in his late forties. He is a look-development subject only, not a production cast member.
- **Body:** MPFB phenotype from the spec `charlab/specs/elias.json`, with the eyes enlarged slightly (+0.3 scale target) for
  readability.
- **Assets:** high-poly eyes with a brown iris, `eyebrow010`, `eyelashes01`, `short02` hair, teeth, tongue, the
  `male_elegantsuit01` suit (jacket, shirt, tie, trousers), `shoes04` dress shoes and the `middleage_caucasian_male`
  skin texture.
- **Rig:** `game_engine`, 53 bones including 30 finger bones.
- **Pose:** an authored relaxed standing pose (arms aimed in world space) and a relaxed finger pose.
- **Build:** 5.5 s headless on the CPU; GLB 15.9 MB **[M]**.

Wardrobe limit **[V]**: the system pack's only professional women's outfit is a striped blouse and skirt, and every shoe
comes with sports socks. That is why the study uses a man in a business suit.

## 2. The two treatments (same character, pose, light and camera)

| | Refined toon | Painterly |
|---|---|---|
| **Shading** | Light amount cut into crisp bands; each band recolours the colour beneath (warm skin shadows, cool cloth shadows) | Same bands, softened, then a Kuwahara brush filter on the character only, warm-light / cool-shadow split toning and pigment grain |
| **Ink** | Bold silhouette outline plus interior lines (nose, lips, jaw, lapels, folds) found from surface-normal edges | Thinner, softened silhouette and interior lines |
| **Textures** | Photographic skin and cloth simplified into colour fields (lips, brows, shirt, tie kept; pores and weave removed) | Same |
| **Fit with the plates** | Closer: shares the plates' ink line and flat bands | Softer; slightly blurs the ink line the plates rely on |
| **Still render time, 1080p, incl. PNG readback [M]** | 1.0–1.3 s (medium, turnaround, hands); 2.9–4.4 s (close-up, wide) | 3.2–5.4 s |

**My assessment:**
- **Close-ups:** the painterly version is kinder to faces; it hides the patchy skin bands.
- **Fit with the environments:** the refined toon version fits the existing ink-and-flat-colour plates better.
- **Speed:** painterly costs 2.5–3× more per frame.

## 3. Inspection results

| Check | Method | Result |
|---|---|---|
| **Clothing intersections** | For every body vertex, a ray along its normal: a garment just *inside* the skin with nothing outside it is a poke-through (`inspect_character.py`). Run on the exported GLB in 6 poses | Standing: **0** suit and **0** shoe poke-through vertices **[M]**. Walking: **26–40** wrist and hand vertices where the sleeve cuff passes inside the hand as the wrist flexes, up to about 19 mm. A real, small cuff issue for M3. Shoes: 0 in every pose |
| **Hair attachment** | Same test, scalp against hair, plus the hair-to-scalp distance | Gap at the 10th percentile **0.6 mm**: the hair sits on the head and does not float **[M]**. 56 crown vertices lie outside the hair shell, up to about 20 mm, but none show through in the top or back views (`m23_5_hair.jpg`) |
| **Eye alignment** | Eyeball centres in the GLB; offset from MPFB's eye-joint helpers at build time | Left and right symmetric within **0.27 mm**; height difference **0.03 mm**; interocular distance **60.3 mm** (adult typical); both eyeballs sit 8.5 mm in front of the joint helper, identically **[M]**. Close-ups show the irises centred under the lids |
| **Skin shading** | Visual | Hue-shifted bands read as illustrated. On this face's geometry, though, the bands form **patchy, mask-like areas** on the cheeks and nose in toon close-ups. This is the weakest point. Painterly softens it |
| **Facial expressions** | Shape keys: neutral, concern, smile, surprise, blink | All five read. The expression keys were transferred to the brows (8), lashes (4), teeth and hair, so brows lift with the skin, lashes close on a blink, and teeth show on surprise **[M]** (`m23_3_expressions.jpg`). The smile is subtle; stronger targets would be a tuning step |
| **Hands** | Visual, both hands | Relaxed hands are anatomically natural, with five fingers and a believable curl (`m23_4_hands.jpg`). **The grip on a folder is not acceptable:** the fingers don't wrap it and the folder passes through the hand. Tuned grips and contact are M3.2 |
| **Consistency from every angle** | Turnaround 0°, 45°, 90°, 180° | One model, so identity, proportions and clothing are consistent by construction **[M]** |

## 4. Asset-loading safeguard (implemented and tested)

**The problem, now measured [M].** A character layer that loads its model asynchronously was rendered by HyperFrames
before the model existed:
- **0 of 120 frames** contained the character with a 4-second load, and again with a 20-second load;
- in both cases the render **reported success**.

**The fix, in three parts:**
1. **`kit/assemble.py ready_gate=[...]`** (opt-in; without it the output is byte-identical to before, which a test
   verifies).
   - The timeline is registered only after every named layer calls `window.__elReady(name)`. HyperFrames supports late
     registration (it polls for up to 45 s, then rebinds) **[V]** (hyperframes 0.9.88 source).
   - `window.__elFail` or a 40-second timeout raises an uncaught page error. HyperFrames treats that as a fatal script
     failure, so the render **aborts** instead of writing blank frames.
2. **`scripts/lib/frame_state.mjs compositionURL()`.** The QA tools (qc, layout, figure, contact and isolation checks)
   open documents that contain ES modules over a local HTTP server, because Chromium blocks modules from `file://`.
   Other documents keep `file://`.
3. **A pinned single-file three.js r186.1 bundle for the character layer** (`three186-char.js`, 793 KB, built with
   esbuild from `charlab/three_bundle_entry.js`), with no import map.
   - **Why:** `render.py` finds a reduced document's files by their literal paths. Files reached through an import-map
     prefix were missing, so the loader returned 404, the reduced chunk failed, and `render.py` fell back to the full
     document.
   - **Side effect:** the same gap would also have hidden loader changes from the render cache.
   - **Result:** with one literal file there is no gap.

**Test results with `render.py --isolate --jobs 2` and the real 15.9 MB character [M]:**

| Variant | Frames with the character | Outcome |
|---|---|---|
| No gate, 4 s load | 0 / 120 | "success": the silent failure |
| No gate, 20 s load | 0 / 120 | "success": the silent failure |
| Gate, 20 s load, layer in its own script region | **120 / 120** | Both chunks from reduced documents, isolation check passed, no fallback |
| Gate, layer reports a failure | none written | **Render aborted, exit 1** ("asset gate: char: …") |

Automated tests: `tests/epoch_ledger/test_asset_gate.py`, 3 tests. They cover the gate being off or on, the timeline being
held until the layer is ready, a failure surfacing as a page error, and module documents being served over HTTP. The
whole suite passes: **92 tests**.

## 5. Comparison with Rig v4 (`m23_6_rig4_comparison.jpg`)

| | Rig v4 (stored frames) | New character |
|---|---|---|
| **Anatomy and hands** | Simplified; hands are drawn shapes | Natural proportions and five-finger hands |
| **Consistency across angles** | Views are separate drawings | One model, consistent by construction |
| **Clothing** | Flat shapes | Real garments: collar, tie, lapels, cuffs, shoes |
| **Faces** | Simple, very readable | Detailed but generic; patchy shading in toon close-ups |
| **Style fit with the vector plates** | **Native**: same flat vector language | **Partial**: a shaded figure in front of flat vector sets; the toon treatment narrows the gap but doesn't close it |

## 6. Honest verdict against the brief

| Requirement | Status |
|---|---|
| Natural human proportions | **Met** |
| Expressive eyes | **Partly.** Eyes are aligned and visible, but small; they read in close-ups only |
| Detailed hair | **Partly.** Strand texture shows, but the hairstyle is a stiff low-poly helmet |
| Believable clothing | **Met** standing; small cuff intersections in motion |
| Anatomically correct hands | **Met** relaxed; **not met** when holding objects (M3.2) |
| Illustrated, not plastic | **Partly.** Clearly not plastic or photoreal, but still reads as a stylised 3D game character, not premium illustration |
| Not a mannequin or simplistic cartoon; no uncanny realism | Mostly met; the face is generic |
| Compatibility with the environments | **Partly** (§5) |

**Conclusion.** The pipeline works end to end, and the technical bar is met: anatomy, consistency, expressions, assets,
licensing, safeguard and QA. **The premium illustrated look is not yet reached.** The remaining gap is art direction:
- faces;
- hair;
- the style match with the flat vector sets.

None of these are engineering problems.

## 7. Performance note **[E]**
Still times are not frame times, but they set expectations:
- **Refined toon:** about 1.2 s per medium shot.
- **Painterly:** about 3.3 s per medium shot.

Both are measured on one character over a plate, on 4 CPUs. An episode with many character shots would need several
hours of rendering per 10 minutes. The cost can be cut a lot by halving MSAA, using a smaller shadow map and skipping
the ink-normal pass in wide shots, but none of this is measured yet. No 2–3-episodes-a-week claim is made; that is the
performance milestone M4.2.

## 8. Recommendation

**Do not adopt this look as final yet.** Approve one focused art-direction iteration, **M2.3b**, still images only, with a
clear exit criterion. Do not approve motion work yet.

M2.3b would test a third treatment closer to the series:
- **"Flat editorial illustration":**
  - palette-driven flat fills instead of photographic textures;
  - two shading bands;
  - bolder, variable-width ink;
  - painted facial details (liner, brows, lips, cheek accents) as decals;
- **stylised hair** built as shaped cards;
- **modest facial stylisation** through MPFB targets (jaw, cheekbones, eye shape) for a distinctive, mature editorial face;
- **one female character** from the same pipeline, to show range despite the limited wardrobe.

**Exit criterion:** you judge one character's close-up and medium shot, placed in the bank or bakery set, as matching the
series. Otherwise we consider the alternative: keep the 3D skeleton only for mechanics, and render characters in the
series' vector style.

**Estimate [E]:** a human developer 3–5 days; Claude about 3–6 h, medium usage.

**Clothing is still limited.** The free system wardrobe is small. More professional outfits would need CC0 community
packs, each checked for licence, or garments modelled by us.
