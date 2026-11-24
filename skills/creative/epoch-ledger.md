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

## When to use

- The user asks for an Epoch Ledger episode, a "documentary for the channel", or a finance /
  economics / history explainer in the approved pilot's style.
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
   (`id`, `text`, optional `pause_after`). 6–10 min ≈ 900–1,450 words at 0.95 speed
   (the pilot ran ≈ 2.4 words/s). Open on the hook — never a logo or title card.
3. **Art direction** → `art-direction.md`: scene table with one distinct primary subject per
   scene, the word each beat syncs to, and the episode's signature device (1–2 beats).
4. **Narration** → `python epoch-ledger/scripts/narrate.py epoch-ledger/episodes/<slug>`
   (per-line TTS, trimmed, breaths, −16 LUFS, Whisper `small.en` words, caption pages, SRT).
5. **Build** → `episodes/<slug>/build.py` using `kit.assemble.Scene`. Key every tween to
   `line(id)` or `word(text, after)` times from the artifacts, never to guessed seconds.
   Reuse `kit.characters`, `kit.sets`, `kit/vault3d.js` (new camera shots per episode),
   `kit/helpers.js` (`walk`, `blink`, `talk`, `stamp`, `count`).
6. **Check** → `npx --yes hyperframes@0.9.88 lint` (0 errors) and `snapshot` contact sheets
   at every beat. Review: overlaps, text over 3D objects, caption band (y ≥ 880) clear,
   characters fully visible, numbers legible, sync to the named words.
7. **Preview** changed scenes only: `render.py scene WS <id> --preview`.
8. **Final** → `render.py render WS -o projects/<slug>/renders/final.mp4`. With the
   `remotion` caption engine, then run `remotion_caption_burn` with
   `config → captions.remotion_burn_inputs` and re-encode to `yuv420p` (pilot path).
9. **Verify** → `ffprobe` (1920×1080, 30 fps, yuv420p, AAC 48 kHz), loudness ≈ −16 LUFS,
   `blackdetect`/`freezedetect` clean, sampled frame sheet reviewed, captions match script.

## Authoring rules that keep renders cheap

- One `Scene` per narrative beat; its CSS/JS stay inside the scene (the assembler wraps them in
  `/*scene:<id>*/` regions). Shared code changes invalidate every cached chunk — keep helpers stable.
- Give the vault (or any long-lived layer) explicit `shots`; it only draws inside them.
- Prefer HTML for text (webfonts do not apply inside SVG `<text>`); keep SVG for drawings.
- Deterministic only: no `Math.random()` / `Date.now()`; use the seeded helpers.

## Known limits (say them up front)

- Characters are clean flat-cartoon vector, not painterly; hands are simple shapes; the walk
  cycle swings from the hip; mouths flap rather than lip-sync.
- No free music source in the cloud environment; no GPU, so CPU rendering ≈ 14 min per minute
  of video for a first render (see the kit README for the cached path).
