# P11 — Narration-driven visual storytelling (visual approval gate)

**Status:** experimental and opt-in (`epoch-ledger/charlab/p11/`). This is a controlled comparison with P10: the
**same narration audio and word timings**, re-directed so that every clause is shown.
- Preserved: P10 and all earlier versions.
  - P10's compositor is reused unchanged, apart from one backward-compatible option: a nod amplitude per nod, with
    two-element nods behaving exactly as before.
  - P10's sequence and deliverables are untouched.
- Unchanged: production defaults, Rig v4, `render.py`, the 1080p30 output, Kokoro narration, gold captions, and no lip
  sync.
- Free local tools only. Nothing was purchased or commissioned, and no paid APIs were used.

Date: 2026-11-27.

**Deliverables** (in `projects/charlab_p11/`; compressed copies in `charlab/evidence/p11_*.jpg`):

| File | Content |
|---|---|
| `p11_narrated_test.mp4` | 16.5 s, 1920×1080, 30 fps, the same narration as P10 |
| `frames/t*.png`, `frames_sheet.png` | Representative frames |
| `compare_p10_p11.png` | The same four narration moments in P10 and P11 |
| `narration_visual_map.md` | The timestamped narration-to-visual mapping (23 events) |
| `sync_report.json` | Semantic sync measured on the rendered film |

## 1. What changed on screen

| Narration (word times) | P10 showed | P11 shows |
|---|---|---|
| "A baker **asks** his **bank**" (0.1–1.5 s) | Two people standing; he gestures | The loan application slides across the desk on "asks"; the banker looks down at it and nods on "bank" |
| "for a **loan** of **$10,000**." (1.5–3.4 s) | The same two-shot; the amount only in the caption | Insert from above: the form reads LOAN APPLICATION on "loan"; **$10,000 is written as it is said**, underlined and marked REQUESTED |
| "**No vault** is **opened**," (4.2–5.4 s) | The banker smiles and nods | **3D vault**: the steel gate is shut and locked with a red SEALED tag. The camera moves in on the lock on "vault"; a status card reads *Sealed · not opened* on "opened" |
| "**no cash** changes **hands**." (5.8–7.3 s) | A cut to the banker's close-up | The camera moves past the lock to the **cash stacked inside**; on "cash", *The cash stays put*; on "hands", *✓ Untouched* |
| "The banker simply **records** the **loan** and **credits** his **account**." (7.9–11.4 s) | Banker close-up; a balance-sheet card | **She types on her laptop**; her screen opens on "records" and the entry is typed; *Loan to the baker +$10,000* (assets) on "loan"; *Baker's deposit +$10,000* (liabilities) on "credits"; *One loan, one deposit: both sides +$10,000* on "account" |
| "**10,000** **new** **dollars** now **exist**." (12.0–14.5 s) | Baker close-up; a counter | **He checks his phone**; his balance counts to $10,000 on "10,000"; *Money in the economy*: bank deposits grow by a new $10,000 on "new", vault cash *unchanged* on "dollars", *New money: created by the loan* on "exist"; he smiles |

- **Shots: 5, cuts: 4.** P10 had 3 shots and 2 cuts. Every shot introduces something:

  | Shot | Medium | Introduces |
  |---|---|---|
  | S1 | 2.5D two-shot | Context and action |
  | S2 | Insert from above | Information |
  | S3 | 3D vault | What does **not** happen |
  | S4 | 2.5D close-up with a screen | Action and mechanism |
  | S5 | 2.5D close-up with a diagram | Consequence |

- **Story actions instead of standing:** the form changes hands, the banker types, the baker checks his account. The
  artist's own bust bodies with a laptop and a phone carry these actions.
- **3D only where it adds meaning:** the vault. Space, bars and stacked cash make "sealed" and "untouched" physical.
  The rest is cached 2.5D.

## 2. The reusable planning method (`charlab/p11/visual_map.py`, guide `charlab/p11/NARRATION_TO_VISUAL.md`)
The method is not banking-specific: the map is the film's data, the tool is the method.

1. **Clauses** come from the narrator's punctuation in the Whisper word timestamps.
2. **Concepts.** The ideas each clause states are anchored to the words that carry them: "vault", "$10,000",
   "credits".
3. **Events.** Each visual event is anchored to a word plus a small offset (−0.35 s to +0.30 s). It declares its medium
   (character action, prop, insert, 3D, diagram, graphic, cut) and the concepts it depicts.
4. **Shots** must tile the film and say what each one introduces. A cut alone is not progression.
5. **`check`** reports errors and warnings:
   - errors: a clause that is not shown; a concept that is not depicted, or depicted more than 0.6 s from its word;
     an offset outside the window; gaps between shots; a shot with no stated purpose;
   - warnings: a slow first visual after a clause or a cut; long gaps with nothing new; more than 4 cuts per 10 s.
6. **Build from one timing source.** Character performance, the 3D camera keys and the graphic tweens all read the
   same resolved event times. Re-recording the narration re-times everything.
7. **`inspect`** checks the rendered MP4. It measures when each event's screen region actually changes and compares
   that with the plan (±0.2 s).

**The same checker, applied to both cuts:**
- **P11:** 5 clauses, 10 concepts, 23 events. **0 errors, 0 warnings.**
- **P10 as delivered** (`map_p10_as_delivered.json`): **5 semantic errors.**
  - The $10,000 amount, the sealed vault and the untouched cash were never depicted; they appeared only in the captions.
  - "Asks" and "new money" were shown 1.0–1.4 s away from their words.
  - Warnings: 2.8–4.6 s stretches with nothing new.

## 3. Semantic synchronisation (measured on the rendered film)
- **21 of 23 events change on screen within ±0.2 s of their planned word time.**
  - All 4 cuts land within 0.02 s.
  - The two outside the window are 0.23 s late and 0.21 s early (below).
- **Outside the window:**
  - e05, the amount being written: +0.23 s. The handwriting wipe needs about a quarter of its 0.6 s to show visibly.
    It is on screen while "$10,000" is being said (2.60–3.38 s).
  - e21, the vault-cash bar: −0.21 s. The measured change includes the diagram card fading in 0.1 s before it.
- **First explanatory visual:**
  - P11: 0.5 s (the application).
  - P10: about 8.5 s (the balance-sheet card); before that, only characters.

## 4. Performance (cold run of `run_p11.sh`; 4 vCPU, no GPU; caches cleared)

| Step | Wall time | Peak RSS |
|---|---|---|
| Plan: map check and resolve | 0.3 s | — |
| 4 set stills (two-shot, two close-ups, desk from above) + depth | 17.9 + 18.2 + 16.9 + 13.6 s, + 4 × 4.0 s | 1.4 GB |
| Cast and performance | 1.3 s | 0.1 GB |
| 2.5D shots S1, S2, S4, S5 (4 workers) | 10.8 + 8.3 + 16.6 + 19.2 s | 5.5 GB |
| **3D vault S3** (114 frames, procedural three.js, 2 workers) | **175.8 s** | 2.9 GB |
| HyperFrames build + render (graphics, captions, narration) | 1.0 + 83.1 s | 5.5 GB |
| **Total** (narration reused) | **399.0 s** | **5.5 GB** |

| | P10 | P11 | Change |
|---|---|---|---|
| Finished film, like for like (P10's 16.9 s narration step counted for both) | 249.9 s → 15.1 min per finished minute | 415.9 s → **25.2 min per finished minute** | +66% |
| Without the 3D shot | — | 240 s → 14.5 min per finished minute | About P10 |
| Share of the total | Characters 31%, HyperFrames 32% | 3D vault 44% for 23% of the screen time | — |

- **The cost increase comes from the one fully animated 3D shot.** The 2.5D path stays at P10's cost even with more
  shots and an extra camera set-up.
- **The vault in software WebGL:**
  - It costs about 2.5 s per frame at native resolution. Parallel workers do not help, because the renderer already
    uses all the cores.
  - Static shadow maps, a single shadowed light and simpler shading on the plain walls gave only small gains.
  - Rendering at 0.75 of the resolution and scaling up to 1080p cut it by about 30%, with no visible difference after
    the painterly pass (checked on crops).
- **Memory:** 5.5 GB peak, down from P10's 6.5 GB.
- **Estimated compute cost:**
  - Assumption: a 4-vCPU cloud machine at about $0.15–0.25 per hour.
  - On that basis: roughly **$0.06–0.11 per finished minute**. This is an estimate, not a quote.

## 5. Inspection and remaining limitations

**QC (`qc.mjs --video`):**
- Passed: no black frames, no flashes, no freezes, consistent opening.
- Cuts detected at 1.87, 3.97, 7.77 and 11.77 s, all planned.
- Loudness −16.1 LUFS, true peak −4.5 dBFS.

**Remaining limitations:**
1. **Hand-to-hand actions are limited by the art.**
   - The application slides across the desk, but the baker cannot reach down to push it: the elbow rig's clean range
     is −15° to +12°, and handing over would need about 35°.
   - Typing reads through head motion, the laptop and the on-screen entry, not through moving fingers.
2. **Wardrobe continuity:** the banker's close-up uses the artist's laptop bust (a navy shirt) rather than the blazer
   from the two-shot. The colour and the person carry across the cut; the garment does not.
3. **One artwork edit:** the artist's laptop carries a comic logo, covered with a plain patch in the lid's own colour.
4. **The vault is our own procedural 3D.** It is clean and clear but simpler than the bank set: no wear, no decals.
   Its banknotes are a generic fictional design, not real currency.
5. **Illustrative numbers:** the diagram's bar lengths are schematic. Only the $10,000 is from the narration. No vault
   figure is invented; the vault cash is labelled "unchanged".
6. **The S1 desk form** is a 2D card set in perspective on the plate. It reads at two-shot distance; a close look would
   show it is flat.
7. **Cost:** the 3D shot dominates render time. Use fully animated 3D only where space or physical state is the point.

## 6. Recommendation (for your decision)
- Adopt the narration-to-visual map (plan → check → build from resolved times → inspect) as the planning step for
  narrated passages.
- It turns your rule ("every meaningful clause must be shown, when it is said") into something checked before
  rendering and measured after.
- P11 shows the method on the same narration: the explanatory visuals arrive at 0.5 s instead of about 8.5 s, every
  stated idea is depicted on its word, and the 2.5D cost stays at P10 levels.
- P11 is not yet proposed as the final production implementation. Your review of pacing, the 3D vault's look and the
  screen and diagram design would come first.

## Reproducibility
```
epoch-ledger/charlab/p11/run_p11.sh [OUT.mp4] [WORKERS]       # cold, end to end; per-step timings in .runtime/charlab/p11/perf.jsonl
python3 epoch-ledger/charlab/p11/visual_map.py check  epoch-ledger/charlab/p11/map_p11.json --table MAP.md --resolved RES.json
python3 epoch-ledger/charlab/p11/visual_map.py check  epoch-ledger/charlab/p11/map_p10_as_delivered.json     # the P10 comparison
python3 epoch-ledger/charlab/p11/visual_map.py inspect epoch-ledger/charlab/p11/map_p11.json projects/charlab_p11/p11_narrated_test.mp4
.venv/bin/python -m pytest tests/epoch_ledger/test_charlab_p11.py
```
- Needs `.runtime/charlab/p8/src/open-peeps.fig` (CC0; not committed) and P10's narration (`projects/charlab_p10/`,
  produced by `run_p10.sh`).
