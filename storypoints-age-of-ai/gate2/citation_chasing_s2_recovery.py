"""Rate-aware, append-only recovery of D14 Semantic Scholar API failures.

The published fallback is immutable. This supplement retries only rows explicitly
marked ``unresolved_api_failure`` and checkpoints every seed and relationship.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any

from gate2.citation_chasing_s2 import FINAL as BASELINE, FIELDS, S2Error, _get, _match_title, _normalize, _relations
from gate2.citation_chasing import OUTPUT, sha256


FINAL = OUTPUT / "round1_semantic_scholar_recovery"
WORK = OUTPUT / ".round1_s2_recovery_work"
VERSION = "d14-s2-recovery/1.0.0"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _atomic_json(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _resolve_once(seed: dict[str, Any], api_key: str) -> dict[str, Any]:
    from urllib.parse import quote

    identifiers: list[str] = []
    if seed.get("doi"):
        identifiers.append("DOI:" + seed["doi"])
    if seed.get("arxiv_id"):
        identifiers.append("ARXIV:" + seed["arxiv_id"])
    for identifier in identifiers:
        payload = _get("/paper/" + quote(identifier, safe=":"), {"fields": FIELDS}, api_key)
        if payload.get("paperId"):
            return {**seed, "status": "resolved", "match_basis": identifier.split(":", 1)[0].lower(), "s2_record": payload}
    payload = _get("/paper/search", {"query": seed["title"], "limit": "5", "fields": FIELDS}, api_key)
    matched = _match_title(seed, payload.get("data") or [])
    return {
        **seed,
        "status": "resolved" if matched else "unresolved",
        "match_basis": "exact_normalized_title" if matched else "unresolved",
        "s2_record": matched,
    }


def run() -> dict[str, Any]:
    if FINAL.exists():
        raise S2Error("immutable D14 Semantic Scholar recovery exists")
    baseline_manifest = BASELINE / "fallback_manifest.json"
    if not baseline_manifest.exists():
        raise S2Error("verified fallback required before recovery")
    baseline_hash = sha256(baseline_manifest)
    baseline = _read_jsonl(BASELINE / "fallback_seed_resolution.jsonl")
    retry_rows = [row for row in baseline if row.get("status") == "unresolved_api_failure"]
    if not retry_rows:
        raise S2Error("no API-failure rows require recovery")

    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    delay = 1.0 if api_key else 3.0
    seed_dir = WORK / "seed_records"
    relation_dir = WORK / "relations"
    seed_dir.mkdir(parents=True, exist_ok=True)
    relation_dir.mkdir(exist_ok=True)
    recovered: list[dict[str, Any]] = []
    consecutive_api_failures = 0
    for seed in retry_rows:
        path = seed_dir / f"{seed['family_id']}.json"
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        if previous and previous.get("status") != "unresolved_api_failure":
            row = previous
        else:
            try:
                row = _resolve_once(seed, api_key)
            except S2Error:
                row = {**seed, "status": "unresolved_api_failure", "match_basis": "api_failure", "s2_record": None}
            prior_attempts = int((previous or {}).get("recovery_attempt_count", 1 if previous else 0))
            row["recovery_attempt_count"] = prior_attempts + 1
            _atomic_json(path, row)
            time.sleep(delay)
        recovered.append(row)
        if row.get("status") == "unresolved_api_failure":
            consecutive_api_failures += 1
        else:
            consecutive_api_failures = 0
        if consecutive_api_failures >= 3:
            status = {
                "status": "paused_rate_limit",
                "retry_population": len(retry_rows),
                "checkpointed_count": len(list(seed_dir.glob("*.json"))),
                "consecutive_api_failures": consecutive_api_failures,
                "next_action": "Resume after public API cooldown; completed checkpoints will not be repeated.",
                "security_boundary": "Public scholarly metadata only; no Git, PDFs, credential files, or private systems.",
            }
            _atomic_json(WORK / "recovery_status.json", status)
            return status

    relations: list[dict[str, Any]] = []
    related: dict[str, dict[str, Any]] = {}
    relation_failures: list[dict[str, str]] = []
    for seed in recovered:
        record = seed.get("s2_record") or {}
        paper_id = record.get("paperId")
        if not paper_id:
            continue
        for kind, direction, node_key in (("references", "backward", "citedPaper"), ("citations", "forward", "citingPaper")):
            path = relation_dir / f"{seed['family_id']}_{direction}.json"
            if path.exists():
                envelope = json.loads(path.read_text(encoding="utf-8"))
            else:
                try:
                    data = _relations(paper_id, kind, api_key)
                    envelope = {"status": "complete", "data": data}
                except S2Error:
                    envelope = {"status": "api_failure", "data": []}
                _atomic_json(path, envelope)
                time.sleep(delay)
            if envelope["status"] != "complete":
                relation_failures.append({"family_id": seed["family_id"], "direction": direction})
                continue
            for edge in envelope["data"]:
                node = edge.get(node_key) or {}
                related_id = node.get("paperId")
                if not related_id:
                    continue
                related[related_id] = node
                relations.append({"seed_family_id": seed["family_id"], "seed_s2_id": paper_id, "direction": direction, "related_s2_id": related_id})

    WORK.mkdir(parents=True, exist_ok=True)
    resolution_path = WORK / "recovered_seed_resolution.jsonl"
    relationship_path = WORK / "recovered_relationships.jsonl"
    candidate_path = WORK / "recovered_candidates.jsonl"
    failure_path = WORK / "relation_failures.json"
    resolution_path.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in recovered), encoding="utf-8")
    relationship_path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in relations), encoding="utf-8")
    normalized = [_normalize(row) for _, row in sorted(related.items())]
    candidate_path.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in normalized), encoding="utf-8")
    failure_path.write_text(json.dumps(relation_failures, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "status": "d14_s2_rate_aware_recovery_complete",
        "pipeline_version": VERSION,
        "protocol_version": "1.3",
        "baseline_manifest_sha256": baseline_hash,
        "retry_population": len(retry_rows),
        "recovered_count": sum(r.get("status") == "resolved" for r in recovered),
        "still_api_failure_count": sum(r.get("status") == "unresolved_api_failure" for r in recovered),
        "confirmed_unresolved_count": sum(r.get("status") == "unresolved" for r in recovered),
        "relationship_count": len(relations),
        "unique_related_count": len(normalized),
        "relation_api_failure_count": len(relation_failures),
        "pacing_seconds": delay,
        "server_retry_after_honored": True,
        "credential_handling": "Optional API key read from environment header only; never printed or persisted.",
        "security_boundary": "Public scholarly metadata only; no Git, PDFs, credentials files, package installation, or private systems.",
        "recovered_seed_resolution_sha256": sha256(resolution_path),
        "recovered_relationships_sha256": sha256(relationship_path),
        "recovered_candidates_sha256": sha256(candidate_path),
        "relation_failures_sha256": sha256(failure_path),
    }
    manifest_path = WORK / "recovery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (WORK / "recovery_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  recovery_manifest.json\n", encoding="utf-8")
    WORK.replace(FINAL)
    return manifest


def verify() -> dict[str, Any]:
    path = FINAL / "recovery_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    checks = (
        ("recovered_seed_resolution.jsonl", "recovered_seed_resolution_sha256"),
        ("recovered_relationships.jsonl", "recovered_relationships_sha256"),
        ("recovered_candidates.jsonl", "recovered_candidates_sha256"),
        ("relation_failures.json", "relation_failures_sha256"),
    )
    for name, field in checks:
        if sha256(FINAL / name) != manifest[field]:
            raise S2Error(f"D14 recovery hash mismatch: {name}")
    if sha256(BASELINE / "fallback_manifest.json") != manifest["baseline_manifest_sha256"]:
        raise S2Error("D14 recovery baseline binding failed")
    if (FINAL / "recovery_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise S2Error("D14 recovery manifest sidecar mismatch")
    rows = _read_jsonl(FINAL / "recovered_seed_resolution.jsonl")
    if len(rows) != manifest["retry_population"]:
        raise S2Error("D14 recovery population conservation failed")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args()
    print(json.dumps(run() if args.command == "run" else verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
