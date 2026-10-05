"""Report writers for Article 9 assessments."""

from __future__ import annotations

import re
from pathlib import Path

DISCLAIMER = "Decision-support only. Not legal advice."
NO_GAPS = "No Article 9 condition gaps and no Article 30 field gaps."


def safe_output_stem(activity_id: str) -> str:
    """Keep report filenames inside the output directory."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", activity_id.strip())
    return cleaned or "activity"


def prepare_output(path: Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target
