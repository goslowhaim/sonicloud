from __future__ import annotations

from datetime import date

from .models import Evidence, Opportunity


def render_korean_report(opportunities: list[Opportunity], evidence: list[Evidence]) -> str:
    evidence_by_id = {item.evidence_id: item for item in evidence}
    ranked = sorted(opportunities, key=lambda item: item.score.weighted_total, reverse=True)

    lines: list[str] = [
        f"# 일일 시장조사 보고서 - {date.today().isoformat()}",
        "",
        "## 요약",
        "",
        f"- 후보 수: {len(ranked)}",
        "- 수익화 우선순위: 고 eCPM권 광고형 안드로이드 앱",
        "- 보고서 언어: 한국어",
        "",
        "## 상위 후보",
        "",
    ]

    for index, opportunity in enumerate(ranked[:10], start=1):
        lines.extend(
            [
                f"### {index}. {opportunity.title_ko}",
                "",
                f"- 결정: `{opportunity.decision.value}`",
                f"- 총점: `{opportunity.score.weighted_total}`",
                f"- 신뢰도: `{opportunity.confidence.value}`",
                f"- 타깃 사용자: {opportunity.target_user}",
                f"- 문제: {opportunity.problem_statement_ko}",
                f"- 사용 장면: {opportunity.use_case}",
                f"- 예상 입력/결과: {opportunity.expected_input} -> {opportunity.expected_output}",
                f"- MVP 범위: {', '.join(opportunity.mvp_scope)}",
                f"- 리스크: {', '.join(opportunity.policy_risks) if opportunity.policy_risks else '낮음'}",
                f"- 남는 모듈: {', '.join(opportunity.reusable_assets)}",
                "- 근거:",
            ]
        )
        for evidence_id in opportunity.evidence_ids:
            item = evidence_by_id.get(evidence_id)
            if item is None:
                lines.append(f"  - `{evidence_id}`: 누락된 evidence")
                continue
            lines.append(f"  - `{evidence_id}`: {item.title} ({item.source_type.value}, {item.country})")
        lines.append("")

    lines.extend(["## 하네스 품질 메모", "", "- 스키마 검증을 통과한 데이터만 보고서에 포함했습니다."])
    return "\n".join(lines)
