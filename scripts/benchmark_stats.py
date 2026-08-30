#!/usr/bin/env python3
"""Validate, summarize and compare raw benchmark samples."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean, median, stdev


REQUIRED_COLUMNS = {"benchmark", "variant", "run", "value", "unit", "correct"}
TRUE_VALUES = {"1", "true", "yes", "pass"}
FALSE_VALUES = {"0", "false", "no", "fail"}


@dataclass(frozen=True)
class Sample:
    benchmark: str
    variant: str
    run: int
    value: float
    unit: str
    correct: bool


@dataclass(frozen=True)
class Summary:
    benchmark: str
    variant: str
    unit: str
    samples: int
    correct_samples: int
    mean: float
    standard_deviation: float
    p50: float
    p95: float
    minimum: float
    maximum: float
    median_absolute_deviation: float


@dataclass(frozen=True)
class Comparison:
    benchmark: str
    variant: str
    unit: str
    baseline_p50: float
    candidate_p50: float
    regression_percent: float
    threshold_percent: float
    direction: str
    status: str


def parse_correct(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"invalid correctness value: {value!r}")


def read_samples(path: Path) -> list[Sample]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            raise ValueError(f"missing sample columns: {missing}")
        samples: list[Sample] = []
        seen_runs: set[tuple[str, str, str, int]] = set()
        for line_number, row in enumerate(reader, start=2):
            try:
                benchmark = row["benchmark"].strip()
                variant = row["variant"].strip()
                unit = row["unit"].strip()
                run = int(row["run"])
                value = float(row["value"])
                correct = parse_correct(row["correct"])
            except (AttributeError, TypeError, ValueError) as error:
                raise ValueError(f"line {line_number}: {error}") from error
            if not benchmark or not variant or not unit:
                raise ValueError(f"line {line_number}: group fields must be non-empty")
            if run <= 0 or not math.isfinite(value):
                raise ValueError(
                    f"line {line_number}: run must be positive and value finite"
                )
            key = (benchmark, variant, unit, run)
            if key in seen_runs:
                raise ValueError(f"line {line_number}: duplicate run for {key}")
            seen_runs.add(key)
            samples.append(Sample(benchmark, variant, run, value, unit, correct))
    if not samples:
        raise ValueError("sample file is empty")
    return samples


def nearest_rank(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile without values")
    ordered = sorted(values)
    index = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[index]


def summarize(samples: list[Sample]) -> list[Summary]:
    groups: dict[tuple[str, str, str], list[Sample]] = defaultdict(list)
    for sample in samples:
        groups[(sample.benchmark, sample.variant, sample.unit)].append(sample)
    results: list[Summary] = []
    for (benchmark, variant, unit), group in sorted(groups.items()):
        values = [sample.value for sample in group]
        p50 = median(values)
        results.append(
            Summary(
                benchmark=benchmark,
                variant=variant,
                unit=unit,
                samples=len(values),
                correct_samples=sum(sample.correct for sample in group),
                mean=fmean(values),
                standard_deviation=stdev(values) if len(values) > 1 else 0.0,
                p50=p50,
                p95=nearest_rank(values, 0.95),
                minimum=min(values),
                maximum=max(values),
                median_absolute_deviation=median(
                    [abs(value - p50) for value in values]
                ),
            )
        )
    return results


def compare(
    baseline: list[Summary],
    candidate: list[Summary],
    direction: str,
    threshold_percent: float,
    minimum_samples: int,
) -> list[Comparison]:
    if direction not in {"lower", "higher"}:
        raise ValueError("direction must be lower or higher")
    if threshold_percent < 0 or minimum_samples < 1:
        raise ValueError("threshold must be non-negative and minimum samples positive")
    baseline_by_key = {
        (item.benchmark, item.variant, item.unit): item for item in baseline
    }
    candidate_by_key = {
        (item.benchmark, item.variant, item.unit): item for item in candidate
    }
    if baseline_by_key.keys() != candidate_by_key.keys():
        missing = sorted(baseline_by_key.keys() - candidate_by_key.keys())
        extra = sorted(candidate_by_key.keys() - baseline_by_key.keys())
        raise ValueError(f"sample groups differ; missing={missing}, extra={extra}")

    results: list[Comparison] = []
    for key in sorted(baseline_by_key):
        before = baseline_by_key[key]
        after = candidate_by_key[key]
        if before.samples < minimum_samples or after.samples < minimum_samples:
            raise ValueError(f"group {key} has fewer than {minimum_samples} samples")
        if before.correct_samples != before.samples or after.correct_samples != after.samples:
            raise ValueError(f"group {key} contains failed correctness checks")
        if before.p50 == 0:
            raise ValueError(f"group {key} has a zero baseline median")
        relative_change = (after.p50 / before.p50 - 1.0) * 100.0
        regression = relative_change if direction == "lower" else -relative_change
        results.append(
            Comparison(
                benchmark=key[0],
                variant=key[1],
                unit=key[2],
                baseline_p50=before.p50,
                candidate_p50=after.p50,
                regression_percent=regression,
                threshold_percent=threshold_percent,
                direction=direction,
                status="REGRESSION" if regression > threshold_percent else "PASS",
            )
        )
    return results


def render_summaries(items: list[Summary], output_format: str) -> str:
    if output_format == "json":
        return json.dumps([asdict(item) for item in items], indent=2) + "\n"
    lines = [
        "| Benchmark | Variant | N | Correct | Mean | Stddev | P50 | P95 | MAD | Unit |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in items:
        benchmark = item.benchmark.replace("|", "\\|")
        variant = item.variant.replace("|", "\\|")
        unit = item.unit.replace("|", "\\|")
        lines.append(
            f"| {benchmark} | {variant} | {item.samples} | "
            f"{item.correct_samples}/{item.samples} | {item.mean:.6g} | "
            f"{item.standard_deviation:.6g} | {item.p50:.6g} | "
            f"{item.p95:.6g} | {item.median_absolute_deviation:.6g} | "
            f"{unit} |"
        )
    return "\n".join(lines) + "\n"


def render_comparisons(items: list[Comparison], output_format: str) -> str:
    if output_format == "json":
        return json.dumps([asdict(item) for item in items], indent=2) + "\n"
    lines = [
        "| Benchmark | Variant | Baseline P50 | Candidate P50 | Regression | Limit | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in items:
        benchmark = item.benchmark.replace("|", "\\|")
        variant = item.variant.replace("|", "\\|")
        unit = item.unit.replace("|", "\\|")
        lines.append(
            f"| {benchmark} | {variant} | {item.baseline_p50:.6g} "
            f"{unit} | {item.candidate_p50:.6g} {unit} | "
            f"{item.regression_percent:.3f}% | {item.threshold_percent:.3f}% | "
            f"{item.status} |"
        )
    return "\n".join(lines) + "\n"


def write_output(rendered: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    summarize_parser = subparsers.add_parser("summarize")
    summarize_parser.add_argument("samples", type=Path)
    summarize_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    summarize_parser.add_argument("--output", type=Path)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("baseline", type=Path)
    compare_parser.add_argument("candidate", type=Path)
    compare_parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    compare_parser.add_argument("--max-regression-percent", type=float, default=5.0)
    compare_parser.add_argument("--min-samples", type=int, default=5)
    compare_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    compare_parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "summarize":
            summaries = summarize(read_samples(args.samples))
            write_output(render_summaries(summaries, args.format), args.output)
            return 0
        comparisons = compare(
            summarize(read_samples(args.baseline)),
            summarize(read_samples(args.candidate)),
            args.direction,
            args.max_regression_percent,
            args.min_samples,
        )
        write_output(render_comparisons(comparisons, args.format), args.output)
        return 1 if any(item.status == "REGRESSION" for item in comparisons) else 0
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
