"""CLI tests for check and conditions modes."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from main import cli

ROOT = Path(__file__).resolve().parents[1]
HEALTH = ROOT / "sample_data" / "occupational_health.json"
BIOMETRIC = ROOT / "sample_data" / "biometric_door_access.json"
MEMBERSHIP = ROOT / "sample_data" / "membership_body.json"


def test_check_health_is_pass() -> None:
    result = CliRunner().invoke(cli, ["--mode", "check", "--input", str(HEALTH)])
    assert result.exit_code == 0, result.output
    assert "PASS" in result.output
    assert "100/100" in result.output
    assert "Article 35" in result.output


def test_check_biometric_is_fail() -> None:
    result = CliRunner().invoke(cli, ["--mode", "check", "--input", str(BIOMETRIC)])
    assert result.exit_code == 0, result.output
    assert "FAIL" in result.output
    assert "A9-01" in result.output


def test_conditions_membership_shows_met_evidence() -> None:
    result = CliRunner().invoke(cli, ["--mode", "conditions", "--input", str(MEMBERSHIP)])
    assert result.exit_code == 0, result.output
    assert "PARTIAL" in result.output
    assert "body_aim" in result.output
    assert "MET" in result.output


def test_missing_input_fails() -> None:
    result = CliRunner().invoke(cli, ["--mode", "check", "--input", "missing.json"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_version() -> None:
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "gdpr-article-9-toolkit" in result.output
