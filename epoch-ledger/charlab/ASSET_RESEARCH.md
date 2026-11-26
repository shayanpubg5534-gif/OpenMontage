# Character asset foundations: research for the artistic-direction gate (after M5)

Status: in progress. No assets purchased, no paid APIs. Licences are as stated by the publishers; each one must be
re-checked on the download page before any use.

Target (producer, M5 review): premium, full-colour, stylized animated financial documentary for adults. Not
photorealism, not childish cartoons, not low-poly game characters, not game cutscenes. Intentional design, believable
anatomy (head, neck, jaw and shoulders integrated), expressive faces (eyes, brows, cheeks, jaw), distinctive hair,
natural clothing, refined materials, cinematic light; environments in the same language.

## Candidates

| Foundation | Licence | What it is | Fit | Access from this environment |
|---|---|---|---|---|
| **Blender Studio character library** (Snow, Rain, Storm; Sprite Fright's Ellie, Victoria, Phil and others) | CC-BY, credit "(CC) Blender Foundation \| studio.blender.org" | Professionally designed, sculpted and rigged film characters with designed hair, clothes, facial rigs and shading. Snow is a stylized adult woman built for the "Stylized Character Workflow" course (Blender 4.1). Sprite Fright rigs need Blender 3.x and CloudRig | **Best artistic match found.** Real character design, not a generic base. Each is a single fixed character (no generator); our own characters would be re-designs from them by an artist, or the characters used as-is with attribution | **Blocked**: the host was added to the environment's allowed list, but fetching it was refused by this session's permission check. Whether downloads need a (free) login is not confirmed |
| **Blender Human Base Meshes v1.4.1** (already evaluated in M5) | CC0 | Sculpt bases incl. stylized heads and bodies | Good anatomy and neck/shoulder flow; no hair, clothes, expressions or rig. A starting point for an artist, not a character | Available (download.blender.org) |
| **CharMorph** (Blender add-on, GPLv3) with Antonia (CC-BY), Vitruvian (CC0), Reom (CC-BY), MB-Lab base (AGPL) | Per base model | Character generator descended from MB-Lab: morphs, Rigify incl. facial rig, hair, fitted clothing | Automatable, rigged, expressive face rig. Bases are realistic in proportion and surface, so stylization would be ours to add. Better anatomy and face rig than MakeHuman, same "generator" look risk | Needs GitHub read access to the `Upliner/CharMorph*` repositories (not enabled for this session) |
| **MakeHuman / MPFB** (current) | CC0 assets | What M2–M5 used | Rejected at M5 review as an artistic standard | — |
| Ara 3D Gen | MIT code, CC0 data (MakeHuman) | Browser generator | Same MakeHuman data, realistic | — |
| Quaternius Universal Base Characters, KayKit | CC0 | Game characters with hair and outfits | Low-poly game style: explicitly excluded by the brief | Available |
| Mixamo | Adobe terms (not open) | Rigged characters and motions | Game style; needs an Adobe login; not open-licensed | Not used |
| AI image-to-3D (TRELLIS, Hunyuan3D, TripoSR) | Mixed (Hunyuan3D excludes EU/UK/KR) | Generated meshes | Needs a GPU; topology unsuited to rigging and facial animation | No GPU here |

## Can an "artist pass" happen inside this automated environment?

Partly. Code can: assemble, retarget, rig-transfer, re-shade, light and render existing professionally made characters;
procedurally adjust them; and build environments, props and graphics. Code cannot do what an artist does when
designing a new character: sculpting a likeable, specific face, designing a hairstyle and modelling hair cards,
tailoring clothes with folds, painting textures. Within this environment the realistic options are:
1. use professionally designed CC-BY characters (Blender Studio) and adapt them (recolour, re-dress from their own
   wardrobe, re-light, our rig and motion stack), with attribution; or
2. commission or recruit a human 3D character artist for original hero characters, using the CC0 base meshes as a
   start, delivered into our existing rig and pipeline; or
3. change the medium for characters: premium 2D illustrated characters (designed in vector by code, as Rig v4 is),
   where design quality is achievable by code, in 3D or 2.5D environments.

## Sources
- Blender Studio Rain rig: https://studio.blender.org/characters/rain/v1/
- Blender Studio Snow: https://studio.blender.org/characters/snow/ and https://studio.blender.org/blog/introducing-snow/
- Blender Studio Ellie (Sprite Fright): https://studio.blender.org/characters/ellie/
- Blender Studio character library announcement: https://studio.blender.org/blog/new-the-character-library
- CharMorph 0.4 (CG Channel): https://www.cgchannel.com/2025/03/check-out-new-open-source-3d-character-generator-charmorph/
- CharMorph docs: https://charmorph-docs.readthedocs.io/en/main/
- Quaternius Universal Base Characters: https://quaternius.com/packs/universalbasecharacters.html
- Blender Human Base Meshes: https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes
