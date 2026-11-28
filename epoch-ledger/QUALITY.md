# The Epoch Ledger — approval checklist

The rules live in **[`STANDARD.md`](STANDARD.md)**, the authoritative production standard. This file is the
checklist to run before asking for approval. It adds no creative rules of its own.

## Before building
- [ ] `treatment.json` written (STANDARD §3A) and `python -m kit.treatment episodes/<slug>/treatment.json` reports no
      errors: thesis, through-line, worlds, and per sequence at least two concepts (one the literal baseline) with the
      choice and its reason, accuracy notes for metaphors, a human anchor and motivated transitions.
- [ ] Hero storyboard key frames (stills made with the production tools) approved in one batch before animation
      (`python -m kit.treatment … --gate motion`).
- [ ] Brief written for each passage: `meaning` (what / why / consequence), key moments, and shot ideas with reasons
      (STANDARD §2.7, §5).
- [ ] `python -m kit.scene_plan PLAN.json` reports no errors. Warnings are answered with a reason or accepted
      knowingly.
- [ ] One `kit/finstate.Ledger` holds the sequence's figures (STANDARD §2.1).
- [ ] Each sequence's `pace` and `steps` are in the treatment, and the narration is long enough for them (no
      "too compressed" warnings left unanswered; STANDARD §3B.10).
- [ ] `python -m kit.pacing plan MAP.json` reviewed: compositions, reading time with captions, competing focal
      points and load per 10 s. Warnings are answered or accepted with a reason (§3B).

## Before asking for approval
- [ ] Facts are sourced; illustrative figures and fictional companies are labelled (§2.1–2.2).
- [ ] Key figures are big enough and on screen long enough to read (§2.3); frames are not overcrowded (§3).
- [ ] Captions are in the approved gold-highlight style, the caption band is clear, and `scripts/layout_check.mjs`
      is clean (§2.4).
- [ ] Continuity of characters, objects and indicators (§2.5).
- [ ] `node epoch-ledger/scripts/qc.mjs WS/index.html --video OUT.mp4` passes: determinism, no
      black/flash/frozen frames, loudness in range (§2.6).
- [ ] `python epoch-ledger/scripts/quality_gates.py epoch-ledger/episodes/<slug>/gates/gates.json --out DIR` passes
      (finance model and figures, figure timing and legibility, chart proportions, layout, contacts, frame scan), and
      the review page's contact sheets were checked against its checklist (grips, orientation, posture,
      intersections, foot sliding, continuity). Automated gates are necessary, not sufficient.
- [ ] Watched the render with sound and muted. The story is followable, and key moments land on their words
      (§3).

## First viewing (STANDARD §3B: watch at normal speed, start to finish, without pausing)
`python -m kit.pacing film MAP.json OUT.mp4` reports picture changes, holds, motion and reading time. It is a
diagnostic; these questions are answered by watching.
- [ ] Could a first-time viewer follow every sequence without pausing or rewinding?
- [ ] Was every important label readable while the caption ran, and did any picture vanish before it was understood?
- [ ] Did one thing at a time ask for attention, or did camera moves, animations and labels compete?
- [ ] Did complex ideas build one step at a time, with time to see the relationship before the next step?
- [ ] Did the pace suit each sequence (hook, character, diagram, mechanism, emotional moment, transition)?
- [ ] Did emotional moments breathe, and did the film stay alive and engaging (not a slideshow)?
- [ ] Is the narration long enough for what it explains, or was anything crammed?

## Director's review (judged on the rendered frames, not on fields or tests)
Review a contact sheet of the actual frames (and watch the film) against the treatment, then write a short answer to
each question in the report. A "no" needs a fix or a stated reason.
- [ ] **Concept:** does each sequence read as its chosen concept, and is the idea clear with the sound off?
- [ ] **Literal or meaningful:** is any sequence the literal baseline by default, an object in a void or a floating
      card standing in for a story?
- [ ] **Places:** are the environments story places, and does an empty space have a reason?
- [ ] **Acting:** do the characters do something story-relevant (hands, posture, objects, eyes, weight, reactions),
      or mostly turn heads and blink? Where the art cannot act, do inserts and reactions tell it? Does any object move
      by itself where a person should be moving it?
- [ ] **Through-line and transitions:** can the viewer follow the thread across cuts, and is every transition
      motivated?
- [ ] **Human consequence:** does each act connect the system to people?
- [ ] **Accuracy:** does each metaphor stay true to the mechanism (for example, pooling, issuance, payment
      distribution and loss allocation are not confused)? Are the data genuine and sourced?
- [ ] **Craft:** is there one focal point, motivated light, depth, readable figures and captions, and continuity?
- [ ] **Distinctness:** could this frame belong to last week's episode? Does it reuse a logged signature device?
- [ ] **Economy:** does every element serve the story? Is anything spectacle or filler?

## Asset policy (unchanged)
- Free local tools only, with no paid APIs; there is no background music.
- CC0 or public-domain assets come from the approved hosts: Poly Haven, ambientCG, Kenney, Quaternius and
  Wikimedia Commons (PD/CC0 checked per file).
- Every downloaded asset gets its own row in `kit/assets/LICENSES.md` in the same commit. A test checks the register.
- No engine migration without approval. OpenMontage + HyperFrames is the production backbone; OpenFilm techniques
  are adopted selectively, with attribution.
