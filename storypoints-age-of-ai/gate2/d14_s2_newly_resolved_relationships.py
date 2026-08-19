"""Retrieve relationships for the two seeds resolved by D14 supplement v2."""
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
from gate2.citation_chasing_s2 import S2Error, _normalize, _relations
from gate2.d14_s2_recovery_supplement import FINAL as SEEDS, verify as verify_seeds


FINAL = OUTPUT / "round1_semantic_scholar_newly_resolved_relationships_v2"
VERSION = "d14-s2-newly-resolved-relationships/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run() -> dict[str, Any]:
    if FINAL.exists():
        raise S2Error(f"immutable newly-resolved relationship package exists: {FINAL}")
    verify_seeds()
    seeds = [row for row in _read(SEEDS / "supplement_seed_resolution.jsonl") if row.get("status") == "resolved"]
    if len(seeds) != 2:
        raise S2Error("newly resolved seed population drift")
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    delay = 1.5 if api_key else 4.0
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-new-rel-", dir=str(FINAL.parent)))
    try:
        responses = staging / "responses"
        responses.mkdir()
        relationships: list[dict[str, Any]] = []
        related: dict[str, dict[str, Any]] = {}
        calls: list[dict[str, Any]] = []
        for seed in seeds:
            paper_id = seed["s2_record"]["paperId"]
            for kind, direction, node_key in (("references", "backward", "citedPaper"), ("citations", "forward", "citingPaper")):
                try:
                    data = _relations(paper_id, kind, api_key)
                    status = "complete"
                except S2Error as exc:
                    data = []
                    status = "api_failure"
                    error_class = type(exc).__name__
                response_path = responses / f"{seed['family_id']}_{direction}.json"
                envelope = {"status": status, "data": data}
                if status != "complete":
                    envelope["error_class"] = error_class
                response_path.write_text(json.dumps(envelope, sort_keys=True) + "\n", encoding="utf-8")
                calls.append({"family_id": seed["family_id"], "seed_s2_id": paper_id, "direction": direction, "status": status, "response_sha256": sha256(response_path)})
                if status == "complete":
                    for edge in data:
                        node = edge.get(node_key) or {}
                        related_id = node.get("paperId")
                        if not related_id:
                            continue
                        related[related_id] = node
                        relationships.append({"seed_family_id": seed["family_id"], "seed_s2_id": paper_id, "direction": direction, "related_s2_id": related_id})
                time.sleep(delay)
        calls_path = staging / "call_ledger.jsonl"
        relationships_path = staging / "relationships.jsonl"
        candidates_path = staging / "candidates.jsonl"
        calls_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in calls), encoding="utf-8")
        relationships_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in relationships), encoding="utf-8")
        candidates = [_normalize(row) for _, row in sorted(related.items())]
        candidates_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates), encoding="utf-8")
        manifest = {
            "status": "d14_newly_resolved_relationships_complete",
            "pipeline_version": VERSION,
            "protocol_version": "1.3",
            "seed_supplement_manifest_sha256": sha256(SEEDS / "supplement_manifest.json"),
            "seed_count": len(seeds),
            "call_count": len(calls),
            "complete_call_count": sum(row["status"] == "complete" for row in calls),
            "api_failure_count": sum(row["status"] != "complete" for row in calls),
            "relationship_count": len(relationships),
            "unique_candidate_count": len(candidates),
            "pacing_seconds": delay,
            "call_ledger_sha256": sha256(calls_path),
            "relationships_sha256": sha256(relationships_path),
            "candidates_sha256": sha256(candidates_path),
            "credential_handling": "Optional API key read from environment header only; never printed or persisted.",
            "security_boundary": "Public scholarly metadata only; no Git/history, PDFs, secrets, installs, or private systems.",
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "manifest.json.sha256").write_text(f"{sha256(manifest_path)}  manifest.json\n", encoding="ascii")
        staging.rename(FINAL)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, field in (("call_ledger.jsonl", "call_ledger_sha256"), ("relationships.jsonl", "relationships_sha256"), ("candidates.jsonl", "candidates_sha256")):
        if sha256(FINAL / name) != manifest[field]:
            raise S2Error(f"newly-resolved relationship checksum mismatch: {name}")
    if sha256(SEEDS / "supplement_manifest.json") != manifest["seed_supplement_manifest_sha256"]:
        raise S2Error("newly-resolved relationship seed binding mismatch")
    if len(_read(FINAL / "call_ledger.jsonl")) != 4:
        raise S2Error("newly-resolved relationship call conservation failure")
    if (FINAL / "manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise S2Error("newly-resolved relationship manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args()
    print(json.dumps(run() if args.command == "run" else verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
