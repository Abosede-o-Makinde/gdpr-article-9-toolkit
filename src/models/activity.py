"""A processing activity checked against UK GDPR Article 9."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

ACTIVITY_ID_PATTERN = r"^[A-Za-z0-9_-]{1,50}$"
CONDITION_LETTERS = set("abcdefghij")


class ProcessingActivity(BaseModel):
    """One processing activity that may involve special category data."""

    activity_id: Annotated[str, Field(pattern=ACTIVITY_ID_PATTERN)]
    name: str = Field(min_length=1)
    organisation: str = ""
    purpose: str = Field(min_length=1)
    special_categories: list[str] = Field(min_length=1)
    data_subjects: str = ""
    claimed_condition: str = ""
    evidence: dict[str, bool | str] = Field(default_factory=dict)
    dpia_completed: bool | None = None
    ropa_activity_id: str | None = None
    ropa_fields: dict[str, bool] = Field(default_factory=dict)
    notes: str = ""

    @field_validator("claimed_condition")
    @classmethod
    def condition_letter(cls, value: str) -> str:
        if value not in CONDITION_LETTERS and value != "":
            raise ValueError("claimed_condition must be empty or a letter from a to j")
        return value

    @field_validator("special_categories")
    @classmethod
    def unique_categories(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("special_categories must not contain duplicates")
        return value
