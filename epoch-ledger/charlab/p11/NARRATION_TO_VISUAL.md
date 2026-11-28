# Narration-to-visual planning (P11 method; experimental, opt-in)

The narrator carries the argument. The picture must **show** each idea at the moment it is said. A caption alone does
not count, and neither does a cut alone. This method works for any finance, economics or history subject: the map is
the film's data, and `visual_map.py` is the method.

## Steps
1. **Record the narration first.** Narration is voice-over, with Whisper word timestamps (`narrate.py` →
   `artifacts/words.json`).
2. **Clauses.** `visual_map.py` splits the narration at the narrator's own punctuation. Every clause must be *shown*,
   either by a change or by the composition already on screen (a `held` event; STANDARD §3B). Synchronisation is for
   meaningful changes: a new visual per phrase is not the goal.
3. **Concepts.** For each clause, list the ideas it states and anchor each one to the word that carries it.
   Examples: "vault", "$10,000", "credits", "tariff", "1873", "the run on the bank".
4. **Events.** For each concept, decide how it is *shown*:

   | Medium | Use it when |
   |---|---|
   | `character-action` | A person does the thing (types, reads, hands over, reacts with consequence) |
   | `prop` | An object moves or changes (a form slides across, a stamp lands) |
   | `insert` | A detail close-up makes a small decisive fact legible (the amount on the form) |
   | `3d` | Space, scale or a physical state matters (a sealed vault, a crowded trading floor, a port) |
   | `diagram` | A mechanism or a cause and effect (balance-sheet entries, money supply, a flow) |
   | `graphic` | A short label or number tied to something on screen |
   | `cut` | Only as the first event of a shot that brings something new |

   Anchor each event to its word with a small offset (default window −0.35 s to +0.30 s). Event times are derived from
   the word timestamps, so a re-recorded narration re-times every visual automatically.
5. **Shots.** Group events into shots. Each shot declares what it `introduces`: context, information, action or
   consequence. A shot whose only event is the cut is not progression.
6. **Check** (`visual_map.py check`):
   - Errors:
     - a clause with no visual;
     - a concept not depicted, or depicted more than `concept_window` (0.6 s) from its word;
     - an offset outside the window;
     - shots that do not tile the film, or that introduce nothing.
   - Warnings:
     - a slow first visual after a clause or a cut;
     - more than 4 cuts per 10 s.
   - Pacing (load, reading time with captions, competing focal points, composition durations by pace) is checked by
     `python -m kit.pacing plan MAP.json` and, on the render, `python -m kit.pacing film MAP.json OUT.mp4`. A long,
     developing composition is good pacing, not a gap.
   - The checker also writes the timestamped table (`--table`) and the resolved times (`--resolved`).
7. **Build from the resolved times.** Character performance, 3D camera keys and graphic tweens all read the same
   resolved events. In P11: `prepare.py`, `render_vault.sh` and `sequences/p11_test.py`.
8. **Inspect the render** (`visual_map.py inspect`).
   - For each event it measures when its screen region actually changes in the final MP4 and compares that with the
     plan.
   - Cuts are found as frame-to-frame spikes. Other changes are measured against a reference frame inside the event's
     own shot, so fades and eased moves are caught.
   - An event is in sync within ±0.2 s. This complements the technical QC (`qc.mjs`).

## Directing rules this enforces
- **Show what the narration denies or asserts.** "No vault is opened" shows the vault, shut. Negations need a picture
  of the unchanged thing.
- **Cause, then effect.** Show the action (typed entry), then the mechanism (two balance-sheet entries), then the
  consequence (a new deposit; deposits grow, cash unchanged).
- **Characters do story work.** Reading, typing and checking a balance carry the action. Idle blinking and nodding are
  life, not storytelling.
- **3D only where space or physical state is the point.** In P11 that is the vault. Elsewhere, cached 2.5D plates are
  cheaper and as clear.
- **Few cuts, each motivated.** P11 has 4 cuts in 16.5 s, and every shot carries a new idea.

## A non-banking example (railway mania, sketch)
Narration: "Investors poured money into new lines. Many were never finished."
- **Concepts:**
  - "poured" → money flowing in;
  - "lines" → track being laid;
  - "never" → an abandoned cutting.
- **Events:**
  - `diagram`: share subscriptions fill a bar on "poured";
  - `3d`: a crane-less cutting in a field on "lines", the camera moving along unfinished rails;
  - `graphic`: "abandoned" on "never", over rails that end in grass.
- **Shots:** S1 "information" (the money); S2 "consequence" (the unfinished line).

## Files
- `visual_map.py`: the method (clauses, resolve, check, table, inspect).
- `map_p11.json`: the P11 map, with 10 concepts, 23 events and 5 shots.
- `map_p10_as_delivered.json`: P10 described with the same concepts. The checker reports 5 semantic errors there,
  because the amount, the vault and the cash were captioned but not shown.
