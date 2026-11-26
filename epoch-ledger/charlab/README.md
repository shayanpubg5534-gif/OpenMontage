# Character lab (P2 · M2.1)

An isolated test bench for the proposed 3D character layer. It is **not** part of the production kit, and it changes
no approved asset. The 18-minute documentary, Rig v1–v4 and every existing composition are untouched.

| File | What it does |
|---|---|
| `build_character.py` | Builds a character headlessly on the CPU, run with the isolated Blender Python. Steps: spec → MPFB human → rig (default `game_engine`: 53 bones, 30 finger bones) → expression shape keys → CMU retarget → finger-grip action → GLB. Writes a timing and contents report. |
| `specs/*.json` | Character specs: MPFB macro sliders, optional named shape targets, rig and skin colour. `test_adult.json` is a neutral test body, not a cast member. |
| `viewer/index.html` | Loads a GLB in a chosen three.js release with toon shading and ink outlines. Exposes `renderAt(clip, t, framing, morphs)` and `measure(clip, t)`. |
| `build_dressed.py` | M2.3: a fully dressed character from an MPFB preset spec (`specs/elias.json`). It adds eyes, brows, lashes, teeth, hair, clothes and skin, then the rig, expression keys carried onto the brows, lashes and teeth, real (deleted) clothing masks, a standing pose and finger poses, and exports a GLB. Also checks eye alignment. |
| `inspect_character.py` | M2.3: geometric checks of an exported GLB: clothing and scalp poke-through (rays along the skin normal), the hair-to-scalp gap, and eye symmetry and spacing. |
| `viewer/lookdev.html`, `lookdev.mjs` | M2.3: look-development viewer and still renderer. Two treatments, `toon` and `paint`, with hue-shifted banded shading, interior ink lines, silhouette ink, a shadow catcher over an Epoch Ledger plate and shared paper grain; plus diagnostic modes. |
| `evidence_sheets.py` | Assembles stills into labelled evidence sheets (`evidence/`). |
| `install_assets.py` | Reproducible install of the MakeHuman system assets: SHA-256 and size check, licence check (all CC0), safe extraction, receipt. |
| `check_glb.mjs` | Drives the viewer in headless Chromium (CPU WebGL). It checks the GLB loads, then measures: bones, shape keys, clips, determinism, ms per frame, prop-socket drift, foot sliding and root travel. Writes evidence frames. |

## Environment (everything lives in `.runtime/charlab/`, which git ignores)

```
uv venv --python /usr/local/bin/python3 .runtime/charlab/venv && uv pip install --python .runtime/charlab/venv/bin/python bpy==5.3.0
# fallback, also verified: Python 3.11 + bpy 4.5.17 LTS in .runtime/charlab/venv45
git clone https://github.com/makehumancommunity/mpfb2 .runtime/charlab/mpfb2 && git -C .runtime/charlab/mpfb2 checkout v2.0.18
mkdir -p .runtime/charlab/user/extensions/user_default && ln -s $PWD/.runtime/charlab/mpfb2/src/mpfb .runtime/charlab/user/extensions/user_default/mpfb
(cd .runtime/charlab/three && mkdir r0.186.1 && cd r0.186.1 && npm pack three@0.186.1 && tar xzf three-0.186.1.tgz)
curl -O https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/002/02_01.bvh   # into .runtime/charlab/mocap

BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_character.py \
    epoch-ledger/charlab/specs/test_adult.json .runtime/charlab/out --bvh walk=.runtime/charlab/mocap/02_01.bvh
node epoch-ledger/charlab/check_glb.mjs --three .runtime/charlab/three/r0.186.1 --glb .runtime/charlab/out/test_adult.glb --out .runtime/charlab/check
```

## Asset rules (the repository is public)

**Never commit to git:**
- third-party asset files (MakeHuman asset packs, Quaternius, Mixamo);
- GLBs built from Quaternius or Mixamo assets.

The licences allow them inside finished videos, but not redistribution of the assets themselves. Keep them in
`.runtime/` and rebuild them from scripts. CMU motion capture and MPFB's bundled CC0 assets are free of that
restriction, but generated characters still stay out of git, to keep the repository small.

Results and the recommended versions: `epoch-ledger/P2_M21_M22_REPORT.md`.

## Reproducing the setup in a new session

1. **Isolated Blender Python and MPFB:** follow "Environment" above (`bpy` 5.3.0 in `.runtime/charlab/venv`, MPFB at tag `v2.0.18`).
2. **MakeHuman system assets.** Get `makehuman_system_assets_cc0.zip` (280,737,770 bytes, SHA-256
   `b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107`) from the official page,
   https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html. Its mirrors are blocked in this
   cloud environment, so either:
   - allow `files2.makehumancommunity.org` (or `files.makehumancommunity.org`) in the environment's network settings and download it; or
   - upload the ZIP, or an RAR split of it, to the session.

   Then run:
   ```
   python3 epoch-ledger/charlab/install_assets.py PATH/makehuman_system_assets_cc0.zip    # or …part01.rar (needs: apt-get install unar)
   ```
   The script refuses any file whose size or checksum differs, or any asset that isn't CC0. It extracts into the lab's MPFB
   user data and writes `receipt_makehuman_system_assets.json`. `7zip` from Ubuntu cannot unpack RAR (no RAR codec); use `unar`.
3. **three.js for the character layer:** build the pinned single-file bundle, with no import map, so `render.py --isolate`
   and the render cache see every file:
   ```
   mkdir -p .runtime/charlab/bundle/node_modules && ln -s $PWD/.runtime/charlab/three/r0.186.1/package .runtime/charlab/bundle/node_modules/three
   cp epoch-ledger/charlab/three_bundle_entry.js .runtime/charlab/bundle/entry.js
   (cd .runtime/charlab/bundle && npx --yes esbuild@0.25.0 entry.js --bundle --format=esm --minify --outfile=three186-char.js)
   ```
4. **Build and inspect the character, then render the stills:**
   ```
   BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
       epoch-ledger/charlab/specs/elias.json .runtime/charlab/out_m23 --bvh walk=.runtime/charlab/mocap/02_01.bvh
   BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/inspect_character.py \
       .runtime/charlab/out_m23/elias.glb .runtime/charlab/out_m23/inspect.json
   node epoch-ledger/charlab/lookdev.mjs --three .runtime/charlab/three/r0.186.1 --glb .runtime/charlab/out_m23/elias.glb \
       --plate projects/profitable-and-broke/hyperframes/plates/shop-bg-6302a081a386.png --shots SHOTS.json --out DIR
   ```

## Installed asset packs (licence ledger)

| Pack | File / SHA-256 | Source | Licence | Installed to |
|---|---|---|---|---|
| MakeHuman system assets | `makehuman_system_assets_cc0.zip`, 280,737,770 bytes, `b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107` | Official MakeHuman asset-pack page (`static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html`). Downloaded by the user and transferred as an 11-volume RAR5 set; extracted with `unar`. | **CC0** for all 94 assets: hair 10, eyebrows 12, eyelashes 4, eyes 11, teeth 6, tongue 1, skins 23, clothes 20, proxy meshes 7. Read from `packs/makehuman_system_assets.json` and matched 94/94 against the official page | `.runtime/charlab/user/extensions/.user/user_default/mpfb/data/` (git-ignored). MPFB reports it as installed and current. |

## M2.3b — editorial art direction (two characters, three treatments)

| File | What it does |
|---|---|
| `specs/elias.json`, `specs/nadia.json` | Male and female characters. Opt-in M2.3b fields: `face_normals` (strength of the clean-face shading normals), `lod_ratio` (wide-shot LOD export), `recolour` (palette rules, e.g. the sports socks inside the shoe asset → dark tights). |
| `build_dressed.py` | Adds `face_normals`, `export_textures` (`<id>_tex/` + manifest) and `export_lod` (`<id>_lod.glb`) when the spec asks for them. |
| `prepare_textures.py` | Build-time treated textures. `.toon.png` drops photographic detail. `.flat.png` is a controlled palette: k-means per material family; skin is one soft even tone. |
| `viewer/lookdev2.html` | Treatments `toon2`, `editorial` and `hybrid`; set presets `bakery` and `bank` (light rig, shadow colour, ink colour, grade); several characters; switches for `msaa`, `shadow`, `ink` and `lod`. |
| `evidence_sheets2.py` | The M2.3b comparison sheets. |

```
for c in elias nadia; do
  BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
      epoch-ledger/charlab/specs/$c.json .runtime/charlab/out_m23b --bvh walk=.runtime/charlab/mocap/02_01.bvh
  python3 epoch-ledger/charlab/prepare_textures.py .runtime/charlab/out_m23b/${c}_tex --spec epoch-ledger/charlab/specs/$c.json
done
node epoch-ledger/charlab/lookdev.mjs --page lookdev2.html --three .runtime/charlab/three/r0.186.1 \
    --query 'env=bank&chars=elias:-.65:0:15,nadia:.7:.1:-20&out=/.runtime/charlab/out_m23b' --shots SHOTS.json --out DIR
```

## M2.3c — bespoke character geometry (procedural, headless)

| File | What it does |
|---|---|
| `stylise.py` | Run by `build_dressed.py` only when a spec has `"design"`. It adds:<br>• face planes (Taubin smoothing of the face skin as a shape key, then the proxies are refitted);<br>• original hair (a designed hairline, a volume map, flow-aligned clump grooves, lock tips, a solid edge, an optional colour zone, an optional ponytail with clearance and a tie);<br>• designed brows;<br>• lash lines on the eyelash helper geometry.<br>The generated meshes are skinned to the head and carry the body's expression keys. |
| `specs/elias_c.json`, `specs/nadia_c.json` | Designed face targets and `"design"` settings (angles in degrees around the head: az 0 = front, +90 = the character's left). |
| `prepare_textures.py` | With `design.eyes`: an illustrated eye texture (iris found automatically, enlarged, two tones with a limbal ring). |
| `viewer/lookdev3.html` | `lookdev2.html` plus the designed mesh types (`ghair`, `gline`). |
| `verify_design.py` | Skinning, expression, blink and brow-raise measurements for the designed meshes. |
| `evidence_sheets3.py` | M2.3b vs M2.3c sheets. |

Commands: see `epoch-ledger/P2_M23C_REPORT.md`, "Reproducibility".
