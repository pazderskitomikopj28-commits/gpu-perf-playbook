from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class NsightParserTests(unittest.TestCase):
    def test_repeated_launches_are_averaged(self) -> None:
        parser = load_script("parse_ncu_csv")
        records = parser.read_records(ROOT / "tests" / "data" / "ncu_sample.csv")
        summaries = parser.summarize(records)
        by_metric = {summary.metric: summary for summary in summaries}
        duration = by_metric["gpu__time_duration.sum"]
        throughput = by_metric["dram__throughput.avg.pct_of_peak_sustained_elapsed"]
        self.assertEqual(duration.value, "13")
        self.assertEqual(duration.samples, 2)
        self.assertEqual(throughput.value, "76")

    def test_missing_raw_header_is_rejected(self) -> None:
        parser = load_script("parse_ncu_csv")
        with self.assertRaises(ValueError):
            parser.read_records(ROOT / "README.md")


class ManifestTests(unittest.TestCase):
    def test_example_manifest_is_valid(self) -> None:
        validator = load_script("validate_manifest")
        data = json.loads(
            (ROOT / "examples" / "benchmark_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(validator.validate_manifest(data), [])

    def test_unverified_result_is_rejected(self) -> None:
        validator = load_script("validate_manifest")
        data = json.loads(
            (ROOT / "examples" / "benchmark_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        data["benchmarks"][0]["results_file"] = "results.csv"
        errors = validator.validate_manifest(data)
        self.assertTrue(any("must be null" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
