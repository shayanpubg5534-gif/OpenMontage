"""P13R pilot (78 s): "Sold on", paced for a first viewing (STANDARD §3B) on the refined narration
(projects/charlab_p13r/story). Every visual time comes from charlab/p13r/map_p13r.json resolved against the narration's
word timestamps. Ten compositions; each financial idea develops within one of them; labels arrive after the visual they
name and stay. The family, the town, the buyers and the three-tranche structure are illustrative (said in the narration
and tagged); house prices peaking in 2006 and Lehman Brothers' bankruptcy filing on 15 September 2008 are historical.

   0.0– 5.0 K1   their kitchen, dusk 2006: he leans in to sign; on "first home" she looks around, warming
   5.0– 9.9 KT   the table from above: the signature finishes; one bar: the payment takes almost all their income
   9.9–18.4 map  the papers dissolve into the town: their loan → their lender → sold on (pull back) → one pool fills
  18.4–35.4 B1   one building: issued on the pool; three tranches (simplified example); payments up the pipe; paid
                 from the top down
  35.4–41.6 map  the world: a pension fund, a bank, an insurer, each on its word; steady payments flow
  41.6–46.0 town the price line over their town rises to 2006 and turns down; the camera eases to their house;
                 on "can't sell" a FOR SALE sign on it
  46.0–50.0 N1   dissolve: the same kitchen, 2008 night; the letter; "stop"
  50.0–64.6 B2   one building: losses from the bottom; senior still paid in this example, rating cut, value falls;
                 the real-crisis caveat
  64.6–78.0 N2   September 2008: the newspaper on their table; the front page (insert NT 69.6–75.2); the two of them
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
for p in ("p11", "p12", "p13", "p13r"): sys.path.insert(0, str(REPO / "epoch-ledger/charlab" / p))
import formats as F  # noqa: E402  (P13)
import formats_r as FR  # noqa: E402
import visual_map as VM  # noqa: E402
import visuals as V  # noqa: E402
from kit.assemble import Scene  # noqa: E402
import importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location("p13r_shots", REPO / "epoch-ledger/charlab/p13r/shots.py")
_sh = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_sh)
NT_CAM = _sh.NT_CAM                            # the insert's camera (P13R shots), for the overlay that follows it

MAP = json.loads((REPO / "epoch-ledger/charlab/p13r/map_p13r.json").read_text())
RES = VM.resolve(MAP, VM.load_words(REPO / MAP["words"]))
E = {e["id"]: e["t"] for e in RES["events"]}
SH = {s["id"]: s for s in MAP["shots"]}

TITLE = "The Epoch Ledger · P13R pilot · Sold on (2006–2008)"
EPISODE = "projects/charlab_p13r/story"
NARRATION_WAV = "projects/charlab_p13r/hf/narration.wav"
DURATION = MAP["duration"]
R = ".runtime/charlab/p13r"
SEN, MEZ, EQ = "#efe7d6", "#7f93ab", "#c98d4a"
_V = [("K1", 0.0, 5.0), ("KT", 5.0, 9.9), ("B1", SH["S5"]["t0"], SH["S5"]["t1"]), ("N1", 45.99, 50.0), ("B2", SH["S9"]["t0"], SH["S9"]["t1"]),
      ("N2", 64.6, 78.0), ("NT", 69.6, 75.2)]
SHOTS = [{"id": k, "video": f"{R}/shot{k}.mp4", "start": a, "duration": round(b - a, 3)} for k, a, b in _V]
CSS = V.CSS + """
.ptag{position:absolute;left:56px;bottom:150px;padding:8px 14px;border-radius:6px;background:rgba(14,14,16,.55);font:600 22px Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#f6eedf}
.ptag.r{left:auto;right:56px;top:56px;bottom:auto}
.black{position:absolute;inset:0;background:#000}
"""
RULE = ((628, 514), (1175, 678))          # the printed red rule under the headline (night_top plate px; P13 measurement)


def fade_out(sid, t, d=.4):
    return Scene(f"{sid}fo", t, d, "", js=f"tl.to('#{sid}b',{{opacity:0,duration:{d},immediateRender:false}},{t:.2f});")


def tag(sid, t0, t1, text, t_in=None, right=False):
    return Scene(sid, t0, t1 - t0, f'<div id="{sid}x" class="ptag{" r" if right else ""}" style="opacity:0">{text}</div>',
                 js=f"tl.fromTo('#{sid}x',{{opacity:0}},{{opacity:1,duration:.4,immediateRender:false}},{(t_in or t0):.2f});")


def scenes(T):
    o = []
    # S1–S2: the kitchen, then the papers
    o.append(F.super_("yr06", 0.0, 4.9, text="2006", t_in=E["e_year"], sub="their kitchen"))
    o.append(tag("tag", 0.0, 4.9, "Illustrative reconstruction", t_in=0.6))
    o.append(FR.budget_insert("bud", 5.0, 4.9, sign_t=5.05, t_bar=E["e_bar"], t_left=E["e_left"], t_rise=E["e_rise"], video="v_KT"))
    # S4: one map, developing (dissolve in from the papers seen from above)
    s = SH["S4"]
    o.append(FR.pool_map_r("pj", s["t0"] - .3, s["t1"] - s["t0"] + .3, t_keep=s["t0"] + .1, t_sells=E["e_sells"], t_bundled=E["e_country"],
                           t_thousands=E["e_thousands"], t_out=E["e_pool"] + .1))
    o.append(F.xfade("pjx", s["t0"] - .3, .3, in_sel="#pj"))
    # S5: one building, 17 s: names, then payments (one box at a time)
    s = SH["S5"]
    o.append(tag("ex1", E["e_example"], s["t1"], "Simplified example", right=True))
    o.append(F.steps("tr", E["e_layers"] - .15, 30.45 - E["e_layers"] + .15, head="The security: three tranches", head_color=V.INK, arrow="",
                     lines=[(24.2, SEN, "Senior"), (24.9, MEZ, "Mezzanine"), (25.6, EQ, "Equity")]))
    o.append(fade_out("tr", 30.05))
    o.append(F.steps("pay", 30.6, s["t1"] - 30.6, head="Payments: paid from the top", head_color=V.GREEN, arrow="↓",
                     lines=[(30.7, SEN, "1  Senior"), (33.4, MEZ, "2  Mezzanine"), (33.9, EQ, "3  Equity")]))
    # S6: the world, each buyer on its word
    s = SH["S6"]
    o.append(FR.world_map_staged("wm", s["t0"], s["t1"] - s["t0"], origin=("Wall Street", -74.0, 40.7), title="Who buys the layers",
                                 buyers=[("Pension fund · senior · Norway", 10.75, 59.9, (18, -22, "start"), E["e_world"] + .15),
                                         ("Bank · senior · Germany", 8.68, 50.1, (-18, 48, "end"), E["e_banks"]),
                                         ("Insurer · senior · Japan", 139.7, 35.7, (-18, -26, "end"), E["e_insurers"])],
                                 t_flow=E["e_income"], tag="Buyers illustrative", t_tag=38.6, highlight={"United States of America": "#c9a56a"}))
    # S7: their town, prices (no signs here: the sign is seen from their kitchen next)
    s = SH["S7"]
    o.append(FR.price_town_r("pt", s["t0"], s["t1"] - s["t0"] + .3, series=[(2000, 100), (2001, 108), (2002, 117), (2003, 128), (2004, 143), (2005, 164),
                             (2006, 182), (2007, 178), (2008, 162), (2009, 143)], turn=2006, t_line=41.85, t_fall=E["e_fall"],
                             t_push=44.05, t_sign=E["e_sale"], title="US house prices (indicative)"))
    o.append(F.xfade("ptx", s["t1"], .3, out_sel="#pt"))
    # S9: one building, 14.6 s: losses from the bottom, then senior, then the real-crisis caveat
    s = SH["S9"]
    o.append(tag("ex2", 50.6, 60.9, "Simplified example", right=True))
    o.append(F.steps("loss", E["e_losshead"], 56.45 - E["e_losshead"], head="Losses rise from the bottom", head_color=V.RED, arrow="↑",
                     lines=[(53.6, EQ, "equity, then mezzanine")]))
    o.append(fade_out("loss", 56.05))
    o.append(F.steps("sen", 55.42, 60.85 - 55.42, head="Senior, in this example:", head_color=V.INK, arrow="", box=(1350, 150),
                     lines=[(55.5, "#3d7a52", "still paid"), (E["e_rating"], V.RED, "rating cut"), (E["e_value"], V.RED, "market value falls")]))
    o.append(fade_out("sen", 60.45))
    o.append(V.label("real", E["e_real"], s["t1"] - E["e_real"], kicker="In the real crisis", text="Many senior tranches lost money too",
                     box=(70, 620, 900), t_in=E["e_real"]))
    # S10–S11: September 2008, the newspaper, the family
    o.append(F.super_("yr08", 64.6, 4.9, text="September 2008", t_in=E["e_sept"], sub="the same kitchen"))
    (x0, y0), (x1, y1) = RULE
    o.append(F.follow("mark", 69.6, 75.2 - 69.6, cam2d=NT_CAM,
                      svg=f'<path id="markp" d="M{x0} {y0 + 6} Q{(x0 + x1) / 2} {(y0 + y1) / 2 + 14} {x1} {y1 + 6}" stroke="{V.RED}" stroke-width="9" stroke-linecap="round" fill="none"/>',
                      js=f"mDrawOn('#markp',{E['e_bk']:.2f},{{dur:.5}});"))
    o.append(tag("ntag", 69.6, 75.2, "Front page: illustrative reconstruction", t_in=70.2))
    o.append(Scene("end", 77.2, .8, '<div id="endb" class="black" style="opacity:0"></div>',
                   js="tl.fromTo('#endb',{opacity:0},{opacity:1,duration:.75,ease:'sine.in',immediateRender:false},77.22);"))
    return o
