"""gdpr-article-9-toolkit CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src import __version__
from src.article9.conditions import ConditionsConfigError
from src.article9.engine import Assessment, ConditionChecker, format_score
from src.article9.parser import ActivityParseError, load_activity

console = Console()
NO_GAPS = "No Article 9 condition gaps and no Article 30 field gaps."


def _style_for(label: str) -> str:
    if label == "FAIL":
        return "red"
    if label == "PARTIAL" or label in {"MISSING", "NOT SATISFIED"}:
        return "yellow"
    return "green"


def _assess(input_path: Path) -> Assessment:
    return ConditionChecker().assess(load_activity(input_path))


def _print_summary(result: Assessment) -> None:
    activity = result.activity
    colour = _style_for(result.band)
    lines = []
    if activity.organisation:
        lines.append(f"Organisation: {activity.organisation}")
    lines.extend(
        [
            f"Activity: [bold]{activity.name}[/bold]",
            f"Activity ID: {activity.activity_id}",
            f"Special categories: {', '.join(activity.special_categories)}",
            f"Condition: {result.condition_label or 'none'}",
            f"Score: [bold]{format_score(result.score)}[/bold]",
            f"Band: [bold {colour}]{result.band}[/bold {colour}]",
            f"Findings: {len(result.findings)}",
            f"DPIA: {result.dpia.message}",
        ]
    )
    console.print(Panel("\n".join(lines), title="Article 9 assessment"))


def _print_findings(result: Assessment) -> None:
    if not result.findings:
        console.print(f"[green]{NO_GAPS}[/green]")
        return
    table = Table(title="Findings")
    table.add_column("Rule")
    table.add_column("Severity")
    table.add_column("Articles")
    table.add_column("Issue")
    for item in result.findings:
        colour = _style_for(item.severity)
        table.add_row(
            item.rule_id,
            f"[{colour}]{item.severity}[/{colour}]",
            item.articles_label,
            item.title,
        )
    console.print(table)


def _print_evidence(result: Assessment) -> None:
    if not result.evidence:
        console.print("[yellow]No Article 9(2) condition was claimed.[/yellow]")
        return
    table = Table(title="Condition evidence")
    table.add_column("Field")
    table.add_column("Status")
    table.add_column("What is required")
    for row in result.evidence:
        colour = _style_for(row.status)
        table.add_row(row.field, f"[{colour}]{row.status}[/{colour}]", row.description)
    console.print(table)


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["check", "conditions"]),
    default="check",
    show_default=True,
    help="Workflow mode to run.",
)
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(path_type=Path),
    help="JSON processing activity.",
)
@click.version_option(version=__version__, prog_name="gdpr-article-9-toolkit")
def cli(mode: str, input_path: Path) -> None:
    """Check UK GDPR Article 9 processing conditions for special category data."""
    try:
        result = _assess(input_path)
        _print_summary(result)
        if mode == "conditions":
            _print_evidence(result)
        if mode == "check":
            _print_findings(result)
    except (ActivityParseError, ConditionsConfigError, OSError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    cli()
