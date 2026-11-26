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

## M4 findings (motion quality and environments)
| Item | State | Direction |
|---|---|---|
| Mocap pops (CMU 18_08 jumps the whole upper body at 6.7 s) and jitter | **Fixed** at clip preparation: outlier frames repaired, light 5-tap smoothing | Keep the smoothness analysis (`window.analyze()`) as a gate for new clips |
| Seated mocap 114_05 slouches (reclined, legs out) | Not used for professional seated characters; the upright seated hold of 113_15 is used instead | Find or capture an upright seated idle with subtle life |
| Restrained arms looked robotic (snapped toward one stance) | **Changed**: restraint now eases toward the clip's own slow posture | Authored gesture library per character (beat, frame, point, enumerate) |
| Reach onsets made the elbow jump | **Fixed**: IK weight blending, bend-plane-preserving pole | — |
| Feet: plant snaps, shuffling | **Fixed**: 0.2 s ramps, 3.5 cm leash | — |
| Walk-to-chair | Works by chaining walk → stop → sit backwards from the chair anchor (`place: "next"`); not phase-matched | Phase-matched chaining for 'next' placement |
| Environment props are box-built | Readable and consistent with the editorial look, but simple | Bevels and a few hand-shaped hero props (chairs, lamp) per set |
| Depth of field | **Done in M5** (editorial look: depth-based 16-tap DOF per camera key) | — |

## M5 findings (look, characters, narration-driven sequence)
| Item | State | Direction |
|---|---|---|
| Characters read as game NPCs | **Improved** (D redesign: smaller skull, longer neck, larger eyes, refined nose and mouth, flatter skin, editorial shading) but still the main gap | The MakeHuman base topology and stock clothes/hair cap the result. Premium hero characters need an artist pass: sculpted head (Blender Human Base Meshes, CC0, is a good start), modelled hair cards, tailored clothes with folds, hand-painted textures. Keep the rig and motion stack; replace meshes |
| Base mesh alternative (Blender Human Base Meshes v1.4.1, CC0) | Evaluated: better head/neck design, but bare sculpt bases (no clothes, hair, rig compatibility, expressions); cartoon-sized eyes | Use as a sculpt start for an artist pass, not as a drop-in |
| Head looked stuck / mechanically locked on the other person | **Fixed**: gaze shares head 72%, neck and spine take part, seeded micro-motion and short aversions, head stabilised toward upright | Per-character gaze personality (frequency of aversion) |
| Lip sync | **New**: only for a character's own spoken line (`speech` track); Kokoro voice + Whisper timing + letter-to-viseme with loudness | Phoneme-level alignment (e.g. a G2P pass) for crisper consonants; teeth read flat grey, mouth interior needs a dark cavity |
| Hands | Mocap hand poses plus IK contact; fingers stiff and thick | Hand mesh refinement and a richer gesture library |
| Clothing | Stock MakeHuman proxies with editorial ink; folds painted only by shading | Modelled garments with sculpted fold geometry |
| Bakery set | **Rebuilt** to read as a bakery (display case, breads, rack, oven, till, chalkboard, baskets, sacks, pendants, tiles, ceiling) | Hand-shaped hero props; food materials with subtle gradients |
| Lights above a closed ceiling | A ceiling slab darkened the room even with `castShadow=false`; the ceiling is now an unlit plane | Find the stage's shadow path for env meshes |
| 2D/3D style match | 2D scenes use the same paper, ink and palette as the 3D sets | A shared token file for both |

