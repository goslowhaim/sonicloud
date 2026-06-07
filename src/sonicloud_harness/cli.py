from __future__ import annotations

import argparse
from pathlib import Path
import json

from .io import load_jsonl
from .evaluation import evaluate_harness, render_evaluation_markdown
from .models import Evidence, GoldenCase, Opportunity
from .report import render_korean_report
from .ad_policy import (
    AdContext,
    AdEvent,
    AdFormat,
    AppCategory,
    ScreenType,
    render_simulation_markdown,
    simulate_ad_flow,
)
from .validation import parse_bool, parse_int


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Sonicloud offline research harness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate evidence and opportunity files.")
    validate_parser.add_argument("--evidence", type=Path, required=True)
    validate_parser.add_argument("--opportunities", type=Path, required=True)

    report_parser = subparsers.add_parser("report", help="Render a Korean Markdown report.")
    report_parser.add_argument("--evidence", type=Path, required=True)
    report_parser.add_argument("--opportunities", type=Path, required=True)
    report_parser.add_argument("--output", type=Path, required=True)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate grounding and golden-case decisions.")
    evaluate_parser.add_argument("--evidence", type=Path, required=True)
    evaluate_parser.add_argument("--opportunities", type=Path, required=True)
    evaluate_parser.add_argument("--golden-cases", type=Path, required=True)
    evaluate_parser.add_argument("--output", type=Path)

    simulate_parser = subparsers.add_parser("simulate-ads", help="Simulate ad timing policy decisions.")
    simulate_parser.add_argument("--category", choices=[item.value for item in AppCategory], required=True)
    simulate_parser.add_argument("--flow", type=Path, required=True)
    simulate_parser.add_argument("--output", type=Path)

    args = parser.parse_args()

    if args.command == "simulate-ads":
        contexts = _load_ad_contexts(args.flow)
        result = simulate_ad_flow(AppCategory(args.category), contexts)
        output = render_simulation_markdown(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print(f"wrote {args.output}")
        else:
            print(output)
        return

    evidence = load_jsonl(args.evidence, Evidence)
    opportunities = load_jsonl(args.opportunities, Opportunity)

    if args.command == "validate":
        print(f"validated evidence={len(evidence)} opportunities={len(opportunities)}")
        return

    if args.command == "report":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_korean_report(opportunities, evidence), encoding="utf-8")
        print(f"wrote {args.output}")

    if args.command == "evaluate":
        golden_cases = load_jsonl(args.golden_cases, GoldenCase)
        result = evaluate_harness(evidence, opportunities, golden_cases)
        output = render_evaluation_markdown(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print(f"wrote {args.output}")
        else:
            print(output)
        if result.has_blocking_issues:
            raise SystemExit(1)


def _load_ad_contexts(path: Path) -> list[AdContext]:
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


if __name__ == "__main__":
    main()
