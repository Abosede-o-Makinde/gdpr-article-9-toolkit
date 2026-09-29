"""Load a processing activity from a local JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from src.article9.categories import load_special_categories
from src.models.activity import ProcessingActivity


class ActivityParseError(ValueError):
    """Raised when an activity file cannot be read or validated."""


def load_activity(path: Path, categories_path: Path | None = None) -> ProcessingActivity:
    """Parse `path` into a ProcessingActivity and check category ids."""
    if not path.is_file():
        raise ActivityParseError(f"Activity file not found: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ActivityParseError(f"Could not decode {path} as UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ActivityParseError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ActivityParseError(f"{path} must contain a JSON object")

    try:
        activity = ProcessingActivity.model_validate(payload)
    except ValidationError as exc:
        raise ActivityParseError(f"Invalid processing activity in {path}: {exc}") from exc

    known = {category.id for category in load_special_categories(categories_path)}
    unknown = [category for category in activity.special_categories if category not in known]
    if unknown:
        names = ", ".join(sorted(known))
        raise ActivityParseError(
            f"Unknown special category {unknown[0]!r} in {path}. Expected one of: {names}"
        )
    return activity
