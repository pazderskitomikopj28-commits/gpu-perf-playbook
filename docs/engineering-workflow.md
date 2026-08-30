# Engineering workflow

## Git

Use one branch per experiment and keep the benchmark command in the commit
message or results row. A useful sequence is:

```bash
git switch -c feat/reduce-mean-warp
git add src tests docs
git commit -m "feat: add warp-shuffle reduce mean"
git tag -a reduce-mean-v1 -m "baseline and optimized reduction"
```

Never commit generated profiler reports or local credentials. Commit the small
metadata row and keep large reports in a release artifact when needed.

## VS Code

Configure the CUDA extension to use the same compiler and architecture as the
command line. The integrated terminal should run the exact commands in each
README; editor-only launch settings are not a substitute for reproducibility.

## AI Coding

Use an AI coding assistant for scaffolding, API lookup and review, but keep the
human-owned loop explicit:

1. write the shape/stride and numerical contract;
2. ask for a small implementation;
3. inspect synchronization, bounds and aliasing manually;
4. run correctness tests and sanitizers;
5. profile the real workload;
6. record the prompt/decision in the commit or lab note when it materially
   changed the implementation.

This turns “AI Coding” into an auditable engineering practice rather than a
claim that generated code was automatically correct.
