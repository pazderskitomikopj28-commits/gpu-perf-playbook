#!/usr/bin/env python3
"""Capture a compact, reproducible GPU benchmark environment snapshot."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class CommandResult:
    available: bool
    returncode: int | None
    output: str


Runner = Callable[[Sequence[str], Path | None], CommandResult]


def run_command(command: Sequence[str], cwd: Path | None = None) -> CommandResult:
    executable = shutil.which(command[0])
    if executable is None:
        return CommandResult(False, None, "")
    try:
        completed = subprocess.run(
            [executable, *command[1:]],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return CommandResult(True, None, str(error))
    output = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    return CommandResult(True, completed.returncode, output)


def compact_output(output: str, maximum_lines: int = 8) -> str:
    lines = [" ".join(line.split()) for line in output.splitlines() if line.strip()]
    return " | ".join(lines[:maximum_lines])


def redact_remote(remote: str) -> str:
    """Remove URL user information that can contain access tokens."""
    try:
        parsed = urlsplit(remote)
    except ValueError:
        return remote
    if not parsed.scheme or "@" not in parsed.netloc:
        return remote
    hostname = parsed.hostname or ""
    if parsed.port is not None:
        hostname = f"{hostname}:{parsed.port}"
    return urlunsplit((parsed.scheme, hostname, parsed.path, parsed.query, ""))


def tool_record(command: Sequence[str], runner: Runner) -> dict[str, object]:
    result = runner(command, None)
    return {
        "available": result.available,
        "returncode": result.returncode,
        "version_output": compact_output(result.output),
    }


def gpu_records(runner: Runner) -> list[dict[str, str]]:
    fields = ["name", "driver_version", "memory.total", "compute_cap"]
    command = [
        "nvidia-smi",
        f"--query-gpu={','.join(fields)}",
        "--format=csv,noheader,nounits",
    ]
    result = runner(command, None)
    if not result.available or result.returncode != 0:
        fields = fields[:-1]
        command[1] = f"--query-gpu={','.join(fields)}"
        result = runner(command, None)
    if not result.available or result.returncode != 0:
        return []

    records: list[dict[str, str]] = []
    for row in csv.reader(io.StringIO(result.output)):
        if len(row) != len(fields):
            continue
        records.append({field: value.strip() for field, value in zip(fields, row)})
    return records


def git_record(repository: Path, runner: Runner) -> dict[str, object]:
    def git(*arguments: str) -> CommandResult:
        return runner(["git", *arguments], repository)

    commit = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    status = git("status", "--porcelain")
    remote = git("remote", "get-url", "origin")
    return {
        "name": repository.resolve().name,
        "commit": commit.output.strip() if commit.returncode == 0 else None,
        "branch": branch.output.strip() if branch.returncode == 0 else None,
        "dirty": bool(status.output.strip()) if status.returncode == 0 else None,
        "origin": redact_remote(remote.output.strip()) if remote.returncode == 0 else None,
    }


def capture_environment(
    repository: Path, runner: Runner = run_command
) -> dict[str, object]:
    tools = {
        "git": tool_record(["git", "--version"], runner),
        "cmake": tool_record(["cmake", "--version"], runner),
        "nvcc": tool_record(["nvcc", "--version"], runner),
        "nsys": tool_record(["nsys", "--version"], runner),
        "ncu": tool_record(["ncu", "--version"], runner),
    }
    compiler_command = ["cl"] if os.name == "nt" else ["c++", "--version"]
    tools["host_compiler"] = tool_record(compiler_command, runner)
    cuda_paths = {
        name: os.environ[name]
        for name in ("CUDA_PATH", "CUDA_PATH_V12_4", "CUDA_HOME")
        if os.environ.get(name)
    }
    return {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "host": {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "repository": git_record(repository, runner),
        "gpus": gpu_records(runner),
        "tools": tools,
        "cuda_paths": cuda_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.repository.is_dir():
        parser.error(f"repository directory does not exist: {args.repository}")
    snapshot = capture_environment(args.repository)
    rendered = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
