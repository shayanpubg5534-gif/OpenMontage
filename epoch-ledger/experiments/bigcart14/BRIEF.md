# BigCart 14 s: director's brief for the controlled comparison (shared by A′ and B)

Narration (unchanged, the episode's own c03_04 + c03_05):
"They were spending heavily on advertising, employees and infrastructure without earning enough revenue to sustain
themselves. Their survival depended on investors continuing to provide capital."

Figures: `kit/finstate.Ledger(start=13)`, spending ADVERTISING 2 / PAYROLL 1 / SERVERS 1, revenue 1; $20M of funding
arrives at month 2 (cash $4M → $24M). Everything is illustrative and the companies are fictional (both labelled).

## Meaning

- **What:** a dot-com company spends far more than it earns and stays alive only because investors keep sending
  money, which it immediately spends again.
- **Why:** it is chasing growth (advertising, hiring, servers) before revenue exists.
- **Consequence:** its survival is not in its own hands. The money in flows straight back out, so it will need
  investors again.

## Shots (the director's choices under the provisional standard)

| # | Time | Shot | Key moments (precisely timed) | Everything else |
|---|---|---|---|---|
| 1 | 0–6.45 | **The burn, one continuous office shot.** Open close on BigCart's cash on the founder's desk; pull back to reveal the whole operation the money feeds. | "advertising": the commercial airs as the money reaches it. "employees": pay lands on desks. "infrastructure": the new rack arrives. "revenue": one small customer payment arrives, a single bundle against the outflows. | The reveal carries "spending heavily". The founder directs the spending, then watches the meagre inflow and slumps. Slow push back onto the pile for "without earning enough". |
| 2 | 6.45–8.65 | **Insert: the founder's ledger.** His hand writes the month's arithmetic. | "sustain": the shortfall line. "themselves": "Cash left $10M ≈ 3 months" is underlined. | Out −$4M, In +$1M, written in turn; a held moment to read. |
| 3 | 8.65–11.1 | **Boardroom two-shot: the agreement.** | "investors": the signature completes, then a handshake. | The founder makes his case, the investor reads, a colleague watches. "Agreement signed". |
| 4 | 11.1–14.0 | **Two months later, back at the desk.** | "continuing": the wire confirmation prints on the fax. "capital": the pile refills to $24M and the camera pulls back as bills immediately fly out again to the ad, payroll and servers. | "Two months later" and "Money received" labels; the counter rises, then starts falling. |

**Transitions:** hard cuts, on the action. **Camera:** motivated moves only (reveal, emphasis on the inflow, final
pull-back), otherwise steady. **Holds:** shot 2 and the end of shot 3 hold for reading.

## Controls

- Same assets (plates, CC0 textures, rig v3 characters), same ledger, same narration and sound effects, 1080p30.
- No rig v4, depth-layered plates or motion blur.
- **A′** builds this with OpenMontage (HyperFrames assembly, `render.py`, the approved caption layer).
- **B** builds the same shot code as OpenFilm pages (`window.film.frame(t)`), with a `film.html` timeline, a
  WebVTT caption track styled to match, audio clips, and `openfilm render`.
- **A** is the approved v3 baseline, unchanged.
