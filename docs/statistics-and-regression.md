# Benchmark statistics and regression checks

## Keep raw samples

Use one row per fresh-process result. The required schema is
`benchmarks/samples.schema.csv`:

```csv
benchmark,variant,run,value,unit,correct
vector_add,baseline,1,10.0,ms,pass
```

`benchmark`, `variant` and `unit` form a comparison group. Run numbers must be
positive and unique inside that group, values must be finite, and correctness is
part of the data rather than a note added after measurement.

## Summarize repeated runs

```bash
python scripts/benchmark_stats.py summarize raw-samples.csv
```

The tool reports sample count, correctness count, mean, sample standard
deviation, P50, nearest-rank P95, range and median absolute deviation (MAD).
With five runs, nearest-rank P95 is the maximum; publishing it makes occasional
slow fresh-process runs visible instead of smoothing them away.

P50 is the default comparison statistic because GPU clocks, WDDM scheduling and
background activity can create asymmetric outliers. Mean, P95 and MAD remain in
the report so the median cannot hide instability.

## Check a candidate against a baseline

```bash
python scripts/benchmark_stats.py compare baseline.csv candidate.csv \
  --direction lower --max-regression-percent 5 --min-samples 5
```

The command requires identical benchmark groups, passing correctness checks and
at least five samples per side by default. For `lower`, a larger candidate P50 is
a regression; for `higher`, a smaller candidate P50 is a regression. Exit code 1
means at least one group exceeded the configured limit, making the command usable
as a CI gate.

The percentage threshold is an engineering policy, not a statistical
significance test. Set it from prior repeated-run noise on the target machine,
and inspect MAD/P95 before treating a small pass or failure as causal. Do not mix
machines, power modes, toolchains or input shapes in one comparison group.
