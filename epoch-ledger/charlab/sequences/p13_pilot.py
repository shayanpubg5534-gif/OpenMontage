"""P13 pilot (30 s): "Sold on", re-directed. The P12 narration (unchanged, read only), the approved P13 treatment
(charlab/p13/treatment.json). Every visual time comes from charlab/p13/map_p13.json resolved against the narration's
word timestamps. Narrator-led: Kokoro voice-over, gold captions, no lip sync. The family, the town, the buyers and the
tranche structure are illustrative; house prices peaking in 2006 and Lehman Brothers' bankruptcy filing on 15 September
2008 are historical.

  S1  2.5D    their kitchen, dusk 2006: he leans in to sign                          (K1)
  S2  insert  cut on action: the pen signs; the payment fills nearly all income       (KT + document)
  S3  2.5D    he sits back; she looks away to the window → dissolve to the town       (K1)
  S4  map     their loan → their lender → sold on → the town's loans → one pool      (pool_journey)
  S5  3D      match cut: the pool as a plinth; one security, three tranches rise      (B1)
  S6  map     investors abroad, each buying a tranche (illustrative)                  (P12 world_map)
  S7  3D      steady payments: up the pipe, paid from the top down                    (B2)
  S8  map     their town: FOR SALE signs; the price line turns down → dissolve home  (price_town)
  S9  2.5D    the same kitchen, 2008: she reads the letter; he turns away             (N1)
  S10 3D      payments dry up; losses rise from the bottom; senior downgraded         (B3)
  S11 2.5D    September 2008: the newspaper on their table                            (N2)
  S12 insert  the front page from above; then the two of them; the lamp; fade         (NT, N2)
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
for p in ("p11", "p12", "p13"): sys.path.insert(0, str(REPO / "epoch-ledger/charlab" / p))
import formats as F  # noqa: E402
import visual_map as VM  # noqa: E402
import visuals as V  # noqa: E402
from kit.assemble import Scene  # noqa: E402

MAP = json.loads((REPO / "epoch-ledger/charlab/p13/map_p13.json").read_text())
RES = VM.resolve(MAP, VM.load_words(REPO / MAP["words"]))
E = {e["id"]: e["t"] for e in RES["events"]}
SH = {s["id"]: s for s in MAP["shots"]}

TITLE = "The Epoch Ledger · P13 pilot · Sold on (2006–2008)"
EPISODE = "projects/charlab_p12/story"                  # the P12 narration: read only
NARRATION_WAV = "projects/charlab_p12/hf/narration.wav"
DURATION = MAP["duration"]
R = ".runtime/charlab/p13/pilot"
SEN, MEZ, EQ = "#efe7d6", "#7f93ab", "#c98d4a"
# video layers, bottom to top (later entries draw over earlier ones)
_V = [("K1", 0.0, SH["S3"]["t1"]), ("KT", SH["S2"]["t0"], SH["S2"]["t1"]), ("B1", SH["S5"]["t0"], SH["S5"]["t1"]),
      ("B2", SH["S7"]["t0"], SH["S7"]["t1"]), ("N1", SH["S9"]["t0"], SH["S9"]["t1"]), ("B3", SH["S10"]["t0"], SH["S10"]["t1"]),
      ("N2", SH["S11"]["t0"], 30.0), ("NT", SH["S12"]["t0"], 28.6)]
SHOTS = [{"id": k, "video": f"{R}/shot{k}.mp4", "start": a, "duration": round(b - a, 3)} for k, a, b in _V]
CSS = V.CSS + """
.ptag{position:absolute;left:56px;bottom:150px;padding:8px 14px;border-radius:6px;background:rgba(14,14,16,.55);font:600 20px Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#f6eedf}
.black{position:absolute;inset:0;background:#000}
"""
NT_CAM = [[SH["S12"]["t0"], 1.0, 960, 540], [28.6, 1.22, 900, 540]]       # = shots.py NT (film seconds)
RULE = ((628, 514), (1175, 678))                                          # the printed red rule under the headline (plate px)


def scenes(T):
    out = []
    s1, s2 = SH["S1"], SH["S2"]
    out.append(F.super_("yr06", 0.0, s1["t1"], text="2006", t_in=E["e_year"], sub="their kitchen"))
    out.append(Scene("tag", 0.0, s1["t1"], '<div class="ptag">Illustrative reconstruction</div>'))
    out.append(V.document("doc", s2["t0"], s2["t1"] - s2["t0"], title="MORTGAGE AGREEMENT",
                          fields=[("Borrowers", "The family"), ("Purpose", "Purchase of the family home")],
                          bar={"label": "Monthly payment against monthly income", "frac": .9, "t_fill": E["e_bar"], "t_left": E["e_left"],
                               "left_text": "the mortgage payment", "left_label": "little left"},
                          sign_t=E["e_pen"], box=(650, 70, 640, 930), transform="rotateX(14deg) rotateZ(-4deg)", push=1.05, video="v_KT"))
    # S3 → S4: on her look to the window, the town map dissolves in (the street rises into the map)
    s4 = SH["S4"]; d_in = .3
    pj = F.pool_journey("pj", s4["t0"] - d_in, s4["t1"] - s4["t0"] + d_in, t_keep=E["e_keep"], t_sells=E["e_sells"],
                        t_bundled=E["e_bundled"], t_thousands=E["e_thousands"], t_out=s4["t1"] - .55)
    out += [pj, F.xfade("pjx", s4["t0"] - d_in, d_in, in_sel="#pj")]
    s5 = SH["S5"]
    out.append(F.steps("sec", E["e_seclabel"] - .1, s5["t1"] - E["e_seclabel"] + .1, head="One security, built on the pool", head_color=V.INK, arrow="",
                       lines=[(E["e_seclabel"] + .25, SEN, "Senior"), (E["e_seclabel"] + .4, MEZ, "Mezzanine"), (E["e_seclabel"] + .55, EQ, "Equity")]))
    s6 = SH["S6"]
    buyers = [("Oslo pension · senior", 10.75, 59.9, (18, -18, "start")), ("Frankfurt bank · senior", 8.68, 50.1, (18, 40, "start")),
              ("Tokyo insurer · senior", 139.7, 35.7, (-18, -24, "end")), ("London fund · mezzanine", -0.13, 51.5, (-16, -24, "end"))]
    out.append(V.world_map("wm", s6["t0"], s6["t1"] - s6["t0"], origin=("Wall Street", -74.0, 40.7), buyers=buyers,
                           title="Each tranche sold to different investors", t_routes=E["e_routes"], t_buy=E["e_buyers"], t_flow=E["e_flow"],
                           center=(22, 30), scale=6.4, highlight={"United States of America": "#c9a56a"}))
    out.append(Scene("wmtag", s6["t0"], s6["t1"] - s6["t0"], '<div class="ptag" style="bottom:170px">Buyers and tranches illustrative</div>'))
    s7 = SH["S7"]
    out.append(F.steps("pay", E["e_steady"] - .1, s7["t1"] - E["e_steady"] + .1, head="Payments: senior paid first", head_color=V.GREEN, arrow="↓",
                       lines=[(E["e_steady"] + .15, SEN, "1  Senior"), (E["e_mezz"], MEZ, "2  Mezzanine"), (E["e_mezz"] + .35, EQ, "3  Equity")]))
    s8 = SH["S8"]; d_out = .3
    out.append(F.price_town("pt", s8["t0"], s8["t1"] - s8["t0"] + d_out, series=[(2000, 100), (2001, 108), (2002, 117), (2003, 128), (2004, 143), (2005, 164),
                            (2006, 182), (2007, 178), (2008, 162), (2009, 143)], turn=2006, t_sale=E["e_sale"], t_line=E["e_line"], t_fall=E["e_fall"],
                            t_push=E["e_pushhouse"], title="US house prices", note="national index, indicative shape"))
    out.append(F.xfade("ptx", s8["t1"], d_out, out_sel="#pt"))            # their lit house dissolves to their kitchen at night
    s10 = SH["S10"]
    out.append(Scene("home", E["e_red"], .9, f'<div id="homel" style="position:absolute;left:960px;top:330px;transform:translateX(-50%);background:rgba(247,241,228,.95);'
                                             f'border-left:8px solid {V.RED};padding:10px 22px;border-radius:8px;font:800 40px Inter,sans-serif;color:{V.INK};opacity:0">their loan stops paying</div>',
                     js=f"tl.fromTo('#homel',{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{E['e_red']:.2f});tl.to('#homel',{{opacity:0,duration:.2}},{E['e_red'] + .7:.2f});"))
    out.append(F.steps("loss", E["e_secs"] - .1, s10["t1"] - E["e_secs"] + .1, head="Losses: equity hit first", head_color=V.RED, arrow="↑",
                       lines=[(E["e_secs"] + .05, EQ, "1  Equity: wiped out"), (E["e_collapse"] - .14, MEZ, "2  Mezzanine: hit next"),
                              (E["e_collapse"] + .2, SEN, "Senior: downgraded, value falls")]))
    s11 = SH["S11"]
    out.append(F.super_("yr08", s11["t0"], s11["t1"] - s11["t0"], text="September 2008", t_in=E["e_sept"], sub="the same kitchen"))
    (x0, y0), (x1, y1) = RULE
    out.append(F.follow("mark", SH["S12"]["t0"], 28.6 - SH["S12"]["t0"], cam2d=NT_CAM,
                        svg=f'<path id="markp" d="M{x0} {y0 + 6} Q{(x0 + x1) / 2} {(y0 + y1) / 2 + 14} {x1} {y1 + 6}" stroke="{V.RED}" stroke-width="9" stroke-linecap="round" fill="none"/>',
                        js=f"mDrawOn('#markp',{E['e_bk']:.2f},{{dur:.45}});"))
    out.append(Scene("ntag", SH["S12"]["t0"], 28.6 - SH["S12"]["t0"], '<div class="ptag">Front page: illustrative reconstruction</div>'))
    out.append(Scene("end", 29.35, .65, '<div id="endb" class="black" style="opacity:0"></div>',
                     js="tl.fromTo('#endb',{opacity:0},{opacity:1,duration:.6,ease:'sine.in',immediateRender:false},29.38);"))
    return out
