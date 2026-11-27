# The Epoch Ledger — production character standard (approved in P5)

**Approved (P5):** 7.5 heads is the preferred adult target, 7.0–8.0 the accepted range. Snow and Rain are technical test
characters only and are never promoted into the adult cast.

**Desired aesthetic:** premium stylised 3D adult animation with:
- natural adult proportions and smaller heads;
- moderately sized eyes;
- defined adult jaws, noses and facial structure;
- natural shoulders and integrated necks;
- articulated hands;
- sophisticated hair and clothing;
- expressive but restrained faces;
- illustrated, stylised materials: not photoreal skin and not plastic toy surfaces.

Characters appear only when they serve the story. When they do, they must read as **mature adults in a premium,
stylized financial and historical documentary**: not children's animation, not a video game.

## 1. Measurable criteria (checked with `convert/measure_props.py` on the evaluated mesh, A-pose or T-pose, no hair)

| Criterion | Typical adult target | Accept range | Snow | Rain | Einar | Why |
|---|---|---|---|---|---|---|
| Body height in heads (crown→floor ÷ crown→chin) | 7.5 | **7.0–8.0** (older or shorter characters 6.8) | 5.9 ✗ | 5.8 ✗ | 7.0 ✓ | Large heads read as young or cartoon |
| Shoulder width (biacromial, in head heights) | men 1.6–1.8; women 1.35–1.5 | men ≥ 1.5; women ≥ 1.3 | 1.25 ✗ | 0.81 ✗ | 1.64 ✓ | Narrow shoulders read as children |
| Eye width ÷ head width | 20–22% | **≤ 24%** | 27% ✗ | 33% ✗ | 21% ✓ | Moderately stylized eyes, no anime or doll eyes |
| Neck | Neck width ≥ 0.45 × head width; trapezius slopes into the shoulders | Visual check from front and three-quarter | ✓ | ✓ | ✓ | No pasted-on heads (the M5 failure) |
| Face | Adult skull: jaw and chin defined; nose and mouth not shrunk; cheeks not infant-round | Visual check | ✗ | ✗ | ✓ | |
| Hands | Five fingers, adult hand length ≈ 0.75 × face height | Visual check | ✓ | ✓ | ✓ | |

**Style band.** Stylized, not realistic: simplified forms, designed hair, a painterly or illustrated surface, and
appeal. Faces stay readable at documentary shot sizes. Einar meets the proportions but sits at the realistic end;
Mikassa's look is the closest reference found for the intended band.

## 2. Construction requirements
- **Face rig:** shape keys, or bones plus a pose library, covering jaw, lips (open, round, wide, press), cheeks, brows
  (inner and outer), lids and eye aim. `convert_char.py` bakes these into our morph names.
- **Mesh:** hair and clothing as separate meshes, no particle hair; separate eyes with an iris/pupil texture or mask.
- **Rig:** CloudRig or Rigify; T-pose or A-pose rest (both supported since P3).
- **Wardrobe:** suits, shirts and dresses, with period variants (1870s, 1920s, 1970s, today) swappable on the same body.
- **Budget:** about 250k rendered triangles or fewer, and 15 texture tiles or fewer, at 1024 px for the runtime.
- **Licence:** CC0 or CC-BY (commercial use; credit known), or a commissioned work assigned to us.

## 3. Cast plan
Two adult professionals (one woman, one man, 30–50), two older adults (55–70), one young adult. Period variants come
from wardrobe, not new bodies.

## 4. Rules
- Snow and Rain stay technical test characters (Rain may play a younger character only). Do not scale Snow's head or
  reshape Rain: that breaks their face rigs and designs.
- A character passes only if it meets every row of §1 and §2 in measured numbers and in front, three-quarter and
  profile views. Lip sync or a good test render alone is not proof.

## 5. Performance in narrated documentary scenes (permanent standard)
Narration is an independent voice-over, not character dialogue.
- **No automatic lip sync to the narrator.** A character's mouth is never driven by, or timed to, the narration track.
- **What a character does instead**, in priority order: natural body language and weight; subtle breathing; blinks;
  eye movements, with the eyes leading the head; restrained emotional expressions; meaningful gestures; interaction
  with the environment (documents, desks, tools, other characters).
- **Lip sync only for scripted dialogue with an assigned voice.** A character speaks only when the script gives them
  an explicit line and a speaking voice of their own (not the narrator's). Only that line's time range moves the mouth.
- **Retained, disabled by default.** The lip-sync capability stays (`lipsync.py`, `splice_dialogue.py`, the actor
  `speech` track in `elmotion.js`; `say()` in Rig v4). It does nothing unless a shot asks for it explicitly, and
  narrator-driven scenes do not ask for it.
- **Face-rig requirement unchanged:** §2's lip units are still required, so a character *can* speak a scripted line.

## 6. P6 prototype (CharMorph Reom, geometric stylisation): measured against this standard
- **§1 passes for all three variants:** 7.41 / 7.51 / 7.74 heads; shoulders 1.50 / 1.53 / 1.59 head heights; eye
  opening 16.9–18.6% of head width.
- **Construction:** separate wardrobe and mesh hair; Rigify rig data and 51 facial blendshapes present (untested).
- **The style band is not met:** the forms, hair, brows, eyes and materials still read as a generic sculpted avatar,
  not a premium stylised character.
- A proportion pass alone does not make a character acceptable. See `../P6_REPORT.md`.

## 6. Candidates checked in P4 (official public previews only; nothing downloaded or purchased)
Sheet: `projects/charlab_p4/5_candidates.png` (compressed copy: `evidence/p4_5_candidates.jpg`).

| Candidate | Access | Licence (per page) | Fit against §1 | Verdict |
|---|---|---|---|---|
| **Mikassa** (Project Gold) | Blender Studio login and **paid membership** | CC-BY | Adult woman, mature face, small eyes, ≈7.3 heads (estimated from the T-pose preview), CloudRig | **Closest candidate.** Needs documentary wardrobe; measure after download before any decision |
| Victor (Cosmos Laundromat) | Login and paid membership | CC-BY | Caricature: large head and hair, large round eyes, narrow shoulders | Fails the mature standard as designed |
| Vincent | Login and paid membership | CC-BY | Caricatured long-legged proportions, cartoon register | Fails |
| Storm | Login and paid membership | CC-BY ("Storm Rig (CC) Blender Foundation \| studio.blender.org") | A child | Younger roles only |
| Einar (Charge) | **Free download** | CC-BY | 7.0 heads, shoulders 1.64, eyes 21% (measured in P3) | Passes the proportions; realistic style sits outside the stylized band. Possible older or secondary character after a style test |
| Other free sources (Sketchfab, CGTrader, Superhive "free") | Various | Mostly marketplace "royalty free", not CC; rarely a face rig | None found that meets §1–§2 | Not recommended |

**Licence and attribution:**
- The Blender Studio character pages state CC-BY.
- Only Storm's page gives an explicit credit line; the series uses the Blender Studio form "<Name> Rig (CC) Blender
  Foundation | studio.blender.org".
- Licence files inside downloads can only be checked after logging in.
- Membership (from the join page): $17 a month, or $34.50 per three months.

**Recommendation:**
- If you approve one month of membership, download Mikassa (and Victor for completeness), then run
  `measure_props.py` and the conversion pipeline. Decide on measured numbers and a wardrobe plan.
- The only route to a complete, consistent mature cast remains a commissioned character artist working to this
  standard.
