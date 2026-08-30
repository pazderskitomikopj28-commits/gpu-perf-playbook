# RTX 4060 evidence summary — 2026-08-30

This page connects measured results to immutable source commits. Full tables and
commands live in `benchmarks/rtx4060-laptop-2026-08-30.csv` and the two source
repositories.

## Kernel lab

Source commit: [`b080f2c`](https://github.com/pazderskitomikopj28-commits/cuda-kernel-lab/commit/b080f2cf864cb6d5ef891199cb19362fba040e57).

- warp-shuffle reduction: 0.2716 ms P50, 2.6017× median speedup;
- padded tiled transpose: 0.5764 ms P50, 2.0089× vs naive and 1.0266×
  vs the bank-conflicted tile;
- WMMA 512³: 0.0422 ms P50 and 6.3581 TFLOP/s median;
- correctness error was zero; memcheck and racecheck reported no errors.

## Stream pipeline

Source commit: [`14e32d8`](https://github.com/pazderskitomikopj28-commits/cuda-stream-pipeline/commit/14e32d81161bdc657bc6f96136b50ccd1575d725).

- pinned memory delivered 1.4733× median improvement over pageable memory in
  the four-stream experiment;
- four-stream async delivered 0.8539× vs pinned synchronous execution, so it
  was slower rather than faster;
- Nsight Systems measured 7.488 µs median kernel time, 174.461 µs H2D and
  163.854 µs D2H per chunk. Transfer and scheduling dominate the tiny kernel;
- memcheck and racecheck reported no errors.

The negative async result demonstrates the required workflow: verify overlap
and device capabilities, compare against the correct pinned baseline, and report
the actual outcome instead of treating asynchronous API use as proof of speedup.

## Known measurement gap

Nsight Compute CLI initialization exits with `0xC0000409` on this Windows host
for 2024.1.1, driver-matched 2025.4.1 and current 2026.2.1, including elevated
runs and `--list-sets` before any target launch. Consequently this evidence set
contains no claimed hardware-counter result. Nsight Systems, CUDA event timing,
correctness tests and Compute Sanitizer are all independently verified.
