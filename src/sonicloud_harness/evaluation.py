from __future__ import annotations

from dataclasses import dataclass

from .models import Evidence, GoldenCase, Opportunity


@dataclass(frozen=True)
class EvaluationIssue:
    severity: str
    code: str
    subject_id: str
    message: str


@dataclass(frozen=True)
class EvaluationResult:
    issues: list[EvaluationIssue]
    golden_total: int
    golden_matches: int
    opportunity_total: int

    @property
    def golden_accuracy(self) -> float:
        if self.golden_total == 0:
            return 0.0
        return round(self.golden_matches / self.golden_total, 4)

    @property
    def has_blocking_issues(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)


def evaluate_harness(
    evidence: list[Evidence],
    opportunities: list[Opportunity],
    golden_cases: list[GoldenCase],
) -> EvaluationResult:
    issues: list[EvaluationIssue] = []
    evidence_ids = {item.evidence_id for item in evidence}
    opportunity_by_id = {item.opportunity_id: item for item in opportunities}

    for opportunity in opportunities:
        for evidence_id in opportunity.evidence_ids + opportunity.counter_evidence_ids:
            if evidence_id not in evidence_ids:
                issues.append(
                    EvaluationIssue(
                        severity="error",
                        code="missing_evidence",
                        subject_id=opportunity.opportunity_id,
                        message=f"Referenced evidence does not exist: {evidence_id}",
                    )
                )
        if opportunity.decision.value == "pursue" and opportunity.score.weighted_total < 70:
            issues.append(
                EvaluationIssue(
                    severity="warning",
                    code="low_score_pursue",
                    subject_id=opportunity.opportunity_id,
                    message="Pursue decision has total score below 70.",
                )
            )
        if opportunity.score.risk_penalty <= -40 and opportunity.decision.value == "pursue":
            issues.append(
                EvaluationIssue(
                    severity="error",
                    code="high_risk_pursue",
                    subject_id=opportunity.opportunity_id,
                    message="Pursue decision is blocked by high risk penalty.",
                )
            )

    golden_matches = 0
    for golden_case in golden_cases:
        opportunity = opportunity_by_id.get(golden_case.opportunity_id)
        if opportunity is None:
            issues.append(
                EvaluationIssue(
                    severity="error",
                    code="missing_golden_opportunity",
                    subject_id=golden_case.case_id,
                    message=f"Golden case references missing opportunity: {golden_case.opportunity_id}",
                )
            )
            continue
        if opportunity.decision == golden_case.expected_decision:
            golden_matches += 1
        else:
            issues.append(
                EvaluationIssue(
                    severity="warning",
                    code="golden_decision_mismatch",
                    subject_id=golden_case.case_id,
                    message=(
                        f"Expected {golden_case.expected_decision.value}, "
                        f"got {opportunity.decision.value}."
                    ),
                )
            )

    return EvaluationResult(
        issues=issues,
        golden_total=len(golden_cases),
        golden_matches=golden_matches,
        opportunity_total=len(opportunities),
    )


def render_evaluation_markdown(result: EvaluationResult) -> str:
    lines = [
        "# 하네스 평가 결과",
        "",
        f"- 후보 수: {result.opportunity_total}",
        f"- 골든셋 수: {result.golden_total}",
        f"- 골든셋 일치 수: {result.golden_matches}",
        f"- 골든셋 정확도: {result.golden_accuracy}",
        f"- 차단 이슈 있음: {'예' if result.has_blocking_issues else '아니오'}",
        "",
        "## 이슈",
        "",
    ]
    if not result.issues:
        lines.append("- 없음")
    else:
        for issue in result.issues:
            lines.append(f"- `{issue.severity}` `{issue.code}` `{issue.subject_id}`: {issue.message}")
    return "\n".join(lines)
