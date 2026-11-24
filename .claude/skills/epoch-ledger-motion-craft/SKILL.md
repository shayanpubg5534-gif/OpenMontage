---
name: epoch-ledger-motion-craft
description: Motion-design craft and helper library for The Epoch Ledger documentaries — use when writing scene briefs, building or revising Epoch Ledger scenes (composition, kinetic type, diagrams, data, isometric, maps, 3D on CPU, transitions, end screen) or running layout QA. Not for other channels or generic web animation.
---

Read `skills/creative/epoch-ledger-motion-craft.md` (the full guide) and apply it together with
`epoch-ledger/QUALITY.md` and `skills/creative/epoch-ledger.md`. Reusable code:

- `epoch-ledger/kit/motion.js`: bundled into every composition: `MOTION` tokens, `mReveal`,
  `mWordsAt`, `mDrawOn`, `mBoil`, `mDiagram`, `mFocus`, `mFlow`, `mCount`, `mBars`, `mLine`,
  `mAmbient`, `mParallax`, `mPush`, `mStutter`, `mEndScreen`.
- `epoch-ledger/kit/motion.py`: `ktext`, `iso`, `iso_box`, `iso_grid`, `world_map_svg`,
  `projection`, `route_path`, `diagram_node`, `diagram_edge`, `endscreen_html`.
- `epoch-ledger/kit/three_kit.js` (opt-in head script): `ELK3D.keyCam`, `surface`, `flowAlong`,
  `flowField`, `shadowFollow`.
- QA: `node epoch-ledger/scripts/layout_check.mjs WS/index.html --start a --end b`.
- Reference composition: `python epoch-ledger/scripts/motion_demo.py WS`.

Timing rules are flexible guidelines. Ambient life and depth are part of the look. There is no
logo intro. No paid APIs and no extra rendering engines.
