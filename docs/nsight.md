# Nsight evidence workflow

## 1. Establish a deterministic baseline

Record the repository commit, GPU model, driver, CUDA/SUPA SDK version, compiler
flags, input shape, warm-up count, iteration count and correctness threshold.
Run the same command at least three times and keep the raw output.

## 2. Systems timeline

```bash
nsys profile --trace=cuda,nvtx,osrt --stats=true \
  -o reports/kernel_systems ./build/kernel_bench \
  --op reduce --rows 4096 --cols 4096 --iters 10
```

Use Systems for launch gaps, host/device copies, stream overlap, synchronization
and CPU-side orchestration. It is not the right tool for explaining why one
warp is stalled inside a single kernel.

## 3. Compute metrics

```bash
ncu --set basic --page raw --kernel-name-base demangled --csv \
  --log-file reports/kernel_compute.csv ./build/kernel_bench \
  --op reduce --rows 4096 --cols 4096 --iters 3
```

Start with achieved memory throughput, arithmetic throughput, occupancy, warp
stall reasons, branch efficiency and instruction mix. Interpret occupancy as a
constraint, not a goal: a high occupancy number does not prove high performance.
Start with `--set basic`; `--set full` can require many replay passes and should
be used only after the target kernel and question have been narrowed down.

Convert the raw CSV into a reviewable table while preserving the original:

```bash
python scripts/parse_ncu_csv.py reports/kernel_compute.csv \
  --output reports/kernel_compute.md
```

## 4. Make the claim reproducible

Put the command and report path in `benchmarks/results.schema.csv`. If an
optimization changes numerical behavior, record the tolerance and worst-case
error next to the speed result. A benchmark without correctness evidence is not
an optimization result.
