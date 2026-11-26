"""Fetch the CC0 PBR texture sets used by the opt-in cinematic set look (P3) from Poly Haven into .runtime/, and write a
licence manifest. Textures are not committed; this script plus the manifest make them reproducible.

    python3 epoch-ledger/charlab/assets/fetch_textures.py [--res 1k]

Licence: every Poly Haven asset is CC0 1.0 (public domain dedication), https://polyhaven.com/license
"""
import json
import os
import sys
import urllib.request

RES = sys.argv[sys.argv.index("--res") + 1] if "--res" in sys.argv else "1k"
OUT = ".runtime/charlab/textures"
# role -> Poly Haven asset id
SETS = {"desk_wood": "oak_veneer_01", "trim_wood": "dark_wood", "floor_wood": "oak_wood_planks", "wall_plaster": "grey_plaster_02",
        "leather": "brown_leather", "fabric": "rough_linen", "carpet": "dirty_carpet"}
MAPS = {"Diffuse": "diff", "Rough": "rough", "nor_gl": "nor"}
UA = {"User-Agent": "epoch-ledger-charlab/1.0"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()

manifest = {}
for role, aid in SETS.items():
    files = json.loads(get(f"https://api.polyhaven.com/files/{aid}")); info = json.loads(get(f"https://api.polyhaven.com/info/{aid}"))
    d = os.path.join(OUT, aid); os.makedirs(d, exist_ok=True); ent = {"asset": aid, "name": info.get("name"), "authors": list(info.get("authors", {})),
        "source": f"https://polyhaven.com/a/{aid}", "license": "CC0 1.0 Universal — https://polyhaven.com/license", "maps": {}}
    for key, short in MAPS.items():
        if key not in files: continue
        f = files[key][RES]["jpg"] if "jpg" in files[key][RES] else files[key][RES]["png"]
        ext = f["url"].rsplit(".", 1)[1]; p = os.path.join(d, f"{short}.{ext}")
        if not os.path.exists(p): open(p, "wb").write(get(f["url"]))
        ent["maps"][short] = {"url": f["url"], "local": p, "bytes": os.path.getsize(p)}
    manifest[role] = ent; print(role, aid, list(ent["maps"]))
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
json.dump(manifest, open(os.path.join(os.path.dirname(__file__), "textures_manifest.json"), "w"), indent=1)
