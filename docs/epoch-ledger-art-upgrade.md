# The Epoch Ledger: art direction v2 (production upgrade and style frames)

Status: the reusable upgrades are complete and the three style frames are ready for approval.
**No video preview has been rendered, and the documentary has not been regenerated.** Both wait
for approval of these frames.

## Style frames (1920×1080)

Stills are saved in `epoch-ledger/episodes/ai-bubble-vs-dot-com/styleframes/out/`. Each one is
rebuilt by its `sf*.py` script plus `scripts/still.mjs`. The plan for each frame is in
`styleframes/scene_plan.json`, and it passes the validator.

| Frame | Beat | What it shows | Techniques |
|---|---|---|---|
| `sf1_establishing` | 3:30 "Investors poured billions..." | Dusk street in two-point perspective. Summit Ventures' capital pipe runs into BigCart's brick building, which has a rooftop billboard. The TECH STOCKS board rises at the end of the street, with commuters in front. | scene3d facades and extrusions, CC0 brick, concrete and asphalt, dusk sky, haze, lamp light, rig v3 pedestrians |
| `sf2_medium` | 3:37 "...advertising, employees and infrastructure..." | Office medium shot. The manager points at an easel whiteboard (ADS / STAFF / SERVERS against a small REVENUE bar, "GAP = INVESTOR CASH"). Staff react; the room has CRTs, a hiring banner, the Super Bowl poster and windows onto the dusk city. | scene3d interior (CC0 oak floor and plaster), window beams, rig v3 IK poses, diegetic whiteboard |
| `sf3_closeup` | 4:02 "...the money ran out..." | Close-up of the founder at night with the phone at his ear, lit red by the CRT. The screen shows the cash balance falling and "RUNWAY LEFT 3 MONTHS". The term sheet and a calculator showing −4.2M sit on the desk, with the office and city out of focus behind. | `closeup_svg`, diegetic CRT chart, blurred scene3d background, bokeh, grade |

The chart values are illustrative shapes for the narration, not sourced figures. In motion they
will be labelled as illustrative where shown, as `QUALITY.md` requires.

## Reusable upgrades (all listed in `epoch-ledger/COMPONENTS.md`)

- **Perspective and environments**, in `kit/scene3d.js`:
  - a real camera with lens shift and near-plane clipping;
  - builders for boxes, polygons, cylinders, tubes, extrusions, wheels, ground tiling and facades;
  - SVG art mapped onto any quad;
  - depth-sorted character sprites.
- **Light, shadow, texture and atmosphere**:
  - `scene3d` provides Lambert sun light, hemisphere fill, point lamps, distance fog, soft cast
    shadows, emissive windows and screens, and CC0 textures (`texMix` calms busy ones);
  - `kit/lightfx.py` adds skies, haze, light shafts, bloom, depth of field, and a grade with grain.
- **Characters**, in `kit/rig3.py`:
  - 7.5-head proportions in three-quarter view;
  - detailed eyes, brows, mouths and expressions; hands (relaxed, grip, point, open, phone, fist);
  - six costumes;
  - two-bone IK, so hands land on keyboards, phones and boards;
  - `closeup_svg`, a modelled close-up head with tired lids, stubble, key and rim light and a hand.
- **Integrated financial graphics**, in `kit/diegetic.py`: whiteboard chart, CRT chart, market
  board, gauge and press clipping. All are data drawn on objects.
- **Shot design process**:
  - `kit/scene_plan.py` enforces a written plan per shot: shot size, focal point, camera,
    lighting, technique, components, graphics and the guides consulted.
  - The validator rejects plans that skip the motion-craft guide, `COMPONENTS.md` or
    `QUALITY.md`, overlays without a written reason, and more than three same-size shots in a row.
  - The process is wired into `QUALITY.md`, the skill guides, `/epoch-ledger` and `AGENT_GUIDE.md`.
- **Assets**:
  - six CC0 Poly Haven textures, each recorded individually in `kit/assets/LICENSES.md`;
  - a test keeps the register, the manifest and the files in step;
  - ambientCG, Kenney, Quaternius and Wikimedia are approved and allowlisted but unused so far.
    Low-poly model packs were avoided on purpose, because they push towards a simulation-game look.

## How the guides shaped these frames

Before design, I read the motion-craft guide, `COMPONENTS.md` and `QUALITY.md`; this is recorded
per shot in `scene_plan.json`. Applied:

- three shot sizes (establishing, medium, close-up);
- data on objects instead of floating panels;
- one motivated key light per shot;
- depth through fog, blur and foreground layers;
- cause before consequence: money in, spending, then running out.

## Tests

`tests/epoch_ledger/test_art_upgrade.py` (19 tests) covers:

- IK accuracy;
- every pose rendering with its rig parts, deterministically;
- the close-up's animatable ids;
- the diegetic builders and lightfx layers;
- scene-plan validation, including rejection cases;
- the licence register;
- scene3d projection, clipping and determinism in Chromium;
- the component-index entries.

The full Epoch Ledger suite has 51 tests, all passing.

## Known limits

- scene3d draws flat-shaded faces with painter's sorting. Interpenetrating geometry needs a `bias`
  or splitting, and curved surfaces are faceted, which is acceptable in the inked style.
- Hero camera moves in scene3d re-render the SVG every frame. Cost will be measured per shot
  before the motion pass; 2.5D layered moves are the cheaper fallback.
- The close-up rig is drawn three-quarter facing right; flip it to face left. A frontal
  close-up is a future addition.
- Local AI image generation and Manim are deferred, as agreed.
