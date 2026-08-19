"""Prepare and validate two isolated passes for newly resolved D14 candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_new_candidate_consolidation import FINAL as SOURCE, verify as verify_source


FINAL = OUTPUT / "newly_resolved_candidate_screening_v2"
VERSION = "d14-new-candidate-screening/1.0.0"
DECISIONS = {"include", "exclude", "unclear"}
STRATA = {"peer_reviewed_scholarly", "preprint_scholarly", "grey_practitioner", "method_reference"}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _stratum(row: dict[str, Any]) -> str:
    venue = (row.get("venue") or "").casefold()
    url = (row.get("url") or "").casefold()
    return "preprint_scholarly" if row.get("arxiv_id") or "arxiv" in venue or "arxiv" in url else "peer_reviewed_scholarly"


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 new-candidate screening exists: {FINAL}")
    source_manifest = verify_source()
    rows = _read(SOURCE / "new_unique_candidates.jsonl")
    if len(rows) != 33:
        raise ValueError("D14 new-candidate screening population drift")
    criteria = {
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
    }
    packet = [{
        "family_id": row["citation_family_id"], "record_id": row["citation_family_id"], "stage": "title_abstract",
        "search_families": "D14_citation_chasing_round1_supplement", "evidence_stratum_candidate": _stratum(row),
        "member_count": row["occurrence_count"], "title": row["title"], "abstract": row["abstract"],
        "authors": row["authors"], "publication_year": row["publication_year"], "doi": row["doi"],
        "arxiv_id": row["arxiv_id"], "venue": row["venue"], "url": row["url"], "frozen_criteria": criteria,
    } for row in rows]
    packet.sort(key=lambda row: row["family_id"])
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-new-screening-", dir=str(FINAL.parent)))
    try:
        packet_path = staging / "screening_packet.jsonl"
        packet_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in packet), encoding="utf-8")
        manifest = {
            "status": "prepared_for_two_isolated_agent_passes", "protocol_version": "1.3", "controller_version": VERSION,
            "family_count": len(packet), "input_consolidation_manifest_sha256": sha256(SOURCE / "manifest.json"),
            "packet_sha256": sha256(packet_path), "packet_path": str(FINAL / "screening_packet.jsonl"),
            "isolation_contract": "Byte-identical packet, distinct contexts, no cross-pass visibility; concordance is agent concordance, not human inter-rater reliability.",
        }
        manifest_path = staging / "screening_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "screening_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  screening_manifest.json\n", encoding="ascii")
        staging.rename(FINAL)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_packet() -> dict[str, Any]:
    manifest_path = FINAL / "screening_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packet_path = Path(manifest["packet_path"])
    rows = _read(packet_path)
    if len(rows) != 33 or len({row["family_id"] for row in rows}) != 33 or sha256(packet_path) != manifest["packet_sha256"]:
        raise ValueError("D14 new-candidate screening packet mismatch")
    if sha256(SOURCE / "manifest.json") != manifest["input_consolidation_manifest_sha256"]:
        raise ValueError("D14 new-candidate screening source drift")
    if (FINAL / "screening_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 new-candidate screening manifest sidecar mismatch")
    return manifest


def validate_pass(path: Path, pass_id: str) -> dict[str, Any]:
    manifest = verify_packet()
    expected = {row["family_id"]: row for row in _read(Path(manifest["packet_path"]))}
    rows = _read(path)
    seen: set[str] = set()
    contexts: set[str] = set()
    counts = {value: 0 for value in sorted(DECISIONS)}
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ValueError("unknown/duplicate D14 new-candidate decision")
        seen.add(family_id)
        context = row.get("review_context_id")
        if not context or context in contexts:
            raise ValueError("D14 new-candidate review context invalid")
        contexts.add(context)
        if row.get("record_id") != expected[family_id]["record_id"] or row.get("input_checksum") != manifest["packet_sha256"]:
            raise ValueError("D14 new-candidate decision binding mismatch")
        if row.get("stage") != "title_abstract" or row.get("review_pass_id") != pass_id or row.get("prior_screening_decisions_visible") is not False:
            raise ValueError("D14 new-candidate pass/blinding mismatch")
        if row.get("model_prompt_version") != f"screening-agent-{pass_id[-1]}/1.1.0" or row.get("reviewer_type") != "ai_agent":
            raise ValueError("D14 new-candidate prompt/reviewer mismatch")
        if not row.get("reviewer_id") or len(row.get("independence_attestation", "")) < 30:
            raise ValueError("D14 new-candidate provenance incomplete")
        if row.get("decision") not in DECISIONS or row.get("evidence_stratum") not in STRATA or not row.get("reason") or not row.get("source_locator"):
            raise ValueError("D14 new-candidate decision invalid")
        if not isinstance(row.get("confidence"), (int, float)) or not 0 <= row["confidence"] <= 1:
            raise ValueError("D14 new-candidate confidence invalid")
        counts[row["decision"]] += 1
    if seen != set(expected):
        raise ValueError(f"D14 new-candidate pass incomplete: {len(set(expected) - seen)} missing")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("D14 new-candidate pass sidecar mismatch")
    return {"status": "valid_complete_agent_pass", "pass_id": pass_id, "family_count": len(rows), "decision_counts": counts, "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    sub.add_parser("verify-packet")
    validate = sub.add_parser("validate-pass")
    validate.add_argument("path", type=Path)
    validate.add_argument("pass_id", choices=("pass-a", "pass-b"))
    args = parser.parse_args()
    result = prepare() if args.command == "prepare" else verify_packet() if args.command == "verify-packet" else validate_pass(args.path, args.pass_id)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
