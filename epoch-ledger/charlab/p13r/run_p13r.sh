#!/usr/bin/env bash
# P13R pilot (78 s, the refined narration, paced for a first viewing), end to end and cold (experimental, opt-in;
# P12 and P13 untouched). Every step is timed into .runtime/charlab/p13r/perf.jsonl.
#   epoch-ledger/charlab/p13r/run_p13r.sh [OUT.mp4] [WORKERS]
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p13r; R=.runtime/charlab/p13r; OUT=${1:-projects/charlab_p13r/p13r_pilot.mp4}; W=${2:-4}
M="python3 epoch-ledger/charlab/p9/measure.py"; LOG=$R/perf.jsonl
rm -rf $R/plates $R/shots $R/cache projects/charlab_p13r/hf_final; rm -f $LOG $R/shot*.mp4; mkdir -p $R "$(dirname "$OUT")"
# 0 the gates: the treatment approved; the plan checked and resolved to the real word times; its pacing reviewed
$M treatment $LOG -- bash -c "cd epoch-ledger && ../.venv/bin/python -m kit.treatment charlab/p13r/treatment.json --gate motion"
$M plan $LOG -- python3 epoch-ledger/charlab/p11/visual_map.py check $H/map_p13r.json --resolved $R/map_resolved.json --table $H/map_table.md
(cd epoch-ledger && ../.venv/bin/python -m kit.pacing plan charlab/p13r/map_p13r.json --out ../$R/plan_pacing) || true   # diagnostics: findings stay visible
# 1 the kitchen world (P13's sets and plates, unchanged)
$M backdrop $LOG -- node epoch-ledger/charlab/p13/backdrop.mjs .runtime/charlab/p13/backdrop
$M sets $LOG -- python3 epoch-ledger/charlab/p13/sets.py
epoch-ledger/charlab/p13/plates.sh $R/plates $R/cache $LOG
# 2 2.5D shots (identities and the approved 2008 wardrobe change checked)
$M cast_shots $LOG -- python3 $H/shots.py .runtime/charlab/p8/src/open-peeps.fig $R/map_resolved.json $R/plates $R/shots
for k in K1 KT N1 N2 NT; do $M compose_$k $LOG -- node epoch-ledger/charlab/p10/render_shot.mjs $R/shots/shot$k.json $R/shot$k.mp4 --workers $W; done
# 3 the building (P13's scene and renderer)
for k in B1 B2; do $M building_$k $LOG -- python3 $H/render_building.py $R/map_resolved.json $R $W $k; done
# 4 HyperFrames at the approved 1080p30 settings
$M hf_build $LOG -- python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/p13r_pilot.py .runtime/charlab/out_p3 projects/charlab_p13r/hf_final
EPOCH_RENDER_TIMEOUT_PER_FRAME=3 $M hf_render $LOG -- python3 epoch-ledger/scripts/render.py render projects/charlab_p13r/hf_final --isolate --jobs $W -o "$OUT"
# 5 checks on the film: technical QC, sync of meaningful events, pacing (diagnostic)
node epoch-ledger/scripts/qc.mjs --video "$OUT"
python3 epoch-ledger/charlab/p11/visual_map.py inspect $H/map_p13r.json "$OUT" --out $R/sync_report.json | tail -1
(cd epoch-ledger && ../.venv/bin/python -m kit.pacing film charlab/p13r/map_p13r.json "../$OUT" --out ../$R/film_pacing) || true
python3 - "$LOG" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(json.dumps({"total_wall_s": round(sum(r["wall_s"] for r in rows), 1), "peak_rss_mb": max(r["peak_rss_mb"] for r in rows),
                  "steps": {r["label"]: r["wall_s"] for r in rows}}, indent=1))
PY
