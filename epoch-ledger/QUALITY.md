# The Epoch Ledger — visual quality standard and checklist

Applies to every episode and every scene. A scene is approved only when it meets **all four**
independent requirements below. Meeting one never compensates for missing another.

| # | Requirement | Failing example |
|---|---|---|
| 1 | **Professional visual design and environmental detail** | box buildings, flat terrain, toy geometry, empty backgrounds |
| 2 | **Natural, purposeful animation** | sliding figures, identical loops, camera drift standing in for action |
| 3 | **Precise narration-to-action synchronisation** | a platform that stays empty until the sentence ends |
| 4 | **Semantic visual storytelling** — the picture explains the *meaning*, *mechanism*, *cause* or *consequence* of the narration | "enormous investment" illustrated by a train driving along a track |

**Not evidence of quality:** frame-change percentages, camera movement, glow, moving particles.
A moving object is not storytelling; a camera move is not an action; a glowing object is not an
explanation of a technical process. Motion metrics are only a smoke test for frozen frames.

## 0. Scene brief (write it before building)

For every scene, in `storyboard`/`art-direction`, answer:

1. **Message** — what is the narrator communicating?
2. **Understanding** — what must the audience understand afterwards (the idea, not the noun)?
3. **Demonstrating actions** — which visible actions *show* that idea (people working, goods and
   money moving, machines operating, costs piling up, a counter crossing a threshold)?
4. **Trigger words** — which spoken words start each action (Whisper word times)?
5. **Progression** — cause → mechanism → consequence, where the line has one. Show the cause
   before the consequence (e.g. losses accumulate *before* the abandoned station appears).

## 1. Semantic storytelling rules

- **Introducing something does not explain it.** After an object appears, the following
  narration must keep driving meaningful actions. Every company, facility or device gets:
  1. **Introduction** — reveal it;
  2. **Operation** — show what it actually does (internal machinery, people, equipment, the
     technical process), using close-ups, cutaways and interiors;
  3. **Transaction / effect** — show what moves out of it and back (products, services,
     computing capacity, money), returning smoothly to the overview model.
- Abstract economic words need concrete visual equivalents: *investment* = capital being
  deployed (construction, materials, equipment purchases, workers); *returns* = customers,
  freight, revenue accumulating over time against the cost; *insufficient demand* = empty seats,
  idle capacity, falling revenue while costs continue; *disaster* = the consequence of the losses.
- Technical words need the mechanism: *calculations* = data in → many units working in parallel
  → results out; *cooling* = heat building (thermal gradient) → hardware extracting it → coolant
  circulating → temperature falling.
- Financial overlays (ledgers, bars, meters) are welcome when they make the mechanism legible.
  Never invent figures: use unlabelled/illustrative scales and say "Illustrative" on screen.
- Decorative particles, glows and lens effects are allowed only when they carry meaning (a packet
  of data, a unit of money, heat).

## 2. Synchronisation

- Every object and action starts on the Whisper time of the word that names it —
  `W("semiconductor", "c05_02")` — never on a line end or guessed seconds. Nouns bring things on;
  verbs start actions. Labels appear on their word (± 0.3 s). Camera moves start ≈ 1 s early so
  the subject is framed when it is named.
- No unexplained static periods while narration runs. **Intentional holds are fine** when they
  help comprehension (letting a chart or a result land) — but something meaningful is still
  happening or being read.
- `W()` raises if a word is missing, so script edits cannot silently desync a beat. Use caption
  spelling (numerals: "78", "$10").

## 3. Animation

- Characters use the jointed rig (`kit/rig.py` + `kit/rig.js`): varied looks (`crowd_look`),
  purposeful poses for the beat (`rpose`), seeded ambient acting (`ambient`), walks (`rwalk`),
  expressions (`rexpress`), props (phones, tickets, tools).
- Machines move the way they work (wheels roll by distance/radius, rods follow cranks, arms pick
  and place, fans spin, fluid flows in its pipes).
- Camera: dolly, track, crane, parallax (≥ 3 layers in 2D), keyframed 3D cameras (`keyCam`) —
  in service of showing the action, never instead of it.
- Transitions are motivated (match cut, push into a screen, cutaway in/out of the model).

## 4. Visual design

- Premium hybrid: detailed illustrated sets and rigged characters + lit 3D (shadows, fog depth,
  key/fill/rim, emissive accents) + clean infographics. No slide-like frames.
- Environments have detail at three scales: silhouette (varied rooflines, structure), surface
  (procedural textures: brick, corrugated metal, concrete, rust, wood, panel seams, windows) and
  props (signage, cables, crates, tools, vehicles, people).
- Period-appropriate detail; colour grade by meaning (prosperous warm vs failing cold; boom amber
  vs crash red).
- Explanations keep chart/diagram clarity: legible labels at 540p, legend on first use.

## 5. No repetition

- A reused world/set must change at least two of: environment, perspective, action, purpose.
  Keep a shot log (world, camera class, action) and flag duplicates before rendering.

## 6. 3D asset policy

Procedural Three.js (no GPU, software WebGL) is the default. Raise quality with procedural
canvas textures, instancing and richer silhouettes before anything else. CC0 assets (e.g. Poly
Haven / ambientCG textures and HDRIs, Kenney/Quaternius models) are acceptable when licence and
source are recorded in the decision log; adding a download host needs the user's approval. No
paid services; no engine migration without approval.

## 7. Checklist before asking for approval

- [ ] Scene brief written for each scene (section 0)
- [ ] Requirement 4: every line's meaning is demonstrated, not just its subject; each introduced
      object goes on to operate and transact; cause shown before consequence
- [ ] Requirement 3: every action keyed to its word; no unexplained static periods
- [ ] Requirement 2: rigged, varied acting; machines move as they work; no visible loops
- [ ] Requirement 1: no primitive box structures in hero shots; three scales of detail
- [ ] No repeated hero world without two changes (shot log)
- [ ] Text ≥ 34 px at 1080p, caption band (y ≥ 880) clear, sources on data; illustrative scales
      and hypotheticals labelled
- [ ] Motion render of every changed sequence watched and compared with the previous version
- [ ] Remaining limitations written down for the approval report
