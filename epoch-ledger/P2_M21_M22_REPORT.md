# P2 report: M2.1 (toolchain compatibility) and M2.2 (generated gate settings)

Status: both milestones are complete. M2.3 (look development) waits for your approval and for the asset downloads in §5.
Date: 2026-11-25.

Scope:
- No production code path changed. The 18-minute documentary, Rig v1–v4, approved assets and caches are untouched.
- Nothing was rendered except a 2-second, 60-frame test clip of the test body (§2.6).
- No rejected technology was installed.
- Everything installed is isolated in `.runtime/charlab/`, which git ignores:
  - `bpy` in its own virtual environments;
  - MPFB in an isolated Blender user directory;
  - three.js release packages;
  - test motion-capture files.

Evidence labels: **[M]** measured here, **[V]** read from source, licence text or registry, **[K]** prior knowledge
(the host is blocked here), **[U]** untested.

## 1. Recommended versions (each pinned after testing, not chosen for being newest)

| Component | Recommended | Also tested | Why |
|---|---|---|---|
| Blender Python | **`bpy` 5.3.0** (Python 3.13, the system version) | **`bpy` 4.5.17 LTS** (Python 3.11 via uv): identical output, kept as a verified fallback | Both build the same character and GLB **[M]**. 5.3 builds in 2.8 s against 7.1 s for 4.5, and exits cleanly. 4.5 hangs on interpreter shutdown when run as a module; the script now exits explicitly **[M]**. 4.5 is the long-term-support line **[K]**, which is why it stays tested. |
| MPFB | **2.0.18** (release tag `v2.0.18`, 2026-10-04) | `master` (2026-11-22) not used | Latest release. Needs Blender ≥ 4.2 **[V]**. MPFB's own headless test suite: **1,100 pass, 16 fail, 18 skipped**, identical on Blender 5.3 and 4.5 LTS. Of the 16 failures, 12 need the MakeHuman asset pack (not installable here) and 4 come from Rigify not registering inside Blender-as-a-module; we don't use Rigify **[M]**. |
| three.js (new character layer only) | **0.186.1** | 0.187.0, and the production 0.160.0 | All three give identical results on the test GLB **[M]**. 0.186.1 is a patch release, and the Three.js Skills target r186 **[V]**. 0.187.0 has no patch release yet. The existing r160 modules stay unchanged. |
| HyperFrames | **0.9.88** (unchanged) | – | It rendered an r187 ES-module character layer next to the page's r160 global **[M]** (§2.6). The latest is 0.9.94 **[V]**; any upgrade waits for a determinism test. |
| Rig | **MPFB `game_engine`** | MPFB `default` (163 bones: eyes, jaw, tongue, face) and `cmu_mb` (31 bones, no real fingers) | 53 bones, with five fingers of three joints per hand (30 finger bones). It uses Unreal-mannequin bone names, the common target for motion libraries **[M]**. It has no eye or jaw bones, so faces use shape keys (§2.3). |
| Motion | **CMU** now; Quaternius UAL and Mixamo when downloaded | – | Licences in §4. |

## 2. Compatibility results [M]

### 2.1 Headless CPU character generation
- MPFB 2.0.18 loads in `bpy` 5.3.0 and 4.5.17 with no display and no GPU, from an isolated Blender user directory.
- **The whole chain takes 2.8 s on 5.3 (7.1 s on 4.5):** human from sliders, identity baked, rig fitted, 12 expression shape keys, helper geometry removed, two motion-capture clips retargeted, finger-grip action, GLB export.
- **Output:** 13,380 vertices, 53 bones, 30 finger bones, 3 animations (walk 2.83 s, sit 6.0 s, grip), 1.2 MB GLB.
- **MPFB test suite:** the same 1,100 passed and the same 16 failed (the same tests) on 5.3 and on 4.5 LTS.

### 2.2 Rigging and GLB export
- The rig fits to MPFB's joint helpers, so it must be added before the helpers are removed. The script does this.
- Helpers are removed with `bmesh` while shape keys are preserved.
- The skin weights come from MPFB's own weight files.
- The GLB loads in three.js 0.160.0, 0.186.1 and 0.187.0 with no errors.

### 2.3 Faces
- **12 expression units ship with MPFB's core, and all of them work as shape keys in three.js:** eye closure, eyes wide, inner brows up, brows down, mouth corner pull, mouth depression, mouth open, mouth compression. Blink, smile and brows visibly change the face.
- **Visemes and ARKit face units** need MakeHuman's `faceunits01` pack (§5). Narrators speak off screen, so these matter only for characters who speak on camera.

### 2.4 Animation
- **Retargeting CMU motion capture → `game_engine` works for walking and sitting.**
  - Rest poses are matched by bone direction.
  - Rotations transfer as deltas from the matched pose.
  - Root motion is scaled by leg length.
  - Results: 22 bones per clip; the walk travels 2.93 m, plausible and grounded in side view (`projects/charlab_m21/motion.png`).
- **Determinism:** seeking to the same time from different histories gives identical pixels, in every three.js version tested.
- **Problems found and fixed during the test:**
  - the pelvis double-counted the hip height, so the character floated;
  - the imported source clip was exported as an extra animation;
  - the cgspeed CMU conversions start with a setup pose frame;
  - Blender 4.5 needs `use_nodes` to create a material node tree, while 5.x deprecates it.
- **Remaining motion limits (measured):**
  - **Foot sliding.** While planted, the left toe drifts 3.1 mm per frame on average (worst 8 mm). The right toe averages 9.8 mm per frame, with spikes up to 126 mm. Foot-locking IK is needed (M3.1).
  - **CMU has no finger data**, so fingers come from our own poses. The grip test curls all 30 finger bones, but the thumb axis is crude, and tuned grips are M3.2.
  - **Sitting has no seat yet.** The character sits in mid-air until seat contact is added (M3.1).

### 2.5 Prop attachment
- A prop parented to `hand_r` drifts **0 m** from its socket across every frame of the walk.
- Visible grip quality (fingers wrapped around the object, its orientation, intersections) is **not proven yet**; that is M3.2.

### 2.6 Rendering
- **Speed:** headless Chromium on SwiftShader (CPU), 1920×1080 with toon bands and ink outlines, one bare character with no set: **150–166 ms per frame** including PNG readback.
- **This is not an episode-speed claim.** Real scenes with sets, several characters and post-processing must be measured in M4.2 before any 2–3-documentaries-a-week figure.
- **HyperFrames:**
  - **What ran:** a 2-second test composition built with `kit/assemble.py`. It loads the GLB asynchronously in an r187 module, while the page also loads the existing r160 global.
  - **Result:** HyperFrames 0.9.88 rendered all 60 frames with the character present from frame 0.
  - **What still needs proof:** that was one run with one worker. Before production, the layer needs an explicit readiness guarantee that holds with `--isolate` and parallel jobs **[U]**.

## 3. M2.2: quality-gate settings generated from the build [M]

**What changed:**
- **`kit/gates.py` (new).** The code that draws a figure declares it once, and the gate settings are written from those declarations:
  - **`G.value(metric)`** reads the number from the financial model, so the on-screen figure and the checked claim cannot diverge.
  - **`G.fig(id, text, cue, shows=…)`** tags the element and registers it for the figure check and the finance check. Its cue is checked against the narration word timings at build time, so a manifest can never name a word that isn't spoken.
  - **`G.chart` / `G.mark`** register charts and the value of every mark.
  - **`G.write(ws, scenes=…)`** writes `WS/gates/gates.json` with the figures, finance claims and cuts, and `"contacts": "auto"`.
- **`contact_check.mjs --auto`.** No contacts file is needed: it reads every `R4.hold` (and anything pushed to `window.__gates.contacts`) from the built composition, so the hold that animates a prop is the hold that is checked. Tested on real Rig v4 builds:
  - **BigCart final preview:** 2 holds found. The wire held in the founder's left hand is reported **132 px from that hand at 12.57 s**. This is an existing approved preview; it is reported, not changed.
  - **Rig v4 proof:** 1 hold found.
- **`quality_gates.py`** understands generated settings and adds a contact sheet at the start of every discovered hold.
- **`templates/episode/build.py`** now creates `Gates` and writes the settings on every build. Checked with a throwaway episode.

**Tests:** `tests/epoch_ledger/test_gate_manifests.py`, 3 tests.
- Build-time validation: an unknown cue, a duplicate id, or a chart without marks fails the build.
- A generated episode passes the finance, figure, layout and contact gates end to end. The contact was discovered in the page.
- The same build with a wrong figure and an interest-free loan fails the finance gate.

**Not migrated:** *Profitable and Broke* keeps its hand-written fixtures. Its props use an episode-local bridge (`BR`), not `R4.hold`, and the episode is a frozen reference.

## 4. Licensing of every external component and asset

| Item | Licence | Commercial video use | Conditions | Evidence |
|---|---|---|---|---|
| `bpy` 5.3.0 / 4.5.17 | GPL-3.0 | Yes. A tool; its output is ours | – | **[V]** PyPI |
| MPFB 2.0.18 code | GPL-3.0 | Yes. A tool | – | **[V]** `LICENSE.md`, `blender_manifest.toml` |
| MPFB bundled assets (base mesh, targets, rigs, weights, poses, expressions, textures) | **CC0 1.0** | Yes | None | **[V]** `LICENSE.md` §C, `LICENSE.ASSETS.md` |
| MakeHuman system assets (eyes, brows, lashes, teeth, hair, clothes, skins) | CC0 **[K]** | Yes **[K]** | Check the licence file inside the pack before use | Host blocked |
| MakeHuman community packs | Per asset (CC0 or CC-BY) **[K]** | Varies | One entry per asset in a licence ledger | Host blocked |
| CMU motion capture (cgspeed BVH via the una-dinosauria mirror) | Free for any use | Yes | Attribution courtesy (already in `ink-theater/THIRD_PARTY_NOTICES.md`) | **[V]** mirror README |
| Quaternius Universal Animation Library | **Quaternius Asset License v1.0** (updated 2026-08-28), even though the pack page still says CC0; the licence in force when you download is the one that applies | **Yes** (films and videos are named), no credit required | **No redistribution of the assets themselves, original or modified** | **[V]** quaternius.com/license.html |
| Mixamo | Adobe terms | Yes **[K]** | Adobe ID; no redistribution of the raw files **[K]** | Host blocked |
| three.js | MIT | Yes | – | **[V]** |
| HyperFrames | Apache-2.0 | Yes | – | **[V]** |

**The repository is public [V].** So these stay out of git, in `.runtime/`, rebuilt by scripts:
- Quaternius and Mixamo files, and any GLB containing their animation;
- MakeHuman asset packs, which are large.

## 5. Downloads I need from you (these hosts are blocked here)

| # | What | Official page | Version / file | Needed for |
|---|---|---|---|---|
| 1 | **MakeHuman system assets** | https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html (the link MPFB 2.0.18 itself uses, `ui/weburls.py`) | The current system-assets ZIP on that page. MPFB records it as `makehuman_system_assets.json` once installed. The exact file name could not be read here | **Required for M2.3:** eyes, eyebrows, eyelashes, teeth, hair, clothes, skin materials |
| 2 | **Face units pack** | http://static.makehumancommunity.org/assets/assetpacks.html (`URL_ASSET_PACKS` in MPFB) | `faceunits01` | Optional: visemes and ARKit expressions for characters who speak on camera |
| 3 | **Quaternius Universal Animation Library** | https://quaternius.itch.io/universal-animation-library (linked from quaternius.com) | The free "Standard" version, in GLB or FBX | M3.1: about 120 clips, including multi-direction locomotion (uses the same Unreal-mannequin naming as our rig) |
| 4 | Mixamo (optional) | https://www.mixamo.com | Per-clip FBX, "Without Skin", 30 fps | Decide after M3.1 |

**How to deliver them:**
- **Upload:** upload the ZIPs to this session. I will place them in `.runtime/charlab/assets/` (git-ignored) and record their licences.
- **Or allow these hosts in the environment:**
  - `static.makehumancommunity.org` and `files.makehumancommunity.org`;
  - `quaternius.itch.io` plus itch's download host.

  The itch download host is shown only at download time and could not be determined here, so uploading is the reliable route.

## 6. Limitations (actual, not estimated)

1. **No style judgement is possible yet.** Without the system assets the body has no eyes, brows, hair, clothing or skin texture. The test images show compatibility, not the look.
2. **MPFB's realistic skin is a procedural Blender shader**, which glTF cannot carry. The illustrated look will come from our own three.js toon and painterly shading plus painted textures. That is M2.3 work, and the main quality risk.
3. **The `game_engine` rig has no eye or jaw bones.** Eye direction will need eye meshes with their own rotation, or the 163-bone `default` rig, which was not retarget-tested.
4. **Foot sliding, thumb axis, seat contact and the first-frame setup pose** are known motion issues (§2.4).
5. **The HyperFrames readiness for asynchronous layers** is unproven with parallel or isolated rendering.
6. **Performance is measured on one bare character only.**
7. **The Blender 4.5 module hangs on exit**, worked around. Rigify does not register in the module build, and we don't need it.

## 7. Recommended next step (needs your approval)

**M2.3 look development for one character, stills only**, after the system assets arrive (§5 #1):
- toon, painterly or both shading tests;
- skin, hair and clothing treatment;
- wide, medium, close-up and side-profile stills, plus a turnaround, side by side with a current Rig v4 frame.

In the same step, add the HyperFrames readiness guard for the character layer and test it with `--isolate`.

Estimate **[E]**:
- **Human developer:** 4–6 days.
- **Claude:** about 4–8 h of working time; medium to large usage.

No motion-library work starts until you approve the look.
