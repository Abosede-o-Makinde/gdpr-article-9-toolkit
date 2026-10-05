"""Tests for Article 9 scoring, the DPIA flag, and Article 30 gaps."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.article9.conditions import ConditionsConfigError, load_conditions
from src.article9.engine import PROHIBITION_RULE, ConditionChecker, Finding, band_for
from src.article9.parser import load_activity

ROOT = Path(__file__).resolve().parents[1]


def _assess(name: str):
    activity = load_activity(ROOT / "sample_data" / name)
    return ConditionChecker().assess(activity)


def test_occupational_health_passes_and_still_flags_dpia() -> None:
    result = _assess("occupational_health.json")
    assert result.band == "PASS"
    assert result.score == 100
    assert result.findings == []
    assert result.condition_label == "Art. 9(2)(h) Health or social care"
    assert result.dpia.required is True
    assert result.dpia.completed is True
    assert "Article 35" in result.dpia.message
    assert all(row.status == "MET" for row in result.evidence)


def test_biometric_access_fails_without_a_condition() -> None:
    result = _assess("biometric_door_access.json")
    assert result.band == "FAIL"
    assert result.score == 0
    assert result.condition_label == ""
    prohibition = [item for item in result.findings if item.rule_id == PROHIBITION_RULE]
    assert len(prohibition) == 1
    assert prohibition[0].severity == "FAIL"
    assert "9(1)" in prohibition[0].articles_label
    assert result.dpia.completed is False


def test_membership_body_is_partial_when_retention_is_missing() -> None:
    result = _assess("membership_body.json")
    assert result.band == "PARTIAL"
    assert result.score == 90
    assert len(result.findings) == 1
    gap = result.findings[0]
    assert gap.rule_id == "A9-30"
    assert gap.severity == "PARTIAL"
    assert "time limits" in gap.title
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


def test_dpia_completion_not_recorded() -> None:
    activity = load_activity(ROOT / "sample_data" / "occupational_health.json")
    activity.dpia_completed = None
    result = ConditionChecker().assess(activity)
    assert result.dpia.required is True
    assert "not recorded" in result.dpia.message


def test_band_for_partial_only() -> None:
    finding = Finding("A9-30", "PARTIAL", "gap", ("30",), 10, "record it")
    assert band_for([finding]) == "PARTIAL"
    assert band_for([]) == "PASS"


def test_missing_conditions_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConditionsConfigError, match="not found"):
        load_conditions(tmp_path / "missing.json")
