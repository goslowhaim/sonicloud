from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class SourceType(str, Enum):
    APP_STORE = "app_store"
    FORUM = "forum"
    TREND = "trend"
    FREELANCE_MARKET = "freelance_market"
    APP_MARKETPLACE = "app_marketplace"
    RSS = "rss"


@dataclass(frozen=True)
class SourceTarget:
    source_id: str
    name: str
    source_type: SourceType
    url: str
    market_scope: str
    cadence: str
    allowed_use: str
    tags: list[str]
    notes: str = ""


@dataclass(frozen=True)
class SourceTargetIssue:
    severity: str
    code: str
    source_id: str
    message: str


BANNED_SOURCE_TERMS = {
    "adult",
    "porn",
    "sex",
    "casino",
    "gambling",
    "betting",
    "wager",
}


def load_source_targets(path: Path) -> list[SourceTarget]:
    targets: list[SourceTarget] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            try:
                targets.append(
                    SourceTarget(
                        source_id=payload["source_id"],
                        name=payload["name"],
                        source_type=SourceType(payload["source_type"]),
                        url=payload["url"],
                        market_scope=payload["market_scope"],
                        cadence=payload["cadence"],
                        allowed_use=payload["allowed_use"],
                        tags=list(payload.get("tags", [])),
                        notes=payload.get("notes", ""),
                    )
                )
            except Exception as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return targets


def validate_source_targets(targets: list[SourceTarget]) -> list[SourceTargetIssue]:
    issues: list[SourceTargetIssue] = []
    seen_ids: set[str] = set()

    for target in targets:
        if target.source_id in seen_ids:
            issues.append(
                SourceTargetIssue("error", "duplicate_source_id", target.source_id, "Source ID must be unique.")
            )
        seen_ids.add(target.source_id)

        if not target.url.startswith("https://"):
            issues.append(
                SourceTargetIssue("error", "non_https_url", target.source_id, "Source URL must use HTTPS.")
            )

        searchable = " ".join([target.source_id, target.name, target.url, *target.tags]).lower()
        banned_hits = sorted(term for term in BANNED_SOURCE_TERMS if term in searchable)
        if banned_hits:
            issues.append(
                SourceTargetIssue(
                    "error",
                    "excluded_category_source",
                    target.source_id,
                    f"Source target matches excluded terms: {', '.join(banned_hits)}",
                )
            )

        if not target.allowed_use:
            issues.append(
                SourceTargetIssue(
                    "warning",
                    "missing_allowed_use",
                    target.source_id,
                    "Allowed-use note should explain why this source is acceptable.",
                )
            )

    return issues


def render_source_validation_markdown(targets: list[SourceTarget], issues: list[SourceTargetIssue]) -> str:
    lines = [
        "# 수집 대상 검증",
        "",
        f"- 대상 수: {len(targets)}",
        f"- 차단 이슈 있음: {'예' if any(issue.severity == 'error' for issue in issues) else '아니오'}",
        "",
        "## 대상",
        "",
    ]
    for target in targets:
        lines.append(f"- `{target.source_id}` `{target.source_type.value}` {target.name}: {target.url}")

    lines.extend(["", "## 이슈", ""])
    if not issues:
        lines.append("- 없음")
    else:
        for issue in issues:
            lines.append(f"- `{issue.severity}` `{issue.code}` `{issue.source_id}`: {issue.message}")
    return "\n".join(lines)
