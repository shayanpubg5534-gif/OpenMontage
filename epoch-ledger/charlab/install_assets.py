#!/usr/bin/env python3
"""Install the MakeHuman system assets into the character lab's isolated MPFB user-data folder, reproducibly.

    python3 epoch-ledger/charlab/install_assets.py SOURCE [--dest DIR] [--check-only]

SOURCE is either the original ZIP (makehuman_system_assets_cc0.zip) or the first volume of a RAR split of it
(…part01.rar; all volumes in the same folder; needs `unar`, `apt-get install unar`). The script:
  1. extracts the ZIP from the RAR volumes if needed;
  2. verifies the ZIP's size and SHA-256 against the pinned values below (refuses anything else);
  3. checks every entry path is relative and stays inside the destination (no '..', no absolute paths);
  4. reads packs/makehuman_system_assets.json and requires every asset to be CC0 and all 94 expected assets present;
  5. extracts into DEST (default: the lab's MPFB user data: .runtime/charlab/user/extensions/.user/user_default/mpfb/data)
     and writes an install receipt (receipt_makehuman_system_assets.json) next to it.
Uses only the Python standard library (plus `unar` for RAR input). The assets never go into git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / ".runtime/charlab/user/extensions/.user/user_default/mpfb/data"
PACK = {
    "name": "makehuman_system_assets",
    "file": "makehuman_system_assets_cc0.zip",
    "bytes": 280_737_770,
    "sha256": "b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107",
    "official_page": "https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html",
    "mirrors": ["https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip",
                "https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip"],
    "licence": "CC0 1.0 (every asset, per packs/makehuman_system_assets.json and the official page)",
    "expected_counts": {"skins": 23, "clothes": 20, "eyebrows": 12, "eyes": 11, "hair": 10, "proxymeshes": 7, "teeth": 6,
                        "eyelashes": 4, "tongue": 1},
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def from_rar(first: Path, work: Path) -> Path:
    if not shutil.which("unar"):
        raise SystemExit("RAR input needs `unar` (apt-get install unar); 7-Zip in Debian/Ubuntu cannot decode RAR")
    subprocess.run(["unar", "-q", "-f", "-o", str(work), str(first)], check=True)
    zips = list(work.glob("*.zip"))
    if len(zips) != 1:
        raise SystemExit(f"expected one ZIP inside the RAR set, found {[z.name for z in zips]}")
    return zips[0]


def verify(zp: Path) -> dict:
    size, digest = zp.stat().st_size, sha256(zp)
    if size != PACK["bytes"] or digest != PACK["sha256"]:
        raise SystemExit(f"checksum mismatch: {size} bytes, sha256 {digest} (expected {PACK['bytes']}, {PACK['sha256']})")
    z = zipfile.ZipFile(zp)
    bad = [n for n in z.namelist() if n.startswith(("/", "\\")) or ".." in Path(n).parts or ":" in n]
    if bad:
        raise SystemExit(f"unsafe paths in archive: {bad[:5]}")
    if z.testzip() is not None:
        raise SystemExit("corrupt entry in archive")
    meta = json.loads(z.read("packs/makehuman_system_assets.json"))
    non_cc0 = {k: v.get("license") for k, v in meta.items() if v.get("license") != "CC0"}
    if non_cc0:
        raise SystemExit(f"assets that are not CC0: {non_cc0}")
    counts: dict = {}
    for v in meta.values():
        counts[v["type"]] = counts.get(v["type"], 0) + 1
    if counts != PACK["expected_counts"]:
        raise SystemExit(f"asset counts differ from the official list: {counts}")
    return {"bytes": size, "sha256": digest, "entries": len(z.namelist()), "assets": len(meta), "counts": counts}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as td:
        zp = from_rar(a.source, Path(td)) if a.source.suffix.lower() == ".rar" else a.source
        info = verify(zp)
        print(f"verified: {info['assets']} assets, all CC0, {info['entries']} entries, sha256 {info['sha256']}")
        if a.check_only:
            return 0
        a.dest.mkdir(parents=True, exist_ok=True)
        dest = a.dest.resolve()
        with zipfile.ZipFile(zp) as z:
            for n in z.namelist():
                target = (dest / n).resolve()
                if dest not in target.parents and target != dest:
                    raise SystemExit(f"refusing to write outside the destination: {n}")
            z.extractall(dest)
        receipt = dict(PACK, installed_to=str(dest), installed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), verified=info)
        (dest / "receipt_makehuman_system_assets.json").write_text(json.dumps(receipt, indent=2))
        print(f"installed to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
