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

## M5 review (producer, 2026-11-26): characters rejected as an artistic standard
M5 is conditionally accepted as an experimental technical baseline only. Next gate: static artistic comparison, no
animation renders. Character problems named in the review (all open):
| Problem | Note |
|---|---|
| Helmet-like hair | Stock MakeHuman proxies and our procedural hair are shells, not designed hairstyles |
| Artificial skin and facial shading; flat, game-like lighting | Two-band shading on a generic mesh; no designed light on faces |
| Lifeless expressions (eyes, brows, cheeks, jaw) | Only 16 MakeHuman units; no cheek or jaw-driven deformation, no designed expression set |
| Thick, unnatural hands | Stock MakeHuman hand topology |
| Poor clothing geometry and materials | Stock proxies, no modelled folds |
| Limited individuality | Both characters come from the same generic base |
| Unconvincing mouths and teeth | Flat teeth, no mouth cavity |
| **Female neck: too large, pasted-on head** | Made worse by the D redesign (`measure-neck-height-incr` 0.6–0.7 lengthened it). Head, neck, jaw and shoulder integration is a mesh-design problem |
| Documentary elements to plan | Chart typography and hierarchy, financial-model-driven data (one model file per story, illustrative figures labelled), environment detail, original sound effects, render-performance bottleneck (Standard close-ups at ~5 s/frame) |

## Artistic-direction gate (static comparison, 2026-11-26) — see `P2_ARTGATE_REPORT.md`
| Item | State | Direction |
|---|---|---|
| Character foundation | Only professionally designed characters (Blender Studio, CC-BY) reach the brief; none form a consistent, customizable adult cast | Human character artist for a small stylized adult cast on Snow's construction template |
| Blender-to-runtime conversion | Naive glTF export breaks (modifiers, shaders, rig drivers) | Automated bake/convert step, proved on Snow first |
| Native Blender rendering on CPU | Cycles 10–30 s per character frame; EEVEE 59–186 s (software GL) | Only with a GPU or more cores |
| Environments vs. premium characters | Primitive-built sets look simple next to professional characters | Upgrade sets to modelled props and materials |
| Code-drawn 2D | Coherent but below premium (hands, bodies, hair) | Not the final style without an illustrator |
| CharMorph | Realistic bases; hair broken headless; Vitruvian blocked by Git LFS | Not for this brief |

## Producer decision after the artistic-direction gate (option D, hybrid)
- Snow is the reference for craft, anatomy, expressiveness, hair and shading. Rain to be investigated as a mature adult
  professional (no unjustified proportion changes; the M5 neck mistake is not to be repeated).
- Victoria, Ellie, Rex unsuitable as the standard cast; Einar too realistic to mix with Snow. CharMorph and code-drawn 2D
  stay experimental alternatives; M5 stays an experimental technical baseline.
- No artist hire, purchases or subscriptions at this stage; automated character development continues.
- **Environment upgrade (recorded separately, not this milestone):** the bank set looks too simple beside professionally
  designed characters; sets need modelled props, real materials and designed light to the same standard.
- Production direction stays a narration-driven hybrid: professional 3D characters only when they serve the story,
  cinematic 3D environments and object visualisations, advanced financial charts and diagrams, documents, maps,
  timelines and editorial illustration. Target: 2–3 quality documentaries per week.

## Conversion feasibility (Snow) — see `P2_CONVERT_REPORT.md`
| Item | State | Direction |
|---|---|---|
| Blender → runtime conversion | **Works** (geometry, skeleton, weights, 21 face morphs from his own rig, baked materials, clips) | Adopt as the experimental ingestion path |
| Eyes | Glassier than the original (no cornea refraction or placed highlight) | Runtime eye shader |
| Skin | No subsurface scattering in the runtime | Wrap-lighting term |
| Texture memory | ~350 MB GPU for one character | Half-resolution tiles / LOD |
| Gestures | Mocap 'talk' too theatrical; IK palm orientation wrong in the test | Calm conversational gesture library, palm presets |
| HyperFrames | Same loader path, not yet rendered through render.py | One render.py run after approval |
| Rain | Not adaptable to a mature adult without re-sculpting | Artist work or a different character |
| Cast | Only one suitable professional character (Snow) | Mikassa/Victor (login) or artist-designed characters, ingested by the converter |


## P3 — professional character runtime and cinematic integration — see `../P3_REPORT.md`
| Item | State | Direction |
|---|---|---|
| Snow's proportions | 5.9 heads tall, shoulders 1.25 head heights, eyes 27% of head width: inherent in the design (camera adds 7%) | **Technical test character only**; not a cast member |
| Rain | Young by design | Younger roles only |
| Adult cast | None meets the requirements (`CAST.md`) | **Your decision:** one month of Blender Studio membership (Mikassa, Victor, Storm; CC-BY) and/or a commissioned artist |
| Skin | Wrap + scatter approximation; tone matches native | Real SSS only with a heavier renderer |
| Eyes | Iris colour, pupil size, dark interior and catch-light now match the native | Cornea refraction is still approximated |
| Hair / shirt | Slightly darker than native | Per-character material tuning |
| Texture memory | 1024 px tiles: 84 MiB GPU vs 336, no visible close-up loss (PSNR 50 dB) | Use half resolution by default for converted characters |
| Gestures | Library of 11 presets; palms correct; seated rest hands; mocap sit clip still drives the torso | More seated clips; gesture variety per character |
| Cinematic set | CC0 PBR textures, detail, motivated light; about 2× the editorial render cost | Apply to the bakery set; textured books, real chairs |
| Window view | Painted plate, softened | A 3D street or photographic plate |

## P4 — mature standard, cinematic quality, CPU optimisation — see `../P4_REPORT.md`
| Item | State | Direction |
|---|---|---|
| HyperFrames cold starts | The local planner splits renders into chunks of about 10 frames, each a new page (GLB, textures, about 14 s of shader compile); this dominates cinematic render time | Single-session 3D shot renderer, composited in HyperFrames as a video layer (needs approval) |
| Balanced speed | 0.62–1.44 s per 1080p frame single-session (target 3–5 min per 10 s met only for locked-off wide shots) | GPU or many-core machine; locked-off or slow-move cinematography |
| Anchor switches on moving cameras | Small edge steps every 4–6 frames | Cross-fade between anchors, or a finer tolerance on edge-heavy shots |
| Balanced shadows | PCF (harder than VSM) | Soft PCF filter in the composed map |
| P4 look cost | +0.2–0.4 s per frame in Balanced (extra lights, bevels, street) | Move the rim and face key onto character-only lighting |
| Furniture | Bevelled boxes; books and chairs still simple | Modelled props (CC0 or commissioned) |
| Cast | No adult meets the standard; Mikassa is the closest (paid membership needed to measure) | Your decision: one month of membership and/or an artist commission |

## P5 — continuous-session rendering and mature cast research — see `../P5_REPORT.md`
| Item | State | Direction |
|---|---|---|
| Cinematic shot rendering | Continuous session: 9.96 s cold end-to-end in 505.5 s (8.4 min); warm re-render 1.6 s; resume frame-identical | GPU or many-core host for the 3–5 min target; locked-off and slow moves where the story allows |
| Per-frame render cost | 1.19 s per frame Balanced (SwiftShader) dominates | Hardware; fewer anchor rebuilds; lighter character shaders |
| Revision granularity | Per demo (shot) file | One demo per shot in documentaries; per-camera-cut ranges later if needed |
| Mature cast | No free or automatic route reaches the approved aesthetic; proportions solvable (CharMorph bases 7.4–7.9 heads) | Your decision: Mikassa (membership) and/or an artist-made stylised style kit on a parametric base |
| Einar | 6.98 heads; realistic; costume and prosthetic arm | Only with sculpting and wardrobe work |
| CharMorph bases | Exports unrigged; particle hair broken | Re-verify Rigify face-rig generation if pursued |

## P6 — permanent documentary animation standard (narration is not dialogue)
| Item | State | Direction |
|---|---|---|
| Narrator lip sync | Forbidden by standard; never existed in code (mouth tracks only from explicit `speech` / `say()`); now documented and test-guarded | Keep |
| Scripted dialogue lip sync | Retained, opt-in per line with an assigned voice, off by default | Use only where the script gives a character a line |
| Acting in narrated scenes | Breathing, blinks, gaze, expressions and gesture presets exist (elmotion, perflib) | More environmental interactions (handling documents, tools) and listening/reacting presets; no animation tests run in P6 |
