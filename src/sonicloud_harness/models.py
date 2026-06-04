from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import (
    AccessMethod,
    Confidence,
    Decision,
    Language,
    LegalStatus,
    MarketPriority,
    MonetizationModel,
    SourceType,
)
from .validation import ValidationError, require_non_empty, require_range, require_unique


@dataclass(frozen=True)
class Source:
    source_id: str
    source_type: SourceType
    access_method: AccessMethod
    legal_status: LegalStatus
    name: str
    url: str
    cost_usd: float = 0.0
    notes: str = ""

    def validate(self) -> None:
        require_non_empty(self.source_id, "source_id")
        require_non_empty(self.name, "name")
        require_non_empty(self.url, "url")
        if self.cost_usd < 0:
            raise ValidationError("cost_usd must be non-negative")


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_id: str
    source_type: SourceType
    collected_at: str
    url_or_locator: str
    language: Language
    country: str
    title: str
    summary: str
    observed_signal: str
    content_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        for field_name in (
            "evidence_id",
            "source_id",
            "collected_at",
            "url_or_locator",
            "country",
            "title",
            "summary",
            "observed_signal",
            "content_hash",
        ):
            require_non_empty(getattr(self, field_name), field_name)
        try:
            datetime.fromisoformat(self.collected_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("collected_at must be ISO-8601") from exc


@dataclass(frozen=True)
class ScoreBreakdown:
    demand_strength: float
    ad_monetization_fit: float
    mvp_feasibility: float
    competitive_gap: float
    high_ecpm_market_fit: float
    retention_potential: float
    asset_reusability: float
    risk_penalty: float

    def validate(self) -> None:
        for field_name in (
            "demand_strength",
            "ad_monetization_fit",
            "mvp_feasibility",
            "competitive_gap",
            "high_ecpm_market_fit",
            "retention_potential",
            "asset_reusability",
        ):
            require_range(getattr(self, field_name), field_name, 0, 100)
        require_range(self.risk_penalty, "risk_penalty", -100, 0)

    @property
    def weighted_total(self) -> float:
        return round(
            self.demand_strength * 0.25
            + self.ad_monetization_fit * 0.25
            + self.mvp_feasibility * 0.20
            + self.competitive_gap * 0.15
            + self.high_ecpm_market_fit * 0.10
            + self.retention_potential * 0.10
            + self.asset_reusability * 0.05
            + self.risk_penalty * 0.20,
            2,
        )


@dataclass(frozen=True)
class Opportunity:
    opportunity_id: str
    title_ko: str
    problem_statement_ko: str
    target_user: str
    current_alternatives: list[str]
    use_case: str
    expected_input: str
    expected_output: str
    monetization_model: MonetizationModel
    market_priority: MarketPriority
    evidence_ids: list[str]
    counter_evidence_ids: list[str]
    confidence: Confidence
    mvp_scope: list[str]
    policy_risks: list[str]
    reusable_assets: list[str]
    score: ScoreBreakdown
    decision: Decision

    def validate(self) -> None:
        for field_name in (
            "opportunity_id",
            "title_ko",
            "problem_statement_ko",
            "target_user",
            "use_case",
            "expected_input",
            "expected_output",
        ):
            require_non_empty(getattr(self, field_name), field_name)
        if len(self.evidence_ids) < 2:
            raise ValidationError("opportunity must reference at least 2 evidence_ids")
        require_unique(self.evidence_ids, "evidence_ids")
        require_unique(self.counter_evidence_ids, "counter_evidence_ids")
        self.score.validate()


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    opportunity_id: str
    valid_opportunity: str
    expected_decision: Decision
    rationale_ko: str

    def validate(self) -> None:
        require_non_empty(self.case_id, "case_id")
        require_non_empty(self.opportunity_id, "opportunity_id")
        if self.valid_opportunity not in {"yes", "no", "uncertain"}:
            raise ValidationError("valid_opportunity must be yes, no, or uncertain")
        require_non_empty(self.rationale_ko, "rationale_ko")
