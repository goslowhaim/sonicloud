from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .ad_policy import render_simulation_markdown, simulate_ad_flow
from .ad_simulation import AdSimulationSpec, load_ad_contexts, load_ad_simulation_specs
from .evaluation import evaluate_harness, render_evaluation_markdown
from .io import load_jsonl
from .models import Evidence, GoldenCase, Opportunity
from .report import render_korean_report


@dataclass(frozen=True)
class BatchConfig:
    evidence_path: str
    opportunities_path: str
    golden_cases_path: str
    output_dir: str
    ad_simulations_path: str | None = None
    ad_simulation_reports: bool = True


@dataclass(frozen=True)
class BatchRunResult:
    run_date: str
    output_dir: Path
    report_path: Path
    evaluation_path: Path
    ad_simulation_paths: list[Path]
    has_blocking_issues: bool


def load_batch_config(path: Path) -> BatchConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return BatchConfig(
        evidence_path=payload["evidence_path"],
        opportunities_path=payload["opportunities_path"],
        golden_cases_path=payload["golden_cases_path"],
        output_dir=payload["output_dir"],
        ad_simulations_path=payload.get("ad_simulations_path"),
        ad_simulation_reports=bool(payload.get("ad_simulation_reports", True)),
    )


def run_batch(config: BatchConfig, run_date: str) -> BatchRunResult:
    evidence = load_jsonl(Path(config.evidence_path), Evidence)
    opportunities = load_jsonl(Path(config.opportunities_path), Opportunity)
    golden_cases = load_jsonl(Path(config.golden_cases_path), GoldenCase)
    ad_simulations = (
        load_ad_simulation_specs(Path(config.ad_simulations_path))
        if config.ad_simulations_path
        else None
    )

    output_dir = Path(config.output_dir) / run_date
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "daily-report.ko.md"
    report_path.write_text(render_korean_report(opportunities, evidence), encoding="utf-8")

    evaluation = evaluate_harness(evidence, opportunities, golden_cases, ad_simulations)
    evaluation_path = output_dir / "evaluation.md"
    evaluation_path.write_text(render_evaluation_markdown(evaluation), encoding="utf-8")

    simulation_paths: list[Path] = []
    if ad_simulations and config.ad_simulation_reports:
        simulation_paths = write_ad_simulation_reports(ad_simulations, output_dir)

    return BatchRunResult(
        run_date=run_date,
        output_dir=output_dir,
        report_path=report_path,
        evaluation_path=evaluation_path,
        ad_simulation_paths=simulation_paths,
        has_blocking_issues=evaluation.has_blocking_issues,
    )


def write_ad_simulation_reports(specs: list[AdSimulationSpec], output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for spec in specs:
        contexts = load_ad_contexts(Path(spec.flow_path))
        simulation = simulate_ad_flow(spec.category, contexts)
        path = output_dir / f"ad-simulation.{spec.simulation_id}.md"
        path.write_text(render_simulation_markdown(simulation), encoding="utf-8")
        paths.append(path)
    return paths
