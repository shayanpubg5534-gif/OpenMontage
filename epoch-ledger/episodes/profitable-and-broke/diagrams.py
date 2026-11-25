"""Profitable and Broke — the explanatory diagrams. One visual language throughout: warm paper, ink outlines,
green = money in, red = money out, blue = the loan, gold = profit. Every number comes from LEDGER, and every
step lands on the word that names it (times are absolute seconds on the episode timeline).
"""
from __future__ import annotations

INK, GREEN, RED, BLUE, GOLD, TEAL, PAPER = "#1b1410", "#2f8a4a", "#c0442e", "#2d6fb3", "#d9a520", "#2f6f73", "#f7f1e4"
LEDGER = {"balance": 12000, "revenue": 40000, "flour": 18000, "wages": 12000, "costs": 30000, "profit": 10000,
          "loan": 18000, "short": -18000, "end": 22000, "days": 60}
F = "font-family"


def usd(v, sign=False):
    s = f"${abs(v):,.0f}"
    return ("−" if v < 0 else "+" if sign else "") + s


def text(x, y, s, size=40, w=800, fill=INK, anchor="start", fam="Inter", eid=None):
    i = f' id="{eid}"' if eid else ""
    return f'<text{i} x="{x}" y="{y}" {F}="{fam}" font-weight="{w}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def paper(title, sub=""):
    grid = "".join(f'<path d="M0 {y} H1920" stroke="#e8dcc4" stroke-width="2"/>' for y in range(60, 1080, 60))
    return (f'<rect width="1920" height="1080" fill="{PAPER}"/>{grid}'
            + text(110, 128, title, 60, 800, INK, fam="Fraunces") + (text(112, 180, sub, 32, 700, "#7a6a58") if sub else ""))


def order_card(cid="order", x=1200, y=250):
    """The supermarket's purchase order (S1 → S2): readable at 1080p (≥ 40 px body, 64 px figures)."""
    return (f'<g id="{cid}" transform="translate({x} {y})"><rect x="0" y="0" width="560" height="430" rx="18" fill="#fffdf6" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="0" y="0" width="560" height="84" rx="18" fill="{RED}"/><rect x="0" y="60" width="560" height="24" fill="{RED}"/>'
            + text(280, 58, "FRESHMART · PURCHASE ORDER", 32, 800, "#fffdf6", "middle")
            + text(40, 160, "12,000 loaves", 64, 800, INK, fam="Fraunces")
            + text(40, 212, "every month", 40, 700, "#5a4a3a")
            + f'<path d="M40 248 H520" stroke="#d8ccb4" stroke-width="3"/>'
            + text(40, 312, "Pays", 40, 700, "#5a4a3a") + text(520, 312, usd(LEDGER["revenue"]), 56, 800, GREEN, "end", fam="Fraunces")
            + text(40, 382, "Payment terms", 36, 700, "#5a4a3a") + text(520, 382, "60 days", 44, 800, RED, "end")
            + '</g>')


# ── S2: one month of the order (profit view) ───────────────────────────────────────────────────────────────────────
def profit_board(t):
    """t: dict of word times. Revenue bar, the two costs lift off it, the remainder turns into profit."""
    k = 14          # px per $1,000
    base, x0, w = 900, 330, 240
    rev, fl, wa, pr = LEDGER["revenue"] * k / 1000, LEDGER["flour"] * k / 1000, LEDGER["wages"] * k / 1000, LEDGER["profit"] * k / 1000
    top = base - rev
    svg = (paper("One month of the new order", "What Maya earns, and what it costs her")
           + f'<path d="M150 {base} H1780" stroke="{INK}" stroke-width="4"/>'
           # revenue column (three stacked parts that will separate)
           + f'<g id="pb-rev"><rect id="pb-r0" x="{x0}" y="{base - pr}" width="{w}" height="{pr}" fill="{GREEN}" stroke="{INK}" stroke-width="4"/>'
           f'<rect id="pb-r1" x="{x0}" y="{base - pr - wa}" width="{w}" height="{wa}" fill="{GREEN}" stroke="{INK}" stroke-width="4"/>'
           f'<rect id="pb-r2" x="{x0}" y="{top}" width="{w}" height="{fl}" fill="{GREEN}" stroke="{INK}" stroke-width="4"/></g>'
           + f'<g id="pb-revl">{text(x0 + w / 2, top - 70, "From the supermarket", 34, 700, "#5a4a3a", "middle")}'
           f'{text(x0 + w / 2, top - 20, usd(LEDGER["revenue"]), 60, 800, GREEN, "middle", fam="Fraunces", eid="pb-revv")}</g>'
           # cost labels and arrows (appear as the parts lift away)
           + f'<g id="pb-fll" opacity="0">{text(860 + w / 2, base - fl - 70, "Flour", 40, 800, RED, "middle")}{text(860 + w / 2, base - fl - 20, "−" + usd(LEDGER["flour"]), 52, 800, RED, "middle", fam="Fraunces")}</g>'
           + f'<g id="pb-wal" opacity="0">{text(1190 + w / 2, base - wa - 70, "Wages", 40, 800, RED, "middle")}{text(1190 + w / 2, base - wa - 20, "−" + usd(LEDGER["wages"]), 52, 800, RED, "middle", fam="Fraunces")}</g>'
           + f'<path id="pb-a1" d="M{x0 + w + 10} {top + 40} C 700 {top - 60}, 800 {top - 40}, 880 {base - fl - 120}" fill="none" stroke="{RED}" stroke-width="6" marker-end="url(#pb-ah)"/>'
           + f'<path id="pb-a2" d="M{x0 + w + 10} {top + fl + 40} C 800 {top + 40}, 1100 {top}, 1210 {base - wa - 120}" fill="none" stroke="{RED}" stroke-width="6" marker-end="url(#pb-ah)"/>'
           + f'<defs><marker id="pb-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{RED}"/></marker></defs>'
           + f'<g id="pb-cost" opacity="0"><path d="M860 {base - fl - 140} V{base - fl - 165} H{1190 + w} V{base - wa - 140}" fill="none" stroke="{INK}" stroke-width="4"/>'
           f'{text((860 + 1190 + w) / 2, base - fl - 185, "Costs " + usd(LEDGER["costs"]), 48, 800, INK, "middle")}</g>'
           + f'<g id="pb-prl" opacity="0">'
           f'{text(x0 + w + 30, base - pr / 2 - 8, "Profit", 40, 800, "#8a6a10")}{text(x0 + w + 30, base - pr / 2 + 46, usd(LEDGER["profit"]), 56, 800, "#8a6a10", fam="Fraunces")}</g>'
           + text(1780, 1000, "Illustrative figures", 24, 700, "#9a8a74", "end"))
    rv, fl_t, wa_t, c_t, p_t, pf_t = t["40,000"], t["Flour"], t["wages"], t["30,000"], t["10,000"], t["profit"]
    js = f"""
gsap.set(['#pb-r0', '#pb-r1', '#pb-r2'], {{ scaleY: 0, transformOrigin: '50% 100%' }});
gsap.set('#pb-revl', {{ opacity: 0 }}); gsap.set(['#pb-a1', '#pb-a2'], {{ opacity: 0 }});
tl.to(['#pb-r0', '#pb-r1', '#pb-r2'], {{ scaleY: 1, duration: .5, ease: 'power2.out', stagger: .12 }}, {rv - .55:.2f});
tl.to('#pb-revl', {{ opacity: 1, duration: .3 }}, {rv - .1:.2f});
{{ const o = {{ v: 0 }}; tl.to(o, {{ v: {LEDGER['revenue']}, duration: .7, ease: 'power2.out', onUpdate: () => document.querySelector('#pb-revv').textContent = '$' + Math.round(o.v).toLocaleString('en-US') }}, {rv - .55:.2f}); }}
// flour lifts off the top of the revenue column and lands in its own column
tl.to('#pb-a1', {{ opacity: 1, duration: .2 }}, {fl_t - .15:.2f});
tl.to('#pb-r2', {{ x: {860 - x0}, y: {LEDGER['revenue'] * k / 1000 - LEDGER['flour'] * k / 1000}, fill: '{RED}', duration: .7, ease: 'power2.inOut' }}, {fl_t - .1:.2f});
tl.to('#pb-fll', {{ opacity: 1, duration: .3 }}, {fl_t + .45:.2f});
tl.to('#pb-a2', {{ opacity: 1, duration: .2 }}, {wa_t - .15:.2f});
tl.to('#pb-r1', {{ x: {1190 - x0}, fill: '{RED}', duration: .7, ease: 'power2.inOut' }}, {wa_t - .1:.2f});
tl.to('#pb-wal', {{ opacity: 1, duration: .3 }}, {wa_t + .45:.2f});
tl.to('#pb-cost', {{ opacity: 1, duration: .35 }}, {c_t - .05:.2f});
tl.to(['#pb-a1', '#pb-a2'], {{ opacity: .25, duration: .4 }}, {c_t + .5:.2f});
// what is left is the profit
tl.to('#pb-revl', {{ opacity: .35, duration: .4 }}, {p_t - .4:.2f});
tl.to('#pb-r0', {{ fill: '{GOLD}', duration: .45 }}, {p_t - .15:.2f});
tl.to('#pb-prl', {{ opacity: 1, duration: .35 }}, {p_t:.2f});
tl.fromTo('#pb-r0', {{ scaleX: 1 }}, {{ scaleX: 1.06, transformOrigin: '50% 100%', duration: .18, yoyo: true, repeat: 1, ease: 'sine.inOut', immediateRender: false }}, {pf_t:.2f});
"""
    return svg, js


# ── S3: when the money moves (timeline) ────────────────────────────────────────────────────────────────────────────
def timeline_board(t):
    ax_y, x0, x1 = 520, 230, 1690
    dx = (x1 - x0) / 60
    ticks = "".join(f'<path d="M{x0 + d * dx} {ax_y - 12} V{ax_y + 12}" stroke="{INK}" stroke-width="4"/>'
                    + text(x0 + d * dx, ax_y + 56, f"Day {d}", 30, 700, "#5a4a3a", "middle") for d in range(0, 61, 10))
    svg = (paper("When the money moves", "The costs come first. The payment comes later.")
           + f'<path d="M{x0 - 40} {ax_y} H{x1 + 60}" stroke="{INK}" stroke-width="5"/>' + ticks
           + f'<g id="tb-now">{f"<rect x={chr(34)}{x0 - 70}{chr(34)} y={chr(34)}{ax_y - 150}{chr(34)} width={chr(34)}140{chr(34)} height={chr(34)}56{chr(34)} rx={chr(34)}10{chr(34)} fill={chr(34)}{INK}{chr(34)}/>"}'
           f'{text(x0, ax_y - 110, "TODAY", 34, 800, "#fffdf6", "middle")}<path d="M{x0} {ax_y - 94} V{ax_y - 14}" stroke="{INK}" stroke-width="4"/></g>'
           # money out, now
           + f'<g id="tb-out1" opacity="0"><path d="M{x0 - 30} {ax_y + 90} V{ax_y + 300}" stroke="{RED}" stroke-width="16" marker-end="url(#tb-ahr)"/>'
           f'{text(x0 + 10, ax_y + 210, "Flour", 40, 800, RED)}{text(x0 + 10, ax_y + 264, "−" + usd(LEDGER["flour"]), 50, 800, RED, fam="Fraunces")}</g>'
           + f'<g id="tb-out2" opacity="0"><path d="M{x0 + 260} {ax_y + 90} V{ax_y + 260}" stroke="{RED}" stroke-width="16" marker-end="url(#tb-ahr)"/>'
           f'{text(x0 + 300, ax_y + 190, "Wages", 40, 800, RED)}{text(x0 + 300, ax_y + 244, "−" + usd(LEDGER["wages"]), 50, 800, RED, fam="Fraunces")}</g>'
           + f'<g id="tb-due" opacity="0"><rect x="{x0 - 60}" y="{ax_y + 330}" width="620" height="70" rx="35" fill="{RED}"/>'
           f'{text(x0 + 250, ax_y + 378, "Due now", 40, 800, "#fffdf6", "middle")}</g>'
           # the wait, and the payment
           + f'<rect id="tb-wait" x="{x0}" y="{ax_y - 40}" width="{x1 - x0}" height="80" fill="{GOLD}" opacity="0"/>'
           + f'<g id="tb-cal" transform="translate({x0} {ax_y - 130})"><rect x="-70" y="-44" width="140" height="88" rx="12" fill="#fffdf6" stroke="{INK}" stroke-width="4"/>'
           f'<rect x="-70" y="-44" width="140" height="26" rx="10" fill="{TEAL}"/>{text(0, 30, "Day 0", 34, 800, INK, "middle", eid="tb-day")}</g>'
           + f'<g id="tb-in" opacity="0"><path d="M{x1} {ax_y + 300} V{ax_y + 70}" stroke="{GREEN}" stroke-width="16" marker-end="url(#tb-ahg)"/>'
           f'{text(x1 - 30, ax_y + 210, "Supermarket pays", 40, 800, GREEN, "end")}{text(x1 - 30, ax_y + 264, usd(LEDGER["revenue"], True), 50, 800, GREEN, "end", fam="Fraunces")}</g>'
           + f'<defs><marker id="tb-ahr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="2.6" markerHeight="2.6" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{RED}"/></marker>'
           f'<marker id="tb-ahg" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="2.6" markerHeight="2.6" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{GREEN}"/></marker></defs>'
           + text(1780, 1000, "Illustrative figures", 24, 700, "#9a8a74", "end"))
    f1, wg, due, sp, d60 = t["flour2"], t["wages2"], t["due"], t["pays"], t["days"]
    js = f"""
tl.fromTo('#tb-out1', {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power2.out', immediateRender: false }}, {f1 - .05:.2f});
tl.fromTo('#tb-out2', {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power2.out', immediateRender: false }}, {wg - .05:.2f});
tl.fromTo('#tb-due', {{ opacity: 0, scale: .8 }}, {{ opacity: 1, scale: 1, transformOrigin: '50% 50%', duration: .3, ease: 'back.out(2)', immediateRender: false }}, {due - .05:.2f});
// sixty days pass: the calendar chip travels along the axis, the wait shades in
tl.to('#tb-cal', {{ x: {x1 - x0}, duration: {d60 - sp + .15:.2f}, ease: 'power1.inOut' }}, {sp:.2f});
tl.fromTo('#tb-wait', {{ opacity: 0, scaleX: 0 }}, {{ opacity: .25, scaleX: 1, transformOrigin: '0% 50%', duration: {d60 - sp + .15:.2f}, ease: 'power1.inOut', immediateRender: false }}, {sp:.2f});
{{ const o = {{ d: 0 }}; tl.to(o, {{ d: 60, duration: {d60 - sp + .15:.2f}, ease: 'power1.inOut', onUpdate: () => document.querySelector('#tb-day').textContent = 'Day ' + Math.round(o.d) }}, {sp:.2f}); }}
tl.fromTo('#tb-in', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power2.out', immediateRender: false }}, {d60 + .2:.2f});
"""
    return svg, js


# ── S4b / S5b: the cash balance on Maya's tablet ───────────────────────────────────────────────────────────────────
def cash_chart(uid, phase, t):
    """phase 'gap' (S4b): $12,000 → pays the bills → −$18,000.  phase 'loan' (S5b): the loan fills the gap, the
    supermarket pays on day 60, the loan is repaid → $22,000."""
    X0, X1, Y0 = 300, 1700, 640                  # chart area; Y0 = the $0 line
    ky = 9                                         # px per $1,000
    dx = (X1 - X0) / 60
    Y = lambda v: Y0 - v * ky / 1000
    grid = "".join(f'<path d="M{X0} {Y(v)} H{X1}" stroke="#e0d4bc" stroke-width="2"/>'
                   + text(X0 - 20, Y(v) + 10, usd(v) if v else "$0", 28, 700, "#7a6a58", "end") for v in range(-20000, 40001, 10000))
    days = "".join(text(X0 + d * dx, Y(-20000) + 50, f"Day {d}", 26, 700, "#7a6a58", "middle") for d in range(0, 61, 10))
    svg = (f'<rect width="1920" height="1080" fill="#1b1d22"/><rect x="40" y="30" width="1840" height="1020" rx="30" fill="{PAPER}"/>'
           + f'<rect x="40" y="30" width="1840" height="96" rx="30" fill="#1f3550"/><rect x="40" y="96" width="1840" height="30" fill="#1f3550"/>'
           + text(100, 96, "Harbor Community Bank", 38, 800, "#f2f2ee", fam="Fraunces") + text(1820, 96, "Maya's Bakery · business account", 32, 700, "#9fc0e0", "end")
           + text(110, 200, "Cash balance", 52, 800, INK, fam="Fraunces")
           + grid + f'<path d="M{X0} {Y0} H{X1}" stroke="{INK}" stroke-width="4"/>' + days
           + f'<path id="{uid}-redzone" d="M{X0} {Y0} H{X1} V{Y(LEDGER["short"])} H{X0}Z" fill="{RED}" opacity="0"/>'
           + f'<path id="{uid}-line" d="" fill="none" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
           + f'<rect id="{uid}-loan" x="{X0}" y="{Y0}" width="{X1 - X0}" height="{LEDGER["loan"] * ky / 1000}" fill="{BLUE}" opacity="0"/>'
           + f'<g id="{uid}-bal">{text(X0 + 40, Y(LEDGER["balance"]) - 30, "In the bank " + usd(LEDGER["balance"]), 44, 800, GREEN)}</g>'
           + f'<g id="{uid}-pay" opacity="0"><path d="M{X0 + 30} {Y(12000) + 20} V{Y(-18000) - 30}" stroke="{RED}" stroke-width="12" marker-end="url(#{uid}-ah)"/>'
           f'{text(X0 + 64, Y(5500), "Bills paid " + "−" + usd(LEDGER["costs"]), 40, 800, RED)}</g>'
           + f'<g id="{uid}-short" opacity="0"><rect x="{X0 + 440}" y="{Y(-18000) - 86}" width="560" height="76" rx="38" fill="{RED}"/>'
           f'{text(X0 + 720, Y(-18000) - 34, "18,000 short", 46, 800, "#fffdf6", "middle")}</g>'
           + f'<g id="{uid}-loanl" opacity="0">{text(X0 + 720, Y(-9000) + 16, "Loan " + usd(LEDGER["loan"], True), 46, 800, "#fffdf6", "middle")}</g>'
           + f'<g id="{uid}-cur" opacity="0"><path d="M{X0} {Y(40000)} V{Y(-20000)}" stroke="{TEAL}" stroke-width="4" stroke-dasharray="10 8"/>'
           f'<rect x="{X0 - 70}" y="{Y(40000) - 60}" width="140" height="52" rx="10" fill="{TEAL}"/>{text(X0, Y(40000) - 21, "Day 0", 32, 800, "#fffdf6", "middle", eid=uid + "-curd")}</g>'
           + f'<g id="{uid}-in" opacity="0"><path d="M{X1 - 40} {Y(0) - 10} V{Y(40000) + 40}" stroke="{GREEN}" stroke-width="12" marker-end="url(#{uid}-ahg)"/>'
           f'{text(X1 - 70, Y(36000), "Supermarket pays " + usd(LEDGER["revenue"], True), 38, 800, GREEN, "end")}</g>'
           + f'<g id="{uid}-rep" opacity="0">{text(X1 - 70, Y(30000) + 30, "Loan repaid " + "−" + usd(LEDGER["loan"]), 38, 800, BLUE, "end")}</g>'
           + f'<g id="{uid}-end" opacity="0"><rect x="{X1 - 520}" y="{Y(22000) - 6}" width="500" height="76" rx="38" fill="{GREEN}"/>'
           f'{text(X1 - 270, Y(22000) + 46, "Day 60: " + usd(LEDGER["end"]), 44, 800, "#fffdf6", "middle")}</g>'
           + f'<defs><marker id="{uid}-ah" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="2.6" markerHeight="2.6" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{RED}"/></marker>'
           f'<marker id="{uid}-ahg" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="2.6" markerHeight="2.6" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{GREEN}"/></marker></defs>'
           + text(1830, 1030, "Illustrative figures", 24, 700, "#9a8a74", "end"))
    # the balance line is a function of three animated amounts: paid (0..30k at day 0), loan (0..18k at day 0),
    # reached (day the cursor has reached), in (0..40k at day 60), repaid (0..18k at day 60)
    js = f"""
{{ const S = {{ paid: {0 if phase == 'gap' else LEDGER['costs']}, loan: 0, reach: {4 if phase == 'gap' else 60}, inn: 0, rep: 0 }};
  const X = d => {X0} + d * {dx:.4f}, Yv = v => {Y0} - v * {ky / 1000};
  const draw = () => {{ const b0 = {LEDGER['balance']} - S.paid + S.loan, end = b0 + S.inn - S.rep;
    let d = `M${{X(0)}} ${{Yv({LEDGER['balance']})}} L${{X(0)}} ${{Yv(b0)}} L${{X(S.reach)}} ${{Yv(b0)}}`;
    if (S.reach >= 60) d += ` L${{X(60)}} ${{Yv(b0 + S.inn)}} L${{X(60)}} ${{Yv(end)}}`;
    document.getElementById('{uid}-line').setAttribute('d', d);
    document.getElementById('{uid}-line').setAttribute('stroke', b0 + (S.reach >= 60 ? S.inn - S.rep : 0) < 0 ? '{RED}' : '{INK}'); }};
  const drv = (props, at, dur, ease) => tl.to(S, Object.assign({{}}, props, {{ duration: dur, ease: ease || 'power2.inOut', onUpdate: draw }}), at);
  tl.fromTo('#{uid}-line', {{ opacity: 1 }}, {{ opacity: 1, duration: .01, onUpdate: draw, immediateRender: false }}, {t['start']:.2f});
  draw();
"""
    if phase == "gap":
        pay, short = t["pays"], t["18,000"]
        js += f"""
  tl.fromTo('#{uid}-pay', {{ opacity: 0 }}, {{ opacity: 1, duration: .25, immediateRender: false }}, {pay - .1:.2f});
  drv({{ paid: {LEDGER['costs']} }}, {pay:.2f}, .8, 'power2.in');
  tl.to('#{uid}-bal', {{ opacity: .3, duration: .3 }}, {pay + .2:.2f});
  tl.to('#{uid}-redzone', {{ opacity: .18, duration: .4 }}, {pay + .7:.2f});
  drv({{ reach: 60 }}, {pay + .9:.2f}, 1.0, 'power1.inOut');
  tl.fromTo('#{uid}-short', {{ opacity: 0, scale: .8 }}, {{ opacity: 1, scale: 1, transformOrigin: '50% 50%', duration: .3, ease: 'back.out(2)', immediateRender: false }}, {short - .05:.2f});
}}"""
    else:
        ln, rp, sp = t["loan_fill"], t["repaid"], t["pays2"]
        js += f"""
  tl.set('#{uid}-redzone', {{ opacity: .18 }}, {t['start']:.2f}); tl.set('#{uid}-short', {{ opacity: 1 }}, {t['start']:.2f}); tl.set('#{uid}-bal', {{ opacity: .3 }}, {t['start']:.2f});
  // the loan fills exactly the gap
  tl.fromTo('#{uid}-loan', {{ opacity: 0, scaleY: 0 }}, {{ opacity: .85, scaleY: 1, transformOrigin: '50% 0%', duration: .5, ease: 'power2.out', immediateRender: false }}, {ln:.2f});
  drv({{ loan: {LEDGER['loan']} }}, {ln:.2f}, .5);
  tl.to(['#{uid}-redzone', '#{uid}-short'], {{ opacity: 0, duration: .35 }}, {ln + .2:.2f});
  tl.fromTo('#{uid}-loanl', {{ opacity: 0 }}, {{ opacity: 1, duration: .3, immediateRender: false }}, {ln + .3:.2f});
  // the days pass; on day 60 the supermarket pays and the loan is repaid the same day
  tl.fromTo('#{uid}-cur', {{ opacity: 0, x: 0 }}, {{ opacity: 1, x: 0, duration: .2, immediateRender: false }}, {rp:.2f});
  tl.to('#{uid}-cur', {{ x: {X1 - X0}, duration: {sp - rp - .2:.2f}, ease: 'power1.inOut' }}, {rp + .2:.2f});
  {{ const o = {{ d: 0 }}; tl.to(o, {{ d: 60, duration: {sp - rp - .2:.2f}, ease: 'power1.inOut', onUpdate: () => document.querySelector('#{uid}-curd').textContent = 'Day ' + Math.round(o.d) }}, {rp + .2:.2f}); }}
  tl.to(['#{uid}-loan', '#{uid}-loanl'], {{ opacity: .35, duration: .4 }}, {sp - .2:.2f});
  tl.fromTo('#{uid}-in', {{ opacity: 0 }}, {{ opacity: 1, duration: .3, immediateRender: false }}, {sp:.2f});
  drv({{ inn: {LEDGER['revenue']} }}, {sp:.2f}, .45);
  tl.fromTo('#{uid}-rep', {{ opacity: 0 }}, {{ opacity: 1, duration: .3, immediateRender: false }}, {sp + .45:.2f});
  drv({{ rep: {LEDGER['loan']} }}, {sp + .45:.2f}, .45);
  tl.fromTo('#{uid}-end', {{ opacity: 0, scale: .85 }}, {{ opacity: 1, scale: 1, transformOrigin: '50% 50%', duration: .3, ease: 'back.out(2)', immediateRender: false }}, {sp + .9:.2f});
}}"""
    return svg, js
