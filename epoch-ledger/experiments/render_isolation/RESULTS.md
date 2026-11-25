# Stage 4: per-shot render isolation (controlled benchmark, 2026-11-25)

**Question.** Does rendering each shot from its own reduced document speed up HyperFrames renders, as the
OpenFilm comparison suggested (OpenFilm rendered the same film 2.2× faster)?

**Setup.**
- Workspace: BigCart 14 s A′ preview, rebuilt with the Stage 3 kit. It has 4 shots, 420 frames at 1080p30,
  quality "looks".
- Machine: 4 cores, HyperFrames 0.9.88, one run per mode, run one after another on an otherwise idle machine.
- Each "isolated" document is the full document minus the top-level clips and `/*scene:*/` regions that do not
  overlap the chunk (audio dropped). Its contents are exactly what render.py's chunk cache key already hashes.

## Results

| Mode | Workers | Wall time | vs full | Chunk times (s) |
|---|---|---|---|---|
| full: one chunk, full document | 2 | 152.5 s | 1.00× | 152.2 |
| full: one chunk, full document | 4 | 139.5 s | 1.09× | 139.3 |
| shots: 4 chunks, full document each | 2 | 174.4 s | 0.87× | 74.8 · 30.2 · 34.6 · 34.3 |
| isolated: 4 chunks, reduced documents (82–196 KB of 308 KB), one at a time | 2 | 152.2 s | 1.00× | 71.2 · 24.8 · 26.1 · 29.6 |
| **isolated-par**: same, 2 chunks at a time × 2 workers, HyperFrames render lock off | 2+2 | **87.2 s** | **1.75×** | 75.3 · 25.7 · 28.3 · 32.7 |

**Fidelity** (PSNR against the full render):
- Isolated: average 50.0 dB, minimum 44.7 dB. There are no localized differences: the maximum per-pixel Δ is 51,
  spread across the frame, consistent with rasterization and encoder noise.
- Control (shots, same document): average 55.4 dB, minimum 47.1 dB.

**Determinism.** `qc.mjs` element-state determinism passes on the isolated documents. Pixel-only raster noise is
the same as with the full document, and the QC pass is about 25% faster per frame on a reduced document.

## Findings
1. **Isolation alone does not explain OpenFilm's speed.** One reduced document per shot renders at about the same
   rate per frame as the full document. The gain is 5–25% on short shots, which pays back the per-chunk overhead.
2. **Splitting without isolation is slower** (+14%): every chunk loads and initializes the whole film.
3. **The real gain is parallelism, which isolation makes safe and cheap.** HyperFrames 0.9.88 holds one render slot
   per user account (`~/.cache/hyperframes/locks/render.lock`), so `render.py --jobs N` has been silently
   serialized. Isolated chunks run side by side (`HYPERFRAMES_RENDER_LOCK=off` for those child processes only)
   and gave a 1.75× speedup. The longest shot (6.45 s) bounds it here; an episode with many shots should balance
   better.
4. Giving one render 4 workers instead of 2 helped only 9%: per-frame capture does not scale with workers.

## Phase 1 — adopted as `render.py --isolate` (validation, 2026-11-25)

Method:
- The same machine and the same HyperFrames 0.9.88 for every run.
- The baseline is the previous behaviour: full document, one chunk at a time.
- `--isolate` uses scene-aligned chunks, reduced documents, two HyperFrames slots × 2 workers, and the equivalence
  check before rendering.
- The documentary windows ran on a hard-linked copy of the workspace. `mix.wav` was added there, because the real
  workspace references a `mix.wav` that does not exist and the full-document path refuses to render without it.

| Sequence (content) | Full document | `--isolate` | Speed-up |
|---|---|---|---|
| BigCart 14 s (characters, V3 charts, scene3d plates, a caption across a cut, narration), `render` | 146.3 s (0.35 s/frame) | 91.7 s (0.22 s/frame) | 1.6× |
| Documentary 36.6–52.4 s (Three.js campus and chip worlds, a crossfade, a character), `range` | 787.7 s (1.38 s/frame) | 181.1 s (0.38 s/frame) | 4.3× (3.6× per frame) |
| Documentary 763–789.6 s (railway: characters, charts, five crossfades, captions across chunk boundaries), `range` | 1991.3 s (2.19 s/frame) | 144.0 s (0.18 s/frame) | 13.8× (12× per frame) |

The full document costs more per frame the longer the film is, because every frame of the 18-minute document is
seeked in an 18-minute DOM. A reduced document holds only its scene, so its per-frame cost stays flat.

Fidelity (PSNR against the full-document render, every frame):

| Sequence | Average | Minimum |
|---|---|---|
| BigCart | 50.0 dB | 44.7 dB |
| 3D window | 48.8 dB | 45.2 dB |
| Railway | 47.5 dB | 43.1 dB |

- Narration audio is bit-identical (decoded-PCM md5) in all three.
- `qc.mjs --video`: no black stretches, single-frame flashes or frozen stretches at any chunk boundary; −16.1 to
  −16.2 LUFS.
- No chunk fell back to the full document.

Bugs found and fixed along the way:
- `render.py range` trimmed with a 3-decimal `-ss`, so a window whose start fell at 2/30 s into a chunk came out
  one frame early, in both modes. It now trims by frame number.
- A master timeline shorter than its composition clamped every seek past its last tween. `kit.assemble` now
  extends it.

Known limitation: the equivalence check compares DOM state, plus 2D canvas pixels where readable. It cannot read
WebGL canvases, so 3D-world parity rests on the per-scene regions being self-contained. That held here, as the
PSNR figures confirm.

## Original recommendation (now implemented)
Add an opt-in `render.py --isolate`:
- reduced per-chunk documents;
- `--jobs` run truly in parallel, with the render lock off only for its own children, and the Stage 2 orphan and
  watchdog guards still applied;
- longest chunk first;
- a separate cache-key suffix.

The full-document path stays as the fallback. Then validate on a real episode-length workspace before making it
the default.
