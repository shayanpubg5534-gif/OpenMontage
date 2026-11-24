# The Epoch Ledger — series production (creative skill)

> Series: finance, economics and history documentaries · Kit: `epoch-ledger/` · Runtime: HyperFrames (atelier) + Three.js
> Approved pilot: `epoch-ledger/episodes/how-banks-create-money/` (31.6 s, 1080p30)

**What it is:** the locked production method for The Epoch Ledger channel — a warm editorial
illustration look (hand-authored outlined SVG characters and sets, brass-and-ink palette,
layered parallax, Three.js hero beats), Kokoro narration, Whisper word-synced captions, and a
scene-cached render path. It is a **series kit, not a pipeline**: episodes run on the
`animation` pipeline with `render_runtime: "hyperframes"` and atelier composition.

Read `epoch-ledger/README.md` (series bible, layout, workflow, performance) before authoring.
For HyperFrames mechanics read `skills/core/hyperframes.md`; for motion principles see
`skills/meta/bespoke-composition.md`.

## Production targets (approved — `config/production.json → production`)

- **Cadence:** 2–3 high-quality documentaries per week (replaces the earlier 20-per-month plan).
  Quality beats volume: never trade accuracy, visuals or story for speed.
- **Length:** 8–10 minutes by default. Extend to 12–13 minutes only when the topic genuinely
  needs deeper explanation, historical context or detailed storytelling. **Never add filler**:
  no repeated points, padded recaps, slow holds or tangents to reach a length. Shorter and
  tight beats longer and slack.
- **Output:** 1920×1080, 16:9, 30 fps by default. 2560×1440 (1440p/QHD) is supported but
  optional; do not make it the default until it has been benchmarked on a real episode.
- **Narration:** Kokoro `bm_george` at 0.95 — unchanged.
- **Priorities, in order:** visual quality, factual accuracy, storytelling, audience retention.
- **Visual priorities:** detailed full-colour illustration, cinematic 3D, animated charts and
  diagrams, every visual synchronized to the narration.
- **Opening:** a powerful hook in the first seconds; never a logo intro or title card.
- **Cost:** free local tools only; no paid external APIs; avoid unnecessary AI usage
  (snapshot before rendering, preview single scenes, rely on the render cache, no speculative
  full re-renders).

## When to use

- The user asks for an Epoch Ledger episode, a "documentary for the channel", or a finance /
  economics / history explainer in the approved pilot's style (8–13 min long-form).
- Any request that names the series characters (Maya, the loan officer) or the ledger look.

## Pre-approved decisions (do not re-ask; do log them)

The user approved these with the pilot. Record each in `decision_log` at proposal with
`category` as shown, citing `epoch-ledger/config/production.json`:

| Category | Decision |
|---|---|
| `voice_selection` | Kokoro `bm_george`, speed 0.95 (free, local) |
| `render_runtime_selection` | HyperFrames for visuals (+ Three.js); Remotion considered for captions |
| `composition_mode` | atelier (series kit = engine + series bible; each episode authors its own scenes) |
| `playbook_override` | Epoch Ledger series look (palette/type/illustration rules in the kit README) |
| `music_source` | none unless the user drops a track in `music_library/` (surface it at proposal) |

Still ask before: changing voice, runtime, caption engine (`config → captions.engine`),
resolution/fps, adding paid providers, or using generated imagery.

The series kit is the one sanctioned exception to atelier's "never reuse creative components":
characters, palette and type are **series identity** and must stay consistent across episodes.
Scenes, compositions, metaphors and the signature device are still authored fresh per episode.

## Episode workflow

1. **Research** (animation pipeline research stage): 3–5 sourced data points; finance claims
   must be correct (cite central-bank, government or academic sources).
2. **Script** → `epoch-ledger/episodes/<slug>/script.json`: one entry per narration line
   (`id`, `text`, optional `pause_after`). Budget ≈ 150 words per minute at 0.95 speed (the
   pilot measured 156 incl. pauses): 8–10 min ≈ 1,200–1,500 words; 12–13 min ≈ 1,800–1,950.
   Justify any length over 10 minutes in the proposal (what depth or context needs it).
   Open on the hook — never a logo or title card. Structure for retention: hook → stakes →
   mechanism → turn/reveal → consequence, with a fresh visual question every 30–60 s.
3. **Scene briefs + art direction** → before building any scene write its brief (message,
   what the audience must understand, demonstrating actions, trigger words, cause → mechanism →
   consequence) and meet all four requirements in `epoch-ledger/QUALITY.md`: design detail,
   purposeful animation, word-level sync, **semantic storytelling** (show the meaning, not just
   the subject; every introduced object then operates and transacts). `art-direction.md`: scene table with one distinct primary subject per
   scene, the word each beat syncs to, the episode's signature device (1–2 beats), and a shot
   log (world, camera class, action) so no hero world repeats (see `epoch-ledger/QUALITY.md`).
4. **Narration** → `python epoch-ledger/scripts/narrate.py epoch-ledger/episodes/<slug>`
   (per-line TTS, trimmed, breaths, −16 LUFS, Whisper `small.en` words, caption pages, SRT).
5. **Build** → `episodes/<slug>/build.py` using `kit.assemble.Scene`. **Semantic sync is
   mandatory:** every object/action starts on the Whisper time of the word that names it
   (`W("semiconductor", "c05_02")`), never at a line end or on guessed seconds; camera moves
   start ≈ 1 s before the word. Characters use the jointed rig (`kit/rig.py`, `kit/rig.js`:
   `rig_svg`, `crowd_look`, `rpose`, `rwalk`, `ambient`, `rexpress`); 3D shots use keyframed
   cameras (`keyCam`).
   Reuse `kit.characters`, `kit.sets`, `kit/vault3d.js` (new camera shots per episode),
   `kit/helpers.js` (`walk`, `blink`, `talk`, `stamp`, `count`).
6. **Check** → `npx --yes hyperframes@0.9.88 lint` (0 errors) and `snapshot` contact sheets
   at every beat **and at each synced word time**. Review: overlaps, text over 3D objects,
   caption band (y ≥ 880) clear, characters fully visible, numbers legible, sync to the named
   words. Then render a short 540p motion sample of each priority sequence
   (`render.py range WS --start a --end b --fps 30 --quality draft`) and watch it — run the full
   checklist in `epoch-ledger/QUALITY.md` before asking for approval.
7. **Preview** changed scenes only: `render.py scene WS <id> --preview`.
8. **Final** → `render.py render WS -o projects/<slug>/renders/final.mp4`. With the
   `remotion` caption engine, then run `remotion_caption_burn` with
   `config → captions.remotion_burn_inputs` and re-encode to `yuv420p` (pilot path).
   Optional 1440p: build with `EPOCH_RESOLUTION=1440p` (scenes stay authored at 1920×1080;
   each scene is zoomed 4/3 so vectors and 3D re-rasterise sharply) and use the `hyperframes`
   caption engine. The kit sizes the root to the output frame and zooms each
   top-level clip (never the root); confirm in a snapshot that the frame is filled edge to edge.
9. **Verify** → `ffprobe` (1920×1080, 30 fps, yuv420p, AAC 48 kHz), loudness ≈ −16 LUFS,
   `blackdetect`/`freezedetect` clean, sampled frame sheet reviewed, captions match script.

## Reuse without repetition

Reusing kit components is expected; looking the same every week is not. Per episode:

- Re-stage kit pieces: new camera moves, framing, scale, lighting and accent colours; new
  vault shots rather than the pilot's; characters in new poses, places and props.
- Every scene's primary subject differs from its neighbours; no episode reuses a previous
  episode's hero shot or signature device.
- Each episode gets at least one new illustrated set or 3D scene and its own signature device.
- Charts and diagrams are built for this episode's data (accurate scales, labelled sources),
  never copied from a previous episode.
- Distinctness review before final render: "Could this frame belong to last week's episode?"
  If yes, re-stage it.

## Factual accuracy

- Every number, date and claim in narration or on screen traces to a cited source recorded in
  the research brief; prefer central banks, statistics offices, official histories and
  peer-reviewed work. Charts show real data with correct units and time ranges.
- Simplify without misleading: name the important caveat when a simplification hides one.

## Authoring rules that keep renders cheap

- One `Scene` per narrative beat; its CSS/JS stay inside the scene (the assembler wraps them in
  `/*scene:<id>*/` regions). Shared code changes invalidate every cached chunk — keep helpers stable.
- Give the vault (or any long-lived layer) explicit `shots`; it only draws inside them.
- Prefer HTML for text (webfonts do not apply inside SVG `<text>`); keep SVG for drawings.
- Deterministic only: no `Math.random()` / `Date.now()`; use the seeded helpers.

## Known limits (say them up front)

- Characters are clean flat-cartoon vector, not painterly; hands are simple shapes; the rig
  has elbows/knees/neck but no fingers or facial morphs; mouths flap rather than lip-sync.
- 3D is low-poly procedural geometry (no downloaded models, no GPU): good lighting, shadows and
  camera work, but not photoreal.
- No free music source in the cloud environment; no GPU, so CPU rendering ≈ 14 min per minute
  of video for a first render at 1080p (≈ 2–3 h for a 10-minute episode; see the kit README
  for the cached path). 1440p has 1.78× the pixels and is not yet benchmarked.
