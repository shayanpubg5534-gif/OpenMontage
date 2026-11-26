#!/bin/bash
# M4 character builds: the M2.3c specs with the motion clip set (CMU, free licence) → .runtime/charlab/out_m4
set -e
cd "$(dirname "$0")/../.."
M=.runtime/charlab/mocap; OUT=${1:-.runtime/charlab/out_m4}
CL="--bvh idle=$M/137_28.bvh:18.9:22.4 --bvh walk_start=$M/82_08.bvh:8.0:14.2 --bvh walk_stop=$M/16_34.bvh:0:2.9 --bvh walk_turn_r=$M/16_19.bvh:0:3.4 \
    --bvh sit=$M/113_15.bvh:0.3:7.0 --bvh sit_idle=$M/114_05.bvh:0.5:11.0 --bvh talk=$M/19_08.bvh:0.4:9.0 --bvh listen=$M/18_08.bvh:2.4:9.6"
for c in ${CHARS:-elias_c nadia_c}; do
  BLENDER_USER_RESOURCES=$PWD/.runtime/charlab/user .runtime/charlab/venv/bin/python epoch-ledger/charlab/build_dressed.py \
     epoch-ledger/charlab/specs/$c.json $OUT $CL > $OUT.$c.log 2>&1 &
done
wait
for c in ${CHARS:-elias_c nadia_c}; do python3 epoch-ledger/charlab/prepare_textures.py $OUT/${c}_tex --spec epoch-ledger/charlab/specs/$c.json; done
