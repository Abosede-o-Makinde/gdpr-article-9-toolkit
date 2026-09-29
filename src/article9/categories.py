"""Load the Article 9(1) special category catalogue."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CATEGORIES_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "special_categories.json"
)


class CategoryConfigError(ValueError):
    """Raised when the special category catalogue cannot be read."""


@dataclass(frozen=True)
class SpecialCategory:
    """One category listed in UK GDPR Article 9(1)."""

    id: str
    label: str
    note: str = ""


def load_special_categories(path: Path | None = None) -> tuple[SpecialCategory, ...]:
    """Read the special category catalogue from JSON."""
    catalogue_path = path or DEFAULT_CATEGORIES_PATH
    if not catalogue_path.is_file():
        raise CategoryConfigError(f"Category catalogue not found: {catalogue_path}")

    try:
        payload = json.loads(catalogue_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise CategoryConfigError(f"Could not decode {catalogue_path} as UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CategoryConfigError(f"Invalid JSON in {catalogue_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise CategoryConfigError(f"{catalogue_path} must contain a JSON object")

    raw_categories = payload.get("categories")
    if not isinstance(raw_categories, list) or not raw_categories:
        raise CategoryConfigError(f"{catalogue_path} must list at least one category")

    categories: list[SpecialCategory] = []
    for item in raw_categories:
        if not isinstance(item, dict):
            raise CategoryConfigError(f"Each category in {catalogue_path} must be an object")
        category_id = item.get("id")
        label = item.get("label")
        note = item.get("note", "")
        if not isinstance(category_id, str) or not category_id:
            raise CategoryConfigError(f"Category id missing in {catalogue_path}")
        if not isinstance(label, str) or not label:
            raise CategoryConfigError(f"Category label missing for {category_id}")
        if not isinstance(note, str):
            raise CategoryConfigError(f"Category note for {category_id} must be a string")
        categories.append(SpecialCategory(id=category_id, label=label, note=note))

    ids = [category.id for category in categories]
    if len(ids) != len(set(ids)):
        raise CategoryConfigError(f"Duplicate special category id in {catalogue_path}")
    return tuple(categories)
