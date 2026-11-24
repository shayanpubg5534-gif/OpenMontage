---
description: Produce or revise an Epoch Ledger documentary episode (finance/economics/history) in the approved pilot style — hand-authored vector characters, HyperFrames + Three.js, Kokoro narration, Whisper captions, scene-cached 1080p30 render.
argument-hint: [episode topic or slug, plus what to do]
---

Read `AGENT_GUIDE.md`, then `skills/creative/epoch-ledger.md` (pre-approved decisions, episode workflow, review checklist) and `epoch-ledger/README.md` (series bible, kit layout, render workflow), then do the work described below.

- Run it on the `animation` pipeline in atelier mode with `render_runtime: "hyperframes"`; log the pre-approved decisions from `epoch-ledger/config/production.json` in `decision_log`.
- New episode: `python epoch-ledger/scripts/new_episode.py "<Title>"` → write `script.json` + `art-direction.md` → `scripts/narrate.py` → `build.py` → lint + snapshot → `scripts/render.py`.
- Reuse the kit (`kit/characters.py`, `kit/sets.py`, `kit/vault3d.js`, `kit/helpers.js`, `kit/captions.py`); author every scene fresh and key it to narration word times.
- Revisions: change only the affected scene and re-render with `scripts/render.py` (cached chunks are reused). Never re-render the whole film for a one-scene change.
- Targets: 2–3 episodes/week, 8–10 min (12–13 min only when depth or context requires it; never filler); powerful hook, no logo intro; priorities are visual quality, factual accuracy, storytelling, retention.
- Keep 1920×1080, 30 fps, yuv420p, no watermark by default; 1440p only on request (`EPOCH_RESOLUTION=1440p`). Kokoro bm_george at 0.95. No paid APIs; avoid unnecessary AI usage. Ask before changing voice, runtime, caption engine or default resolution.

Request: $ARGUMENTS

Always apply `epoch-ledger/QUALITY.md` (four requirements: design detail, purposeful animation, word-level sync, semantic storytelling; scene brief before building; introduce → operate → transact): visuals start on the spoken word that names them (Whisper word times), no repeated hero shots, rigged acting, layered camera motion; watch a motion sample before asking for approval.
Check `epoch-ledger/COMPONENTS.md` before writing new components; keep it updated in the same commit.
When building or revising scenes, load `skills/creative/epoch-ledger-motion-craft.md` (motion language, composition, kinetic type, diagrams, data, isometric, maps, 3D on CPU, end screen) and use `kit/motion.js` / `kit/motion.py` / `kit/three_kit.js`; run `scripts/layout_check.mjs` on every changed range. Timing rules are flexible guidelines; keep ambient life and depth.
