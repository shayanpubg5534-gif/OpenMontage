# Creative direction layer and the P13 storyboard (the P12 mortgage passage, re-directed)

Status: **awaiting your approval of the treatment and the hero key frames.** No animation has been rendered. P12 is
untouched: its narration, assets, cast, scripts and film are unchanged and are read only.

- **Key frames:** `charlab/evidence/p13/KF1.jpg` … `KF6.jpg`.
- **Sheets:**
  - `charlab/evidence/p13/storyboard_sheet.jpg`: the six frames with the chosen concepts.
  - `charlab/evidence/p13/compare_p12_vs_p13.jpg`: the same narration at the same times, P12 on the left and the new
    direction on the right.
- **Treatment:** `charlab/p13/treatment.json`, with its readable version in `charlab/p13/treatment.md`.

## 1. Step 1: the creative direction layer (committed `b5f3d4b`)

| What | Where | Notes |
|---|---|---|
| Permanent standard | `STANDARD.md` §3A (13 points) and §5 process | The process runs: treatment → storyboard gate → brief → build → check → watch plus director's review. |
| Director's guide | `skills/creative/epoch-ledger-director.md` | Wrapped by `.claude/skills/epoch-ledger-director`. |
| Routing | `AGENT_GUIDE.md`, `CLAUDE.md`, `/epoch-ledger`, `skills/creative/epoch-ledger.md` (step 4a), `skills/INDEX.md`, `README.md`, `COMPONENTS.md` | |
| Treatment checker | `kit/treatment.py` (template: `templates/episode/treatment.json`, copied into new episodes) | It checks that the thinking is written down: the literal baseline is considered, exactly one concept is chosen, metaphors have accuracy notes, acting is more than heads and blinks, and transitions have motives. `--gate motion` blocks animation until the hero frames are approved. |
| Scene-plan fields | `kit/scene_plan.py` `"direction": 2` (opt-in) | Each shot gets a world, an acting beat and `transition_in`. Plans without the field behave exactly as before. |
| Director's review | `QUALITY.md` | Ten questions answered on the rendered frames, not on fields or tests. |
| References (not restrictions) | `direction/VISUAL_LANGUAGE.md`, `direction/CONCEPT_NOTES.md`, `direction/used_devices.json` | |

**Compatibility.** Everything is additive. Rig v4, the P5 renderer, `render.py`, HyperFrames assembly and production
defaults are not modified. Existing episodes and plans validate as before.

## 2. Step 2: the treatment (same narration, same timing)

- **Thesis:** understand that a family's mortgage was sold, pooled and turned into a security with ranked claims, so
  that when families stopped paying, losses travelled from a kitchen to investors worldwide. Feel the growing distance
  between those who owe and those who own, then the consequence coming home.
- **Through-line:** one family's loan. Their house is gold on the map, in the pool and under the building, and it is the
  first to turn red.
- **Arc:** a kitchen table → pool, security, world → the mechanism breaks → the same table, changed.

| Seq. | Narration | Chosen concept (the literal baseline, P12's picture, rejected each time) | Hero |
|---|---|---|---|
| q1 | "In 2006, a family signs a mortgage they can barely afford." | **The kitchen table** at dusk, with a street of similar houses through the window. | ✔ KF1 |
| q2 | "The lender doesn't keep the loan; it sells it on," | **The street rises into the map:** their house turns gold, and its line runs to the lender, then on. | |
| q3 | "bundled with thousands of others into a single security." | **Pool, then building:** the town's loans converge into one pool. The pool becomes the foundation of a paper-model building whose floors are the tranches. | ✔ KF2, KF3 |
| q4 | "Investors around the world buy it because it promises steady payments." | **Floors sold abroad:** payments climb the servicer's pipe and fall floor by floor. Each buyer on the world map is labelled with the floor it owns. | KF4 |
| q5 | "But then house prices fall," | **The chart grows out of the town:** FOR SALE signs appear, and the sourced price index draws across the rooftops and turns down. | |
| q6 | "and families stop paying." | **The same table, two years later:** night, the pendant off, one lamp left on. She holds the letter; he has turned away. | ✔ KF6 |
| q7 | "The payments dry up, the securities collapse," | **The flood:** the pipe's flow thins, and red rises through equity into mezzanine. Senior floors stay dry but dim and are marked downgraded. | ✔ KF5 |
| q8 | "and in September 2008, Lehman Brothers goes bankrupt." | **The newspaper on their table** beside her letter. Wall Street's failure and the family's notice share one frame. | KF6 |

There are four hero sequences (q1, q3, q6, q7). The others are still directed and reuse the same worlds and formats.
Every transition has a motive:
- through the window into the street;
- the pool rectangle cut to the plinth;
- the pipe's flow becoming the routes;
- a dissolve on their lit window;
- the letter's red rule becoming the rising red.

**Accuracy (the securitisation caveats).** The four stages are distinct objects:
- **Origination:** house → lender.
- **Pooling:** the pool, a trust.
- **Issuance:** the building, which stands on the pool but is not the pool.
- **Distribution and loss allocation:**
  - payments are paid senior first;
  - losses rise from the bottom;
  - senior floors are reached only past the subordination below them, and are shown downgraded and dimmed, not
    destroyed;
  - the lender's sale line stays drawn, because lenders kept some risk.

Buyers and figures are labelled illustrative. The Lehman front page is labelled a reconstruction (filing 15 September,
dated 16 September).

## 3. The key frames, and how each is produced in animation

All six frames were made with the production tools, so each is a frame the animation path can reproduce. The whole
storyboard rebuilds cold in **58 s** with `charlab/p13/run_storyboard.sh`.

| Frame | Built with | What the animation adds (all within current capability) |
|---|---|---|
| **KF1** kitchen 2006 | New kitchen set from existing `motion/env.js` components and CC0 textures, `shot_render.mjs` plate, depth pass, P10 compositor, P12 identities | He shifts his weight forward and his head lowers to the papers (shift, tilt, face swap). She draws her mug in. Push-in to the papers. Insert: cut on action (pen lifted, then the signed page). |
| **KF2** pooling map | New `pool_map` format (HyperFrames) | Lines draw on house by house, the gold thread runs house → lender → pool, and loan tiles fill the pool. |
| **KF3** the security | New `scenes/tranches.js` (`three_shot.mjs`, procedural) and `frame_overlay` | The camera rises from their gold house up the building. Payment drops climb the pipe and windows light floor by floor, top down (events). |
| **KF4** investors | P12 `world_map` (reused) plus `label` | Routes and buyers appear and payment dots flow (as in P12). The through-line label arrives. |
| **KF5** losses | `tranches.js` loss state | The pipe thins, red houses spread in the pool, and the flood rises through equity into mezzanine. Senior windows dim and the downgraded label appears. |
| **KF6** kitchen 2008 | Same room re-lit (night variant), P10 compositor, P12 `newspaper` | Her eyes drop to the letter. He turns his head away and sits back. The paper is set on the table (cut). Push-in on "bankruptcy". |

**Expected animation cost:** about P12's, 16 min per finished minute.
- The building renders at about 2 s per frame, like P12's 3D stack (210 s for its shot), with static holds rendered
  once.
- The kitchen uses the same compositor as P12's 2.5D shots (about 10–20 s each).
- The new world is built once and reused. Its plates take 11 s each and the depth pass 4 s.

## 4. Decisions for you

1. **Approve or redirect the treatment and the hero frames** (q1, q3, q6, q7), in one batch. After approval I set
   `"approved": true` and `kit.treatment --gate motion` lets animation start.
2. **One wardrobe change, proposed, not adopted.** In 2008 the wife wears the artist's "holding a paper" bust: a dark
   sweater whose flecks take her sage colour. It is the only pose in the free library with a held letter, so it gives
   her hands the consequence.
   - Her head, hair and skin stay her identity and are checked.
   - It is declared in `p13/keyframes.py` (`WARDROBE_CHANGES`) and applied in that process only; P12's `cast.py` is
     unchanged.
   - If you prefer strict wardrobe continuity, KF6 falls back to her sage shirt with the coffee mug, and the letter
     goes on the table in an insert.
3. **The tranche building as a series device.** It is logged in `direction/used_devices.json`, so later episodes reuse
   it only with a reason.

## 5. Limitations (honest)

- **Hands:** the free character art has no hand-to-object contact at a table. No pose shows hands on papers, and no
  pose sits at a table, so the art provides only busts behind the table. Signing is told with a cut on action and an
  insert. Acting is in posture, weight, head direction, held objects (mug, letter) and reactions. A commissioned set
  of table poses (signing, hands on papers) would lift this most. That needs your approval and is not requested here.
- **Faces:** the expressions are the artist's set. The right one is chosen per beat; "Blank" reads as looking down at
  the page. There is no talking face anywhere, keeping to the voice-over standard.
- **The 3D building** is deliberately a model on a table, not a real skyscraper, so it reads as an explanation.
- **Investors and labels** in KF4 are illustrative patterns (documented in general, not one real deal) and are
  labelled.
- **q2 and q5** have no key frame. They are directed sequences built from the KF2 format (the street map reprise and
  the price line over the rooftops) and are described in the treatment.
- **Character lighting** in the night frame is matched from the plate (`light.match`). Under the cold street light his
  shirt still reads slightly bright. I'll fine-tune that during animation.

## 6. Production overhead for 2–3 episodes a week

| Step | Cost per 8–10 min episode |
|---|---|
| Treatment (`treatment.json`, one table row per sequence) | About 30–45 min of agent time. It is checked in under a second. |
| Hero storyboard (3–5 heroes, 4–8 frames) | Stills from the production tools: about 1 min of render for this passage, about 5–10 min for an episode. Plus one batched approval from you per episode. |
| New world | A set JSON from existing components, two plates and a depth pass (about 30 s). It is then reused and re-lit. |
| Animation | Unchanged from P12. Hero worlds add one-off builds. Directed sequences reuse formats and worlds. |

The only new manual gate is one storyboard approval per episode, covering the heroes in a single batch. Non-hero
sequences go straight to build.

## 7. Tests and reproducibility

- `pytest tests/epoch_ledger/test_creative_direction.py tests/epoch_ledger/test_charlab_p13.py`.
- The full `tests/epoch_ledger` suite passes. One pre-existing, timing-sensitive lock test is flaky under full-suite
  load; it passes on its own and is unrelated.
- `epoch-ledger/charlab/p13/run_storyboard.sh` rebuilds the backdrops, sets, plates, depth, 2.5D and 3D frames, board,
  treatment check and sheets cold.
- Timings are in `charlab/p13/perf_cold_run.jsonl`.
