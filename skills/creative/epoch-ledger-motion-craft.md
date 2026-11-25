---
name: epoch-ledger-motion-craft
description: Motion-design craft for The Epoch Ledger — load when building or revising Epoch Ledger scenes (composition, timing, kinetic type, diagrams, data, isometric, maps, 3D performance, end screen). Companion to skills/creative/epoch-ledger.md and epoch-ledger/QUALITY.md; uses kit/motion.js, kit/motion.py, kit/three_kit.js.
---

# Epoch Ledger — motion craft

Read this when you write a scene brief or build or revise a scene. It turns general motion-design
practice into series rules and points to the kit functions that implement them. **Rules marked
"guideline" are defaults, not limits:** break them when the story is clearer for it, and say why
in the scene brief. `QUALITY.md` still governs, and the four requirements outrank everything here.

Credits: this guide was informed by a review of the MIT-licensed iart-ai motion-skills packs. All
wording and code here are original. Nothing was copied from packs without a licence (see
`docs/epoch-ledger-production-setup.md`).

## 1. Motion language (set once per episode)

Series defaults live in `config/production.json → motion_language` and in `MOTION` (kit/motion.js):

| Role | Easing | Typical duration |
|---|---|---|
| enter / appear | `expo.out` (fast start, gentle settle) | 0.45 s (`MOTION.dur.base`) |
| exit | `power3.in` | 0.25 s |
| move / reposition | `sine.inOut` | 0.8 s |
| settle (diagrams, iso builds) | `power3.out`; **no overshoot on financial content** | 0.45 s |
| camera | `sine.inOut`, slow and long | 1.6 s or more |
| data (bars, counters) | `power2.out` | 0.8–1.4 s |

Stagger rhythm: lines 80 ms, words 55 ms, characters 28 ms, list items 60 ms, grids 25 ms. A group
reveal usually settles within ~0.9 s (guideline; `mStaggerFor` compresses long groups). Write the
episode's choices in `art-direction.md`; deviate per scene when the brief says why.

## 2. Composition per shot

- **One focal point** at a time, usually on a third (33 % / 67 %); rank everything else below it
  by size, then contrast, then colour, then position.
- **Three motion layers:** *primary* (the action the eye follows, which explains the line),
  *secondary* (reactions: labels settling, shadows, people responding) and *ambient*
  (environmental life). **Keep ambient life**: drifting light, smoke, crowds, fans, water, parallax
  and atmospheric depth are part of the series look (`mAmbient`, `mParallax`, `ambient()` for rigs).
  Ambient motion stays low-contrast and never competes with the primary action.
- **Camera:** one intent per move (push, pull, pan, follow, crane). Combined moves are allowed when
  they read as one gesture (a craning push into a cutaway). Guideline: avoid stacking unrelated moves.
  Start the move ~1 s before the word that names the subject (`keyCam` / `mPush`).
- **Direction carries meaning:** new things enter from the right or from below; going back or
  dismissing exits left or down; drilling deeper is a push in; leaving a detail is a pull out to
  the model.
- **The "1/3" guideline:** long unbroken slides (more than about a third of the frame) read as
  "the template moved". Break them with an intermediate beat, a scale change or a camera move. With
  many elements, let roughly a third act at once while the rest hold or breathe. Both are judgement
  calls, not limits.
- **Anticipation and follow-through:** a small counter-move before a big action; attached parts
  (labels, shadows, cargo) settle 40–80 ms after the body. Organic paths travel in arcs.
- **Restraint:** one "wow" moment per sequence. Never animate text the viewer is still reading,
  and never transition the transition.

## 3. Kinetic typography (narration-locked)

- `ktext()` pre-splits text at build time, so line breaks never depend on font loading.
  `mWordsAt(sel, [W(...), ...])` lands each word on its spoken time; `mReveal(sel, t, {by, style})`
  handles headlines and key phrases.
- Granularity: **line** (calm, premium; default for statements), **word** (energy; key phrases),
  **character** (only for short punchy words). Mask (wipe up from a hidden baseline) is the
  default style; blur-in costs render time, so use it sparingly.
- Type is for the key phrase, number or term. The narration and captions carry the sentence;
  don't duplicate captions on screen.

## 4. Diagrams, mechanisms, blueprints

- **Progressive disclosure:** nodes, then edges, then labels, each on its spoken word
  (`mDiagram`). Nothing appears all at once.
- **Focus and context:** light the active step and dim the rest (`mFocus` / `mUnfocus`), so the
  viewer always knows where to look.
- **Flow means movement of something real:** goods, money, power, data or coolant. Use
  `mFlow(path, t0, t1, {dots, reverse})` (marching dash plus travelling tokens) with a consistent
  colour grammar: cyan for products and services, gold for money, orange for heat.
- **Blueprint and hand-drawn beats:** `mDrawOn` draws strokes in document order, with fills after
  outlines. Author paths in the order a hand would draw them. For a hand-drawn line, alternate
  pre-drawn variants every ~4 frames (`mBoil`); never jitter every frame.
- **Exploded views:** separate along one axis in assembly order and reseat exactly. Label each part
  as it separates.

## 5. Data and charts

- Every value is a pure function of timeline time (GSAP on `tl`); no timers and no
  `Math.random()`.
- Counters: `mCount` (Intl formatting, tabular figures, lands on the exact value). Bars: `mBars`.
  Lines: `mLine`. Label axes and units once, and show the source.
- **Holds (guideline):** let a finished chart rest about 2 s (`MOTION.hold.chart`) before the next
  beat when the viewer needs to read it. Shorten the hold when the narration moves on and the
  point has landed; lengthen it for dense charts.
- Never invent figures. Illustrative scales say **"Illustrative"** on screen.

## 6. Isometric economic worlds

- True isometric: ground axes at ±30° (`iso`, `iso_box`, `iso_grid` in kit/motion.py) or a
  Three.js orthographic camera (the diorama).
- One fixed light for the whole scene: top face full colour, left about 82 %, right about 64 %
  (`shade`).
- Build bottom-up by physical position. Lift on Z (translateY), never scale (scaling breaks the
  projection). Camera drift stays small and slow in 2.5D; real 3D worlds can travel.

## 7. Maps (geography beats)

- Vector maps from Natural Earth (`world_map_svg`, `projection('equirect' | 'mercator' |
  'ortho')`; data licence in `kit/data/LICENSES.md`). Highlight countries with focus and context:
  target lit, everything else muted.
- Routes are great circles (`route_path`) drawn in reading order (`mDrawOn` / `mFlow`). Pins and
  labels use the same projection so they stay locked to place. Labels stay horizontal and inside
  the safe area.
- An optional editorial "stutter" on overlays (`mStutter`, 12 fps steps) gives a documentary-map
  texture while the base map and camera stay smooth. Use it as a stylistic choice, not a default.
- Check disputed borders before an editorial use.

## 8. 3D on CPU (software WebGL)

- Use `kit/three_kit.js` (`ELK3D`): `keyCam`, procedural `surface()` materials (brick, panel,
  louvre, concrete, asphalt, rust, wood), `flowAlong` tokens, `flowField` for air, heat and smoke,
  and `shadowFollow`.
- Cost control: animate emissive or material properties instead of adding lights; one
  shadow-casting light whose frustum follows the shot; instance repeated objects; reuse geometries
  and materials. Post-processing (ambient occlusion, depth of field) only on hero shots, measured
  first.
- Seed everything; particles are pure functions of time, so any frame can be seeked.

## 8b. Illustrated 3D sets, light and close-ups (art direction v2)

- **Plan first.** Every shot gets a `scene_plan.json` entry (`kit/scene_plan.py`). Pick shot size
  by purpose: establishing to place the relationship, medium to explain with people and the
  object, close-up for consequence and emotion, insert or chart where data must be read.
- **Sets:** `kit/scene3d.js`. Build in metres with a real camera (`S3.camera`, lens `shift` keeps
  architecture vertical), facades with irregular lit windows, extrusions for vehicles and
  profiles, CC0 textures (`tex`, `texMix` to calm busy textures), `ground` tiling for floors.
  One key light (sun or lamp) and a hemisphere fill, fog for depth, soft cast shadows. Anchor
  glows and labels to 3D points with `cam.project` so they move with the camera.
- **Atmosphere:** `kit/lightfx.py`: graded `sky`, `haze` at the horizon, `beams` through windows,
  `glow` on sources, `depth_blur` on foreground or background layers, and `grade` (vignette, grain).
- **People:** `kit/rig3.py`. `figure_svg` for staging (IK `REACH` puts hands on keyboards, phones
  and boards); mirror with `scale(-1 1)` to face left; `closeup_svg` for faces (expression,
  tired lids, key/rim colour matching the light source in the scene).
- **Data on objects:** `kit/diegetic.py`. Whiteboards, CRTs, market boards, gauges and press
  clippings, mapped with `S3.art`. Prefer these to overlays; use a standalone chart when
  precision matters more than context.
- **Camera in motion:** move the `S3.camera` position or look keys per frame (re-render the SVG) for
  hero moves, or layer the rendered set with `mCamera`/`mParallax` for 2.5D moves; slow, motivated
  pushes, not constant drift.

## 8c. Meaning-first visual storytelling (outranks style and animation quantity)

Two rejected previews define the boundaries. The first held one whiteboard for ~14 s across five concepts (too
static). The second cut ten times in 14 s, used a coin tank that read as cheese, repeated pipes and valves, and did
not separate a funding agreement from money received (too frantic, too metaphorical). The standard between them:

1. **Understand before designing.** For each narration passage write `meaning` = what happens, why, consequence
   (the plan validator requires it). Group the words into *concept beats*: "spending on advertising, employees and
   infrastructure" is ONE beat (spending), not three shots.
2. **Connected compositions, progressive animation.** One composition per beat, typically 2.5–5 s, in which the
   named parts appear or act on their words (bills fly to the TV on "advertising", pay lands on desks on
   "employees", a rack is wheeled in on "infrastructure"). Validator: ≥ `MIN_SHOT` 2 s per composition (inserts
   0.5 s with an `insert_reason`), ≤ `MAX_CUTS_PER_10S` 4, no hold over `MAX_HOLD` 6 s without a `hold_reason`.
3. **Recognisable and accurate.** Money is banknotes and bundles (`kit/money.py`); advertising is an actual
   commercial or billboard; salaries are pay; infrastructure is equipment being installed. Use a metaphor only when
   it explains something a literal image cannot, and do not repeat one metaphor across every beat.
4. **One source of truth for numbers.** Build a `kit/finstate.Ledger`; every pile, counter, chart and runway is
   derived from it, and figures are labelled illustrative when they are. Indicators keep the same geometry across
   beats (the cash chart in "shortfall" returns unchanged in "money received").
5. **Explain with the right tool.** When the idea is quantitative (out vs in, runway), use a clean chart
   (`kit/explain.py`) and give it time to be read; when it is an action (signing, paying, installing), show
   people doing it; when it is a process with steps, number the steps (agreement → money received).
6. **Separate steps that are legally or economically different** (agreement vs receipt, revenue vs profit,
   valuation vs cash) into distinct visual moments.
7. **Characters act with intent:** eyes lead the head (`R3.look`), weight-shift stances (`stand2`, `hips`),
   contact with objects (`rig3.reach`, `hold`), interaction between characters (handshake, handing over, signing
   with `R3.write`), anticipation and follow-through (`R3.keys`).
8. **The mute test** still applies: with the sound off, the story (what, why, consequence) must be followable.
9. **Not evidence of quality:** number of animations, cuts, camera drift, blinking, particles, frame-difference
   statistics.
10. **Rendering:** static sets are cached plates (`kit/plates.py`); characters, money and charts animate live.
    References: `episodes/ai-bubble-vs-dot-com/motiontest/office_v3.py`, `office_v3_plan.json` (current) and the
    rejected `office_v2_plan.json` / `scene_plan.json` kept as negative examples in the tests.

## 9. Transitions

Motivated only: a match cut on shape or action, a push into a screen or cutaway (circular iris),
a seam split, a dip on a beat, or a whip with the action. Keep one transition family per sequence.
Remotion techniques (frame-pure `interpolate` and `spring` thinking, typed props) apply directly to
GSAP on our timeline. The Remotion caption pass stays available (`config → captions`). Standalone
Remotion templates from other skill packs are **not** used.

## 10. End screen (YouTube)

- `endscreen_html()` + `mEndScreen()`: the last **5–20 s**, with two video slots and a round
  subscribe slot as empty framed areas (YouTube's own elements cover them), over a live, slowly
  moving continuation of the film's final world. There is **no logo intro and no logo sting**: the
  identity is typography and palette. Keep the slots out of the caption band and in the frame's
  safe area. Narration may finish over it.

## 11. Optional future capability: Manim

For an equation-heavy or proof-like explanation (compounding, discounting, option pricing
surfaces), Manim CE (MIT, available from PyPI) can render a self-contained beat. It is **not
installed**. Adding it needs approval, a style pass to match the series palette and type, and a
separate render step.

## 12. QA for every changed scene

1. `snapshot` contact sheets at every synced word time.
2. `node epoch-ledger/scripts/layout_check.mjs WS/index.html --start a --end b`: text collisions,
   caption-band intrusions, off-frame labels, text over `data-keep` objects. Mark decorative text
   with `data-deco` and important labels with `data-read`.
3. A short 540p motion render (`render.py range`), watched and compared with the previous version.
4. `python epoch-ledger/scripts/motion_demo.py WS` shows every helper in one 30-second reference
   composition.
