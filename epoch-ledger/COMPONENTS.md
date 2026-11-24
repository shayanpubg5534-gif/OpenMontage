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
| `render.py` (`plan`, `scene`, `range`, `render`) | `scripts/render.py` | scene-cached chunk renders; `range --start --end` for preview clips |
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
| `layout_check.mjs` | `scripts/` | text-collision / caption-band / off-frame QA over time |
| `motion_demo.py` | `scripts/` | reference composition exercising every helper |

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
