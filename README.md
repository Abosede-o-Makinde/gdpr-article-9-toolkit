# gdpr-article-9-toolkit

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GDPR Art. 9](https://img.shields.io/badge/GDPR-Art.%209-important)](docs/ARTICLE9_GUIDE.md)

Checks UK GDPR Article 9 processing conditions for special category data, and flags Article 35 DPIA and Article 30 ROPA gaps.

## The problem this solves

Article 9(1) prohibits processing special category data unless an Article 9(2) condition applies. Teams still start health, biometric, or political-opinion processing with the category named and the condition left blank.

**gdpr-article-9-toolkit** reads one processing activity as JSON, checks the claimed Article 9(2)(a) to (j) evidence, and exports a PASS, PARTIAL, or FAIL assessment. It runs locally. It does not call a cloud service and it does not store biometric images.

## Features

| Capability | Module | CLI mode |
| ---------- | ------ | -------- |
| Activity JSON | `parser.py` | `--input` |
| Article 9(2)(a)-(j) evidence | `engine.py` | `--mode check` |
| Evidence checklist | `engine.py` | `--mode conditions` |
| Article 35 DPIA flag | `dpia_flag.py` | every mode |
| Article 30 field check | `ropa_fields.py` | `--mode check` |
| Markdown, JSON, and PDF | `reporter/` | `--mode report` |

## Installation

```bash
pip install -r requirements.txt
python main.py --help
python main.py --version
```

## Commands

| Mode | Required flags | What you get |
| ---- | -------------- | ------------ |
| `check` | `--input activity.json` | Band, score, findings, DPIA notice |
| `conditions` | `--input activity.json` | Claimed condition and evidence status |
| `report` | `--input`, optional `--output` | Terminal output plus Markdown, JSON, and PDF |

### Examples

```bash
python main.py --mode check --input sample_data/occupational_health.json
python main.py --mode check --input sample_data/biometric_door_access.json
python main.py --mode conditions --input sample_data/membership_body.json
python main.py --mode report --input sample_data/occupational_health.json --output outputs/
```

## Worked examples

| Activity | Condition | Band | Why |
| -------- | --------- | ---- | --- |
| Occupational health screening | Art. 9(2)(h) | **PASS** | Health purpose, professional secrecy, and Article 30 fields are recorded. Article 35 is still flagged. |
| Biometric door access | none | **FAIL** | Facial recognition uniquely identifies people and no Article 9(2) condition is claimed. |
| Membership political opinions | Art. 9(2)(d) | **PARTIAL** | The not-for-profit condition is evidenced. The Article 30 retention field is not. |

```text
Activity: Occupational health screening
Condition: Art. 9(2)(h) Health or social care
Score: 100/100
Band: PASS
Findings: 0
DPIA: Article 35 requires a DPIA before this special category processing.
```

```text
Activity: Biometric door access
Condition: none
Score: 0/100
Band: FAIL
A9-01  Article 9(1) prohibits this processing until a 9(2) condition is identified
```

Pre-generated reports: [`sample_outputs/`](sample_outputs/)

The rule notes are in [docs/ARTICLE9_GUIDE.md](docs/ARTICLE9_GUIDE.md).

## GDPR coverage

| Article | Obligation | Handled by |
| ------- | ---------- | ---------- |
| Art. 9(1) | Prohibition on special category processing | FAIL when no 9(2) condition is claimed |
| Art. 9(2)(a)-(j) | Processing conditions | Evidence fields for the claimed paragraph |
| Art. 9(3) | Professional secrecy for health data | Required evidence on condition (h) |
| Art. 35 | DPIA for high-risk processing | Flag on every special category activity |
| Art. 30 | Record of processing activities | Purpose, data subjects, categories, recipients, retention, security |

Condition (g) asks for a Data Protection Act 2018 Schedule 1 condition by name. This version does not encode every Schedule 1 paragraph.

## Repository structure

```text
gdpr-article-9-toolkit/
├── main.py
├── src/article9/         # parser, conditions, engine, DPIA flag, ROPA checks
├── src/reporter/         # Markdown, JSON, and PDF
├── config/               # Article 9(1) categories and 9(2) evidence rules
├── sample_data/          # PASS, FAIL, and PARTIAL activities
├── sample_outputs/       # committed demo reports
├── docs/                 # Article 9 guide
└── tests/
```

## Limitations

- Decision-support only. A DPO still has to confirm the condition is the right one.
- Detects missing and unsatisfied evidence. It does not decide that a cited law actually authorises the processing.
- Schedule 1 is named, not fully encoded.
- Local CLI only. No live system scan and no biometric images.
- The score is this tool's method, not an ICO grade.

## Licence

MIT. This tool is decision-support only and is not legal advice.
