"""Processor cutaway (c04_07): how one accelerator performs enormous numbers of calculations.

Scene brief: Message — specialised processors do huge numbers of calculations. Understanding — the
chip moves data from memory into a large grid of small compute units that all work at the same time;
results stream out. Actions: data blocks leave the memory stacks along bus traces ("perform"); a wave
of multiply-and-add operations ripples across the grid as values pass between neighbours; one unit
is magnified to show the operation itself; the view pulls back to show the grid repeated across the
whole die ("enormous numbers"); finished results flow out to the output buffer ("calculations").
No performance figures are shown (none invented).
"""

N = 8          # units per side in the magnified block
CELL = 74      # px


def grid_block(px, x0, y0):
    cells = []
    for r in range(N):
        for c in range(N):
            x, y = x0 + c * CELL, y0 + r * CELL
            cells.append(f'<g class="{px}-cell" data-r="{r}" data-c="{c}"><rect x="{x}" y="{y}" width="{CELL - 10}" height="{CELL - 10}" rx="8" '
                         f'fill="#0f2238" stroke="#2f6a8a" stroke-width="2.5"/>'
                         f'<text x="{x + (CELL - 10) / 2}" y="{y + (CELL - 10) / 2 + 9}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="24" fill="#5fb6d6">×+</text></g>')
    return "".join(cells)


def die_svg(px):
    import random
    rnd = random.Random(7)
    traces = "".join(
        f'<path d="M{x} {y} h{rnd.choice([60, 120, 180])} v{rnd.choice([-40, 40, 80])} h{rnd.choice([60, 120])}" stroke="#1d3a52" stroke-width="3" fill="none"/>'
        for x, y in ((rnd.randrange(-100, 1900), rnd.randrange(0, 1080)) for _ in range(160)))
    vias = "".join(f'<circle cx="{rnd.randrange(0, 1920)}" cy="{rnd.randrange(0, 1080)}" r="4" fill="#2a5a7a"/>' for _ in range(220))
    gx, gy = 560, 150
    mem = "".join(f'<g transform="translate(90 {150 + k * 200})"><rect width="230" height="160" rx="10" fill="#1a2230" stroke="#6a7a90" stroke-width="3"/>'
                  + "".join(f'<rect x="12" y="{14 + j * 18}" width="206" height="12" rx="3" fill="#2a3446"/>' for j in range(8))
                  + '</g>' for k in range(4))
    buses = "".join(f'<path id="{px}-bus{r}" d="M320 {230 + (r // 2) * 200 + (r % 2) * 60} C420 {230 + (r // 2) * 200 + (r % 2) * 60} 460 {gy + 32 + r * CELL} {gx - 8} {gy + 32 + r * CELL}" '
                    f'stroke="#2f6a8a" stroke-width="6" fill="none"/>' for r in range(N))
    outs = "".join(f'<path id="{px}-out{r}" d="M{gx + N * CELL} {gy + 32 + r * CELL} C{gx + N * CELL + 120} {gy + 32 + r * CELL} 1380 {560} 1560 {560}" '
                   f'stroke="#2f6a8a" stroke-width="6" fill="none"/>' for r in range(N))
    return f"""<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
 <rect x="-400" y="-300" width="2720" height="1680" fill="#07111c"/>{traces}{vias}
 {mem}<text x="205" y="132" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#cfe6f5">Memory</text>
 {buses}{outs}
 <rect x="{gx - 26}" y="{gy - 26}" width="{N * CELL + 42}" height="{N * CELL + 42}" rx="16" fill="none" stroke="#38d6ff" stroke-width="4"/>
 <g id="{px}-grid">{grid_block(px, gx, gy)}</g>
 <g transform="translate(1560 470)"><rect width="250" height="180" rx="12" fill="#1a2230" stroke="#6a7a90" stroke-width="3"/>
  {''.join(f'<rect id="{px}-res{j}" x="16" y="{16 + j * 19}" width="218" height="13" rx="3" fill="#2a3446"/>' for j in range(8))}</g>
 <text x="1685" y="452" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#cfe6f5">Results</text>
</svg>"""


def tiles_svg(px):
    """The pulled-back die: the magnified block is one of many identical blocks."""
    blocks = []
    for r in range(6):
        for c in range(10):
            x, y = 60 + c * 182, 40 + r * 170
            inner = "".join(f'<rect class="{px}-mini" x="{x + 8 + (k % 8) * 20}" y="{y + 8 + (k // 8) * 19}" width="15" height="14" rx="2" fill="#0f2238"/>' for k in range(64))
            blocks.append(f'<rect x="{x}" y="{y}" width="172" height="160" rx="8" fill="#0a1a2a" stroke="#2f6a8a" stroke-width="2"/>{inner}')
    return f'<svg viewBox="0 0 1920 1080" class="full" xmlns="http://www.w3.org/2000/svg"><rect width="1920" height="1080" fill="#07111c"/>{"".join(blocks)}</svg>'
