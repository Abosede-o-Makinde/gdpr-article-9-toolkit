"""Tests for scoring a claimed Article 9(2) condition."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.article9.conditions import ConditionsConfigError, load_conditions
from src.article9.engine import ConditionChecker, Finding, band_for
from src.article9.parser import load_activity

ROOT = Path(__file__).resolve().parents[1]


def _assess(name: str):
    activity = load_activity(ROOT / "sample_data" / name)
    return ConditionChecker().assess(activity)


def test_occupational_health_passes() -> None:
    result = _assess("occupational_health.json")
    assert result.band == "PASS"
    assert result.score == 100
    assert result.findings == []
    assert result.condition_label == "Art. 9(2)(h) Health or social care"
    assert all(row.status == "MET" for row in result.evidence)


def test_false_evidence_fails_the_condition() -> None:
    activity = load_activity(ROOT / "sample_data" / "occupational_health.json")
    activity.evidence["professional_secrecy"] = False
    result = ConditionChecker().assess(activity)
    assert result.band == "FAIL"
    titles = [item.title for item in result.findings]
    assert any("professional_secrecy" in title for title in titles)


def test_named_schedule_1_condition_can_pass() -> None:
    activity = load_activity(ROOT / "sample_data" / "occupational_health.json")
    activity.claimed_condition = "g"
    activity.special_categories = ["health"]
    activity.evidence = {
        "schedule_1_condition": "preventing or detecting unlawful acts",
        "law_cited": "DPA 2018 Schedule 1 paragraph 10",
        "suitable_safeguards": True,
        "appropriate_policy_document": True,
    }
    result = ConditionChecker().assess(activity)
    assert result.band == "PASS"
    assert "Substantial public interest" in result.condition_label


def test_empty_schedule_1_name_is_not_satisfied() -> None:
    activity = load_activity(ROOT / "sample_data" / "occupational_health.json")
    activity.claimed_condition = "g"
    activity.evidence = {
        "schedule_1_condition": "   ",
        "law_cited": "DPA 2018",
        "suitable_safeguards": True,
        "appropriate_policy_document": True,
    }
    result = ConditionChecker().assess(activity)
    assert result.band == "FAIL"
    assert any(row.status == "NOT SATISFIED" for row in result.evidence)


def test_missing_evidence_field_is_reported() -> None:
    activity = load_activity(ROOT / "sample_data" / "occupational_health.json")
    del activity.evidence["professional_secrecy"]
    result = ConditionChecker().assess(activity)
    missing = [row for row in result.evidence if row.field == "professional_secrecy"]
    assert missing[0].status == "MISSING"
    assert result.band == "FAIL"


def test_band_for_partial_only() -> None:
    finding = Finding("A9-30", "PARTIAL", "gap", ("30",), 10, "record it")
    assert band_for([finding]) == "PARTIAL"
    assert band_for([]) == "PASS"


def test_missing_conditions_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConditionsConfigError, match="not found"):
        load_conditions(tmp_path / "missing.json")
