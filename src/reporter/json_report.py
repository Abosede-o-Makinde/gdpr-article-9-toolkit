"""Write an Article 9 assessment as JSON."""

from __future__ import annotations

import json
from pathlib import Path

from src.article9.engine import Assessment
from src.reporter import DISCLAIMER, prepare_output


def write_json(result: Assessment, output_path: Path) -> Path:
    """Export a machine-readable assessment."""
    target = prepare_output(output_path)
    activity = result.activity
    payload = {
        "activity_id": activity.activity_id,
        "name": activity.name,
        "organisation": activity.organisation,
        "purpose": activity.purpose,
        "special_categories": activity.special_categories,
        "claimed_condition": activity.claimed_condition,
        "condition_label": result.condition_label,
        "score": result.score,
        "band": result.band,
        "dpia_required": result.dpia.required,
        "dpia_completed": result.dpia.completed,
        "dpia_message": result.dpia.message,
        "evidence": [
            {"field": row.field, "status": row.status, "description": row.description}
            for row in result.evidence
        ],
        "finding_count": len(result.findings),
        "findings": [item.to_dict() for item in result.findings],
        "disclaimer": DISCLAIMER,
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target
