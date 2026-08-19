"""Prepare and validate the frozen D08 family-level screening packet."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
D06 = ROOT / "gate2/output/systematic/v1.3/20260816/d06"
D07 = ROOT / "gate2/output/systematic/v1.3/20260816/d07"
OUTPUT = ROOT / "gate2/output/systematic/v1.3/20260816/d08"
VERSION = "d08-screening-controller/1.0.0"
PREPARED_AT = "2026-08-16T09:44:00Z"
SHARD_SIZE = 100
DECISIONS = {"include", "exclude", "unclear"}
STRATA = {"peer_reviewed_scholarly", "preprint_scholarly", "grey_practitioner", "method_reference"}


class ScreeningControlError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_inputs() -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    families = [json.loads(line) for line in (D07 / "study_families.jsonl").read_text(encoding="utf-8").splitlines()]
    with (D06 / "canonical_records.csv").open(encoding="utf-8", newline="") as handle:
        reports = {row["canonical_id"]: row for row in csv.DictReader(handle)}
    return families, reports


def _stratum(row: dict[str, str]) -> str:
    candidate = row.get("evidence_stratum_candidate", "").casefold()
    record_type = row.get("record_type", "").casefold()
    venue = row.get("venue", "").casefold()
    if "preprint" in candidate or "arxiv" in venue or "ssrn" in venue:
        return "preprint_scholarly"
    if "method" in candidate:
        return "method_reference"
    if "grey" in candidate or record_type in {"dataset", "repository", "report", "posted-content"}:
        return "grey_practitioner"
    return "peer_reviewed_scholarly"


def prepare(output_dir: Path = OUTPUT) -> dict[str, Any]:
    if output_dir.exists():
        raise ScreeningControlError(f"immutable D08 packet already exists: {output_dir}")
    families, reports = _load_inputs()
    packet_rows = []
    for family in sorted(families, key=lambda row: row["family_id"]):
        representative_id = family["representative_canonical_id"]
        representative = reports[representative_id]
        member_summaries = []
        for member_id in family["member_canonical_ids"]:
            member = reports[member_id]
            member_summaries.append({
                "canonical_id": member_id,
                "title": member["title"],
                "abstract": member["abstract"],
                "authors": member["authors"],
                "published": member["published"],
                "doi": member["doi"],
                "arxiv_id": member["arxiv_id"],
                "venue": member["venue"],
                "record_type": member["record_type"],
                "url": member["url"],
            })
        packet_rows.append({
            "family_id": family["family_id"],
            "record_id": representative_id,
            "stage": "title_abstract",
            "search_families": representative["search_families"],
            "evidence_stratum_candidate": _stratum(representative),
            "member_count": family["member_count"],
            "member_reports": member_summaries,
            "frozen_criteria": {
                "include": {
                    "I1": "professional or realistically simulated software engineering/development/delivery",
                    "I2": "generative AI, LLM assistant, or agentic coding system is material, unless deliberately foundational S8 evidence",
                    "I3": "measures, models, or substantively analyzes human effort/attention/oversight, estimation/planning, lifecycle readiness, flow, or quality consequences",
                    "I4": "inspectable method, framework definition, dataset, or evidence trail is indicated",
                    "I6": "within date window or intentionally retained foundational evidence",
                },
                "exclude": {
                    "E1": "non-software domain without transferable software-engineering construct",
                    "E2": "code-generation accuracy benchmark only, without human/process/delivery implication",
                    "E3": "education-only without transferable measure or professional relevance",
                    "E4": "opinion/marketing/news without distinct traceable evidence or construct",
                    "E9": "only predicts traditional Story Points without evidence that AI changes work or estimation validity",
                    "E10": "building AI/ML products generally, not AI assistance in software delivery",
                },
                "unclear_rule": "retain as unclear when supplied title/abstract metadata cannot safely resolve inclusion; do not infer missing evidence",
            },
        })

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d08-", dir=str(output_dir.parent)))
    try:
        shards = []
        for start in range(0, len(packet_rows), SHARD_SIZE):
            rows = packet_rows[start:start + SHARD_SIZE]
            name = f"screening_packet_{start // SHARD_SIZE + 1:03d}.jsonl"
            path = staging / name
            path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
            shards.append({"path": name, "sha256": sha256(path), "row_count": len(rows),
                           "first_family_id": rows[0]["family_id"], "last_family_id": rows[-1]["family_id"]})
        manifest = {
            "status": "prepared_for_two_isolated_agent_passes",
            "protocol_version": "1.3",
            "controller_version": VERSION,
            "prepared_at_utc": PREPARED_AT,
            "input_d07_manifest_sha256": sha256(D07 / "d07_manifest.json"),
            "family_count": len(packet_rows),
            "shard_size": SHARD_SIZE,
            "shard_count": len(shards),
            "screening_unit": "candidate_study_family_with_representative_record_id",
            "prompt_a": {"path": "evidence_review/prompts/screening_agent_a_v1.1.0.md", "sha256": sha256(ROOT / "evidence_review/prompts/screening_agent_a_v1.1.0.md")},
            "prompt_b": {"path": "evidence_review/prompts/screening_agent_b_v1.1.0.md", "sha256": sha256(ROOT / "evidence_review/prompts/screening_agent_b_v1.1.0.md")},
            "isolation_contract": "Each pass receives these byte-identical shards in a distinct context and must not inspect the other pass output. Concordance is agent concordance, not human inter-rater reliability.",
            "shards": shards,
        }
        manifest_path = staging / "d08_packet_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d08_packet_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d08_packet_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_packet(output_dir: Path = OUTPUT) -> dict[str, Any]:
    manifest_path = output_dir / "d08_packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["input_d07_manifest_sha256"] != sha256(D07 / "d07_manifest.json"):
        raise ScreeningControlError("D08 packet is not bound to current D07")
    total = 0
    family_ids = []
    for shard in manifest["shards"]:
        path = output_dir / shard["path"]
        if sha256(path) != shard["sha256"]:
            raise ScreeningControlError(f"screening shard hash mismatch: {path.name}")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if len(rows) != shard["row_count"]:
            raise ScreeningControlError(f"screening shard row count mismatch: {path.name}")
        total += len(rows)
        family_ids.extend(row["family_id"] for row in rows)
    if total != manifest["family_count"] or len(family_ids) != len(set(family_ids)):
        raise ScreeningControlError("D08 packet family reconciliation failed")
    if (output_dir / "d08_packet_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ScreeningControlError("D08 packet manifest sidecar mismatch")
    return manifest


def validate_pass(pass_path: Path, pass_id: str, output_dir: Path = OUTPUT) -> dict[str, Any]:
    if pass_id not in {"pass-a", "pass-b"}:
        raise ScreeningControlError("pass_id must be pass-a or pass-b")
    manifest = verify_packet(output_dir)
    expected: dict[str, tuple[str, str]] = {}
    for shard in manifest["shards"]:
        for line in (output_dir / shard["path"]).read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            expected[row["family_id"]] = (row["record_id"], shard["sha256"])
    decisions = [json.loads(line) for line in pass_path.read_text(encoding="utf-8").splitlines()]
    seen = set()
    counts = {decision: 0 for decision in sorted(DECISIONS)}
    for row in decisions:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ScreeningControlError(f"unknown or duplicate family decision: {family_id}")
        seen.add(family_id)
        record_id, checksum = expected[family_id]
        if row.get("record_id") != record_id or row.get("input_checksum") != checksum:
            raise ScreeningControlError(f"record/checksum mismatch for {family_id}")
        if row.get("stage") != "title_abstract" or row.get("review_pass_id") != pass_id:
            raise ScreeningControlError(f"stage/pass mismatch for {family_id}")
        required_prompt = f"screening-agent-{pass_id[-1]}/1.1.0"
        if row.get("model_prompt_version") != required_prompt:
            raise ScreeningControlError(f"prompt version mismatch for {family_id}")
        if row.get("reviewer_type") != "ai_agent" or row.get("prior_screening_decisions_visible") is not False:
            raise ScreeningControlError(f"agent blindness declaration missing for {family_id}")
        if not row.get("reviewer_id") or not row.get("review_context_id") or len(row.get("independence_attestation", "")) < 30:
            raise ScreeningControlError(f"agent provenance incomplete for {family_id}")
        decision = row.get("decision")
        if decision not in DECISIONS or row.get("evidence_stratum") not in STRATA:
            raise ScreeningControlError(f"invalid decision/stratum for {family_id}")
        if not row.get("reason") or not row.get("source_locator"):
            raise ScreeningControlError(f"reason/locator missing for {family_id}")
        confidence = row.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise ScreeningControlError(f"invalid confidence for {family_id}")
        counts[decision] += 1
    if seen != set(expected):
        raise ScreeningControlError(f"screening pass incomplete: missing {len(set(expected) - seen)} families")
    return {"status": "valid_complete_agent_pass", "pass_id": pass_id, "family_count": len(seen), "decision_counts": counts, "sha256": sha256(pass_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    sub.add_parser("verify-packet")
    validate = sub.add_parser("validate-pass")
    validate.add_argument("pass_path", type=Path)
    validate.add_argument("pass_id", choices=("pass-a", "pass-b"))
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "verify-packet":
        result = verify_packet()
    else:
        result = validate_pass(args.pass_path, args.pass_id)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
