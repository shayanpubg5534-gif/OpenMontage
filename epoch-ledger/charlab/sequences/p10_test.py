"""P10 narrated 2.5D test (16.5 s): "Ten thousand new dollars". Narrator-led (Kokoro voice-over, gold captions); the
characters act, they never lip-sync (narration standard). Three prerendered 2.5D shots (p10/compose.mjs) placed as video
clips (hf_sequence.py, opt-in `video` shots) under one financial motion graphic, keyed to the narration's word times.

Beats:
  A  medium two-shot  "A baker asks his bank for a loan of ten thousand dollars. No vault is opened..."
                      the baker explains with a real elbow gesture on "loan" and "ten thousand dollars"; the banker listens
  B  banker close-up  "...No cash changes hands. The banker simply records the loan, and credits his account."
                      the bank's balance sheet builds beside her: the loan appears as an asset on "loan", the baker's
                      deposit as a liability on "credits": both sides of the ledger, from one keystroke
  C  baker close-up   "Ten thousand new dollars now exist."  the new money counts up beside him; he smiles
"""
from kit.assemble import Scene

TITLE = "The Epoch Ledger · P10 2.5D narrated test · Ten thousand new dollars"
EPISODE = "projects/charlab_p10/story"
NARRATION_WAV = "projects/charlab_p10/hf/narration.wav"
DURATION = 16.5
CUTS = [0.0, 5.7, 11.75, 16.5]
SHOTS = [{"id": k, "video": f".runtime/charlab/p10/shot{k}.mp4", "start": CUTS[i], "duration": round(CUTS[i + 1] - CUTS[i], 3)}
         for i, k in enumerate("ABC")]

INK, GOLD, GREEN, MUTED = "#2b2118", "#c9963a", "#3d7a52", "#6b5a48"
CSS = f"""
.p10card{{position:absolute;padding:34px 40px 30px;border-radius:10px;background:rgba(251,247,238,.95);box-shadow:0 24px 60px rgba(25,12,4,.38);border:2px solid #cdbb98}}
.p10k{{font:700 19px Inter,sans-serif;letter-spacing:2.4px;text-transform:uppercase;color:#8a7a64}}
.p10h{{font:700 40px Fraunces,Georgia,serif;color:{INK};margin:6px 0 18px}}
.p10cols{{display:grid;grid-template-columns:1fr 1fr;gap:0 34px}}
.p10col{{border-top:3px solid {INK};padding-top:14px;min-height:150px}}
.p10ch{{font:700 18px Inter,sans-serif;letter-spacing:2px;color:{MUTED};margin-bottom:16px}}
.p10e{{font:600 25px Inter,sans-serif;color:{INK};opacity:0}}
.p10v{{font:700 38px Fraunces,Georgia,serif;color:{GREEN};margin-top:4px;font-variant-numeric:tabular-nums}}
.p10big{{font:700 96px Fraunces,Georgia,serif;color:{INK};font-variant-numeric:tabular-nums;line-height:1}}
.p10sub{{font:600 26px Inter,sans-serif;color:{MUTED};margin-top:14px}}
"""


def scenes(T):
    words = T["words"]

    def W(word, n=1):
        k = 0
        for w in words:
            if "".join(ch for ch in w["word"].lower() if ch.isalnum()).startswith(word):
                k += 1
                if k == n: return w["start"]
        raise KeyError(word)
    loan2, cred, tenk2, exist = W("loan", 2), W("credits"), W("10000", 2), W("exist")
    out = []
    # B: the bank's balance sheet beside the banker (left two-thirds of the frame; captions stay clear below)
    b0, b1 = W("records") - 0.3, CUTS[2]
    card = (f'<div id="bs" class="p10card" style="left:120px;top:110px;width:820px;opacity:0">'
            f'<div class="p10k">The bank\'s balance sheet</div><div class="p10h">One keystroke, two entries</div>'
            f'<div class="p10cols"><div class="p10col"><div class="p10ch">ASSETS</div><div id="ea" class="p10e">Loan to the baker<div class="p10v" id="va">+$0</div></div></div>'
            f'<div class="p10col"><div class="p10ch">LIABILITIES</div><div id="el" class="p10e">Baker\'s deposit<div class="p10v" id="vl">+$0</div></div></div></div></div>')
    js = (f"tl.fromTo('#bs',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.45,ease:MOTION.ease.enter,immediateRender:false}},{b0:.2f});"
          f"tl.fromTo('#ea',{{opacity:0,x:-16}},{{opacity:1,x:0,duration:.35,immediateRender:false}},{loan2 - .1:.2f});"
          f"mCount('#va',0,10000,{loan2:.2f},.7,{{prefix:'+$'}});"
          f"tl.fromTo('#el',{{opacity:0,x:16}},{{opacity:1,x:0,duration:.35,immediateRender:false}},{cred - .05:.2f});"
          f"mCount('#vl',0,10000,{cred + .05:.2f},.55,{{prefix:'+$'}});"
          f"tl.to('#bs',{{opacity:0,duration:.3}},{b1 - .3:.2f});")
    out.append(Scene("ledger", b0, b1 - b0, card, js=js))
    # C: the new money, beside the baker (right side)
    c0, c1 = CUTS[2] + 0.2, CUTS[3]
    card2 = (f'<div id="nm" class="p10card" style="left:1060px;top:150px;width:700px;opacity:0">'
             f'<div class="p10k">New money</div><div class="p10big" id="nv" style="margin-top:14px">$0</div>'
             f'<div class="p10sub" id="ns" style="opacity:0">created by the loan: no vault, no cash</div></div>')
    js2 = (f"tl.fromTo('#nm',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.45,ease:MOTION.ease.enter,immediateRender:false}},{c0:.2f});"
           f"mCount('#nv',0,10000,{tenk2:.2f},1.1,{{prefix:'$'}});"
           f"tl.fromTo('#nv',{{color:'{INK}'}},{{color:'{GOLD}',duration:.4,immediateRender:false}},{exist:.2f});"
           f"tl.fromTo('#ns',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.4,immediateRender:false}},{exist + .15:.2f});"
           f"tl.to('#nm',{{opacity:0,duration:.4}},{c1 - .45:.2f});")
    out.append(Scene("newmoney", c0, c1 - c0, card2, js=js2))
    return out
