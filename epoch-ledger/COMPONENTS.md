# Epoch Ledger — component index

Find reusable parts here before reading source files or writing new code. Reuse means
re-staging: a new camera, setting, action or purpose each time (see `QUALITY.md` §5).
**Maintenance rule:** any commit that adds, renames or removes a reusable component updates this
file in the same commit (`tests/epoch_ledger` checks the listed files and symbols exist).
Paths are relative to `epoch-ledger/`. "Episode" items live in `episodes/ai-bubble-vs-dot-com/`
and are copied/promoted into `kit/` when a second episode needs them.

## Pipeline and timing

| Component | Where | Use |
|---|---|---|
| `assemble`, `Scene`, `RESOLUTIONS` | `kit/assemble.py` | build a cache-friendly HyperFrames `index.html`; per-clip zoom for 540p/1080p/1440p |
| `caption_layer` | `kit/captions.py` | HyperFrames-native word-highlight captions (approved pilot look) |
| `narrate.py` | `scripts/narrate.py` | per-line Kokoro TTS (content-addressed cache), Whisper words, caption pages, SRT, audio check |
| `render.py` (`plan`, `scene`, `range`, `render`) | `scripts/render.py` | scene-cached chunk renders; `range --start --end` for preview clips. Cache keys follow asset references through CSS/JS/HTML; stale HyperFrames locks (dead pid) are removed and orphaned renders of the workspace stopped before rendering (`--keep-orphans` to only report); each chunk runs under a watchdog; `--isolate` renders scene-aligned chunks from reduced documents in parallel HyperFrames slots (verified against the full document by `scripts/isolate_check.mjs`, full-document fallback), `--jobs N` now runs N chunks at once |
| `L`, `W`, `WE` | episode `timeline.py` | line windows and Whisper word times — **every beat keys to `W(word, line)`** |
| `sfx.py` | episode `sfx.py` | synthesised original sound design + mix (no music) |

## Motion kit (series-wide; guide: `skills/creative/epoch-ledger-motion-craft.md`)

| Component | Where | Use |
|---|---|---|
| `MOTION` tokens | `kit/motion.js` (bundled in every composition) | series easing / durations / stagger (mirrors `config → production.motion_language`) |
| `mReveal`, `mUnreveal`, `mWordsAt`, `mSplit` | `kit/motion.js` | kinetic type: masked line/word/char reveals; words landing on their Whisper times |
| `ktext` | `kit/motion.py` | pre-split kinetic text markup (stable line breaks) |
| `mDrawOn`, `mBoil` | `kit/motion.js` | blueprint / hand-drawn stroke draw-on (fills after outlines); boiling line |
| `mDiagram`, `mFocus`, `mUnfocus`, `mFlow` | `kit/motion.js` | nodes → edges → labels; focus + context; marching connectors with tokens |
| `diagram_node`, `diagram_edge` | `kit/motion.py` | SVG node/edge markup for the above |
| `mCount`, `mBars`, `mLine` | `kit/motion.js` | exact formatted counters (tabular figures), bars, line draw |
| `mCamera` | `kit/motion.js` | 2D world camera: crane / pan / push across a large illustrated world (e.g. 3840×2160), depth-layer parallax, breathing holds |
| `mAmbient`, `mParallax`, `mPush`, `mStutter` | `kit/motion.js` | environmental life, depth parallax, camera push, editorial 12 fps steps |
| `iso`, `iso_box`, `iso_grid`, `shade` | `kit/motion.py` | true-isometric 2.5D builds with one fixed light |
| `world_map_svg`, `projection`, `route_path`, `countries` | `kit/motion.py` + `kit/data/` | Natural Earth vector maps, highlights, great-circle routes |
| `endscreen_html`, `mEndScreen` | `kit/motion.py`, `kit/motion.js` | YouTube end screen (last 5–20 s), live background, no logo |
| `ELK3D.keyCam`, `surface`, `flowAlong`, `flowField`, `shadowFollow` | `kit/three_kit.js` (opt-in head script) | 3D camera keys, procedural materials, meaningful particle flows, shot-following shadows |
| `layout_check.mjs` | `scripts/` | text-collision / caption-band / off-frame QA over time; also text painted over by a later SVG mark (`text-occluded`) and text on a same-coloured mark (`text-low-contrast`). All text in diagram layers (`data-diagram`, kit `-Lboard` layers) counts as readable; `--read <css>` adds more |
| **P1 quality gates** | `scripts/quality_gates.py` | runs every gate for an episode from `episodes/<slug>/gates/gates.json` and writes `gates.json` + a review page; never renders. `python epoch-ledger/scripts/quality_gates.py epoch-ledger/episodes/<slug>/gates/gates.json --out DIR` |
| `finmodel` (`Scenario`, `simulate`, `validate`) | `kit/finmodel.py` | daily cash model (payment terms, recurring flows, loans with financing cost, overdraft limit; unpaid bills tracked as a shortfall, never as a negative balance) and the validator: FIN-FIGURE, FIN-ARITH, FIN-NEG-BALANCE, FIN-RECURRING, FIN-LOAN-SIZE, FIN-FIN-COST, FIN-COST-SHOWN. Complements `finstate.Ledger` (monthly runway arithmetic) |
| `figure_check.mjs` | `scripts/` | each figure the narration names is legible when spoken (in its clip, opacity, in frame, not painted over, contrast) and not revealed long before; chart marks proportional to their values and on a shared baseline |
| `Gates` (`value`, `fig`, `chart`, `mark`, `event`, `write`) | `kit/gates.py` | **gate settings generated by the build** (no hand-written manifests): the call that draws a figure tags it and registers it (cue validated against the narration at build time; value read from the `finmodel` scenario), charts register their marks and values, `write(ws, scenes=…)` emits `WS/gates/gates.json` with figures, finance claims, cuts and `"contacts": "auto"`. Used by `templates/episode/build.py` |
| `contact_check.mjs` | `scripts/` | every frame of every hold: wrist-to-prop distance (`detached`), prop covering wrist and palm (`hand-hidden`), one-frame prop jumps or flips (`prop-pop`). `--auto` reads every `R4.hold` (and `window.__gates.contacts`) from the built page, so the hold that animates a prop is the hold that is checked. Rig v4 today; the 3D character layer reports the same quantities from bone sockets |
| `review_sheets.py` | `scripts/` | from a stored MP4: consecutive-frame contact sheets (−5…+10) around every interaction and cut, optional enlarged crops, 1-in-30 frame sample, human checklist page |
| determinism guards | `kit/helpers.js`, `kit/assemble.py` (automatic) | transform origins applied once per element instead of inside tweens; `force3D:false`; overlapping tweens of one property clipped so the later one takes over (`__elResolveOverlaps`); start states primed so frame 0 shows them |
| `qc.mjs` | `scripts/` | STANDARD §2.6 QC: determinism (element state of frames drawn in time order vs shuffled order must match; pixel-only differences are reported as Chromium raster noise; idea from OpenFilm `look`, MIT), video scan for black / single-frame flash / opening jump / frozen stretches, loudness, cut-time study. `node scripts/qc.mjs WS/index.html --video OUT.mp4` |
| `motion_demo.py` | `scripts/` | reference composition exercising every helper |

## Art direction v2: illustrated 3D, light, characters, diegetic data (plan first: `kit/scene_plan.py`)

Use these for new or regenerated scenes. Approval stills live in `episodes/ai-bubble-vs-dot-com/styleframes/`
(`sf1_establishing.py`, `sf2_medium.py`, `sf3_closeup.py`, shared `common.py`; outputs in `styleframes/out/`).

| Component | Where | Use |
|---|---|---|
| `scene_plan.py` (`validate`, `python -m kit.scene_plan PLAN.json`) | `kit/scene_plan.py` | **mandatory** per-shot plan: beat, understanding, shot size, focal point, camera, lighting, technique, components, graphics (diegetic/standalone/overlay+why), rationale, guides consulted. Enforces shot-size variety and no unjustified overlays |
| `S3.camera({pos, look, fov, shift})` | `kit/scene3d.js` | real perspective camera with lens shift (vertical-safe architecture), `project()` for anchoring glows/labels to 3D points |
| `S3.scene()` → `box`, `quad`/`poly`, `cyl`, `tube`, `extrude`, `wheel`, `ground` | `kit/scene3d.js` | build sets in metres; faces lit by sun + sky/ground hemisphere + point lamps, fog, soft cast shadows |
| `S3.facade({...})` | `kit/scene3d.js` | brick/glass building fronts: window grid, lit windows, sills, lintels, frames (seeded) |
| `S3.art(p0, p1, p3, w, h, markup)` | `kit/scene3d.js` | map any SVG (whiteboard, billboard, screen, poster) onto a 3D quad in perspective |
| `S3.sprite(foot, height, markup, aspect)` | `kit/scene3d.js` | depth-sorted 2D characters/props standing in the 3D set (occlusion + shadow) |
| `S3.render(sc, cam, L, {ow, shadowBlur, uid})` | `kit/scene3d.js` | painter-sorted lit SVG with ink outlines thinning by distance; materials: `color, tex, texScale, texMix, tint, emissive, gloss, alpha, outline, receiver, doubleSided` |
| `sky`, `haze`, `beams`, `glow`, `depth_blur`, `grade` | `kit/lightfx.py` | graded skies, atmospheric haze, light shafts, bloom, depth of field, vignette + grain + colour grade |
| `figure_svg(p, costume, pose, expr, ...)`, `POSES`, `REACH`, `ik(` | `kit/rig3.py` | 7.5-head characters (three-quarter), detailed faces/hands/costumes; two-bone IK places hands on targets; FK groups compatible with `rig.js` |
| `closeup_svg(p, expr, hand, key, ...)` | `kit/rig3.py` | modelled close-up head + shoulders (expression, tired lids, stubble, key/rim light, hand with phone or on chin); ids `-brows`, `-mouth`, `-lids`, `-hand` animate |
| `R3.rot`, `R3.pose`, `R3.blinks`, `R3.breathe`, `R3.talk`, `R3.type`, `R3.idle`, `R3.walk` | `kit/rig3.js` (opt-in head script) | rig v3 acting on the master timeline: exact joint angles (`pose_angles` from Python, shortest arc), irregular blinks, breathing (on an `R3.carrier` group, so it never fights a joint's rotate()), speech flaps (only for a character speaking in the story), typing, weight shifts, and walking a scene3d sprite between two 3D points with perspective scale |
| `R4.create`, `walk`, `turn`, `sit`, `stand`, `reach`, `release`, `hold`, `look`, `express`, `say`, `nod`, `shift`, `place`, `key`; `rig4.CAST`, `create_js`, `sprite_svg` | `kit/rig4.js` (opt-in head script, `R4.attach(tl)`), `kit/rig4.py` | **rig v4**: a 3D skeleton seen orthographically and drawn each frame as continuous illustrated shapes — one model for front / ¾ / profile / rear (continuous yaw), seamless bending limbs, two-bone IK with poles (planted feet, palm-on-target reaching with automatic lean), grip / open / point hands with held props, faces on the head sphere (eyes lead the head, brows, smile, blinks), mouth only inside `say()` windows, spring-lagged hair and tie, `occlude` for table edges. Keyframes are evaluated as pure functions of time (later key takes over). Proof: `experiments/rig4_proof/build.py`. Rig v3 stays available |
| `depth.layered`, `Layered.html`, `Layered.move_js`, `depth.foliage`; `DL.move`, `DL.set` | `kit/depth.py`, `kit/depth.js` (opt-in head script) | **depth-layered environments**: one scene3d set rendered as cached bg / mg / fg plates (`S3.render(..., {layer, split})`: architecture stays back, solid objects split by camera depth, `layer` tags win; fg/mg plates transparent; depth of field baked into the plate), haze between layers, characters at midground depth with foreground occlusion; a parallax camera that trucks / rises / dollies each layer by the inverse of its depth (with just-enough overscan). Demo: `experiments/depth_demo/build.py` |
| `pose_angles`, `JOINTS` | `kit/rig3.py` | IK-resolved joint angles per pose for `R3.P` |
| `tank_svg`, `glass_pipe`, `valve_wheel`, `gauge_dial`, `envelope`, `tv_set`, `brass_plate`, `coin_defs` | `kit/finmech.py` | **financial mechanisms**: the company's cash as a glass tank of coins, money flows as glass pipes (spending, revenue, capital), valves, gauges, pay envelopes, an ad-playing TV — every moving part id'd |
| `FM.coins`, `FM.drop`, `FM.level`, `FM.valve`, `FM.needle`, `FM.lamp`, `FM.powerOn`, `FM.pop`, `FM.stampIn` | `kit/finmotion.js` (opt-in head script) | money moving along pipes, coins dropping under gravity, tank levels, valves with anticipation, gauge needles with follow-through, alarms, CRT power-on, prop pops, stamp impacts — all seekable |
| `plate(out_dir, name, html)` | `kit/plates.py` | cache a static set as a 2x PNG plate (hash-keyed); animate only foreground live layers over it |
| `Camera` | `kit/camera3d.py` | Python twin of the scene3d camera for laying out 2D overlays on plates; `Camera.js()` gives the identical JS camera |
| `reach`, `hold`, `hand_point`, `PROPS3`, `R3.keys` | `kit/rig3.py`, `kit/rig3.js` | IK to put a hand on a target in the set; props (stamp, pen, envelope) that move with the hand; keyframed joint actions with anticipation/follow-through |
| `Ledger` (`spend`, `earn`, `balance`, `monthly_burn`, `runway_months`, `balance_after`, `curve`, `fmt`) | `kit/finstate.py` | **one source of truth** for every on-screen figure in a sequence (piles, counters, charts, runway) |
| `cash_pile`, `bundle_svg`, `bill_defs`, `wire_slip`, `term_sheet`, `commercial` | `kit/money.py` | recognisable money (banknote bundles, flying bills), the funding agreement vs the wire actually received, a real TV commercial |
| `cashflow_bars`, `runway_chart` | `kit/explain.py` | educational charts from the Ledger: money out by category vs money in with the shortfall; cash over time, runway to zero, funding jumps, "next round needed" |
| `FM.bills`, `FM.pileTo`, `FM.count` | `kit/finmotion.js` | banknotes flying on arcs, a cash pile that always matches the ledger, step counters |
| `R3.look`, `R3.write`, poses `stand2` / `hips` | `kit/rig3.js`, `kit/rig3.py` | eye direction (irises clipped in the eye), signing, relaxed weight-shift stances |
| `office_v3.py`, `sfx_office_v3.py`, `office_v3_plan.json` | episode `motiontest/` | **current reference**: meaning-first, three connected beats in four compositions (spending → shortfall → agreement → money received) |
| `office_v2.py`, `sfx_office_v2.py`, `office_v2_plan.json` | episode `motiontest/` | **reference for narration-driven choreography**: 10 shots in 14 s, one action per beat, follow-the-money motif, cached plates + live foreground |
| `make_motiontest.py` | episode `motiontest/` | reference for animating style-frame sets: captures a style frame's `page()` call, renders the set per shot (`uid`), adds narration-locked acting, diagrams and 2.5D camera; slices the episode narration and builds captions |
| `portrait_svg` | `kit/rig3.py` | medium-close bust for inserts and over-shoulder shots |
| `whiteboard_chart`, `whiteboard_gap`, `crt_chart`, `ticker_board`, `gauge`, `press_clip` | `kit/diegetic.py` | financial data drawn on objects in the scene (map with `S3.art` or place in a 2.5D layer); parts carry ids (`{uid}-seg0`, `-gap`, `-line`, `-fig`...) for word-locked builds |
| CC0 textures + `LICENSES.md` | `kit/assets/textures/`, `kit/assets/LICENSES.md` | brick, wood_floor, plaster, asphalt, concrete, carpet (Poly Haven, CC0); every new asset gets its own licence row |
| `still.mjs` | `scripts/still.mjs` | `node scripts/still.mjs page.html out.png` — 1920×1080 style-frame stills (no video render) |

## Characters and acting

| Component | Where | Use |
|---|---|---|
| `rig_svg`, `crowd_look`, `PROPS` | `kit/rig.py` | jointed rig v2 (elbows, knees, neck), varied looks, hats (`cap`, `bowler`, `top`, `hard`, `bonnet`), props (phone, receiver, ticket, pad, pen, newspaper, coffee, box, hammer, shovel, suitcase, sack, coin, tablet) |
| `rpose`, `rwalk`, `ambient`, `rtalk`, `rexpress`, `rcycle` | `kit/rig.js` | poses (phone, write, type, point, signal, shout, cheer, handsHead, slump, shrug, hold, hammerUp/Down, carry, lift, wave, sit, pay), natural walk, seeded ambient acting, talking, expressions, work cycles |
| `place` | episode `floor.py` | position a rig SVG (x, y, width, flip) |
| `modern`, `modern_user` | episode `rig_people.py` | modern cast; seated user at a desk |
| `worker`, `traveller` | episode `scenes_railway.py` | 1870s workwear / travellers with period hats |
| `person`, `suit` | episode `money_cutaways.py` | modern staff; cleanroom bunny suits |
| `maya_svg`, `banker_svg`, `person_svg` | `kit/characters.py` | pilot characters (v1 rigs; keep for continuity) |

## Illustrated sets (SVG)

| Component | Where | Use |
|---|---|---|
| `floor_scene` (+ `BOARD_JS`, `CSS`) | episode `floor.py` | 1999 trading floor, boom or panic: live quote board, CRT banks, rigged crowd, runners, 5-layer parallax |
| `crt_close`, `portal` (+ `O2_CSS`) | episode `scenes_opening.py` | 1999 CRT desktop: mail, online shop, connected-world windows |
| `defs`, `locomotive`, `coach`, `boxcar`, `track`, `station_building`, `canopy`, `derrick` | episode `railway_sets.py` | 1870s railway kit with brick/plank/ballast patterns, warm or cold grade |
| `startup`, `tower`, `board`, `sky`, `skyline`, `cars` | episode `scenes_burn.py` | redesign world: cutaway dot-com building (billboard, office, servers, lobby cash tank), VC tower + boardroom, capital pipe + valve, market board, street |
| `station` | episode `scenes_railway.py` | busy / failing / ruined station with acting cast |
| `laptop`, `chat` | episode `scenes_infra.py` | home office at night, chat UI, request path to a data centre |
| `fab`, `cloud`, `lab`, `customers`, `iris` | episode `money_cutaways.py` | company operation cutaways (introduce → operate → transact) with circular iris in/out |
| `die_svg`, `tiles_svg`, `grid_block` | episode `die.py` | processor cutaway: memory → compute grid → results |
| `bank_street`, `office_background`, `ledger_sheet`, `credit_gauge`, … | `kit/sets.py` | pilot sets |

## Explanatory overlays

| Component | Where | Use |
|---|---|---|
| `ledger_capital` | episode `scenes_railway.py` | "Capital deployed" ledger rows + upfront-cost bar (illustrative) |
| returns chart, yearly P&L bars, spend-vs-returns columns | episode `scenes_railway.py` (`rwc`, `rwd`, `rwf`) | cumulative returns crossing cost; revenue under constant costs; justified / not justified |
| cooling gauge + coolant loop | episode `scenes_infra.py` (`cool_html`) | temperature into/out of the safe range; chip → exchanger loop |
| capex ledger | episode `scenes_infra.py` (`capex_html`) | buildings, power, cooling, servers — tied to 3D highlights |
| `show`, `hide`, `pop`, `rise`, `drift` | episode `js/episode_helpers.js` | fades and simple beats |
| `blink`, `count`, `walk`, `talk`, `stamp` | `kit/helpers.js` | pilot helpers (counters, stamps) |

## 3D worlds (`AI3D`, episode `js/ai3d.js`)

| World | Shows | Key params |
|---|---|---|
| `dataHall` | rack corridor (opening only) | `cam`, `gold`, `pulse` |
| `serverRack` | one rack macro: sled slides out, fans, heat map, cold plates, supply/return coolant | `keys`, `slide`, `run`, `peak`, `cool` |
| `chip` | accelerator chip, exploded view; `batch:true` = packaging line | `cam`, `explode`, `glow`, `batch` |
| `campus` | v1 campus (opening ground-level construction) | `cam`, `build` |
| `campus2` | detailed campus: halls, chillers, generators, substation, pylons, feeders, construction, deliveries | `keys`, `power`, `supply`, `energy`, `running`, `build`, `items` |
| `diorama` | economic model: nodes rise, flows, per-link payments, growth boost, circular loop | `keys`, `platform`, `ghost`, `rise`, `flow`, `pay[]`, `grow`, `boost[]`, `loop`, `rev` |
| `railway2` | 4-4-0 with rolling spoked wheels, rods, steam; towns; abandoned branch | `keysA`, `keysB`, `turn`, `returns`, `sign` |
| `keyCam`, `moveCam`, `canvasTex` | camera keyframes; procedural textures | — |
| `vault3d` | `kit/vault3d.js` | pilot vault |
