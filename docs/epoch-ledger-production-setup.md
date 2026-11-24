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

## Premium motion-design tooling — feasibility (2026-11-24)

Goal: documentary motion design where every animation explains the narration (see
`epoch-ledger/QUALITY.md`), not more camera moves or decoration. Probed in this environment
(4 vCPU, 15 GB RAM, no GPU, software WebGL); nothing new was installed.

**Main finding:** the biggest quality gains in the AI-bubble revisions came from authoring, not
from new software: a written scene brief per scene, illustrated cutaways that show each mechanism
(construction gang, fab line, coolant loop, compute grid), rigged characters doing the work, and
ledgers and charts that build on the spoken words. New tools mostly add material quality and
speed up asset creation.

### Capability matrix

| Capability | Best route in our stack | Status / evidence | Cost & CPU impact |
|---|---|---|---|
| Premium cinematic 3D | Three.js r160 (in use) + CC0 glTF models + HDRI lighting + selective post-processing | three addons (GLTFLoader, RGBELoader, RoomEnvironment, EffectComposer, SSAO/GTAO, Bokeh, SMAA) reachable via cdn.jsdelivr.net (HTTP 200); MIT | free; post-processing ≈ +50–150 % render time, so use only on hero shots |
| Kinetic typography | GSAP 3.15 (vendored) + SplitText / DrawSVG / MotionPath | plugins reachable (200); GSAP's standard no-charge licence allows commercial use | free; negligible CPU (DOM) |
| Smooth morphing, transitions | GSAP MorphSVGPlugin, clip-path irises (in use), shared-element match cuts | reachable (200) | free; negligible |
| Isometric economic worlds | Three.js orthographic camera (diorama in use) + CC0 low-poly models (Kenney/Quaternius) or hand-drawn SVG isometric sets | model hosts not reachable from this environment (see below) | free; models cut authoring time per building from ~1 h to minutes |
| Detailed hand-drawn illustration | SVG sets + jointed rig v2 (in use); optional rough.js (MIT 4.6.6) for a hand-inked line | rough.js reachable (200) | free; cheap to render |
| Blueprint / exploded views | Three.js exploded assemblies (chip, rack in use) + SVG blueprint overlays with DrawSVG | — | free |
| Meaningful particles / simulation | instanced particles driven by the quantity they represent (coolant, money, data — in use); physics (cannon-es 0.20, MIT) only as *baked* trajectories | live physics is not seek-safe in frame-accurate renders; bake in Python/Node, play back by time | free |
| Materials, lighting, shadows, reflections | PBR + procedural canvas textures (in use) → CC0 PBR textures and HDRIs (Poly Haven, ambientCG) | hosts not reachable (blocked by network policy) | free (CC0); allowlisting needs your approval |
| Natural characters + interaction | rig v2 (elbows, knees, props, work poses, `rcycle`) — in use | — | free; crowds raise render cost (trading floor 26× real time) |
| Dynamic financial charts | SVG/HTML + GSAP (in use); d3-scale/shape for exact axes (d3 skill present) | — | free |

### Tool-by-tool

- **Blender** — the highest material and lighting ceiling, but not practical as the main
  renderer here: `download.blender.org` is blocked, there is no `bpy` wheel for our Python
  versions (pip: "no matching distribution"), and CPU Cycles at 1080p would need ≈ 1–3 min per
  frame on 4 vCPU (an 18-minute film is about 33,000 frames, i.e. weeks). EEVEE on software
  OpenGL would also be slow and unreliable. Blender is GPL; its rendered output is free to use. **Recommendation:** use it only
  later, if approved, to model or bake hero assets exported to glTF, or to pre-render a few
  seconds of hero plates. Needs an allowlisted download (~350 MB).
- **Three.js enhancements** — **recommended first.** Add GLTFLoader (CC0 models), HDRI image-based lighting for real
  reflections, and an optional EffectComposer pass (GTAO ambient occlusion + SMAA, light depth
  of field) applied only to hero shots, behind a per-shot flag so drafts stay fast.
- **GSAP plugins** — **recommended.** SplitText for narration-synced kinetic type (words land on
  Whisper times), MorphSVG for object morphs (chip → icon → bar), DrawSVG for blueprint line
  drawing. Already licensed for free commercial use; it means adding plugin files to the vendored set.
- **Manim CE 0.19.1** (PyPI reachable; MIT) — excellent for equation-led maths, but it renders
  outside HyperFrames, in a different visual language, and our charts already build in SVG.
  **Not recommended** for the series now; revisit for a maths-heavy episode.
- **Lottie** (lottie-web 5.13.0, MIT; HyperFrames has a Lottie adapter) — good for small icon
  animations, but authoring needs After Effects + Bodymovin (paid) or third-party files
  (licence per file). **Low priority.**
- **Open-source 3D/texture libraries** — Poly Haven and ambientCG (CC0 textures, HDRIs, models),
  Kenney and Quaternius (CC0 low-poly models). All are blocked from this environment today.
  **Recommended:** allow `dl.polyhaven.org`, `api.polyhaven.com`, `ambientcg.com` (and optionally
  `kenney.nl`). Record each asset's source and licence in the decision log; download once into a
  versioned asset cache.
- **UI UX Pro Max** (MIT; web UI design-intelligence skill: palettes, font pairings, UX rules) —
  built for app and website interfaces, not motion graphics. It could inform typography for
  on-screen panels, but adds little to documentary animation. **Not recommended** as a pipeline
  component; the series already has a locked type and palette system.

### Recommended plan (in order of impact per hour)

1. Keep the authoring standard: scene brief → cause, mechanism, consequence, with
   introduce → operate → transact for every object (done; enforced by `QUALITY.md`).
2. With your approval, allowlist the CC0 asset hosts and build a small licensed library
   (≈ 40 models: vehicles, cranes, transformers, chillers, office and shop interiors, trees) plus
   6–8 HDRIs. This replaces hand-built box geometry in 3D shots.
3. Add GSAP SplitText / MorphSVG / DrawSVG to the vendored runtime for kinetic type, morphs and
   blueprint draws.
4. Add a per-shot "hero" post-processing flag (GTAO + SMAA ± depth of field) and measure the render cost on
   one 10-second shot before using it widely.
5. Defer Blender, Manim and Lottie unless a specific episode needs them.

Costs: no money (all free or CC0); the costs are authoring time and CPU render time. Measured
draft rates on this machine are 11–26× real time at 540p, depending on 3D load and crowd size.
