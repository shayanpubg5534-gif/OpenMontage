#!/usr/bin/env python3
"""Scaffold a new Epoch Ledger episode: epoch-ledger/episodes/<slug>/ + projects/<slug>/hyperframes/.

  python epoch-ledger/scripts/new_episode.py "The Fall of Bretton Woods"
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
REPO = KIT.parent


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    title = sys.argv[1]
    slug = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    ep = KIT / "episodes" / slug
    if ep.exists():
        sys.exit(f"{ep} already exists")
    shutil.copytree(KIT / "templates" / "episode", ep)
    for f in ep.iterdir():
        if f.is_file():
            f.write_text(f.read_text().replace("__TITLE__", title).replace("__SLUG__", slug))
    (ep / "artifacts").mkdir()
    pilot = KIT / "episodes" / "how-banks-create-money"
    ws = REPO / "projects" / slug / "hyperframes"
    ws.mkdir(parents=True, exist_ok=True)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(pilot / f, ws / f)
    (ws / "meta.json").write_text(json.dumps({"id": slug, "name": title}, indent=2))
    subprocess.run(["bash", str(KIT / "scripts" / "vendor.sh"), str(ws)], check=True)
    sys.path.insert(0, str(REPO))
    from lib.checkpoint import init_project
    init_project(slug, title=title, pipeline_type="animation", series="The Epoch Ledger")
    print(f"episode source: {ep}\nworkspace:      {ws}\nnext: edit {ep / 'script.json'}, then run scripts/narrate.py")


if __name__ == "__main__":
    main()
