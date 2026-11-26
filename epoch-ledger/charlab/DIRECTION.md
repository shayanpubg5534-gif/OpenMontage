# Narration-driven direction (experimental production guideline)

Status: **experimental**. Recorded in M5 at the producer's request as a permanent documentary principle. It applies
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
- **Mix the vocabulary.** Use the right form for each beat: 3D scenes with characters for place and people; object and
  document close-ups for evidence; animated diagrams, timelines and charts for mechanisms and numbers.
- **Transitions carry meaning.** A transition connects two ideas. Examples: a camera push into the shop ends on the
  ledger; the ledger's date column becomes the timeline axis; the gap on the timeline becomes the cash chart; the chart's
  zero line dissolves into the bank meeting. No arbitrary wipes.
- **Lip sync only for speech.** Characters' mouths move only when that character speaks their own line on the
  soundtrack. Third-person narration never drives a mouth. Narrated scenes use acting (look, posture, gesture, expression).
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
5. Does anyone on screen speak? If not, no mouth motion.
