# The Epoch Ledger — cast requirements and acquisition routes (P3)

Status: research and decision document. Nothing has been purchased, no account was created or logged into, and no
artist has been contacted. The decisions marked **(your decision)** are yours.

## 1. What the series needs

Characters appear only where they serve the story (DIRECTION.md); documents, diagrams, maps and objects carry the rest.
When a person is on screen, the cast has to read as **adults in a premium financial documentary**:

| Role family | Typical use | Needed |
|---|---|---|
| Adult professional woman, 30–50 | business owner, economist, banker, official | 2 designs |
| Adult professional man, 30–50 | business owner, banker, investor, clerk | 2 designs |
| Older man and older woman, 55–70 | merchant, statesman, depositor, retiree | 1 + 1 |
| Young adult, 20s | worker, customer, apprentice | 1 |
| Child / teen | rare, only when the story is about a young person | Rain (already available) |

Period variants (late 1800s, 1920s, 1970s) come from wardrobe and hair swaps on the same bodies, not new characters.
The cast should also cover a range of ethnicities.

**Design requirements** (from P2/P3 measurements; Snow and Rain fail the first three):
- **Adult proportions:** 6.5–7.5 heads tall (realistic references 7.5–8; Snow 5.9; Rain 5.8; Einar 7.0).
- **Shoulders:** at least 1.5 head heights for men, about 1.3 for women (Snow 1.25, Rain 0.81).
- **Eyes:** eye width no more than about 24% of head width (Snow 27%, Rain 33%, Einar 21%). The style is stylised,
  not caricatured.
- **Construction:** a face rig with jaw, lips, cheeks, brows and eyelids, through shape keys or bones. CloudRig or
  Rigify, so `convert_char.py` can bake expressions.
- **Mesh:** hair and clothing as separate meshes, not particle hair. Five rigged fingers.
- **Licence:** CC-BY or CC0, commercial use allowed, credit line known.
- **Runtime budget:** about 250k rendered triangles and about 15 texture tiles or fewer (Snow: 214k, 15).

## 2. What we have

| Character | Licence | Verdict |
|---|---|---|
| Snow (Blender Studio) | CC-BY | **Technical test character only.** Young, casual, oversized head and eyes (P3.1). The conversion pipeline, performance library and cinematic look were all proven on him |
| Rain (Blender Studio) | CC-BY | **Younger roles only.** Youth is sculpted into her proportions; the maturity study failed (P2). Do not force her into adult roles |
| Einar (Blender Studio) | CC-BY | Adult proportions, but a realistic style that doesn't match the art direction |
| Victoria, Ellie, Rex, Phil, Jay, Gabby (Sprite Fright etc.) | CC-BY | Unsuitable designs (creatures, children, cartoon register) |
| M5 MakeHuman characters | CC0 output | Baseline only: rejected for craft |
| CharMorph | GPL tool, CC0/CC-BY bases | Experimental; not a complete foundation |

## 3. Acquisition routes

### A. Blender Studio login-gated characters (paid subscription) — **(your decision)**
Verified on the official pages on 2026-11-26. Each asset page shows **"Login to Download"**. Downloads require an
active Blender Studio membership; the page comments and the join page agree. A free account is not enough.

| Character | Page | Licence (per page) | Blender | Notes |
|---|---|---|---|---|
| **Mikassa** | studio.blender.org/characters/mikassa/v1/ | CC-BY | 4.2 LTS (will not work in older versions) | Project Gold, Nov 2024, by Demeter Dzadik (CloudRig author: the Snow profile mostly carries over) |
| **Victor** | studio.blender.org/characters/5d41b19f28b38e1763906a9a/v2/ | CC-BY | 3.4 | Cosmos Laundromat (2015 film), v2 Jan 2023, by Beau Gerbrands; older rig: needs its own conversion profile (about an hour of mapping) |
| Storm | studio.blender.org/characters/storm/v1/ | CC-BY | 5.0 | Nov 2025, CloudRig; same family as Snow (highest converter reuse) |

- **Membership prices on studio.blender.org/join:**
  - $17 a month.
  - $34.50 every three months ($11.50 a month).
  - Organisation plans from $540 a month.
- **What the membership buys:** download access only. Use is governed by each asset's licence. The pages do not state the CC-BY version.
  CC-BY allows commercial use, modification and redistribution, provided the credit line is given (for example "Mikassa Rig (CC)
  Blender Foundation | studio.blender.org").
- **Exact requirements:**
  1. A Blender Studio account with an active membership (one month is enough to download).
  2. Download the asset files.
  3. Keep the credit in every video that shows the character.
  4. Check the licence file inside each download before production use. The page states CC-BY, but per-file notices
     take precedence. It was not possible to read inside the downloads without logging in.
- **Risks and caveats:**
  - Victor is the recognisable lead of a Blender film. CC-BY allows using him, but viewers may associate the series
    with that film; re-styling his hair and wardrobe is advisable.
  - Suitability (age, proportions, eye size) can only be measured after download. The measurement tools are ready
    (`convert/measure_props.py`).
  - Mikassa's and Storm's age and style should be checked on the preview images before paying.
- **Cost to us:** one month of membership; about 1 to 3 hours of conversion work per character; no recurring cost
  afterwards.

### B. Commission a human character artist — **(your decision; not contacted)**
The scalable route to a consistent, owned cast. Brief: 6 characters to the design requirements above, delivered as
`.blend` files with CloudRig or Rigify and face shape keys. The artist assigns the rights to us, or the work is
licensed CC-BY or commercially to us. Our pipeline ingests each through a conversion profile. The artist's choices
define the visual identity of the series. Budget and contract are your decision.

### C. Free alternatives (checked; none meets the bar)
- MakeHuman/MPFB (CC0 output): the M-series baseline, rejected for craft.
- CharMorph: experimental.
- Sketchfab CC-BY models: rarely rigged with faces; licence varies per model.
- Mixamo characters: Adobe terms, not CC; rights restricted, so we avoid them.
- VRoid and Ready Player Me: per-model or per-platform terms; anime or avatar register.

### D. Re-sculpt Snow or Rain
Possible, but this is artist work (route B in effect). Scaling body parts procedurally was ruled out, because it
breaks the facial rig and the design.

## 4. Recommendation
1. **Short term:** keep producing with narration-driven visuals. Use people sparingly, and use no adult cast member
   until one meets the requirements.
2. **Decision A** (lowest cost, fastest): approve one month of Blender Studio membership. Download Mikassa, Victor and
   Storm, then run the P3 measurement and conversion pipeline on each. This gives one adult woman and one adult man as
   candidates, if their proportions pass.
3. **Decision B** (long term): commission an artist for a cast designed for the series. Our pipeline is ready to
   ingest it.
