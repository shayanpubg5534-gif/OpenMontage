"""P12 validation passage (30 s): "Sold on". A new subject, the 2006–2008 US mortgage crisis, built with the P11 method
and the P12 format library. Every visual time comes from charlab/p12/map_p12.json resolved against the narration's word
timestamps. Narrator-led: Kokoro voice-over, gold captions, no lip sync. The family is illustrative; the market events
(house prices peaking in 2006, Lehman Brothers' bankruptcy filing on 15 September 2008) are historical.

  S1 2.5D    the family at the lender's office; 2006 on the wall calendar          (environmental typography)
  S2 insert  the mortgage agreement: signed; the payment barely fits their income  (document close-up, before/after bar)
  S3 3D      their folder, stamped SOLD, is one of thousands in one strapped bundle (selective 3D, camera reveal)
  S4 map     investors worldwide buy it; payments flow to them steadily            (geographic map, flow diagram)
  S5 chart   US house prices peak in 2006 and fall                                  (animated chart)
  S6 2.5D    at home: the payment is overdue; her face falls                        (character + document prop)
  S7 map     the payments stop; the securities' value collapses                    (map reprise, before/after)
  S8 insert  September 2008: Lehman Brothers files for bankruptcy                  (newspaper close-up, timeline)
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "epoch-ledger/charlab/p11")); sys.path.insert(0, str(REPO / "epoch-ledger/charlab/p12"))
import visual_map as VM  # noqa: E402
import visuals as V  # noqa: E402
from kit.assemble import Scene  # noqa: E402

MAP = json.loads((REPO / "epoch-ledger/charlab/p12/map_p12.json").read_text())
RES = VM.resolve(MAP, VM.load_words(REPO / MAP["words"]))
E = {e["id"]: e["t"] for e in RES["events"]}
SH = {s["id"]: s for s in MAP["shots"]}

TITLE = "The Epoch Ledger · P12 validation · Sold on (2006–2008)"
EPISODE = "projects/charlab_p12/story"
NARRATION_WAV = "projects/charlab_p12/hf/narration.wav"
DURATION = MAP["duration"]
VIDEO = {"S1": "shotS1", "S2": "shotS2", "S3": "stack", "S6": "shotS6", "S8": "shotS8"}
SHOTS = [{"id": s["id"], "video": f".runtime/charlab/p12/{VIDEO[s['id']]}.mp4", "start": s["t0"], "duration": round(s["t1"] - s["t0"], 3)}
         for s in MAP["shots"] if s["id"] in VIDEO]
CSS = V.CSS + """
.ptag{position:absolute;left:56px;bottom:150px;padding:8px 14px;border-radius:6px;background:rgba(14,14,16,.55);font:600 20px Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#f6eedf}
"""
d = lambda k: SH[k]["t1"] - SH[k]["t0"]


def scenes(T):
    out = []
    s = SH["S1"]
    out.append(V.env_card("cal", s["t0"], d("S1"), top="MAY", big="2006", box=(800, 120, 170, 230), transform="rotateY(-6deg)", t_in=E["e02"]))
    out.append(Scene("tag", s["t0"], d("S1"), '<div class="ptag">Illustrative reconstruction</div>', js=""))
    s = SH["S2"]
    out.append(V.document("doc", s["t0"], d("S2"), title="MORTGAGE AGREEMENT",
                          fields=[("Borrowers", "The family"), ("Purpose", "Purchase of the family home")],
                          bar={"label": "Monthly payment against monthly income", "frac": .9, "t_fill": E["e06"], "t_left": E["e07"],
                               "left_text": "the mortgage payment", "left_label": "little left"},
                          sign_t=E["e05"], box=(650, 70, 640, 930), transform="rotateX(14deg) rotateZ(-4deg)", push=1.05, video="v_S2"))
    s = SH["S3"]
    out.append(V.label("mbs", s["t0"], d("S3"), kicker="Thousands of mortgages, one bundle", text="One mortgage-backed security",
                       box=(560, 70, 800), t_in=E["e12"], align="center"))
    s = SH["S4"]
    buyers = [("London", -0.13, 51.5, (-16, -16, "end")), ("Frankfurt", 8.68, 50.1, (18, 34, "start")), ("Hong Kong", 114.2, 22.3), ("Tokyo", 139.7, 35.7), ("Singapore", 103.8, 1.35)]
    out.append(V.world_map("mapa", s["t0"], d("S4"), origin=("United States", -74.0, 40.7), buyers=buyers,
                           title="The security is sold to investors worldwide", t_routes=E["e14"], t_buy=E["e15"], t_flow=E["e16"],
                           center=(22, 26), scale=6.4, highlight={"United States of America": "#c9a56a"}))
    s = SH["S5"]
    series = [(2000, 100), (2001, 108), (2002, 117), (2003, 128), (2004, 143), (2005, 164), (2006, 182), (2007, 178), (2008, 162),
              (2009, 143), (2010, 141), (2011, 135), (2012, 134)]
    out.append(V.line_chart("hpi", s["t0"], d("S5"), series=series, turn=2006, t_fall=E["e18"], title="US house prices",
                            note="Falling after 2006", ylabel="Index, 2000 = 100 (indicative)",
                            source="Indicative shape of the S&P/Case-Shiller U.S. National Home Price Index"))
    s = SH["S6"]
    out.append(V.document("notice", s["t0"], d("S6"), title="MORTGAGE PAYMENT", fields=[("Due", "This month"), ("Status", "Not received")],
                          box=(1080, 470, 620, 470), transform="rotateX(30deg) rotateZ(5deg)"))
    out.append(V.stamp("od", s["t0"], d("S6"), text="OVERDUE", box=(1300, 600, 300, 92), rotate=-8, t_in=E["e20"]))
    s = SH["S7"]
    out.append(V.world_map("mapb", s["t0"], d("S7"), origin=("United States", -74.0, 40.7), buyers=buyers,
                           title="The payments stop", t_dry=E["e22"], center=(22, 26), scale=6.4,
                           highlight={"United States of America": "#c9a56a"},
                           panel={"label": "Value of the securities", "t_before": E["e23"], "t_after": E["e24"], "at": (560, 560)}))
    s = SH["S8"]
    out.append(V.newspaper("np", s["t0"], d("S8"), masthead="THE EVENING LEDGER", date="Tuesday, September 16, 2008",
                           headline="Lehman Brothers files for bankruptcy", emph="bankruptcy",
                           deck="The investment bank, founded in 1850, makes the largest bankruptcy filing in U.S. history.",
                           t_head=E["e27"], t_emph=E["e28"], box=(560, 190, 800, 980), transform="rotateX(12deg) rotateZ(2deg)", video="v_S8",
                           timeline={"marks": [("2006", 0), ("2007", 1 / 3), ("2008", 2 / 3)], "to_frac": 32 / 36, "to_label": "September 2008",
                                     "t_move": E["e26"]}))
    return out
