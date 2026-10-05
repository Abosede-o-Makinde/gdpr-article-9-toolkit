"""Score a processing activity against UK GDPR Article 9(2) evidence."""

from __future__ import annotations

from dataclasses import dataclass

from src.article9.conditions import (
    ConditionsConfigError,
    ProcessingCondition,
    load_conditions,
)
from src.article9.dpia_flag import DpiaFlag, flag_dpia
from src.article9.ropa_fields import ropa_gaps
from src.models.activity import ProcessingActivity

PROHIBITION_RULE = "A9-01"
EVIDENCE_RULE = "A9-02"
ROPA_RULE = "A9-30"


@dataclass
class Finding:
    """One gap in the Article 9 condition or the Article 30 record."""

    rule_id: str
    severity: str
    title: str
    articles: tuple[str, ...]
    weight: int
    remediation: str

    @property
    def articles_label(self) -> str:
        return ", ".join(f"Art. {article}" for article in self.articles)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "title": self.title,
            "articles": list(self.articles),
            "weight": self.weight,
            "remediation": self.remediation,
        }


@dataclass(frozen=True)
class EvidenceRow:
    """How one required evidence field was answered."""

    field: str
    status: str
    description: str


@dataclass
class Assessment:
    """Result of checking one processing activity."""

    activity: ProcessingActivity
    findings: list[Finding]
    evidence: list[EvidenceRow]
    dpia: DpiaFlag
    score: float
    band: str
    condition_label: str


def format_score(score: float) -> str:
    return f"{score:.0f}/100" if score == int(score) else f"{score}/100"


def band_for(findings: list[Finding]) -> str:
    """FAIL if a prohibition or evidence check failed; PARTIAL if only Article 30 gaps remain."""
    if any(item.severity == "FAIL" for item in findings):
        return "FAIL"
    if findings:
        return "PARTIAL"
    return "PASS"


class ConditionChecker:
    """Apply Article 9(2)(a)-(j) evidence rules and Article 30 field checks."""

    def __init__(self, conditions: tuple[ProcessingCondition, ...] | None = None) -> None:
        loaded = conditions if conditions is not None else load_conditions()
        self.conditions = {condition.id: condition for condition in loaded}

    def assess(self, activity: ProcessingActivity) -> Assessment:
        condition = self.conditions.get(activity.claimed_condition)
        findings: list[Finding] = []
        evidence: list[EvidenceRow] = []
        label = ""
        if condition is None:
            findings.append(
                Finding(
                    rule_id=PROHIBITION_RULE,
                    severity="FAIL",
                    title=(
                        "Article 9(1) prohibits this processing "
                        "until a 9(2) condition is identified"
                    ),
                    articles=("9(1)",),
                    weight=100,
                    remediation=(
                        "Claim one Article 9(2)(a) to (j) condition and record its evidence."
                    ),
                )
            )
        else:
            label = f"Art. {condition.paragraph} {condition.name}"
            evidence = _evidence_rows(activity, condition)
            findings.extend(_evidence_findings(evidence))
        for gap in ropa_gaps(activity):
            findings.append(
                Finding(
                    rule_id=ROPA_RULE,
                    severity="PARTIAL",
                    title=gap.title,
                    articles=("30",),
                    weight=10,
                    remediation=gap.remediation,
                )
            )
        score = round(max(0.0, 100.0 - sum(item.weight for item in findings)), 1)
        return Assessment(
            activity=activity,
            findings=findings,
            evidence=evidence,
            dpia=flag_dpia(activity),
            score=score,
            band=band_for(findings),
            condition_label=label,
        )


def _evidence_rows(
    activity: ProcessingActivity, condition: ProcessingCondition
) -> list[EvidenceRow]:
    rows: list[EvidenceRow] = []
    for spec in condition.required_evidence:
        value = activity.evidence.get(spec.field)
        rows.append(EvidenceRow(spec.field, _status(spec.field_type, value), spec.description))
    return rows


def _status(field_type: str, value: object) -> str:
    if value is None:
        return "MISSING"
    if field_type == "bool":
        return "MET" if value is True else "NOT SATISFIED"
    if isinstance(value, str) and value.strip():
        return "MET"
    return "NOT SATISFIED"


def _evidence_findings(rows: list[EvidenceRow]) -> list[Finding]:
    findings: list[Finding] = []
    for row in rows:
        if row.status == "MET":
            continue
        findings.append(
            Finding(
                rule_id=EVIDENCE_RULE,
                severity="FAIL",
                title=f"Evidence {row.status.lower()}: {row.field}",
                articles=("9(2)",),
                weight=40,
                remediation=row.description,
            )
        )
    return findings


__all__ = [
    "Assessment",
    "ConditionChecker",
    "ConditionsConfigError",
    "Finding",
    "band_for",
    "format_score",
]
