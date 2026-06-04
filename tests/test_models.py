import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sonicloud_harness.enums import Confidence, Decision, MarketPriority, MonetizationModel
from sonicloud_harness.models import Opportunity, ScoreBreakdown
from sonicloud_harness.validation import ValidationError


class ModelValidationTest(unittest.TestCase):
    def test_score_weighted_total_includes_risk_penalty(self) -> None:
        score = ScoreBreakdown(
            demand_strength=80,
            ad_monetization_fit=70,
            mvp_feasibility=60,
            competitive_gap=50,
            high_ecpm_market_fit=90,
            retention_potential=40,
            asset_reusability=80,
            risk_penalty=-20,
        )

        self.assertEqual(score.weighted_total, 70.0)

    def test_opportunity_requires_two_evidence_items(self) -> None:
        opportunity = Opportunity(
            opportunity_id="opp_test",
            title_ko="테스트 후보",
            problem_statement_ko="테스트 문제",
            target_user="테스트 사용자",
            current_alternatives=[],
            use_case="테스트 사용 장면",
            expected_input="입력",
            expected_output="출력",
            monetization_model=MonetizationModel.ADS,
            market_priority=MarketPriority.GLOBAL_FIRST,
            evidence_ids=["ev_1"],
            counter_evidence_ids=[],
            confidence=Confidence.C,
            mvp_scope=["기능"],
            policy_risks=[],
            reusable_assets=["모듈"],
            score=ScoreBreakdown(50, 50, 50, 50, 50, 50, 50, -10),
            decision=Decision.WATCH,
        )

        with self.assertRaises(ValidationError):
            opportunity.validate()


if __name__ == "__main__":
    unittest.main()
