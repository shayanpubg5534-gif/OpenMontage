# Character development backlog (known limitations, kept for later milestones)

Recorded at the M3 motion milestone. Nothing here was worked on in M3 except where noted; no static appearance pass
was started.

## Appearance (from M2.3c, deferred)
| Item | Current state | Direction for later |
|---|---|---|
| **Hairstyles: not a permanent restriction** | The procedural generator (`stylise.py`) makes short, groomed, side-parted and pulled-back styles well (a shell over the scalp with clumps, a solid edge, an optional ponytail). It cannot yet make loose, long or layered hair: fringes, hair falling past the shoulders, curls, buns or asymmetric volume. Female characters are **not** limited to pulled-back hair as a rule; it is just what is available today | (1) Extend the generator with free-hanging lock sheets (cards with thickness) for shoulder-length and long hair, plus fringe pieces; (2) or a small set of hand-shaped hair meshes per recurring cast member, modelled once in free Blender, then skinned, expression-keyed and shaded by the existing pipeline; (3) long hair in motion needs hair bones or a cheap spring layer (see Motion) |
| Ponytail in motion | Rigid to the head bone | A two- or three-bone spring chain, or the spring layer used for the bag swing |
| **Mouth and teeth** | Stock teeth texture reads grey; open-mouth shapes (surprise) look tense; lips are the weakest feature | Flat-palette teeth and tongue treatment; tune the mouth-open target per character; add a few designed mouth shapes |
| **Hair rendering** | Highlight band can read slightly glossy on Nadia; colour zones are hard-edged | Matte highlight shapes; softer zone edges |
| **Facial lighting** | Hard key light gives one big shadow across the face in three-quarter views | Per-shot face fill, or a face-specific shadow threshold; decide in look development, not in motion |
| Clothing variety | One professional outfit per gender in the CC0 pack | More garments from CC0 sources or simple modelled garments |

## Motion (found during M3; see `P2_M3_REPORT.md`)
| Item | State | Direction |
|---|---|---|
| Mocap coverage | CMU has one usable sit, a few walks with stops and turns, and conversation clips with large gestures | Add clips as needed; gestures are mostly authored with arm IK for restraint |
| Turning in place | Not demonstrated; walking turns rely on the mocap clip | Procedural step-turn or a turn clip, with the foot pinning layer |
| Walk → sit in one move | Demonstrated from standing near the chair; a long walk ending exactly at a chair is not automated | Path planning that ends on the sit clip's start pose |
| Wrist and finger data | CMU has no fingers and poor wrists; fingers are posed by the compiler and wrists are eased toward the rest stance | Hand IK and finger poses are fine for documentary gestures; fine manipulation needs authored poses per prop |
| Skirt and thighs | Fixed for sitting with `cloth_follow_legs` (skirt weights follow the thighs below the hips) | Check other garments (long coats, wide trousers) when they are added |
| Lip sync | Not part of this milestone | Viseme shapes exist in MakeHuman; drive them from the narration timing later |
