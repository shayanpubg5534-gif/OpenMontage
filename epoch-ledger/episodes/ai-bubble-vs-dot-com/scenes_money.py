"""Money-flow ecosystem 7:15–8:38 (storyboard s040–s042): a 3D economy that builds with the narration.

Semantic sync: every object and action starts on the Whisper time of the word that names it (the
platform on "imagine", the fab on "semiconductor", chips flowing on "purchases", ...), never at the
end of a sentence. A staged perspective camera frames each subject as it is named.
"""
import json

from kit.assemble import Scene
from timeline import L, W


def build():
    l = {k: L(k) for k in [f"c05_{i:02d}" for i in range(1, 17)]}
    s, e = l["c05_01"][0] - .4, l["c05_15"][1] + .6
    w_imag, w_simp, w_econ = W("imagine", "c05_01"), W("simplified", "c05_01"), W("economy", "c05_01")
    r = {"fab": W("semiconductor", "c05_02"), "cloud": W("cloud", "c05_03"), "lab": W("AI", "c05_04"), "cust": W("businesses", "c05_05")}
    flow = [W("purchases", "c05_03"), W("rents", "c05_04"), W("use", "c05_05")]
    w_pay, w_money = W("pay", "c05_05"), W("Money", "c05_06")
    grow = {"cust": W("expands", "c05_07"), "fab": W("sell", "c05_08"), "cloud": W("rent", "c05_09"), "lab": W("attract", "c05_10")}
    w_fin = W("finance", "c05_12")
    w_inv, w_dev, w_purch = W("investing", "c05_13"), W("developer", "c05_14"), W("purchases", "c05_15")
    loop = [w_inv, w_dev + .2, w_purch, l["c05_15"][1] - .3]
    # Staged camera beats: (word time, position, look-at, fov). The move starts ~1.1 s before the word so
    # the subject is framed as it is named; between beats a slow push-in keeps the shot alive.
    beats = [
        (s, (22, 12, 26), (0, 0, 0), 44),                       # low sweep over the platform as it assembles
        (w_imag, (16, 26, 28), (0, 0, 0), 42),                  # four empty plots appear on "imagine"
        (w_econ, (14, 21, 24), (0, 0, 0), 40),
        (r["fab"], (-2.5, 4.5, 6.5), (-9, 1.2, -3), 38),        # INTRO fab (then cutaway: production)
        (r["cloud"], (2, 6.5, 11), (-3, 1, 2.5), 40),           # INTRO cloud
        (flow[0], (-1, 8, 11), (-6, 1, 0), 42),                 # TRANSACTION chips → cloud, money ← (then cutaway: install)
        (r["lab"], (10, 4.5, 4), (3.5, 1.8, -2.5), 36),         # INTRO AI developer
        (flow[1], (6, 9, 11), (0, 1, 0), 42),                   # TRANSACTION capacity → lab, rent ← (then cutaway: train/operate)
        (r["cust"], (5, 2.2, 10.5), (9, 1, 2.5), 42),           # INTRO customers (then cutaway: use + pay)
        (w_money, (18, 24, 26), (0, 0, 0), 40),                 # overview: money moves through the system
        (grow["cust"], (15, 6, 11), (9, .5, 3), 38),            # growth: each link visibly busier
        (grow["fab"], (-3.5, 6, 6.5), (-9, .5, -3), 38),
        (grow["cloud"], (1.5, 6, 10), (-3, .5, 3), 38),
        (grow["lab"], (9.5, 6, 4), (3.5, 1.5, -2.5), 38),
        (l["c05_11"][0], (10, 30, 24), (0, 0, 0), 40),
        (w_fin, (.5, 40, 4.5), (.5, 0, 0), 38),
        (w_inv, (-3, 29, 7), (-3, 0, -1), 40),
        (w_dev, (1, 28, 8), (1, 0, 0), 40),
        (w_purch, (-4, 28, 8), (-5, 0, 0), 40),
        (l["c05_15"][1] - .2, (14, 32, 30), (0, 0, 0), 42),
    ]
    def push(pos, look, k):
        return [round(p + (q - p) * k, 3) for p, q in zip(pos, look)]
    keys = []
    for i, (t, pos, look, fov) in enumerate(beats):
        nxt = beats[i + 1][0] if i + 1 < len(beats) else e
        arrive = t + (.3 if i else 0)
        keys.append([round(arrive, 3), list(pos), list(look), fov])
        keys.append([round(max(arrive + .1, nxt - 1.1), 3), push(pos, look, .07), list(look), fov])
    rev = {"lab": loop[1], "cloud": loop[2], "fab": loop[3]}
    regions = [("diorama", [(s, e)], f"""AI3D.add('diorama',{{start:{s},end:{e},world:'diorama',dur:{e - s},keys:{json.dumps(keys)},
 platform:{s + .3},ghost:{w_imag},rise:{json.dumps(r)},flow:{json.dumps(flow)},pay:{json.dumps([flow[0] + .5, flow[1] + .4, w_pay])},grow:{json.dumps(grow)},boost:{json.dumps([grow['fab'], grow['cloud'], grow['lab']])},
 loop:{json.dumps(loop)},rev:{json.dumps(rev)},packetLabel:'mf-packet',
 labels:{{fab:'mf-fab',cloud:'mf-cloud',lab:'mf-lab',cust:'mf-cust'}}}});""")]
    lab = lambda i, t, sub: (f'<div class="lbl" id="{i}" style="left:0;top:0;text-align:center">{t}<small>{sub}</small></div>')
    html = (lab("mf-fab", "Chip maker", "designs &amp; sells chips") + lab("mf-cloud", "Cloud provider", "data centres")
            + lab("mf-lab", "AI developer", "trains models") + lab("mf-cust", "Customers", "businesses &amp; people")
            + "".join(f'<div class="lbl" id="mf-rev-{k}" style="left:0;top:0;font:800 40px Inter;color:#f2c66d">+ revenue</div>' for k in rev)
            + '<div class="lbl" id="mf-packet" style="left:0;top:0;font-size:46px;color:#f2c66d">$1 billion</div>'
            '<div class="tag m" id="mf-tag1">Simplified model</div><div class="tag l" id="mf-tag2">Hypothetical — not a specific company</div>'
            '<div id="mf-legend" style="position:absolute;right:56px;top:60px;font:700 28px Inter;color:#e8f3ff;opacity:0;text-align:right;line-height:1.6">'
            '<span style="color:#7fe9ff">■</span> chips &amp; services<br><span style="color:#f2c66d">●</span> payments</div>'
            '<div id="mf-exp" style="position:absolute;right:56px;top:200px;width:300px;opacity:0;font:700 28px Inter;color:#e8f3ff">Investor expectations'
            '<div style="margin-top:10px;height:22px;border-radius:11px;background:#16233a;overflow:hidden"><div id="mf-exp-bar" style="height:100%;width:20%;background:linear-gradient(90deg,#38d6ff,#f2c66d)"></div></div></div>')
    js = f"""
show('#mf-tag1',{w_simp}); hide('#mf-tag1',{l['c05_12'][0]});
show('#mf-fab',{r['fab'] + .3}); show('#mf-cloud',{r['cloud'] + .3}); show('#mf-lab',{r['lab'] + .3}); show('#mf-cust',{r['cust'] + .3});
hide(['#mf-fab','#mf-cloud','#mf-lab','#mf-cust'],{w_fin - .2}); show(['#mf-fab','#mf-cloud','#mf-lab','#mf-cust'],{w_fin + 1.2});
show('#mf-legend',{w_pay}); hide('#mf-legend',{l['c05_12'][0]});
show('#mf-exp',{W('investors', 'c05_11')}); tl.fromTo('#mf-exp-bar',{{width:'20%'}},{{width:'86%',duration:2.2,ease:'power2.out'}},{W('anticipate', 'c05_11')}); hide('#mf-exp',{l['c05_12'][0] + 1});
show('#mf-tag2',{W('Imagine', 'c05_13')}); hide('#mf-tag2',{e - .4});
"""
    import money_cutaways as mc
    w_prod, w_adv, w_chips = W("produces", "c05_02"), W("advanced", "c05_02"), W("chips", "c05_02")
    w_inst, w_dc = W("installs", "c05_03"), W("data", "c05_03")
    w_train, w_oper = W("train", "c05_04"), W("operate", "c05_04")
    w_indiv, w_use = W("individual", "c05_05"), W("use", "c05_05")
    parts = [mc.fab("mcf", w_prod - .3, l["c05_03"][0] - .45, dict(pattern=w_prod, cut=w_adv - .1, pack=W("computing", "c05_02"), ship=w_chips + .1)),
             mc.cloud("mcc", w_inst - .35, l["c05_04"][0] - .45, dict(install=w_inst + .15, ready=w_dc)),
             mc.lab("mcl", w_train - .55, l["c05_05"][0] - .45, dict(train=w_train, operate=w_oper)),
             mc.customers("mcu", w_indiv - .2, l["c05_06"][0] - .5, dict(pay=w_pay, use=w_use))]
    html += "".join(h for h, _ in parts)
    js += "\n".join(j for _, j in parts)
    return [Scene("mf", round(s, 3), round(e - s, 3), html, css=mc.CSS, js=js)], regions, ""
