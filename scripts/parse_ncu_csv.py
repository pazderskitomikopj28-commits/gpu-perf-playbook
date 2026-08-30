#!/usr/bin/env python3
"""Convert an Nsight Compute raw-page CSV into a compact, stable summary."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean


REQUIRED_COLUMNS = {"Kernel Name", "Metric Name", "Metric Unit", "Metric Value"}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def numeric_value(value: str) -> float | None:
    normalized = value.replace(",", "").strip()
    try:
        return float(normalized)
    except ValueError:
        return None


@dataclass(frozen=True)
class MetricSummary:
    kernel: str
    metric: str
    unit: str
    value: str
    samples: int


def read_records(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [[clean(cell) for cell in row] for row in csv.reader(handle)]

    header_index = next(
        (
            index
            for index, row in enumerate(rows)
            if REQUIRED_COLUMNS.issubset(set(row))
        ),
        None,
    )
    if header_index is None:
        raise ValueError(
            "Nsight Compute header not found; export with --csv --page raw"
        )

    header = rows[header_index]
    records: list[dict[str, str]] = []
    for row in rows[header_index + 1 :]:
        if not any(row) or row == header:
            continue
        padded = row + [""] * (len(header) - len(row))
        record = dict(zip(header, padded, strict=False))
        if record.get("Metric Name") and record.get("Kernel Name"):
            records.append(record)
    if not records:
        raise ValueError("no metric records found after the Nsight Compute header")
    return records


def summarize(records: list[dict[str, str]]) -> list[MetricSummary]:
    groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for record in records:
        key = (
            record["Kernel Name"],
            record["Metric Name"],
            record["Metric Unit"],
        )
        groups[key].append(record["Metric Value"])

    summaries: list[MetricSummary] = []
    for (kernel, metric, unit), values in sorted(groups.items()):
        numbers = [numeric_value(value) for value in values]
        if all(number is not None for number in numbers):
            mean = fmean(number for number in numbers if number is not None)
            rendered = f"{mean:.6g}"
        else:
            unique = list(dict.fromkeys(values))
            rendered = unique[0] if len(unique) == 1 else "; ".join(unique)
        summaries.append(
            MetricSummary(kernel, metric, unit, rendered, len(values))
        )
    return summaries


def render_markdown(summaries: list[MetricSummary]) -> str:
    lines = [
        "| Kernel | Metric | Value | Unit | Samples |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for item in summaries:
        cells = [item.kernel, item.metric, item.value, item.unit]
        escaped = [cell.replace("|", "\\|") for cell in cells]
        lines.append(
            f"| {escaped[0]} | {escaped[1]} | {escaped[2]} | "
            f"{escaped[3]} | {item.samples} |"
        )
    return "\n".join(lines) + "\n"


def render_json(summaries: list[MetricSummary]) -> str:
    return json.dumps(
        [
            {
                "kernel": item.kernel,
                "metric": item.metric,
                "value": item.value,
                "unit": item.unit,
                "samples": item.samples,
            }
            for item in summaries
        ],
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.csv_path.is_file():
        parser.error(f"file does not exist: {args.csv_path}")

    try:
        summaries = summarize(read_records(args.csv_path))
    except ValueError as error:
        parser.error(str(error))
    rendered = (
        render_json(summaries)
        if args.format == "json"
        else render_markdown(summaries)
    )
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
