"""Episode cast helpers built on the kit rig (modern characters)."""
from floor import place
from kit.rig import crowd_look, rig_svg


def modern(i, **o):
    c = crowd_look(i)
    c.update(dict(tie=None, badge=False), **o)
    return c


def modern_user(p, x=-90, y=300, w=640):
    """Seated user at a desk, bust, facing right toward a laptop."""
    c = modern(14, jacket="#3a5a6a", jacket_sh="#2a4250", jacket_hi="#5a7a8a", shirt="#e8e2d4")
    return place(rig_svg(p, c, "bust"), x, y, w).replace(f"height:{w * 500 / 300:.0f}px", f"height:{w * 360 / 300:.0f}px")
