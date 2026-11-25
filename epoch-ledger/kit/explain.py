"""Explanatory finance charts that read at a glance, built from a kit.finstate.Ledger (never hand-typed numbers).

  cashflow_bars(uid, x, y, w, h, ledger, icons)   money OUT (stacked by category) vs money IN, with the monthly
                                                   shortfall bracket — ids: {uid}-seg{i}/-segl{i}, {uid}-in/-inl,
                                                   {uid}-gap/-gapl, {uid}-outl, {uid}-title
  runway_chart(uid, x, y, w, h, ledger, months, injections, labels)
                                                   cash balance over time: {uid}-line (first run-down), {uid}-zero,
                                                   {uid}-runway marker, and for injections {uid}-jump, {uid}-line2,
                                                   {uid}-next ("next round needed")
All text sits on the chart (no floating panels); every chart says "Illustrative" when the figures are.
"""
from __future__ import annotations

from .finstate import Ledger

INK = "#1b1410"
CAT_COLORS = ["#e07a5f", "#f2c66d", "#7fd8ff", "#c39bd3"]


def _panel(x, y, w, h, title, uid, note="Illustrative figures"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#fbf7ee" stroke="#c8bba0" stroke-width="3"/>'
            f'<text id="{uid}-title" x="{x + 34}" y="{y + 58}" font-family="Fraunces" font-weight="800" font-size="40" fill="#1f2a44">{title}</text>'
            f'<text x="{x + w - 30}" y="{y + h - 22}" text-anchor="end" font-family="Inter" font-weight="700" font-size="20" fill="#8a8070">{note}</text>')


def cashflow_bars(uid: str, x: float, y: float, w: float, h: float, led: Ledger, icons: dict | None = None, title: str = "One month at BigCart") -> str:
    base, top = y + h - 90, y + 110
    k = (base - top) / max(led.total_spending, led.total_income)
    bw = w * .2
    ox, ix = x + w * .2, x + w * .47
    out = [_panel(x, y, w, h, title, uid), f'<path d="M{x + 40} {base} H{x + w - 40}" stroke="{INK}" stroke-width="4"/>']
    yy = base
    for i, (lab, v) in enumerate(led.spending.items()):
        y0 = yy - v * k
        out.append(f'<rect id="{uid}-seg{i}" x="{ox}" y="{y0:.1f}" width="{bw:.1f}" height="{v * k:.1f}" fill="{CAT_COLORS[i % 4]}" stroke="{INK}" stroke-width="3"/>')
        icon = (icons or {}).get(lab, "")
        out.append(f'<g id="{uid}-segl{i}"><text x="{ox - 16}" y="{(y0 + yy) / 2 + 10:.0f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="26" fill="{INK}">{lab.title()}</text>'
                   f'<text x="{ox + bw / 2:.0f}" y="{(y0 + yy) / 2 + 11:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="28" fill="{INK}">{led.fmt(v)}</text>{icon}</g>')
        yy = y0
    out_top = yy
    out.append(f'<g id="{uid}-outl"><text x="{ox + bw / 2:.0f}" y="{base + 34}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="22" letter-spacing="2" fill="#b0402a">MONEY OUT</text>'
               f'<text x="{ox + bw / 2:.0f}" y="{base + 68}" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="32" fill="#b0402a">{led.fmt(led.total_spending)}</text></g>')
    iv = led.total_income
    out.append(f'<rect id="{uid}-in" x="{ix}" y="{base - iv * k:.1f}" width="{bw:.1f}" height="{iv * k:.1f}" fill="#5fb36a" stroke="{INK}" stroke-width="3"/>')
    out.append(f'<g id="{uid}-inl"><text x="{ix + bw / 2:.0f}" y="{base + 34}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="22" letter-spacing="2" fill="#2a6a2a">MONEY IN</text>'
               f'<text x="{ix + bw / 2:.0f}" y="{base + 68}" text-anchor="middle" font-family="Fraunces" font-weight="800" font-size="32" fill="#2a6a2a">{led.fmt(iv)}</text></g>')
    gx = ix + bw + 26
    in_top = base - iv * k
    out.append(f'<g id="{uid}-gap"><path d="M{ox + bw + 8} {out_top:.1f} H{ix + bw + 8}" stroke="{INK}" stroke-width="3" stroke-dasharray="10 8"/>'
               f'<path d="M{gx} {out_top + 4:.1f} V{in_top - 4:.1f}" stroke="#d9503f" stroke-width="6"/>'
               f'<path d="M{gx - 12} {out_top + 16:.1f} L{gx} {out_top + 2:.1f} L{gx + 12} {out_top + 16:.1f} M{gx - 12} {in_top - 16:.1f} L{gx} {in_top - 2:.1f} L{gx + 12} {in_top - 16:.1f}" stroke="#d9503f" stroke-width="5" fill="none"/></g>')
    out.append(f'<g id="{uid}-gapl"><text x="{gx + 22}" y="{(out_top + in_top) / 2 - 6:.0f}" font-family="Inter" font-weight="800" font-size="28" fill="#d9503f">SHORTFALL</text>'
               f'<text x="{gx + 22}" y="{(out_top + in_top) / 2 + 34:.0f}" font-family="Fraunces" font-weight="800" font-size="38" fill="#d9503f">{led.fmt(-led.monthly_burn)}</text>'
               f'<text x="{gx + 22}" y="{(out_top + in_top) / 2 + 64:.0f}" font-family="Inter" font-weight="700" font-size="22" fill="#d9503f">every month</text></g>')
    return "".join(out)


def runway_chart(uid: str, x: float, y: float, w: float, h: float, led: Ledger, months: int = 6, injections: dict | None = None,
                 labels: list[str] | None = None, title: str = "BigCart's cash", ymax: float | None = None, ticks: tuple | None = None) -> str:
    pts = led.curve(months, injections)
    vmax = ymax or max(v for _, v in pts) * 1.1
    gx0, gx1, gy0, gy1 = x + 90, x + w - 40, y + 100, y + h - 80
    X = lambda m: gx0 + (gx1 - gx0) * m / months
    Y = lambda v: gy1 - (gy1 - gy0) * v / vmax
    out = [_panel(x, y, w, h, title, uid),
           f'<path d="M{gx0} {gy0 - 10} V{gy1} H{gx1}" stroke="{INK}" stroke-width="3" fill="none"/>',
           f'<path id="{uid}-zero" d="M{gx0} {gy1} H{gx1}" stroke="#d9503f" stroke-width="4"/>']
    for m in range(months + 1):
        lab = (labels or [str(i) for i in range(months + 1)])[m]
        out.append(f'<text x="{X(m):.0f}" y="{gy1 + 34}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="22" fill="#5a5048">{lab}</text>')
    for v in (ticks or (vmax * .25, vmax * .5, vmax * .75)):
        out.append(f'<path d="M{gx0} {Y(v):.0f} H{gx1}" stroke="#d8cfbd" stroke-width="2"/><text x="{gx0 - 10}" y="{Y(v) + 7:.0f}" text-anchor="end" font-family="Inter" font-weight="700" font-size="20" fill="#8a8070">{led.fmt(round(v))}</text>')
    first_inj = min(injections) if injections else None
    seg1 = [(m, v) for m, v in pts if first_inj is None or m <= first_inj]
    if first_inj is not None:
        seg1 = seg1[:[i for i, (m, _) in enumerate(seg1) if m == first_inj][0] + 1]
    d1 = "M" + " L".join(f"{X(m):.1f} {Y(v):.1f}" for m, v in seg1)
    out.append(f'<path id="{uid}-line" d="{d1}" stroke="#1f3a7a" stroke-width="7" fill="none" stroke-linejoin="round"/>')
    # where the first run-down would hit zero without new money
    zero_m = led.runway_months
    if zero_m <= months:
        out.append(f'<g id="{uid}-runway"><path id="{uid}-proj" d="M{X(seg1[-1][0] if first_inj else 0):.1f} {Y(seg1[-1][1] if first_inj else led.balance):.1f} L{X(zero_m):.1f} {gy1}" '
                   f'stroke="#d9503f" stroke-width="5" stroke-dasharray="12 10" fill="none"/>'
                   f'<circle cx="{X(zero_m):.1f}" cy="{gy1}" r="10" fill="#d9503f"/>'
                   f'<text x="{X(zero_m):.1f}" y="{gy1 - 24}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="#d9503f">cash runs out</text></g>')
    if injections:
        m = first_inj
        before = [v for mm, v in pts if mm == m][0]
        after = [v for mm, v in pts if mm == m][-1]
        rest = [(mm, v) for mm, v in pts if mm >= m][1:]
        d2 = f"M{X(m):.1f} {Y(after):.1f} " + " ".join(f"L{X(mm):.1f} {Y(v):.1f}" for mm, v in rest)
        out.append(f'<g id="{uid}-jump"><path d="M{X(m):.1f} {Y(before):.1f} V{Y(after):.1f}" stroke="#2a8a3a" stroke-width="8"/>'
                   f'<path d="M{X(m) - 14:.1f} {Y(after) + 22:.1f} L{X(m):.1f} {Y(after) + 2:.1f} L{X(m) + 14:.1f} {Y(after) + 22:.1f}" stroke="#2a8a3a" stroke-width="6" fill="none"/>'
                   f'<text x="{X(m) + 18:.1f}" y="{Y(after) + 8:.1f}" font-family="Inter" font-weight="800" font-size="26" fill="#2a8a3a">{led.fmt(injections[m], signed=True)} from investors</text></g>')
        out.append(f'<path id="{uid}-line2" d="{d2}" stroke="#1f3a7a" stroke-width="7" fill="none" stroke-linejoin="round"/>')
        last_m, last_v = rest[-1] if rest else (m, after)
        out.append(f'<g id="{uid}-next"><circle cx="{X(last_m):.1f}" cy="{Y(last_v):.1f}" r="10" fill="#d9503f"/>'
                   f'<text x="{X(last_m) - 10:.1f}" y="{Y(last_v) - 26:.1f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="26" fill="#d9503f">next round needed</text></g>')
    return "".join(out)
