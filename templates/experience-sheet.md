# GPU project evidence sheet

Copy one sheet per real project. Replace every bracketed field with measured or
verifiable information before using it in an application.

## Project

- Name: [project name]
- Repository: [public URL]
- Commit/tag: [commit]
- Date: [YYYY-MM-DD]
- My role: [what I personally implemented]

## Technical contract

- Input/output shapes and dtypes: [..]
- Numerical reference and tolerance: [..]
- Target GPU / driver / SDK: [..]
- Build command and flags: [..]

## Optimization evidence

1. Baseline: [implementation and mean latency]
2. Bottleneck: [Nsight Systems/Compute observation]
3. Change: [mapping, memory layout, tiling, synchronization or math path]
4. Result: [mean/p50/p95, throughput, speedup]
5. Correctness: [test command and max error]

## Engineering evidence

- Tests: [command]
- Reproducibility: [container/environment/README]
- Git history: [links to meaningful commits]
- AI Coding contribution: [what was suggested, what I reviewed, what I changed]

## Platform-portability note

- NVIDIA CUDA result: [measured / not measured]
- BIRENSUPA result: [measured / not measured]
- If not measured, write: “接口边界已预留，尚未在壁仞真机验证”，not “熟悉壁仞架构”。
