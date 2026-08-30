# GPU benchmark report

Copy this template for each measured experiment. Replace every bracketed field
before publishing a result.

## Experiment metadata

- Experiment: [name]
- Repository and revision: [URL and full commit]
- Measurement date: [YYYY-MM-DD]
- GPU / driver / SDK / compiler: [versions]
- Build configuration and flags: [configuration]
- Input shapes and dtypes: [contract]

## Hypothesis and method

- Question: [what behavior is being tested]
- Baseline: [reference implementation]
- Variant: [one controlled change]
- Warm-up and measured iterations: [counts]
- Timing method: [CUDA event, wall clock, profiler]
- Numerical reference and tolerance: [correctness rule]

## Results

| Variant | Mean | P50 | P95 | Throughput | Correctness |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline | [..] | [..] | [..] | [..] | [..] |
| Variant | [..] | [..] | [..] | [..] | [..] |

## Interpretation

1. Profiler observation: [timeline or kernel metric]
2. Explanation: [mapping, memory, synchronization, scheduling or math path]
3. Limitations: [uncontrolled variables and unavailable metrics]
4. Follow-up experiment: [next falsifiable question]

## Reproduction

```text
[build command]
[test command]
[benchmark command]
[profiler command]
```

Large profiler reports may remain outside Git. Record their filename and a
cryptographic hash here when they are not committed.

## Backend portability

- CUDA status: [measured / not measured]
- Alternative backend status: [measured / stub / not available]
- Required porting work: [execution mapping, memory API, matrix API, compiler,
  profiler]

An interface seam or stub is not a measured backend result; label it explicitly.
