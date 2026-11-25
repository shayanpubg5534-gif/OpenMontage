# P1 report: quality gates

Status: P1 complete. P2 waits for your approval.
Date: 2026-11-25.

Scope:
- Nothing was rendered or re-rendered. The gates read the stored *Profitable and Broke* build (`index.html`) and its stored MP4.
- The 18-minute documentary, its scenes and caches are untouched. It was only *read* to test for false alarms (§4).
- No software was installed.

Evidence labels:
- **[M]** measured here;
- **[V]** verified from source files or registries;
- **[E]** estimate;
- **[U]** untested.

## 1. What was built

| Gate | File | What it checks |
|---|---|---|
| Finance | `kit/finmodel.py` (new) | A daily cash model of the business, covering:<ul><li>payment terms;</li><li>recurring revenue and costs;</li><li>loans with interest and fees;</li><li>an overdraft limit.</li></ul>The balance never falls below the overdraft limit. Bills that cannot be paid are tracked as a **shortfall**, never drawn as a negative balance. Validator rules:<ul><li>a shown figure ≠ the model (`FIN-FIGURE`);</li><li>profit ≠ revenue − costs (`FIN-ARITH`);</li><li>a shortfall drawn as a balance (`FIN-NEG-BALANCE`);</li><li>a recurring deal with one-off costs (`FIN-RECURRING`);</li><li>a loan smaller than the gap (`FIN-LOAN-SIZE`);</li><li>a free loan with no reason (`FIN-FIN-COST`);</li><li>a financing cost not shown (`FIN-COST-SHOWN`, warning).</li></ul> |
| Figure timing and legibility | `scripts/figure_check.mjs` (new) | Every figure the narration names must be **legible when it is spoken**: in its clip, opacity ≥ 0.6, inside the frame, not painted over, contrast ≥ 1.6, for 80 % of the 1.2 s after the word. It must not be revealed more than 0.75 s before the word. Charts: marks proportional to their values, on a shared baseline. |
| Layout | `scripts/layout_check.mjs` (extended) | Diagram text now counts as readable text; it was previously treated as decoration, which is why the overlapping markers passed. New checks:<ul><li>`text-occluded`: text painted over by a later shape, using real painted-pixel hit testing;</li><li>`text-low-contrast`: e.g. red text on a red bar;</li><li>SVG text measured by its glyphs, not its line box;</li><li>crossfades are not counted as collisions.</li></ul>Its behaviour on existing compositions is unchanged (§4). |
| Contacts | `scripts/contact_check.mjs` (new) | Every frame of every hold:<ul><li>wrist-to-prop distance (`detached`);</li><li>prop covering both wrist and palm (`hand-hidden`);</li><li>one-frame prop jumps or orientation flips (`prop-pop`).</li></ul>It works on Rig v4 today. The 3D layer will report the same quantities from bone sockets. |
| Frames | `scripts/qc.mjs --video` (unchanged) | Black, flash, opening jump, freeze, loudness. |
| Visual review | `scripts/review_sheets.py` (new) | From the stored MP4:<ul><li>contact sheets of 16 consecutive frames (−5…+10) around every interaction and every cut, with optional enlarged crops;</li><li>a 1-in-30 frame sample;</li><li>one HTML page with the gate results and the human checklist (grips, finger contact, orientation, posture, intersections, foot sliding, continuity).</li></ul> |
| Runner | `scripts/quality_gates.py` (new) | Runs all of the above from `episodes/<slug>/gates/gates.json`, writes one report and the review page, and exits 1 on any failure. |

Fixtures for the stored episode are in `episodes/profitable-and-broke/gates/`: `finance.json`, `figures.json`, `contacts.json`, `interactions.json` and `gates.json`.

Documentation: `COMPONENTS.md` (new rows) and `QUALITY.md` (approval checklist now requires the gates and the review page).

Tests: `tests/epoch_ledger/test_quality_gates.py`. It has 9 tests: the finance rules, plus each browser gate run on a synthetic composition with known defects, and the review tool run on a generated clip.

## 2. Results on the stored *Profitable and Broke* build [M]

One command, 101 s in total for the 41 s video: finance 0 s, figures 27 s, layout 5 s, contacts 23 s, frame scan 12 s. The review page took about 34 s more.

**Four of the five gates fail. Frame scan passes.**

### Your earlier findings: are they now caught automatically?

| Your finding | Caught? | How the gate reports it |
|---|---|---|
| Wages label missing at the right moment | **Yes**, by two gates | The label is red text on a red bar, so its contrast is 1.00. The bar itself floats 146 px above the baseline (`off-baseline`). |
| Overlapping timeline markers | **Yes** | The travelling "Day 0" chip paints over the "TODAY" marker from 16.0 to 19.75 s (`text-occluded`, `text-overlap`). The figure gate also reports "TODAY" illegible when "due" is spoken. |
| Hands hidden by the tablet | **Yes** | `hand-hidden` in 87 of 87 frames. |
| Unnatural arms | **No** | Not measurable on Rig v4: the arm is one drawn shape. This goes to the human contact-sheet review, and to joint-limit checks in the 3D layer. |
| Awkward folder posture | **Partly** | The folder flips from flat to upright in one frame at 30.167 s (`prop-pop`, size ×2.02). Maya's wrist is 52 px from the folder at the moment of the hand-off, and the folder covers her hand in 18 of 23 frames. The posture itself is a human-review item. |
| Floating crate | **Yes** | The crate drifts up to 125 px from Daniel's wrist while he walks (`detached`). The contact sheet confirms the hands swing free. |
| Funding gap shown as a negative balance | **Yes** | `FIN-NEG-BALANCE`. |
| Recurring order without recurring expenses | **Yes** | The order is "a month". The second month's $30,000 falls due on day 30, before the first payment on day 60. The true peak shortfall is **$48,000**, not $18,000, and the day-60 balance is $0, not $22,000 (`FIN-FIGURE`, `FIN-LOAN-SIZE`). |
| No financing costs | **Yes** | `FIN-FIN-COST`. |
| Simplistic characters, flat environments, too many wide shots | **No** | These are judgements of art and direction, not measurable defects. They are handled by the P2 style gate and the shot plan. |

### Problems the gates found that were not on your list

All of these were confirmed on the stored frames.

- **The order sheet floats at Daniel's hip during his walk-in.** The sheet hides his hand in 36 of 54 frames, and the sheet jumps between frames at 1.4–2.1 s.
- **The "+$40,000" payment is legible for only about 0.3 s** before the cut at 21.55 s.
- **The loan amount disappears for about 0.45 s across the cut** at 30.75 s. This is borderline: legible in 10 of 13 samples against a threshold of 80 %.
- **Four `caption-band` warnings.** Text sits in the caption band at:
  - 14.25–15.75 s, the profit value;
  - 18.0–21.5 s, the "Due now" pill;
  - 24.5–26.25 s and 33.0–34.75 s, the "Day 10" axis labels.

  Captions do not actually cover them. This is the existing band rule, kept unchanged.

**Early reveals: none.** No figure among the 15 narrated figures appeared more than 0.75 s before its word.

## 3. Raw gate output [M]

```
finance   FAIL  peak shortfall 48,000 before financing, 38,000 after
                FIN-NEG-BALANCE, FIN-FIGURE ×2 (18,000 short → 48,000; Day 60 $22,000 → $0), FIN-LOAN-SIZE, FIN-FIN-COST
figures   FAIL  12/17: wages (contrast 1.00), today-marker (painted over), payment-60d (4/13), loan-18k (10/13),
                profit-bars (#pb-r1 bottom at 765 px vs 911 px)
layout    FAIL  wages ×2 low contrast; TODAY overlap + occluded; 4 caption-band ranges
contacts  FAIL  3/11: order-dan hand hidden 36/54; order-maya detached 59 px at 6.93 s; tablet hand hidden 87/87;
                folder-maya detached 52 px + hand hidden 18/23; crate-dan detached 125 px;
                pops: #sheet1 (walk-in), #folder5 30.167 s, #crate6 (walk)
frames    PASS  no black/flash/freeze, opening consistent, −15.2 LUFS, true peak −3.3 dBFS
```

## 4. Checks for false alarms [M]

- **Synthetic compositions:** each check fires on its planted defect and stays quiet on the correct controls (proportional bars, a label shown on its word, a hand on its prop).
- **The extended layout check on other stored compositions:**
  - BigCart final14 and *How Banks Create Money*: 0 issues.
  - 18-minute documentary, first 180 s, read-only: the same 6 ticker-over-year-label overlaps the previous version already reported, and nothing new.
- **Test suite:** `tests/epoch_ledger` passes, 86 tests. One pre-existing, timing-dependent test (`test_render_preflight_clears_stale_and_orphaned_locks`, which kills an orphan process) failed once in three full runs and passed alone and in the other runs. It does not touch anything changed here.

## 5. Remaining limitations

1. **The fixtures for this stored episode were written by hand** from its script and `build.py`, because the old build does not emit them. Their element ids, cue words and hold windows are mine. For new episodes, the builder should emit `figures.json`, `contacts.json` and `interactions.json` automatically from the shot script. That is milestone M2.2 below.
2. **Contrast and occlusion only see SVG shapes.** Text over raster plates or photos, and HTML overlays, are not evaluated.
3. **The contact check measures a wrist point against the prop's bounding box.** It cannot see fingers, grip shape, object orientation or posture on Rig v4; those stay human-review items on the contact sheets. In the 3D layer, the same gate will use bone sockets, joint limits and mesh penetration.
4. **Thresholds are heuristic and tunable per item:**
   - prop jumps: 30 px and 2.5× the neighbouring frames;
   - label legibility: 0.6 s settle, 1.2 s hold, 80 %;
   - early reveal: 0.75 s lead.

   A deliberate fast throw would need an exemption flag.
5. **The finance model is daily, with simple interest and one currency.** It has no taxes, VAT or partial-payment terms beyond settling the oldest bill first.
6. **`caption-band` is a band rule.** It warns about text near the captions even when nothing is covered.
7. **The gates run on the built composition and the stored video.** Running them on the 18-minute documentary would need fixtures for it. That was not done, as instructed.

## 6. P2 requirements (exact)

### Software [V]
- **`bpy` 5.3.0**, from PyPI, which is reachable:
  - wheel `cp313` / `manylinux_2_28_x86_64`, 428 MB;
  - requires Python 3.13 (we have 3.13.18) and glibc 2.28 or newer (we have 2.39).
- **Installation plan:** an isolated virtual environment under the scratch area or `.runtime/`, never the system Python.
- **Fallback:** `bpy` 4.5.x LTS needs Python 3.11. It would need a uv-managed Python 3.11 **[U]**.
- **MPFB 2.0.18** (`src/mpfb/blender_manifest.toml`):
  - requires Blender 4.2 or later;
  - **compatibility with 5.3 is not stated and is the first P2 test [U]**.
  - The GitHub source contains the base mesh (`3dobjs/base.obj`, 1.7 MB), the rigs (`rigs/standard/rig.default.json`, with fingers, and `rig.game_engine.json`) and the shape targets (verified by reading individual files).
- **three.js r187** from npm, for the isolated character layer only. The existing r160 modules stay.
- **CloudAI-X Three.js skills (r186):** copied as Markdown when the layer is built, after the compatibility test.

### Licences [V]
- **MPFB code** is GPL-3.0. It is a tool we run; it is not distributed with the videos.
- **MPFB/MakeHuman bundled assets** are CC0 1.0: base mesh, targets, rigs, poses, expressions, clothes (MHCLO), textures (`LICENSE.md` §C).
- **Characters we generate are ours.**
- **Community asset packs** (extra clothes, hair, skins) carry **their own licences** (CC0 or CC-BY). Each one used will be recorded in a licence ledger before use.

### CPU-only
- `bpy` runs headless. Character authoring, rigging and glTF export need no GPU **[E: standard bpy usage; to confirm in M2.1]**.
- Blender's EEVEE renderer needs a GPU. This container has no Vulkan driver and only Mesa GLX libraries **[V]**, so **EEVEE will not be used**.
- **Style samples are rendered in three.js in headless Chromium (SwiftShader)**, exactly as production would render them. The earlier spike measured 0.17 s per frame for a simple scene **[M]**.

### Network permissions needed (currently blocked here) [M]

| Host | Why | Without it |
|---|---|---|
| `github.com` and `codeload.github.com` (read, public repos) | Download the MPFB2 source as a whole (raw.githubusercontent works file by file, but cannot list folders) | You upload the MPFB2 release zip |
| `static.makehumancommunity.org`, `files.makehumancommunity.org` | MakeHuman system asset packs (clothes, hair, eyebrows, eyelashes, skins), the MPFB docs | You upload the asset packs. Without clothes and hair the style gate cannot be judged fairly |
| `extensions.blender.org` (optional) | Alternative MPFB install | Not needed if the GitHub source is reachable |
| `drive.google.com` and its download host (later, P3) | Quaternius CC0 animation packs | Manual upload |
| `www.mixamo.com` + Adobe sign-in (optional, later) | Mixamo | It stays a manual, optional source; production never depends on it |

These are already reachable: PyPI, the npm registry, raw.githubusercontent.com (including the CMU motion-capture mirror), polyhaven.com, ambientcg.com and quaternius.com (the site, not its downloads).

### Disk [M]
49 GB free. Estimated P2 footprint: about 2 GB (`bpy`, assets, outputs) **[E]**.

### Mixamo (investigation only) [K]
- It needs an Adobe ID, and downloads are manual, per clip, from the web interface. There is no API.
- Our repository's visibility matters: raw Mixamo FBX files should not be committed to a public repository, so only baked animation inside our own character files would be stored.
- The terms must be re-read from Adobe's page, which is blocked here, before any use.
- Recommendation: decide after M3.1 shows what CMU and Quaternius cover.

### Honest risk for the style gate
MakeHuman produces anatomically natural bodies and faces, but its stock clothes, hair and skin textures are plain. Reaching your bar would need several things:
- painted textures or shader work;
- stylised hair;
- tuned toon bands and outlines;
- possibly sculpted facial detail.

The style gate exists to find out whether that bar is reachable with free tools, before any motion work. If it isn't, the fallback is to keep the 3D skeleton for mechanics and draw the characters in 2D on top. That would be a new proposal for you to approve.

## 7. Milestones from P2 on

Each milestone is small, independently usable, and ends with a deliverable you can review.

How to read the estimates:
- **Human** = days for an experienced technical artist or developer.
- **Claude** = agent working time and approximate usage. This is not wall-clock time, and it excludes waiting for your reviews.
- **Usage scale:** S ≈ well within one usage window; M ≈ about one window; L ≈ two or more windows.

All estimates are **[E]**.

| Milestone | Deliverable you can use or approve | Human | Claude (usage) |
|---|---|---|---|
| **M2.1 Toolchain check** | Isolated `bpy`; MPFB loaded headless; one base character exported to glTF; a three.js test page loads it. Measured: install size, export time, Blender 5.3 compatibility. Report only | 1 d | 1–2 h (S) |
| **M2.2 Gate manifests from the build** | Shot scripts emit `figures.json`, `contacts.json` and `interactions.json` automatically, so the gates need no hand fixtures (usable for every new episode, any rig) | 1–2 d | 2–3 h (S–M) |
| **M2.3 Look development, one character** | Toon shading (three bands), ink outline, palette, skin, hair and clothing treatment; **stills** in wide, medium, close-up and side profile, plus a turnaround; side-by-side with a Rig v4 frame | 4–6 d | 4–8 h (M–L) |
| **Style gate: your approval** | Approve, request changes, or stop | – | – |
| M2.4 Second character + faces | A second cast member; expression set (neutral, concern, relief, smile, surprise); hands at rest and gripping, as stills | 3–4 d | 3–5 h (M) |
| M3.1 Motion test, single actions | Isolated 3–5 s clips, each judged alone: walk (four directions), turn, sit, stand, bend; CMU retarget quality report | 4–6 d | 4–8 h (M–L) |
| M3.2 Hands and contact | Grip, pinch and pen poses; bone sockets; pick-up, put-down and hand-off clips; contact gate with joint limits, penetration and foot sliding | 5–8 d | 6–10 h (L) |
| **Motion gate: your approval** | Approve the individual capabilities before any sequence | – | – |
| M4.1 One set | One interior in the toon look, real light and shadow, four style frames | 3–5 d | 3–6 h (M) |
| M4.2 Performance proof | Measured CPU seconds per frame for wide, medium and close-up shots with characters, and the measured episode render time. Only after this can a 2–3-episodes-a-week claim be made | 1 d | 1–2 h (S) |
| M5 Acceptance test "The Invoice" | 20–25 s, the 10 criteria in the audit, the review page | 2–3 d | 3–5 h (M) |
| M6 Template | Episode template on the new stack; docs | 2 d | 2–3 h (S) |

Rendering time comes on top of these figures. Each still is seconds. Each motion clip is minutes **[E]**.

## 8. What P2 needs from you

1. **Approve P2 starting with M2.1 and M2.2.** M2.2 is useful on its own, whatever happens with the new characters.
2. **Network:** allow the hosts in §6, or upload the MPFB2 release zip and the MakeHuman asset packs.
3. **The look reference** for the style gate: two or three images, or a description of "premium illustrated" as you see it. For example: line weight, how painterly the shading is, how realistic or stylised the faces are, and any reference artists or films.
