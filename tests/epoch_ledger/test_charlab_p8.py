"""Character lab P8 (experimental): static checks (no rendering, no third-party files needed).

- the Figma decoder's path-command conversion and Kiwi float decoding are correct
- P8 tools compile; P8 demos are static stills with no actors (no speech); raw Fab files are never committed
"""
import json
import py_compile
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P8 = REPO / "epoch-ledger/charlab/p8"
sys.path.insert(0, str(P8))


def test_tools_compile():
    for f in ("figdecode.py", "peeps_extract.py", "peeps_compose.py", "compose_25d.py", "bm_pose.py", "make_sheets.py"):
        py_compile.compile(str(P8 / f), doraise=True)


def test_figma_path_commands():
    import figdecode as F
    blob = bytes([1]) + struct.pack("<2f", 0, 0) + bytes([2]) + struct.pack("<2f", 10, 0) + \
        bytes([4]) + struct.pack("<6f", 10, 5, 5, 10, 0, 10) + bytes([0])
    assert F.commands_to_svg(blob) == "M 0.00 0.00 L 10.00 0.00 C 10.00 5.00 5.00 10.00 0.00 10.00 Z"


def test_kiwi_float_roundtrip():
    import figdecode as F
    for v in (1.0, -2.5, 0.125, 1234.5):
        bits = struct.unpack("<I", struct.pack("<f", v))[0]
        enc = ((bits >> 23) | (bits << 9)) & 0xFFFFFFFF          # inverse of the decoder's rotation
        assert abs(F.R(struct.pack("<I", enc)).f() - v) < 1e-6
    assert F.R(b"\x00").f() == 0.0


def test_p8_demos_are_static_and_silent():
    for name in ("p8_bank_plate.json", "p8_bank_3d.json"):
        d = json.loads((REPO / "epoch-ledger/charlab/motion/demos" / name).read_text())
        assert d["actors"] == {} and d["look"] == "cinematic"
    d = json.loads((REPO / "epoch-ledger/charlab/motion/demos/p8_bank_3d.json").read_text())
    assert d["props"]["businessman"]["url"].startswith("/.runtime/")   # the Fab asset is referenced from .runtime only


def test_raw_fab_assets_not_tracked():
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout
    for ext in (".fbx", ".glb", ".blend", ".fig"):
        assert not any(l.endswith(ext) and "businessman" in l.lower() for l in out.splitlines())
