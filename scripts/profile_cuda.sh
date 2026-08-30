#!/usr/bin/env bash
set -euo pipefail

exe="${1:?usage: profile_cuda.sh <executable> [args...] }"
shift
report_dir="${REPORT_DIR:-reports}"
ncu_set="${NCU_SET:-basic}"
mkdir -p "${report_dir}"

nsys profile --force-overwrite=true --trace=cuda,nvtx,osrt --stats=true \
  -o "${report_dir}/systems" "${exe}" "$@"

ncu --force-overwrite --set "${ncu_set}" --page raw --kernel-name-base demangled \
  --csv --log-file "${report_dir}/compute.csv" "${exe}" "$@"
