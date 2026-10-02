"""Article 35 DPIA flag for special category processing."""

from __future__ import annotations

from dataclasses import dataclass

from src.models.activity import ProcessingActivity


@dataclass(frozen=True)
class DpiaFlag:
    """A notice that an Article 35 DPIA is required. It does not change the band."""

    required: bool
    completed: bool | None
    message: str


def flag_dpia(activity: ProcessingActivity) -> DpiaFlag:
    """Special category data triggers an Article 35 DPIA."""
    if activity.dpia_completed is True:
        status = "A DPIA is recorded as completed."
    elif activity.dpia_completed is False:
        status = "No completed DPIA is recorded."
    else:
        status = "DPIA completion is not recorded."
    message = (
        "Article 35 requires a DPIA before this special category processing. "
        f"{status} This check does not generate the DPIA."
    )
    return DpiaFlag(required=True, completed=activity.dpia_completed, message=message)
