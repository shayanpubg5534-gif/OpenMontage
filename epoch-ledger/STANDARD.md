# The Epoch Ledger — production standard (authoritative)

This is the single source of creative and quality rules for every Epoch Ledger episode. Other documents point here.
Approved by the user on 2026-11-25. It supersedes the creative rules previously spread across `QUALITY.md`, the
skill guides, `/epoch-ledger`, `AGENT_GUIDE.md` and `config/production.json`. Those files now only point here, keep
the craft techniques, or hold machine settings.

**Precedence:**
1. §2, the hard requirements.
2. The user's direction for the episode.
3. §3, the creative principles.
4. Craft guidance in `skills/creative/epoch-ledger-motion-craft.md`.
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

## 4. Capabilities

`epoch-ledger/COMPONENTS.md` indexes the kit:
- scene3d sets and cached plates (`kit/plates.py`);
- rig v3 with IK, props, eyes and stances;
- `money`, `explain` (charts), `finmech`, `diegetic`, `lightfx`, `motion.js`, `finmotion.js`, `R3` and the Ledger.

Use what serves the scene, and build new parts when nothing fits (then index them).

## 5. Process

1. **Brief.** For each passage, write the meaning, the key moments, and the shot ideas with a reason for each.
   Shot plans live in a `scene_plan.json` checked by `kit/scene_plan.py`, which reports errors for objective
   problems and warnings for pacing.
2. **Build** with the kit and render previews (`scripts/render.py range` / `render`).
3. **Check:**
   - Automated, by `scripts/qc.mjs`: determinism, frame scan (black, flash, frozen), loudness and timing study
     (information only), plus `scripts/layout_check.mjs` for text.
   - **Not evidence of creative quality:** motion frequency, cut counts, camera drift, blinking or particles.
4. **Watch** the render with sound and muted, then ask for approval.
