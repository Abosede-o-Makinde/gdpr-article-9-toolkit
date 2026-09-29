"""Tests for the Article 9(2) conditions catalogue."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.article9.conditions import (
    CONDITION_IDS,
    ConditionsConfigError,
    load_conditions,
)


def test_conditions_are_paragraphs_a_to_j() -> None:
    conditions = load_conditions()
    assert tuple(condition.id for condition in conditions) == CONDITION_IDS
    assert tuple(condition.paragraph for condition in conditions) == tuple(
        f"9(2)({letter})" for letter in CONDITION_IDS
    )


def test_each_condition_requires_evidence() -> None:
    for condition in load_conditions():
        assert condition.name
        assert condition.summary
        assert condition.required_evidence
        fields = [item.field for item in condition.required_evidence]
        assert len(fields) == len(set(fields))
        for item in condition.required_evidence:
            assert item.field_type in {"bool", "string"}
            assert item.description


def test_substantial_public_interest_names_schedule_1_only() -> None:
    substantial = next(condition for condition in load_conditions() if condition.id == "g")
    fields = {item.field for item in substantial.required_evidence}
    assert "schedule_1_condition" in fields
    assert "Schedule 1" in substantial.summary
    assert "journalism" not in {condition.id for condition in load_conditions()}


def test_health_condition_requires_professional_secrecy() -> None:
    health = next(condition for condition in load_conditions() if condition.id == "h")
    secrecy = next(
        item for item in health.required_evidence if item.field == "professional_secrecy"
    )
    assert secrecy.required is True
    assert "9(3)" in secrecy.description


def test_missing_conditions_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(ConditionsConfigError, match="not found"):
        load_conditions(missing)


def test_wrong_condition_order_raises(tmp_path: Path) -> None:
    source = Path("config/article9_conditions.json").read_text(encoding="utf-8")
    swapped = source.replace('"id": "a"', '"id": "z"', 1)
    path = tmp_path / "conditions.json"
    path.write_text(swapped, encoding="utf-8")
    with pytest.raises(ConditionsConfigError, match="a to j"):
        load_conditions(path)


def test_unknown_evidence_type_raises(tmp_path: Path) -> None:
    source = Path("config/article9_conditions.json").read_text(encoding="utf-8")
    broken = source.replace('"type": "bool"', '"type": "number"', 1)
    path = tmp_path / "conditions.json"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ConditionsConfigError, match="bool or string"):
        load_conditions(path)
