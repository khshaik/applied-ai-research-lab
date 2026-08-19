"""Final bounded retry for five unresolved D14 Semantic Scholar seeds."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import time
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.citation_chasing_s2 import S2Error, _relations
from gate2.citation_chasing_s2_recovery import _resolve_once
from gate2.d14_s2_recovery_supplement import FINAL as SOURCE, verify as verify_source


FINAL = OUTPUT / "round1_semantic_scholar_final_retry_v3"
WORK = OUTPUT / ".round1_semantic_scholar_final_retry_v3_work"
VERSION = "d14-s2-final-retry/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"); tmp.replace(path)


def run() -> dict[str, Any]:
    if FINAL.exists():
        raise S2Error("immutable final S2 retry exists")
    verify_source(); source_rows = _read(SOURCE / "supplement_seed_resolution.jsonl")
    unresolved = [row for row in source_rows if row["status"] == "unresolved_api_failure"]
    if len(unresolved) != 5:
        raise S2Error("final S2 retry population drift")
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""); delay = 1.5 if key else 4.0
    seed_dir = WORK / "seed_records"; relation_dir = WORK / "relations"; seed_dir.mkdir(parents=True, exist_ok=True); relation_dir.mkdir(parents=True, exist_ok=True)
    resolutions = []; consecutive = 0
    for seed in unresolved:
        path = seed_dir / f"{seed['family_id']}.json"
        if path.exists():
            row = json.loads(path.read_text(encoding="utf-8"))
            attempted_now = False
        else:
            attempted_now = True
            try:
                row = _resolve_once(seed, key)
            except S2Error as exc:
                row = {**seed, "status": "unresolved_api_failure", "match_basis": "api_failure", "s2_record": None, "error_class": type(exc).__name__}
            row["final_retry_attempt_count"] = 1; _atomic(path, row); time.sleep(delay)
        resolutions.append(row)
        if attempted_now:
            consecutive = consecutive + 1 if row["status"] == "unresolved_api_failure" else 0
        if attempted_now and consecutive >= 3:
            status = {"status": "paused_rate_limit", "population": 5, "checkpointed": len(list(seed_dir.glob("*.json"))),
                      "consecutive_failures": consecutive, "next_action": "Resume after cooldown without repeating checkpoints.",
                      "security_boundary": "Public metadata only; no secret output, Git/history, PDFs, installs, or private systems."}
            _atomic(WORK / "status.json", status); return status
    relationship_rows = []
    for seed in resolutions:
        paper_id = (seed.get("s2_record") or {}).get("paperId")
        if not paper_id:
            continue
        for kind, direction in (("references", "backward"), ("citations", "forward")):
            path = relation_dir / f"{seed['family_id']}_{direction}.json"
            if path.exists():
                envelope = json.loads(path.read_text(encoding="utf-8"))
            else:
                try:
                    envelope = {"status": "complete", "data": _relations(paper_id, kind, key)}
                except S2Error as exc:
                    envelope = {"status": "api_failure", "data": [], "error_class": type(exc).__name__}
                _atomic(path, envelope); time.sleep(delay)
            relationship_rows.append({"family_id": seed["family_id"], "paper_id": paper_id, "direction": direction,
                                      "status": envelope["status"], "response_path": str(path), "response_sha256": sha256(path),
                                      "relationship_count": len(envelope["data"])})
    resolution_path = WORK / "seed_resolution.jsonl"; relation_path = WORK / "relationship_resolution.jsonl"
    resolution_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in resolutions), encoding="utf-8")
    relation_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in relationship_rows), encoding="utf-8")
    manifest = {"status": "d14_s2_final_retry_complete", "pipeline_version": VERSION, "protocol_version": "1.3",
                "population": 5, "resolution_counts": dict(Counter(row["status"] for row in resolutions)),
                "relationship_call_count": len(relationship_rows), "relationship_api_failure_count": sum(row["status"] != "complete" for row in relationship_rows),
                "relationship_count": sum(row["relationship_count"] for row in relationship_rows), "pacing_seconds": delay,
                "source_manifest_sha256": sha256(SOURCE / "supplement_manifest.json"), "seed_resolution_sha256": sha256(resolution_path),
                "relationship_resolution_sha256": sha256(relation_path),
                "credential_handling": "Optional API key read from environment header only; never printed or persisted.",
                "security_boundary": "Public scholarly metadata only; no Git/history, PDFs, secret output, installs, or private systems."}
    manifest_path = WORK / "manifest.json"; _atomic(manifest_path, manifest)
    (WORK / "manifest.json.sha256").write_text(f"{sha256(manifest_path)}  manifest.json\n", encoding="ascii")
    WORK.replace(FINAL); return manifest


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "manifest.json"; manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256(SOURCE / "supplement_manifest.json") != manifest["source_manifest_sha256"]:
        raise S2Error("final retry source binding mismatch")
    if sha256(FINAL / "seed_resolution.jsonl") != manifest["seed_resolution_sha256"] or sha256(FINAL / "relationship_resolution.jsonl") != manifest["relationship_resolution_sha256"]:
        raise S2Error("final retry ledger mismatch")
    if len(_read(FINAL / "seed_resolution.jsonl")) != 5 or (FINAL / "manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise S2Error("final retry conservation/checksum failure")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("run", "verify")); args = parser.parse_args()
    result = run() if args.command == "run" else verify(); print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
