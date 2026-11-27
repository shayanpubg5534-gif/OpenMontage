# P7 — Professional character asset research (decision gate)

**Status:** research only. Nothing was purchased, installed, built or rendered, and no artist was contacted. Rig v4, the
P5 renderer, production defaults and the narration and dialogue standard are untouched.

**P6 recorded:** accepted as a technical experiment, rejected for production visual quality. **Variant B** (Reom) is the
preferred technical foundation, not an approved character. All P6 work is preserved.

Date: 2026-11-27.

**How facts were verified, and what was not:**
- This cloud environment's network blocks the vendor sites (Reallusion, Daz 3D, Fab, Superhive, Blender Studio):
  direct page fetches failed at DNS.
- Prices and licence terms below come from **web searches restricted to each vendor's own domain**, which quote the
  official pages. Each claim links to its official source.
- **I could not open the preview images.** The quality expectations below rest on vendor descriptions and the known
  output of these systems, **not on inspecting these listings' previews**.
- Before any decision, please look at the preview links (about 10 minutes). If you allow these hosts for this
  environment, I can fetch and compare the previews myself.

## 1. Requirements used for judging
Premium cinematic stylised adults; mature, believable proportions; designed faces, hair, eyes and clothing; men and
women of several ages, ethnicities and builds; interchangeable hair and wardrobe (business, casual, period later); full
body rig and hands; face expressions, blinks and gaze; optional lip sync for scripted dialogue; a Blender → GLB route
into our three.js runtime; commercial licence for monetised YouTube; CPU-friendly.

## 2. Ranked shortlist

### Rank 1 — Reallusion Character Creator 5 + ActorMIXER (system), evaluated before buying
| Item | Finding |
|---|---|
| Source | [Character Creator 5](https://www.reallusion.com/plan-and-pricing/individual/perpetual/character-creator-5-3101), [CC5 Deluxe](https://www.reallusion.com/character-creator/cc5-deluxe.html), [ActorMIXER](https://www.reallusion.com/character-creator/actor-mixer/), [HD Caricature MIXER](https://www.reallusion.com/contentstore/character-creator/3d-character/hd-caricature-mixer/default.html) |
| Previews | The official pages above; stylised examples: [Toon base article](https://magazine.reallusion.com/2023/12/27/former-disney-character-artist-adopts-reallusions-new-character-creator-toon-base/), [stylised CC5 → Blender workflow](https://magazine.reallusion.com/2025/11/27/a-stylized-wolverine-workflow-with-character-creator-5-actormixer-blender-hd-workflow/) |
| Price (one-time, perpetual) | **CC5 $299 list** (shown at $149.50 in a sale page). **CC5 Deluxe $647 list** (shown at $323.50; includes ActorMIXER PRO and the core library); an older page said $479. **HD Caricature MIXER $234 list** ($117 on sale). **ActorMIXER PRO $199 list** if bought separately. Free updates 5.1–5.9. The sales appear to end 30 November. A subscription also exists ([subscription page](https://www.reallusion.com/plan-and-pricing/individual/subscription)) |
| Licence | [Content License Policy](https://www.reallusion.com/license/content.html): the **Standard licence** lets you "export content to external tools and engines such as … Blender", and rendering images or video for commercial use is included. The former Extended privileges are now in Standard. **Caveats:** third-party marketplace packs carry their own terms. One clause limits *interactive or real-time products* to one character per licence; we render video, but our three.js runtime is real-time, so get written confirmation from Reallusion first |
| Characters and customisation | Unlimited identities from morphs: male, female, age, ethnicity, body type; ActorMIXER blends heads; the Caricature MIXER adds six stylised body archetypes; a large hair and clothing library (official and marketplace), including business wear |
| Rig, face, animation | Full body and finger rig; facial expression system and visemes (lip-sync tools), blink and gaze. Our standard keeps lip sync off unless a character has scripted dialogue |
| Blender / GLB | FBX, OBJ and USD export; free official "Blender Auto Setup". GLB via Blender, then our converter (a new profile for CC bone and morph names, about 1–2 days, as for Snow in P3) |
| Integration difficulty | **Medium.** **Windows-only** (no macOS, Linux or virtual machines, per Reallusion's FAQ), so characters must be authored on a Windows PC and exported to our Linux pipeline. HD meshes need a lighter export for the CPU runtime |
| Expected quality vs our standard | Proportions and maturity: high. Finish of skin, hair and clothing: professional. **Stylisation:** the toon and caricature tools trend toward cartoon or caricature, and the realistic base trends photoreal. The semi-realistic premium band in between depends on art direction |
| Limitations | A recognisable house look; stylised adult women are less covered; heavy meshes; Windows dependency; content packs cost extra (about $20–80 each) |

**Why first:** it is the only verified **system** that covers every requirement at once (identities, both sexes, ages,
wardrobe, rig, face, Blender export, commercial video) for a few hundred dollars. The open question is purely
artistic: can it reach our band? That can be tested without buying: the **30-day trial** allows limited exports
(30) and no commercial use, which is enough for an internal look test.

### Rank 2 — A custom artist-made style kit on Reom (from P6)
| Item | Finding |
|---|---|
| What | An artist sculpts stylised head and body targets as Reom morphs (male and female), plus 6–10 hair pieces, 8–12 garments (business and casual), and a painted material set. Our P6 pipeline generates the identities, measures them and fits them to the runtime |
| Cost | Rough market rates: a stylised, rigged character is about **$1,500–5,000** each ([vsquad](https://vsquad.art/blog/articles/how-much-does-a-3d-character-cost-vsquad/), [Meshy guide](https://www.meshy.ai/blog/3d-character-modeling-services)); hourly rates $45–150 by region. A style kit as scoped is **about $8,000–25,000 and 6–12 weeks** (my estimate from those rates; get 2–3 bids against a written specification) |
| Licence | A commissioned work assigned to us; Reom's CC-BY attribution remains |
| Quality | **The only route that guarantees our exact look**, consistent and owned |
| Integration | Low (our pipeline already does it); rig and face data are already in Reom |
| Limitations | Highest cost and risk (choosing the artist, revisions); period wardrobe is extra |

### Rank 3 — Fab: Lab3 Studio stylised corporate characters (pack, not a system)
| Item | Finding |
|---|---|
| Source | [Business Man 01](https://www.fab.com/listings/1d062181-d5bc-49b0-9331-ae6b7895548d), [Lab3 Characters Bundle 01](https://www.fab.com/listings/af731659-11b3-4306-b9cf-ecabfccad059), seller [Lab3 Studio](https://www.fab.com/sellers/Lab3%20Studio/about); similar: [Businessman – Modular – Rigged – Animated](https://www.fab.com/listings/7ddc1954-f7d7-49cf-acd0-b8662cc6ba7f) ($79.99, another seller) |
| Previews | The listing pages (not inspected by me) |
| Price | Lab3 prices were not in the indexed snippets; check the listings. Fab packs of this kind are typically under $200 |
| Licence | [Fab Standard License](https://www.fab.com/eula) allows distributing "rendered linear media", for example broadcast or streamed video. Fab is engine-agnostic, so standard licences are usable outside Unreal. The Personal tier is for revenue under about $100k a year. You may not resell the assets themselves |
| Characters | A few pre-built stylised "contemporary/corporate" men and women, plus a modular parts kit (15 clothing items in Bundle 01) |
| Rig and face | Unreal Quinn skeleton; ARKit blendshapes; blink example |
| Blender / GLB | Source FBX included, so Blender and then GLB is direct; a Quinn → our skeleton profile is needed |
| Difficulty | Low–medium |
| Quality vs standard | **Unknown until the previews are checked.** The description is "stylized art style" for games; likely game-stylised rather than premium cinematic |
| Limitations | Fixed identities, few ages and ethnicities, limited wardrobe, no historical clothing, no customisation outside Unreal (the "Mutable" system is Unreal-only) |

Useful as a **cheap integration test or background cast**, not as the main system.

### Rank 4 — Blender Studio "Mikassa" (one character)
- [Mikassa rig](https://studio.blender.org/characters/mikassa/v1/) (CC-BY, Blender 4.2+, CloudRig, pose library).
- **Membership:** $17 a month or $34.50 per three months ([join](https://studio.blender.org/join/)).
- **Possibly free:** a user comment on the page says there is a download button even without a subscription.
  **Unverified; worth checking before paying.**
- **Quality:** artist-made premium stylised, mature.
- **Limitations:**
  - One woman in fantasy costume; no wardrobe system, no male counterpart, no identities.
  - "Pretty heavy" production rig.
  - Needs a CloudRig profile, close to Snow's.
- Best as a **quality reference and a test of the pipeline**, not a cast.

## 3. Investigated and not recommended
| Candidate | Why not |
|---|---|
| **Daz 3D Genesis 9 + toon figures** ([Toon Generations 9](https://www.daz3d.com/toon-generations-9-character-for-genesis-9) $24.99; [bundle](https://www.daz3d.com/toon-generations-9-bundle-for-genesis-9) $54.99; [Toon Heroes](https://www.daz3d.com/toon-heroes-for-genesis-9); [Genesis 9 Toon shapes](https://www.daz3d.com/blog/filatoon-shader-and-genesis-9-toon-shapes)) | A huge library and cheap. **But:** the [EULA](https://www.daz3d.com/eula) allows renders and 2D animation, while real-time use needs per-product *Interactive Licences*. Exporting meshes to other software is, by forum reading, a grey area. Our runtime is real-time three.js. The toon range is anime or family-cartoon styled, not mature premium. Too much licence risk per asset |
| **Synty Sidekick** ([packs](https://syntystore.com/collections/sidekick-character-packs), $139.99–199.99) | A modular system, but a low-poly game look; tools are Unity and Unreal only |
| **Blender add-on character creators** on Superhive: [AutoCharacters](https://superhivemarket.com/products/autocharacters-male--female-body-presets-base) ($26.99–157.49 introductory, $59.98–349.97 list; clothing only in "Complete"; the licence field says "Creative Commons" while the tiers say Standard and Commercial, an unresolved inconsistency), [Classic Stylized Male](https://superhivemarket.com/products/customisable-stylized-male-basemesh--rigged-with-90-blendshapes), [Easy Characters](https://superhivemarket.com/products/easy-characters) (free) | Blender-native and easy to integrate. Quality and style could not be verified (previews not viewable); descriptions suggest generic or game bases; business wardrobe not confirmed. **Worth a preview check only**, not a recommendation |
| **MetaHuman** ([2025 licence change](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/)) | Photoreal by design (the wrong band); sources disagree on use outside Unreal |
| Other Fab and Sketchfab single "office" NPCs | Single fixed characters, mostly low-poly game NPCs |

## 4. Comparison of the main routes

| | CC5 + ActorMIXER | Reom style kit (artist) | Lab3 Fab packs | Mikassa |
|---|---|---|---|---|
| Up-front cost | ~$300–650 software + ~$100–300 content | ~$8k–25k | ~$50–200 | $0–34.50 |
| Reusable system | **Yes** (identities, ages, sexes, wardrobe) | **Yes** (our own) | No (pack) | No (one character) |
| Our exact look | Uncertain (art direction) | **Yes** | Unlikely | Their look |
| Licence for monetised video | Yes (Standard; confirm runtime clause) | Yes (assigned) | Yes (Fab Standard) | Yes (CC-BY) |
| Blender → GLB | FBX → our converter | Native (P6 pipeline) | FBX → converter | CloudRig profile |
| Practical blocker | Windows-only authoring | Budget, artist choice | Few identities | Single character |
| Time to first test | Days (trial) | 6–12 weeks | Days | Days |

## 5. Recommendation (your decision)
1. **First, at no cost:** look at the preview links in §2, or let me add the vendor hosts so I can compare previews
   against our sheets.
2. **If you have a Windows PC:** run a **Character Creator 5 trial look test** (30 days, evaluation only): one man and
   one woman, 35–45, business wear, pushed toward our band with the HD Caricature MIXER and a toon base.
   - Export them, and I convert them and produce the same static sheets and bank still as P6.
   - **Decide on CC5 only if that test meets the standard.** It would then cost about $300–650 plus content.
3. **If the CC5 look test fails, or there is no Windows machine:** commission the **Reom style kit**. Our pipeline and
   rig data are ready for it.
4. Keep **Mikassa** as a quality reference (check the free-download claim first), and the **Lab3 packs** only as a
   cheap integration test or background characters.

**No existing system was verified to meet the premium stylised standard out of the box.** CC5 is the only one that
plausibly can, and that needs a look test.

Stopping here at the decision gate.
