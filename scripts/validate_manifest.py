#!/usr/bin/env python3
"""Validate benchmark provenance before results are published."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED = {
    "name",
    "repository",
    "commit",
    "executable",
    "command",
    "inputs",
    "warmup_iterations",
    "measured_iterations",
    "correctness",
    "measured_on",
    "results_file",
}
MEASURED_ON_REQUIRED = {"gpu", "driver", "sdk", "compiler"}
FULL_COMMIT = re.compile(r"[0-9a-fA-F]{40}\Z")


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_entry(entry: Any, index: int) -> list[str]:
    prefix = f"entry {index}"
    if not isinstance(entry, dict):
        return [f"{prefix}: must be an object"]

    errors: list[str] = []
    missing = REQUIRED - set(entry)
    if missing:
        errors.append(f"{prefix} missing: {sorted(missing)}")
        return errors

    for field in ("name", "repository", "executable", "command"):
        if not nonempty_string(entry[field]):
            errors.append(f"{prefix}.{field}: must be a non-empty string")
    if nonempty_string(entry["repository"]) and not entry["repository"].startswith(
        ("https://", "ssh://", "git@")
    ):
        errors.append(f"{prefix}.repository: must identify a remote repository")

    if not isinstance(entry["inputs"], dict) or not entry["inputs"]:
        errors.append(f"{prefix}.inputs: must be a non-empty object")
    for field, allow_zero in (("warmup_iterations", True), ("measured_iterations", False)):
        value = entry[field]
        minimum = 0 if allow_zero else 1
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            errors.append(f"{prefix}.{field}: must be an integer >= {minimum}")

    correctness = entry["correctness"]
    if not isinstance(correctness, dict):
        errors.append(f"{prefix}.correctness: must be an object")
    else:
        if not nonempty_string(correctness.get("metric")):
            errors.append(f"{prefix}.correctness.metric: must be a non-empty string")
        tolerance = correctness.get("tolerance")
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or tolerance < 0:
            errors.append(f"{prefix}.correctness.tolerance: must be a number >= 0")

    measured_on = entry["measured_on"]
    results_file = entry["results_file"]
    commit = entry["commit"]
    if measured_on is None:
        if results_file is not None:
            errors.append(f"{prefix}.results_file: must be null until measured_on is set")
        if commit is not None:
            errors.append(f"{prefix}.commit: must be null until a run is measured")
    else:
        if not isinstance(measured_on, dict):
            errors.append(f"{prefix}.measured_on: must be null or an object")
        else:
            missing_hardware = MEASURED_ON_REQUIRED - set(measured_on)
            if missing_hardware:
                errors.append(
                    f"{prefix}.measured_on missing: {sorted(missing_hardware)}"
                )
            for field in MEASURED_ON_REQUIRED & set(measured_on):
                if not nonempty_string(measured_on[field]):
                    errors.append(
                        f"{prefix}.measured_on.{field}: must be a non-empty string"
                    )
        if not nonempty_string(results_file):
            errors.append(f"{prefix}.results_file: required after measurement")
        if not isinstance(commit, str) or FULL_COMMIT.fullmatch(commit) is None:
            errors.append(f"{prefix}.commit: must be the full 40-character Git hash")
    return errors


def validate_manifest(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["manifest root must be an object"]
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    entries = data.get("benchmarks")
    if not isinstance(entries, list) or not entries:
        errors.append("manifest must contain a non-empty benchmarks list")
        return errors
    names: set[str] = set()
    for index, entry in enumerate(entries):
        errors.extend(validate_entry(entry, index))
        if isinstance(entry, dict) and nonempty_string(entry.get("name")):
            if entry["name"] in names:
                errors.append(f"entry {index}.name: duplicate benchmark name")
            names.add(entry["name"])
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    errors = validate_manifest(data)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        f"manifest valid: {len(data['benchmarks'])} benchmark entries; "
        "provenance policy satisfied"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
