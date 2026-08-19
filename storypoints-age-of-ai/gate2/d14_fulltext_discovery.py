"""Checkpointed OpenAlex discovery of lawful OA PDF locations for D14.

Only DOI identifiers are transmitted. The API key is read from the environment
and is never printed or persisted. This controller retrieves metadata only.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from gate2.citation_chasing import CitationChasingError, OUTPUT, _request_json, sha256
from gate2.d14_fulltext_inventory import FINAL as FULLTEXT, verify as verify_inventory
from gate2.d14_fulltext_locations import FINAL as LOCATIONS, verify as verify_locations

FINAL = FULLTEXT / "openalex_location_discovery"
WORK = FULLTEXT / ".openalex_location_discovery_work"
VERSION = "d14-openalex-location-discovery/1.0.0"
BATCH_SIZE = 50


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line]


def _doi(value: str) -> str:
    out = (value or "").strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if out.startswith(prefix):
            out = out[len(prefix):]
    return out


def _https(url: str) -> bool:
    parsed = urlparse(url or "")
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password and parsed.port in (None, 443)


def eligible_locations(record: dict[str, Any]) -> list[dict[str, str]]:
    candidates = []
    named = [("best_oa_location", record.get("best_oa_location")), ("primary_location", record.get("primary_location"))]
    named.extend(("location", loc) for loc in (record.get("locations") or []))
    seen = set()
    for basis, location in named:
        location = location or {}
        url = location.get("pdf_url") or ""
        if not location.get("is_oa") or not _https(url) or url in seen:
            continue
        seen.add(url)
        candidates.append({
            "url": url,
            "basis": f"live_openalex_{basis}_oa_pdf",
            "license_status": str(location.get("license") or "openalex_is_oa"),
        })
    return candidates


def _pending() -> list[dict[str, Any]]:
    verify_inventory()
    verify_locations()
    inventory = {r["citation_family_id"]: r for r in _read(FULLTEXT / "retrieval_inventory.jsonl")}
    rows = []
    for location in _read(LOCATIONS / "location_candidates.jsonl"):
        if location["candidate_locations"]:
            continue
        item = inventory[location["citation_family_id"]]
        doi = _doi(item.get("doi") or "")
        if doi:
            rows.append({"citation_family_id": item["citation_family_id"], "doi": doi})
    return sorted(rows, key=lambda r: r["citation_family_id"])


def run(max_batches: int = 20) -> dict[str, Any]:
    if FINAL.exists():
        raise CitationChasingError("immutable D14 OpenAlex location discovery exists")
    api_key = os.environ.get("OPENALEX_API_KEY", "")
    if not api_key:
        raise CitationChasingError("OPENALEX_API_KEY is not configured")
    pending = _pending()
    WORK.mkdir(parents=True, exist_ok=True)
    raw = WORK / "raw"
    raw.mkdir(exist_ok=True)
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    attempted = min(len(batches), max_batches)
    for index, batch in enumerate(batches[:attempted]):
        path = raw / f"batch_{index:04d}.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            value = "|".join(row["doi"] for row in batch)
            payload = _request_json("/works", {"filter": f"doi:{value}", "per-page": "200"}, api_key)
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
            tmp.replace(path)
            time.sleep(0.4)

    complete = attempted == len(batches)
    records = {}
    raw_hashes = {}
    for path in sorted(raw.glob("batch_*.json")):
        raw_hashes[path.name] = sha256(path)
        for record in json.loads(path.read_text(encoding="utf-8")).get("results") or []:
            doi = _doi(record.get("doi") or "")
            if doi:
                records[doi] = record
    rows = []
    for item in pending:
        record = records.get(item["doi"])
        locations = eligible_locations(record or {})
        rows.append({
            **item,
            "openalex_id": (record or {}).get("id"),
            "metadata_status": "matched" if record else "not_returned",
            "candidate_locations": locations,
            "location_status": "candidate_identified" if locations else "no_openalex_oa_pdf_identified",
        })
    ledger = WORK / "location_discoveries.jsonl"
    ledger.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    counts = Counter(row["location_status"] for row in rows)
    manifest = {
        "status": "complete" if complete else "checkpointed_incomplete",
        "pipeline_version": VERSION,
        "protocol_version": "1.3",
        "pending_family_count": len(pending),
        "doi_query_count": len(pending),
        "batch_size": BATCH_SIZE,
        "batch_count": len(batches),
        "completed_batch_count": len(raw_hashes),
        "matched_metadata_count": sum(r["metadata_status"] == "matched" for r in rows),
        "status_counts": dict(sorted(counts.items())),
        "ledger_sha256": sha256(ledger),
        "raw_hashes": raw_hashes,
        "credential_handling": "OPENALEX_API_KEY read from environment only; never printed or persisted.",
        "security_boundary": "Public DOI metadata lookup only; no PDFs, Git/history, secrets, private systems, or access-control bypass.",
    }
    manifest_path = WORK / "discovery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (WORK / "discovery_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  discovery_manifest.json\n", encoding="utf-8")
    if complete:
        WORK.replace(FINAL)
    return manifest


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "discovery_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["status"] != "complete":
        raise CitationChasingError("location discovery is incomplete")
    if sha256(FINAL / "location_discoveries.jsonl") != manifest["ledger_sha256"]:
        raise CitationChasingError("location discovery ledger checksum mismatch")
    if {p.name: sha256(p) for p in sorted((FINAL / "raw").glob("batch_*.json"))} != manifest["raw_hashes"]:
        raise CitationChasingError("location discovery raw checksum mismatch")
    if (FINAL / "discovery_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise CitationChasingError("location discovery manifest sidecar mismatch")
    rows = _read(FINAL / "location_discoveries.jsonl")
    if len(rows) != manifest["pending_family_count"] or len({r["citation_family_id"] for r in rows}) != len(rows):
        raise CitationChasingError("location discovery population mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    parser.add_argument("--max-batches", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(run(args.max_batches) if args.command == "run" else verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
