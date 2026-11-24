"""Money-flow ecosystem 7:15–8:38 (storyboard s040–s042): a 3D isometric economy that builds with the narration."""
from kit.assemble import Scene
from timeline import L, W


def build():
    l = {k: L(k) for k in [f"c05_{i:02d}" for i in range(1, 17)]}
    s, e = l["c05_01"][0] - .4, l["c05_15"][1] + .6
    w_inv, w_dev = W("investing", "c05_13"), W("developer", "c05_14")
    w_purch = W("purchases", "c05_15")
    w_pay = W("pay", "c05_05")
    labels = {"fab": "mf-fab", "cloud": "mf-cloud", "lab": "mf-lab", "cust": "mf-cust"}
    regions = [("diorama", [(s, e)], f"""AI3D.add('diorama',{{start:{s},end:{e},world:'diorama',dur:{e - s},orbit:[.62,1.02],zoom:[.92,1.12],
 rise:{{fab:{l['c05_02'][0]},cloud:{l['c05_03'][0]},lab:{l['c05_04'][0]},cust:{l['c05_05'][0]}}},
 flow:[{l['c05_03'][0] + 1.5},{l['c05_04'][0] + 1.5},{l['c05_05'][0] + .6}],pay:{w_pay},
 grow:{{cust:{l['c05_07'][0] + 1},fab:{l['c05_08'][0]},cloud:{l['c05_09'][0]},lab:{l['c05_10'][0]}}},
 loop:[{w_inv},{w_dev + .2},{w_purch},{l['c05_15'][1] - .3}],packetLabel:'mf-packet',
 labels:{{fab:'mf-fab',cloud:'mf-cloud',lab:'mf-lab',cust:'mf-cust'}}}});""")]
    lab = lambda i, t, sub: (f'<div class="lbl" id="{i}" style="left:0;top:0;text-align:center">{t}<small>{sub}</small></div>')
    html = (lab("mf-fab", "Chip maker", "designs &amp; sells chips") + lab("mf-cloud", "Cloud provider", "data centres")
            + lab("mf-lab", "AI developer", "trains models") + lab("mf-cust", "Customers", "businesses &amp; people")
            + '<div class="lbl" id="mf-packet" style="left:0;top:0;font-size:46px;color:#f2c66d">$1 billion</div>'
            '<div class="tag m" id="mf-tag1">Simplified model</div><div class="tag l" id="mf-tag2">Hypothetical — not a specific company</div>'
            '<div id="mf-legend" style="position:absolute;right:56px;top:60px;font:700 28px Inter;color:#e8f3ff;opacity:0;text-align:right;line-height:1.6">'
            '<span style="color:#7fe9ff">●</span> products &amp; services<br><span style="color:#f2c66d">●</span> payments</div>'
            '<div id="mf-exp" style="position:absolute;right:56px;top:200px;width:300px;opacity:0;font:700 28px Inter;color:#e8f3ff">Investor expectations'
            '<div style="margin-top:10px;height:22px;border-radius:11px;background:#16233a;overflow:hidden"><div id="mf-exp-bar" style="height:100%;width:20%;background:linear-gradient(90deg,#38d6ff,#f2c66d)"></div></div></div>')
    js = f"""
show('#mf-tag1',{s + .6}); hide('#mf-tag1',{l['c05_12'][0]});
show('#mf-fab',{l['c05_02'][0] + .4}); show('#mf-cloud',{l['c05_03'][0] + .4}); show('#mf-lab',{l['c05_04'][0] + .4}); show('#mf-cust',{l['c05_05'][0] + .4});
show('#mf-legend',{w_pay + .4}); hide('#mf-legend',{l['c05_12'][0]});
show('#mf-exp',{l['c05_11'][0]}); tl.fromTo('#mf-exp-bar',{{width:'20%'}},{{width:'86%',duration:2.2,ease:'power2.out'}},{l['c05_11'][0] + .3}); hide('#mf-exp',{l['c05_12'][0] + 1});
show('#mf-tag2',{w_inv - .4}); hide('#mf-tag2',{e - .4});
"""
    return [Scene("mf", round(s, 3), round(e - s, 3), html, js=js)], regions, ""
