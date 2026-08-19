"""Retry only unresolved D14 Semantic Scholar seed and relation calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.citation_chasing_s2 import FIELDS, S2Error, _get, _match_title, _relations
from gate2.citation_chasing_s2_recovery import FINAL as BASELINE, _resolve_once, verify as verify_baseline


FINAL = OUTPUT / "round1_semantic_scholar_recovery_supplement_v2"
WORK = OUTPUT / ".round1_s2_recovery_supplement_v2_work"
VERSION = "d14-s2-recovery-supplement/2.0.0"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def run() -> dict[str, Any]:
    if FINAL.exists():
        raise S2Error(f"immutable D14 supplement exists: {FINAL}")
    baseline = verify_baseline()
    resolutions = _read_jsonl(BASELINE / "recovered_seed_resolution.jsonl")
    unresolved = [row for row in resolutions if row.get("status") == "unresolved_api_failure"]
    relation_failures = json.loads((BASELINE / "relation_failures.json").read_text(encoding="utf-8"))
    if len(unresolved) != 7 or len(relation_failures) != 2:
        raise S2Error("D14 supplement population drift")
    by_family = {row["family_id"]: row for row in resolutions}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    delay = 1.5 if api_key else 4.0
    seed_dir = WORK / "seed_records"
    relation_dir = WORK / "relations"
    seed_dir.mkdir(parents=True, exist_ok=True)
    relation_dir.mkdir(parents=True, exist_ok=True)
    resolved_rows: list[dict[str, Any]] = []
    consecutive_failures = 0

    for seed in unresolved:
        path = seed_dir / f"{seed['family_id']}.json"
        if path.exists():
            row = json.loads(path.read_text(encoding="utf-8"))
        else:
            try:
                row = _resolve_once(seed, api_key)
            except S2Error as exc:
                row = {**seed, "status": "unresolved_api_failure", "match_basis": "api_failure", "s2_record": None, "error_class": type(exc).__name__}
            row["supplement_attempt_count"] = 1
            _atomic_json(path, row)
            time.sleep(delay)
        resolved_rows.append(row)
        consecutive_failures = consecutive_failures + 1 if row.get("status") == "unresolved_api_failure" else 0
        if consecutive_failures >= 3:
            status = {
                "status": "paused_rate_limit",
                "seed_population": 7,
                "checkpointed_seed_count": len(list(seed_dir.glob("*.json"))),
                "consecutive_api_failures": consecutive_failures,
                "next_action": "Resume after API cooldown; completed checkpoints will not be repeated.",
                "security_boundary": "Public scholarly metadata only; no Git/history, PDFs, secrets, installs, or private systems.",
            }
            _atomic_json(WORK / "supplement_status.json", status)
            return status

    relation_rows: list[dict[str, Any]] = []
    for failure in relation_failures:
        seed = by_family[failure["family_id"]]
        paper_id = (seed.get("s2_record") or {}).get("paperId")
        if not paper_id:
            raise S2Error("relationship retry seed lacks frozen Semantic Scholar ID")
        direction = failure["direction"]
        kind, node_key = ("citations", "citingPaper") if direction == "forward" else ("references", "citedPaper")
        path = relation_dir / f"{seed['family_id']}_{direction}.json"
        if path.exists():
            envelope = json.loads(path.read_text(encoding="utf-8"))
        else:
            try:
                envelope = {"status": "complete", "data": _relations(paper_id, kind, api_key)}
            except S2Error as exc:
                envelope = {"status": "api_failure", "data": [], "error_class": type(exc).__name__}
            _atomic_json(path, envelope)
            time.sleep(delay)
        relation_rows.append({"family_id": seed["family_id"], "direction": direction, "paper_id": paper_id, "status": envelope["status"], "response_path": str(path), "response_sha256": sha256(path)})

    WORK.mkdir(parents=True, exist_ok=True)
    resolution_path = WORK / "supplement_seed_resolution.jsonl"
    relation_path = WORK / "supplement_relation_resolution.jsonl"
    resolution_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in resolved_rows), encoding="utf-8")
    relation_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in relation_rows), encoding="utf-8")
    manifest = {
        "status": "d14_s2_recovery_supplement_complete",
        "pipeline_version": VERSION,
        "protocol_version": "1.3",
        "baseline_manifest_sha256": sha256(BASELINE / "recovery_manifest.json"),
        "seed_population": len(unresolved),
        "seed_resolved_count": sum(row.get("status") == "resolved" for row in resolved_rows),
        "seed_confirmed_no_match_count": sum(row.get("status") == "unresolved" for row in resolved_rows),
        "seed_api_failure_count": sum(row.get("status") == "unresolved_api_failure" for row in resolved_rows),
        "relation_population": len(relation_rows),
        "relation_complete_count": sum(row["status"] == "complete" for row in relation_rows),
        "relation_api_failure_count": sum(row["status"] != "complete" for row in relation_rows),
        "pacing_seconds": delay,
        "credential_handling": "Optional API key read from environment header only; never printed or persisted.",
        "supplement_seed_resolution_sha256": sha256(resolution_path),
        "supplement_relation_resolution_sha256": sha256(relation_path),
        "security_boundary": "Public scholarly metadata only; no Git/history, PDFs, secrets, package installation, or private systems.",
    }
    manifest_path = WORK / "supplement_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (WORK / "supplement_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  supplement_manifest.json\n", encoding="ascii")
    WORK.replace(FINAL)
    return manifest


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "supplement_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256(BASELINE / "recovery_manifest.json") != manifest["baseline_manifest_sha256"]:
        raise S2Error("D14 supplement baseline binding mismatch")
    if sha256(FINAL / "supplement_seed_resolution.jsonl") != manifest["supplement_seed_resolution_sha256"]:
        raise S2Error("D14 supplement seed checksum mismatch")
    if sha256(FINAL / "supplement_relation_resolution.jsonl") != manifest["supplement_relation_resolution_sha256"]:
        raise S2Error("D14 supplement relation checksum mismatch")
    if (FINAL / "supplement_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise S2Error("D14 supplement manifest sidecar mismatch")
    if len(_read_jsonl(FINAL / "supplement_seed_resolution.jsonl")) != manifest["seed_population"]:
        raise S2Error("D14 supplement seed conservation failure")
    if len(_read_jsonl(FINAL / "supplement_relation_resolution.jsonl")) != manifest["relation_population"]:
        raise S2Error("D14 supplement relation conservation failure")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args()
    result = run() if args.command == "run" else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
