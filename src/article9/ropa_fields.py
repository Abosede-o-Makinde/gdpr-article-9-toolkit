"""Article 30 fields that must be recorded when special category data is processed."""

from __future__ import annotations

from dataclasses import dataclass

from src.models.activity import ProcessingActivity

REQUIRED_ROPA_FIELDS: tuple[tuple[str, str], ...] = (
    ("purposes_recorded", "Purposes of processing"),
    ("data_subject_categories_recorded", "Categories of data subjects"),
    (
        "personal_data_categories_recorded",
        "Categories of personal data, including special category data",
    ),
    ("recipients_recorded", "Recipients or categories of recipients"),
    ("retention_recorded", "Envisaged time limits for erasure"),
    ("security_measures_recorded", "Security measures"),
)


@dataclass(frozen=True)
class RopaGap:
    """One Article 30 field that is missing from the activity record."""

    field: str
    title: str
    remediation: str


def ropa_gaps(activity: ProcessingActivity) -> list[RopaGap]:
    """Return Article 30 gaps. A missing field does not by itself prohibit processing."""
    gaps: list[RopaGap] = []
    if not (activity.ropa_activity_id or "").strip():
        gaps.append(
            RopaGap(
                field="ropa_activity_id",
                title="Article 30 record is not identified",
                remediation="Give this activity an id in the Record of Processing Activities.",
            )
        )
    recorded = activity.ropa_fields
    for field, label in REQUIRED_ROPA_FIELDS:
        if recorded.get(field) is not True:
            gaps.append(
                RopaGap(
                    field=field,
                    title=f"Article 30 field not recorded: {label}",
                    remediation=(
                        f"Record {label.lower()} on the Article 30 record for this activity."
                    ),
                )
            )
    return gaps
