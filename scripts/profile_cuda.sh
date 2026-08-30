#!/usr/bin/env bash
set -euo pipefail

exe="${1:?usage: profile_cuda.sh <executable> [args...] }"
shift
report_dir="${REPORT_DIR:-reports}"
mkdir -p "${report_dir}"

nsys profile --trace=cuda,nvtx,osrt --stats=true \
  -o "${report_dir}/systems" "${exe}" "$@"

ncu --set full --kernel-name-base demangled \
  --csv --log-file "${report_dir}/compute.csv" "${exe}" "$@"
