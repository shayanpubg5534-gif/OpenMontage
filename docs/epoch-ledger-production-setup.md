# The Epoch Ledger — Production Environment Report

Status as of 2026-11-24, cloud environment **"OpenMontage"** (4 vCPU, 15 GB RAM, no GPU).

## What is installed and verified

| Capability | Tool / engine | Status | Evidence |
|---|---|---|---|
| Python runtime | `.venv` (Python 3.10, via `make setup`) | Ready | 2,922 tests pass |
| Remotion (React motion graphics, charts, maps, captions) | `remotion-composer/` v4.0.484 | Ready | 23 s 1080p30 chart demo rendered in 2 min 32 s |
| HyperFrames (HTML/GSAP motion, Three.js 3D) | `npx hyperframes` 0.9.88 | Ready | 5 s 1080p GSAP chart + WebGL 3D coin rendered in 16 s |
| Three.js 3D | via HyperFrames (software WebGL) | Ready | as above |
| FFmpeg | 6.1.1 (libx264, libx265, AAC, libass subtitles) | Ready | — |
| Natural narration TTS | **`kokoro_tts`** (new, Kokoro-82M ONNX) | Ready | ~3x faster than real time on CPU; routed via `tts_selector` |
| Fallback TTS | `piper_tts` (lessac, ryan-high, alan voices) | Ready | — |
| Word-level captions | `transcriber` (faster-whisper base.en / small.en) | Ready | word timestamps verified |
| Subtitles | `subtitle_gen`, `remotion_caption_burn` | Ready | — |
| Diagrams | `diagram_gen` (Mermaid CLI) | Ready | — |
| Character rigs | `character-animation` toolchain (SVG rigs) | Works, basic look | procedural shapes only |
| Archival imagery | LoC, Archive.org, Openverse, Wikimedia, NASA | Network open | Wikimedia rate-limits generic clients |
| Image generation | 0 of 31 providers | **Not available** | needs GPU or a paid API |
| Video generation | 0 of 35 providers | Not available | needs GPU or a paid API |
| Music | `pixabay_music` (scraper) | Unreliable | Pixabay blocks datacenter IPs; use `music_library/` |

## Environment changes made

- Network allowlist (personal environment "OpenMontage"): HuggingFace model hosts, GitHub
  release assets, `cdn.jsdelivr.net` (GSAP/Three.js for HyperFrames), and free public-domain
  archive / royalty-free stock hosts.
- Environment variables: `REMOTION_BROWSER_EXECUTABLE`, `HYPERFRAMES_BROWSER_PATH` → the
  preinstalled Chrome Headless Shell (Remotion's own browser download host is unreachable).
- Setup script: runs `make setup`, installs Kokoro, faster-whisper, dev deps, Piper voices,
  Whisper models and Mermaid CLI on every fresh container.
- Repo: `remotion-composer/remotion.config.ts` (honours `REMOTION_BROWSER_EXECUTABLE`) and
  `tools/audio/kokoro_tts.py` (+ tests).

## Limitations and how to overcome them

1. **No GPU → no free image/video generation.** Full-colour hand-drawn illustrations and
   expressive cartoon characters need an image model. Options, cheapest first:
   - *Zero cost now:* atelier-mode SVG/HTML illustration authored per scene, public-domain
     archival art (engravings, period photos, political cartoons) with paper-texture grading,
     Ink Theater doodles. Strong for charts/maps/timelines; weaker for characters.
   - *Free per image:* run ComfyUI (SDXL / FLUX + an illustration LoRA) on your own NVIDIA
     GPU (12 GB+ VRAM) and use `comfyui_image`. Either run Claude Code on that PC, or expose
     ComfyUI through a tunnel and add its host to this environment.
   - *Small budget (only if you approve):* a hosted image API costs cents per image; generate
     a reusable **character cast** once (turnaround sheets, expressions), then animate those
     cut-outs in Remotion/HyperFrames so per-episode image spend stays low.
2. **CPU rendering speed.** Remotion ran at ~6.6x slower than real time, so an 8-minute episode
   takes roughly 50–60 min to render here; 20 episodes ≈ 20 render-hours/month. Render
   scenes in parallel chunks, keep heavy WebGL scenes short, or render on a local machine.
3. **Ephemeral containers.** Generated projects live in `projects/` (git-ignored). Download
   finals or push them to storage before the session ends.
4. **Music.** Drop licensed tracks (e.g. YouTube Audio Library) into `music_library/`; local
   music generation needs a GPU.
5. **Kokoro voices** have limited emotional control — direct pacing via punctuation, sentence
   splits and `speed` (0.9–1.0 suits documentary narration).

## Ready for the 30-second financial documentary test

Recommended path: `animated-explainer` pipeline (or `animation` for heavier motion design),
Kokoro narration → Whisper word timings → Remotion or HyperFrames composition with animated
charts, map and timeline, archival imagery, burned-in captions → 1080p H.264 MP4, no watermark.
The only missing pieces for the full brief are generated illustrations/characters (see 1) and
music (see 4).
