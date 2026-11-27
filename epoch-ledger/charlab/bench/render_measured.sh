#!/usr/bin/env bash
# Render a HyperFrames workspace through the production render.py (read-only use) and record wall time and memory:
# system memory in use (free -m) and the summed RSS of the render's process tree (chromium + ffmpeg), every 2 s.
#   epoch-ledger/charlab/bench/render_measured.sh WS OUT.mp4 LOGDIR TAG
set -u
WS=$1; OUT=$2; LOG=$3; TAG=$4; mkdir -p "$LOG"
cd "$(dirname "$0")/../../.."
t0=$(date +%s.%N)
EPOCH_RENDER_TIMEOUT_PER_FRAME=${EPOCH_RENDER_TIMEOUT_PER_FRAME:-3} python3 epoch-ledger/scripts/render.py render "$WS" --isolate --jobs ${JOBS:-2} -o "$OUT" > "$LOG/$TAG.log" 2>&1 &
pid=$!
while kill -0 $pid 2>/dev/null; do
  tree=$(pstree -p $pid 2>/dev/null | grep -o '([0-9]*)' | tr -d '()' | tr '\n' ',' | sed 's/,$//')
  rss=$( [ -n "$tree" ] && ps -o rss= -p "$tree" 2>/dev/null | awk '{s+=$1} END {print int(s/1024)}' || echo 0)
  echo "$(date +%s) $(free -m | awk '/Mem:/{print $3}') ${rss:-0}" >> "$LOG/$TAG.mem"
  sleep 2
done
wait $pid; rc=$?
t1=$(date +%s.%N)
python3 - "$LOG" "$TAG" "$t0" "$t1" "$rc" <<'PY'
import json, sys
log, tag, t0, t1, rc = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
rows = [list(map(int, l.split())) for l in open(f"{log}/{tag}.mem") if len(l.split()) == 3]
r = {"tag": tag, "rc": rc, "wall_s": round(t1 - t0, 1), "peak_system_used_mb": max((x[1] for x in rows), default=0),
     "baseline_system_used_mb": rows[0][1] if rows else 0, "peak_render_tree_rss_mb": max((x[2] for x in rows), default=0)}
open(f"{log}/{tag}.json", "w").write(json.dumps(r, indent=1)); print(json.dumps(r))
PY
