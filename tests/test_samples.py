from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sonicloud_harness.io import load_jsonl
from sonicloud_harness.ad_simulation import load_ad_simulation_specs
from sonicloud_harness.evaluation import evaluate_harness
from sonicloud_harness.models import Evidence, GoldenCase, Opportunity, Source
from sonicloud_harness.report import render_korean_report


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


class SampleDataTest(unittest.TestCase):
    def test_seed_files_validate(self) -> None:
        sources = load_jsonl(SAMPLES / "sources.seed.jsonl", Source)
        evidence = load_jsonl(SAMPLES / "evidence.seed.jsonl", Evidence)
        opportunities = load_jsonl(SAMPLES / "opportunities.seed.jsonl", Opportunity)
        golden_cases = load_jsonl(SAMPLES / "golden_cases.seed.jsonl", GoldenCase)

        self.assertGreaterEqual(len(sources), 1)
        self.assertGreaterEqual(len(evidence), 2)
        self.assertGreaterEqual(len(opportunities), 1)
        self.assertGreaterEqual(len(golden_cases), 1)

    def test_korean_report_renders(self) -> None:
        evidence = load_jsonl(SAMPLES / "evidence.seed.jsonl", Evidence)
        opportunities = load_jsonl(SAMPLES / "opportunities.seed.jsonl", Opportunity)
        report = render_korean_report(opportunities, evidence)

        self.assertIn("일일 시장조사 보고서", report)
        self.assertIn("상위 후보", report)
        self.assertIn("광고형 안드로이드 앱", report)

    def test_seed_golden_cases_match(self) -> None:
        evidence = load_jsonl(SAMPLES / "evidence.seed.jsonl", Evidence)
        opportunities = load_jsonl(SAMPLES / "opportunities.seed.jsonl", Opportunity)
        golden_cases = load_jsonl(SAMPLES / "golden_cases.seed.jsonl", GoldenCase)
        result = evaluate_harness(evidence, opportunities, golden_cases)

        self.assertFalse(result.has_blocking_issues)
        self.assertEqual(result.golden_accuracy, 1.0)

    def test_seed_ad_simulations_match_manifest(self) -> None:
        evidence = load_jsonl(SAMPLES / "evidence.seed.jsonl", Evidence)
        opportunities = load_jsonl(SAMPLES / "opportunities.seed.jsonl", Opportunity)
        golden_cases = load_jsonl(SAMPLES / "golden_cases.seed.jsonl", GoldenCase)
        ad_simulations = load_ad_simulation_specs(SAMPLES / "ad_simulation_manifest.seed.jsonl")
        result = evaluate_harness(evidence, opportunities, golden_cases, ad_simulations)

        self.assertFalse(result.has_blocking_issues)

    def test_simulate_ads_cli_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "sonicloud_harness.cli",
                "simulate-ads",
                "--category",
                "document_scanner",
                "--flow",
                str(SAMPLES / "ad_flows.document_scanner.seed.jsonl"),
            ],
            check=True,
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
        )

        self.assertIn("광고 정책 시뮬레이션", completed.stdout)


if __name__ == "__main__":
    unittest.main()
