---
name: epoch-ledger-director
description: Creative direction for The Epoch Ledger documentaries — use before planning or revising any episode, passage or scene: treatment (understand/feel, through-line, worlds, concepts incl. the literal baseline, exact metaphors, acting, transitions, human consequence), the hero storyboard gate and the director's review of rendered frames. Not for other channels.
---

Read `skills/creative/epoch-ledger-director.md` (the full guide) and apply it with `epoch-ledger/STANDARD.md` §3A and
`epoch-ledger/QUALITY.md` (director's review). References, not restrictions: `epoch-ledger/direction/VISUAL_LANGUAGE.md`,
`epoch-ledger/direction/CONCEPT_NOTES.md` (log metaphor and signature uses in `direction/used_devices.json`).

- Write `episodes/<slug>/treatment.json` (template `epoch-ledger/templates/episode/treatment.json`) and run
  `python -m kit.treatment episodes/<slug>/treatment.json` from `epoch-ledger/`; it writes `treatment.md`.
- Storyboard hero sequences as stills with the production tools; batch them for approval; then
  `python -m kit.treatment … --gate motion` must pass before animation.
- Then plan shots (`scene_plan.json` with `"direction": 2`, the narration-to-visual map) and build with the
  `epoch-ledger-motion-craft` skill and the kit.

Choose the concept first and the means second. Every element serves understanding or feeling.
