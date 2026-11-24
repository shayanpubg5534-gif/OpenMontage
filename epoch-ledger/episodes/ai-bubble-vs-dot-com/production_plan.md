# Production plan — Is the AI Bubble Bigger Than the Dot-Com Bubble?

Status: **refined script ready for approval** (Option C approved as a one-time flagship exception:
16–19 minutes acceptable; series standard unchanged). Nothing has been rendered.

## Update after approval (2026-11-24)

- Option C with light refinement: 22 changes (repetition, wording, 2 factual corrections, ECB
  period precision, spoken "twenty twenty-six"). **Refined narration: 18:19.5 (1,099.5 s)**,
  1,986 words, 400 caption pages — see `refined_script.md`.
- ECB figures verified against the primary text; "processors" correction withdrawn (correct
  British pronunciation, Whisper limitation).
- Approved: HyperFrames-native captions (subject to visual + timing validation against the pilot
  in the first draft); narration + original sound effects, no music; read-only access to FRED,
  World Bank and ECB (FRED downloads are refused by FRED itself — see `fact_check.md`).
- Render estimate at 18:19.5 with HyperFrames captions (no Remotion pass, no re-encode):
  ≈ 4.3 h for the first full 1080p render + ≈ 11 min chunk overhead; one-scene revisions 4–8 min.
- Next (after approval): representative 960×540 draft previews of selected scenes; no full render.

## Representative draft previews (2026-11-24) — awaiting approval

960×540, 30 fps, HyperFrames captions, narration + original sound design (mix ≈ −15 LUFS).

| Preview | Film time | Length | Render wall time | × real time |
|---|---|---|---|---|
| p1 Opening (complete) | 0:00–0:52 | 52.4 s | 698 s | 13.3× |
| p2 Nasdaq collapse | 4:00–4:46 | 45.7 s | 337 s | 7.4× |
| p3 3D AI infrastructure | 5:53–6:28 | 34.9 s | 504 s | 14.4× |
| p4 Money-flow ecosystem | 7:16–8:38 | 82.4 s | 799 s | 9.7× |
| p5 Debt explanation | 9:37–10:17 | 39.8 s | 417 s | 10.5× |
| p6 Railway analogy | 12:43–13:00 | 17.3 s | 253 s | 14.6× |
| **Total** | | **272.5 s** | **3,008 s (50 min)** | **11.0×** |

3D-heavy scenes (software WebGL) cost the most. Projection for the full 18:19.5 at 540p: ≈ 3.4 h.
The 1080p rate has not been measured on this episode; expect it to be materially slower — measure
one 10-second 1080p chunk (≈ 3–5 min) before scheduling the final render.

---


Companion files: `fact_check.md` · `narration_timings.md` · `storyboard.md` (68 scenes) ·
`art-direction.md` · `artifacts/decision_log.json`.

## 1. Narration — actual duration

| | Value |
|---|---|
| Script | 1,988 words · 10 chapters · 166 narration lines · 175 sentences |
| Voice | Kokoro bm_george, speed 0.95 (unchanged series setting) |
| Pacing | 0.45 s between paragraphs, 0.6 s after short emphatic lines, 1.8 s at chapter breaks (chapter cards) |
| **Measured duration** | **18:31 (1,111.4 s)** |
| Speech rate | 4.1 syllables/s — same pace as the pilot (4.0); the script's longer vocabulary (≈ 2.1 syllables/word vs 1.4 in the pilot) is why it runs long |
| Captions | 403 Whisper-timed pages, script wording, approved pilot style |

**This is ≈ 5.5 minutes over the 12–13 minute target, and over the series maximum of 13 minutes.**
Faster voice speed cannot close the gap (1.0× ≈ 17.7 min, 1.1× ≈ 16.2 min) and would change the
approved voice. Options (your decision):

| Option | Result | Notes |
|---|---|---|
| A. Edit the script to ≈ 1,400 words | ≈ 13 min | Keeps every argument; I would propose line-level trims (redundant restatements in Ch. 2, 5, 6, 8, 9) for your approval before re-voicing only the changed lines |
| B. Two episodes | Part 1 "The Dot-Com Bubble" (Ch. 1–3 + bridge, ≈ 5.5 min — too short alone, so better with new material) or split after Ch. 4 (≈ 7.4 + ≈ 11.1 min) | Fits 2–3 episodes/week; second part may need a short recap |
| C. Keep 18.5 min as a one-off flagship | 18:31 | Exceeds series policy; ≈ 45 % more render time and production effort |

My recommendation: **A** — a tight 13-minute cut is better for retention and stays within policy.
The storyboard is timed to the current 18:31 narration; after trims it regenerates automatically
(`storyboard_spec.py`) and scenes covering cut lines are merged or dropped.

## 2. Factual corrections (details in `fact_check.md`)

1. c03_12 "roughly seventy-seven percent" → **seventy-eight** (Nasdaq closes 5,048.62 → 1,114.11 = −77.9%).
2. c03_14 "two thousand three hundred dollars" → **two thousand two hundred** ($10,000 × 1,114.11 / 5,048.62 = $2,207).
3. c07_07–08 (> 3% of GDP vs 1.1%): matches secondary coverage of the ECB November 2026 review;
   **confirm in the ECB box before picture lock** (needs read access to ecb.europa.eu).
4. Audio: c01_07 "processors" sounds like "processes" (re-voice proposed); "2026" is read
   "two thousand and twenty-six" (optional "twenty twenty-six").

All hypotheticals, scenarios and forecasts get on-screen labels (list in `fact_check.md`).
The script already presents a crash as possible, not certain.

## 3. Visual direction

- **Three palettes, one series:** 1990s sequences in warm vintage (amber, cream, faded teal, CRT
  green, film grain); modern AI sequences in navy, steel blue, cyan and brushed metal; analysis
  beats on the series ledger palette (parchment, ink, brass). Palette shifts are motivated by
  transitions (the 1999→2026 corridor, the rewind in s007).
- **Opening hook:** cold open on a 1999 exchange floor ticker wall turning to falling particles —
  no title or logo; chapter cards are 2-second overlays on live imagery, never blank slides.
- **3D (Three.js):** AI accelerator chip (exploded view), server sled → rack → data hall,
  cooling airflow, substation and transmission lines, hyperscale campus, iceberg reveal,
  isometric chip-fab → cloud → AI lab → customer diorama (reused in Ch. 5 and Ch. 9 for
  continuity, re-lit at night for the scenario), fibre trench, railway analogy.
- **Characters (original, full colour):** Dan (1999 founder), two 1999 investors, a 90s teen,
  Ade (modern analyst); series characters Maya (re-staged in modern settings) and the loan
  officer (Ch. 6). Expressive poses, blinks, gestures; no stick figures.
- **Charts with real data and source labels:** Nasdaq Composite 1995–2003 (peak and trough
  markers), $10,000 illustration, internet-user growth, $5.5 trillion capex forecast (labelled
  FORECAST), GDP-share comparison (labelled ESTIMATE), hypothetical cash-flow waterfall.
- **Diagrams that build with the narration:** money flows and the circular-financing loop,
  balance scales, domino scenario, ripple map.
- **Pacing:** 68 scenes, average 16 s, each with internal beats every 3–8 s keyed to Whisper
  word times; the 8 scenes over 25 s are deliberate continuity explanations (charts and the
  circular-financing diagram) with progressive builds.
- **Mobile-readable text:** ≥ 34 px labels at 1080p, ≥ 28 px source labels, nothing critical in
  the caption band (y ≥ 880).

## 4. Assets

| Type | Reuse (re-staged) | New |
|---|---|---|
| Characters | Maya, loan officer | Dan, 2 investors, teen, Ade |
| Sets (SVG) | ledger sheet, office bones | 1999 exchange floor, 1999 desktop, 90s living room, garage startup, dot-com office, VC street, rainy street, modern home/office/street, conference room |
| 3D | vault3d engine patterns, lighting rig | chip, server/rack/data hall, campus, substation, iceberg, isometric diorama, fibre trench, railway, city ripple map |
| Charts | count() helper | Nasdaq line, capex stack, GDP bars, waterfall, user growth, schematic lines |
| Data | — | Nasdaq Composite monthly closes (FRED `NASDAQCOM`), internet users (World Bank/ITU) |
| Audio | narration ready | subtle sound design (see §6) |

**Environment changes needed at production start (approval prompt):** allow
`fred.stlouisfed.org` and `api.worldbank.org` (chart data) and `www.ecb.europa.eu` (primary-source
check). No paid services.

## 5. Time and rendering estimates (4 vCPU, software WebGL, measured pilot rate 0.47 s/frame)

| Item | 18:31 cut (as voiced) | ≈ 13:00 cut (option A) |
|---|---|---|
| Frames at 30 fps | 33,342 | ≈ 23,400 |
| Full 1080p render (HyperFrames, first pass) | ≈ 4.4 h + ≈ 11 min chunk overhead | ≈ 3.1 h |
| Captions — Remotion path (approved) | + ≈ 1.1 h burn + ≈ 20 min re-encode | + ≈ 50 min + ≈ 14 min |
| Captions — HyperFrames path (same look, needs approval) | + 0 | + 0 |
| 960×540 draft of one chapter (≈ 2 min) | ≈ 7–15 min (estimate; ~4× fewer pixels, not yet measured) | same |
| One-scene revision after final | ≈ 4–8 min | same |

3D-heavy scenes (data hall, campus, diorama) may run slower than the pilot's vault in software
WebGL; I will measure them in the first draft chapter and report before the full render.

**Production effort:** build and review chapter by chapter (snapshot contact sheets → 960×540
draft → your review), roughly 3–5 working sessions for authoring plus the final render. AI usage is
the main cost driver; I will report actual usage per chapter.

## 6. Audio plan

- Narration: done (bm_george 0.95), −16 LUFS.
- Music: none available yet — `music_library/` is empty and no free licensed source is reachable
  from this environment. Options: you supply a commercially licensed track (e.g. YouTube Audio
  Library, licence noted) mixed at ≈ −28 LUFS under narration with ducking; or no music.
- Sound design: original, generated in-house with FFmpeg (soft whooshes for transitions, subtle
  tick/typewriter textures, low data-centre hum, distant trading-floor murmur synthesised from
  noise) — no licensing issues, kept 18–24 dB under the narration.

## 7. Decisions needed

1. **Duration:** A (trim to ≈ 13 min — recommended), B (two episodes) or C (keep 18:31).
2. **Factual corrections 1–2** (78%, $2,200) — approve re-voicing those two lines.
3. **Audio fixes:** re-voice c01_07 "processors"? "2026" as "twenty twenty-six"?
4. **Captions engine:** keep Remotion (approved, + ≈ 1.1–1.5 h per full render) or switch to the
   identical-looking HyperFrames captions (no extra pass).
5. **Music:** supply a licensed track, or narration + original sound design only.
6. **Network access** for chart data and the ECB primary-source check (§4).

## Revised visual samples v2 (2026-11-24) — awaiting approval

960×540, 30 fps, draft. Motion = mean absolute luma change between consecutive frames (0–255)
and % of near-static frames (< 0.4), same windows as the original previews.

| Sample | Window | Render | Motion old → new | Near-static old → new |
|---|---|---|---|---|
| r1 Trading floor (boom → panic) | 0:00–0:16 | 424 s (26×) | 2.44 → 3.14 | 8% → 2% |
| r2 Railway | 12:42.9–13:00.2 | 261 s (15×) | 1.45 → 3.94 | 17% → 5% |
| r3 AI infrastructure | 5:53–6:28 | 501 s (14×) | 2.60 → 2.15 | 26% → 28% |
| r4 Money flow | 7:15.7–7:50 | 367 s (11×) | 0.19 → 1.17 | 96% → 46% |

Open items: the laptop chat (r3, first 9 s) is still near-static; money-flow camera holds are
too still between beats; railway horizon hill is a featureless slab and the falling sign is
off-camera; the 2026 half of the split screen is too dark; the rigged crowd doubles render cost.

## Revised samples v3 — semantic storytelling pass (2026-11-24) — awaiting approval

960×540, 30 fps, draft. Clips are in `projects/ai-bubble-vs-dot-com/previews/v3/`.

| Sample | Window | Length | Render | × real time |
|---|---|---|---|---|
| Opening hook (floor → internet montage → seam → 2026 hall) | 0:00–0:34 | 34.0 s | 645 s | 19× |
| AI infrastructure (laptop → processors → cooling → power → capex) | 5:53–6:28 | 35.0 s | 607 s | 17× |
| Money flow, complete (introduce → operate → transact, loop) | 7:15.7–8:38 | 82.2 s | 949 s | 11.5× |
| Railway (construction → returns → losses → decay → comparison) | 12:42.9–13:09.5 | 26.6 s | 482 s | 18× |
