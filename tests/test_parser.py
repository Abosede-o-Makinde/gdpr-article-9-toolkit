"""Tests for processing-activity JSON loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.article9.categories import CategoryConfigError, load_special_categories
from src.article9.parser import ActivityParseError, load_activity
from src.models.activity import ProcessingActivity

ARTICLE_9_CATEGORY_IDS = (
    "racial_or_ethnic_origin",
    "political_opinions",
    "religious_or_philosophical_beliefs",
    "trade_union_membership",
    "genetic_data",
    "biometric_identification",
    "health",
    "sex_life_or_sexual_orientation",
)


def _write(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _activity(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "activity_id": "OH-001",
        "name": "Occupational health screening",
        "organisation": "Example Healthcare Trust",
        "purpose": "Assess fitness for a safety-critical role",
        "special_categories": ["health"],
        "data_subjects": "employees",
        "claimed_condition": "h",
        "evidence": {"professional_secrecy": True},
        "dpia_completed": True,
        "ropa_activity_id": "PA-OH-001",
        "ropa_fields": {"purposes_recorded": True},
        "notes": "",
    }
    payload.update(overrides)
    return payload


def test_catalogue_lists_article_9_categories() -> None:
    categories = load_special_categories()
    assert tuple(category.id for category in categories) == ARTICLE_9_CATEGORY_IDS
    biometric = categories[5]
    assert biometric.id == "biometric_identification"
    assert "uniquely identify" in biometric.note


def test_load_activity_round_trip(tmp_path: Path) -> None:
    path = _write(tmp_path / "activity.json", _activity())
    activity = load_activity(path)
    assert activity.activity_id == "OH-001"
    assert activity.organisation == "Example Healthcare Trust"
    assert activity.special_categories == ["health"]
    assert activity.claimed_condition == "h"
    assert activity.evidence["professional_secrecy"] is True
    assert activity.dpia_completed is True
    assert activity.ropa_activity_id == "PA-OH-001"
    assert activity.ropa_fields["purposes_recorded"] is True


def test_empty_claimed_condition_is_allowed(tmp_path: Path) -> None:
    path = _write(tmp_path / "activity.json", _activity(claimed_condition=""))
    activity = load_activity(path)
    assert activity.claimed_condition == ""


def test_unknown_special_category_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "activity.json", _activity(special_categories=["payroll"]))
    with pytest.raises(ActivityParseError, match="Unknown special category 'payroll'"):
        load_activity(path)


def test_duplicate_special_category_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "activity.json", _activity(special_categories=["health", "health"]))
    with pytest.raises(ActivityParseError, match="Invalid processing activity"):
        load_activity(path)


def test_invalid_condition_letter_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "activity.json", _activity(claimed_condition="k"))
    with pytest.raises(ActivityParseError, match="Invalid processing activity"):
        load_activity(path)


def test_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(ActivityParseError, match="not found"):
        load_activity(missing)


def test_invalid_json_raises(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(ActivityParseError, match="Invalid JSON"):
        load_activity(broken)


def test_non_utf8_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "latin.json"
    path.write_bytes(b'{"activity_id": "\xff"}')
    with pytest.raises(ActivityParseError, match="UTF-8"):
        load_activity(path)


def test_json_array_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "array.json", [])
    with pytest.raises(ActivityParseError, match="JSON object"):
        load_activity(path)


def test_missing_required_fields_raises(tmp_path: Path) -> None:
    path = _write(tmp_path / "empty.json", {"activity_id": "OH-001"})
    with pytest.raises(ActivityParseError, match="Invalid processing activity"):
        load_activity(path)


def test_activity_id_rejects_invalid_characters() -> None:
    with pytest.raises(ValidationError):
        ProcessingActivity.model_validate(_activity(activity_id="../escape"))


def test_evidence_rejects_numbers(tmp_path: Path) -> None:
    path = _write(tmp_path / "activity.json", _activity(evidence={"count": 3}))
    with pytest.raises(ActivityParseError, match="Invalid processing activity"):
        load_activity(path)


def test_broken_category_catalogue_raises(tmp_path: Path) -> None:
    catalogue = tmp_path / "categories.json"
    catalogue.write_text("{", encoding="utf-8")
    with pytest.raises(CategoryConfigError, match="Invalid JSON"):
        load_special_categories(catalogue)
