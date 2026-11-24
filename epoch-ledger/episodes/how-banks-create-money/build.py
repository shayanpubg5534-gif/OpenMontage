"""Episode builder: How Banks Create Money (Epoch Ledger pilot, approved 2026-11-24).

Usage:  python epoch-ledger/episodes/how-banks-create-money/build.py [WORKSPACE]
Writes WORKSPACE/index.html (default: projects/how-banks-create-money/hyperframes).
Reads narration timing from this episode's artifacts/ and the shared kit.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[1]  # epoch-ledger/
sys.path.insert(0, str(KIT_ROOT))

from kit.characters import OUT, banker_svg, maya_svg  # noqa: E402
from kit.sets import (bank_keyboard, bank_street, bokeh, credit_gauge, ledger_sheet,  # noqa: E402
                      office_background, office_foreground, street_foreground)

WORKSPACE = Path(sys.argv[1]) if len(sys.argv) > 1 else KIT_ROOT.parent / "projects" / "how-banks-create-money" / "hyperframes"
timing = json.loads((HERE / "artifacts" / "narration_timing.json").read_text())
D = timing["total"]

street_svg = bank_street()
street_fg = street_foreground()
office_bg = office_background()
office_fg = office_foreground()
gauge = credit_gauge()
ledger_svg = ledger_sheet()
keyboard_svg = bank_keyboard()
bokeh = bokeh()

css = """
@font-face{font-family:Fraunces;font-weight:600;src:url(fonts/fraunces-latin-600-normal.woff2) format('woff2')}
@font-face{font-family:Fraunces;font-weight:800;src:url(fonts/fraunces-latin-800-normal.woff2) format('woff2')}
@font-face{font-family:Inter;font-weight:500;src:url(fonts/inter-latin-500-normal.woff2) format('woff2')}
@font-face{font-family:Inter;font-weight:700;src:url(fonts/inter-latin-700-normal.woff2) format('woff2')}
:root{--ink:#14213d;--parch:#f4ead5;--brass:#d4a24c;--green:#2f7d5b;--teal:#1f7a78;--coral:#e0603a}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#0b0f17}
#root{position:relative;width:1920px;height:1080px;font-family:Inter,sans-serif;color:var(--ink)}
.clip{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden}
.cam{position:absolute;inset:0;transform-origin:50% 50%}
.full{position:absolute;left:0;top:0;width:1920px;height:1080px}
.char{position:absolute;overflow:visible}
.label{font-family:Inter;font-weight:700;letter-spacing:.18em;text-transform:uppercase;font-size:20px}
.serif{font-family:Fraunces;font-weight:800}
#gl{position:absolute;left:0;top:0;width:1920px;height:1080px}
.vignette{background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 55%,rgba(5,8,14,.55) 100%);pointer-events:none}
/* scene 1 */
#myth{position:absolute;left:110px;top:100px;width:820px;text-shadow:0 4px 24px rgba(0,0,0,.9)}
#myth .label{color:#d4a24c}
#myth h2{font-family:Fraunces;font-weight:800;font-size:76px;line-height:1.02;color:#f4ead5;margin-top:14px;position:relative;display:inline-block}
#myth-strike{position:absolute;left:-8px;right:-8px;top:52%;height:9px;background:#e0603a;border-radius:6px;transform-origin:0 50%}
#myth-x{position:absolute;left:760px;top:150px;width:110px;height:110px;border:7px solid #e0603a;border-radius:50%;color:#e0603a;font:800 66px/96px Fraunces;text-align:center}
#myth-true{font-family:Fraunces;font-weight:600;font-style:normal;font-size:40px;color:#9cc9e6;margin-top:26px}
/* scene 2 */
#s2-maya{left:150px;top:418px;width:270px;height:450px}
#s2-tag{position:absolute;left:120px;top:300px;background:#14213d;color:#f4ead5;border-radius:14px;padding:12px 20px;border:3px solid #d4a24c;white-space:nowrap}
#s2-tag b{font-family:Fraunces;font-size:34px;display:block}
#s2-bubble{position:absolute;left:640px;top:232px;background:#fff;border:4px solid #1b2230;border-radius:28px;padding:18px 28px;font:800 40px Fraunces;color:#14213d;white-space:nowrap;box-shadow:0 8px 0 rgba(27,34,48,.18)}
#s2-bubble:after{content:"";position:absolute;left:180px;bottom:-26px;border:14px solid transparent;border-top:18px solid #1b2230}
/* scene 3 */
#s3-maya{left:420px;top:330px;width:330px;height:396px}
#s3-banker{left:1060px;top:250px;width:420px;height:490px}
.card{position:absolute;background:#fffaf0;border:4px solid #1b2230;border-radius:20px;box-shadow:0 14px 0 rgba(27,34,48,.18)}
#s3-gauge{left:790px;top:70px;width:290px;height:250px;padding:16px}
#s3-gauge .card-svg{width:256px;height:176px;display:block}
#s3-score{font:800 44px Fraunces;text-align:center;margin-top:-6px}
#s3-good{position:absolute;right:14px;top:14px;background:#2f7d5b;color:#fff;border-radius:10px;padding:4px 10px;font-size:16px}
#s3-doc{left:800px;top:340px;width:250px;height:250px;padding:22px}
#s3-doc .ln{height:12px;background:#e2d7c1;border-radius:6px;margin:12px 0}
#s3-stamp{position:absolute;left:14px;top:96px;border:6px solid #c0392b;color:#c0392b;border-radius:12px;padding:6px 14px;font:800 40px Fraunces;letter-spacing:.06em;transform:rotate(-12deg)}
#s3-book{left:650px;top:230px;width:620px;height:360px;background:#f7f0de;padding:0;overflow:hidden}
#s3-book .spine{position:absolute;left:306px;top:0;bottom:0;width:8px;background:#c9b48c}
#s3-book .hd{position:absolute;top:26px;font:700 18px Inter;letter-spacing:.16em;color:#7a6a4c}
.bookline{position:absolute;font:600 24px Fraunces;white-space:nowrap}
.bookline i{position:absolute;left:0;bottom:-8px;height:5px;width:100%;border-radius:4px;transform-origin:0 50%}
/* scene 4 */
#s4{background:radial-gradient(ellipse at 50% 40%,#f7efdc 0%,#ecdfc2 70%,#e0cfab 100%)}
#s4-title{position:absolute;left:0;right:0;top:120px;text-align:center;color:#7a6a4c}
.colhead{position:absolute;top:262px;width:640px;text-align:center}
.colhead b{display:block;font:800 46px Fraunces;color:#14213d}
.colhead span{font:500 22px Inter;color:#7a6a4c}
.row{position:absolute;top:470px;width:620px;display:flex;align-items:center;gap:20px}
.row .amt{margin-left:auto;font:800 50px Fraunces}
.row .txt{font:600 34px Fraunces;line-height:1.1}
.row .txt small{display:block;font:500 20px Inter;color:#7a6a4c;margin-top:4px}
.badge{position:absolute;width:56px;height:56px;border-radius:50%;background:#14213d;color:#f4ead5;font:800 30px/56px Fraunces;text-align:center}
.av{width:74px;height:74px;border-radius:50%;background:#1f7a78;border:4px solid #1b2230;overflow:hidden;position:relative;flex:none}
#s4-iou{left:300px;top:640px;width:330px;padding:16px 22px;transform:rotate(-4deg)}
#s4-iou p{font:600 24px Fraunces}
#s4-check{position:absolute;left:0;right:0;top:800px;text-align:center;font:700 26px Inter;color:#2f7d5b;letter-spacing:.08em}
#s4-tag{position:absolute;left:800px;top:740px;width:320px;text-align:center;font:700 20px Inter;color:#9c7a30;letter-spacing:.14em;text-transform:uppercase}
/* scene 5 */
#s5{background:linear-gradient(160deg,#14213d 0%,#173a4a 60%,#1f5a5a 100%)}
#s5-typed{position:absolute;left:150px;top:470px;width:680px;height:70px;border-radius:14px;background:#0e1626;border:3px solid #3f5273;overflow:hidden}
#s5-typed span{position:absolute;left:20px;top:16px;font:700 28px Inter;color:#7fe0c4;white-space:nowrap;letter-spacing:.04em}
#s5-cursor{position:absolute;left:20px;top:14px;width:4px;height:40px;background:#7fe0c4}
#s5-phone{position:absolute;left:1040px;top:150px;width:300px;height:610px;border-radius:44px;background:#0e1626;border:6px solid #1b2230;box-shadow:0 0 0 10px #2b3a52,0 30px 60px rgba(0,0,0,.4)}
#s5-screen{position:absolute;left:14px;top:14px;right:14px;bottom:14px;border-radius:32px;background:linear-gradient(180deg,#f7f3ea,#eae2cf);padding:44px 22px;overflow:hidden}
#s5-bal{font:800 40px Fraunces;color:#14213d;margin-top:8px;font-variant-numeric:tabular-nums}
#s5-tx{position:absolute;left:18px;right:18px;top:300px;background:#fff;border-radius:16px;padding:14px;border:2px solid #d9ccb0}
#s5-tx b{display:block;font:700 18px Inter}
#s5-tx span{font:800 26px Fraunces;color:#2f7d5b}
#s5-maya{left:1380px;top:340px;width:470px;height:564px;transform:scaleX(-1)}
/* scene 6 overlays */
#s6-lock{position:absolute;left:110px;top:100px;color:#f4ead5;text-shadow:0 4px 24px rgba(0,0,0,.9)}
#s6-lock .label{color:#e0603a}
#s6-eq{position:absolute;left:0;right:0;top:70px;padding:24px 0 40px;background:linear-gradient(180deg,rgba(8,11,18,.85),rgba(8,11,18,0));text-shadow:0 4px 24px rgba(0,0,0,.9);text-align:center;color:#f4ead5;font:800 64px Fraunces;white-space:nowrap}
#s6-eq span{display:inline-block;margin:0 14px}
#s6-eq .gold{color:#f2c66d}
#s6-brand{position:absolute;right:70px;top:60px;color:#d4a24c;opacity:.9}
"""

segs = timing["segments"]

html = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="vendor/gsap.min.js"></script>
<script src="vendor/three.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1920" data-height="1080">

 <canvas id="gl" class="clip" data-start="0" data-duration="{D}" data-track-index="0" width="1920" height="1080"></canvas>

 <div id="s1" class="clip" data-start="0" data-duration="4.75" data-track-index="1">
  <div id="myth">
   <div class="label">The common belief</div>
   <h2 id="myth-h">Your loan is other people’s savings<div id="myth-strike"></div></h2>
   <div id="myth-true">So where does the money come from?</div>
  </div>
  <div id="myth-x">✕</div>
 </div>

 <div id="s2" class="clip" data-start="4.45" data-duration="5.35" data-track-index="2">
  <div id="s2-cam" class="cam">
   {street_svg}
   <div id="s2-maya-wrap" style="position:absolute;left:0;top:0;width:1920px;height:1080px">
    {maya_svg("m2", "walk").replace('class="char "', 'class="char" style="left:150px;top:418px;width:270px;height:450px"')}
    <div id="s2-tag" style="left:120px;top:300px"><span class="label" style="font-size:14px;color:#d4a24c">The customer</span><b>Maya</b></div>
   </div>
   {street_fg}
   <div id="s2-bubble">“A $10,000 loan, please.”</div>
  </div>
 </div>

 <div id="s3" class="clip" data-start="9.5" data-duration="5.8" data-track-index="3">
  <div id="s3-cam" class="cam">
   {office_bg}
   {banker_svg("b3").replace('class="char "', 'class="char" style="left:1060px;top:250px;width:420px;height:490px"')}
   {maya_svg("m3", "bust").replace('class="char "', 'class="char" style="left:390px;top:286px;width:380px;height:456px"')}
   {office_fg}
   <div id="s3-gauge" class="card"><div class="label" style="font-size:15px;color:#7a6a4c">Credit check</div>{gauge}<div id="s3-score">300</div><div id="s3-good" class="label">Good</div></div>
   <div id="s3-doc" class="card"><div class="label" style="font-size:15px;color:#7a6a4c">Loan application</div>
     <div class="serif" style="font-size:30px;margin-top:6px">$10,000</div><div class="ln"></div><div class="ln" style="width:70%"></div><div class="ln" style="width:85%"></div>
     <div id="s3-stamp">APPROVED</div></div>
   <div id="s3-book" class="card"><div class="spine"></div>
     <div class="hd" style="left:40px">Assets</div><div class="hd" style="left:340px">Liabilities</div>
     <div class="bookline" id="s3-l1" style="left:40px;top:150px">Loan to Maya&nbsp;&nbsp;10,000<i style="background:#2f7d5b"></i></div>
     <div class="bookline" id="s3-l2" style="left:340px;top:230px">Maya’s deposit&nbsp;&nbsp;10,000<i style="background:#e0603a"></i></div>
   </div>
  </div>
 </div>

 <div id="s4" class="clip" data-start="15.0" data-duration="6.15" data-track-index="4">
  <div id="s4-cam" class="cam">
   <div id="s4-title" class="label">Ledger Bank · balance sheet</div>
   <div class="colhead" style="left:320px"><b>Assets</b><span>what the bank is owed</span></div>
   <div class="colhead" style="left:960px"><b>Liabilities</b><span>what the bank owes</span></div>
   {ledger_svg}
   <div class="badge" id="s4-b1" style="left:226px;top:478px">1</div>
   <div class="row" id="s4-r1" style="left:300px">
     <div class="av">{maya_svg("m4a", "bust").replace('class="char "', 'class="char" style="left:-34px;top:-14px;width:140px;height:168px"')}</div>
     <div class="txt">Loan to Maya<small>her promise to repay</small></div><div class="amt" style="color:#2f7d5b">+$10,000</div></div>
   <div class="badge" id="s4-b2" style="left:1676px;top:478px">2</div>
   <div class="row" id="s4-r2" style="left:1030px">
     <div class="av" style="background:#e0603a">{maya_svg("m4b", "bust").replace('class="char "', 'class="char" style="left:-34px;top:-14px;width:140px;height:168px"')}</div>
     <div class="txt">Maya’s deposit<small>money in her account</small></div><div class="amt" style="color:#e0603a">+$10,000</div></div>
   <div id="s4-iou" class="card"><div class="label" style="font-size:14px;color:#7a6a4c">IOU</div><p>“I promise to repay $10,000.”</p>
     <svg viewBox="0 0 240 50" width="240" height="50"><path id="s4-sig" d="M8 34 C30 4 40 46 60 22 S90 10 100 30 S140 40 150 18 S190 26 230 20" stroke="#1f3a7a" stroke-width="4" fill="none" stroke-linecap="round"/></svg></div>
   <div id="s4-tag">Written at the same moment</div>
   <div id="s4-check">ASSETS = LIABILITIES ✓</div>
  </div>
 </div>

 <div id="s5" class="clip" data-start="20.7" data-duration="4.95" data-track-index="5">
  <div id="s5-cam" class="cam">
   <svg viewBox="0 0 1920 1080" class="full">{bokeh}</svg>
   <div class="label" style="position:absolute;left:150px;top:420px;color:#9cc9e6;font-size:16px">Bank terminal</div>
   <div id="s5-typed"><span id="s5-text">CREDIT ACCT 4417 · MAYA · +10,000.00</span><div id="s5-cursor"></div></div>
   {keyboard_svg}
   <div id="s5-phone"><div id="s5-screen">
     <div class="label" style="font-size:13px;color:#7a6a4c">Ledger Bank · Current account</div>
     <div id="s5-bal">$0.00</div>
     <div class="label" style="font-size:12px;color:#7a6a4c;margin-top:2px">Available balance</div>
     <div id="s5-tx"><b>Loan proceeds</b><span>+$10,000.00</span></div>
   </div></div>
   {maya_svg("m5", "phone").replace('class="char "', 'class="char" style="left:1380px;top:340px;width:470px;height:564px;transform:scaleX(-1)"')}
  </div>
 </div>

 <div id="s6" class="clip" data-start="25.2" data-duration="{round(D-25.2, 2)}" data-track-index="6">
  <div id="s6-lock"><div class="label">Vault status</div><div class="serif" style="font-size:52px;margin-top:6px">Sealed · untouched</div></div>
  <div id="s6-eq"><span id="e1">Loan</span><span id="e2" class="gold">→</span><span id="e3">Deposit</span><span id="e4" class="gold">= new money</span></div>
  <div id="s6-brand" class="label">The Epoch Ledger</div>
 </div>

 <div id="vig" class="clip vignette" data-start="0" data-duration="{D}" data-track-index="7"></div>
 <audio id="vo" src="narration.wav" data-start="0" data-duration="{D}" data-track-index="8"></audio>
</div>
<script>
{(HERE / "scene.js").read_text().replace("__D__", str(D))}
</script>
</body></html>
"""

WORKSPACE.mkdir(parents=True, exist_ok=True)
(WORKSPACE / "index.html").write_text(html)
print("wrote index.html", len(html))
