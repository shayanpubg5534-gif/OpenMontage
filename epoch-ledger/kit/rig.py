"""Epoch Ledger jointed character rig (v2): two-segment arms and legs, neck pivot, hand props.

Same 300x500 viewBox and outline style as the v1 cast, so placement code is unchanged, but every
limb bends: shoulder → elbow → hand, hip → knee → foot. Pair with kit/rig.js (poses, natural walk,
seeded ambient motion). Pivots (viewBox units):
    neck 150,182 · shoulder 150,204 · elbow 150,262 · hip 150,330 · knee 150,400

    rig_svg("t1", crowd_look(7), mode="full", prop_front="phone")
"""
from __future__ import annotations

from .characters import OUT

SKINS = [("#f2c9a6", "#d6a684"), ("#e3b08c", "#c48d6a"), ("#c68a63", "#a56d4b"), ("#a8714c", "#8a5a3c"),
         ("#8a5a3c", "#6e452c"), ("#6b4430", "#523322")]
HAIRS = ["#1d1410", "#3b2a20", "#6b4a2b", "#9a6a3a", "#c9a46a", "#5c5c5c", "#2b2b2b", "#8a3a22"]
STYLES = ["short", "parted", "curly", "bun", "bald", "long", "buzz"]
JACKETS = [("#2e6fbf", "#235596", "#4a8ad6"), ("#c8453b", "#9c342c", "#e0645a"), ("#e0b53a", "#b8922a", "#f2cf62"),
           ("#3f8f5a", "#2f6c44", "#5aae76"), ("#7a4bb0", "#5c3888", "#9468c8"), ("#e07a2e", "#b35f22", "#f0984e"),
           ("#1f8fa0", "#176c79", "#36aebe"), ("#2e3c5c", "#222d45", "#3e5078"), ("#6b6f78", "#50535a", "#8a8e98")]
SHIRTS = ["#f3efe4", "#dfe9f5", "#f5e6c8", "#e8d9f0", "#ffffff"]
PANTS = [("#23324d", "#1a2539"), ("#3a3a40", "#2a2a2e"), ("#5a4a38", "#463828"), ("#b89a6c", "#9a7f56"), ("#2e3c5c", "#222d45")]
TIES = [None, "#9b2f2f", "#2f4f9b", "#d4a24c", "#2f7d5b", None]


def crowd_look(i: int, **over) -> dict:
    """Deterministic varied look for crowd member i (skin, hair, style, jacket, shirt, tie, glasses)."""
    def pick(seq, k):
        return seq[(i * k + i // 3) % len(seq)]
    sk, sk_sh = pick(SKINS, 5)
    j, j_sh, j_hi = pick(JACKETS, 7)
    pa, pa_sh = pick(PANTS, 3)
    look = dict(skin=sk, skin_sh=sk_sh, hair=pick(HAIRS, 11), hair_style=pick(STYLES, 13), jacket=j, jacket_sh=j_sh,
                jacket_hi=j_hi, shirt=pick(SHIRTS, 17), pants=pa, pants_sh=pa_sh, shoe=["#1f1a16", "#5a3a22", "#2a2a2a"][i % 3],
                tie=pick(TIES, 19), glasses=(i * 7) % 5 == 0, badge=True, height=0.94 + ((i * 37) % 13) / 100)
    look.update(over)
    return look


def _hair(c, back: bool) -> str:
    h, hi, o = c["hair"], c.get("hair_hi", c["hair"]), OUT
    st = c["hair_style"]
    if st == "bald":
        return "" if back else f'<path d="M132 92 C140 70 176 64 194 86" stroke="{h}" stroke-width="5" fill="none" opacity=".7"/>'
    if back:
        if st == "long":
            return f'<path d="M112 100 C104 60 140 40 172 46 C204 52 212 86 206 120 L210 190 C190 200 150 200 128 186 L118 150Z" fill="{h}" stroke="{o}" stroke-width="3"/>'
        if st == "bun":
            return f'<circle cx="112" cy="70" r="26" fill="{h}" stroke="{o}" stroke-width="3"/>'
        return ""
    if st == "curly":
        return (f'<g fill="{h}" stroke="{o}" stroke-width="3">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                [(128, 82, 17), (146, 64, 19), (168, 58, 19), (190, 70, 17), (202, 92, 13), (122, 104, 14), (136, 70, 14)]) + "</g>")
    if st == "buzz":
        return f'<path d="M124 100 C120 66 150 52 176 56 C198 60 206 80 202 100 C196 88 160 80 130 104Z" fill="{h}" opacity=".85"/>'
    if st == "parted":
        return (f'<path d="M118 104 C110 64 146 42 178 50 C204 56 210 82 204 106 C198 90 182 78 160 80 C150 82 140 90 132 102 C126 100 122 102 120 112Z" fill="{h}" stroke="{o}" stroke-width="3"/>'
                f'<path d="M160 52 C158 62 156 72 152 80" stroke="{hi}" stroke-width="3" fill="none"/>')
    if st == "long":
        return f'<path d="M120 96 C116 66 146 50 174 56 C198 62 208 84 202 106 C192 92 176 84 160 86 C146 86 132 96 124 112Z" fill="{h}" stroke="{o}" stroke-width="3"/>'
    if st == "bun":
        return f'<path d="M120 96 C116 66 146 50 174 56 C198 62 208 84 202 106 C194 94 184 86 172 88 C162 76 148 80 142 92 C134 88 126 94 122 108Z" fill="{h}" stroke="{o}" stroke-width="3"/>'
    return f'<path d="M120 100 C112 62 146 44 176 52 C200 58 208 80 202 104 C196 94 186 88 172 90 C160 80 144 84 136 96 C130 92 124 96 122 108Z" fill="{h}" stroke="{o}" stroke-width="3"/>'


PROPS = {
    "phone": '<g><rect x="138" y="300" width="22" height="40" rx="4" fill="#2a2a2e" stroke="{o}" stroke-width="2.5"/><rect x="141" y="290" width="16" height="14" rx="3" fill="#2a2a2e"/></g>',
    "receiver": '<g><path d="M132 300 C128 330 172 330 168 300" stroke="#2a2a2e" stroke-width="12" fill="none" stroke-linecap="round"/></g>',
    "ticket": '<rect x="134" y="296" width="34" height="26" rx="2" fill="#fffaf0" stroke="{o}" stroke-width="2" transform="rotate(-10 150 309)"/>',
    "pad": '<g><rect x="128" y="300" width="44" height="54" rx="3" fill="#fff6d8" stroke="{o}" stroke-width="2.5"/><path d="M134 314 H164 M134 324 H160 M134 334 H164" stroke="#7a8aa0" stroke-width="2"/></g>',
    "pen": '<path d="M150 300 L156 336" stroke="#1f3a7a" stroke-width="5" stroke-linecap="round"/>',
    "newspaper": '<g><rect x="118" y="292" width="70" height="52" fill="#efe9da" stroke="{o}" stroke-width="2.5"/><path d="M124 302 H180 M124 312 H170 M124 322 H176" stroke="#6b6b6b" stroke-width="3"/></g>',
    "hammer": '<g><path d="M150 318 L150 206" stroke="#7a5230" stroke-width="7" stroke-linecap="round"/><rect x="132" y="190" width="36" height="20" rx="3" fill="#4a4e56" stroke="{o}" stroke-width="2.5"/></g>',
    "shovel": '<g><path d="M150 318 L150 420" stroke="#7a5230" stroke-width="6" stroke-linecap="round"/><path d="M138 418 L162 418 L158 450 Q150 458 142 450Z" fill="#6b7078" stroke="{o}" stroke-width="2.5"/></g>',
    "suitcase": '<g><rect x="126" y="326" width="50" height="38" rx="5" fill="#7a4a2a" stroke="{o}" stroke-width="2.5"/><path d="M142 326 Q150 316 158 326" stroke="{o}" stroke-width="3" fill="none"/><path d="M126 340 H176" stroke="#c9a15a" stroke-width="3"/></g>',
    "sack": '<g><path d="M128 300 Q124 352 150 356 Q178 352 172 300 Q150 290 128 300Z" fill="#c9b48a" stroke="{o}" stroke-width="2.5"/><path d="M140 300 L160 300" stroke="#8a7350" stroke-width="3"/></g>',
    "coin": '<circle cx="150" cy="306" r="9" fill="#f2c66d" stroke="#8a6a1c" stroke-width="2.5"/>',
    "tablet": '<g><rect x="126" y="292" width="52" height="38" rx="5" fill="#20242c" stroke="{o}" stroke-width="2.5"/><rect x="131" y="297" width="42" height="28" rx="2" fill="#7fd8ff"/></g>',
    "coffee": '<g><rect x="138" y="300" width="24" height="30" rx="3" fill="#f4ead5" stroke="{o}" stroke-width="2.5"/><path d="M162 306 C172 306 172 320 162 320" stroke="{o}" stroke-width="2.5" fill="none"/></g>',
}


def rig_svg(p: str, c: dict, mode: str = "full", prop_front: str | None = None, prop_back: str | None = None,
            cls: str = "") -> str:
    """mode: full (whole body) | bust (no legs). Faces right (+x); flip with CSS scaleX(-1)."""
    o = OUT
    pants, pants_sh = c["pants"], c["pants_sh"]
    jk, jk_sh, jk_hi = c["jacket"], c["jacket_sh"], c["jacket_hi"]

    def arm(side):
        fill = jk_sh if side == "back" else jk
        prop = PROPS.get(prop_front if side == "front" else prop_back, "")
        return f"""<g id="{p}-uarm-{side}">
  <path d="M136 200 C148 192 164 198 166 208 L163 266 L139 266Z" fill="{fill}" stroke="{o}" stroke-width="3"/>
  <g id="{p}-farm-{side}">
   <path d="M139 258 L163 258 L160 304 L141 304Z" fill="{fill}" stroke="{o}" stroke-width="3"/>
   <path d="M140 296 L160 296 L160 306 L140 306Z" fill="{c['shirt']}" stroke="{o}" stroke-width="2"/>
   <g id="{p}-prop-{side}">{prop.format(o=o)}</g>
   <ellipse cx="150" cy="316" rx="11" ry="12" fill="{c['skin']}" stroke="{o}" stroke-width="3"/>
  </g></g>"""

    def leg(side):
        fill = pants_sh if side == "back" else pants
        return f"""<g id="{p}-thigh-{side}">
  <path d="M133 324 L167 324 L164 404 L138 404Z" fill="{fill}" stroke="{o}" stroke-width="3"/>
  <g id="{p}-shin-{side}">
   <path d="M138 398 L164 398 L162 470 L141 470Z" fill="{fill}" stroke="{o}" stroke-width="3"/>
   <path d="M136 468 L166 468 C182 470 189 480 187 490 L136 490Z" fill="{c['shoe']}" stroke="{o}" stroke-width="3"/>
  </g></g>"""

    tie = (f'<path d="M146 192 L154 192 L157 212 L151 262 L148 266 L145 262 L143 212Z" fill="{c["tie"]}" stroke="{o}" stroke-width="2"/>'
           if c.get("tie") else "")
    badge = (f'<rect x="168" y="232" width="20" height="14" rx="2" fill="#fffaf0" stroke="{o}" stroke-width="1.5"/>'
             if c.get("badge") else "")
    hc = c.get("hat_col")
    hat = {"cap": f'<path d="M126 86 C132 58 186 54 198 84 L212 90 C200 96 150 96 126 92Z" fill="{hc or "#5a4a3a"}" stroke="{o}" stroke-width="3"/>',
           "bowler": f'<path d="M122 90 L206 90 C204 96 124 98 122 90Z M134 90 C134 56 194 54 194 90Z" fill="{hc or "#2a2420"}" stroke="{o}" stroke-width="3"/>',
           "top": f'<path d="M120 88 L208 88 C206 96 122 96 120 88Z M138 88 L142 34 L188 34 L190 88Z" fill="{hc or "#1e1c1c"}" stroke="{o}" stroke-width="3"/>',
           "hard": f'<path d="M124 90 C124 52 200 50 202 90 L210 94 L118 94Z" fill="{hc or "#f2b632"}" stroke="{o}" stroke-width="3"/>',
           "bonnet": f'<path d="M116 120 C104 60 170 40 206 80 C196 70 140 70 124 124Z" fill="{hc or "#c98a6a"}" stroke="{o}" stroke-width="3"/>',
           }.get(c.get("hat"), "")
    glasses = (f'<rect x="146" y="105" width="20" height="17" rx="5" fill="#dff0ff" fill-opacity=".25" stroke="#22262e" stroke-width="2.5"/>'
               f'<rect x="172" y="105" width="20" height="17" rx="5" fill="#dff0ff" fill-opacity=".25" stroke="#22262e" stroke-width="2.5"/>'
               f'<path d="M166 112 L172 112" stroke="#22262e" stroke-width="2.5"/>') if c.get("glasses") else ""
    head = f"""<g id="{p}-head">
  <path d="M138 148 L162 148 L165 192 L135 192Z" fill="{c['skin']}" stroke="{o}" stroke-width="3"/>
  <path d="M137 158 L163 166 L163 178 L137 172Z" fill="{c['skin_sh']}"/>
  {_hair(c, True)}
  <ellipse cx="124" cy="117" rx="9" ry="13" fill="{c['skin']}" stroke="{o}" stroke-width="3"/>
  <path d="M128 82 C150 62 190 70 196 100 C202 126 198 150 180 160 C164 170 142 166 133 150 C124 136 120 102 128 82Z" fill="{c['skin']}" stroke="{o}" stroke-width="3"/>
  <path d="M131 100 C128 120 132 142 142 154 C138 136 138 116 142 100Z" fill="{c['skin_sh']}" opacity=".5"/>
  {_hair(c, False)}
  <ellipse cx="155" cy="114" rx="5.5" ry="7" fill="#fff"/><ellipse cx="181" cy="114" rx="6.5" ry="8" fill="#fff"/>
  <g id="{p}-pupils"><circle cx="157" cy="115" r="3.8" fill="#2b1a10"/><circle cx="183.5" cy="115" r="4.4" fill="#2b1a10"/></g>
  <g class="lids"><ellipse class="lid" cx="155" cy="114" rx="6.5" ry="8" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/>
   <ellipse class="lid" cx="181" cy="114" rx="7.5" ry="9" fill="{c['skin']}" transform="scale(1 0)" style="transform-box:fill-box;transform-origin:50% 0%"/></g>
  <path id="{p}-brows" d="M147 101 Q154 97 162 100 M173 99 Q181 94 190 98" stroke="{c['hair'] if c['hair_style'] != 'bald' else c['skin_sh']}" stroke-width="3.6" fill="none" stroke-linecap="round"/>
  {glasses}{hat}
  <path d="M191 118 Q199 129 190 132" stroke="{c['skin_sh']}" stroke-width="2.8" fill="none" stroke-linecap="round"/>
  <path id="{p}-mouth" d="M170 141 Q181 150 191 139 Q181 145 170 141Z" fill="#8e3b3b" stroke="{o}" stroke-width="2"/>
  <path id="{p}-open" d="M172 139 Q181 156 190 139Z" fill="#5a1f1f" stroke="{o}" stroke-width="2" opacity="0"/>
 </g>"""
    torso = f"""<g id="{p}-torso">
  <path d="M110 198 C118 182 182 182 192 198 L198 302 C198 322 188 336 180 338 L120 338 C112 336 102 322 102 302Z" fill="{jk}" stroke="{o}" stroke-width="3"/>
  <path d="M110 198 C106 240 104 290 106 320 C112 330 118 336 124 338 L122 250Z" fill="{jk_sh}" opacity=".8"/>
  <path d="M180 200 C186 240 190 280 188 318" stroke="{jk_hi}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
  <path d="M136 188 L164 188 L150 238Z" fill="{c['shirt']}" stroke="{o}" stroke-width="2.5"/>{tie}
  <path d="M136 188 L150 238 L140 254 L126 200Z" fill="{jk_sh}" stroke="{o}" stroke-width="2.5"/>
  <path d="M164 188 L150 238 L160 254 L174 200Z" fill="{jk_hi}" stroke="{o}" stroke-width="2.5"/>{badge}
 </g>"""
    parts = [arm("back")]
    if mode == "full":
        parts += [leg("back"), leg("front")]
    parts += [f'<g id="{p}-upper">', torso, head, arm("front"), "</g>"]
    vb = "0 0 300 500" if mode == "full" else "0 0 300 360"
    h = c.get("height", 1.0)
    return (f'<svg id="{p}" class="char rig {cls}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" overflow="visible" '
            f'data-h="{h:.2f}">' + "".join(parts) + "</svg>")
