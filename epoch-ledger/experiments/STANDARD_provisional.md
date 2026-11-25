# The Epoch Ledger — production standard (PROVISIONAL, for the A / A′ / B comparison)

Status: provisional. Written for the controlled comparison approved on 2026-11-25. It does **not** yet replace
`epoch-ledger/QUALITY.md`, the skill guides or the plan validator; it becomes authoritative only after approval.
It resolves the conflicts found in the audit and turns rules of taste into guidance.

## 1. What we make

Professional animated financial documentaries: accurate, understandable, visually engaging, and sustainable to
produce. The viewer should understand what is happening, why, and what follows, and should be able to follow most of
the story with the sound off.

## 2. Hard requirements (objective; these fail a scene)

1. **Facts and figures.** Sourced facts are correct. Illustrative figures for fictional companies are labelled
   illustrative, and every number on screen comes from one `kit/finstate.Ledger`, so counters, piles, charts and
   documents agree.
2. **Disclosure.** Fictional companies and people are labelled as fictional at their first appearance in a sequence.
3. **Captions.** Captions are always readable. Nothing important sits in the caption band (y ≥ 880 at 1080p), and no
   on-screen text collides with captions or other text (`scripts/layout_check.mjs`).
4. **Continuity.** A character keeps one look, an object one design, and an indicator one meaning and scale within a
   sequence.
5. **Technical quality.** Renders are deterministic, with no black, flashing or frozen frames caused by errors
   (automated frame scan), clean audio levels, and the approved narration voice and caption style.
6. **Meaning before design.** Each passage has a written brief stating what happens, why, and the consequence,
   before any scene code is written.

## 3. Creative principles (guidance; the director decides)

- **Concepts, not words.** Group the narration into concept beats. Within a beat, choose the few *key moments*
  whose timing matters (a reveal, a decision, a number, a consequence) and land those precisely on the words that
  name them. Everything else may anticipate the words, follow them, or carry over a passage. Word-level locking is
  a tool for emphasis, not a rule.
- **Choose the right way to explain.**
  - Show people acting when the idea is an action (paying, signing, installing).
  - Use a document, ledger or chart when the idea is a quantity.
  - Use a metaphor only when it makes the idea easier, and do not reuse it by default.
- **Pacing serves comprehension.**
  - Hold a composition while it is still telling the viewer something, and change it when the idea changes.
  - Rapid montage is fine when the content is a montage; a still hold is fine when the viewer needs to read or
    feel something.
  - There are no fixed shot lengths or cut quotas.
- **Composition and camera.** One clear focal point at a time, a readable information hierarchy, and camera moves
  with a motive (reveal, follow, emphasise). Vary shot sizes because the story needs it, not to fill a quota.
- **Life on screen.** Ambient movement is welcome when it supports the world. Neither it nor constant motion is a
  substitute for meaningful action, and a deliberate stillness is a valid choice.
- **Characters act with intent.** Eyes lead the head, weight shifts with the stance, hands make contact with
  objects, characters react to each other, and actions have anticipation and follow-through.
- **Depth of treatment by importance.** Not every company or machine needs an introduce → operate → transact
  treatment. Spend detail where the story's understanding depends on it.

## 4. Tools (capabilities, not formulas)

`COMPONENTS.md` lists what exists: scene3d sets, plates, rig v3 with IK and props, finmech, money, explain,
diegetic, lightfx, motion.js, finmotion and R3. Use what serves the scene, and build new parts when nothing fits.

## 5. Checks

- **Automated:** layout (text), frame scan (black, flashes, frozen frames, determinism), loudness, ledger
  consistency, and timing study (cuts, holds, motion pace) as information.
- **Not evidence of creative quality:** motion frequency, cut counts, camera drift, blinking and particles.
- **Final judgement:** watch the render, with and without sound.

## 6. Supersedes (once approved)

| Current rule | Replaced by |
|---|---|
| `QUALITY.md` §2 / skill step 7: "every object and action starts on the word" | §3 concepts and key moments |
| `QUALITY.md` §1: the mandatory introduce → operate → transact for every entity | §3 depth by importance |
| `QUALITY.md` §2 / §3: "no unexplained static periods", "keep the world alive in every shot" | §3 life on screen |
| `QUALITY.md` §3 and skill step 7: rig v2 for characters | rig v3 (`kit/rig3.py`, `kit/rig3.js`) |
| `QUALITY.md` §6: "procedural Three.js is the default" | the tool chosen per scene in the brief |
| `scene_plan.py`: MIN_SHOT / MAX_CUTS_PER_10S / MAX_HOLD as hard failures | warnings, with a written reason when exceeded |
| `scene_plan.py`: the self-declared "consulted guides" field | removed. The brief's meaning, key moments and choices are the evidence. |
