#!/usr/bin/env python3
"""Summarize an Nsight Compute CSV without depending on pandas."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    if not args.csv_path.is_file():
        parser.error(f"file does not exist: {args.csv_path}")

    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    rows = [[clean(cell) for cell in row] for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        print("No rows found")
        return 0

    print(f"rows={len(rows)} columns={max(len(row) for row in rows)}")
    for index, row in enumerate(rows[:8]):
        print(f"row[{index}]=" + " | ".join(row))
    if len(rows) > 8:
        print(f"... {len(rows) - 8} more rows (keep the raw CSV for auditability)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
