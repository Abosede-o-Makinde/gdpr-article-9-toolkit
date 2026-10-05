# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-10-02

### Added

- CLI modes: `check`, `conditions`, `report`
- Article 9(1) category catalogue and activity parser
- Article 9(2)(a) to (j) evidence rules, including a named Schedule 1 condition for paragraph (g)
- PASS / PARTIAL / FAIL banding
- Article 35 DPIA flag that does not by itself change the band
- Article 30 field checks for special category activities
- Markdown, JSON, and PDF exporters
- Sample activities: occupational health (PASS), biometric door access (FAIL), membership body (PARTIAL)
- Docs: `ARTICLE9_GUIDE.md` and a README worked example
- GitHub Actions test pipeline (ruff, black, pytest coverage, bandit)
