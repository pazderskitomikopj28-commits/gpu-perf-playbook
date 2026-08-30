from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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
        data["benchmarks"][0]["commit"] = None
        data["benchmarks"][0]["measured_on"] = None
        data["benchmarks"][0]["results_file"] = "results.csv"
        errors = validator.validate_manifest(data)
        self.assertTrue(any("must be null" in error for error in errors))


class BenchmarkStatisticsTests(unittest.TestCase):
    def test_summary_uses_nearest_rank_p95_and_reports_mad(self) -> None:
        stats = load_script("benchmark_stats")
        samples = stats.read_samples(ROOT / "tests" / "data" / "benchmark_samples.csv")
        summary = stats.summarize(samples)[0]
        self.assertEqual(summary.samples, 5)
        self.assertEqual(summary.correct_samples, 5)
        self.assertAlmostEqual(summary.p50, 10.0)
        self.assertAlmostEqual(summary.p95, 10.2)
        self.assertAlmostEqual(summary.median_absolute_deviation, 0.1)

    def test_lower_is_better_regression_is_detected(self) -> None:
        stats = load_script("benchmark_stats")
        baseline = stats.summarize(
            [stats.Sample("bench", "v", run, value, "ms", True)
             for run, value in enumerate((10.0, 10.1, 9.9, 10.0, 10.2), start=1)]
        )
        candidate = stats.summarize(
            [stats.Sample("bench", "v", run, value, "ms", True)
             for run, value in enumerate((11.0, 11.1, 10.9, 11.0, 11.2), start=1)]
        )
        result = stats.compare(baseline, candidate, "lower", 5.0, 5)[0]
        self.assertEqual(result.status, "REGRESSION")
        self.assertAlmostEqual(result.regression_percent, 10.0)

    def test_duplicate_run_is_rejected(self) -> None:
        stats = load_script("benchmark_stats")
        content = (
            "benchmark,variant,run,value,unit,correct\n"
            "b,v,1,1.0,ms,pass\n"
            "b,v,1,1.1,ms,pass\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "samples.csv"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate run"):
                stats.read_samples(path)


class EnvironmentCaptureTests(unittest.TestCase):
    def test_localized_command_output_uses_system_encoding(self) -> None:
        capture = load_script("capture_environment")
        encoded = "编译器 19.38".encode(capture.locale.getpreferredencoding(False))
        self.assertEqual(capture.decode_command_output(encoded), "编译器 19.38")

    def test_remote_credentials_are_redacted(self) -> None:
        capture = load_script("capture_environment")
        self.assertEqual(
            capture.redact_remote("https://token@example.com/org/repo.git"),
            "https://example.com/org/repo.git",
        )

    def test_gpu_csv_is_parsed(self) -> None:
        capture = load_script("capture_environment")

        def runner(command, _cwd):
            if command[0] == "nvidia-smi":
                return capture.CommandResult(
                    True, 0, "NVIDIA GeForce RTX 4060 Laptop GPU, 591.74, 8188, 8.9"
                )
            return capture.CommandResult(False, None, "")

        records = capture.gpu_records(runner)
        self.assertEqual(records[0]["driver_version"], "591.74")
        self.assertEqual(records[0]["compute_cap"], "8.9")


if __name__ == "__main__":
    unittest.main()
