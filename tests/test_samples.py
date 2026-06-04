from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sonicloud_harness.io import load_jsonl
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


if __name__ == "__main__":
    unittest.main()
