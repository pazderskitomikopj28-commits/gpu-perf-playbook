#!/usr/bin/env python3
"""Validate that benchmark metadata is complete and contains no fake result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = {"name", "executable", "command", "inputs", "measured_on", "results_file"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = data.get("benchmarks")
    if not isinstance(entries, list) or not entries:
        parser.error("manifest must contain a non-empty benchmarks list")
    errors: list[str] = []
    for index, entry in enumerate(entries):
        missing = REQUIRED - set(entry)
        if missing:
            errors.append(f"entry {index} missing: {sorted(missing)}")
        if entry.get("measured_on") is None and entry.get("results_file") not in (None, ""):
            errors.append(f"entry {index}: results_file must be null until measured_on is set")
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"manifest valid: {len(entries)} benchmark entries; no unverified result claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
