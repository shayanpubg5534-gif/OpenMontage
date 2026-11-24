"""Storyboard for 'Is the AI Bubble Bigger Than the Dot-Com Bubble?' — keyed to narration line ids.

Run after narrate.py: writes storyboard.md + storyboard.json with timestamps from
artifacts/narration_timing.json and sentence timings from artifacts/words.json.

Each scene: (id, first_line, last_line, era, primary subject, beats, method, assets, label)
  era: V = 1990s vintage palette (warm amber, cream, faded teal, CRT green)
       M = modern AI palette (deep navy, steel blue, cyan, brushed metal, cold white)
       L = ledger/analysis palette (series parchment, ink, brass)
  method: HF = HyperFrames HTML/SVG/GSAP · 3D = Three.js in HyperFrames · CH = data chart
          (HyperFrames SVG/D3-style, real data) · DG = animated diagram
  assets: R = reuse kit component (re-staged) · N = new for this episode
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

S = [
 # ── Chapter 1 — History Repeating Itself ─────────────────────────────
 ("s001", "c01_01", "c01_01", "V", "Hook: 1999 trading-floor ticker wall",
  "Cold open, no title. Camera pushes through a glowing 1999 exchange floor: amber LED ticker rows of invented dot-com tickers scroll; traders' silhouettes; CRT monitors. On 'change the world' the ticker turns green and accelerates.",
  "HF + 3D", "N: exchange floor set, ticker wall (deterministic tickers), trader silhouettes", ""),
 ("s002", "c01_02", "c01_02", "V", "Beige 1999 PC boots a web page",
  "Hard cut to a beige tower + CRT on a desk; dial-up handshake lights blink; a generic 1999 portal page draws line by line. Short, punchy beat on 'They were right.'",
  "HF", "N: 1999 desktop (CRT, tower, modem, mouse), generic browser chrome (no real brands)", ""),
 ("s003", "c01_03", "c01_04", "V", "Market value evaporating",
  "The ticker wall from s001 freezes, then numbers turn red and dissolve into falling amber particles. Office lights switch off row by row; a founder character (Dot-Com Dan, new) lowers his head over a cardboard box of belongings. 'Spectacular disaster' lands on a slow dolly back.",
  "HF + 3D particles", "N: character 'Dan' (1999 founder: khakis, fleece vest), office row; R: helpers blink/talk", ""),
 ("s004", "c01_05", "c01_06", "M", "Era cross-fade: 1999 → today",
  "A wipe sweeps left→right: the amber office ages into a dark steel data-centre corridor (palette shift vintage→modern). 'Artificial intelligence.' — single cyan light pulse travels down the corridor. Era tag '1999 → 2026' small, top-left.",
  "3D", "N: data-centre aisle (instanced racks, LEDs, cold-aisle light)", ""),
 ("s005", "c01_07", "c01_07", "M", "Three-beat montage of the boom",
  "Beat 1 'data centres': aerial 3D of a hyperscale campus being built (cranes, rows of halls). Beat 2 'semiconductor': macro orbit over an AI accelerator chip (die, HBM stacks). Beat 3 'investors': modern trading screens with Maya (series character, re-staged in modern office) watching charts rise.",
  "3D + HF", "N: campus diorama, accelerator chip model; R: Maya (new pose/outfit accent)", ""),
 ("s006", "c01_08", "c01_09", "L", "The question",
  "Split screen: left half vintage amber (1999 ticker), right half modern navy (2026 chip). A brass ledger line draws between them. Question resolves as two short HTML labels 'Revolution?' / 'Repeat?' (not the full sentence). Slow push in.",
  "HF", "R: theme, ledger-line device", ""),
 ("s007", "c01_10", "c01_10", "V", "Travel back in time",
  "Camera rushes backwards through the corridor; racks morph into CRT monitors; a calendar flips 2026→1993; warm grain fades in.",
  "3D + HF", "N: calendar flip, film-grain overlay (deterministic)", ""),
 # ── Chapter 2 — The Birth of a Financial Bubble ───────────────────────
 ("s010", "c02_01", "c02_02", "V", "Chapter card + early-90s home",
  "Chapter card 'Chapter 2 — The Birth of a Financial Bubble' (2 s, over image). A 1993 family room: modem cable to a phone socket, a teenager logs on; the screen's text world opens into a globe of connections.",
  "HF", "N: 90s living room set; character 'teen' (oversized flannel)", "Chapter card"),
 ("s011", "c02_03", "c02_04", "V", "Information travelling instantly",
  "Pull out to an illustrated globe; amber light-packets arc between cities; storefront icons topple like dominoes on 'vulnerable to disruption' (bookshop, travel agent, record store).",
  "HF + DG", "N: vintage globe map (d3-geo / world-atlas), storefront icons", ""),
 ("s012", "c02_05", "c02_07", "V", "Entrepreneurs and investors",
  "Dan (founder) in a garage startup pitches to two investors (new characters) around a whiteboard; four icons pop on the whiteboard as each sector is named (cart, billboard, bank card, envelope). Investors lean in on 'part of that future'.",
  "HF", "N: garage set, investor characters (1999 suits); R: talk/blink helpers", ""),
 ("s013", "c02_08", "c02_08", "V", "Money flowing in",
  "Gold banknote streams pour from a 1999 venture-capital office building across the street into the garage; counter ticks up (unlabelled stylised, no fake figures).",
  "HF + particles", "N: VC building facade; R: coin/note particle helper", ""),
 ("s014", "c02_09", "c02_11", "L", "Profits vs potential (scale)",
  "A brass balance scale: left pan 'Profits' (small), right pan 'Potential' (a glowing cloud) — the scale tips. Labels 'Visitors · Users · Market share' drop in as the right pan fills while a red 'Losses' stamp appears below.",
  "HF + DG", "N: balance-scale illustration", ""),
 ("s015", "c02_12", "c02_13", "V", "Expansion first",
  "Dan's startup map: pins multiply across a US map faster than a 'Profit' meter moves (it stays at zero).",
  "HF + DG", "N: US map pins", ""),
 ("s016", "c02_14", "c02_17", "L", "Hypothetical: online store losing money on every order",
  "Labelled 'Hypothetical'. A cartoon online pet-food store (invented 'BarkBox99'-style generic name avoided — use 'Store.com') ships boxes; each box shows +$10 revenue, −$13 cost; a loss counter grows with every order while the valuation balloon above inflates anyway as investors pump air.",
  "HF + DG", "N: store/warehouse vignette, valuation balloon", "Hypothetical"),
 ("s017", "c02_18", "c02_20", "V", "Reasonable vs speculation",
  "Two paths fork from the garage: one leads to a sturdy warehouse (reasonable), one to a house of cards (speculation). As 'stock prices continued rising' a rising line chart overlays both, and fog rolls in until the paths become indistinguishable.",
  "HF", "N: fork-in-path diorama, fog layers", ""),
 # ── Chapter 3 — When the Bubble Burst ─────────────────────────────────
 ("s020", "c03_01", "c03_02", "V", "Chapter card + Nasdaq 1999 chart",
  "Chapter card. Animated Nasdaq Composite line (real monthly closes, Jan 1995–Dec 1999) draws on a cream chart; 1999 segment highlighted with '+85.6% in 1999' callout.",
  "CH", "N: Nasdaq dataset (FRED NASDAQCOM, monthly close)", "Source: Nasdaq / FRED (NASDAQCOM)"),
 ("s021", "c03_03", "c03_05", "V", "Burning cash",
  "Inside a lavish 1999 startup office (foosball, Aeron-style chairs generic): a cash pile on a desk shrinks as three spend arrows pull from it (Ads · Staff · Servers); a small 'Revenue' trickle can't keep up. A runway clock counts down.",
  "HF + DG", "N: lavish dot-com office set", ""),
 ("s022", "c03_06", "c03_08", "V", "Confidence breaks",
  "Investors from s012 now frown at a valuation report; a glass 'confidence' meter cracks; the chart from s020 continues past March 2000 and tips over.",
  "HF + CH", "R: investor characters; N: crack effect", "Source: Nasdaq / FRED"),
 ("s023", "c03_09", "c03_11", "V", "Shutdown",
  "Dan locks the garage; 'CLOSED' sign; employees with boxes walk out under rain (parallax rain layer); a 1999 investor watches a brokerage statement go red.",
  "HF", "R: Dan, office; N: rain layer", ""),
 ("s024", "c03_12", "c03_12", "V", "Peak to trough chart",
  "Full Nasdaq chart 1995–2003: peak marker 5,048.62 (10 Mar 2000) and trough 1,114.11 (9 Oct 2002); a red bracket draws the decline '−78%'.",
  "CH", "R: s020 chart", "Nasdaq Composite closes · Source: Nasdaq / FRED"),
 ("s025", "c03_13", "c03_14", "L", "$10,000 illustration",
  "Labelled 'Illustration'. A stack of ten $1,000 bills placed at the peak marker shrinks to a ≈ $2,200 stack at the trough as the line falls; counter animates $10,000 → $2,207.",
  "CH + HF", "R: count() helper", "Illustration: index level only, no dividends or fees"),
 ("s026", "c03_15", "c03_17", "V", "The internet keeps growing",
  "Same rainy street at dawn: streetlights on, a delivery van with parcels, a household PC with a broadband modem; a soft green 'internet users' growth curve (real ITU data 1995–2010) rises behind.",
  "HF + CH", "N: ITU users dataset", "Source: ITU / World Bank internet users"),
 ("s027", "c03_18", "c03_20", "L", "The illusion vs the expectations",
  "A magician's curtain drops away from the internet globe (real, glowing) revealing the balloon of expectations popping instead. Transition: balloon fragments become cyan particles → modern era.",
  "HF + particles", "R: globe from s011; balloon from s016", ""),
 # ── Chapter 4 — The New Technological Gold Rush ──────────────────────
 ("s030", "c04_01", "c04_02", "M", "Chapter card + generative AI arrives",
  "Chapter card in modern palette. A modern kitchen: Maya types a prompt on a laptop; the screen streams text, code and an image (generic UI, no brand).",
  "HF", "R: Maya (modern home set, new)", "Chapter card"),
 ("s031", "c04_03", "c04_04", "M", "Businesses adopt",
  "Office floor of glass desks; holographic dashboards bloom over teams (productivity, costs, new services); the camera rises to a skyline where giant company towers light up (no logos).",
  "HF + 3D", "N: modern office, skyline towers", ""),
 ("s032", "c04_05", "c04_06", "M", "Software → hardware reveal",
  "A chat window on screen dissolves into a cable that the camera follows underground into infrastructure — the 'iceberg' reveal: small software tip, vast physical base.",
  "3D", "N: iceberg cross-section", ""),
 ("s033", "c04_07", "c04_07", "M", "The processor",
  "Hero macro: AI accelerator chip in Three.js — exploded view (substrate, interposer, die, HBM stacks) assembling; light streaks race across the die.",
  "3D", "N: accelerator chip (procedural geometry, PBR metal)", ""),
 ("s034", "c04_08", "c04_08", "M", "The server and the hall",
  "Chip seats into a server sled → sled slides into a rack → camera pulls back down a data-hall aisle.",
  "3D", "N: server sled, rack, data hall (instanced)", ""),
 ("s035", "c04_09", "c04_09", "M", "Cooling",
  "Thermal view: racks glow orange; cold blue air flows from floor vents (animated particles); liquid-cooling pipes pulse.",
  "3D", "N: airflow particles, pipe shader", ""),
 ("s036", "c04_10", "c04_11", "M", "Power",
  "Pull up through the roof: substation, transmission lines to the horizon carry pulses of energy into the campus at dusk.",
  "3D", "N: substation + pylons", ""),
 ("s037", "c04_12", "c04_14", "M", "$5.5 trillion forecast",
  "Labelled 'FORECAST'. Seven anonymous company towers (no logos) each extrude a column of capex; columns merge into one ≈ $5.5 trillion stack against a 2030 marker. Caveat line appears under it: 'Forecast · includes non-AI capex'.",
  "CH + 3D", "N: capex stack chart", "FORECAST · ECB FSR Nov 2026 (broker estimates)"),
 ("s038", "c04_15", "c04_16", "L", "Spending today, value tomorrow",
  "Two-sided ledger page: 'Spent today' fills fast in coral; 'Returns tomorrow' is a dotted, unfilled outline with a question mark.",
  "HF + DG", "R: ledger sheet (re-styled modern)", ""),
 # ── Chapter 5 — Following the Money ─────────────────────────────────
 ("s040", "c05_01", "c05_05", "M", "Simplified AI economy chain",
  "Labelled 'Simplified model'. Isometric 3D diorama: chip fab → cloud data centre → AI lab → customers (homes and offices). Each node builds on its narration line; glowing money arrows travel customer→lab→cloud→fab.",
  "3D + DG", "N: isometric node buildings, flow arrows", "Simplified model"),
 ("s041", "c05_06", "c05_11", "M", "Demand expands",
  "More customers appear; every node grows a level (more fab output, more racks, more users); a small 'investor expectations' gauge rises.",
  "3D + DG", "R: s040 diorama", ""),
 ("s042", "c05_12", "c05_15", "M", "Circular financing",
  "Labelled 'Hypothetical'. The chip maker sends a $1 billion arrow to the AI developer; part flows to the cloud company; the cloud company flows back to the chip maker — the loop glows and spins, highlighting that money circulates inside the industry.",
  "DG + 3D", "R: s040 diorama", "Hypothetical — not a specific company"),
 ("s043", "c05_16", "c05_17", "M", "Outside demand vs inside financing",
  "Split meters: 'Paid by customers' vs 'Financed within the industry'; an analyst character (new: modern analyst 'Ade') examines with a magnifier.",
  "HF + DG", "N: analyst character", ""),
 ("s044", "c05_18", "c05_20", "L", "Not fraud — but check the revenue",
  "Handshake between two partner buildings (positive framing), then the camera tilts down to the foundations labelled 'external revenue'.",
  "HF", "N: handshake illustration", ""),
 ("s045", "c05_21", "c05_23", "M", "Chain held up by expectations",
  "The whole diorama rises on a pillar of glowing 'expectations' clouds; on 'frighteningly quickly' the clouds flicker and the structure wobbles.",
  "3D", "R: s040", ""),
 # ── Chapter 6 — The Growing Role of Debt ────────────────────────────
 ("s050", "c06_01", "c06_01", "M", "Chapter card + debt",
  "Chapter card. Bond certificates (stylised) stack into the foundations of a data-centre construction site.",
  "HF + 3D", "N: bond certificate", "Chapter card"),
 ("s051", "c06_02", "c06_05", "L", "Hypothetical cash-flow waterfall",
  "Labelled 'Hypothetical company'. Waterfall chart: $10B operating cash flow − $6B capex = $4B free cash flow (green). Capex bar extends to $14B → free cash flow drops to −$4B (red), crossing zero on 'becomes negative'.",
  "CH", "N: waterfall chart", "Hypothetical company"),
 ("s052", "c06_06", "c06_06", "L", "Four ways to cover the gap",
  "Four doors open around the −$4B gap: Cash reserves · Sell assets · Raise equity · Borrow; the 'Borrow' door glows.",
  "HF", "", ""),
 ("s053", "c06_07", "c06_07", "M", "IMF warning",
  "A modern conference room; report cover reading 'Global Financial Stability Report · Oct 2026' (text only, no logo) on a table; a debt-gauge needle climbs into amber.",
  "HF", "N: report cover, debt gauge (re-styled credit gauge)", "Source: IMF GFSR, Oct 2026"),
 ("s054", "c06_08", "c06_11", "L", "Obligations don't disappear",
  "The series loan officer (kit character, re-staged in a modern bank) stamps a repayment schedule; calendar pages tick regardless of a falling demand line beside him.",
  "HF", "R: loan officer, stamp(), office set (new lighting/palette)", ""),
 ("s055", "c06_12", "c06_15", "M", "Ageing data centre",
  "Labelled 'Hypothetical'. A data hall ages: its chips dim as a newer, brighter generation glows next door; a loan-balance bar declines slower than the equipment's value bar.",
  "3D + CH", "R: data hall from s034", "Hypothetical"),
 ("s056", "c06_16", "c06_16", "L", "The tension",
  "Two clocks: a fast-spinning 'technology' clock and a slow 'loan' clock, joined by a taut rope.",
  "HF", "", ""),
 # ── Chapter 7 — Is This Bigger Than the Dot-Com Bubble? ─────────────
 ("s060", "c07_01", "c07_06", "L", "Four ways to measure",
  "Chapter card. A brass measuring kit on the ledger desk: tape (infrastructure), scale (market value), chain (debt), magnifier (valuation vs value) — each lifts as its question is asked.",
  "HF", "N: measuring tools illustration", "Chapter card"),
 ("s061", "c07_07", "c07_09", "L", "GDP share comparison",
  "Two bars on a clean chart: Internet boom 1996–2003 ≈ 1.1% of US GDP (amber) and AI build-out 2025–2032 > 3% (cyan, dashed top = estimate). Caveat line on 'not perfectly equivalent'.",
  "CH", "N: bar chart", "ESTIMATE · research cited by ECB FSR Nov 2026"),
 ("s062", "c07_10", "c07_11", "M", "Larger investment ≠ larger bubble",
  "The cyan bar becomes a scaffold; text label 'Investment ≠ bubble' in small caps.",
  "HF", "", ""),
 ("s063", "c07_12", "c07_13", "V", "Railway analogy",
  "Labelled 'Analogy'. 19th-century railway diorama (sepia-gold): a train linking busy cities (lights, cargo) vs a gleaming line to an empty plain where tumbleweeds roll.",
  "3D + HF", "N: railway diorama (low-poly, warm)", "Analogy"),
 ("s064", "c07_14", "c07_15", "L", "Returns justify spending?",
  "Ledger scale balances 'Spending' vs 'Returns'; the needle hovers, undecided.",
  "HF", "R: balance scale from s014 (modern skin)", ""),
 # ── Chapter 8 — Why This Time Could Be Different ────────────────────
 ("s070", "c08_01", "c08_02", "V", "Chapter card + then",
  "Chapter card. Left panel: 1999 startup with empty bank vault icon and a 'thin' business plan.",
  "HF", "R: Dan", "Chapter card"),
 ("s071", "c08_03", "c08_05", "M", "Now: profitable giants",
  "Right panel: modern towers with revenue streams flowing in (cloud, ads, software, subscriptions, commerce) — five labelled pipes.",
  "HF + DG", "R: skyline towers", ""),
 ("s072", "c08_06", "c08_08", "M", "AI already in use",
  "Quick vignettes (3–4 s each): developer pair-programming with AI, support agent with AI assistant, researcher with charts, admin automating forms — Maya appears in one.",
  "HF", "N: 3 workplace vignettes; R: Maya", ""),
 ("s073", "c08_09", "c08_10", "L", "Profitable ≠ good investment",
  "A wealthy tower drops coins into a well marked 'returns?'; some echo back, some don't.",
  "HF", "", ""),
 ("s074", "c08_11", "c08_13", "V", "Fibre-optic precedent",
  "3D: fibre cables laid in trenches (vintage dusk), most strands dark; time-lapse to modern night — the same strands light up with traffic.",
  "3D", "N: fibre trench, light-strand shader", ""),
 ("s075", "c08_14", "c08_16", "L", "Society wins, investors may not",
  "Split: thriving city using the network (lights) vs an investor's ledger in red for the original builder.",
  "HF", "", ""),
 # ── Chapter 9 — What Happens If Expectations Collapse? ──────────────
 ("s080", "c09_01", "c09_01", "M", "Scenario framing",
  "Chapter card + 'SCENARIO — not a forecast' tag. Many users on devices, but a small revenue cup only partly fills.",
  "HF", "", "Scenario — not a forecast"),
 ("s081", "c09_02", "c09_05", "M", "Domino chain",
  "Return to s040 diorama at night: the cloud node dims (plans cut), fab orders drop, a data centre with 'For lease' banner, a debt-laden building creaks — dominoes tip one by one.",
  "3D", "R: s040 diorama", "Scenario"),
 ("s082", "c09_06", "c09_07", "M", "Markets move first",
  "A valuation line falls ahead of a slower 'economy' line — showing markets anticipate.",
  "CH (schematic, unlabelled axes, 'illustrative')", "", "Illustrative"),
 ("s083", "c09_08", "c09_10", "M", "Ripple effects",
  "Camera pulls out: ripples travel from the tech district to pension buildings, banks, construction cranes, power plants.",
  "3D", "N: city ripple map", "Scenario"),
 ("s084", "c09_11", "c09_15", "L", "Not inevitable — other outcomes",
  "The dominoes freeze; three alternate paths branch: demand grows (lights return), costs fall (efficiency meter), new apps (new buildings), plus a gentle slope 'gradual adjustment' instead of a cliff.",
  "HF + DG", "", "Scenario"),
 ("s085", "c09_16", "c09_16", "L", "Competing forces",
  "A tug-of-war rope between 'Returns' and 'Investment' — balanced.",
  "HF", "", ""),
 # ── Chapter 10 — The Lesson History Keeps Teaching Us ───────────────
 ("s090", "c10_01", "c10_03", "V", "The lesson from 1999",
  "Chapter card. Return to the 1999 exchange floor from s001, now empty and quiet at night; one CRT still shows the internet globe glowing.",
  "HF + 3D", "R: s001 set (night)", "Chapter card"),
 ("s091", "c10_04", "c10_06", "M", "AI could transform",
  "Dawn over a modern city: AI data centres hum on the horizon; Maya walks to work (walk cycle, new street). Fog of 'speculation' hovers above the towers.",
  "HF + 3D", "R: Maya walk(), new modern street set", ""),
 ("s092", "c10_07", "c10_08", "L", "The real question",
  "Ledger scale (s064) close-up: 'Profits' vs 'Commitments'.",
  "HF", "R: scale", ""),
 ("s093", "c10_09", "c10_10", "L", "Expectations ahead of reality",
  "Two lines race: 'expectations' pulls far ahead of 'economic reality' until the gap glows red.",
  "CH (schematic, 'illustrative')", "", "Illustrative"),
 ("s094", "c10_11", "c10_12", "L", "Two generations",
  "Split: Dan in 1999 (vintage) and Maya in 2026 (modern) look at each other across the ledger line from s006 — the opening device returns.",
  "HF", "R: Dan, Maya, s006 device", ""),
 ("s095", "c10_13", "c10_14", "L", "Sign-off",
  "Ledger book closes; brass embossed 'The Epoch Ledger'; tagline 'Understanding the past. Decoding the present.' End on held frame (2 s).",
  "HF", "N: closing book", ""),
]


def load(path):
    return json.loads((HERE / "artifacts" / path).read_text())


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def main():
    timing = load("narration_timing.json")
    seg = {s["id"]: s for s in timing["segments"]}
    order = [s["id"] for s in timing["segments"]]
    script = json.loads((HERE / "script.json").read_text())
    chapters = {c["n"]: c["title"] for c in script["chapters"]}
    covered = []
    out, md = [], []
    md.append(f"# Storyboard — {script['title']}\n")
    md.append(f"Total narration: **{fmt(timing['total'])}** ({timing['total']:.1f} s) · {len(S)} scenes · "
              f"{len(order)} narration lines. Times are from the generated narration.\n")
    md.append("Era palettes: **V** 1990s vintage (warm amber, cream, faded teal) · **M** modern AI (navy, steel, "
              "cyan, metal) · **L** ledger/analysis (parchment, ink, brass). Methods: HF HyperFrames · 3D Three.js · "
              "CH data chart · DG animated diagram. Assets: R reuse kit (re-staged) · N new.\n")
    prev_ch = None
    for sid, a, b, era, subj, beats, method, assets, label in S:
        ia, ib = order.index(a), order.index(b)
        ids = order[ia:ib + 1]
        covered += ids
        ch = int(a[1:3])
        start = seg[a]["start"] - (0.6 if ia else seg[a]["start"])
        end = seg[b]["end"] + 0.3
        dur = end - start
        if ch != prev_ch:
            md.append(f"\n## Chapter {ch} — {chapters[ch]}\n")
            md.append("| Scene | Time | Dur | Era | Primary subject | Visual beats | Method | Assets | On-screen label |")
            md.append("|---|---|---|---|---|---|---|---|---|")
            prev_ch = ch
        md.append(f"| {sid} | {fmt(start)}–{fmt(end)} | {dur:.1f}s | {era} | {subj} | {beats} | {method} | {assets} | {label} |")
        out.append({"id": sid, "lines": ids, "start": round(start, 2), "end": round(end, 2), "era": era,
                    "subject": subj, "beats": beats, "method": method, "assets": assets, "label": label})
    missing = [i for i in order if i not in covered]
    dupes = {i for i in covered if covered.count(i) > 1}
    assert not missing and not dupes, (missing, dupes)
    (HERE / "storyboard.json").write_text(json.dumps(out, indent=1))
    (HERE / "storyboard.md").write_text("\n".join(md) + "\n")
    long = [o for o in out if o["end"] - o["start"] > 25]
    print(f"{len(out)} scenes, all {len(order)} lines covered; scenes > 25 s: {[(o['id'], round(o['end'] - o['start'], 1)) for o in long]}")


if __name__ == "__main__":
    main()
