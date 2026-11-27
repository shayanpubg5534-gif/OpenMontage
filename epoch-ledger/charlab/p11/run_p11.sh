#!/usr/bin/env bash
# P11 narration-driven re-direction of the P10 test, end to end and cold (experimental, opt-in; P10 and earlier untouched).
#   epoch-ledger/charlab/p11/run_p11.sh [OUT.mp4] [WORKERS]
# The narration is P10's, unchanged (a controlled comparison: same words, same timing). Every visual time comes from the
# narration-to-visual map (map_p11.json), resolved against the narration's word timestamps. Each step is timed into
# .runtime/charlab/p11/perf.jsonl; set stills are rendered fresh (no cache) so the numbers are a cold run.
set -euo pipefail
cd "$(dirname "$0")/../../.."
H=epoch-ledger/charlab/p11; R=.runtime/charlab/p11; P=$R/plates; S=$R/shots
OUT=${1:-projects/charlab_p11/p11_narrated_test.mp4}; W=${2:-4}
M="python3 epoch-ledger/charlab/p9/measure.py"; LOG=$R/perf.jsonl
rm -rf $P $S $R/cache_cold projects/charlab_p11/hf_final; rm -f $LOG; mkdir -p $P $S "$(dirname "$OUT")"
# 1 plan: check the narration-to-visual map and resolve every event to the narrator's real word times
$M plan $LOG -- python3 $H/visual_map.py check $H/map_p11.json --resolved $R/map_resolved.json --table $R/map_table.md
# 2 one still of the set per camera set-up (two-shot, banker close, baker close, desk from above) + depth + anchors + paint
for k in A B C D; do
  D=epoch-ledger/charlab/motion/demos/p10_cam$k.json; [ $k = D ] && D=epoch-ledger/charlab/motion/demos/p11_camD.json
  $M plate_$k $LOG -- node epoch-ledger/charlab/shot_render.mjs --demo $D --chars .runtime/charlab/out_p3 \
     --three .runtime/charlab/three/r0.186.1 --quality cin_balanced --cache $R/cache_cold --out $P/cam$k.mp4
  ffmpeg -loglevel error -y -i $P/cam$k.mp4 -frames:v 1 $P/cam${k}_raw.png
  $M track_$k $LOG -- node epoch-ledger/charlab/p9/cam_track.mjs $D epoch-ledger/charlab/p10/points.json $P/track$k
  ffmpeg -loglevel error -y -i $P/cam${k}_raw.png -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt)" $P/cam${k}_paint.png
done
# 3 cast and per-shot performance, keyed to the resolved events
$M prepare $LOG -- python3 $H/prepare.py .runtime/charlab/p8/src/open-peeps.fig $R/map_resolved.json $P $P $S
# 4 the 2.5D shots (P10 compositor, W workers each) and the 3D vault (camera keyed to the narration)
for k in S1 S2 S4 S5; do $M compose_$k $LOG -- node epoch-ledger/charlab/p10/render_shot.mjs $S/shot$k.json $R/shot$k.mp4 --workers $W; done
$M vault_3d $LOG -- $H/render_vault.sh $R/map_resolved.json $R/vault.mp4 2
# 5 HyperFrames: shots as video clips + the narration-synchronised graphics + gold captions + narration (render.py)
$M hf_build $LOG -- python3 epoch-ledger/charlab/hf_sequence.py epoch-ledger/charlab/sequences/p11_test.py .runtime/charlab/out_p3 projects/charlab_p11/hf_final
EPOCH_RENDER_TIMEOUT_PER_FRAME=3 $M hf_render $LOG -- python3 epoch-ledger/scripts/render.py render projects/charlab_p11/hf_final --isolate --jobs $W -o "$OUT"
# 6 checks: technical QC, then semantic sync (does each planned visual actually change on screen at its word?)
node epoch-ledger/scripts/qc.mjs --video "$OUT"
python3 $H/visual_map.py inspect $H/map_p11.json "$OUT" --out $R/sync_report.json | tail -1
python3 - "$LOG" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(json.dumps({"total_wall_s": round(sum(r["wall_s"] for r in rows), 1), "peak_rss_mb": max(r["peak_rss_mb"] for r in rows),
                  "steps": {r["label"]: r["wall_s"] for r in rows}}, indent=1))
PY
