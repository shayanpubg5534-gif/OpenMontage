#!/usr/bin/env bash
# P5: measured end-to-end cold render through the continuous-session architecture.
#   epoch-ledger/charlab/bench/e2e_prerender.sh SEQUENCE.py CHARS WS OUT.mp4 LOGDIR [SHOT_CACHE]
# Phases (wall clock): 1) hf_sequence --prerender (continuous-session 3D render + encode + workspace build)
#                      2) render.py (HyperFrames compositing of video layer + captions + labels + audio; production tool, unmodified)
set -u
SEQ=$1; CHARS=$2; WS=$3; OUT=$4; LOG=$5; CACHE=${6:-$PWD/.runtime/charlab/shotcache_e2e}
cd "$(dirname "$0")/../../.."; mkdir -p "$LOG"
( while true; do echo "$(date +%s) $(free -m | awk '/Mem:/{print $3}')" >> "$LOG/mem.log"; sleep 2; done ) & MON=$!
t0=$(date +%s.%N)
python3 epoch-ledger/charlab/hf_sequence.py "$SEQ" "$CHARS" "$WS" --prerender --shot-cache "$CACHE" > "$LOG/build.json" 2> "$LOG/build.err"; rc1=$?
t1=$(date +%s.%N)
EPOCH_RENDER_TIMEOUT_PER_FRAME=${EPOCH_RENDER_TIMEOUT_PER_FRAME:-3} python3 epoch-ledger/scripts/render.py render "$WS" --isolate --jobs ${JOBS:-1} -o "$OUT" > "$LOG/render.log" 2>&1; rc2=$?
t2=$(date +%s.%N)
kill $MON
python3 - "$LOG" "$t0" "$t1" "$t2" "$rc1" "$rc2" "$OUT" <<'PY'
import json, sys, subprocess
log, t0, t1, t2, rc1, rc2, out = sys.argv[1], *map(float, sys.argv[2:5]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
mem = [int(l.split()[1]) for l in open(f"{log}/mem.log") if len(l.split()) == 2]
b = json.loads(open(f"{log}/build.json").read().strip().splitlines()[-1]) if rc1 == 0 else {}
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames", "-of", "json", out], capture_output=True, text=True).stdout if rc2 == 0 else ""
r = {"rc_build": rc1, "rc_render": rc2, "phase1_prerender_and_build_s": round(t1 - t0, 1), "phase2_hyperframes_composite_s": round(t2 - t1, 1),
     "total_wall_s": round(t2 - t0, 1), "peak_system_mem_mb": max(mem or [0]), "baseline_mem_mb": mem[0] if mem else 0,
     "shots": b.get("prerendered"), "output": json.loads(probe) if probe else None}
open(f"{log}/e2e.json", "w").write(json.dumps(r, indent=1)); print(json.dumps({k: r[k] for k in ("rc_build", "rc_render", "phase1_prerender_and_build_s", "phase2_hyperframes_composite_s", "total_wall_s", "peak_system_mem_mb")}))
PY
