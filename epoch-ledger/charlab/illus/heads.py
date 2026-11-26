"""Artistic-direction gate: premium 2D illustrated characters (original designs, experimental).

Editorial-illustration style: designed shapes, painted two-tone light with soft gradients, tinted line work (no black
outlines), warm paper grain. Each character has a turnaround (front, three-quarter, profile) drawn as separate views,
as in professional 2D cut-out animation. Heads are drawn in a local frame: head centre (0, 0), crown y=-160, chin y=140.
"""
from __future__ import annotations

# ── palettes ─────────────────────────────────────────────────────────────────────────────────────────────────────────
NADIA = dict(skin="#c48a66", skin_sh="#9f6a4f", skin_lt="#dca582", blush="#c57a64", line="#6e4234", lip="#8e4f45",
             lip_lt="#a9665a", hair="#2b1d18", hair_sh="#1a1110", hair_lt="#4b342a", iris="#3a2418", brow="#2b1d18",
             top="#c58f2e", top_sh="#9c6f1f", top_lt="#dba948", blouse="#efe5d3", blouse_sh="#d6c8b0", ear="#e3b23c")
ELIAS = dict(skin="#e2b494", skin_sh="#bf8c70", skin_lt="#f1cbaf", blush="#d99a86", line="#7a4a3a", lip="#b06e5e",
             lip_lt="#c58372", hair="#8d8783", hair_sh="#625d5a", hair_lt="#b4aea9", iris="#4a5a66", brow="#6d6763",
             top="#27324a", top_sh="#1a2236", top_lt="#3b4866", blouse="#eef0f3", blouse_sh="#cfd4dc", tie="#8a2f36",
             tie_sh="#651f26", glasses="#3a2c26")

GRAIN = """<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/>
  <feColorMatrix type="matrix" values="0 0 0 0 .35  0 0 0 0 .25  0 0 0 0 .18  0 0 0 .07 0"/>
  <feComposite in2="SourceGraphic" operator="in"/>
</filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="soft2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2"/></filter>"""


def P(d, fill, line=None, w=2.4, extra=""):
    s = f'<path d="{d}" fill="{fill}"'
    if line:
        s += f' stroke="{line}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'
    return s + f' {extra}/>'


def shaded(clip_id, d, base, sh, lt, line, sh_d, lt_d, w=2.4):
    """a shape filled with base colour, a painted shadow shape and a soft light shape clipped to it, then its line"""
    return (f'<clipPath id="{clip_id}"><path d="{d}"/></clipPath>' + P(d, base)
            + f'<g clip-path="url(#{clip_id})">' + P(sh_d, sh, extra='filter="url(#soft2)"') + P(lt_d, lt, extra='filter="url(#soft)" opacity=".75"') + '</g>'
            + P(d, "none", line, w))


# ── female head: front ──────────────────────────────────────────────────────────────────────────────────────────────
EXPR = {  # brow lift, inner-brow tilt (+ raises inner ends), lid squeeze, mouth: corner lift, open
    "neutral": dict(by=0, tilt=0, lid=0, lower=0, corner=0, open=0),
    "smile": dict(by=-2, tilt=0, lid=3, lower=5, corner=-7, open=7),
    "worried": dict(by=-4, tilt=10, lid=-1, lower=1, corner=6, open=0),
    "speaking_ah": dict(by=-2, tilt=2, lid=0, lower=0, corner=0, open=16),
}


def nadia_front(c=NADIA, expr="neutral"):
    E = EXPR[expr]
    face = "M0,-158 C64,-158 106,-114 107,-50 C108,0 102,44 86,76 C66,114 34,138 0,140 C-34,138 -66,114 -86,76 C-102,44 -108,0 -107,-50 C-106,-114 -64,-158 0,-158 Z"
    # light from the upper left: the shadow side follows the right contour, under the brow ridge and the jaw
    face_sh = "M58,-150 C100,-120 116,-60 110,0 C104,60 80,110 30,140 C70,130 96,96 104,40 C96,70 76,100 60,108 C82,60 88,0 80,-60 C74,-100 62,-130 40,-152 Z"
    face_lt = "M-78,-118 C-50,-142 -12,-136 -20,-100 C-28,-60 -60,-20 -84,-30 C-98,-52 -96,-96 -78,-118 Z"
    # neck: wide, short, flowing into the trapezius; jaw shadow cast on it
    neck = "M-52,86 C-50,124 -54,150 -66,172 L-74,200 L74,200 L66,172 C54,150 50,124 52,86 Z"
    neck_sh = "M-70,80 C-30,134 30,138 70,84 L70,128 C36,150 -30,150 -70,120 Z M40,120 C50,150 64,172 100,182 L60,190 C50,170 44,150 40,120 Z"
    s = []
    # hair back mass + low bun (behind the head, peeking out at the nape)
    s.append(P("M-124,-44 C-132,-124 -88,-184 0,-186 C88,-184 132,-124 124,-44 C122,6 114,52 100,80 C70,64 -70,64 -100,80 C-114,52 -122,6 -124,-44 Z", c["hair_sh"]))
    # neck and shoulders
    s.append(shaded("nf_neck", neck, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], neck_sh, "M-46,120 C-40,110 -24,140 -34,168 Z"))
    # blouse with a soft round collar, cardigan with ribbed edge and folds
    s.append(P("M-70,176 C-120,186 -190,204 -214,236 L-228,340 L228,340 L214,236 C190,204 120,186 70,176 C52,206 -52,206 -70,176 Z", c["blouse"], c["blouse_sh"], 2))
    s.append(P("M-70,176 C-52,206 52,206 70,176 C76,186 74,194 66,200 C44,226 -44,226 -66,200 C-74,194 -76,186 -70,176 Z", c["blouse"], c["blouse_sh"], 1.8))
    s.append(P("M-40,214 C-14,224 14,224 40,214", "none", c["blouse_sh"], 2, 'opacity=".8"'))
    s.append(P("M-228,340 L-214,236 C-196,208 -140,192 -90,186 C-80,230 -64,290 -46,340 Z", c["top"], c["top_sh"], 2.2))
    s.append(P("M228,340 L214,236 C196,208 140,192 90,186 C80,230 64,290 46,340 Z", c["top"], c["top_sh"], 2.2))
    s.append(P("M228,340 L214,236 C196,208 150,196 120,190 C130,240 150,300 160,340 Z", c["top_sh"], extra='opacity=".7"'))
    s.append(P("M-90,186 C-80,230 -64,290 -46,340 M90,186 C80,230 64,290 46,340", "none", c["top_sh"], 9, 'opacity=".45"'))   # ribbed placket
    s.append(P("M-200,250 C-170,226 -130,212 -100,206", "none", c["top_lt"], 10, 'opacity=".45" filter="url(#soft2)"'))
    s.append(P("M-176,300 C-160,280 -140,268 -120,262 M-150,330 C-140,316 -126,306 -110,300", "none", c["top_sh"], 2, 'opacity=".55"'))
    # ears + earrings
    for sx in (-1, 1):
        s.append(P(f"M{sx*103},-14 C{sx*122},-24 {sx*127},4 {sx*121},24 C{sx*117},40 {sx*108},44 {sx*101},36 Z", c["skin_sh"] if sx > 0 else c["skin"], c["line"], 2))
        s.append(P(f"M{sx*108},-6 C{sx*116},0 {sx*116},14 {sx*110},24", "none", c["skin_sh"], 1.6))
        s.append(f'<circle cx="{sx*111}" cy="50" r="5.5" fill="{c["ear"]}" stroke="#8c6a1c" stroke-width="1.2"/><circle cx="{sx*109.5}" cy="48.5" r="1.6" fill="#fff4c8"/>')
    # face
    s.append(shaded("nf_face", face, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], face_sh, face_lt).replace('url(#soft2)', 'url(#soft)', 1))
    s.append(P("M-70,-36 C-50,-46 -30,-44 -16,-38 M70,-36 C50,-46 30,-44 16,-38", "none", c["skin_sh"], 6, 'opacity=".22" filter="url(#soft2)"'))  # brow ridge
    s.append(P("M-86,60 C-70,90 -40,110 -10,112", "none", c["skin_sh"], 8, 'opacity=".12" filter="url(#soft2)"'))
    s.append(f'<ellipse cx="-58" cy="44" rx="27" ry="15" fill="{c["blush"]}" opacity="{.32 + .1*(expr=="smile")}" filter="url(#soft)"/>')
    s.append(f'<ellipse cx="58" cy="44" rx="25" ry="14" fill="{c["blush"]}" opacity="{.28 + .1*(expr=="smile")}" filter="url(#soft)"/>')
    # eyes (upper lid follows lid squeeze, lower lid pushes up in a smile)
    lid, low = E["lid"], E["lower"]
    for sx in (-1, 1):
        x = sx * 44
        eye = f"M{x-24},0 C{x-14},{-15+lid} {x+12},{-17+lid} {x+25},-2 C{x+14},{9-low} {x-10},{10-low} {x-24},0 Z"
        s.append(P(eye, "#f2ebe2"))
        s.append(f'<clipPath id="eye{sx}{expr}"><path d="{eye}"/></clipPath>')
        s.append(f'<g clip-path="url(#eye{sx}{expr})"><circle cx="{x+1}" cy="-3" r="11.5" fill="{c["iris"]}"/><circle cx="{x+1}" cy="-2" r="11.5" fill="none" stroke="#1d110b" stroke-width="2"/>'
                 f'<circle cx="{x+1}" cy="-3" r="5.2" fill="#120a07"/><circle cx="{x-3}" cy="-7" r="2.8" fill="#fff" opacity=".9"/>'
                 f'<path d="M{x-26},-20 L{x+26},-20 L{x+26},-6 C{x+10},-12 {x-10},-12 {x-26},-6 Z" fill="{c["skin_sh"]}" opacity=".5"/></g>')
        s.append(P(f"M{x-25},1 C{x-14},{-16+lid} {x+12},{-18+lid} {x+26},-3", "none", c["hair_sh"], 3.4))
        s.append(P(f"M{x+20},{-7+lid/2} L{x+29},{-12+lid/2}", "none", c["hair_sh"], 2.2))
        s.append(P(f"M{x-16},{11-low} C{x-4},{14-low} {x+10},{13-low} {x+20},{7-low}", "none", c["line"], 1.1, 'opacity=".3"'))
        s.append(P(f"M{x-21},{-27+lid} C{x-8},{-35+lid} {x+12},{-35+lid} {x+24},{-25+lid}", "none", c["skin_sh"], 1.4, 'opacity=".5"'))
        if low: s.append(P(f"M{x-14},{18-low} C{x-4},{22-low} {x+8},{21-low} {x+16},{16-low}", "none", c["skin_sh"], 1.2, 'opacity=".3"'))
    # brows: tapered, inner ends lift when worried
    by, tilt = E["by"], E["tilt"]
    for sx in (-1, 1):
        s.append(P(f"M{sx*16},{-36+by-tilt} C{sx*30},{-48+by-tilt*.6} {sx*58},{-54+by} {sx*82},{-42+by} "
                   f"C{sx*62},{-47+by} {sx*36},{-42+by-tilt*.5} {sx*16},{-30+by-tilt} Z", c["brow"]))
        if tilt: s.append(P(f"M{sx*10},{-44+by} C{sx*14},{-54+by} {sx*20},{-58+by} {sx*24},{-56+by}", "none", c["skin_sh"], 1.4, 'opacity=".55"'))
    # nose: bridge shadow on the right, rounded tip, small wings, cast shadow below
    s.append(P("M8,-24 C12,0 18,24 22,40", "none", c["skin_sh"], 3, 'opacity=".55" filter="url(#soft2)"'))
    s.append(P("M-14,50 C-20,46 -24,52 -20,58 C-14,64 -6,62 0,64 C6,62 14,64 20,58 C24,52 20,46 14,50", "none", c["line"], 1.8))
    s.append(P("M-9,58 C-6,60 -3,60 -2,59 M9,58 C6,60 3,60 2,59", "none", "#4a2a22", 2.2))
    s.append(f'<ellipse cx="-2" cy="46" rx="8" ry="6" fill="{c["skin_lt"]}" opacity=".6" filter="url(#soft2)"/>')
    s.append(P("M-16,68 C-6,74 8,74 18,68 C8,72 -6,72 -16,68 Z", c["skin_sh"], extra='opacity=".6"'))
    # mouth
    k, o = E["corner"], E["open"]
    if o:
        s.append(P(f"M-29,{86+k} C-14,{80} 14,{80} 29,{86+k} C18,{96+o} -18,{96+o} -29,{86+k} Z", "#5a2a27", c["line"], 1.6))
        s.append(P(f"M-21,{86} C-8,{83} 8,{83} 21,{86} L19,{90} C8,{88} -8,{88} -19,{90} Z", "#f2ece4"))
        if o > 10: s.append(f'<ellipse cx="2" cy="{92+o*.6}" rx="12" ry="{o*.28}" fill="#a2524c"/>')
        s.append(P(f"M-29,{86+k} C-20,82 -8,79 0,81 C8,79 20,82 29,{86+k}", "none", c["lip"], 3.4))
        s.append(P(f"M-18,{94+o} C-8,{99+o} 8,{99+o} 18,{94+o}", "none", c["lip"], 3))
    else:
        s.append(P(f"M-28,{88+k} C-16,80 -6,80 0,83 C6,80 16,80 28,{88+k} C14,90 -14,90 -28,{88+k} Z", c["lip"]))
        s.append(P(f"M-26,{89+k} C-12,104 12,104 26,{89+k} C12,92 -12,92 -26,{89+k} Z", c["lip_lt"]))
        s.append(P(f"M-28,{88+k} C-14,92 14,92 28,{88+k}", "none", "#5e2f2a", 2.2))
        s.append(f'<ellipse cx="-6" cy="96" rx="9" ry="3" fill="#d79a8a" opacity=".55" filter="url(#soft2)"/>')
    if k < 0:   # smile: cheek push and naso-labial curve
        s.append(P("M-36,64 C-42,76 -40,86 -34,92 M36,64 C42,76 40,86 34,92", "none", c["skin_sh"], 1.8, 'opacity=".35"'))
    s.append(P("M-10,121 C-4,124 4,124 10,121", "none", c["skin_sh"], 1.4, 'opacity=".3"'))
    # hair front: centre part, volume swept back over the ears, strand groups and flyaways
    s.append(P("M2,-178 C-76,-178 -128,-128 -127,-56 C-126,-24 -120,10 -112,32 C-104,-6 -98,-50 -84,-86 C-64,-128 -28,-144 -2,-150 Z", c["hair"], c["hair_sh"], 2))
    s.append(P("M2,-178 C76,-178 128,-128 127,-56 C126,-24 120,10 112,32 C104,-6 98,-50 84,-86 C64,-128 28,-144 2,-150 Z", c["hair"], c["hair_sh"], 2))
    s.append(P("M2,-178 C60,-176 110,-140 124,-80 C112,-120 80,-150 40,-160 Z", c["hair_sh"], extra='opacity=".75"'))
    for d, wdt, op in (("M-20,-168 C-64,-160 -100,-128 -112,-78", 5, .55), ("M-6,-160 C-44,-150 -74,-126 -88,-96", 3, .5),
                       ("M-40,-166 C-82,-150 -110,-110 -118,-60", 2.4, .45), ("M28,-164 C70,-150 100,-118 110,-80", 2.2, .35),
                       ("M-110,-20 C-114,0 -112,20 -106,34", 2, .5)):
        s.append(P(d, "none", c["hair_lt"], wdt, f'opacity="{op}"'))
    s.append(P("M-4,-150 C-2,-158 0,-166 2,-178", "none", c["hair_sh"], 1.6))   # parting
    s.append(P("M-100,-60 C-116,-40 -122,-10 -116,20 M104,-70 C116,-40 120,-8 114,22", "none", c["hair"], 2.4))   # loose strands
    s.append(P("M-58,-150 C-80,-170 -96,-168 -104,-158", "none", c["hair"], 1.6, 'opacity=".8"'))   # flyaway
    return "\n".join(x for x in s if x)


def _eye(x, y, w, c, key, lid=0, low=0, look=0, far=False):
    """almond eye of width w (foreshortened when far); look shifts the iris horizontally"""
    h = w * .52
    d = f"M{x-w/2},{y} C{x-w*.3},{y-h*.62+lid} {x+w*.25},{y-h*.7+lid} {x+w/2},{y-h*.08} C{x+w*.3},{y+h*.36-low} {x-w*.22},{y+h*.4-low} {x-w/2},{y} Z"
    r = 11.5 * (w / 48) ** .5
    o = [P(d, "#f2ebe2"), f'<clipPath id="e{key}"><path d="{d}"/></clipPath>',
         f'<g clip-path="url(#e{key})"><circle cx="{x+look}" cy="{y-3}" r="{r}" fill="{c["iris"]}"/><circle cx="{x+look}" cy="{y-3}" r="{r*.46}" fill="#120a07"/>'
         f'<circle cx="{x+look-r*.35}" cy="{y-3-r*.35}" r="{r*.24}" fill="#fff" opacity=".9"/><path d="M{x-w},{y-22} L{x+w},{y-22} L{x+w},{y-6} C{x},{y-12} {x},{y-12} {x-w},{y-6} Z" fill="{c["skin_sh"]}" opacity=".5"/></g>',
         P(f"M{x-w/2-1},{y+1} C{x-w*.3},{y-h*.66+lid} {x+w*.25},{y-h*.74+lid} {x+w/2+1},{y-h*.12}", "none", c["hair_sh"], 3.2),
         P(f"M{x-w*.43},{y-h*.95+lid} C{x-w*.15},{y-h*1.3+lid} {x+w*.25},{y-h*1.3+lid} {x+w*.48},{y-h*.9+lid}", "none", c["skin_sh"], 1.3, 'opacity=".5"')]
    if far: o.append(P(f"M{x-w/2-1},{y+1} L{x-w/2-8},{y-4}", "none", c["hair_sh"], 2))
    else: o.append(P(f"M{x+w/2-2},{y-h*.1} L{x+w/2+8},{y-h*.35}", "none", c["hair_sh"], 2))
    return "".join(o)


def nadia_34(c=NADIA, expr="neutral"):
    """three-quarter view, turned toward screen-left"""
    E = EXPR[expr]
    face = "M14,-158 C-48,-158 -84,-120 -91,-64 C-95,-40 -97,-26 -93,-16 C-89,4 -93,24 -87,50 C-79,90 -59,122 -24,138 C10,141 48,126 78,96 C99,72 111,30 111,-30 C111,-110 72,-158 14,-158 Z"
    sh = "M60,-150 C100,-110 116,-40 110,20 C104,70 80,110 40,132 C70,120 96,80 100,40 C92,70 70,98 50,106 C76,60 84,0 76,-60 C70,-100 56,-130 36,-152 Z"
    lt = "M-70,-118 C-44,-140 -10,-132 -18,-96 C-26,-56 -56,-20 -80,-32 C-92,-56 -88,-98 -70,-118 Z"
    neck = "M-40,108 C-40,136 -44,160 -56,178 L-62,204 L96,204 C86,174 82,140 84,72 Z"
    s = []
    s.append(P("M10,-184 C-70,-182 -118,-128 -112,-50 C-108,-10 -100,20 -92,40 L118,70 C132,20 136,-40 128,-90 C116,-150 70,-186 10,-184 Z", c["hair_sh"]))
    s.append(P("M104,54 C140,46 166,70 160,104 C154,132 120,138 102,122 C88,108 88,68 104,54 Z", c["hair"], c["hair_sh"], 2))      # bun
    s.append(P("M112,70 C132,66 150,80 150,100", "none", c["hair_lt"], 2.4, 'opacity=".5"'))
    s.append(shaded("n34_neck", neck, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], "M-50,96 C-10,140 50,140 90,70 L96,204 L40,204 C40,170 30,150 -50,120 Z", "M-36,140 C-30,130 -20,160 -30,190 Z"))
    s.append(P("M70,84 C50,120 20,160 -6,196", "none", c["skin_sh"], 3, 'opacity=".45" filter="url(#soft2)"'))   # sternocleidomastoid
    s.append(P("M-62,184 C-120,192 -186,210 -206,240 L-216,340 L232,340 L224,238 C204,206 150,190 96,184 C70,214 -40,216 -62,184 Z", c["blouse"], c["blouse_sh"], 2))
    s.append(P("M-62,184 C-40,214 70,214 96,184 C102,196 98,204 88,208 C60,232 -38,232 -58,206 C-66,198 -68,190 -62,184 Z", c["blouse"], c["blouse_sh"], 1.8))
    s.append(P("M-216,340 L-206,240 C-190,212 -130,196 -82,190 C-74,234 -62,290 -48,340 Z", c["top"], c["top_sh"], 2.2))
    s.append(P("M232,340 L224,238 C206,208 160,194 112,188 C104,232 98,290 92,340 Z", c["top_sh"], c["top_sh"], 2.2))
    s.append(P("M-190,252 C-160,230 -120,216 -92,210", "none", c["top_lt"], 10, 'opacity=".45" filter="url(#soft2)"'))
    s.append(P("M-82,190 C-74,234 -62,290 -48,340 M112,188 C104,232 98,290 92,340", "none", c["top_sh"], 9, 'opacity=".45"'))
    # near ear + earring
    s.append(P("M78,-12 C98,-24 106,4 100,26 C96,40 86,44 78,36 Z", c["skin_sh"], c["line"], 2))
    s.append(P("M86,-4 C94,2 94,16 88,26", "none", c["line"], 1.4, 'opacity=".6"'))
    s.append(f'<circle cx="88" cy="50" r="5.5" fill="{c["ear"]}" stroke="#8c6a1c" stroke-width="1.2"/>')
    s.append(shaded("n34_face", face, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], sh, lt).replace('url(#soft2)', 'url(#soft)', 1))
    s.append(f'<ellipse cx="-62" cy="40" rx="16" ry="14" fill="{c["blush"]}" opacity=".3" filter="url(#soft)"/><ellipse cx="22" cy="44" rx="28" ry="16" fill="{c["blush"]}" opacity=".3" filter="url(#soft)"/>')
    lid, low = E["lid"], E["lower"]
    s.append(_eye(-60, -2, 30, c, "34f" + expr, lid, low, look=-4, far=True))
    s.append(_eye(14, -2, 46, c, "34n" + expr, lid, low, look=-6))
    by, tilt = E["by"], E["tilt"]
    s.append(P(f"M-42,{-34+by-tilt} C-54,{-44+by-tilt*.6} -70,{-48+by} -84,{-38+by} C-70,{-42+by} -56,{-38+by-tilt*.5} -42,{-28+by-tilt} Z", c["brow"]))
    s.append(P(f"M-14,{-34+by-tilt} C6,{-48+by-tilt*.6} 30,{-54+by} 52,{-42+by} C32,{-47+by} 10,{-42+by-tilt*.5} -14,{-28+by-tilt} Z", c["brow"]))
    # nose in silhouette over the far cheek
    s.append(P("M-40,-20 C-46,4 -58,26 -66,40 C-70,48 -64,56 -54,56 C-50,60 -42,62 -36,58 C-30,62 -22,58 -20,52", c["skin"], c["line"], 1.8))
    s.append(P("M-42,-12 C-40,10 -34,30 -28,42", "none", c["skin_sh"], 3, 'opacity=".4" filter="url(#soft2)"'))
    s.append(P("M-44,54 C-42,56 -39,57 -37,56", "none", "#4a2a22", 2.2))
    s.append(f'<ellipse cx="-58" cy="40" rx="7" ry="5" fill="{c["skin_lt"]}" opacity=".6" filter="url(#soft2)"/>')
    k, o = E["corner"], E["open"]
    if o:
        s.append(P(f"M-62,{88+k*.6} C-50,80 -20,80 -4,{86+k} C-14,{96+o} -50,{96+o} -62,{88+k*.6} Z", "#5a2a27", c["line"], 1.6))
        s.append(P("M-54,86 C-44,83 -22,83 -10,86 L-12,90 C-24,88 -44,88 -52,90 Z", "#f2ece4"))
        s.append(P(f"M-62,{88+k*.6} C-52,82 -36,79 -28,81 C-20,79 -10,82 -4,{86+k}", "none", c["lip"], 3.2))
    else:
        s.append(P(f"M-60,{88+k*.6} C-50,81 -38,80 -30,83 C-22,80 -12,82 -4,{88+k} C-20,91 -44,91 -60,{88+k*.6} Z", c["lip"]))
        s.append(P(f"M-58,{89+k*.6} C-46,103 -18,103 -6,{89+k} C-20,92 -44,92 -58,{89+k*.6} Z", c["lip_lt"]))
        s.append(P(f"M-60,{88+k*.6} C-44,92 -20,92 -4,{88+k}", "none", "#5e2f2a", 2.1))
    s.append(P("M-50,118 C-40,124 -30,124 -22,120", "none", c["skin_sh"], 1.4, 'opacity=".3"'))
    # hair front: part shifted to the far side, volume over the near temple, swept back to the bun
    s.append(P("M-30,-176 C-88,-168 -116,-120 -112,-60 C-110,-30 -104,0 -98,18 C-94,-20 -90,-56 -78,-90 C-62,-126 -44,-142 -28,-150 Z", c["hair"], c["hair_sh"], 2))
    s.append(P("M-30,-176 C40,-188 110,-160 128,-90 C134,-50 128,-10 120,30 C112,0 104,-30 94,-56 C80,-100 40,-138 -24,-150 Z", c["hair"], c["hair_sh"], 2))
    s.append(P("M-24,-150 C40,-140 84,-100 98,-54 C106,-30 112,0 116,20", "none", c["hair_sh"], 2, 'opacity=".7"'))
    for d, wdt, op in (("M-10,-168 C40,-170 90,-140 112,-90", 5, .5), ("M0,-158 C40,-152 76,-128 94,-96", 3, .45),
                       ("M-40,-168 C-80,-154 -100,-120 -104,-80", 3, .5), ("M60,-150 C90,-120 108,-60 110,-10", 2.2, .35)):
        s.append(P(d, "none", c["hair_lt"], wdt, f'opacity="{op}"'))
    s.append(P("M-98,-40 C-104,-10 -102,14 -96,30", "none", c["hair"], 2.2))
    return "\n".join(s)


def nadia_profile(c=NADIA, expr="neutral"):
    """profile, facing screen-left"""
    E = EXPR[expr]
    head = ("M30,-160 C-36,-160 -82,-124 -93,-72 C-97,-50 -99,-38 -101,-30 C-100,-20 -96,-14 -98,-8 C-104,10 -116,32 -122,44 "
            "C-122,52 -114,56 -104,56 C-100,62 -100,68 -104,74 C-108,80 -104,86 -98,88 C-104,92 -104,100 -98,106 "
            "C-92,110 -92,116 -96,124 C-98,138 -84,148 -60,148 C-30,148 0,138 18,120 C40,102 58,84 68,64 "
            "C98,34 118,-14 116,-68 C112,-128 82,-160 30,-160 Z")
    sh = "M40,-150 C100,-120 124,-50 112,10 C100,60 76,90 40,118 L150,150 L150,-170 Z"
    lt = "M-80,-110 C-60,-136 -20,-138 -30,-100 C-40,-60 -70,-40 -88,-50 C-98,-70 -92,-96 -80,-110 Z"
    neck = "M-58,140 C-56,164 -60,184 -66,204 L94,204 C80,170 70,120 66,62 C40,100 0,130 -58,140 Z"
    s = []
    s.append(P("M-4,-182 C-70,-178 -102,-130 -98,-78 L-80,-60 C40,-60 120,-10 112,60 C140,30 150,-40 140,-90 C126,-150 70,-186 -4,-182 Z", c["hair_sh"]))
    s.append(P("M96,46 C130,30 166,50 168,86 C170,120 136,134 108,122 C88,112 80,64 96,46 Z", c["hair"], c["hair_sh"], 2))
    s.append(P("M106,56 C130,48 156,62 158,88", "none", c["hair_lt"], 2.4, 'opacity=".5"'))
    s.append(shaded("np_neck", neck, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], "M-60,130 C0,140 50,110 70,60 L100,204 L50,204 C50,170 30,150 -60,150 Z", "M-50,160 C-40,150 -30,180 -40,200 Z"))
    s.append(P("M50,90 C30,130 0,170 -30,200", "none", c["skin_sh"], 3, 'opacity=".4" filter="url(#soft2)"'))
    s.append(P("M-70,190 C-110,200 -150,214 -170,240 L-180,340 L200,340 L190,236 C170,206 130,192 96,190 C60,214 -30,214 -70,190 Z", c["blouse"], c["blouse_sh"], 2))
    s.append(P("M-180,340 L-170,240 C-150,214 -110,200 -76,194 C-60,240 -40,300 -30,340 Z", c["top"], c["top_sh"], 2.2))
    s.append(P("M200,340 L190,236 C170,206 120,194 40,200 C20,250 10,300 0,340 Z", c["top"], c["top_sh"], 2.2))
    s.append(P("M180,250 C150,226 100,214 60,212", "none", c["top_lt"], 10, 'opacity=".4" filter="url(#soft2)"'))
    s.append(P("M40,200 C20,250 10,300 0,340", "none", c["top_sh"], 9, 'opacity=".45"'))
    s.append(shaded("np_head", head, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], sh, lt).replace('url(#soft2)', 'url(#soft)', 1))
    s.append(f'<ellipse cx="-56" cy="40" rx="26" ry="16" fill="{c["blush"]}" opacity=".3" filter="url(#soft)"/>')
    # ear
    s.append(P("M22,-14 C44,-26 58,0 52,24 C48,40 34,46 24,38 C20,20 20,4 22,-14 Z", c["skin"], c["line"], 2))
    s.append(P("M30,-4 C42,0 44,16 36,28", "none", c["line"], 1.4, 'opacity=".6"'))
    s.append(f'<circle cx="32" cy="50" r="5.5" fill="{c["ear"]}" stroke="#8c6a1c" stroke-width="1.2"/>')
    # eye (profile wedge), brow, nostril, mouth line
    lid, low = E["lid"], E["lower"]
    eye = f"M-92,-4 C-86,{-12+lid} -74,{-14+lid} -66,-8 C-72,{0-low} -84,{2-low} -92,-4 Z"
    s.append(P(eye, "#f2ebe2"))
    s.append(f'<clipPath id="epf{expr}"><path d="{eye}"/></clipPath><g clip-path="url(#epf{expr})"><ellipse cx="-86" cy="-5" rx="6" ry="9" fill="{c["iris"]}"/><circle cx="-88" cy="-7" r="1.8" fill="#fff"/></g>')
    s.append(P(f"M-93,-3 C-86,{-14+lid} -74,{-16+lid} -64,-9 L-58,-14", "none", c["hair_sh"], 3))
    s.append(P(f"M-90,{-22+lid} C-82,{-28+lid} -72,{-26+lid} -66,{-20+lid}", "none", c["skin_sh"], 1.3, 'opacity=".5"'))
    by, tilt = E["by"], E["tilt"]
    s.append(P(f"M-98,{-34+by-tilt} C-86,{-44+by-tilt*.5} -66,{-46+by} -50,{-36+by} C-66,{-40+by} -84,{-36+by-tilt*.5} -98,{-28+by-tilt} Z", c["brow"]))
    s.append(P("M-108,50 C-104,52 -100,52 -98,50", "none", "#4a2a22", 2.2))
    s.append(P("M-98,-6 C-90,12 -88,30 -94,46", "none", c["skin_sh"], 3, 'opacity=".35" filter="url(#soft2)"'))
    k, o = E["corner"], E["open"]
    s.append(P(f"M-104,74 C-96,74 -88,{80+k*.5} -84,{86+k}", "none", c["lip"], 3))
    s.append(P(f"M-98,88 L-84,{88+k}", "none", "#5e2f2a", 2.2))
    s.append(P(f"M-98,106 C-94,100 -88,{94+k*.5} -84,{90+k}", "none", c["lip_lt"], 3))
    # hair: hairline at the temple, swept back over the ear to the bun
    s.append(P("M-90,-110 C-60,-150 0,-170 40,-168 C96,-160 130,-110 130,-50 C130,0 120,40 104,60 C90,30 70,10 50,-10 C30,-30 10,-40 -10,-60 C-40,-80 -70,-90 -90,-110 Z", c["hair"], c["hair_sh"], 2))
    s.append(P("M-86,-104 C-70,-126 -40,-140 -10,-142", "none", c["hair"], 6))
    for d, wdt, op in (("M-70,-128 C-20,-160 60,-160 110,-110", 5, .5), ("M-60,-100 C-10,-120 50,-110 100,-60", 3, .45),
                       ("M-20,-70 C20,-60 60,-30 96,30", 2.4, .4), ("M20,-150 C80,-140 120,-90 124,-30", 2.2, .35)):
        s.append(P(d, "none", c["hair_lt"], wdt, f'opacity="{op}"'))
    return "\n".join(s)


def _suit(c, yaw):
    """shirt collar, tie and suit shoulders; yaw: 0 front, 1 three-quarter (to screen-left), 2 profile"""
    dx = (0, -22, -60)[yaw]
    o = [P(f"M{-84+dx},190 C{-140+dx},196 -200,214 -224,246 L-236,340 L236,340 L224,246 C200,214 {140+dx},196 {84+dx},190 Z", c["top"], c["top_sh"], 2.2),
         P(f"M236,340 L224,246 C200,214 {150+dx},198 {110+dx},194 C{120+dx},240 {140+dx},300 {150+dx},340 Z", c["top_sh"], extra='opacity=".8"'),
         P("M-210,262 C-180,236 -140,222 -110,216", "none", c["top_lt"], 10, 'opacity=".45" filter="url(#soft2)"')]
    if yaw < 2:
        o += [P(f"M{-60+dx},180 L{-90+dx},200 L{-38+dx},340 L{dx+4},236 Z", c["blouse"], c["blouse_sh"], 1.8),         # shirt + collar points
              P(f"M{60+dx},180 L{90+dx},200 L{46+dx},340 L{dx+4},236 Z", c["blouse_sh"], c["blouse_sh"], 1.8),
              P(f"M{-12+dx},222 L{16+dx},222 L{22+dx},240 L{10+dx},252 L{-6+dx},252 L{-18+dx},240 Z", c["tie"], c["tie_sh"], 1.6),
              P(f"M{-6+dx},252 L{10+dx},252 L{26+dx},340 L{-22+dx},340 Z", c["tie"], c["tie_sh"], 1.6),
              P(f"M{6+dx},256 L{20+dx},340", "none", c["tie_sh"], 6, 'opacity=".5"'),
              P(f"M{-60+dx},180 L{-36+dx},222 L{-10+dx},226 M{60+dx},180 L{36+dx},222 L{14+dx},226", "none", c["blouse_sh"], 2),
              P(f"M{-90+dx},200 L{-60+dx},270 L{-40+dx},340 L{-110+dx},340 L{-130+dx},250 Z", c["top"], c["top_sh"], 2),        # lapels
              P(f"M{90+dx},200 L{64+dx},270 L{48+dx},340 L{120+dx},340 L{136+dx},250 Z", c["top_sh"], c["top_sh"], 2)]
    else:
        o += [P("M-60,190 L-90,206 L-70,240 L-40,214 Z", c["blouse"], c["blouse_sh"], 1.8),
              P("M-90,206 L-70,270 L-50,340 L-120,340 L-136,260 Z", c["top"], c["top_sh"], 2)]
    return '<g transform="translate(0,-18)">' + "".join(o) + '</g>'


def elias(view="front", c=ELIAS, expr="neutral"):
    """male, fifties: broader jaw, receding grey hair with a side part, glasses, suit"""
    E = EXPR[expr]; s = []
    lid, low, by, tilt, k, o = E["lid"], E["lower"], E["by"], E["tilt"], E["corner"], E["open"]
    if view == "front":
        face = "M0,-156 C70,-156 112,-112 112,-46 C112,8 112,50 98,82 C80,120 40,142 0,144 C-40,142 -80,120 -98,82 C-112,50 -112,8 -112,-46 C-112,-112 -70,-156 0,-156 Z"
        sh = "M60,-150 C104,-110 120,-40 114,30 C108,90 76,130 30,146 C80,140 110,90 116,30 L130,170 L130,-160 Z"
        lt = "M-74,-118 C-44,-142 -8,-134 -18,-96 C-28,-56 -62,-18 -88,-32 C-100,-58 -96,-100 -74,-118 Z"
        neck = "M-62,90 C-62,126 -66,152 -76,176 L-86,206 L86,206 L76,176 C66,152 62,126 62,90 Z"
        s.append(shaded("ef_neck", neck, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], "M-80,80 C-30,140 30,144 80,86 L80,140 C40,160 -30,160 -80,130 Z", "M-50,130 C-40,120 -30,150 -40,180 Z"))
        s.append(_suit(c, 0))
        for sx in (-1, 1):
            s.append(P(f"M{sx*108},-14 C{sx*128},-26 {sx*134},6 {sx*126},30 C{sx*122},46 {sx*110},50 {sx*104},40 Z", c["skin_sh"] if sx > 0 else c["skin"], c["line"], 2))
            s.append(P(f"M{sx*114},-4 C{sx*122},4 {sx*122},18 {sx*116},28", "none", c["skin_sh"], 1.6))
        s.append(shaded("ef_face", face, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], sh, lt).replace('url(#soft2)', 'url(#soft)', 1))
        s.append(P("M-98,70 C-80,110 -40,134 0,136 C40,134 80,110 98,70", "none", c["skin_sh"], 10, 'opacity=".16" filter="url(#soft2)"'))   # jaw plane
        s.append(P("M-30,-118 C-10,-122 10,-122 30,-118 M-26,-104 C-8,-107 8,-107 26,-104", "none", c["skin_sh"], 1.4, 'opacity=".35"'))      # forehead lines
        for sx in (-1, 1):
            s.append(_eye(sx * 46, 0, 42, c, f"ef{sx}{expr}", lid, low, look=0))
            s.append(P(f"M{sx*30},{14-low} C{sx*44},{20-low} {sx*58},{18-low} {sx*66},{10-low}", "none", c["skin_sh"], 1.6, 'opacity=".45"'))   # under-eye
            s.append(P(f"M{sx*20},{-34+by-tilt} C{sx*38},{-46+by-tilt*.6} {sx*62},{-48+by} {sx*84},{-36+by} C{sx*64},{-40+by} {sx*40},{-36+by-tilt*.5} {sx*20},{-26+by-tilt} Z", c["brow"], c["hair_sh"], 1))
            s.append(f'<rect x="{sx*46-30}" y="-22" width="60" height="42" rx="12" fill="none" stroke="{c["glasses"]}" stroke-width="3.4"/>')
        s.append(P("M-16,-6 C-8,-12 8,-12 16,-6", "none", c["glasses"], 3.4))
        s.append(P("M-76,-8 L-106,-14 M76,-8 L106,-14", "none", c["glasses"], 3))
        s.append(P("M8,-8 C14,18 22,40 26,52", "none", c["skin_sh"], 3.4, 'opacity=".55" filter="url(#soft2)"'))
        s.append(P("M-18,56 C-24,50 -28,58 -22,64 C-14,70 -6,68 0,70 C6,68 14,70 22,64 C28,58 24,50 18,56", "none", c["line"], 1.8))
        s.append(P("M-10,64 C-7,66 -4,66 -2,65 M10,64 C7,66 4,66 2,65", "none", "#4a2a22", 2.2))
        s.append(P("M-40,62 C-48,80 -46,96 -38,104 M40,62 C48,80 46,96 38,104", "none", c["skin_sh"], 2, 'opacity=".45"'))    # naso-labial (age)
        if o:
            s.append(P(f"M-30,{94+k} C-14,88 14,88 30,{94+k} C18,{104+o} -18,{104+o} -30,{94+k} Z", "#5a2a27", c["line"], 1.6))
            s.append(P("M-22,93 C-8,90 8,90 22,93 L20,97 C8,95 -8,95 -20,97 Z", "#f0ebe2"))
        else:
            s.append(P(f"M-30,{94+k} C-14,90 14,90 30,{94+k} C14,96 -14,96 -30,{94+k} Z", c["lip"]))
            s.append(P(f"M-26,{95+k} C-10,106 10,106 26,{95+k} C10,98 -10,98 -26,{95+k} Z", c["lip_lt"], extra='opacity=".8"'))
            s.append(P(f"M-30,{94+k} C-14,97 14,97 30,{94+k}", "none", "#6a3a32", 2.2))
        s.append(P("M-18,126 C-6,132 6,132 18,126", "none", c["skin_sh"], 1.8, 'opacity=".45"'))
        # hair: receding at the temples, side part on the left, short sides
        s.append(P("M-118,-40 C-124,-120 -80,-170 -4,-172 C76,-172 122,-126 118,-44 C116,-20 112,0 108,14 C104,-20 100,-56 92,-80 C80,-74 60,-90 50,-112 C20,-120 -20,-120 -50,-112 C-60,-90 -80,-74 -92,-80 C-100,-56 -104,-20 -108,14 C-112,0 -116,-20 -118,-40 Z", c["hair"], c["hair_sh"], 2))
        s.append(P("M-56,-112 C-30,-150 30,-160 96,-120", "none", c["hair_sh"], 2, 'opacity=".7"'))
        s.append(P("M-50,-114 C-58,-130 -60,-150 -50,-164", "none", c["hair_sh"], 2))
        for d, wdt, op in (("M-40,-150 C0,-168 50,-160 90,-128", 5, .55), ("M-30,-136 C10,-150 50,-144 80,-118", 3, .45), ("M-90,-110 C-100,-80 -104,-40 -106,0", 2.4, .45)):
            s.append(P(d, "none", c["hair_lt"], wdt, f'opacity="{op}"'))
    elif view == "34":
        face = "M14,-156 C-50,-156 -88,-118 -95,-62 C-99,-40 -101,-26 -97,-16 C-93,4 -97,28 -91,56 C-82,98 -58,130 -20,142 C20,144 60,126 88,94 C108,70 116,30 116,-30 C116,-110 76,-156 14,-156 Z"
        sh = "M62,-150 C104,-110 120,-40 114,20 C108,80 84,118 44,138 C80,124 104,84 110,40 L140,170 L140,-160 Z"
        lt = "M-74,-118 C-46,-142 -10,-132 -20,-96 C-28,-56 -58,-20 -84,-32 C-96,-56 -92,-98 -74,-118 Z"
        neck = "M-46,112 C-46,140 -50,164 -62,182 L-70,206 L100,206 C90,176 86,140 88,76 Z"
        s.append(shaded("e34_neck", neck, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], "M-60,100 C-10,146 54,144 94,72 L100,206 L40,206 C40,170 30,150 -60,124 Z", "M-40,140 C-30,130 -22,160 -32,190 Z"))
        s.append(P("M76,90 C56,126 24,166 -2,200", "none", c["skin_sh"], 3, 'opacity=".45" filter="url(#soft2)"'))
        s.append(_suit(c, 1))
        s.append(P("M84,-14 C104,-26 112,4 106,28 C102,44 90,48 82,40 Z", c["skin_sh"], c["line"], 2))
        s.append(P("M92,-4 C100,2 100,16 94,26", "none", c["line"], 1.4, 'opacity=".6"'))
        s.append(shaded("e34_face", face, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], sh, lt).replace('url(#soft2)', 'url(#soft)', 1))
        s.append(P("M-90,64 C-70,110 -30,136 10,136 C50,132 80,110 94,84", "none", c["skin_sh"], 10, 'opacity=".16" filter="url(#soft2)"'))
        s.append(_eye(-62, 0, 28, c, "e34f" + expr, lid, low, look=-4, far=True))
        s.append(_eye(14, 0, 42, c, "e34n" + expr, lid, low, look=-6))
        s.append(P(f"M-46,{-34+by-tilt} C-58,{-44+by-tilt*.6} -74,{-46+by} -88,{-36+by} C-74,{-40+by} -60,{-36+by-tilt*.5} -46,{-26+by-tilt} Z", c["brow"]))
        s.append(P(f"M-12,{-34+by-tilt} C8,{-48+by-tilt*.6} 32,{-52+by} 56,{-40+by} C36,{-44+by} 12,{-40+by-tilt*.5} -12,{-26+by-tilt} Z", c["brow"]))
        s.append(f'<rect x="-82" y="-20" width="40" height="40" rx="11" fill="none" stroke="{c["glasses"]}" stroke-width="3.2"/><rect x="-14" y="-22" width="58" height="42" rx="12" fill="none" stroke="{c["glasses"]}" stroke-width="3.4"/>')
        s.append(P("M-42,-6 C-34,-12 -22,-12 -14,-6 M44,-8 L86,-12", "none", c["glasses"], 3.2))
        s.append(P("M-42,-20 C-48,6 -62,30 -70,44 C-74,52 -68,60 -58,60 C-52,64 -44,66 -38,62 C-32,66 -24,62 -22,56", c["skin"], c["line"], 1.8))
        s.append(P("M-46,58 C-44,60 -41,61 -39,60", "none", "#4a2a22", 2.2))
        s.append(P("M-30,64 C-20,80 -18,94 -24,104", "none", c["skin_sh"], 2, 'opacity=".45"'))
        s.append(P(f"M-64,{94+k*.6} C-50,89 -22,89 -6,{94+k} C-22,96 -48,96 -64,{94+k*.6} Z", c["lip"]))
        s.append(P(f"M-60,{95+k*.6} C-46,105 -20,105 -8,{95+k} C-22,98 -46,98 -60,{95+k*.6} Z", c["lip_lt"], extra='opacity=".8"'))
        s.append(P(f"M-64,{94+k*.6} C-46,97 -22,97 -6,{94+k}", "none", "#6a3a32", 2.2))
        s.append(P("M-52,128 C-40,134 -28,134 -18,130", "none", c["skin_sh"], 1.6, 'opacity=".45"'))
        s.append(P("M-108,-40 C-110,-120 -60,-170 10,-172 C80,-172 126,-126 124,-44 C124,-10 120,20 114,40 C108,0 104,-40 96,-66 C80,-66 64,-84 58,-108 C30,-118 -10,-118 -50,-112 C-64,-92 -84,-80 -98,-82 C-102,-60 -104,-40 -106,-20 Z", c["hair"], c["hair_sh"], 2))
        s.append(P("M-50,-112 C-20,-150 40,-160 100,-118", "none", c["hair_sh"], 2, 'opacity=".7"'))
        for d, wdt, op in (("M-40,-150 C0,-168 60,-160 104,-122", 5, .55), ("M20,-150 C70,-140 110,-100 118,-50", 3, .45), ("M100,-60 C108,-30 110,0 110,30", 2.4, .45)):
            s.append(P(d, "none", c["hair_lt"], wdt, f'opacity="{op}"'))
    else:  # profile
        head = ("M30,-158 C-40,-158 -86,-122 -97,-70 C-101,-48 -103,-36 -105,-28 C-104,-18 -100,-12 -102,-6 C-108,12 -122,36 -128,50 "
                "C-128,58 -120,62 -110,62 C-106,68 -106,74 -110,80 C-114,86 -110,92 -104,94 C-110,98 -110,106 -104,112 "
                "C-98,116 -98,124 -102,132 C-104,146 -90,156 -64,156 C-30,156 4,144 24,124 C46,106 64,88 74,66 "
                "C104,36 122,-14 120,-68 C116,-128 86,-158 30,-158 Z")
        neck = "M-62,148 C-60,172 -64,190 -70,206 L100,206 C86,172 76,124 72,64 C46,104 4,138 -62,148 Z"
        s.append(shaded("ep_neck", neck, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], "M-64,138 C0,148 56,114 76,64 L106,206 L56,206 C56,170 36,150 -64,158 Z", "M-54,166 C-44,156 -34,186 -44,204 Z"))
        s.append(P("M56,96 C36,136 6,176 -26,204", "none", c["skin_sh"], 3, 'opacity=".4" filter="url(#soft2)"'))
        s.append(_suit(c, 2))
        s.append(shaded("ep_head", head, c["skin"], c["skin_sh"], c["skin_lt"], c["line"], "M40,-150 C104,-120 128,-50 116,10 C104,64 80,96 44,124 L160,160 L160,-170 Z", "M-84,-110 C-64,-136 -24,-138 -34,-100 C-44,-60 -74,-40 -92,-50 C-102,-70 -96,-96 -84,-110 Z").replace('url(#soft2)', 'url(#soft)', 1))
        s.append(P("M26,-14 C50,-28 64,0 58,26 C54,44 38,50 28,42 C24,22 24,4 26,-14 Z", c["skin"], c["line"], 2))
        s.append(P("M34,-4 C46,0 48,18 40,30", "none", c["line"], 1.4, 'opacity=".6"'))
        eye = f"M-96,-2 C-90,{-10+lid} -78,{-12+lid} -70,-6 C-76,{2-low} -88,{4-low} -96,-2 Z"
        s.append(P(eye, "#f2ebe2")); s.append(f'<clipPath id="epm{expr}"><path d="{eye}"/></clipPath><g clip-path="url(#epm{expr})"><ellipse cx="-90" cy="-3" rx="6" ry="9" fill="{c["iris"]}"/><circle cx="-92" cy="-5" r="1.8" fill="#fff"/></g>')
        s.append(P(f"M-97,-1 C-90,{-12+lid} -78,{-14+lid} -68,-7", "none", c["hair_sh"], 3))
        s.append(P(f"M-104,{-32+by-tilt} C-90,{-42+by-tilt*.5} -70,{-44+by} -54,{-34+by} C-70,{-38+by} -88,{-34+by-tilt*.5} -104,{-26+by-tilt} Z", c["brow"]))
        s.append(f'<rect x="-108" y="-20" width="38" height="38" rx="10" fill="none" stroke="{c["glasses"]}" stroke-width="3.2"/>')
        s.append(P("M-70,-6 L28,-10", "none", c["glasses"], 3.2))
        s.append(P("M-114,56 C-110,58 -106,58 -104,56", "none", "#4a2a22", 2.2))
        s.append(P("M-110,80 C-102,80 -94,84 -90,90", "none", c["lip"], 3)); s.append(P("M-104,94 L-90,94", "none", "#6a3a32", 2.2)); s.append(P("M-104,112 C-100,106 -94,100 -90,96", "none", c["lip_lt"], 3))
        s.append(P("M-86,70 C-80,84 -80,96 -84,104", "none", c["skin_sh"], 2, 'opacity=".45"'))
        s.append(P("M-88,-112 C-60,-152 10,-170 50,-166 C104,-158 132,-110 130,-50 C130,-10 124,24 112,50 C100,20 84,0 70,-16 C56,-34 40,-46 20,-56 C-10,-70 -40,-80 -60,-100 C-70,-106 -80,-108 -88,-112 Z", c["hair"], c["hair_sh"], 2))
        for d, wdt, op in (("M-70,-130 C-20,-162 60,-160 112,-112", 5, .55), ("M-50,-104 C0,-122 60,-110 104,-60", 3, .45), ("M60,-40 C90,-20 110,10 116,40", 2.4, .4)):
            s.append(P(d, "none", c["hair_lt"], wdt, f'opacity="{op}"'))
    return "\n".join(s)


def hand_open(c, flip=1):
    """open palm-up gesture, fingers slightly curled (local frame: wrist at 0,0, fingers toward +x)"""
    f = lambda d: d if flip == 1 else d
    palm = "M0,-22 C30,-30 62,-26 80,-14 C92,-6 96,8 88,18 C72,30 36,32 6,22 C-6,16 -8,-14 0,-22 Z"
    fingers = ["M78,-14 C96,-22 118,-22 132,-14 C138,-10 136,-2 128,0 C114,2 96,0 84,-2 Z",
               "M86,-2 C104,-6 126,-4 140,4 C146,8 142,16 134,16 C118,16 100,14 88,10 Z",
               "M86,10 C102,10 122,14 134,22 C140,26 136,34 128,33 C112,31 98,26 86,20 Z",
               "M80,20 C94,24 110,30 118,38 C122,44 116,48 110,46 C98,42 86,36 78,28 Z",
               "M20,-22 C30,-42 48,-56 66,-60 C74,-61 76,-54 70,-50 C56,-42 46,-32 40,-20 Z"]   # thumb
    o = [P(palm, c["skin"], c["line"], 2)] + [P(d, c["skin"], c["line"], 1.8) for d in fingers]
    o.append(P("M20,4 C40,12 62,12 80,6", "none", c["skin_sh"], 2, 'opacity=".6"'))
    o.append(P("M84,-2 L88,10 M86,10 L84,20", "none", c["skin_sh"], 1.4, 'opacity=".6"'))
    o.append(P("M6,22 C36,32 72,30 88,18 C70,34 30,38 6,30 Z", c["skin_sh"], extra='opacity=".6"'))
    return f'<g transform="scale({flip},1)">' + "".join(o) + "</g>"


def hands_folded(c):
    """two hands resting on a desk, fingers loosely interlaced (wrists at left and right)"""
    o = []
    for sx in (-1, 1):
        o.append(P(f"M{sx*-110},10 C{sx*-80},-8 {sx*-40},-14 {sx*-6},-8 C{sx*8},-4 {sx*10},12 {sx*0},20 C{sx*-30},30 {sx*-80},32 {sx*-110},26 Z", c["skin"], c["line"], 2))
        for j in range(4):
            y = -10 + j * 9
            o.append(P(f"M{sx*-12},{y} C{sx*6},{y-4} {sx*22},{y-2} {sx*30},{y+4} C{sx*32},{y+8} {sx*26},{y+10} {sx*20},{y+9} C{sx*8},{y+8} {sx*-4},{y+8} {sx*-12},{y+6} Z", c["skin_sh"] if j % 2 else c["skin"], c["line"], 1.4))
        o.append(P(f"M{sx*-40},-14 C{sx*-30},-30 {sx*-12},-36 {sx*4},-32 C{sx*10},-30 {sx*8},-22 {sx*0},-22 C{sx*-12},-22 {sx*-24},-16 {sx*-30},-8 Z", c["skin"], c["line"], 1.6))
    o.append(P("M-110,26 C-60,40 60,40 110,26 L110,34 C60,48 -60,48 -110,34 Z", c["skin_sh"], extra='opacity=".35" filter="url(#soft2)"'))
    return "".join(o)


def office_bg(w=1920, h=1080):
    """illustrated bank office, same language as the characters (warm paper, soft light, tinted lines)"""
    o = [f'<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9dcc4"/><stop offset="1" stop-color="#d8c6a8"/></linearGradient>',
         f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe0ea"/><stop offset="1" stop-color="#eef0e6"/></linearGradient>',
         f'<radialGradient id="pool" cx=".3" cy=".25" r=".7"><stop offset="0" stop-color="#fff3d8" stop-opacity=".55"/><stop offset="1" stop-color="#fff3d8" stop-opacity="0"/></radialGradient>',
         f'<rect width="{w}" height="{h}" fill="url(#wall)"/>',
         '<rect x="0" y="640" width="1920" height="440" fill="#b48a62"/>',
         # window with a city beyond
         '<rect x="170" y="110" width="760" height="470" fill="url(#sky)" stroke="#5a4232" stroke-width="10"/>',
         '<path d="M190,580 L190,380 L260,380 L260,330 L330,330 L330,420 L400,420 L400,300 L470,300 L470,580 Z M500,580 L500,400 L560,400 L560,350 L620,350 L620,580 Z M650,580 L650,420 L720,420 L720,280 L800,280 L800,580 Z M820,580 L820,380 L910,380 L910,580 Z" fill="#9fb4c4" opacity=".75"/>',
         '<path d="M170,345 L930,345 M550,110 L550,580" stroke="#5a4232" stroke-width="8"/>',
         '<path d="M170,580 L930,580 L950,600 L150,600 Z" fill="#6e4f3a"/>',
         # light shafts from the window
         '<path d="M170,110 L930,110 L1500,1080 L-200,1080 Z" fill="url(#pool)" opacity=".7"/>',
         # bookshelf and framed certificate
         '<rect x="1240" y="150" width="520" height="520" fill="#6e4a32" stroke="#4a3122" stroke-width="6"/>']
    import random
    rnd = random.Random(4)
    for r in range(4):
        y = 170 + r * 124
        o.append(f'<rect x="1252" y="{y+108}" width="496" height="10" fill="#4a3122"/>')
        x = 1258
        while x < 1730:
            bw = rnd.randint(14, 30); bh = rnd.randint(70, 102); col = rnd.choice(["#8a3b32", "#2f4b6e", "#c79a4a", "#3d5a45", "#e3d8c2", "#5b3b5e"])
            if rnd.random() < .12: x += 30; continue
            o.append(f'<rect x="{x}" y="{y+108-bh}" width="{bw}" height="{bh}" fill="{col}" stroke="#3a2618" stroke-width="1.2"/>'); x += bw + 2
    o.append('<rect x="1010" y="170" width="170" height="220" fill="#f1e8d4" stroke="#4a3122" stroke-width="8"/><text x="1095" y="250" text-anchor="middle" font-family="Georgia" font-size="20" fill="#3a3226">HARBOR</text><text x="1095" y="276" text-anchor="middle" font-family="Georgia" font-size="15" fill="#3a3226">SAVINGS &amp; LOAN</text><circle cx="1095" cy="340" r="14" fill="#9b2f2a"/>')
    o.append('<rect x="0" y="0" width="1920" height="1080" fill="#3a2a20" opacity=".06"/>')
    return "".join(o)


def desk_fg():
    return ('<path d="M-40,780 L1960,780 L1960,1080 L-40,1080 Z" fill="#7a5236"/><path d="M-40,780 L1960,780 L1960,800 L-40,800 Z" fill="#9a6c48"/>'
            '<path d="M-40,800 L1960,800 L1960,830 L-40,830 Z" fill="#5e3d28" opacity=".5"/>'
            '<g transform="translate(880,742) rotate(-4)"><rect x="0" y="0" width="230" height="44" fill="#f4efe2" stroke="#b9a988" stroke-width="2"/><rect x="10" y="8" width="210" height="30" fill="#ebe4d3"/></g>'
            '<path d="M1120,770 L1240,760" stroke="#2a2a2a" stroke-width="6" stroke-linecap="round"/>')


def page(body, w=1920, h=1080, bg="#efe6d6"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:{bg}}} .lbl{{font:600 22px Inter,Arial;fill:#5a4a3a;letter-spacing:1.5px}}
</style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{GRAIN}</defs>
<rect width="{w}" height="{h}" fill="{bg}"/>{body}<rect width="{w}" height="{h}" fill="#000" filter="url(#grain)"/></svg></body></html>"""


if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    body = ""
    if len(sys.argv) > 2 and sys.argv[2] == "scene":
        b = office_bg()
        b += f'<g transform="translate(560,520) scale(1.25)">{nadia_34(expr="worried")}</g>'
        b += f'<g transform="translate(1440,500) scale(1.2)">{elias("profile")}</g>'
        b += desk_fg()
        b += f'<g transform="translate(600,800) scale(1.1)">{hands_folded(NADIA)}</g>'
        b += f'<g transform="translate(1290,790) scale(-1.05,1.05)">{hand_open(ELIAS)}</g>'
        open(out, "w").write(page(b)); raise SystemExit
    if len(sys.argv) > 2 and sys.argv[2] == "hands":
        b = f'<g transform="translate(400,500) scale(2)">{hand_open(NADIA)}</g><g transform="translate(1250,540) scale(2)">{hands_folded(ELIAS)}</g>'
        open(out, "w").write(page(b)); raise SystemExit
    if len(sys.argv) > 2 and sys.argv[2] == "elias":
        for i, (v, lab) in enumerate((("front", "FRONT"), ("34", "THREE-QUARTER"), ("profile", "PROFILE"))):
            body += f'<g transform="translate({330 + i * 620},450) scale(1.3)">{elias(v)}</g><text class="lbl" x="{330 + i * 620}" y="1040" text-anchor="middle">{lab}</text>'
        open(out, "w").write(page(body)); raise SystemExit
    if len(sys.argv) > 2 and sys.argv[2] == "turn":
        for i, (f, lab) in enumerate(((nadia_front, "FRONT"), (nadia_34, "THREE-QUARTER"), (nadia_profile, "PROFILE"))):
            body += f'<g transform="translate({330 + i * 620},450) scale(1.3)">{f()}</g><text class="lbl" x="{330 + i * 620}" y="1040" text-anchor="middle">{lab}</text>'
        open(out, "w").write(page(body)); raise SystemExit
    for i, e in enumerate(("neutral", "smile", "worried", "speaking_ah")):
        body += f'<g transform="translate({250 + i * 475},450) scale(1.2)">{nadia_front(expr=e)}</g>'
        body += f'<text class="lbl" x="{250 + i * 475}" y="1040" text-anchor="middle">{e.upper()}</text>'
    open(out, "w").write(page(body))
