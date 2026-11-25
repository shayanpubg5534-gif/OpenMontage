# The Epoch Ledger: production architecture audit

Status: report for approval. Nothing was installed, no production code was changed and nothing was rendered.
Date: 2026-11-25. Scope: the whole repository (both branches), in-repo skills and tools, and the external
technologies named in the brief.

How to read the evidence labels:
- **[V] verified**: checked in this session, in the repository, the package registries or the upstream source.
- **[M] measured**: a number measured on this container earlier in the project (4 CPUs, 15 GB RAM, no GPU).
- **[K] prior knowledge, not re-verified**: this environment blocks blender.org, helpx.adobe.com, synfig.org,
  opentoonz.github.io and raea.io, so these points come from documentation known before this session.
- **[E] estimate**, and **[U] untested possibility**.

---

## Part 1. What we have

### 1.1 Branches [V]
Only two branches exist: `main` (merges of PR #4 and #5) and `claude/epoch-ledger-setup-nzjuxr`, which is 18 commits
ahead. No other branch holds character or rendering work.

### 1.2 Character systems: six exist, and none of them is V5, V6 or V7 [V]

| System | Where | Technique | Used by | Status |
|---|---|---|---|---|
| Rig v1/v2 | `kit/rig.py`, `rig.js`, `episodes/ai-bubble-vs-dot-com/rig_people.py` | SVG parts, GSAP rotations | **The 18-minute AI-bubble documentary** (5 of 7 scene files), the episode template (`templates/episode/build.py`) | Production, frozen |
| Hand-drawn cast | `kit/characters.py` (Maya and others) | Hand-authored SVG per character | *How Banks Create Money* pilot, the episode template | Production, per-character |
| Rig v3 | `kit/rig3.py`, `rig3.js` | SVG, natural proportions, 2-bone IK, props, eyes | BigCart experiments, office v2/v3 | Fallback |
| **Rig v4** | `kit/rig4.py`, `rig4.js` | Orthographic 3D skeleton, tube limbs, IK, springs, occlusion, clothing | rig4_proof, BigCart final14, *Profitable and Broke* | Newest; experimental episodes only |
| Character-animation contract tool | `tools/character/character_animation.py` | Generic spec → SVG rig → pose library → action timeline | Only its own contract test | Not integrated; generic |
| Ink Theater puppet | `ink-theater/ink-puppet.js`, `ink-theater.js` | Doodle line puppet, FABRIK IK, CMU mocap converted to 2D | The separate ink-doodle format | Production for that format only |

**Why older versions are still used.** The 18-minute documentary was built and approved on Rig v1/v2 before v3
existed. Moving it to a newer rig would invalidate its scene cache and reopen approved scenes, so it was never
migrated. That was the right call, and it remains right. The episode template still points at v1/v2 and the
hand-drawn cast, so a new episode would start from the oldest system. That is a gap. `STANDARD.md` §4 still
lists "rig v3" as the capability, which is a stale document.

**Is the newest the best?** Not in every respect. Rig v4 has the best mechanics: IK, views, secondary motion and
occlusion. The hand-drawn cast (`characters.py`) has the most *illustrated* detail, because each character was
drawn rather than generated. v4's procedural tubes are the source of the "simplistic" and "unnatural arm"
complaints. No single in-repo rig combines illustrated quality with natural mechanics. That is the core problem
this audit has to solve.

### 1.3 Other production components [V]

| Department | Component (latest) | Used in production? |
|---|---|---|
| Composition and timing | HyperFrames 0.9.88 (pinned) with the GSAP 3.15.0 master timeline; `kit/assemble.py` | Yes, everywhere |
| Rendering | `scripts/render.py`: chunk cache, `--isolate`, `--jobs`, locks, watchdog | Yes. `--isolate` was **[M]** 1.6–13.8× faster |
| QA | `scripts/qc.mjs` (determinism, black/flash/freeze/jump, loudness, cut study), `layout_check.mjs`, `scene_plan.py` review | Yes |
| 2.5D sets | `scene3d.js` illustrated vector-3D engine, `plates.py` cached plates, `depth.py/js` layer bands and parallax, `camera3d` | Yes (v3/v4 era) |
| WebGL 3D | three.js **r160** vendored (`three.min.js`), `three_kit.js`, `vault3d.js`, `ai3d.js` | Yes, for objects and worlds; not for characters |
| Diagrams and charts | `explain`, `finmotion.js`, `motion.js` (`mBars`, `mLine`, `mDiagram`…), `motion.py` (iso, maps, routes) | Yes |
| Diegetic finance | `money`, `finmech`, `finstate`, `diegetic`, `lightfx` | Yes (`finstate` only in office v3) |
| Narration | Kokoro ONNX v1.0, voice bm_george, speed 0.95 | Yes |
| Captions | Whisper word timings, gold highlight (`kit/captions`) | Yes |
| Sound | Original synthesized SFX per episode (`sfx.py`, `sound_final.py`); no music | Yes |
| Hybrid 3D-character spike | `experiments/hybrid_spike/` (three r160, SwiftShader) | Experiment only: **[M]** 168 ms per 1080p frame |

### 1.4 Capabilities that exist but are not integrated [V]

| Capability | Where | Value to us |
|---|---|---|
| CMU motion-capture pipeline (BVH fetch, skeleton auto-mapping for CMU and Mixamo, provenance catalogue) | `ink-theater/mocap/` (12 clips, CMU licence: free for any use) | **High as a pattern.** The fetch, mapping and provenance code is reusable. The output is a 2D projection, so the clips themselves are not usable for 3D characters. |
| Three.js skills (animation, loaders, lighting, postprocessing…) | `.agents/skills/threejs-*` | Useful, but written for r150–r160 |
| Official GSAP skills | `.agents/skills/gsap-*` | Already present; current |
| HyperFrames adapters for Lottie, Three.js, WAAPI, Anime.js, TypeGPU | `.agents/skills/hyperframes-animation/adapters/` | The Three.js adapter is how a character layer plugs in officially |
| Character rigging, pose library, animation QA skills | `.agents/skills/character-rigging`, `pose-library-design`, `character-animation-qa`, `svg-character-animation` | Generic 2D guidance; overlaps with Rig v4. The QA skill's frame-sampling idea is already in `qc.mjs` |
| Three.js world generator (terrain, biomes, camera fly-throughs) | `tools/graphics/threejs_world.py` | For exterior establishing shots and landscapes; not evaluated in output |
| Blender world assembly | `tools/graphics/blender_world.py` | Hard-wired to a *Windows* portable Blender path; not runnable here as-is |
| 3D asset generation | `.agents/skills/3d-asset-generation` | Mostly paid providers (Atlas Cloud, fal.ai): excluded. The licensed-catalogue part is usable |
| Meta AnimatedDrawings | `animated-drawing` skill | Single-view raster drawings driven by mocap; no props or turns |

### 1.5 Duplicates [V]
- **Character systems:** the six listed in 1.2.
- **Video frameworks:** HyperFrames (used) and Remotion (skills `remotion`, `remotion-best-practices`, `remotion-to-hyperframes`; unused by Epoch Ledger).
- **Motion-design guidance:** `epoch-ledger-motion-craft` (ours, series-specific), `motion-graphics`, `framer-motion`, `lottie-bodymovin`, plus the hyperframes-animation rules.
- **Three.js:** a copy of `three.min.js` in every project workspace (same r160 file, which is harmless), plus three generations of three helpers (`three_kit.js`, `vault3d.js`, `ai3d.js`).
- **Docs:** `ARCHITECTURE_HYBRID.md` (previous proposal), `STANDARD.md`, `QUALITY.md` and `COMPONENTS.md` overlap on capabilities.

---

## Part 2. External technologies

"Engine" means software that produces frames. "Skill" means agent instructions (Markdown) that only change how an
agent writes code.

| Technology | Kind | Version and activity | Licence | Fits CPU-only container? | Verdict |
|---|---|---|---|---|---|
| **HyperFrames** | Engine | npm latest **0.9.94** (published 2026-11-25); we pin 0.9.88 **[V]**. GitHub shows 8,094 commits and 131 open issues **[V]** | Apache-2.0 **[V]** | Yes **[M]** | KEEP |
| **three.js** | Engine (WebGL) | Latest **r187** (2026-10-30); we vendor **r160** **[V]** | MIT **[V]** | Yes, via SwiftShader **[M]** | UPGRADE (character layer) |
| Three.js skeletal / skinned / morph / blending | Engine features | `SkinnedMesh`, `AnimationMixer` with crossfades and additive layers, morph targets: long-standing core APIs **[K]**; `mixer.setTime` determinism verified in our spike **[M]** | MIT | Yes **[M]** | INTEGRATE |
| **GSAP** | Engine | 3.15.1 latest; we ship 3.15.0 **[V]** | GSAP standard "no charge" licence; all plugins free since the Webflow acquisition **[V]** | Yes | KEEP |
| **FFmpeg** | Engine | 6.1.1 installed **[V]** | LGPL/GPL | Yes | KEEP |
| **Remotion** | Engine | 4.0.547 (2026-11-24) **[V]** | Free only for individuals, companies of up to 3 employees and non-profits; otherwise a paid Company License **[V]** | Yes | SKIP: duplicates HyperFrames, conditional licence |
| **Blender** (`bpy`) | Engine (offline authoring, retargeting, baking) | PyPI `bpy` **5.3.0**, cp313, 428 MB **[V]**; our Python is 3.13 **[V]**; blender.org was unreachable to confirm the LTS line **[K]** | GPL-3.0 (outputs are ours) **[V]** | Yes for scripting and export. Cycles/EEVEE final renders on CPU are slow **[K]**, so it is not our renderer | INTEGRATE as offline tool |
| **Rigify** | Blender add-on (auto-rig) | Bundled with Blender (extension in 4.2+) **[K]** | GPL | Yes | SKIP as primary: it makes animator control rigs for GUI work. Our automated pipeline needs a deform skeleton, which MPFB2 supplies |
| **MakeHuman / MPFB2** | Blender add-on and asset library | Not re-checked (hosts blocked) **[K]** | Code GPL; **exported characters CC0** **[K]** | Yes, via `bpy` **[U]** | INTEGRATE (gate P2) |
| **Adobe Mixamo** | Web service (auto-rig, animation library) | Web UI only, no public API **[K]** | Free with an Adobe ID; royalty-free use in projects; raw files may not be redistributed as-is **[K]** | Downloads are files, so rendering is unaffected | INVESTIGATE (your decision: it needs an Adobe account, and manual downloads) |
| **CMU mocap** | Data | Already used by ink-theater **[V]** | Free for any use **[V]** | Yes | INTEGRATE |
| **OpenToonz** | 2D app | v1.8.0 latest; 190 open issues **[V]**; headless `tcomposer` exists **[K]** | BSD **[K]** | Not in apt **[V]** | SKIP: hand-drawn workflow, needs art per view |
| **Synfig Studio** | 2D app | v1.5.5 (assets 2026-03-16) **[V]** | GPL **[K]** | Not in apt **[V]** | SKIP: as above, plus integration cost |
| **RAEA** | Engine (Rust, Bevy 0.20 + wgpu, React/TS compositions) | v0.1.9 (2026-11-22), 0.1.10-rc1 on 2026-11-25; first release 2026-11-11, near-daily rc releases **[V]** | FSL-1.1-ALv2: free unless you build a competing product; each version becomes Apache-2.0 after two years **[V]**. App "Pro" tier is paid; engine free **[V]** | **Unproven.** It needs a DX12/Vulkan/GL GPU driver **[V]**. This container has the Vulkan loader but **no Vulkan driver** (no lavapipe ICD) **[V]**. A software path (Mesa lavapipe/llvmpipe) would need installing and is untested **[U]**. glibc 2.39 + AVX requirement is met **[V]** | SKIP for production; optional sandboxed benchmark later |
| **CloudAI-X/threejs-skills** | Skill | Targets three r186, 13 skills (adds performance, React Three Fiber, asset pipeline) **[V]**; 4.4k stars, 26 commits **[V]** | MIT **[V]** | n/a | UPGRADE our older `.agents/skills/threejs-*` **together with** the three.js upgrade |
| **Official GSAP skills** | Skill | Already in `.agents/skills/gsap-*` **[V]** | MIT **[V]** | n/a | KEEP |
| **LottieFiles motion-design-skill** | Skill | 9 commits, 3.7k stars **[V]** | MIT **[V]** | n/a | SKIP: UI micro-interaction focus; its render path is a hosted service (Creator MCP). Our motion-craft guide already covers documentary motion |
| **design-dna** | Skill | 27 commits **[V]** | MIT **[V]** | n/a | SKIP: website design-token extraction; our series tokens already exist (`theme.css`, `STANDARD.md`) |
| **Genjutsu** | Skill | v4.2.0 (2026-11-13), 105 commits **[V]** | MIT **[V]** | n/a | SKIP: website and UI animation |

**About RAEA's speed claims.** Its "faster than they play" figures are Apple-Silicon and GPU measurements. None
apply to us. On a CPU software rasterizer it would compete with SwiftShader at best **[E]**. It would also replace
HyperFrames, the cache, `--isolate` and `qc.mjs`, which are proven, rather than plug into them. It is two weeks
old, so it is not suitable as a production base for a weekly schedule.

**About Mixamo.** Mixamo would give the largest ready motion library. It needs an Adobe ID and manual browser
downloads, because there is no API. If you approve an account, the files enter the same retarget pipeline as CMU
clips. Without it, CMU plus Quaternius (CC0) plus our own procedural layer is sufficient for documentary actions
(walk, sit, stand, gesture, type, carry).

---

## Part 3. The architecture by department

### 3.1 Root causes of the previous failures

| Failure | Root cause | Fix in the recommended architecture |
|---|---|---|
| Detached or hidden hands | Hand and prop are separate drawings with screen-space depth order | Props are parented to hand-bone sockets; the depth buffer orders them; QA measures hand-to-socket distance per frame |
| Unnatural bending | Hand-written IK with drawn tubes; no clavicle, no joint limits | A skinned anatomical mesh; clips carry real body mechanics; IK only for the final contact, with joint limits |
| Floating objects | A prop follows a computed wrist point across layers | A prop is always owned by a bone or a surface; ownership changes are timed events; QA fails on any unowned prop |
| Incomplete chart labels | Labels drawn in code without a check against the narration | The financial-model validator checks every value has a visible label at the moment it is spoken |
| Overlapping markers | Diagram text not registered with `layout_check` | All diagram text is auto-registered; collision is a failing gate |
| Premature figure reveals | No rule linking reveal time to narration | `scene_plan` rule: a figure appears no earlier than its spoken word minus a lead time |
| Awkward framing, too many wides | 2.5D sprites only hold up at one distance | Real 3D shot grammar (wide, medium, close-up, over-the-shoulder, insert) with a per-sequence shot-size mix check |
| Repetitive movements | A small hand-keyed action set | A clip library with variations and seeded offsets; QA flags the same clip repeated within N seconds |

### 3.2 Department decisions

| Department | Decision | What changes |
|---|---|---|
| Character design (illustrated, full colour) | **REPLACE** (principal characters) | MPFB2 CC0 bodies exported to glTF, with toon (cel) shading in three bands, ink outlines and the series palette. Faces get shape keys for blink, brows, smile and visemes (visemes only when a character speaks on screen). Rig v4 stays for background figures inside diagrams |
| Anatomy and proportions | REPLACE | Skinned meshes: connected by construction |
| Walking in several directions, turns | REPLACE | Retargeted clips plus root motion on paths; turns come from the 3D model, not separate views |
| Sit, stand, bend | REPLACE | Clips, plus IK to the actual seat and desk heights |
| Grip, write, sign, carry, hand-offs | INTEGRATE | Finger pose library (open, grip, pinch, pen); bone sockets; hand-off is a reparent at the frame where both sockets coincide; a pen tip drives the signature stroke on the paper surface |
| Facial expressions, clothing movement | INTEGRATE | Shape keys; spring bones on hems, ties and lanyards (our closed-form springs, ported) |
| Illustrated environments | KEEP + UPGRADE | `scene3d` and plates stay for illustrated diagram-style sets. Character scenes use three.js sets with CC0 kits (Poly Haven, ambientCG, Quaternius) under the same toon look |
| Cinematic 3D lighting and shadows | INTEGRATE | Real lights and shadow maps (measured affordable **[M]**) |
| Camera | UPGRADE | Shot-grammar presets in the 3D layer; `camera3d` and `depth` stay for 2.5D shots |
| Charts, diagrams, maps, timelines | KEEP + UPGRADE | Same SVG/GSAP kit; values come from the financial model; label and collision gates |
| Typography, colour, transitions | KEEP | `theme.css`, motion tokens |
| Story and narration sync | KEEP + UPGRADE | Word-timed shot script; the reveal-lead rule |
| Narration, captions, SFX, music | KEEP | Kokoro bm_george 0.95, gold captions, original SFX, no music |
| Rendering speed, caching, assembly | KEEP | HyperFrames + `render.py --isolate` + cache. The 3D layer is just another seekable layer |
| Financial accuracy | INTEGRATE | One Python cash-flow model per episode (daily, recurring revenue and costs, payment terms, financing cost); diagrams read from it |
| Visual QC | UPGRADE | Interaction QA: contact distances, penetration, unowned props, repeat-clip check, and consecutive-frame contact sheets (−5…+10 frames) around every interaction for human review |

---

## Part 4. Recommendations

### 4.1 Component classification

| Component | Class | Now → recommended | Why it is better / what it solves | Remaining limits | Needs | Complexity, performance | Evidence |
|---|---|---|---|---|---|---|---|
| HyperFrames | KEEP | 0.9.88 pinned; test 0.9.94 on a branch with the determinism check before moving | Proven spine; official Three.js adapter | Fast-moving project | none | – | **[V][M]** |
| render.py `--isolate`, cache, `--jobs` | KEEP | – | 1.6–13.8× faster than full-document renders | – | none | – | **[M]** |
| qc.mjs, layout_check, scene_plan | KEEP + UPGRADE | Add interaction QA, label gate, diagram-text registration, reveal rule, repeat-clip check | Turns past failures into failing tests | Visual taste still needs a human | none | Low | **[V]** |
| Rig v1/v2 | KEEP (frozen) | Only for the existing 18-minute documentary | Protects an approved cache | – | none | – | **[V]** |
| Rig v3 | KEEP (frozen fallback) | – | Fallback if the new layer slips | – | none | – | **[V]** |
| Rig v4 | KEEP (reduced role) | Background figures and diagram people | Cheap, stylised, works with diagrams | Not for principal characters | none | – | **[V]** |
| Principal characters | **REPLACE** | Rig v4 → MPFB2 CC0 glTF, toon + ink, in three.js | Connected anatomy; real occlusion; any angle and shot size; grip by sockets | Look must pass a style gate; "3D game" risk | `bpy` 5.3 wheel (428 MB), MPFB2 + MakeHuman asset downloads (needs network allow-listing) | High authoring, then reusable. **[M]** 0.17 s/frame in a simple scene; **[E]** 0.3–0.6 s rich | spike **[M]**, licences **[K]** |
| Motion clips | INTEGRATE | CMU mocap (BVH → Blender retarget → glTF actions); Quaternius CC0; Mixamo optional | Natural weight and gait without hand-keying | Mocap cleanup (foot slide, retarget errors) | The same `bpy`; Mixamo needs your Adobe ID | Medium | **[V]** (CMU pipeline exists) |
| Contact layer (IK, sockets, finger poses) | INTEGRATE | New, small, deterministic | Removes floating props and hidden hands by construction | Fine finger contact on small props still needs per-prop sockets | none | Medium | spike **[M]** |
| three.js | UPGRADE | r160 → r186/r187 for the character layer only, after a determinism and speed check; existing r160 modules untouched | Current loaders, animation and toon/outline paths; matches the current skills | Two three versions must never load on one page | none (vendored file) | Low–medium | **[V]** |
| threejs skills | UPGRADE | Repo copies (r150–r160) → CloudAI-X r186, same step as above | Current API knowledge for the agent | Skill text only | Copy of MIT Markdown files | Low | **[V]** |
| GSAP + official skills | KEEP | 3.15.0 (3.15.1 is a patch) | – | – | none | – | **[V]** |
| scene3d, plates, depth, camera3d | KEEP | For illustrated diagram-style sets | Proven look and speed | – | none | – | **[M]** |
| Charts and diagrams kit | KEEP + UPGRADE | Fed by the financial model | Fixes labels and misleading charts | – | none | Low | **[V]** |
| Financial model + validator | INTEGRATE | New | Funding gap, recurring costs and financing costs are always modelled | Scenario authoring per episode | none | Low–medium | – |
| Blender (`bpy`) | INTEGRATE (offline only) | Authoring, retargeting, glTF export; never the per-frame renderer | Scriptable; outputs are ours | 428 MB; GPL tool | wheel install | Medium | **[V]** |
| blender_world.py | UPGRADE later | Hard-coded Windows path → configurable; only if needed | – | – | – | – | **[V]** |
| threejs_world.py | INVESTIGATE | Exterior establishing shots | Terrain and fly-throughs | Output not yet reviewed | none | – | **[V]** |
| ink-theater mocap tooling | INTEGRATE (pattern) | Reuse the fetch, skeleton aliasing and provenance catalogue | Licence-clean clip library | Its 2D output is not reusable | none | Low | **[V]** |
| character_animation.py tool | SKIP | Generic; overlaps Rig v4 | – | – | – | – | **[V]** |
| Rigify | SKIP | Not needed for an automated deform rig | – | – | – | – | **[K]** |
| Mixamo | INVESTIGATE | Your decision on an Adobe account | Bigger motion library | Manual, account-bound | Adobe ID | – | **[K]** |
| OpenToonz, Synfig | SKIP | Need per-view hand art, GUI workflow, not packaged here | – | – | – | – | **[V][K]** |
| RAEA | SKIP (production); optional sandbox benchmark | Two weeks old; GPU driver required; no Vulkan driver here; would replace the proven stack | – | – | Installing Mesa lavapipe and a 321 MB release | – | **[V]** |
| Remotion | SKIP | Duplicates HyperFrames; licence conditional on company size | – | – | – | – | **[V]** |
| LottieFiles motion skill, design-dna, Genjutsu | SKIP | Web/UI design focus; our motion-craft guide is series-specific | – | – | – | – | **[V]** |
| Local diffusion and AI video | SKIP | CPU generation impractical; consistency uncontrollable | – | – | – | – | earlier test |
| Meta AnimatedDrawings | SKIP | Single view, raster, no props | – | – | – | – | **[V]** |

### 4.2 The one recommended architecture

```
script + Kokoro narration (bm_george 0.95) ── Whisper word times ──┐
                                                                    ▼
financial model (Python) ── validator ── values ─▶ SVG/GSAP diagrams, maps, timelines (existing kit)
        │                                               │  label gate · collision gate · reveal rule
        ▼                                               │
shot script (Python, word-timed) ── shot grammar, actions, contacts
        │
        ├─▶ 2.5D illustrated shots: scene3d / plates / depth / Rig v4 extras  (existing, unchanged)
        │
        └─▶ 3D character shots: three.js layer via HyperFrames' Three.js adapter, seeked by the master timeline
              characters  MPFB2 CC0 → Blender (bpy, offline) → glTF; toon bands + ink outlines; face shape keys
              motion      CMU / Quaternius (/ Mixamo) clips, retargeted offline; AnimationMixer.setTime
              contact     IK with joint limits · finger poses · bone sockets · reparent hand-offs
              sets        CC0 kits + own models; real lights and shadows; looping background life
        ▼
HyperFrames composition → render.py --isolate + cache → qc.mjs + interaction QA + contact sheets → MP4
captions (gold) · original SFX · no music · 1080p30 (1440p optional)
```

Rules that make it maintainable:
- Blender is an **authoring** tool, never in the render loop. Rendering stays in Chromium, which our cache,
  isolation and QC already understand.
- One three.js version per page. The character layer is r186/r187; older pages keep r160.
- Each character is a versioned asset (`cast/<name>/<name>.glb`, plus a source `.py` that regenerates it) so
  identity cannot drift between episodes.
- Every prop is owned by a bone or a surface at every frame.

### 4.3 Phased roadmap (each phase is committed separately and needs your go-ahead)

| Phase | Work | Exit criterion | Estimate **[E]** |
|---|---|---|---|
| P0 | Your decisions: approve the architecture; allow installing the `bpy` wheel (no GPU driver or RAEA install is needed); allow network hosts for MPFB2 and MakeHuman assets (blender.org hosts are currently blocked); decide on Mixamo | Decisions recorded | – |
| P1 | Quality gates that need no new software: financial model + validator, diagram-text registration, label gate, reveal rule, repeat-clip check | Gates fail on the known *Profitable and Broke* defects (tested on stored artifacts, not re-rendered) | 2–3 days |
| P2 | **Style gate:** one character via MPFB2 → glTF, toon + ink, in four shot sizes, as **stills** | Your approval of the look. If rejected, stop; fallback is a hand-painted layered 2D character on Rig v4 mechanics | 3–5 days |
| P3 | Motion and contact library: walk (four directions), turn, sit, stand, bend, gesture, type, carry; grip, pen and hand-off sockets; finger poses | Interaction QA passes on isolated test clips | 1–2 weeks |
| P4 | One three.js set kit (office or shop) with background life and the shot-grammar camera presets | Four style frames approved | 1 week |
| P5 | Fresh acceptance test (4.4) | All criteria pass + your visual sign-off | 2–3 days |
| P6 | Episode template switched to the new stack; docs (`STANDARD.md`, `COMPONENTS.md`) updated; three skills upgraded | A new episode can be started from the template | 2 days |

**Capacity [E].** An 8–10-minute episode is 14,400–18,000 frames. At 0.18–0.38 s per frame **[M]** for existing
shot types and an estimated 0.3–0.6 s for character shots, with `--isolate` and two jobs, that is about 1.5–3 h of
rendering per episode, which supports 2–3 a week. The limit is authoring, which the reusable cast, motion and set
libraries are meant to reduce.

### 4.4 Fresh acceptance test (new material; nothing reconstructed)

**Scenario:** "The Invoice". A supplier walks into a small print shop, hands the owner an invoice, the owner reads
it, sits, signs a cheque and hands it back; a small cash-flow diagram then shows the payment term and the effect on
the bank balance. 20–25 s, 1080p30, Kokoro narration, gold captions, original SFX, no music.

**Must contain:**
- a walk with a turn;
- a hand-off in each direction;
- sitting at a desk;
- writing a signature;
- picking up and putting down a held object;
- a close-up reaction;
- an over-the-shoulder shot;
- one diagram driven by the financial model.

**Pass criteria** (all automated unless marked):
1. Hand-to-socket distance ≤ 3 px at 1080p and no mesh penetration on every frame of every contact.
2. No prop without an owner on any frame.
3. No joint beyond its limit; no limb or hand hidden during a contact unless the shot plan says so.
4. Determinism: identical frames from different seek histories; `--isolate` output equal to a full-document render on sampled frames.
5. Each value in the diagram is labelled at the moment it is spoken, and matches the model. The bank balance is never negative unless an overdraft is modelled.
6. No text collision, no cropping of required elements, captions in their band.
7. Frame scan: no black, flash, freeze or opening jump; loudness on target.
8. At least four shot sizes; no clip repeated within 8 s.
9. Speed: ≤ 0.6 s per frame on this container for character shots.
10. **Human review:** contact sheets (−5…+10 frames) around every interaction, a 1-in-30 frame sample, and the video itself, checked against the permanent quality requirements.

---

## Appendix: evidence

- Registry checks (2026-11-25):
  - hyperframes 0.9.94 (Apache-2.0)
  - three 0.187.0 (MIT)
  - gsap 3.15.1
  - remotion 4.0.547 (company licence)
  - bpy 5.3.0 (GPL-3.0)
- READMEs and licences were downloaded as text from raw.githubusercontent.com and not executed. The readable
  findings are the RAEA and RAEA settings files, the Remotion licence, and the README and LICENSE of:
  - threejs-skills
  - motion-design-skill
  - design-dna
  - genjutsu
  - gsap-skills
- GitHub release pages: OpenToonz v1.8.0, Synfig v1.5.5, RAEA v0.1.9 / 0.1.10-rc1.
- Container: glibc 2.39, AVX2, Vulkan loader present with no driver, Python 3.13, FFmpeg 6.1.1, 4 CPUs, 15 GB RAM.
- Blocked hosts, so marked **[K]**: www.blender.org, docs.blender.org, helpx.adobe.com, opentoonz.github.io,
  www.synfig.org, raea.io.
