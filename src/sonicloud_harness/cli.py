from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_jsonl
from .models import Evidence, Opportunity
from .report import render_korean_report


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

    args = parser.parse_args()

    evidence = load_jsonl(args.evidence, Evidence)
    opportunities = load_jsonl(args.opportunities, Opportunity)

    if args.command == "validate":
        print(f"validated evidence={len(evidence)} opportunities={len(opportunities)}")
        return

    if args.command == "report":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_korean_report(opportunities, evidence), encoding="utf-8")
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
