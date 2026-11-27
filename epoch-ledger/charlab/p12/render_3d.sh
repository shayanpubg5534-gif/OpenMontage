#!/usr/bin/env bash
# P12: render the selective 3D shot S3 (scenes/stack.js) with the camera keyed to the narration, W parallel workers
# (frame ranges; static holds are rendered once), join, and apply the series' painterly pass.
#   epoch-ledger/charlab/p12/render_3d.sh RESOLVED_MAP OUT.mp4 [W]
set -euo pipefail
cd "$(dirname "$0")/../../.."
RES=$1; OUT=$2; W=${3:-2}; TMP=$(mktemp -d)
read -r D KEYS EV < <(python3 - "$RES" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])); s = next(x for x in r["shots"] if x["id"] == "S3"); E = {e["id"]: round(e["t"] - s["t0"], 3) for e in r["events"]}
D = round(s["t1"] - s["t0"], 3); Y = 0.83          # top of the bundle (scenes/stack.js YTOP)
# hold on the family's folder through "doesn't keep" (SOLD prints), pull back on "sells", the bundle on "bundled", the
# whole block on "thousands", settle for "a single security"
keys = [[0, [0.12, Y + .5, .36], [0.06, Y, .03], 40], [E["e10"], [0.12, Y + .5, .36], [0.06, Y, .03], 40],
        [E["e10b"] + .2, [0.7, Y + 1.6, 1.9], [0.05, Y - .1, 0], 42], [E["e11"] + .6, [4.6, Y + 3.2, 6.9], [0, .4, 0], 42], [D, [5.5, Y + 3.6, 8.4], [0, .35, 0], 42]]
print(D, json.dumps(keys, separators=(",", ":")), json.dumps({"keep": E["e09"]}, separators=(",", ":")))
PY
)
N=$(python3 -c "print(round($D*30))"); PER=$(( (N + W - 1) / W )); pids=()
for ((w=0; w<W; w++)); do a=$((w*PER)); b=$((a+PER-1)); [ $a -ge $N ] && break; [ $b -ge $N ] && b=$((N-1))
  node epoch-ledger/charlab/p12/three_shot.mjs epoch-ledger/charlab/p12/scenes/stack.js $TMP/p$w.mp4 $D "$KEYS" "$EV" --from $a --to $b > $TMP/p$w.log & pids+=($!)
  echo "file '$TMP/p$w.mp4'" >> $TMP/list.txt; done
for p in "${pids[@]}"; do wait $p; done
ffmpeg -loglevel error -y -f concat -safe 0 -i $TMP/list.txt -c copy $TMP/raw.mp4
ffmpeg -loglevel error -y -i $TMP/raw.mp4 -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt),vignette=angle=0.4,noise=alls=4:allf=t,format=yuv420p" \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:v libx264 -preset medium -crf 16 "$OUT"
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$OUT"); [ "$n" = "$N" ] || { echo "3d: $n frames, expected $N"; exit 1; }
cat $TMP/p*.log; rm -rf $TMP
