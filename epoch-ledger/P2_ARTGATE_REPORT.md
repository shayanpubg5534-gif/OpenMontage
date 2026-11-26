# Artistic-direction gate: static comparison of character foundations

Status: static evidence only. No animation renders, nothing promoted, Rig v4 and the production pipeline untouched, no
purchases or paid APIs. M5 stays a conditionally accepted technical baseline. Date: 2026-11-26.

**Short answer.** Of everything freely available, only professionally designed characters (Blender Studio, approach A)
reach the quality you are asking for: head, neck and shoulders that read as one anatomy, designed hair, real mouths and
teeth, and expressions that use the eyes, brows, cheeks and jaw. But they are fixed, individual film characters, not a
customizable cast, and they do not plug into our runtime without a conversion pipeline. The tools in this environment
cannot, on their own, produce a consistent, customizable, premium adult cast: that needs a human character artist. My
recommendation is below (§5).

## 1. What was evaluated (evidence: `projects/charlab_artgate/evidence/sheets/`)

| Sheet | Approach | What it shows |
|---|---|---|
| `A_blender_studio.png` | **A. Professionally designed Blender Studio characters** | Snow, Rain, Einar, Victoria, Ellie and Rex in native Cycles with one neutral light rig: full body front / ¾ / profile, close-ups front / ¾ / profile, and an expression from each character's own pose library. Arms posed down by script (Rain's rig did not take the pose) |
| `A_in_set.png` | A, in a documentary environment | Snow and Victoria inside our bank set (exported from the runtime), Cycles, medium and close-up |
| `B_2d_illustrated.png` | **B. Premium 2D illustrated, drawn by code** | Original female and male designs: turnarounds, four expressions incl. a speaking mouth, hands, and an illustrated bank-office scene |
| `C_charmorph.png` | **C. CharMorph** | Antonia, Reom and MB-Lab male bases as imported headlessly, default hair |
| `D_m5_baseline.png` | **D. M5 baseline** | The M5 characters in our runtime, incl. the dialogue close-up with the neck you flagged |
| `E_integration.png` | Integration tests | A Blender Studio character exported into our three.js runtime as-is, and rendered in Blender on this CPU-only machine |

Candidates not evaluated, with reasons:
- **Login required:** Storm (Blender 5.0), Mikassa (Gold showcase, adult woman, Blender 4.2) and Victor (Cosmos
  Laundromat, adult man) need a Blender Studio login, which is probably a paid subscription. Official pages if you want
  to fetch them manually: https://studio.blender.org/characters/storm/ , https://studio.blender.org/characters/mikassa/ ,
  https://studio.blender.org/characters/5d41b19f28b38e1763906a9a/v2/ . Mikassa and Victor are the two that would add
  adult characters to approach A.
- **Not rendered:** Jay, Phil (Sprite Fright teenagers, same style as Ellie and Rex) and Gabby (Settlers, cartoon).
- **CharMorph Vitruvian** (CC0; 100+ FACS face shapes incl. visemes; six real hairstyles): its files are in Git LFS,
  which this session's read-only Git access does not serve. Official source: https://github.com/Upliner/CharMorph-Vitruvian
- **Ruled out by the brief:** low-poly game packs (Quaternius, KayKit), Mixamo (game style, Adobe terms), and AI
  image-to-3D (needs a GPU; meshes not suited to facial animation).

## 2. Assessment against your criteria

Ratings: ●●● strong, ●● adequate, ● weak, ✗ fails or absent.

| Criterion | A · Blender Studio | B · 2D illustrated (code-drawn) | C · CharMorph | D · M5 |
|---|---|---|---|---|
| Head, neck, jaw and shoulder integration | ●●● (Snow, Einar); ●● caricatures by design (Rex, Victoria) | ●● after a dedicated fix; still simplified | ●● anatomically realistic | ✗ (female neck pasted-on) |
| Facial expressions and individuality | ●●● strong designed individuality; expression and phoneme libraries ship with most | ●● readable, limited range | ● face rig present, bases generic | ● |
| Hair | ●●● designed sculpted hair, groom on some | ● smooth caps | ✗ default particle hair broke in headless import | ✗ helmet-like |
| Clothing | ●●● modelled, with folds | ● flat shapes | ✗ none (underwear only) | ● |
| Hands | ●●● | ✗ glove-like | ●● realistic | ● thick |
| Materials, lighting, shading | ●●● in Blender; ✗ in our runtime as-is | ●● consistent paper/ink/palette | ●● realistic skin | ● |
| Male and female compatibility | ● each film has its own style; Snow + Rain are one family but young | ●●● same hand | ●●● same generator | ●●● |
| Custom hairstyles, ages, body types, ethnicities, historical clothing | ✗ one fixed character each; changes need a 3D artist | ● every variation is a new drawing | ●●● morphs for age, body, ethnicity; clothing and hair need assets | ●● morphs, but rejected look |
| Reuse across subjects and periods | ● recognisable film characters, modern clothes | ●● with an illustrator, cheap to extend | ●● | ●● |
| Facial animation, lip sync, body movement | ●●● rigs, shape keys, phoneme poses (Rex, Victoria, Ellie, Snow) | ●● mouth swaps (e.g. Rhubarb Lip Sync, MIT, offline) and cut-out motion | ●●● FACS + visemes (Vitruvian only) | ●● (our viseme track) |
| Integration with HyperFrames / OpenMontage | ✗ as-is (§3); ●● after a bake/convert pipeline or with Blender rendering | ●●● SVG in HyperFrames today | ● same problems as A, plus particle hair | ●●● |
| CPU rendering cost (this 4-core container) | Cycles 6–30 s per full-body view, 11–56 s per close-up (Victoria's strand hair up to 284 s); EEVEE 59–186 s; our runtime ~1–5 s if converted | milliseconds per frame | Cycles 5–42 s per view | ~1–5 s |
| Licence for commercial YouTube | CC-BY: commercial use and modification allowed, credit required | ours | Antonia, Reom CC-BY; Vitruvian CC0; **MB-Lab AGPL-3 (avoid)**; add-on GPL-3 (tool only) | CC0 assets |

Notes from the review of the sheets:
- **Environments must rise with the characters.** Snow placed in our bank set (`A_in_set.png`, Cycles, about 22 s per
  1280×720 frame) shows the mismatch at once: next to a professionally made character, our primitive-built furniture and
  painted window read as simple. A premium cast needs environments built to the same standard (modelled props, real
  materials, designed light), from CC0 sources such as Poly Haven plus our own set components.
- **Snow** is the only professionally designed character that suits an adult documentary as-is: a stylized young man
  with believable anatomy and a full expression library. **Rain**, from the same family, reads young (large eyes).
  **Einar** is near-realistic, a different style. **Victoria, Ellie and Rex** are deliberate caricatures (Sprite
  Fright): excellent craft, wrong register.
- **2D by code** reaches clean, consistent editorial illustration and reads well as a documentary frame, but hands,
  bodies, hair and three-quarter faces stay below a premium standard. A professional illustrator would change that; I
  cannot draw at that level by writing paths.
- **CharMorph** is a capable generator for realistic people (ages, body types, ethnicities by morph), the opposite of the
  stylized brief, and its hair and clothing need extra assets.

## 3. Integration requirements (measured, not assumed)

Exporting Snow to glTF for our three.js runtime (`E_integration.png`, `snow_gltf_export_report.json`):
- **Dropped modifiers:** 15 subdivision, 6 lattice (face shaping), 5 mirror (mirrored halves missing, e.g. one eye),
  14 mask, 7 corrective smooth and 5 surface deform (teeth and face attachments).
- **Shaders:** procedural skin shaders do not export; skin renders black.
- **Rig:** the 290-bone CloudRig deform chain is driven by control bones and drivers; rotating deform bones directly did
  not pose the arms.
- **Size:** 88 MB with textures.

Making approach A work in our pipeline therefore needs one of:
1. **A conversion ("bake") step in Blender, automated:** apply mirror and subdivision; turn lattice, surface-deform
   and corrective effects into shape keys; bake shaders to textures (or re-shade in our editorial look); export the
   deform skeleton with a mapping to our motion system's bones (retargeting); export the face shape keys and phoneme
   poses for our viseme track. Feasible with scripts, estimated one milestone, with risk around facial rigs that rely on
   drivers.
2. **Render characters in Blender** and composite them into HyperFrames as image sequences. Simple and faithful, but on
   this CPU-only container Cycles costs about 10–30 s per character frame at 1080p, about 2–6 CPU-hours for a 25 s
   sequence with characters on screen for half of it. Practical only with a GPU or more cores.

## 4. Can a professional artist pass happen inside this automated environment?

No, not for designing new characters. Code here can convert, re-dress from existing wardrobe pieces, recolour, light,
rig-map and render characters that someone has designed well, and it can generate realistic variations (CharMorph). It
cannot sculpt a specific, appealing stylized face, design a hairstyle, tailor period clothing or paint textures to a
professional standard; this gate shows the ceiling of what I can draw by code (`B_2d_illustrated.png`). A consistent,
customizable premium cast needs a human character artist (3D or 2D). The Blender Studio "Stylized Character Workflow"
files (Snow) document a professional process and are CC-BY, so they can serve as the technical template and reference
an artist works from.

## 5. Recommendation

1. **Direction: stylized 3D in the Snow family's standard**, built by a human character artist as a small cast (for
   example four to six adults of different ages, body types and ethnicities, with modular period wardrobes), using
   Snow's construction (CloudRig, shape-key face, designed hair) as the template. Keep our motion system, gaze,
   lip-sync track, sets, narration-driven direction and HyperFrames pipeline.
2. **Engineering, in parallel and automatable here:** the Blender-to-runtime conversion step (§3.1), proved first on
   Snow (CC-BY, with credit), so artist-made characters drop straight into the pipeline.
3. **Until there is an artist:** keep characters to wide and medium shots, and carry close storytelling with documents,
   diagrams and objects (the narration-driven principle already favours this). If close-ups are needed before then,
   Snow can stand in for a male lead under CC-BY with credit, but he is a recognisable Blender film character and there
   is no matching adult woman among the free downloads (Mikassa needs a login).
4. **Not recommended:** further procedural work on MakeHuman (M5), CharMorph for this brief, or code-drawn 2D as the
   final character style.

If you prefer a fully automated route with no human artist, the honest position is that the available free tools
cannot produce a substantial, consistent improvement in character design; the best automated option is (3) above.

## 6. Licences (exact, as published)
| Asset | Licence | Attribution / notes |
|---|---|---|
| Blender Studio characters (Snow, Rain, Einar, Victoria, Ellie, Rex, Jay, Phil, Gabby, …) | CC-BY (stated on each character page) | Credit Blender Foundation and studio.blender.org, e.g. "(CC) Blender Foundation \| studio.blender.org". Commercial use, monetised YouTube and modification are allowed under CC-BY with credit. They are recognisable characters from Blender's films |
| CharMorph add-on | GPL-3 (code) | Tool only; output is not code |
| CharMorph Antonia | CC-BY | Olaf Delgado-Friedrichs and contributors |
| CharMorph Reom | CC-BY | ComplexAce (mesh), Hope (morphs, textures) |
| CharMorph Vitruvian | CC0 | No attribution required |
| CharMorph MB-Lab bases | AGPL-3 | Avoid for commercial character use (licence written for software) |
| Blender Human Base Meshes | CC0 | — |
| 2D designs (approach B) | Our own | — |

## Evidence and reproducibility
- Sheets: `projects/charlab_artgate/evidence/sheets/` (not in git); compressed copies in `epoch-ledger/charlab/evidence/artgate_*.jpg`.
- Per-view renders and timings: `.runtime/charlab/bstudio/views/<name>/` (`timings.json`).
- Tools (in git): `charlab/bstudio/inspect_blend.py`, `render_views.py`, `render_in_set.py`, `export_gltf.py`,
  `integration_shot.mjs`, `export_set.mjs`, `charmorph_import.py`, `make_sheet.py`; `charlab/viewer/integration.html`,
  `export_set.html`; 2D designs `charlab/illus/heads.py`.
- Research notes: `charlab/ASSET_RESEARCH.md`.
