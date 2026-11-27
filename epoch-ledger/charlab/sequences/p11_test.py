"""P11 narration-driven re-direction of the P10 test (same narration, 16.5 s). Every clause is SHOWN when it is said:
all visual times come from the narration-to-visual map (charlab/p11/map_p11.json), resolved against the narration's real
word timestamps, so the graphics below and the character actions in the 2.5D shots share one source of timing.

  S1  2.5D two-shot   "A baker asks his bank"        the loan application slides across the desk; the banker looks down, nods
  S2  insert, above   "for a loan of $10,000."       the form: LOAN APPLICATION; the amount is written as it is said; underlined
  S3  3D vault        "No vault is opened, no cash changes hands."  the gate stays locked (SEALED); the camera moves past
                      the lock to the cash inside: untouched
  S4  2.5D close-up   "The banker simply records the loan and credits his account."  she types; her screen: the loan
                      becomes an asset, the deposit a liability, balanced
  S5  2.5D close-up   "10,000 new dollars now exist."  his balance counts to $10,000; deposits grow by a new $10,000 while
                      vault cash is unchanged: new money, created by the loan
Narrator-led: Kokoro voice-over, gold captions, no lip sync.
"""
import json
import sys
from pathlib import Path

from kit.assemble import Scene

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "epoch-ledger/charlab/p11"))
import visual_map as VM  # noqa: E402

MAP = json.loads((REPO / "epoch-ledger/charlab/p11/map_p11.json").read_text())
RES = VM.resolve(MAP, VM.load_words(REPO / MAP["words"]))
E = {e["id"]: e["t"] for e in RES["events"]}
SHOT = {s["id"]: s for s in MAP["shots"]}

TITLE = "The Epoch Ledger · P11 narration-driven test · Ten thousand new dollars"
EPISODE = "projects/charlab_p10/story"                    # the same narration as P10 (controlled comparison)
NARRATION_WAV = "projects/charlab_p10/hf/narration.wav"
DURATION = MAP["duration"]
VIDEO = {"S1": ".runtime/charlab/p11/shotS1.mp4", "S2": ".runtime/charlab/p11/shotS2.mp4", "S3": ".runtime/charlab/p11/vault.mp4",
         "S4": ".runtime/charlab/p11/shotS4.mp4", "S5": ".runtime/charlab/p11/shotS5.mp4"}
SHOTS = [{"id": s["id"], "video": VIDEO[s["id"]], "start": s["t0"], "duration": round(s["t1"] - s["t0"], 3)} for s in MAP["shots"]]

INK, GOLD, GREEN, MUTED, PAPER = "#2b2118", "#c9963a", "#3d7a52", "#6b5a48", "#fbf7ee"
CSS = f"""
.card{{position:absolute;padding:22px 28px;border-radius:10px;background:rgba(251,247,238,.95);box-shadow:0 18px 44px rgba(25,12,4,.36);border:2px solid #cdbb98}}
.kick{{font:700 17px Inter,sans-serif;letter-spacing:2.4px;text-transform:uppercase;color:#8a7a64}}
.big{{font:700 40px Fraunces,Georgia,serif;color:{INK};margin-top:4px}}
.row{{font:600 30px Inter,sans-serif;color:{INK};display:flex;justify-content:space-between;gap:24px;opacity:0}}
.val{{font:700 42px Fraunces,Georgia,serif;color:{GREEN};font-variant-numeric:tabular-nums}}
.form{{position:absolute;background:#f8f3e8;box-shadow:0 10px 26px rgba(20,10,4,.45);border-radius:3px}}
.fl{{font:600 19px Inter,sans-serif;color:#5a4a3a;letter-spacing:1px}}
.screen{{position:absolute;left:90px;top:150px;width:860px;height:470px;border-radius:14px;background:#20242a;box-shadow:0 26px 60px rgba(10,6,2,.5);border:3px solid #111}}
.scr{{position:absolute;inset:16px;border-radius:8px;background:#f6f4ee;overflow:hidden}}
.bar{{position:absolute;height:56px;border-radius:6px}}
"""


def scenes(T):
    out = []
    t = lambda k, a=0.0: round(E[k] + a, 3)

    # ── S1: the application slides across the desk (between the two of them), toward the banker ───────────────────────
    s = SHOT["S1"]
    form1 = ('<div id="f1w" style="position:absolute;left:0;top:0;width:1920px;height:1080px;perspective:900px">'
             '<div id="f1" class="form" style="left:610px;top:812px;width:150px;height:118px;transform:rotateX(60deg) rotateZ(-8deg);'
             'transform-origin:50% 100%;padding:8px 10px;box-sizing:border-box">'
             '<div style="font:800 11px Inter;color:#3a2f25;letter-spacing:.6px">LOAN APPLICATION</div>'
             '<div style="margin-top:8px;height:3px;background:#cbbfa8"></div><div style="margin-top:7px;height:3px;width:70%;background:#cbbfa8"></div>'
             '<div style="margin-top:7px;height:3px;width:85%;background:#cbbfa8"></div></div></div>')
    js = (f"tl.fromTo('#f1',{{x:0,y:0,rotationZ:-8}},{{x:300,y:-14,rotationZ:4,duration:.75,ease:'power2.inOut',immediateRender:false}},{t('e02')});")
    out.append(Scene("S1form", s["t0"], s["t1"] - s["t0"], form1, js=js))

    # ── S2: the form, from above: the amount is written as it is said, then underlined and marked requested ───────────
    s = SHOT["S2"]
    form2 = ('<div id="f2w" style="position:absolute;inset:0;perspective:1600px">'
             '<div id="f2" class="form" style="left:640px;top:150px;width:600px;height:790px;transform:rotateX(16deg) rotateZ(-5deg);transform-origin:50% 60%;padding:46px 54px;box-sizing:border-box">'
             f'<div style="font:800 34px Fraunces,Georgia,serif;color:{INK};letter-spacing:.5px">LOAN APPLICATION</div>'
             '<div style="height:3px;background:#3a2f25;margin:16px 0 28px"></div>'
             '<div class="fl">APPLICANT</div><div style="font:600 30px Inter;color:#2b2118;margin:6px 0 22px">The baker</div>'
             '<div class="fl">BUSINESS</div><div style="font:600 30px Inter;color:#2b2118;margin:6px 0 34px">Bakery</div>'
             '<div class="fl">AMOUNT REQUESTED</div>'
             '<div style="position:relative;height:110px;margin-top:6px">'
             '<div id="amt" style="position:absolute;left:0;top:0;font:italic 700 84px Fraunces,Georgia,serif;color:#1f3a6b;clip-path:inset(0 100% 0 0)">$10,000</div>'
             f'<div id="und" style="position:absolute;left:0;top:100px;height:6px;width:330px;background:{GOLD};transform:scaleX(0);transform-origin:0 50%"></div></div>'
             f'<div id="req" style="margin-top:34px;display:inline-block;padding:8px 18px;border:4px solid {GOLD};border-radius:6px;font:800 26px Inter;color:{GOLD};letter-spacing:3px;opacity:0;transform:rotate(-6deg)">REQUESTED</div>'
             '</div></div>')
    js = (f"tl.fromTo(['#v_S2','#f2w'],{{scale:1}},{{scale:1.05,transformOrigin:'50% 55%',duration:{s['t1'] - s['t0']:.2f},ease:'sine.inOut',immediateRender:false}},{s['t0']:.2f});"
          +f"tl.fromTo('#amt',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.6,ease:'none',immediateRender:false}},{t('e05', -.05)});"   # written at the pace it is said
          + f"tl.fromTo('#und',{{scaleX:0}},{{scaleX:1,duration:.3,ease:'power2.out',immediateRender:false}},{t('e06')});"
          + f"tl.fromTo('#req',{{opacity:0,scale:1.4}},{{opacity:1,scale:1,duration:.25,ease:'back.out(2)',immediateRender:false}},{t('e06', .2)});")
    out.append(Scene("S2form", s["t0"], s["t1"] - s["t0"], form2, js=js))

    # ── S3: vault status (sealed, not opened), then the cash inside: untouched ─────────────────────────────────────────
    s = SHOT["S3"]
    lock = ('<svg width="34" height="38" viewBox="0 0 34 38" style="vertical-align:-6px;margin-right:12px"><rect x="3" y="16" width="28" height="20" rx="4" fill="#9e2a22"/>'
            '<path d="M9 16 V11 a8 8 0 0 1 16 0 V16" stroke="#9e2a22" stroke-width="5" fill="none"/></svg>')
    vs = (f'<div id="vs" class="card" style="left:110px;top:90px;opacity:0"><div class="kick">The vault</div><div class="big">{lock}Sealed · not opened</div></div>'
          f'<div id="vc" class="card" style="left:1170px;top:90px;width:560px;opacity:0"><div class="kick">Vault cash</div>'
          f'<div class="big">The cash stays put</div><div id="vu" style="margin-top:10px;font:700 26px Inter;color:{GREEN};opacity:0">✓ Untouched: no cash changes hands</div></div>')
    js = (f"tl.fromTo('#vs',{{opacity:0,y:-14}},{{opacity:1,y:0,duration:.35,immediateRender:false}},{t('e09')});"
          f"tl.to('#vs',{{opacity:0,duration:.3}},{t('e10', -.1)});"
          f"tl.fromTo('#vc',{{opacity:0,y:-14}},{{opacity:1,y:0,duration:.35,immediateRender:false}},{t('e11')});"
          f"tl.fromTo('#vu',{{opacity:0,x:-10}},{{opacity:1,x:0,duration:.3,immediateRender:false}},{t('e12')});")
    out.append(Scene("S3labels", s["t0"], s["t1"] - s["t0"], vs, js=js))

    # ── S4: her screen: the ledger entry is typed; the loan is an asset, the deposit a liability; balanced ─────────────
    s = SHOT["S4"]
    scr = ('<div id="sc" class="screen" style="opacity:0"><div class="scr" style="padding:30px 36px;box-sizing:border-box">'
           '<div style="display:flex;justify-content:space-between;align-items:center"><div class="kick">Bank ledger · new entry</div>'
           '<div style="width:12px;height:12px;border-radius:6px;background:#3d7a52"></div></div>'
           f'<div id="ty" style="margin-top:14px;font:600 30px ui-monospace,Menlo,monospace;color:{INK};white-space:nowrap;overflow:hidden;width:0">New loan: the baker, $10,000</div>'
           f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0 30px;margin-top:26px">'
           f'<div style="border-top:3px solid {INK};padding-top:12px"><div class="kick" style="margin-bottom:14px">Assets</div>'
           f'<div id="ra" class="row" style="flex-direction:column;gap:4px">Loan to the baker<span id="va" class="val">+$10,000</span></div></div>'
           f'<div style="border-top:3px solid {INK};padding-top:12px"><div class="kick" style="margin-bottom:14px">Liabilities</div>'
           f'<div id="rl" class="row" style="flex-direction:column;gap:4px">Baker\'s deposit<span id="vl" class="val">+$10,000</span></div></div></div>'
           f'<div id="bal" style="margin-top:30px;padding:14px 18px;border-radius:8px;background:rgba(201,150,58,.14);border:2px solid {GOLD};font:700 26px Inter;color:{INK};opacity:0">'
           f'One loan, one deposit: <span style="color:{GOLD}">both sides +$10,000</span></div></div></div>'
           '<svg style="position:absolute;inset:0" width="1920" height="1080"><path id="lk" d="M952 470 C1060 500 1100 650 1150 760" stroke="#f6f4ee" stroke-width="3" stroke-dasharray="7 7" fill="none" opacity="0"/></svg>')
    js = (f"tl.fromTo('#sc',{{opacity:0,scale:.92,transformOrigin:'100% 70%'}},{{opacity:1,scale:1,duration:.35,ease:'power2.out',immediateRender:false}},{t('e14')});"
          f"tl.to('#lk',{{opacity:.8,duration:.3}},{t('e14')});"
          f"tl.fromTo('#ty',{{width:0}},{{width:520,duration:{max(.4, t('e15') - t('e14') - .2):.2f},ease:'steps(28)',immediateRender:false}},{t('e14', .15)});"
          f"tl.fromTo('#ra',{{opacity:0,y:12}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t('e15')});"
          f"tl.fromTo('#rl',{{opacity:0,y:12}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t('e16')});"
          f"tl.fromTo('#bal',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t('e17')});")
    out.append(Scene("S4screen", s["t0"], s["t1"] - s["t0"], scr, js=js))

    # ── S5: his balance; then what it means: deposits grow by a new $10,000, vault cash unchanged ──────────────────────
    s = SHOT["S5"]
    ph = (f'<div id="ph" class="card" style="left:900px;top:520px;width:300px;opacity:0;border-radius:22px;background:#f6f4ee">'
          f'<div class="kick">His account</div><div id="pb" class="big" style="font-size:54px;font-variant-numeric:tabular-nums">$0</div>'
          f'<div style="font:600 20px Inter;color:{GREEN};margin-top:6px">Deposit · loan funds</div></div>'
          '<svg style="position:absolute;inset:0" width="1920" height="1080"><path id="pl" d="M905 640 C860 700 840 760 820 840" stroke="#f6f4ee" stroke-width="3" stroke-dasharray="7 7" fill="none" opacity="0"/></svg>')
    dg = (f'<div id="dg" class="card" style="left:1250px;top:130px;width:590px;opacity:0;box-sizing:border-box">'
          f'<div class="kick">Money in the economy</div>'
          f'<div style="font:600 24px Inter;color:{MUTED};margin-top:26px">Bank deposits</div>'
          f'<div style="position:relative;height:56px;margin-top:8px"><div class="bar" style="left:0;width:290px;background:#7d8a96"></div>'
          f'<div id="dn" class="bar" style="left:290px;width:90px;background:{GOLD};transform:scaleX(0);transform-origin:0 50%"></div>'
          f'<div id="dl" style="position:absolute;left:402px;top:10px;font:700 28px Fraunces;color:{GOLD};opacity:0">+$10,000</div></div>'
          f'<div id="cr" style="opacity:0"><div style="font:600 24px Inter;color:{MUTED};margin-top:30px">Vault cash</div>'
          f'<div style="position:relative;height:56px;margin-top:8px"><div class="bar" style="left:0;width:220px;background:#7d8a96"></div>'
          f'<div style="position:absolute;left:236px;top:12px;font:700 26px Inter;color:{MUTED}">unchanged</div></div></div>'
          f'<div id="nm" style="margin-top:40px;padding:16px 20px;border-radius:8px;border:2px solid {GOLD};background:rgba(201,150,58,.14);font:700 30px Fraunces;color:{INK};opacity:0">'
          f'New money: <span style="color:{GOLD}">created by the loan</span></div></div>')
    js = (f"tl.fromTo('#ph',{{opacity:0,y:16}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t('e19', -.12)});tl.to('#pl',{{opacity:.8,duration:.3}},{t('e19', -.12)});"
          f"mCount('#pb',0,10000,{t('e19')},.8,{{prefix:'$'}});"
          f"tl.fromTo('#dg',{{opacity:0,x:24}},{{opacity:1,x:0,duration:.3,immediateRender:false}},{t('e20', -.1)});"
          f"tl.fromTo('#dn',{{scaleX:0}},{{scaleX:1,duration:.45,ease:'power2.out',immediateRender:false}},{t('e20')});"
          f"tl.fromTo('#dl',{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{t('e20', .3)});"
          f"tl.fromTo('#cr',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t('e21')});"
          f"tl.fromTo('#nm',{{opacity:0,scale:.95}},{{opacity:1,scale:1,duration:.35,ease:'back.out(1.6)',immediateRender:false}},{t('e22')});"
          f"tl.to(['#ph','#pl','#dg'],{{opacity:0,duration:.4}},{s['t1'] - .45:.2f});")
    out.append(Scene("S5graphics", s["t0"], s["t1"] - s["t0"], ph + dg, js=js))
    return out
