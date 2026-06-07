from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AdEvent(str, Enum):
    APP_OPENED = "app_opened"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    RESULT_SAVED = "result_saved"
    RESULT_SHARED = "result_shared"
    SCREEN_CLOSED = "screen_closed"
    SETTINGS_OPENED = "settings_opened"


class ScreenType(str, Enum):
    INPUT = "input"
    PROCESSING = "processing"
    RESULT = "result"
    SHARE = "share"
    SETTINGS = "settings"
    ERROR = "error"


class AdFormat(str, Enum):
    BANNER = "banner"
    INTERSTITIAL = "interstitial"
    REWARDED = "rewarded"


class AppCategory(str, Enum):
    DEFAULT = "default"
    DOCUMENT_SCANNER = "document_scanner"
    PDF_CONVERTER = "pdf_converter"
    QR_SCANNER = "qr_scanner"
    FILE_MANAGER = "file_manager"


@dataclass(frozen=True)
class AdContext:
    event: AdEvent
    screen: ScreenType
    ad_format: AdFormat
    now_seconds: int
    last_ad_seconds: int | None = None
    user_action_completed: bool = False
    has_unsaved_work: bool = False
    is_first_session: bool = False
    has_error: bool = False
    label: str = ""


@dataclass(frozen=True)
class AdDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class AdTimingPolicy:
    min_interval_seconds: int = 180
    first_session_block_seconds: int = 120
    allowed_completion_events: set[AdEvent] = field(
        default_factory=lambda: {
            AdEvent.TASK_COMPLETED,
            AdEvent.RESULT_SAVED,
            AdEvent.RESULT_SHARED,
            AdEvent.SCREEN_CLOSED,
        }
    )
    blocked_screens: set[ScreenType] = field(
        default_factory=lambda: {
            ScreenType.INPUT,
            ScreenType.PROCESSING,
            ScreenType.ERROR,
        }
    )

    def decide(self, context: AdContext) -> AdDecision:
        if context.has_error:
            return AdDecision(False, "block_error_state")

        if context.has_unsaved_work:
            return AdDecision(False, "block_unsaved_work")

        if context.screen in self.blocked_screens:
            return AdDecision(False, f"block_screen_{context.screen.value}")

        if context.ad_format == AdFormat.INTERSTITIAL:
            if context.event not in self.allowed_completion_events:
                return AdDecision(False, f"block_event_{context.event.value}")
            if not context.user_action_completed:
                return AdDecision(False, "block_before_user_action_completed")

        if context.is_first_session and context.now_seconds < self.first_session_block_seconds:
            return AdDecision(False, "block_first_session_warmup")

        if context.last_ad_seconds is not None:
            elapsed = context.now_seconds - context.last_ad_seconds
            if elapsed < self.min_interval_seconds:
                return AdDecision(False, "block_cooldown")

        return AdDecision(True, "allow")

    @classmethod
    def for_category(cls, category: AppCategory) -> "AdTimingPolicy":
        if category == AppCategory.DEFAULT:
            return cls()

        if category == AppCategory.DOCUMENT_SCANNER:
            return cls(
                min_interval_seconds=240,
                first_session_block_seconds=180,
                allowed_completion_events={
                    AdEvent.RESULT_SAVED,
                    AdEvent.RESULT_SHARED,
                    AdEvent.SCREEN_CLOSED,
                },
                blocked_screens={
                    ScreenType.INPUT,
                    ScreenType.PROCESSING,
                    ScreenType.SHARE,
                    ScreenType.ERROR,
                },
            )

        if category == AppCategory.PDF_CONVERTER:
            return cls(
                min_interval_seconds=180,
                first_session_block_seconds=120,
                allowed_completion_events={
                    AdEvent.TASK_COMPLETED,
                    AdEvent.RESULT_SAVED,
                    AdEvent.RESULT_SHARED,
                    AdEvent.SCREEN_CLOSED,
                },
                blocked_screens={
                    ScreenType.INPUT,
                    ScreenType.PROCESSING,
                    ScreenType.ERROR,
                },
            )

        if category == AppCategory.QR_SCANNER:
            return cls(
                min_interval_seconds=300,
                first_session_block_seconds=180,
                allowed_completion_events={
                    AdEvent.TASK_COMPLETED,
                    AdEvent.SCREEN_CLOSED,
                },
                blocked_screens={
                    ScreenType.INPUT,
                    ScreenType.PROCESSING,
                    ScreenType.SHARE,
                    ScreenType.ERROR,
                },
            )

        if category == AppCategory.FILE_MANAGER:
            return cls(
                min_interval_seconds=420,
                first_session_block_seconds=240,
                allowed_completion_events={
                    AdEvent.SCREEN_CLOSED,
                    AdEvent.SETTINGS_OPENED,
                },
                blocked_screens={
                    ScreenType.INPUT,
                    ScreenType.PROCESSING,
                    ScreenType.RESULT,
                    ScreenType.SHARE,
                    ScreenType.ERROR,
                },
            )

        raise ValueError(f"Unsupported app category: {category.value}")


class FakeAdAdapter:
    def __init__(self, policy: AdTimingPolicy | None = None) -> None:
        self.policy = policy or AdTimingPolicy()
        self.shown: list[AdContext] = []
        self.blocked: list[tuple[AdContext, AdDecision]] = []

    def maybe_show(self, context: AdContext) -> AdDecision:
        decision = self.policy.decide(context)
        if decision.allowed:
            self.shown.append(context)
        else:
            self.blocked.append((context, decision))
        return decision


@dataclass(frozen=True)
class AdSimulationStep:
    context: AdContext
    decision: AdDecision


@dataclass(frozen=True)
class AdSimulationResult:
    category: AppCategory
    steps: list[AdSimulationStep]

    @property
    def shown_count(self) -> int:
        return sum(1 for step in self.steps if step.decision.allowed)

    @property
    def blocked_count(self) -> int:
        return sum(1 for step in self.steps if not step.decision.allowed)


def simulate_ad_flow(category: AppCategory, contexts: list[AdContext]) -> AdSimulationResult:
    policy = AdTimingPolicy.for_category(category)
    adapter = FakeAdAdapter(policy)
    steps = [AdSimulationStep(context, adapter.maybe_show(context)) for context in contexts]
    return AdSimulationResult(category=category, steps=steps)


def render_simulation_markdown(result: AdSimulationResult) -> str:
    lines = [
        "# 광고 정책 시뮬레이션",
        "",
        f"- 카테고리: `{result.category.value}`",
        f"- 허용: {result.shown_count}",
        f"- 차단: {result.blocked_count}",
        "",
        "| # | label | event | screen | format | decision | reason |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, step in enumerate(result.steps, start=1):
        context = step.context
        decision = "allow" if step.decision.allowed else "block"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    context.label or "-",
                    context.event.value,
                    context.screen.value,
                    context.ad_format.value,
                    decision,
                    step.decision.reason,
                ]
            )
            + " |"
        )
    return "\n".join(lines)
