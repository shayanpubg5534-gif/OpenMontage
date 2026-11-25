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

## Motion test (24.7 s, approved style frames in motion)

Source: `epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/`. It has three parts:

- `make_motiontest.py` builds the composition.
- `sfx_motiontest.py` makes the original synthesised effects.
- `scene_plan.json` is the shot plan; it passes the validator.

The builder captures each style frame's own `page()` call, so the stills and the motion can never
drift apart. Render with `epoch-ledger/scripts/render.py render projects/ai-bubble-vs-dot-com/motiontest -o ...`.

The narration is the episode's own lines, unedited: c03_03–c03_05 (contiguous), then c03_10.
Captions are in the approved pilot style.

| Shot | Time | Narration-locked actions |
|---|---|---|
| Establishing | 0–5.4 s | The market-board line climbs on "rising". Gold glints flow through the capital pipe into BigCart. The furnace chimney smoke and gold embers thicken on "struggling". The founder walks to BigCart's door. Commuters walk, talk and blink. A three-layer parallax dolly moves the sky, set and foreground at different rates. A label states that the companies are fictional. |
| Medium | 5.4–19.15 s | The whiteboard diagram builds on its words: ADS on "advertising", STAFF on "employees", SERVERS on "infrastructure"; REVENUE on "revenue", circled on "sustain"; the level line on "depended"; INVESTOR CASH fills the gap on "investors". The manager (the founder) points at each part, turns to the team and nods on "capital". One staffer puts his hand to his forehead on "without earning enough"; another shakes his head. Typing, a phone call, and a carton of BigCart merchandise carried past on "advertising" keep the room alive. |
| Close-up | 19.15–24.7 s | Brows knit on "without". The eyelids grow heavy on "no longer". The phone comes down on "finance". The cash line hits bottom and the runway counts from 3 to 0 months. The office lights behind him go out one by one on "operations". The CRT flicker drives the red key light. |

**Render performance:**
- First render: 741 frames at 1080p30 ("looks" quality), split into two chunks rendered with `--jobs 2` on 4 vCPU.
- Wall time was 9 min 35 s, about 23× real time. The revision render took 10 min 26 s, about 25× real time.
- The textured street and office sets cost about 1.1 s per frame. The close-up costs about 0.5 s per frame.
- Rough extrapolation for the 18.3-minute film at this density: 6–8 hours. Scene caching means
  only changed scenes re-render.
- Ways to cut the cost: render static set layers once to PNG per shot, keep camera moves as
  transforms over cached plates, and draft at 540p.

## Office sequence v2: narration-driven choreography (redesign after the rejected motion test)

The user rejected the first motion test because it was mostly static illustrations with small movements: one
whiteboard composition held for about 14 s while the narration covered five concepts. The redesign gives each
beat its own visible action:

1. The founder spins the cash tank's valve on "spending".
2. A match cut follows the coins into a TV, which plays the ad, on "advertising".
3. The payroll pipe drops coins that turn into pay envelopes on staff desks while they type and a new hire walks in, on "employees".
4. A technician slides a server into a rack, which lights up, on "infrastructure".
5. A pull-out to the whole money machine shows three outflows against a trickle of revenue, the tank falling, and MONEY OUT / money in kinetic type, on "without earning enough revenue".
6. The gauge falls into the red and the alarm starts, on "sustain".
7. In the Summit boardroom, the investors deliberate.
8. A stamp slams FUNDED in an insert, on "investors".
9. The capital valve opens, on "continuing".
10. The investor pipe pours in and the tank refills, on "capital".

Source: `epoch-ledger/episodes/ai-bubble-vs-dot-com/motiontest/office_v2.py`, with `sfx_office_v2.py` for sound
and `office_v2_plan.json` for the shot plan.

**Reusable capabilities added after the audit:**
- `kit/finmech.py` and `kit/finmotion.js`: financial mechanisms and the motion of props and objects.
- `R3.keys` with `rig3.reach`, `hold` and `hand_point`: action sequences with anticipation, contact and follow-through, and props held in hands.
- `kit/plates.py` and `kit/camera3d.py`: cached backgrounds with live foreground layers on a shared camera.
- `FM.stampIn`, `FM.powerOn` and `FM.pop`: object transformations and reveals.
- The scene-plan `MAX_HOLD` rule, plus the motion-craft §8c rules for narration-triggered choreography and the mute test.

**Gaps that remain:**
- True shape morphing (flubber-style path interpolation) is not implemented. Transformations use swaps, pops and masks.
- Cloth and secondary motion on characters is limited to joint keys.
- There is no lip-sync.

**Performance:** 420 frames at 1080p30 rendered in 143 s, about 0.34 s per frame. That is about 3× faster per frame than
the first motion test's textured shots (about 1.1 s per frame), because the sets are cached plates.

## Office sequence v3: meaning-first standard (current reference)

v2 was rejected for frantic pacing, a coin tank that read as cheese, repetitive pipes and valves, and an
investor agreement that looked the same as money arriving. v3 restructures c03_04–05 into three connected beats
across four compositions:

1. **Spending** (one office shot, 4.6 s). Bills fly from BigCart's cash pile to a TV commercial, to staff pay
   envelopes, and to a server rack being wheeled in. The counter falls from $13M to $9M.
2. **Shortfall** (charts, 4 s). Money out ($4M) against money in ($1M) gives a $3M monthly shortfall, and the
   cash line runs out in about three months.
3. **Agreement** (boardroom, 2.45 s). The term sheet is signed, then a handshake ("1 Agreement signed").
4. **Money received** (2.9 s). A $20M wire arrives, the cash pile and counter go from $4M to $24M, and the same
   chart jumps, then falls toward "next round needed" ("2 Money received").

**System-level changes:**
- `kit/finstate.py`: a Ledger that is the single source of truth for every figure.
- `kit/money.py`: banknotes and bundles, cash piles, wire slip, term sheet, and a real commercial.
- `kit/explain.py`: cash-flow bars and a runway chart.
- `FM.bills`, `FM.pileTo` and `FM.count`.
- Rig: eye direction (`R3.look`), signing (`R3.write`), and the `stand2` and `hips` stances.
- `kit/scene_plan.py`:
  - `meaning` (what, why, consequence) is required for every timed shot;
  - `MIN_SHOT` of 2 s, with inserts allowed at 0.5 s when they carry an `insert_reason`;
  - `MAX_CUTS_PER_10S` of 4;
  - the rejected v1 and v2 plans are kept as negative tests.
- Motion-craft §8c is rewritten as "meaning-first visual storytelling", and the QUALITY checklist is updated.

**Performance:** 420 frames at 1080p30 rendered in 124 s, about 0.30 s per frame, with cached plates.
