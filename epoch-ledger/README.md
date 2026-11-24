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
  48 kHz, `+faststart`, no watermark.

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

| Path for an 8-minute episode | First render | Change one scene |
|---|---|---|
| Pilot path (full HF render + Remotion captions + re-encode) | ≈ 2.5 h | ≈ 2.5 h |
| `render.py` + Remotion captions | ≈ 2.5 h | ≈ 4–8 min + ≈ 30 min caption pass + ≈ 9 min re-encode |
| `render.py` + HyperFrames captions (no re-encode) | ≈ 2 h | ≈ 4–8 min |

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

Not yet benchmarked (needs approval because each test is a real render): pre-rasterising
static SVG set layers to PNG, a 960×540 preview build, SVG filter cost in the ledger scene,
Three.js shadow-map size, and parallel chunk jobs on machines with more cores.
