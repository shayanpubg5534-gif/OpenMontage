# Character lab (P2 · M2.1)

An isolated test bench for the proposed 3D character layer. It is **not** part of the production kit, and it changes
no approved asset. The 18-minute documentary, Rig v1–v4 and every existing composition are untouched.

| File | What it does |
|---|---|
| `build_character.py` | Builds a character headlessly on the CPU, run with the isolated Blender Python. Steps: spec → MPFB human → rig (default `game_engine`: 53 bones, 30 finger bones) → expression shape keys → CMU retarget → finger-grip action → GLB. Writes a timing and contents report. |
| `specs/*.json` | Character specs: MPFB macro sliders, optional named shape targets, rig and skin colour. `test_adult.json` is a neutral test body, not a cast member. |
| `viewer/index.html` | Loads a GLB in a chosen three.js release with toon shading and ink outlines. Exposes `renderAt(clip, t, framing, morphs)` and `measure(clip, t)`. |
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
