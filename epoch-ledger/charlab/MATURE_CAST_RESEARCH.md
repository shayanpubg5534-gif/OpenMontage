# Mature adult cast: technical approaches investigated (P5)

**Goal:** a consistent, reusable cast that meets `CHARACTER_STANDARD.md`: 7.5 heads preferred, 7.0–8.0 accepted;
mature faces; moderately sized eyes; premium stylised, illustrated materials.

**Constraints:** nothing purchased, no accounts created, no artist contacted.

**Evidence** (`projects/charlab_p5/characters/`):

| Sheet | Content |
|---|---|
| `1_candidates_views.png` | Front, three-quarter, side and full-body views, native vs shading-only test |
| `2_proportions.png` | Orthographic silhouettes with measured proportions |

Measurements: `convert/measure_props.py`.

**Labels used below:**
- **Feasible:** shown with evidence here or in earlier milestones.
- **Partly feasible:** works for some requirements, evidence-backed.
- **Speculative:** plausible, but not demonstrated.

## 1. Mature parametric adult bases

| Base | Licence | Measured | Rig / face | Hair, clothing, materials | Verdict |
|---|---|---|---|---|---|
| MPFB2 / MakeHuman | Code GPL; **generated characters CC0** | Adult proportions are parametric (M5 Nadia 6.66 heads, from our own stylisation choices) | Game-engine rig plus MakeHuman expression targets, already mapped to our morph names (M2–M5) | Generic proxy hair and clothing; skin realistic or our flat looks | **Feasible technically, proven** (M2–M5 cast built automatically). **Fails the aesthetic** ("NPC" look, rejected in M5) |
| CharMorph Reom / Antonia | Tool GPL-3; **bases CC-BY** | **7.41 / 7.57 heads** (pass) | Rigify with face rig is generable in CharMorph. *Not verified in P5: our exports are unrigged meshes* | Nude bases; particle hair broken in our renders (P2 gate); realistic skin | **Partly feasible:** good adult anatomy, no character |
| CharMorph MB-Lab male | Base **AGPL** | 7.88 heads | As above | As above | **Avoid:** AGPL obligations on derived assets are unclear for commercial video |

## 2. Commercially usable adult meshes with suitable rigs

| Candidate | Licence and access | Measured / observed | Verdict |
|---|---|---|---|
| Einar (Blender Studio, *Charge*) | CC-BY, free download | **6.98 heads**, shoulders 1.64 hh, eyes 21% | Proportions at the threshold. Realistic, aged, post-apocalyptic costume, prosthetic arm. See §4 |
| Mikassa (Blender Studio) | CC-BY, paid membership | About 7.3 heads (estimated from a preview), mature face, small eyes | **Closest found.** Not measurable without the membership (P4) |
| Victor, Vincent, Storm | CC-BY, paid membership | Caricatures or a child | Fail (P4) |
| Marketplace "free" models | Mostly royalty-free terms, not CC; rarely face-rigged | — | Not recommended |

## 3. A reusable adult base with controlled stylisation and a face rig

**Blender Human Base Meshes bundle v1.4.1** (CC0, Blender Foundation; already on disk):
- Realistic and stylised male and female bodies and heads, with clean animation topology.
- No materials, hair, clothing or rig.
- **It is a sculptor's starting point, not a character.** Using it means artist sculpting, then rigging (Rigify),
  then our converter.

**Automatic stylisation of a realistic base:**
- **Shading only:** tested in P5 (Workbench texture colour, cavity, outline; same cameras; no mesh change).
  **It failed for all three candidates**: realistic forms, wrinkles and pores, costume and hair all remain (sheet 1).
- **Geometry by morphs and smoothing:** tried in M2.3c (stylise.py). Rejected in M5. This is also exactly the
  "scale parts" path the standard rules out.

**Verdict:** feasible **only with sculpting work**. No automatic method here reached the approved aesthetic.

## 4. Can Einar be adapted?

- **Licence:** CC-BY allows modification with attribution and an indication of changes. No obstacle.
- **Rig:** CloudRig from the same studio as Snow. Our converter could ingest him with a new profile (about an hour of
  bone mapping). *Not done in P5.*
- **Blockers:**
  - Realistic sculpt and skin, so shading alone fails (sheet 1).
  - The costume (beanie, winter gear, satchel) is modelled for a post-apocalyptic film.
  - The **prosthetic mechanical arm** is part of the character.
  - 6.98 heads, at the lower threshold.
  - He covers one niche only: an old man.
- **Verdict:** not adaptable into our style without sculpting and a new wardrobe, which is artist work. At best he
  could serve as a specific rugged older-man role, after an arm and costume replacement.

## 5. Can procedural Blender development produce a consistent cast?

- **Consistency, proven:** MPFB (MakeHuman) generates any number of characters on one topology, one rig and one
  expression set. Our pipeline already builds, rigs, dresses and animates them automatically (M2–M5).
- **Quality, not achieved:** stock MakeHuman heads, hair and clothing read generic. Our procedural replacements
  (M2.3c) did not reach premium quality.
- **Hybrid, speculative but the most promising:** an artist makes a **stylised style kit once**: stylised head and
  body targets, hair and clothing proxies, and a material set, all on the MPFB topology or a CloudRig base.
  Procedural generation then produces a consistent cast from it (age, build, ethnicity and wardrobe variants), and
  our converter, performance library and renderer take it from there. **Not demonstrated:** it needs the artist work
  first.

## Summary
- Free and automatic routes reach **adult proportions** (CharMorph bases measure 7.4–7.9 heads; MPFB is parametric).
- **None reaches the approved premium stylised aesthetic** without sculpting, hair and wardrobe made by a person.
- The single most promising asset is still **Mikassa**, behind a paid membership.
- The scalable route is an **artist-made style kit on a parametric base**, so the cast stays consistent and reusable.
- Both of those are your decision.
