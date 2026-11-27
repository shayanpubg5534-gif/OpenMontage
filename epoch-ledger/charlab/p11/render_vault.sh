#!/usr/bin/env bash
# P11: render the 3D vault shot with W parallel workers (frame ranges), join by stream copy, then apply the series'
# painterly pass so the 3D shot matches the painted plates. Internal render scale 0.75 (P11_VAULT_SCALE), output 1080p.
#   epoch-ledger/charlab/p11/render_vault.sh RESOLVED_MAP OUT.mp4 [W]
set -euo pipefail
cd "$(dirname "$0")/../../.."
RES=$1; OUT=$2; W=${3:-4}; TMP=$(mktemp -d)
read -r D KEYS < <(python3 - "$RES" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])); s = next(x for x in r["shots"] if x["id"] == "S3"); E = {e["id"]: e["t"] - s["t0"] for e in r["events"]}
D = round(s["t1"] - s["t0"], 3)
# camera keyed to the narration: settle on the gate, push in on the lock through "vault … opened", move past the lock
# to the cash on "no cash", then hold on the untouched stacks
keys = [[0, [0.6, 1.22, 1.45], [0.08, 1.08, 0], 36], [round(E["e08"], 3), [0.55, 1.2, 1.3], [0.1, 1.08, 0], 34],
        [round(E["e10"] - 0.05, 3), [0.4, 1.16, 0.85], [0.12, 1.06, 0], 30], [round(E["e11"] + 0.35, 3), [-0.05, 1.16, 0.72], [-0.32, 0.95, -1.25], 28],
        [D, [-0.1, 1.15, 0.66], [-0.38, 0.93, -1.25], 27]]
print(D, json.dumps(keys, separators=(",", ":")))
PY
)
N=$(python3 -c "print(round($D*30))"); PER=$(( (N + W - 1) / W )); pids=()
for ((w=0; w<W; w++)); do a=$((w*PER)); b=$((a+PER-1)); [ $a -ge $N ] && break; [ $b -ge $N ] && b=$((N-1))
  P11_VAULT_SCALE=${P11_VAULT_SCALE:-0.75} node epoch-ledger/charlab/p11/vault3d.mjs $TMP/p$w.mp4 $D "$KEYS" --from $a --to $b > $TMP/p$w.log & pids+=($!); echo "file '$TMP/p$w.mp4'" >> $TMP/list.txt; done
for p in "${pids[@]}"; do wait $p; done
ffmpeg -loglevel error -y -f concat -safe 0 -i $TMP/list.txt -c copy $TMP/raw.mp4
ffmpeg -loglevel error -y -i $TMP/raw.mp4 -filter_complex "$(cat epoch-ledger/charlab/p9/paint_filter.txt),vignette=angle=0.4,noise=alls=4:allf=t,format=yuv420p" \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:v libx264 -preset medium -crf 16 "$OUT"
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$OUT"); [ "$n" = "$N" ] || { echo "vault: $n frames, expected $N"; exit 1; }
cat $TMP/p*.log; rm -rf $TMP
