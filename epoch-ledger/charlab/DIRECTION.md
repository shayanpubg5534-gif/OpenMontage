# Narration-driven direction (experimental production guideline)

Status: **experimental; a permanent production principle subject to final approval.** Recorded in M5 at the producer's request and reconfirmed at the M5 review. It applies
to all character-lab work now and is meant to be merged into the production guidelines (`epoch-ledger/QUALITY.md`,
`skills/creative/epoch-ledger.md`) once the character system is approved. Until then, production docs are unchanged.

## The principle

Every visual is designed around what the narrator is saying at that moment. The picture shows the thing the words
name, when the words name it. A scene changes because the story moved on, never because a timer ran out.

- **Show the subject.** When the narration talks about a place, a person, an object or a number, that is what is on
  screen. If it talks about a bakery, the shot is a bakery that reads as a bakery: a display case, bread, an oven, a till.
  A repurposed office or bookshelf does not count.
- **Show the mechanism.** When the narration explains how something works (payment terms, a cash gap, a loan), make
  the mechanism visible: an animated timeline, a flow, a diagram with cause and effect. Avoid generic B-roll.
- **Show the consequence.** When it says what happened as a result, show the result: a balance falling through zero,
  a document stamped, a face reacting.
- **Key to words, not durations.** Animation beats are tied to the timed words (Whisper word timestamps), e.g. the
  twelve monthly profits tick in across "every month", and the balance line crosses zero on "dry". No fixed shot lengths.
- **Characters appear when they serve the story.** Documents, animated charts, diagrams, maps, objects, environments
  and financial mechanisms appear whenever they communicate the narration better than a person would.
- **Camera-angle changes alone are not visual variety.** Cutting between angles of the same room while the narrator
  explains something else does not count as showing it.
- **Mix the vocabulary.** Use the right form for each beat: 3D scenes with characters for place and people; object and
  document close-ups for evidence; animated diagrams, timelines and charts for mechanisms and numbers.
- **Transitions carry meaning.** A transition connects two ideas. Examples: a camera push into the shop ends on the
  ledger; the ledger's date column becomes the timeline axis; the gap on the timeline becomes the cash chart; the chart's
  zero line dissolves into the bank meeting. No arbitrary wipes.
- **Narration is a voice-over, not dialogue (permanent standard).** Characters never lip-sync to the narrator; the
  narration track never drives or times a mouth. Narrated scenes are acted: body language, subtle breathing, blinks,
  eye movements, restrained expressions, meaningful gestures and interaction with the set and props.
- **Lip sync only for scripted dialogue.** A mouth moves only for an explicit line the script gives that character,
  voiced with that character's own assigned voice, and only over that line. Lip sync is opt-in per line (an actor
  `speech` entry) and off by default; the tools stay available but are not used in narrator-only scenes.
- **Figures are honest.** Illustrative financial figures are labelled as illustrative on screen or in the script, and
  come from one internally consistent model (one source file per story) rather than being typed into scenes.
- **Captions follow the voice.** Gold captions show what is being said, narration and dialogue alike.

## How it is done in the lab (M5)

| Step | Tool |
|---|---|
| Script: narration lines (third person) plus any character dialogue | `projects/<ep>/story/script.json` |
| Narration voice, word timing, caption pages | `scripts/narrate.py` (production, read-only; Kokoro + faster-whisper) |
| A character's own line: voice, word timing, viseme track | `charlab/lipsync.py` (Kokoro voice per character) |
| Dialogue placed between narration lines; beat and word timeline | `charlab/splice_dialogue.py` → `artifacts/timeline.json` |
| 3D shots keyed to beats (performance, camera, `speech` track) | `charlab/motion/demos/*.json` |
| 2D storytelling scenes keyed to words (`W("dry")` → time) | `charlab/sequences/*.py` (`scenes(T)`) |
| One composition: several 3D layers + 2D scenes + captions + audio | `charlab/hf_sequence.py` → HyperFrames `render.py` |

## Checklist for each beat

1. What does the narrator say here, in one phrase?
2. What must the viewer *see* to understand it: a place, a person, an object, a mechanism or a consequence?
3. Which word is the beat keyed to?
4. How does the previous picture lead into this one?
5. Does a character have a scripted line with an assigned voice? If not, no mouth motion: act the beat instead.
