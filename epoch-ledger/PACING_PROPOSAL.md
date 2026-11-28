# Proposal: Viewer Comprehension and Visual Pacing standard, and the P13 refinement

Status: **proposal for your approval.**
- Nothing in this document is adopted yet.
- No standard, tool or checker has been changed.
- Nothing has been rendered.
- P12, P13, their assets and the production tools are unchanged.

## 1. What went wrong in P13, measured on the rendered film

I sampled the P13 MP4 at 10 fps and counted **major picture changes**: frames where most of the picture changes at
once (a cut, a dissolve step, a large reveal or a fast camera move).

| Window | Major picture changes | Motion energy |
|---|---|---|
| 0–5 s (kitchen, signing) | 1 | low (3.2) |
| **5–10 s** (sold on, pooled) | **8** | high (13.6) |
| **10–15 s** (security, investors) | **8** | high (14.4) |
| 15–20 s (payments, prices, kitchen) | 5 | high (11.1) |
| 20–25 s (losses, newspaper) | 4 | medium (10.3) |
| 25–30 s (ending) | 2 | low (4.1) |

- **28 major picture changes in 30 s.** The median gap between them is **0.4 s**, and the longest the picture ever holds
  is **2.9 s**.
- From 5 to 15 s the viewer gets a new picture almost every second. That is the stretch you had to pause.

### Text on screen against the time needed to read it

| Text on screen | Words, plus the caption read at the same time | On screen | Needed (≈ 3 words/s with captions running, + 0.5 s) |
|---|---|---|---|
| Mortgage document (title, 2 fields, bar label, "little left") | ≈ 22 + 8 | 2.6 s | ≈ 9 s |
| "One security, built on the pool" + 3 tranche names | 8 + 3 | **1.2 s** | ≈ 4 s |
| World map: title + 4 buyers with their tranches + tag | ≈ 23 + 8 | **1.7 s** after the buyers appear | ≈ 10 s |
| "Payments: senior paid first" + 3 lines | 8 + 6 | 1.8 s | ≈ 5 s |
| House prices: title, note, years, 11 FOR SALE signs | ≈ 10 + 4 | 1.9 s | ≈ 5 s |
| "their loan stops paying" | 4 + 3 | **0.9 s** | ≈ 3 s |
| "Losses: equity hit first" + 3 lines | 13 + 7 | 1.7 s | ≈ 7 s |

**Why this happened:**
1. My own method rewarded density. The narration-to-visual checker (P11) requires a new visual event in every clause
   within 0.6 s, and warns when 2.6 s pass without one. I then tuned the film to pass that measure (41 events and
   36/41 in sync). That is synchronisation, not comprehension.
2. The narration is too compressed for its content (§2).

## 2. Is the 30-second narration too compressed? Yes

- **What it explains:** about 11 distinct ideas in 28.8 s of speech, so 2.6 s per idea:
  - origination;
  - affordability;
  - the sale;
  - pooling;
  - issuance;
  - tranches;
  - global buyers;
  - the payment priority;
  - falling prices;
  - defaults;
  - loss allocation, downgrades and Lehman.
- **What your guidelines call for:** financial diagrams take 6–12 s and complex mechanisms 10–20 s. The pooling,
  priority and loss mechanisms alone need roughly 30–45 s.
- **Speaking rate:** 2.2 words per second. That is normal; the problem is concepts per second, not words per second.
- **Conclusion:** no edit of these 30 s can be comfortable on a first viewing. The passage needs about **70–80 s** of
  narration, or fewer ideas.

## 3. The permanent standard (proposed text for STANDARD.md §3B and QUALITY.md)

### 3B. Viewer comprehension and visual pacing
1. **Comprehension over density.** A shot succeeds when a first-time viewer understands it at normal speed without
   pausing, not when it changes on every keyword.
2. **Synchronisation means landing, not replacing.**
   - A visual change should land on the word that motivates it. But not every phrase needs a new visual.
   - A clause can be served by the composition already on screen, or by a change within it.
3. **Develop, don't replace.**
   - Prefer progressive animation within one composition (a line draws, a layer lights, a label arrives, the camera
     moves to the next detail) over a new scene.
   - Replace the whole picture only when the place, time or idea changes.
   - We distinguish three kinds of change:
     - **motion within a scene:** free;
     - **a new element in the same composition:** budgeted;
     - **a new composition:** expensive.
4. **One step at a time.** A complex idea is built in steps. Each step is visible and readable before the next arrives.
5. **One focal point at a time.**
   - Never introduce competing new elements within the same moment.
   - Stagger them so the eye knows where to look, using the camera, light and colour to lead.
6. **Read time includes the subtitles.**
   - The viewer reads the caption and the picture together.
   - On-screen text stays at least `0.5 s + words ÷ 3` seconds after it appears, counted from when it is fully
     revealed.
   - Supporting text stays shorter than the caption it accompanies.
7. **Mobile first.**
   - Key text is at least 40 px at 1080p and labels are seven words or fewer.
   - At most four lines of text on screen at once, captions excluded.
   - Each element is readable on a phone held upright, which shows the 16:9 frame small.
8. **Let moments breathe.** Emotional beats and reveals hold, with quiet motion such as a slow push, breath or light.
   Holding is not static: it stays alive through small motivated movement.
9. **Motivated transitions, fewer of them.** Every cut or dissolve has a reason in the story. Avoid strings of short
   shots.
10. **Duration guidelines** (flexible; the director adapts them to the narration and subject):

| Content | Typical duration |
|---|---|
| Simple illustration | 3–5 s |
| Character storytelling | 5–8 s |
| Financial diagram | 6–12 s |
| Complex mechanism | 10–20 s when necessary |
| Emotional cinematic moment | 5–10 s |
| Brief transition (nothing to read) | 1–2 s |

11. **Script for the pictures.** At the treatment stage the director estimates each sequence's load against its
    narration. If the narration is too short for what must be understood, the script is lengthened or simplified.
    The visuals are never crammed to fit.
12. **Judged at normal speed.** Comprehension is reviewed by watching the film at 1×, start to finish, without
    pausing: first the director (from the measured pacing report and a real-time watch), then you.

**Kept unchanged:** engaging motion, cinematic storytelling, retention and accuracy. The aim is maximum understanding
and emotional connection, not maximum change per second.

## 4. Workflow changes (proposed; additive; earlier episodes unaffected)

| Step | Change |
|---|---|
| **Treatment** (`kit/treatment.py`) | Each sequence gets a `load` (illustration, character, diagram, mechanism or emotional) and the steps it must teach. The checker compares the narration's duration with the guideline for that load and warns **"narration too compressed: lengthen or simplify"** before anything is recorded. |
| **Script** | The director may propose narration rewrites at the treatment stage when the load demands it. Narration is re-recorded with Kokoro, as now. |
| **Narration-to-visual map** (`visual_map.py`) | Every clause must still be *shown*, but a clause can be served by a **held composition** (`"held": true`) or a progressive change. The "a new event every 2.6 s" warning becomes a **novelty budget**: warn on more than two new compositions per 10 s, or a new composition shorter than its load's minimum. The cut-rate warning drops from four to two per 10 s in explanatory passages. The sync check stays: what changes must change on its word. |
| **New pacing check** (`kit/pacing.py`) | **On the plan:** composition durations against their loads; text dwell against read time (with captions); focal points introduced within 0.5 s of each other; new compositions per 10 s. **On the rendered film:** major picture changes per 10 s, longest and median holds, text dwell measured from the frames. Same output style as the existing checks, with a pacing strip image for the report. |
| **QUALITY.md** | New checklist section, "First viewing at 1×": Could I follow it without pausing? Was every label readable while the caption ran? Did one thing at a time ask for my attention? Did emotional moments breathe? Did any picture vanish before I understood it? |
| **Director's guide** | A short section on pacing: develop within a composition; budget new compositions; hold for reading; plan the camera's path through one diagram instead of cutting between diagrams. |
| **Tests** | Static tests for the new rules and the checker. Plus a regression test: P13's 30 s cut must be flagged, and the refined plan must pass. |

**Overhead:** the pacing check runs in seconds, with no new approval gates. The only new judgement is the load
estimate in the treatment, about one minute per sequence.

## 5. The P13 refinement

The approved story, worlds, metaphors, characters, building and transitions stay exactly as they are. Only the pacing
changes. There are two options.

### Option A: recommended. A ~75 s version with a rewritten narration

Same story, same order and same assets. The narration gets the room its ideas need, and each idea becomes **one
developing composition** instead of several replacements.

| # | Narration (draft; ≈ 175 words, ≈ 75 s at the current pace) | Composition (one each, developing progressively) | ≈ s |
|---|---|---|---|
| 1 | "In 2006, a family signs a mortgage. The monthly payment takes almost everything they earn." | **The kitchen.** Two-shot at dusk; he leans in. Insert: the signature, then **one** bar (payment against income) fills. No field labels. A quiet push; she looks to the window. | 8 |
| 2 | "Their lender doesn't keep the loan. It sells it on. Lenders across the country do the same, and thousands of mortgages are gathered into a single pool." | **The town map, one continuous composition.** Their house → their lender (hold) → sold on (hold) → the camera pulls back → the town's loans flow in → the pool fills. Never more than two labels. | 12 |
| 3 | "On top of that pool, a bank builds a new security, divided into layers called tranches." | **The building.** Match cut from the pool to the plinth. The floors rise slowly; the three tranche names appear one at a time and **stay**. | 8 |
| 4 | "Each month, the families' payments flow in. The top layer, the senior tranche, is paid first; the layers below are paid only after it." | **Same building, continuing.** Their gold payment climbs the pipe; the windows light floor by floor from the top. Legend: "Payments: paid from the top ↓". | 10 |
| 5 | "Pension funds, banks and insurers around the world buy these layers, because they promise steady payments." | **Same building, continuing.** Small investor tags with flags attach to the floors (senior: pension fund, bank, insurer). This **replaces the world-map cut**; buyers are labelled illustrative. Optionally a short world-map pull-out at the end of the beat. | 8 |
| 6 | "Then house prices fall. Families who can't keep up, and can't sell for enough to repay, stop paying." | **Their town:** FOR SALE signs; the price line over the rooftops turns down and **holds**. Then a dissolve on their lit window to **the kitchen at night**: she reads the letter; he turns away. Held. | 11 |
| 7 | "Losses rise from the bottom. The lowest layer is wiped out first, then the next. The senior layer is still being paid, but its rating is cut and its market value falls." | **The building, losses.** Their house turns red; the pipe slows; the flood rises one tranche at a time, each step held; then the "downgraded" tag on the senior floors. Labels accumulate, at most four lines, each on its word. | 12 |
| 8 | "In September 2008, Lehman Brothers, which held billions in mortgage-related assets, files for bankruptcy." | **The kitchen at night:** the newspaper on their table, the insert of the headline (held), back to the two of them and the lamp. Fade. | 8 |

- **Shape:** about 8 compositions in about 77 s, against P13's 12 shots and 28 major changes in 30 s.
- **Expected pacing:** about 1–2 major picture changes per 10 s, with holds of 3–12 s and motion continuing inside
  them.
- **Accuracy:** the wording keeps the four stages separate and keeps the senior caveat. Lehman's link to its own
  mortgage-related holdings is stated, not a simple "domino" chain.
- **Cost:**
  - Narration is re-recorded with Kokoro (local, free).
  - Existing sets, plates, characters, scene code and formats are reused. The building gains longer states and
    investor tags.
  - Holds are rendered once, so the per-second cost falls. My estimate is 15–18 min of computing per finished minute,
    about 20–25 min for the 75 s cut.

### Option B: keep the 30 s narration, re-edit for comprehension

- Merge the building shots and drop the world-map cut: investors become tags on the floors. That leaves about 7
  compositions instead of 12.
- Strip the document to the signature and one bar.
- Cut the legends to one or two lines.
- Remove the price chart's title and note, leaving a single labelled line.

This roughly halves the picture changes. But the passage still asks for about 11 ideas in 29 s, so it will remain
fast on a first viewing. I recommend it only as a teaser, with the full explanation in the episode itself.

## 6. Decisions for you

1. Approve the standard in §3 (wording may be adjusted) and the workflow changes in §4.
2. Choose **Option A** (≈ 75 s, new narration from the draft in §5, which I'll refine) or **Option B** (30 s
   re-edit).
3. After your approval, I will:
   - implement the standard and the checks;
   - run the new pacing check against the P13 cut, as the regression test;
   - plan the refinement and show you its pacing report;
   - then render it for your review at 1×.
