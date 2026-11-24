# The Epoch Ledger — visual quality standard and checklist

Applies to every episode. Run it on snapshot contact sheets **and** on a short motion render of each
priority sequence before asking for approval. A frame sheet alone cannot show stiffness, dead
time or repeated loops: watch the motion.

## 1. Semantic visual-to-narration sync (mandatory)

Objects and actions start **as the concept is spoken**, not after the sentence ends.

- Key every beat to the Whisper word time of the word that names it — `W("semiconductor", "c05_02")`
  — never to a line start plus a guessed offset, and never to the end of a line.
- Nouns bring things on screen; verbs start actions: "imagine an economy" → the platform assembles
  on *imagine*; "a semiconductor manufacturer" → the fab rises on *semiconductor*; "purchases those
  chips" → chips flow on *purchases*; "pay" → payments start on *pay*; "disaster" → the sign falls.
- Labels and tags appear on the word they name (± 0.3 s). Camera moves start ≈ 1 s before the
  word so the subject is framed when it is named.
- No empty frames while the narrator is describing something: if a sentence opens with context
  ("To understand the financial risks…"), the set itself should already be assembling.
- `W()` raises if a word is missing, so a script change can never silently desync a beat. Use the
  caption spelling (numerals: "78", "$10").
- Audit: for every scene, list each noun/verb that has a visual and confirm the visual's start
  time is within 0.3 s of the word (`snapshot --at <word time>`).

## 2. Motion and acting

- Characters use the jointed rig (`kit/rig.py` + `kit/rig.js`): elbows, knees, neck, props.
  Crowds get varied looks (`crowd_look`) and seeded, non-repeating acting (`ambient`), with
  purposeful poses for the story beat (`rpose`) and expressions (`rexpress`).
- Walks use `rwalk` (hip swing, knee flex, counter-swinging arms, bob) — never sliding figures.
- Something meaningful moves in every shot: background activity (runners, screens, smoke,
  traffic, fans), not just a zoom. No floating objects, no identical loops visible side by side.
- Camera: dolly, track, crane, parallax across ≥ 3 depth layers (2D sets: L0 wall → L4 out-of-
  focus foreground); 3D uses keyframed cameras (`keyCam`) with a slow push-in between beats.
- Transitions are motivated (match cut, seam, dip on a beat, whip with the action); never a
  plain cross-fade between unrelated scenes.

## 3. No repetition

- Each 3D world/set appears once per episode as a hero shot. A reuse must change **at least two**
  of: environment, perspective (scale/angle), action, purpose. Example in the AI-bubble flagship:
  data-hall corridor (opening only) vs single-rack macro with cooling (Ch. 4); campus from the
  ground during construction (opening) vs aerial power grid (Ch. 4); chips on a packaging line
  (opening) vs exploded single chip (Ch. 4).
- Keep a shot log in the storyboard: world, camera position class (aerial / eye / macro /
  top-down), action. Flag duplicates before rendering.

## 4. Look

- Premium hybrid: illustrated characters and sets + lit 3D (shadows, fog depth, rim/key/fill,
  emissive accents) + clean infographics. Never a slide: no centred title over a flat colour
  for more than a beat.
- Period-appropriate detail (1999 floor: CRT banks, flap boards, phones, paper tickets;
  1880s railway: 4-4-0 locomotive, balloon stack, wooden freight cars).
- Grade by meaning: warm/prosperous vs cold/abandoned; boom amber vs crash red.
- Explanations keep chart/diagram clarity: labels legible at 540p, colour legend on first use,
  close-ups for each stage of a mechanism, then an overview to show the whole system.

## 5. Checklist before asking for approval

- [ ] Every beat keyed to its word (section 1 audit done)
- [ ] No empty or static frame > 2 s while narration is running
- [ ] Characters: rigged, varied, acting with props; expressions match the beat
- [ ] ≥ 3 parallax layers or a moving 3D camera in every shot
- [ ] No repeated hero world/set without two changes (shot log checked)
- [ ] Text: ≥ 34 px labels at 1080p, caption band (y ≥ 880) clear, sources on data
- [ ] Hypotheticals, estimates and forecasts labelled on screen
- [ ] Motion render of each priority sequence watched; compared with the previous version
- [ ] Remaining limitations written down for the approval report
