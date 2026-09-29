"""Load UK GDPR Article 9(2) processing conditions and their evidence fields."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CONDITION_IDS = tuple("abcdefghij")
EVIDENCE_TYPES = {"bool", "string"}
DEFAULT_CONDITIONS_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "article9_conditions.json"
)


class ConditionsConfigError(ValueError):
    """Raised when the Article 9(2) conditions file cannot be read."""


@dataclass(frozen=True)
class EvidenceField:
    """One piece of evidence a claimed condition must record."""

    field: str
    field_type: str
    required: bool
    description: str


@dataclass(frozen=True)
class ProcessingCondition:
    """One Article 9(2) condition, from (a) through (j)."""

    id: str
    paragraph: str
    name: str
    summary: str
    required_evidence: tuple[EvidenceField, ...]


def load_conditions(path: Path | None = None) -> tuple[ProcessingCondition, ...]:
    """Read Article 9(2)(a) to (j) and the evidence each condition asks for."""
    conditions_path = path or DEFAULT_CONDITIONS_PATH
    if not conditions_path.is_file():
        raise ConditionsConfigError(f"Conditions file not found: {conditions_path}")

    try:
        payload = json.loads(conditions_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ConditionsConfigError(f"Could not decode {conditions_path} as UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConditionsConfigError(f"Invalid JSON in {conditions_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ConditionsConfigError(f"{conditions_path} must contain a JSON object")

    raw_conditions = payload.get("conditions")
    if not isinstance(raw_conditions, list):
        raise ConditionsConfigError(f"{conditions_path} must list conditions")

    conditions = tuple(_parse_condition(item, conditions_path) for item in raw_conditions)
    ids = tuple(condition.id for condition in conditions)
    if ids != CONDITION_IDS:
        found = ", ".join(ids) or "none"
        raise ConditionsConfigError(
            f"{conditions_path} must list conditions a to j in order, found {found}"
        )
    return conditions


def _parse_condition(item: object, path: Path) -> ProcessingCondition:
    if not isinstance(item, dict):
        raise ConditionsConfigError(f"Each condition in {path} must be an object")

    condition_id = item.get("id")
    paragraph = item.get("paragraph")
    name = item.get("name")
    summary = item.get("summary")
    raw_evidence = item.get("required_evidence")
    if not isinstance(condition_id, str) or not condition_id:
        raise ConditionsConfigError(f"Condition id missing in {path}")
    for label, value in (("paragraph", paragraph), ("name", name), ("summary", summary)):
        if not isinstance(value, str) or not value:
            raise ConditionsConfigError(f"Condition {condition_id} is missing {label}")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        raise ConditionsConfigError(f"Condition {condition_id} must list required evidence")

    evidence = tuple(_parse_evidence(field, condition_id, path) for field in raw_evidence)
    field_names = [field.field for field in evidence]
    if len(field_names) != len(set(field_names)):
        raise ConditionsConfigError(f"Condition {condition_id} repeats an evidence field")
    return ProcessingCondition(
        id=condition_id,
        paragraph=paragraph,
        name=name,
        summary=summary,
        required_evidence=evidence,
    )


def _parse_evidence(item: object, condition_id: str, path: Path) -> EvidenceField:
    if not isinstance(item, dict):
        raise ConditionsConfigError(
            f"Evidence for condition {condition_id} in {path} must be an object"
        )
    field = item.get("field")
    field_type = item.get("type")
    required = item.get("required")
    description = item.get("description")
    if not isinstance(field, str) or not field:
        raise ConditionsConfigError(f"Evidence field name missing for condition {condition_id}")
    if field_type not in EVIDENCE_TYPES:
        raise ConditionsConfigError(
            f"Evidence field {field} on condition {condition_id} must be bool or string"
        )
    if not isinstance(required, bool):
        raise ConditionsConfigError(f"Evidence field {field} must set required true or false")
    if not isinstance(description, str) or not description:
        raise ConditionsConfigError(f"Evidence field {field} is missing a description")
    return EvidenceField(
        field=field,
        field_type=field_type,
        required=required,
        description=description,
    )
