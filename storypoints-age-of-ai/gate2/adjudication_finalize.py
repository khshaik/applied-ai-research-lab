"""Validate D09 adjudications and publish final title/abstract decisions."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.title_abstract_screening import OUTPUT as D08, ScreeningControlError, STRATA, sha256
from gate2.screening_reconcile import verify as verify_d09_packet


D09 = D08 / "d09"
VERSION = "d09-adjudication-finalize/1.0.0"
FINALIZED_AT = "2026-08-16T10:18:00Z"
EXCLUSION_CODES = {f"E{number}" for number in range(1, 11)}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def validate_adjudications(path: Path = D09 / "adjudicated_decisions.jsonl") -> dict[str, Any]:
    manifest = verify_d09_packet()
    candidates = _read(D09 / "adjudication_packet.jsonl")
    expected = {row["family"]["family_id"]: row for row in candidates}
    decisions = _read(path)
    seen, counts = set(), Counter()
    for row in decisions:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ScreeningControlError(f"unknown or duplicate adjudication: {family_id}")
        seen.add(family_id)
        source = expected[family_id]
        a, b, family = source["pass_a"], source["pass_b"], source["family"]
        if row.get("record_id") != family["record_id"] or row.get("stage") != "title_abstract":
            raise ScreeningControlError(f"adjudication record/stage mismatch: {family_id}")
        if a["input_checksum"] != b["input_checksum"] or row.get("input_checksum") != a["input_checksum"]:
            raise ScreeningControlError(f"adjudication input checksum mismatch: {family_id}")
        if row.get("adjudicator_id") in {a["reviewer_id"], b["reviewer_id"]}:
            raise ScreeningControlError(f"adjudicator identity is not separate: {family_id}")
        if row.get("review_context_id") in {a["review_context_id"], b["review_context_id"]}:
            raise ScreeningControlError(f"adjudicator context is not separate: {family_id}")
        if row.get("decision") not in {"include", "exclude"}:
            raise ScreeningControlError(f"adjudication did not resolve include/exclude: {family_id}")
        if row.get("exclusion_code") is not None and row.get("exclusion_code") not in EXCLUSION_CODES:
            raise ScreeningControlError(f"invalid adjudication exclusion code: {family_id}")
        if row.get("evidence_stratum") not in STRATA:
            raise ScreeningControlError(f"invalid adjudication stratum: {family_id}")
        if not row.get("rationale") or not row.get("source_locator") or len(row.get("control_check", "")) < 30:
            raise ScreeningControlError(f"adjudication rationale/control incomplete: {family_id}")
        counts[row["decision"]] += 1
    if seen != set(expected):
        raise ScreeningControlError(f"adjudication incomplete: missing {len(set(expected) - seen)} families")
    return {"status": "valid_complete_adjudication", "candidate_count": len(seen),
            "decision_counts": dict(sorted(counts.items())), "sha256": sha256(path),
            "input_manifest_sha256": sha256(D09 / "d08_d09_manifest.json")}


def finalize(output_dir: Path = D09 / "final") -> dict[str, Any]:
    if output_dir.exists():
        raise ScreeningControlError(f"immutable D09 final output already exists: {output_dir}")
    validation = validate_adjudications()
    consensus = _read(D09 / "consensus_decisions.jsonl")
    adjudicated = _read(D09 / "adjudicated_decisions.jsonl")
    rows = []
    for row in consensus:
        rows.append({**row, "exclusion_code": None, "adjudication_id": None})
    for row in adjudicated:
        rows.append({
            "family_id": row["family_id"], "record_id": row["record_id"],
            "final_title_abstract_decision": row["decision"],
            "decision_basis": "separate_agent_adjudication",
            "exclusion_code": row.get("exclusion_code"),
            "adjudication_id": f"ADJ-{hashlib.sha256(row['family_id'].encode()).hexdigest()[:16]}",
        })
    rows.sort(key=lambda row: row["family_id"])
    if len(rows) != 3930 or len({row["family_id"] for row in rows}) != 3930:
        raise ScreeningControlError("D09 final-decision conservation failed")
    counts = Counter(row["final_title_abstract_decision"] for row in rows)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d09-final-", dir=str(output_dir.parent)))
    try:
        decisions_path = staging / "final_title_abstract_decisions.jsonl"
        decisions_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        manifest = {
            "status": "complete",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "finalized_at_utc": FINALIZED_AT,
            "family_count": len(rows), "decision_counts": dict(sorted(counts.items())),
            "consensus_count": len(consensus), "adjudicated_count": len(adjudicated),
            "adjudication_validation": validation,
            "final_decisions_sha256": sha256(decisions_path),
            "interpretation_boundary": "Final title/abstract decisions determine lawful full-text retrieval only; they do not establish eligibility after full text, quality, novelty, or citation support.",
        }
        manifest_path = staging / "d09_final_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d09_final_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d09_final_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify(output_dir: Path = D09 / "final") -> dict[str, Any]:
    manifest_path = output_dir / "d09_final_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["adjudication_validation"] != validate_adjudications():
        raise ScreeningControlError("D09 final output no longer binds adjudications")
    decisions = _read(output_dir / "final_title_abstract_decisions.jsonl")
    if sha256(output_dir / "final_title_abstract_decisions.jsonl") != manifest["final_decisions_sha256"]:
        raise ScreeningControlError("D09 final decisions hash mismatch")
    if len(decisions) != manifest["family_count"] or Counter(row["final_title_abstract_decision"] for row in decisions) != Counter(manifest["decision_counts"]):
        raise ScreeningControlError("D09 final decision counts mismatch")
    if (output_dir / "d09_final_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ScreeningControlError("D09 final manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "finalize", "verify"))
    args = parser.parse_args()
    result = validate_adjudications() if args.command == "validate" else finalize() if args.command == "finalize" else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
