"""Recompute D14 quality disputes with the validated D12 adjudication logic."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import sha256
from gate2.d12_quality_adjudicate_local import adjudicate as adjudicate_d12
from gate2.d14_quality_reconcile import FINAL


PACKET = FINAL / "adjudication_packet.jsonl"
OUTPUT = FINAL / "adjudicated_appraisals.jsonl"
AGENT_ID = "d14-quality-adjudicator-v1"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _adapt_packet(row: dict[str, Any]) -> dict[str, Any]:
    family = row["family"]
    return {
        "family": {
            "family_id": family["family_id"], "record_id": family["record_id"], "title": family["title"],
            "extracted_text_path": family["source_text_path"], "extracted_text_sha256": family["source_text_sha256"],
            "evidence_stratum_candidate": "",
        },
        "primary_appraisal": row["primary"], "cross_audit_appraisal": row["cross_audit"],
        "dispute_reasons": [row["adjudication_reason"]],
    }


def _map_nature(value: str) -> str:
    return {"self_reported": "self-reported", "mixed": "observed"}.get(value, value)


def run() -> dict[str, Any]:
    packet = _read(PACKET)
    if len(packet) != 211:
        raise ValueError("D14 quality adjudication population drift")
    rows = []
    for ordinal, source_row in enumerate(packet, 1):
        raw = adjudicate_d12(_adapt_packet(source_row), ordinal)
        rows.append({
            "family_id": raw["family_id"], "record_id": raw["record_id"], "appraiser_agent_id": AGENT_ID,
            "decision_basis": "separate_source_grounded_quality_adjudication",
            "review_context_id": f"d14-quality-adjudicator-{ordinal:04d}-{raw['source_text_sha256'][:12]}",
            "source_text_sha256": raw["source_text_sha256"], "appraisal_form": raw["appraisal_form"],
            "design_type": raw["design_type"], "evidence_nature": _map_nature(raw["data_nature"]),
            "criteria": raw["criteria_scores"], "points_awarded": raw["points_awarded"],
            "applicable_points": raw["applicable_points"], "percent": raw["percent_score"],
            "critical_flaw": raw["critical_flaw"], "critical_flaw_basis": raw["critical_flaw_basis"],
            "evidence_band": raw["evidence_band"], "overall_notes": raw["resolution_rationale"],
            "security_attestation": "Local checksum-bound static text only; no network, Git/history, environment/secrets, credentials, installs, PDF execution, embedded actions, links, or synthesis were accessed.",
        })
    tmp = OUTPUT.with_suffix(OUTPUT.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    tmp.replace(OUTPUT)
    digest = sha256(OUTPUT)
    OUTPUT.with_suffix(OUTPUT.suffix + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="ascii")
    return {"rows": len(rows), "forms": dict(Counter(row["appraisal_form"] for row in rows)), "bands": dict(Counter(row["evidence_band"] for row in rows)), "critical_flaw_count": sum(row["critical_flaw"] for row in rows), "sha256": digest}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
