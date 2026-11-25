"""Cached background plates: render a static set once (scene3d + lightfx page) to a high-density PNG and reuse it.

Animated parts (characters, props, money flows) then run live over the plate, so a shot's per-frame cost is the
foreground only, and an unchanged set is never re-drawn. Plates are keyed by a hash of the page HTML (and the
assets it references), so editing the set re-renders only that plate.

    from kit.plates import plate
    png = plate(ws / "plates", "office_tank", html)          # -> Path to <name>-<hash>.png (2x density)
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

STILL = Path(__file__).resolve().parents[1] / "scripts" / "still.mjs"


def plate(out_dir: Path, name: str, html: str, scale: int = 2, assets: tuple[Path, ...] = (), wait_ms: int = 1500) -> Path:
    """Render `html` (a full page that draws a 1920x1080 frame) to out_dir/<name>-<hash>.png at `scale` density.
    The page is written next to the plate so relative asset paths (tex/, fonts/, scene3d.js) resolve there."""
    out_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(html.encode())
    for a in assets:
        h.update(Path(a).read_bytes())
    key = h.hexdigest()[:12]
    png = out_dir / f"{name}-{key}.png"
    if png.exists():
        return png
    for old in out_dir.glob(f"{name}-*.png"):
        old.unlink()
    page = out_dir / f"{name}.html"
    page.write_text(html)
    subprocess.run(["node", str(STILL), str(page), str(png), "--scale", str(scale), "--wait", str(wait_ms)], check=True, capture_output=True)
    return png
