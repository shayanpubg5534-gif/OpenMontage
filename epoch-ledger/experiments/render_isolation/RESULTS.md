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

## Recommendation (not yet adopted)
Add an opt-in `render.py --isolate`:
- reduced per-chunk documents;
- `--jobs` run truly in parallel, with the render lock off only for its own children, and the Stage 2 orphan and
  watchdog guards still applied;
- longest chunk first;
- a separate cache-key suffix.

The full-document path stays as the fallback. Then validate on a real episode-length workspace before making it
the default.
