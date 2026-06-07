from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .ad_policy import AdContext, AdEvent, AdFormat, AppCategory, ScreenType
from .validation import parse_bool, parse_int


@dataclass(frozen=True)
class AdSimulationSpec:
    simulation_id: str
    opportunity_id: str
    category: AppCategory
    flow_path: str
    expected_shown_count: int
    expected_blocked_count: int
    required_block_reasons: list[str]


def load_ad_contexts(path: Path) -> list[AdContext]:
    contexts: list[AdContext] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            try:
                contexts.append(
                    AdContext(
                        event=AdEvent(payload["event"]),
                        screen=ScreenType(payload["screen"]),
                        ad_format=AdFormat(payload["ad_format"]),
                        now_seconds=parse_int(payload["now_seconds"], "now_seconds"),
                        last_ad_seconds=payload.get("last_ad_seconds"),
                        user_action_completed=parse_bool(
                            payload.get("user_action_completed", False),
                            "user_action_completed",
                        ),
                        has_unsaved_work=parse_bool(payload.get("has_unsaved_work", False), "has_unsaved_work"),
                        is_first_session=parse_bool(payload.get("is_first_session", False), "is_first_session"),
                        has_error=parse_bool(payload.get("has_error", False), "has_error"),
                        label=payload.get("label", ""),
                    )
                )
            except Exception as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return contexts


def load_ad_simulation_specs(path: Path) -> list[AdSimulationSpec]:
    specs: list[AdSimulationSpec] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            try:
                specs.append(
                    AdSimulationSpec(
                        simulation_id=payload["simulation_id"],
                        opportunity_id=payload["opportunity_id"],
                        category=AppCategory(payload["category"]),
                        flow_path=payload["flow_path"],
                        expected_shown_count=parse_int(payload["expected_shown_count"], "expected_shown_count"),
                        expected_blocked_count=parse_int(
                            payload["expected_blocked_count"],
                            "expected_blocked_count",
                        ),
                        required_block_reasons=list(payload.get("required_block_reasons", [])),
                    )
                )
            except Exception as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return specs
