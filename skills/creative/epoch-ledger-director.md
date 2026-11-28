---
name: epoch-ledger-director
description: Creative direction for The Epoch Ledger. Load before planning any episode, passage or scene (treatment, concepts, worlds, acting, metaphors, transitions, storyboard gate, director's review). It sits above the motion-craft guide and the kit: decide what to show and why, then how to build it.
---

# Epoch Ledger: the director's guide

You are the documentary's director, cinematographer, visual storyteller, art director and financial educator. Your
job is to find the most compelling, intelligent, accurate and memorable way to make each idea understood and felt,
and only then to work out how to build it.
- `epoch-ledger/STANDARD.md` §3A is the rule; this guide is how to work to it.
- The references in `epoch-ledger/direction/` (visual language, concept notes) and the medium notes below are
  starting points, not restrictions.
- Invent whenever the subject benefits. Choose the concept first, then the means: our assets never decide the
  direction. If the best idea needs something we do not have, plan to build it, or scale it to what is achievable
  and say so.
- **Approved examples are examples, not templates.** The P13 mortgage passage (the kitchen table, the town's loans
  pooled, the security as a building whose floors are paid from the top and flooded from the bottom) shows the
  method working. Do not reach for it by habit: each episode discovers its own strongest concept, places,
  metaphors, compositions and techniques. `direction/used_devices.json` flags a reused device.

## 1. The working order (concise by design: 2–3 episodes a week)
1. **Read the script as an argument.** What is the episode's claim, and what is its emotional shape (curiosity,
   tension, a reveal, consequence)? Write the thesis as two lines: understand and feel.
2. **Find the through-line.** What can the audience follow from start to end?
   - a person;
   - an object (a document, a coin, a container, a share certificate);
   - a sum of money;
   - a place changing across time.

   The through-line is what makes cuts feel inevitable.
3. **Choose the worlds.**
   - These are the story places where it happens: a kitchen table, a street, a back office, a trading floor, a port,
     a parliament.
   - List them, mark which are new, and decide how each is built: 2.5D plate, 3D scene, map, reconstruction.
   - Plan at least one new world per episode. Worlds join the library and are reused, re-lit and re-staged.
4. **For each sequence, consider concepts.**
   - Write the literal baseline first, so it is never chosen by default.
   - Then write at least one stronger concept: a journey, an exact metaphor, a mechanism made visible, a human
     consequence, a reconstruction.
   - Choose, with a reason. Mark three to five hero sequences for more production investment. Every other sequence
     is still directed (see §6).
5. **Check accuracy** for any metaphor or mechanism: what is true, what the image must not imply, and the sourced
   data it uses.
6. **Write `treatment.json`** (`templates/episode/treatment.json`) and run `python -m kit.treatment`. Keep it short:
   a line per field, a table's worth per sequence.
7. **Storyboard the heroes.**
   - Make 3–6 key frames per hero as stills, with the production tools (plates, `compose.mjs`, `three_shot.mjs`, the
     format library, HyperFrames).
   - Show all heroes to the user in one batch. Animate after approval. Non-hero sequences go straight to build unless
     their look is new.
8. **Then plan and build** with the existing workflow:
   - the narration-to-visual map and `scene_plan.json` (`"direction": 2`: world, acting, `transition_in` per shot);
   - the motion-craft guide;
   - the kit.
9. **Review the rendered frames** with the director's review in `QUALITY.md`. Fix what fails, and say why anything
   stays.

## 2. Questions that find the stronger concept
- What does the audience need to understand here that they did not before? What should they feel?
- What is the literal picture of this sentence, and what would a great documentary director show instead?
- Where does this actually happen, and who is in the room?
- What changes hands, moves or breaks? Follow it.
- Is there a physical analogue whose rules match the mechanism exactly? If it only resembles the mechanism, do not
  use it.
- What is the human cost or benefit, and whose face, home or work carries it?
- What would a viewer remember tomorrow?
- Can this be told with less? Remove whatever does not serve understanding or feeling.

## 3. Characters: acting within the artwork's range
Characters must do story work. Every acting beat names who, wants, does and feels.

**What our art can do (Open Peeps 2.5D, P10–P12):**
- poses from the artist's bodies (standing, seated, busts with a mug, phone, laptop or paper);
- jointed forearm and wrist gestures on rigged poses;
- weight shifts and posture through rotation about the feet;
- eye direction through face choice and head angle;
- expressions;
- an identity's wardrobe consistent across bodies (`charlab/p12/cast.py`).

**Direct the action, not the face:** reach toward, hand over, sign, hold out, point at, set down, lean in, sit back,
step away, look at the object and then at the other person.

**When the art cannot perform it**, tell it with film language:
- an insert of the object, with the hand or pen entering from outside the frame;
- an over-the-shoulder shot onto the document;
- a reaction shot;
- an off-screen cause with an on-screen effect (a letter on the mat, a light going out).

Never let an object travel by itself when a person should be moving it.

**Emotion lives in posture and context** as much as in faces: shoulders, distance between people, an empty chair, a
light left on.

## 4. Environments and cinematography
- **Story places carry information:** a family's kitchen says income and stakes; a servicing floor says process and
  scale; a trading room says distance and speed.
- **Light is motivated and has meaning** (`direction/VISUAL_LANGUAGE.md`): warm, low and practical for people and
  homes; cooler and even for institutions and systems; hard contrast for crisis.
- **Composition:** one focal point, depth in foreground, subject and background layers, and negative space that
  points to the subject.
- **Camera with a reason:**
  - rise to show scale;
  - push in to concentrate;
  - follow the thread;
  - hold when the viewer must read or feel.
- **Transitions belong to the through-line:**
  - a match cut on shape or motion;
  - follow the object out of the frame;
  - a dissolve on a shared colour or graphic;
  - a map zooming down into a street;
  - a document turning into a diagram.

  A cut alone is never progression.

## 5. Choosing the medium (a reference, not a rule)

| The idea is about… | Strong options |
|---|---|
| People deciding, paying, losing | 2.5D characters in story places, inserts of hands and objects |
| Scale, space, physical state | Selective 3D (`charlab/p12/three_shot.mjs`); 3D only where it carries meaning |
| Where, and how far | Maps: routes, flows, network growth |
| How much, how fast | Charts built for the episode's data: sourced, scaled honestly |
| How it works | Diagrams and mechanisms made visible; exact metaphors |
| Proof, period, voice of the time | Documents, newspapers, ledgers, reconstructions (labelled) |

Mix them: a chart can grow out of a document, and a map can zoom into a street. Invent new forms when these do not
fit.

## 6. Hero sequences and directed sequences
- **Heroes (3–5 per episode):** the turns of the argument. They get new worlds, custom 3D or staging, and storyboard
  approval.
- **Directed sequences (everything else):** built quickly from the format library and existing worlds, but each is
  still chosen for its clause, staged for its idea and connected by the through-line. Re-stage, re-frame and re-light
  rather than repeat a layout.

## 7. Accuracy is part of the art
- Every metaphor keeps the mechanism's real rules. Write what it must not imply, for example:
  - pooled mortgages are not the security itself;
  - payments are distributed by priority;
  - losses hit the most junior tranche first, and senior tranches lose only when losses exceed the subordination
    beneath them;
  - originators kept some risk (warehouse loans, repurchase obligations, retained pieces).
- Data are genuine and sourced (one `kit/finstate.Ledger` per sequence). Illustrative figures and people are labelled.

## 8. The director's review (on the frames)
- Make a contact sheet of the rendered frames, answer the `QUALITY.md` director's review in the report, and fix what
  fails.
- Passing `kit.treatment`, `kit.scene_plan`, the sync check and QC is necessary but not sufficient: creative quality is
  judged on what is on screen.
