#!/usr/bin/env bash
# P13 pilot (30 s, the P12 narration re-directed by the approved P13 treatment), end to end and cold (experimental,
# opt-in; P12 and earlier untouched, the P12 narration is read only). Every step is timed into
# .runtime/charlab/p13/pilot/perf.jsonl; caches are cleared first.
#   epoch-ledger/charlab/p13/run_p13.sh [OUT.mp4] [WORKERS]
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p13; R=.runtime/charlab/p13/pilot; OUT=${1:-projects/charlab_p13/p13_pilot.mp4}; W=${2:-4}
M="python3 epoch-ledger/charlab/p9/measure.py"; LOG=$R/perf.jsonl
rm -rf $R/plates $R/shots $R/cache projects/charlab_p13/hf; rm -f $LOG $R/shot*.mp4; mkdir -p $R "$(dirname "$OUT")"
# 0 the gate: the treatment must be approved before any animation
$M treatment $LOG -- bash -c "cd epoch-ledger && ../.venv/bin/python -m kit.treatment charlab/p13/treatment.json --gate motion"
# 1 plan: the narration-to-visual map, checked and resolved to the real word times (P11 method)
$M plan $LOG -- python3 epoch-ledger/charlab/p11/visual_map.py check $H/map_p13.json --resolved $R/map_resolved.json --table $R/map_table.md
# 2 the kitchen world: window views, newspaper texture, sets, four plates (+ depth + paint)
$M backdrop $LOG -- node $H/backdrop.mjs .runtime/charlab/p13/backdrop
$M sets $LOG -- python3 $H/sets.py
$H/plates.sh $R/plates $R/cache $LOG
# 3 2.5D shots: cast identities (and the approved 2008 wardrobe change) checked, acted from the word times
$M cast_shots $LOG -- python3 $H/shots.py .runtime/charlab/p8/src/open-peeps.fig $R/map_resolved.json $R/plates $R/shots
for k in K1 KT N1 N2 NT; do $M compose_$k $LOG -- node epoch-ledger/charlab/p10/render_shot.mjs $R/shots/shot$k.json $R/shot$k.mp4 --workers $W; done
# 4 the selective 3D: the security building (issuance, payments, losses)
for k in B1 B2 B3; do $M building_$k $LOG -- python3 $H/render_building.py $R/map_resolved.json $R $W $k; done
# 5 HyperFrames: video shots + formats + gold captions + the P12 narration; approved 1080p30 settings
$M hf_build $LOG -- python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/p13_pilot.py .runtime/charlab/out_p3 projects/charlab_p13/hf
EPOCH_RENDER_TIMEOUT_PER_FRAME=3 $M hf_render $LOG -- python3 epoch-ledger/scripts/render.py render projects/charlab_p13/hf --isolate --jobs $W -o "$OUT"
# 6 checks on the rendered film: technical QC and semantic sync
node epoch-ledger/scripts/qc.mjs --video "$OUT"
python3 epoch-ledger/charlab/p11/visual_map.py inspect $H/map_p13.json "$OUT" --out $R/sync_report.json | tail -1
python3 - "$LOG" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(json.dumps({"total_wall_s": round(sum(r["wall_s"] for r in rows), 1), "peak_rss_mb": max(r["peak_rss_mb"] for r in rows),
                  "steps": {r["label"]: r["wall_s"] for r in rows}}, indent=1))
PY
