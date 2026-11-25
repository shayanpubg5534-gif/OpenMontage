# The Epoch Ledger — approval checklist

The rules live in **[`STANDARD.md`](STANDARD.md)**, the authoritative production standard. This file is the
checklist to run before asking for approval. It adds no creative rules of its own.

## Before building
- [ ] Brief written for each passage: `meaning` (what / why / consequence), key moments, and shot ideas with reasons
      (STANDARD §2.7, §5).
- [ ] `python -m kit.scene_plan PLAN.json` reports no errors. Warnings are answered with a reason or accepted
      knowingly.
- [ ] One `kit/finstate.Ledger` holds the sequence's figures (STANDARD §2.1).

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

## Asset policy (unchanged)
- Free local tools only, with no paid APIs; there is no background music.
- CC0 or public-domain assets come from the approved hosts: Poly Haven, ambientCG, Kenney, Quaternius and
  Wikimedia Commons (PD/CC0 checked per file).
- Every downloaded asset gets its own row in `kit/assets/LICENSES.md` in the same commit. A test checks the register.
- No engine migration without approval. OpenMontage + HyperFrames is the production backbone; OpenFilm techniques
  are adopted selectively, with attribution.
