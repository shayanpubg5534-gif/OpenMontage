"""Hand-authored vector characters for 'How Banks Create Money'.

Each character is its own <svg> so GSAP svgOrigin values stay in character-local space.
"""

OUT = "#1b2230"  # outline ink

# ── Maya ────────────────────────────────────────────────────────────────
M = dict(
    skin="#b9744a", skin_sh="#99593a", hair="#2b1b16", hair_hi="#55362a",
    blazer="#1f7a78", blazer_sh="#165c5a", blazer_hi="#2b9390", top="#e3a83b",
    pants="#23324d", pants_sh="#18233a", shoe="#f2efe9", sole="#c9c2b5",
    bag="#8a4b2a", bag_sh="#6b3a20", gold="#d4a24c",
)


def maya_head(p: str) -> str:
    c = M
    return f"""
  <g id="{p}-head">
    <circle cx="112" cy="70" r="27" fill="{c['hair']}" stroke="{OUT}" stroke-width="3"/>
    <circle cx="104" cy="62" r="9" fill="{c['hair_hi']}" opacity=".55"/>
    <path d="M104 98 C96 60 130 42 162 48 C194 54 206 86 198 114 L196 142 C186 152 176 132 176 132 L120 142 C108 132 104 120 104 98Z" fill="{c['hair']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M138 148 L162 148 L165 192 L135 192Z" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M137 158 L163 166 L163 178 L137 172Z" fill="{c['skin_sh']}"/>
    <ellipse cx="124" cy="117" rx="9" ry="13" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M128 82 C150 62 190 70 196 100 C202 126 198 150 180 160 C164 170 142 166 133 150 C124 136 120 102 128 82Z" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M131 100 C128 120 132 142 142 154 C138 136 138 116 142 100Z" fill="{c['skin_sh']}" opacity=".5"/>
    <circle cx="124" cy="133" r="3.6" fill="{c['gold']}" stroke="{OUT}" stroke-width="1.5"/>
    <path d="M120 96 C116 66 146 50 174 56 C198 62 208 84 202 106 C194 94 184 86 172 88 C162 76 148 80 142 92 C134 88 126 94 122 108Z" fill="{c['hair']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M150 62 C162 56 178 58 186 64" stroke="{c['hair_hi']}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".8"/>
    <circle cx="132" cy="78" r="8" fill="{c['hair']}"/><circle cx="196" cy="84" r="7" fill="{c['hair']}"/>
    <ellipse cx="155" cy="114" rx="5.5" ry="7" fill="#fff"/>
    <ellipse cx="181" cy="114" rx="6.5" ry="8" fill="#fff"/>
    <circle cx="157" cy="115" r="3.8" fill="#2b1a10"/><circle cx="183.5" cy="115" r="4.4" fill="#2b1a10"/>
    <circle cx="158.4" cy="113.4" r="1.3" fill="#fff"/><circle cx="185" cy="113.2" r="1.5" fill="#fff"/>
    <g class="lids">
      <ellipse class="lid" cx="155" cy="114" rx="6.5" ry="8" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
      <ellipse class="lid" cx="181" cy="114" rx="7.5" ry="9" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
    </g>
    <path d="M175 106 Q182 102 190 105" stroke="{OUT}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M147 102 Q154 97 162 100" stroke="{c['hair']}" stroke-width="3.6" fill="none" stroke-linecap="round"/>
    <path d="M173 99 Q181 94 190 98" stroke="{c['hair']}" stroke-width="3.6" fill="none" stroke-linecap="round"/>
    <path d="M191 118 Q199 129 190 132" stroke="{c['skin_sh']}" stroke-width="2.8" fill="none" stroke-linecap="round"/>
    <path id="{p}-mouth" d="M170 141 Q181 152 191 139 Q181 145 170 141Z" fill="#8e3b3b" stroke="{OUT}" stroke-width="2"/>
    <ellipse cx="176" cy="131" rx="9" ry="5" fill="#e0705a" opacity=".35"/>
  </g>"""


def maya_torso(p: str) -> str:
    c = M
    return f"""
  <g id="{p}-torso">
    <path d="M110 198 C118 182 182 182 192 198 L198 302 C198 322 188 336 180 338 L120 338 C112 336 102 322 102 302Z" fill="{c['blazer']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M110 198 C106 240 104 290 106 320 C112 330 118 336 124 338 L122 250Z" fill="{c['blazer_sh']}" opacity=".8"/>
    <path d="M180 200 C186 240 190 280 188 318" stroke="{c['blazer_hi']}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
    <path d="M136 188 L164 188 L150 238Z" fill="{c['top']}" stroke="{OUT}" stroke-width="2.5"/>
    <path d="M136 188 L150 238 L140 254 L126 200Z" fill="{c['blazer_sh']}" stroke="{OUT}" stroke-width="2.5"/>
    <path d="M164 188 L150 238 L160 254 L174 200Z" fill="{c['blazer_hi']}" stroke="{OUT}" stroke-width="2.5"/>
    <circle cx="151" cy="266" r="4.5" fill="{c['gold']}" stroke="{OUT}" stroke-width="1.5"/>
    <circle cx="151" cy="294" r="4.5" fill="{c['gold']}" stroke="{OUT}" stroke-width="1.5"/>
    <path d="M168 300 L186 300" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M178 192 L122 318" stroke="{c['bag_sh']}" stroke-width="6" stroke-linecap="round"/>
    <rect x="98" y="300" width="50" height="40" rx="9" fill="{c['bag']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M98 314 Q123 326 148 314 L148 309 Q123 318 98 309Z" fill="{c['bag_sh']}"/>
    <circle cx="123" cy="321" r="3.5" fill="{c['gold']}"/>
  </g>"""


def maya_leg(p: str, which: str) -> str:
    c = M
    fill = c["pants_sh"] if which == "back" else c["pants"]
    return f"""
  <g id="{p}-leg-{which}">
    <path d="M134 326 L166 326 L165 470 L139 470Z" fill="{fill}" stroke="{OUT}" stroke-width="3"/>
    <path d="M152 340 L154 460" stroke="{OUT}" stroke-opacity=".25" stroke-width="2"/>
    <path d="M135 468 L167 468 C183 470 190 480 188 490 L135 490Z" fill="{c['shoe']}" stroke="{OUT}" stroke-width="3"/>
    <rect x="135" y="486" width="53" height="6" rx="3" fill="{c['sole']}" stroke="{OUT}" stroke-width="2"/>
  </g>"""


def maya_arm(p: str, which: str, hold_phone: bool = False) -> str:
    c = M
    fill = c["blazer_sh"] if which == "back" else c["blazer"]
    phone = ""
    if hold_phone:
        phone = (f'<rect x="138" y="300" width="26" height="46" rx="5" fill="#14213d" stroke="{OUT}" stroke-width="2.5"/>'
                 f'<rect x="141" y="305" width="20" height="34" rx="2" fill="#7fe0c4" class="phoneglow"/>')
    return f"""
  <g id="{p}-arm-{which}">
    <path d="M138 198 C150 192 164 198 166 208 L160 304 L140 304 L134 208Z" fill="{fill}" stroke="{OUT}" stroke-width="3"/>
    <path d="M140 296 L160 296 L160 306 L140 306Z" fill="{c['top']}" stroke="{OUT}" stroke-width="2"/>
    {phone}
    <ellipse cx="150" cy="318" rx="11" ry="13" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
  </g>"""


def maya_svg(p: str, mode: str = "walk", cls: str = "") -> str:
    """mode: walk (full body) | bust (no legs) | phone (bust, front arm holds phone)."""
    parts = [maya_arm(p, "back")]
    if mode == "walk":
        parts += [maya_leg(p, "back"), maya_leg(p, "front")]
    parts += [f'<g id="{p}-upper">', maya_torso(p), maya_head(p),
              maya_arm(p, "front", hold_phone=(mode == "phone")), "</g>"]
    vb = "0 0 300 500" if mode == "walk" else "0 0 300 360"
    return (f'<svg id="{p}" class="char {cls}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            + "".join(parts) + "</svg>")


# ── Loan officer (Mr. Okafor) ──────────────────────────────────────────
B = dict(skin="#e7b08a", skin_sh="#c88b66", hair="#c3c6cc", beard="#a7adb5", suit="#2a3550",
         suit_sh="#1e273d", suit_hi="#3a4868", shirt="#f6f3ec", tie="#c0392b", tie_sh="#962d22",
         gold="#d4a24c")


def banker_svg(p: str, cls: str = "") -> str:
    c = B
    return f"""<svg id="{p}" class="char {cls}" viewBox="0 0 360 420" xmlns="http://www.w3.org/2000/svg" overflow="visible">
 <g transform="translate(360 0) scale(-1 1)">
  <g id="{p}-arm-back">
    <path d="M118 214 C100 220 92 240 92 260 L88 360 L120 362 L130 240Z" fill="{c['suit_sh']}" stroke="{OUT}" stroke-width="3"/>
  </g>
  <path d="M100 214 C112 186 252 186 264 214 L278 420 L84 420Z" fill="{c['suit']}" stroke="{OUT}" stroke-width="3"/>
  <path d="M100 214 C94 280 90 360 88 420 L130 420 L126 250Z" fill="{c['suit_sh']}" opacity=".7"/>
  <path d="M248 220 C258 290 264 360 268 410" stroke="{c['suit_hi']}" stroke-width="6" fill="none" opacity=".7" stroke-linecap="round"/>
  <path d="M162 186 L202 186 L182 250Z" fill="{c['shirt']}" stroke="{OUT}" stroke-width="2.5"/>
  <path d="M175 194 L189 194 L193 214 L185 300 L182 304 L179 300 L171 214Z" fill="{c['tie']}" stroke="{OUT}" stroke-width="2.5"/>
  <path d="M173 230 L192 222 M172 252 L190 244 M174 274 L188 268" stroke="{c['tie_sh']}" stroke-width="4"/>
  <path d="M162 186 L182 250 L166 268 L144 200Z" fill="{c['suit_hi']}" stroke="{OUT}" stroke-width="2.5"/>
  <path d="M202 186 L182 250 L198 268 L220 200Z" fill="{c['suit_sh']}" stroke="{OUT}" stroke-width="2.5"/>
  <path d="M222 262 L246 262 L244 272 L224 272Z" fill="{c['gold']}" stroke="{OUT}" stroke-width="2"/>
  <path d="M164 160 L200 160 L202 194 L162 194Z" fill="{c['skin_sh']}" stroke="{OUT}" stroke-width="3"/>
  <g id="{p}-head">
    <ellipse cx="140" cy="122" rx="11" ry="15" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M134 92 C138 50 184 38 212 56 C234 70 238 104 232 132 C228 160 212 180 186 184 C160 186 140 170 134 142Z" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M136 100 C132 124 134 146 146 162 C142 140 142 118 146 100Z" fill="{c['skin_sh']}" opacity=".55"/>
    <ellipse cx="192" cy="62" rx="18" ry="7" fill="#fff" opacity=".35"/>
    <path d="M130 100 C126 124 130 142 140 152 L146 132 C142 116 144 102 152 90 C142 84 134 90 130 100Z" fill="{c['hair']}" stroke="{OUT}" stroke-width="2.5"/>
    <path d="M150 150 C158 190 218 196 234 138 C228 162 212 172 198 168 C188 164 176 164 166 168 C160 164 154 158 150 150Z" fill="{c['beard']}" stroke="{OUT}" stroke-width="2.5"/>
    <path d="M194 148 C202 138 220 138 228 148 C216 144 206 150 194 148Z" fill="{c['beard']}" stroke="{OUT}" stroke-width="2"/>
    <path d="M204 157 Q214 163 222 155" stroke="#6b2b2b" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M227 112 Q244 128 228 136" fill="{c['skin_sh']}" stroke="{OUT}" stroke-width="2.5"/>
    <circle cx="190" cy="116" r="3.8" fill="#2b1a10"/><circle cx="216" cy="116" r="3.6" fill="#2b1a10"/>
    <circle cx="191.2" cy="114.8" r="1.2" fill="#fff"/><circle cx="217.2" cy="114.8" r="1.2" fill="#fff"/>
    <g class="lids">
      <ellipse class="lid" cx="190" cy="115" rx="6" ry="7" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
      <ellipse class="lid" cx="216" cy="115" rx="6" ry="7" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
    </g>
    <path d="M178 100 Q190 92 202 98" stroke="{c['beard']}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="M208 98 Q218 92 228 98" stroke="{c['beard']}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <rect x="176" y="104" width="28" height="22" rx="7" fill="#dff0ff" fill-opacity=".3" stroke="#22262e" stroke-width="3"/>
    <rect x="206" y="104" width="24" height="22" rx="7" fill="#dff0ff" fill-opacity=".3" stroke="#22262e" stroke-width="3"/>
    <path d="M204 112 L206 112 M176 112 L146 110" stroke="#22262e" stroke-width="3"/>
    <path d="M180 108 L186 104" stroke="#fff" stroke-width="2.5" opacity=".7" stroke-linecap="round"/>
  </g>
  <g id="{p}-arm-front">
    <path d="M226 206 C246 198 264 208 266 226 L272 330 L238 336 L230 240Z" fill="{c['suit']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M238 326 L272 322 L273 336 L239 340Z" fill="{c['shirt']}" stroke="{OUT}" stroke-width="2"/>
    <g id="{p}-stamp" opacity="0">
      <rect x="244" y="350" width="22" height="40" rx="6" fill="#8a5a3c" stroke="{OUT}" stroke-width="2.5"/>
      <rect x="236" y="386" width="38" height="12" rx="3" fill="#c0392b" stroke="{OUT}" stroke-width="2.5"/>
    </g>
    <ellipse cx="256" cy="346" rx="17" ry="15" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
  </g>
 </g>
</svg>"""


# ── Configurable cast (same rig as Maya: walk / bust / phone poses, blink lids, pivots) ──
# Reuse the rig, vary the person: hair style, skin, clothing, accessories. Pivots are identical to
# Maya's (hip 150 330, shoulder 150 204), so kit/helpers.js walk()/blink()/talk() work unchanged.
LOOKS = {
    "dan_1999": dict(skin="#e3b08c", skin_sh="#c48d6a", hair="#6b4a2b", hair_hi="#8d6a45", hair_style="short",
                     jacket="#4f6b3a", jacket_sh="#3c5330", jacket_hi="#6a8a4f", shirt="#e8e2cf",
                     pants="#b89a6c", pants_sh="#9a7f56", shoe="#5a3a22", sole="#3a2616", glasses=True, tie=None,
                     bag=False, earring=False),
    "investor_1999": dict(skin="#d9a27c", skin_sh="#b9805e", hair="#3b3b3b", hair_hi="#5c5c5c", hair_style="parted",
                          jacket="#2e3c5c", jacket_sh="#222d45", jacket_hi="#3e5078", shirt="#f3efe4",
                          pants="#2e3c5c", pants_sh="#222d45", shoe="#1f1a16", sole="#111", glasses=False,
                          tie="#9b2f2f", bag=False, earring=False),
    "employee_1999": dict(skin="#8a5a3c", skin_sh="#6e452c", hair="#1d1410", hair_hi="#3a2a20", hair_style="curly",
                          jacket="#b5452f", jacket_sh="#8f3523", jacket_hi="#cf6048", shirt="#f0e6d2",
                          pants="#3c4a68", pants_sh="#2c3850", shoe="#e9e3d6", sole="#bdb5a5", glasses=False,
                          tie=None, bag=False, earring=True),
    "cfo_modern": dict(skin="#c68a63", skin_sh="#a56d4b", hair="#1f1a1a", hair_hi="#3d3333", hair_style="short",
                       jacket="#1f2b40", jacket_sh="#151e2e", jacket_hi="#2f4060", shirt="#dfe9f5",
                       pants="#1f2b40", pants_sh="#151e2e", shoe="#14110f", sole="#000", glasses=True,
                       tie=None, bag=False, earring=False),
}

_HAIR = {
    # back mass, front fringe, extra (drawn over the face outline)
    "short": ('<path d="M120 100 C112 62 146 44 176 52 C200 58 208 80 202 104 C196 94 186 88 172 90 C160 80 144 84 136 96 C130 92 124 96 122 108Z" fill="{hair}" stroke="{o}" stroke-width="3"/>',
              '<path d="M150 60 C164 54 182 58 190 66" stroke="{hair_hi}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".8"/>'),
    "parted": ('<path d="M118 104 C110 64 146 42 178 50 C204 56 210 82 204 106 C198 90 182 78 160 80 C150 82 140 90 132 102 C126 100 122 102 120 112Z" fill="{hair}" stroke="{o}" stroke-width="3"/>',
               '<path d="M160 52 C158 62 156 72 152 80" stroke="{hair_hi}" stroke-width="3" fill="none"/><path d="M126 104 C124 116 124 126 128 134" stroke="{hair}" stroke-width="7" stroke-linecap="round"/>'),
    "curly": ('<g fill="{hair}" stroke="{o}" stroke-width="3">' + "".join(
                f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                [(128, 82, 17), (146, 64, 19), (168, 58, 19), (190, 70, 17), (202, 92, 13), (122, 104, 14), (136, 70, 14)]) + "</g>",
              '<g fill="{hair_hi}" opacity=".6"><circle cx="150" cy="60" r="5"/><circle cx="172" cy="55" r="4"/></g>'),
}


def person_svg(p: str, look: str | dict, mode: str = "walk", cls: str = "") -> str:
    """Any cast member on Maya's rig. look: a LOOKS key or a dict of the same fields."""
    c = dict(LOOKS[look]) if isinstance(look, str) else dict(look)
    c.setdefault("gold", "#d4a24c")
    hair_back, hair_hi = _HAIR[c["hair_style"]]
    hair_back = hair_back.format(o=OUT, **c)
    hair_hi = hair_hi.format(o=OUT, **c)
    glasses = (f'<rect x="146" y="105" width="20" height="17" rx="5" fill="#dff0ff" fill-opacity=".25" stroke="#22262e" stroke-width="2.5"/>'
               f'<rect x="172" y="105" width="20" height="17" rx="5" fill="#dff0ff" fill-opacity=".25" stroke="#22262e" stroke-width="2.5"/>'
               f'<path d="M166 112 L172 112 M146 112 L128 110" stroke="#22262e" stroke-width="2.5"/>') if c.get("glasses") else ""
    earring = f'<circle cx="124" cy="133" r="3.6" fill="{c["gold"]}" stroke="{OUT}" stroke-width="1.5"/>' if c.get("earring") else ""
    head = f"""
  <g id="{p}-head">
    <path d="M138 148 L162 148 L165 192 L135 192Z" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M137 158 L163 166 L163 178 L137 172Z" fill="{c['skin_sh']}"/>
    <ellipse cx="124" cy="117" rx="9" ry="13" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M128 82 C150 62 190 70 196 100 C202 126 198 150 180 160 C164 170 142 166 133 150 C124 136 120 102 128 82Z" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M131 100 C128 120 132 142 142 154 C138 136 138 116 142 100Z" fill="{c['skin_sh']}" opacity=".5"/>
    {earring}
    {hair_back}{hair_hi}
    <ellipse cx="155" cy="114" rx="5.5" ry="7" fill="#fff"/><ellipse cx="181" cy="114" rx="6.5" ry="8" fill="#fff"/>
    <circle cx="157" cy="115" r="3.8" fill="#2b1a10"/><circle cx="183.5" cy="115" r="4.4" fill="#2b1a10"/>
    <circle cx="158.4" cy="113.4" r="1.3" fill="#fff"/><circle cx="185" cy="113.2" r="1.5" fill="#fff"/>
    <g class="lids">
      <ellipse class="lid" cx="155" cy="114" rx="6.5" ry="8" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
      <ellipse class="lid" cx="181" cy="114" rx="7.5" ry="9" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
    </g>
    <path id="{p}-brows" d="M147 101 Q154 97 162 100 M173 99 Q181 94 190 98" stroke="{c['hair']}" stroke-width="3.6" fill="none" stroke-linecap="round"/>
    {glasses}
    <path d="M191 118 Q199 129 190 132" stroke="{c['skin_sh']}" stroke-width="2.8" fill="none" stroke-linecap="round"/>
    <path id="{p}-mouth" d="M170 141 Q181 150 191 139 Q181 145 170 141Z" fill="#8e3b3b" stroke="{OUT}" stroke-width="2"/>
  </g>"""
    tie = (f'<path d="M146 192 L154 192 L157 212 L151 262 L148 266 L145 262 L143 212Z" fill="{c["tie"]}" stroke="{OUT}" stroke-width="2"/>'
           if c.get("tie") else "")
    torso = f"""
  <g id="{p}-torso">
    <path d="M110 198 C118 182 182 182 192 198 L198 302 C198 322 188 336 180 338 L120 338 C112 336 102 322 102 302Z" fill="{c['jacket']}" stroke="{OUT}" stroke-width="3"/>
    <path d="M110 198 C106 240 104 290 106 320 C112 330 118 336 124 338 L122 250Z" fill="{c['jacket_sh']}" opacity=".8"/>
    <path d="M180 200 C186 240 190 280 188 318" stroke="{c['jacket_hi']}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
    <path d="M136 188 L164 188 L150 238Z" fill="{c['shirt']}" stroke="{OUT}" stroke-width="2.5"/>
    {tie}
    <path d="M136 188 L150 238 L140 254 L126 200Z" fill="{c['jacket_sh']}" stroke="{OUT}" stroke-width="2.5"/>
    <path d="M164 188 L150 238 L160 254 L174 200Z" fill="{c['jacket_hi']}" stroke="{OUT}" stroke-width="2.5"/>
  </g>"""

    def leg(which):
        fill = c["pants_sh"] if which == "back" else c["pants"]
        return f"""
  <g id="{p}-leg-{which}">
    <path d="M134 326 L166 326 L165 470 L139 470Z" fill="{fill}" stroke="{OUT}" stroke-width="3"/>
    <path d="M135 468 L167 468 C183 470 190 480 188 490 L135 490Z" fill="{c['shoe']}" stroke="{OUT}" stroke-width="3"/>
    <rect x="135" y="486" width="53" height="6" rx="3" fill="{c['sole']}" stroke="{OUT}" stroke-width="2"/>
  </g>"""

    def arm(which, prop=""):
        fill = c["jacket_sh"] if which == "back" else c["jacket"]
        return f"""
  <g id="{p}-arm-{which}">
    <path d="M138 198 C150 192 164 198 166 208 L160 304 L140 304 L134 208Z" fill="{fill}" stroke="{OUT}" stroke-width="3"/>
    <path d="M140 296 L160 296 L160 306 L140 306Z" fill="{c['shirt']}" stroke="{OUT}" stroke-width="2"/>
    {prop}
    <ellipse cx="150" cy="318" rx="11" ry="13" fill="{c['skin']}" stroke="{OUT}" stroke-width="3"/>
  </g>"""
    box = (f'<g id="{p}-box"><rect x="108" y="300" width="96" height="62" rx="4" fill="#c8a06a" stroke="{OUT}" stroke-width="3"/>'
           f'<path d="M108 314 H204" stroke="#a5814f" stroke-width="3"/><rect x="128" y="286" width="22" height="18" fill="#e9e3d6" stroke="{OUT}" stroke-width="2"/>'
           f'<circle cx="176" cy="292" r="10" fill="#4aa57c" stroke="{OUT}" stroke-width="2"/></g>') if mode == "box" else ""
    parts = [arm("back")]
    if mode in ("walk", "box"):
        parts += [leg("back"), leg("front")]
    parts += [f'<g id="{p}-upper">', torso, head, box, arm("front"), "</g>"]
    vb = "0 0 300 500" if mode in ("walk", "box") else "0 0 300 360"
    return (f'<svg id="{p}" class="char {cls}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            + "".join(parts) + "</svg>")
