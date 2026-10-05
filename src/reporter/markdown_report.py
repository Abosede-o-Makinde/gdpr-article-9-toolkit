"""Write an Article 9 assessment as Markdown."""

from __future__ import annotations

from pathlib import Path

from src.article9.engine import Assessment, format_score
from src.reporter import DISCLAIMER, NO_GAPS, prepare_output


def _cell(value: str) -> str:
    return value.replace("|", "/")


def write_markdown(result: Assessment, output_path: Path) -> Path:
    """Export the band, evidence, findings, and DPIA flag."""
    target = prepare_output(output_path)
    activity = result.activity
    categories = ", ".join(activity.special_categories)
    lines = [
        f"# Article 9 assessment: {activity.name}",
        "",
        f"- Activity ID: `{activity.activity_id}`",
        f"- Organisation: {activity.organisation or '-'}",
        f"- Purpose: {activity.purpose}",
        f"- Special categories: {categories}",
        f"- Claimed condition: {result.condition_label or 'none'}",
        f"- Score: **{format_score(result.score)}**",
        f"- Band: **{result.band}**",
        f"- Findings: {len(result.findings)}",
        "",
        f"**DPIA:** {result.dpia.message}",
        "",
    ]
    if activity.notes:
        lines.extend([f"**Notes:** {activity.notes}", ""])
    if result.evidence:
        lines.extend(
            [
                "## Condition evidence",
                "",
                "| Field | Status | What is required |",
                "| ----- | ------ | ---------------- |",
            ]
        )
        for row in result.evidence:
            lines.append(
                "| " + " | ".join([_cell(row.field), row.status, _cell(row.description)]) + " |"
            )
        lines.append("")
    if not result.findings:
        lines.extend([NO_GAPS, ""])
    else:
        lines.extend(
            [
                "## Findings",
                "",
                "| Rule | Severity | Articles | Issue |",
                "| ---- | -------- | -------- | ----- |",
            ]
        )
        for item in result.findings:
            lines.append(
                "| "
                + " | ".join(
                    [
                        item.rule_id,
                        item.severity,
                        _cell(item.articles_label),
                        _cell(item.title),
                    ]
                )
                + " |"
            )
        lines.extend(["", "## What to do", ""])
        for item in result.findings:
            lines.append(f"- **{item.rule_id}**: {item.remediation}")
        lines.append("")
    lines.extend(["---", DISCLAIMER, ""])
    target.write_text("\n".join(lines), encoding="utf-8")
    return target
