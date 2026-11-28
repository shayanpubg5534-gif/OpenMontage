# The Epoch Ledger — production standard (authoritative)

This is the single source of creative and quality rules for every Epoch Ledger episode. Other documents point here.
Approved by the user on 2026-11-25. It supersedes the creative rules previously spread across `QUALITY.md`, the
skill guides, `/epoch-ledger`, `AGENT_GUIDE.md` and `config/production.json`. Those files now only point here, keep
the craft techniques, or hold machine settings.

**Precedence:**
1. §2, the hard requirements.
2. The user's direction for the episode.
3. §3, the creative principles, §3A, creative direction, and §3B, viewer comprehension and pacing.
4. Direction guidance in `skills/creative/epoch-ledger-director.md` (skill `epoch-ledger-director`) and its references in
   `epoch-ledger/direction/`; craft guidance in `skills/creative/epoch-ledger-motion-craft.md`. Both are references,
   not templates.
5. Machine settings in `config/production.json` (voice, captions, render, palette, motion tokens), which are
   defaults rather than creative rules.

## 1. What we make

Professional animated financial documentaries: cinematic visual storytelling combined with financial clarity.
Viewers should understand what is happening, why, and what follows, and should be able to follow most of the story
with the sound off. The standard sets principles and supplies capabilities. It does not prescribe a formula for
every scene.

## 2. Hard requirements (a scene fails without these)

1. **Facts and figures.**
   - Sourced facts are correct.
   - Illustrative figures (fictional companies, hypotheticals) are labelled illustrative on screen.
   - Every number in a sequence comes from one `kit/finstate.Ledger`, so counters, piles, charts and documents
     agree.
2. **Disclosure.** Fictional companies and people are labelled fictional at their first appearance in a sequence.
3. **Readable figures.** Important financial objects and numbers get enough screen space and reading time:
   - Key figures are at least about 48 px tall at 1080p, and at least 34 px for any text that must be read.
   - They stay on screen for at least about 1 s plus 0.3 s per word, at rest (not moving) for most of that time.
4. **Captions.**
   - The approved caption look: Inter 700 at 46 px, a navy box, the spoken word highlighted in gold, and spoken
     words at full brightness.
   - Captions stay readable, and nothing important sits in the caption band (y ≥ 880 at 1080p).
   - No text collisions (`scripts/layout_check.mjs`).
5. **Continuity.** Within a sequence, a character keeps one look, an object one design, and an indicator one meaning,
   scale and geometry.
6. **Technical quality.**
   - Every frame is a pure function of time: the determinism check passes.
   - No error-caused black, flashing or frozen frames.
   - Audio is clean, around −16 LUFS for narration with sound effects well below.
   - The approved Kokoro voice is used, with no background music.
   - All tools and assets are free and local: no paid APIs, and every asset licence is recorded.
7. **Meaning before design.** Each passage has a written brief (`meaning`: what, why, consequence) before any scene
   code.

## 3. Creative principles (guidance; the director decides)

- **Concepts and key moments.**
  - Group the narration into concept beats.
  - Within a beat, choose the few key moments whose timing carries meaning (a reveal, a decision, a figure, a
    consequence) and land those on the words that name them.
  - Other motion may anticipate the words, follow them, or carry across a passage.
  - Word-level locking is a tool for emphasis, not a rule.
- **Cinematic storytelling plus financial clarity.**
  - Show people and objects acting when the idea is an action: paying, signing, installing, money arriving.
  - Use an animated chart when a chart explains the financial mechanism better: comparisons, shortfalls, runways,
    growth, losses. Give it room and time to be read, and connect it to the story world: the same figures, the same
    colours, and a cut or move that motivates it.
  - Use a metaphor only when it clarifies something a literal image cannot, and do not reuse it by habit.
- **Composition and hierarchy.**
  - One focal point at a time.
  - Avoid overcrowded frames and unnecessary simultaneous movement: one primary action, with supporting motion that
    stays subordinate.
  - Vary shot sizes because the story needs it.
- **Pacing serves comprehension.**
  - Hold a composition while it still tells the viewer something, and change it when the idea changes.
  - Montage is fine when the content is a montage, and deliberate stillness is fine when the viewer must read or
    feel something.
  - There are no fixed shot lengths or cut quotas. The plan checker's pacing numbers are warnings that ask for a
    reason.
- **Camera.** Moves have a motive (reveal, follow, emphasise, connect two things). Otherwise the camera is steady.
- **Characters act like people.**
  - Intent shows through posture and weight, eyes leading the head, overlapping action, contact with objects and
    reactions to each other.
  - Narration is an independent voice-over, not character dialogue. Characters never lip-sync to the narrator.
    Mouths move only when the character has an explicit scripted line with an assigned speaking voice, and only for
    that line. Lip sync is off by default and opt-in per line (Rig v4 `say()`; the lab's `speech` track).
  - In narrated scenes the acting carries the moment: body language, subtle breathing, blinks, eye movements,
    expressions, meaningful gestures and interaction with the environment.
- **Depth of treatment by importance.** Spend operation and transaction detail only where understanding depends on
  it; there is no fixed treatment per company or machine.
- **Life on screen.** Ambient movement is welcome when it supports the world, but it never substitutes for
  meaningful action, and constant motion is not a goal.

## 3A. Creative direction (permanent; approved 2026-11-27)

We do not merely show what the narration says. For every idea we look for the most compelling, intelligent, accurate
and memorable way to make the audience understand it and feel it, then work out how to make it with our tools.

1. **Concept before implementation.**
   - Every passage starts from two questions: what must the audience *understand*, and what must they *feel*?
   - Then consider at least two concepts, one of them the literal baseline (written down so it is never chosen by
     default), and choose the strongest with a reason. The concept is chosen first and the means second.
2. **A through-line.**
   - Each sequence follows something: a person, an object, a sum of money, a place across time.
   - Transitions are motivated by that thread (match cuts, following the object, a move that connects two worlds),
     never by "next shot".
3. **Story places, not empty rooms.**
   - Scenes happen where the story happens: a kitchen table, a street, a servicing floor, a trading room, a port.
   - An abstract or empty space needs a reason, such as an isolated mechanism.
4. **Characters act with intent.**
   - Every character beat says what the person wants, does and feels.
   - The acting is physical and story-relevant: hand gestures, posture changes, object interactions, eye direction,
     weight shifts and emotional reactions. It does not rely mainly on head turns, blinks or mouths.
   - When the artwork cannot perform an action convincingly, framing tells it: an insert of the hands and the object,
     a reaction shot, or an off-screen cause with an on-screen effect.
   - Objects never move by themselves when a person should be moving them.
5. **Metaphors are exact.**
   - Use a metaphor when it explains what a literal image cannot. It must be accurate: it may not imply anything
     false about the mechanism.
   - Once introduced, it keeps its rules for the sequence, and it is not reused by habit across episodes
     (`direction/CONCEPT_NOTES.md` logs uses).
6. **Human consequence.**
   - Systems are connected to people. Every act ties the mechanism to someone it happens to, and data alone never
     ends an emotional beat.
7. **The right medium for each idea.** Choose by what the idea needs, not by what is available:
   - 2.5D illustration for people;
   - 3D for scale, space and physical state;
   - maps for geography;
   - charts for quantities;
   - diagrams for mechanisms;
   - documents for evidence;
   - reconstructions for period and place.

   Combine media, invent new ones, and build what is missing.
8. **Cinematic language.**
   - Composition has one focal point.
   - Light is motivated (the series' light language: `direction/VISUAL_LANGUAGE.md`).
   - Depth comes in layers.
   - Camera moves have reasons.
   - Continuity holds across cuts.
9. **Every element serves the story.** No spectacle for its own sake, no decorative motion, no filler. Ask of each
   element: what does this make the viewer understand or feel? If the answer is nothing, it goes.
10. **Every sequence is directed.**
    - Three to five hero sequences per episode may receive more production investment.
    - Every other sequence is still deliberately directed: no generic layouts, repeated two-shots or low-effort
      cards because a sequence is "not a hero".
11. **Rejected by default** (allowed only with a written reason):
    - the literal object in a void;
    - floating information cards as the main visual;
    - repeated two-shots;
    - decorative motion;
    - unmotivated cuts;
    - data with no human anchor;
    - repeating a previous episode's signature device.
12. **Creative freedom.**
    - The visual language, concept notes and medium guidance are references, not restrictions.
    - Invent new techniques, environments, compositions, transitions and metaphors whenever the subject benefits.
13. **Judged on the output.**
    - Creative quality is judged on the rendered frames and the watched film: the director's review in `QUALITY.md`.
    - Completed schema fields and passing tests show the thinking was written down, not that it is good.

## 3B. Viewer comprehension and visual pacing (permanent; approved 2026-11-28)

A viewer must understand the film comfortably on the **first viewing, at normal speed, without pausing**, while
listening to the narration and reading the captions. The goal is not the most visual change per second; it is the
most understanding, engagement and emotional connection. These are a director's principles, not a stopwatch: the
numbers below are guidelines adapted to each sequence, and checks of them are diagnostics, not proof.

1. **Comprehension over density.** A shot succeeds when its idea is understood, not when it changes on every
   keyword.
2. **Semantic coverage, not a new event per phrase.**
   - Every clause must be *shown*. But it can be served by the composition already on screen (a held composition) or
     by a change within it.
   - Synchronisation still matters for meaningful changes: what changes must change on its word.
3. **Develop, don't replace.**
   - Prefer progressive development within one composition (a line draws, a layer lights, a label arrives, the
     camera moves to the next detail) over a new scene.
   - Replace the whole picture when the place, time or idea changes.
4. **Cognitive load is the whole picture.**
   - Load comes from everything that asks for attention at once: new compositions, new elements, labels and captions
     to read, and motion.
   - Camera moves, rapid zooms, simultaneous animations, competing focal points and frequent internal changes all add
     load. Motion inside a scene is cheaper than a cut, but it is not free.
   - Calm the motion where the viewer must read or think.
5. **One step, one focal point at a time.**
   - Complex ideas are built in steps, each readable before the next.
   - New elements are staggered, so the eye knows where to look. Camera, light and colour lead it.
6. **Reading time includes the subtitles.**
   - Important text stays on screen at least `0.5 s + words ÷ 3` after it is fully revealed. This is a minimum
     estimate, not proof of understanding.
   - Supporting text is concise.
   - Mobile first: key text is at least 40 px at 1080p, labels are seven words or fewer, and normally no more than four
     lines of text are on screen besides the caption.
7. **Pacing adapts to the sequence.** Each sequence declares its pace, and the director adapts:

| Pace | Character | Typical duration of a composition |
|---|---|---|
| `hook` | opening energy: faster cutting allowed if nothing essential must be read | 1.5–4 s |
| `character` | natural, cinematic, room for performance | 5–8 s |
| `illustration` | a simple picture of one idea | 3–5 s |
| `diagram` | a financial diagram, developed progressively | 6–12 s |
| `mechanism` | a complex mechanism, step by step | 10–20 s when necessary |
| `emotional` | a cinematic moment that breathes | 5–10 s |
| `transition` | brief, nothing essential to read | 1–2 s |

   Films should not share one editing rhythm. Energy comes from motivated motion, performance and progressive
   reveals, not from replacing pictures.
8. **Preserve visual richness.**
   - The standard is not a reason to simplify into slides. Keep cinematic camera direction, detailed environments,
     expressive acting, meaningful 2D, 2.5D and 3D animation, animated charts, maps and mechanisms, motivated
     transitions, metaphors and human consequence.
   - Keep a format (a world map, say) when it adds real understanding. Do not drop it only to pass a count.
9. **Let moments breathe.** Emotional beats and reveals hold, kept alive by quiet motion: a slow push, breath, light.
10. **Script for comprehension.**
    - At the treatment stage, each sequence's load is estimated against its narration.
    - When the narration is too short for what must be understood, lengthen or simplify the script (see the concept
      notes for accuracy). Never cram the pictures to fit.
11. **Judged at normal speed.**
    - The automated pacing report (`kit/pacing.py`) is a diagnostic.
    - Comprehension is judged by watching the film at 1×, start to finish, without pausing. The director does this
      first, then the user (QUALITY.md, "First viewing").

## 4. Capabilities

`epoch-ledger/COMPONENTS.md` indexes the kit:
- scene3d sets and cached plates (`kit/plates.py`);
- rig v3 with IK, props, eyes and stances;
- `money`, `explain` (charts), `finmech`, `diegetic`, `lightfx`, `motion.js`, `finmotion.js`, `R3` and the Ledger.

Use what serves the scene, and build new parts when nothing fits (then index them).

## 5. Process

1. **Treatment** (§3A). One concise `treatment.json` per episode:
   - thesis (understand, feel), emotional arc, through-line, worlds, motifs and signature device;
   - per sequence: the concepts considered (including the literal baseline), the chosen concept and why, the
     accuracy notes for any metaphor, the human anchor and the motivated transitions.

   Checked by `python -m kit.treatment`, which also writes `treatment.md` for reading. Each sequence also names its
   `pace` (§3B) and the `steps` it must teach; the checker warns when the narration is too compressed for them.
2. **Storyboard gate.** Key frames of the hero sequences, as stills made with the production tools, are approved in
   one batch before animation. Directed sequences that are not heroes need no storyboard gate unless the look
   changes.
3. **Brief.** For each passage, write the meaning, the key moments, and the shot ideas with a reason for each.
   Shot plans live in a `scene_plan.json` checked by `kit/scene_plan.py`, which reports errors for objective
   problems and warnings for pacing. With `"direction": 2`, shots also carry `world`, `acting` and `transition_in`.
4. **Build** with the kit and render previews (`scripts/render.py range` / `render`).
5. **Check:**
   - Automated, by `scripts/qc.mjs`: determinism, frame scan (black, flash, frozen), loudness and timing study
     (information only), plus `scripts/layout_check.mjs` for text.
   - Pacing (§3B): `python -m kit.pacing plan MAP.json` before building and `python -m kit.pacing film MAP.json OUT.mp4`
     after rendering. These are diagnostics of load and reading time, not proof of comprehension.
   - **Not evidence of creative quality:** motion frequency, cut counts, camera drift, blinking or particles.
6. **Watch** the render at normal speed from start to finish, with sound and muted. Run the first-viewing review and
   the director's review (`QUALITY.md`), then ask for approval.
