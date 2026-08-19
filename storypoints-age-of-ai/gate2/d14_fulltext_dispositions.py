"""Reconcile all D14 title/abstract inclusions to one full-text disposition."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_locations_v3 import FINAL as LOCATIONS, verify as verify_locations
from gate2.d14_pdf_sanitize import FULLTEXT, verify as verify_sanitization
from gate2.d14_secure_fulltext import verify_progress

INVENTORY = FULLTEXT / "retrieval_inventory.jsonl"
FINAL = FULLTEXT / "final_dispositions"
VERSION = "d14-fulltext-dispositions/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _atomic_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    tmp.replace(path)


def build() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError("immutable D14 disposition ledger exists")
    verify_locations(); retrieval_manifest = verify_progress(); sanitization_manifest = verify_sanitization()
    inventory = _read(INVENTORY)
    locations = {row["citation_family_id"]: row for row in _read(LOCATIONS / "location_candidates.jsonl")}
    retrieval = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in (FULLTEXT / "results").glob("CITFAM-*.json")}
    sanitized = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in (FULLTEXT / "sanitization_results").glob("CITFAM-*.json")}
    if len(inventory) != 1017 or len(locations) != 1017 or len(retrieval) != 661 or len(sanitized) != 344:
        raise ValueError("D14 disposition input population drift")
    rows = []
    for item in sorted(inventory, key=lambda row: row["citation_family_id"]):
        fid = item["citation_family_id"]; route_count = len(locations[fid]["candidate_locations"])
        retrieval_row = retrieval.get(fid); sanitized_row = sanitized.get(fid)
        if sanitized_row and sanitized_row["status"] == "sanitized_static_extraction_verified":
            disposition = "sanitized_static_text_available"
            text_path = str(FULLTEXT / "sanitized_text" / f"{fid}.json")
            text_sha256 = sanitized_row["text_sha256"]
        elif sanitized_row:
            disposition = "sanitization_failed"
            text_path = None; text_sha256 = None
        elif retrieval_row:
            mapping = {
                "invalid_pdf_signature": "retrieval_invalid_or_non_pdf",
                "http_failure": "retrieval_http_failure",
                "network_or_policy_failure": "retrieval_network_or_policy_failure",
            }
            disposition = mapping.get(retrieval_row["status"])
            if not disposition:
                raise ValueError(f"unreconciled retrieval state for {fid}: {retrieval_row['status']}")
            text_path = None; text_sha256 = None
        elif route_count == 0:
            disposition = "no_lawful_route_identified"
            text_path = None; text_sha256 = None
        else:
            raise ValueError(f"known D14 route lacks retrieval outcome: {fid}")
        rows.append({
            "citation_family_id": fid,
            "title": item["title"],
            "doi": item.get("doi") or "",
            "arxiv_id": item.get("arxiv_id") or "",
            "lawful_route_count": route_count,
            "fulltext_disposition": disposition,
            "sanitized_text_path": text_path,
            "sanitized_text_sha256": text_sha256,
            "eligible_for_fulltext_screening": disposition == "sanitized_static_text_available",
            "interpretation_boundary": "Availability is not eligibility, quality, novelty, or evidentiary support; unavailable reports remain in flow accounting.",
        })
    counts = Counter(row["fulltext_disposition"] for row in rows)
    expected = {
        "sanitized_static_text_available": 337,
        "sanitization_failed": 7,
        "retrieval_invalid_or_non_pdf": 269,
        "retrieval_http_failure": 39,
        "retrieval_network_or_policy_failure": 9,
        "no_lawful_route_identified": 356,
    }
    if dict(counts) != expected or sum(counts.values()) != 1017:
        raise ValueError(f"D14 disposition conservation mismatch: {dict(counts)}")
    output = FINAL / "fulltext_dispositions.jsonl"
    _atomic_jsonl(output, rows)
    manifest = {
        "status": "d14_fulltext_dispositions_complete",
        "pipeline_version": VERSION,
        "family_count": len(rows),
        "disposition_counts": dict(sorted(counts.items())),
        "screenable_fulltext_count": sum(row["eligible_for_fulltext_screening"] for row in rows),
        "conservation_pass": sum(counts.values()) == 1017,
        "locations_manifest_sha256": sha256(LOCATIONS / "locations_manifest.json"),
        "retrieval_manifest_sha256": sha256(FULLTEXT / "retrieval_progress.json"),
        "sanitization_manifest_sha256": sha256(FULLTEXT / "sanitization_manifest.json"),
        "dispositions_sha256": sha256(output),
        "security_boundary": "Local checksum reconciliation only; no network, Git/history, secrets, PDF execution, or private systems.",
    }
    path = FINAL / "disposition_manifest.json"
    _atomic_json(path, manifest)
    (FINAL / "disposition_manifest.json.sha256").write_text(f"{sha256(path)}  disposition_manifest.json\n", encoding="ascii")
    return manifest


def verify() -> dict[str, Any]:
    path = FINAL / "disposition_manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8"))
    rows = _read(FINAL / "fulltext_dispositions.jsonl")
    if len(rows) != 1017 or len({row["citation_family_id"] for row in rows}) != 1017:
        raise ValueError("D14 disposition population mismatch")
    if sha256(FINAL / "fulltext_dispositions.jsonl") != manifest["dispositions_sha256"]:
        raise ValueError("D14 disposition checksum mismatch")
    if Counter(row["fulltext_disposition"] for row in rows) != Counter(manifest["disposition_counts"]):
        raise ValueError("D14 disposition count mismatch")
    for row in rows:
        if row["eligible_for_fulltext_screening"]:
            text = Path(row["sanitized_text_path"])
            if not text.exists() or sha256(text) != row["sanitized_text_sha256"]:
                raise ValueError(f"D14 screenable text mismatch: {row['citation_family_id']}")
    if (FINAL / "disposition_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("D14 disposition sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("build", "verify")); args = parser.parse_args()
    print(json.dumps(build() if args.command == "build" else verify(), sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
