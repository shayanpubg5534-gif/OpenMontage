# The Epoch Ledger — production kit

Reusable series kit for **The Epoch Ledger** (finance, economics and history documentaries):
the approved pilot's characters, set pieces, Three.js vault, caption style, narration settings
and render configuration, plus scripts that turn a narration script into a 1080p30 MP4.

It is a **series bible + engine, not a new pipeline** (same pattern as `ink-theater/`).
Episodes run on the `animation` pipeline with `render_runtime: hyperframes`, atelier
composition, and the decisions in `config/production.json`. The agent-facing method is
`skills/creative/epoch-ledger.md`; the slash command is `/epoch-ledger`.

Approved pilot: `episodes/how-banks-create-money/` ("How Banks Create Money", 31.6 s,
approved 2026-11-24). Its builder reproduces the approved composition byte-for-byte
(`APPROVED_INDEX_SHA256`, checked by `tests/epoch_ledger/`).

## Layout

| Path | What it is |
|---|---|
| `kit/characters.py` | Maya (walk / bust / phone poses) and the loan officer — outlined, two-tone shaded SVG rigs with blink lids and pivot-ready limbs |
| `kit/rig.py`, `kit/rig.js` | Jointed character rig v2 (elbows, knees, neck, props), varied crowd looks, pose library, natural walk, seeded ambient acting, expressions |
| `kit/motion.js`, `kit/motion.py`, `kit/three_kit.js` | **Motion kit**: kinetic type, draw-on, diagrams, focus/context, flows, counters, bars, ambient life, parallax, stutter, end screen; isometric, Natural Earth maps and routes; 3D camera keys, procedural surfaces, flow fields (guide: `skills/creative/epoch-ledger-motion-craft.md`) |
| `scripts/layout_check.mjs` | Text-collision QA over the timeline (no rendering) |
| `scripts/motion_demo.py` | 30 s reference composition showing every motion helper |
| `kit/data/` | Natural Earth country shapes (world-atlas, ISC; Natural Earth public domain) — `LICENSES.md` |
| `COMPONENTS.md` | **Component index** — every reusable character, set, overlay and 3D world with where it lives; check it first, update it with every new component |
| `QUALITY.md` | **Visual quality standard + checklist**, incl. mandatory word-level semantic sync and the no-repetition shot log |
| `kit/sets.py` | Bank street (layered parallax), loan office, credit gauge, ledger T-account, terminal keyboard, bokeh |
| `kit/vault3d.js` | Three.js vault: configurable camera "shots", coin stacks, pulsing lock, banknotes materialising from gold motes |
| `kit/helpers.js` | Timeline helpers: `blink`, `count`, `usd`, `walk`, `talk`, `stamp` |
| `kit/captions.py` | HyperFrames-native word-highlight captions, visually matching the approved Remotion caption pass |
| `kit/theme.css` | Palette, Fraunces/Inter type, base layout classes |
| `kit/assemble.py` | `Scene` + `assemble()` → a cache-friendly `index.html` (per-scene regions) |
| `config/production.json` | Narration, captions, render settings, palette (single source of truth) |
| `scripts/narrate.py` | Script lines → Kokoro narration → Whisper words → caption pages + SRT |
| `scripts/render.py` | Scene-cached chunk renders, previews, no-re-encode assembly |
| `scripts/vendor.sh` | Fetch GSAP, Three.js and fonts into a workspace |
| `scripts/new_episode.py` | Scaffold `episodes/<slug>/` + `projects/<slug>/hyperframes/` |
| `templates/episode/` | Starter `script.json`, `art-direction.md`, `build.py` |
| `episodes/<slug>/` | Episode **source** (script, builder, art direction, timing artifacts) — committed |

Generated media (narration WAV, renders, caches) lives in `projects/<slug>/` (git-ignored).

## Production targets (approved)

- **2–3 documentaries per week**, 8–10 minutes each; 12–13 minutes only when the topic needs
  deeper explanation, historical context or detailed storytelling. Never add filler.
- **Priorities:** visual quality, factual accuracy, storytelling, audience retention.
- **Output:** 1920×1080 at 30 fps by default; 2560×1440 optional (not default until benchmarked).
- **Cost:** free local tools only; no paid APIs; avoid unnecessary AI usage.
- Reuse kit components, but re-stage them so episodes never look repetitive
  (`skills/creative/epoch-ledger.md` → "Reuse without repetition").

## Series look (locked)

- **Palette:** ink `#14213d` · parchment `#f4ead5` · brass `#d4a24c` · ledger green `#2f7d5b` ·
  teal `#1f7a78` · coral `#e0603a` · sky `#9cc9e6` · outline `#1b2230`.
- **Type:** Fraunces 800/600 for display and numbers; Inter 700/500 for labels. Webfonts work
  in HTML, not SVG `<text>` — put text that must use the series fonts in HTML.
- **Illustration:** hand-authored SVG, 3 px `#1b2230` outlines, flat fills + one shadow tone +
  one highlight stroke. Layered sets with parallax (clouds → far → mid → hero → foreground).
- **Motion:** slow camera drift (scale 1.00↔1.10), `power3` camera, `back.out` label pops,
  `sine.inOut` limbs, `steps()` for typing, at least 3 easings per episode. Signature device
  appears in 1–2 beats only.
- **Composition rules:** start on the hook (no logo/title card); every scene's primary subject
  differs from its neighbours; keep key visuals above y = 880 (caption band); on-screen text
  adds meaning (numbers, labels) and never repeats the narration verbatim.
- **Narration:** Kokoro `bm_george`, speed 0.95, one TTS call per script line, edge silence
  trimmed, 0.30 s breaths, 0.10 s lead, 0.70 s tail, −16 LUFS.
- **Captions:** Whisper `small.en` word times, clause-level pages (≤ 6 words, never split a
  sentence's one-word tail), Inter 700 46 px, `#F8FAFC` text, `#f2c66d` active word with glow,
  `rgba(20,33,61,0.82)` box, 60 px from the bottom.
- **Output:** 1920×1080, 16:9, 30 fps, H.264 `yuv420p` (HyperFrames `looks` = CRF 16), AAC
  48 kHz, `+faststart`, no watermark. Optional 2560×1440: build with `EPOCH_RESOLUTION=1440p`
  (`kit.assemble(resolution="1440p")` sizes the root to 2560×1440 and zooms each top-level clip
  4/3 so vectors, text and the 3D canvas re-rasterise at full resolution; HyperFrames' `--resolution` upscale rejects the
  non-integer factor). `render.py` checks the output size against the composition.

## Workflow

```bash
python epoch-ledger/scripts/new_episode.py "The Fall of Bretton Woods"     # scaffold
# edit epoch-ledger/episodes/<slug>/script.json and art-direction.md
python epoch-ledger/scripts/narrate.py epoch-ledger/episodes/<slug>         # narration + timings
python epoch-ledger/episodes/<slug>/build.py                               # → index.html
cd projects/<slug>/hyperframes && npx --yes hyperframes@0.9.88 lint        # 0 errors required
npx --yes hyperframes@0.9.88 snapshot --at 1,5,9,...                       # look before rendering
python epoch-ledger/scripts/render.py plan    projects/<slug>/hyperframes   # what will render
python epoch-ledger/scripts/render.py scene   projects/<slug>/hyperframes s3 -o /tmp/s3.mp4 --preview
python epoch-ledger/scripts/render.py render  projects/<slug>/hyperframes -o projects/<slug>/renders/final.mp4
```

Caption engine is chosen in `config/production.json → captions.engine`:
`remotion` (the approved pilot path: `remotion_caption_burn` with `remotion_burn_inputs`, then
the `yuv420p` re-encode) or `hyperframes` (`kit/captions.py`, same look, rendered with the
scenes — no extra pass and no re-encode).

To re-render the approved pilot: `bash epoch-ledger/scripts/vendor.sh WS`, copy
`hyperframes.json`/`package.json` and the narration WAV into `WS`, then
`python epoch-ledger/episodes/how-banks-create-money/build.py WS`.

## Rendering performance

Measured on the pilot (4 vCPU, software WebGL, no GPU): HyperFrames 444 s for 943 frames
≈ **0.47 s per frame ≈ 14 min per minute of video**; Remotion caption pass ≈ 3.7 min per
minute; final `yuv420p` re-encode ≈ 1.1 min per minute.

| Path for a 10-minute episode at 1080p | First render | Change one scene |
|---|---|---|
| Pilot path (full HF render + Remotion captions + re-encode) | ≈ 3.2 h | ≈ 3.2 h |
| `render.py` + Remotion captions | ≈ 3.2 h | ≈ 4–8 min + ≈ 37 min caption pass + ≈ 11 min re-encode |
| `render.py` + HyperFrames captions (no re-encode) | ≈ 2.5 h | ≈ 4–8 min |

Weekly load at 2–3 episodes of 8–13 minutes: ≈ 16–39 minutes of video, ≈ 4–9 render-hours of
first renders at 1080p on this 4-vCPU machine, plus cached revisions. 1440p has 1.78× the
pixels; expect a proportional increase until measured.

How `render.py` saves time without touching quality:

- **Scene-level cache.** The timeline is cut at every top-level clip boundary; each chunk's
  key hashes only the shared document, referenced assets, the source of the scenes that
  overlap it, its range and the settings. Untouched chunks are reused.
- **Independent scene renders.** `render.py scene <id>` renders just the chunks a scene
  touches (`hyperframes render --start/--end`), at final or preview settings.
- **No re-encode on assembly.** Chunks are concatenated with stream copy and the narration is
  muxed once. Chunked output was verified identical to a full render (mean per-frame
  difference 0.003, encoder noise) with exact frame counts.
- **Cheap previews first.** `hyperframes snapshot` contact sheets (seconds) → `--preview`
  scene renders (24 fps draft) → final.

Not yet benchmarked (needs approval because each test is a real render): 1440p render time, pre-rasterising
static SVG set layers to PNG, a 960×540 preview build, SVG filter cost in the ledger scene,
Three.js shadow-map size, and parallel chunk jobs on machines with more cores.
