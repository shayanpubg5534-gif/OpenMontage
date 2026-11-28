"""P13 storyboard: the hero key frames of the mortgage passage as HyperFrames stills, built with the production tools
(the kitchen plates and P10 compositor, three_shot.mjs, the P12 format library + P13 formats, gold captions from the
P12 narration). One composition, the frames placed at their narration times; scripts/still.mjs seeks each.

    python3 epoch-ledger/charlab/p13/board.py RUNTIME_DIR WS OUT_DIR
RUNTIME_DIR holds kf/kf1_signing.png, kf/kf6_bookend.png, shots/kf3_raw.png, shots/kf5_raw.png.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE.parent / "p12"), str(ROOT / "epoch-ledger")]
import formats as F  # noqa: E402
import visuals as V  # noqa: E402
from kit.assemble import assemble, prepare_workspace  # noqa: E402

EP = ROOT / "projects/charlab_p12/story/artifacts"        # the P12 narration, unchanged (read only)
SEN, MEZ, EQ = "#efe7d6", "#7f93ab", "#c98d4a"
# (id, film time of the still, window) — times from the P12 word timings (narration unchanged)
FRAMES = [("KF1", 3.10, (2.10, 5.30)), ("KF2", 10.30, (8.80, 11.00)), ("KF3", 11.90, (11.00, 12.50)),
          ("KF4", 16.40, (12.50, 17.20)), ("KF5", 23.40, (21.00, 24.20)), ("KF6", 27.60, (24.20, 30.00))]


def build(rt: Path, ws: Path):
    W = {k: w for k, _, w in FRAMES}; sc = []
    for name, src in (("kf1.png", rt / "kf/kf1_signing.png"), ("kf6.png", rt / "kf/kf6_bookend.png"),
                      ("kf3.png", rt / "shots/kf3_raw.png"), ("kf5.png", rt / "shots/kf5_raw.png")):
        (ws / "shots").mkdir(parents=True, exist_ok=True); shutil.copy(src, ws / "shots" / name)
    a, b = W["KF1"]
    sc.append(F.frame_overlay("k1", a, b - a, src="shots/kf1.png", push=(1.0, 1.04),
                              callouts=[("the mortgage", (700, 860), (930, 760), a + .5, V.GOLD)]))
    a, b = W["KF2"]
    sc.append(F.pool_map("k2", a, b - a, kicker="Sold on: thousands of loans, one pool", lender_label="lender",
                         pool_label=("THE POOL", "a trust: thousands of loans"), family_label="their loan",
                         t_lines=a + .1, t_pool=a + .8))
    a, b = W["KF3"]
    sc.append(F.frame_overlay("k3", a, b - a, src="shots/kf3.png", kicker="The security: one building, three tranches", push=(1.04, 1.0),
                              legend=[(SEN, "Senior: paid first"), (MEZ, "Mezzanine: paid next"), (EQ, "Equity: paid last")],
                              callouts=[("their loan, in the pool", (700, 860), (895, 960), a + .2, V.GOLD),
                                        ("payments rise, then fall floor by floor", (1880, 120), (1262, 40), a + .4, V.GREEN)]))
    a, b = W["KF4"]
    buyers = [("Oslo pension · senior", 10.75, 59.9, (18, -18, "start")), ("Frankfurt bank · senior", 8.68, 50.1, (18, 38, "start")),
              ("Tokyo insurer · senior", 139.7, 35.7, (-18, -22, "end")), ("London fund · mezzanine", -0.13, 51.5, (-16, -22, "end")),
              ("Hong Kong fund · mezzanine", 114.2, 22.3, (-18, 40, "end"))]
    sc.append(V.world_map("k4", a, b - a, origin=("Wall Street", -74.0, 40.7), buyers=buyers,
                          title="Each floor sold to a different investor", t_routes=a + .1, t_buy=a + .5, t_flow=a + .9,
                          center=(22, 30), scale=6.4, highlight={"United States of America": "#c9a56a"}))
    sc.append(V.label("k4l", a + 1.0, b - a - 1.0, kicker="through-line", text="Every payment starts at a kitchen table", box=(70, 700, 860), t_in=a + 1.0))
    a, b = W["KF5"]
    sc.append(F.frame_overlay("k5", a, b - a, src="shots/kf5.png", kicker="Losses rise from the bottom", push=(1.0, 1.03),
                              legend=[(SEN, "Senior: dry, but downgraded"), (MEZ, "Mezzanine: flooding"), (EQ, "Equity: wiped out")],
                              callouts=[("their house: payments stopped", (740, 860), (895, 968), a + .2, V.RED)]))
    a, b = W["KF6"]
    sc.append(F.frame_overlay("k6", a, b - a, src="shots/kf6.png", push=(1.02, 1.08),
                              callouts=[("the notice", (560, 600), (800, 700), a + .2, V.RED)]))
    sc.append(V.newspaper("k6n", 26.0, 4.0, masthead="THE EVENING LEDGER", date="Tuesday, September 16, 2008",
                          headline="Lehman Brothers files for bankruptcy", emph="bankruptcy", t_head=26.2, t_emph=26.8,
                          deck="The fourth-largest US investment bank collapses under mortgage losses.",
                          box=(930, 470, 1100, 760), transform="rotate(-5deg) scale(.56)", push=1.0))
    sc[-1].track = 3
    return sc


def main(rt, ws, out):
    rt, ws, out = Path(rt), Path(ws), Path(out); ws.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    prepare_workspace(ws)
    src = ROOT / "projects/charlab_p12/hf_final"
    for d in ("vendor", "fonts"):
        for f in (src / d).iterdir():
            (ws / d).mkdir(exist_ok=True); shutil.copy(f, ws / d / f.name)
    pages = json.loads((EP / "caption_phrases.json").read_text())
    html = assemble(title="P13 storyboard", duration=30.0, scenes=build(rt, ws), audio=None, caption_pages=pages, extra_css=V.CSS)
    (ws / "index.html").write_text(html)
    subprocess.run(["node", str(HERE / "stills.mjs"), str(ws / "index.html"), str(out)] + [f"{k}={t}" for k, t, _ in FRAMES], check=True)
    print(json.dumps({"frames": [k for k, _, _ in FRAMES], "out": str(out)}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
