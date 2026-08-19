"""Checkpointed Semantic Scholar OA-PDF discovery for unresolved D14 reports."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from gate2.citation_chasing import OUTPUT, sha256

FULLTEXT = OUTPUT / "fulltext"
INVENTORY = FULLTEXT / "retrieval_inventory.jsonl"
LOCATIONS = FULLTEXT / "locations_v2" / "location_candidates.jsonl"
FINAL = FULLTEXT / "s2_location_discovery"
RAW = FINAL / "raw"
VERSION = "d14-s2-fulltext-discovery/1.0.0"
BATCH_SIZE = 250
API = "https://api.semanticscholar.org/graph/v1/paper/batch"


class DiscoveryError(RuntimeError):
    pass


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
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


def _population() -> list[dict[str, Any]]:
    inventory = {row["citation_family_id"]: row for row in _read_jsonl(INVENTORY)}
    locations = _read_jsonl(LOCATIONS)
    if len(inventory) != 1017 or len(locations) != 1017:
        raise DiscoveryError("D14 full-text population drift")
    unresolved = [inventory[row["citation_family_id"]] for row in locations if not row["candidate_locations"]]
    if len(unresolved) != 582 or len({row["citation_family_id"] for row in unresolved}) != 582:
        raise DiscoveryError("D14 unresolved-location population drift")
    return unresolved


def _post(ids: list[str], api_key: str | None) -> list[Any]:
    query = urlencode({"fields": "paperId,title,externalIds,openAccessPdf,url"})
    body = json.dumps({"ids": ids}).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "VDCM-THINKAI-2026/1.0 open-metadata"}
    if api_key:
        headers["x-api-key"] = api_key
    request = Request(f"{API}?{query}", data=body, headers=headers, method="POST")
    for attempt in range(4):
        try:
            with urlopen(request, timeout=60, context=ssl.create_default_context()) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, list) or len(payload) != len(ids):
                raise DiscoveryError("Semantic Scholar batch response does not preserve input cardinality")
            return payload
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                raise
            delay = min(30, int(exc.headers.get("Retry-After") or (2 ** attempt)))
            time.sleep(delay)
        except URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise DiscoveryError("bounded Semantic Scholar retry exhausted")


def _public_oa_pdf(record: Any) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None
    value = record.get("openAccessPdf")
    if not isinstance(value, dict) or not value.get("url"):
        return None
    url = value["url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return None
    return {
        "url": url,
        "basis": "semantic_scholar_explicit_openAccessPdf",
        "license": value.get("license"),
        "status": value.get("status"),
        "paper_id": record.get("paperId"),
    }


def run() -> dict[str, Any]:
    population = _population()
    doi_rows = [row for row in population if row.get("doi")]
    batches = [doi_rows[index:index + BATCH_SIZE] for index in range(0, len(doi_rows), BATCH_SIZE)]
    RAW.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    for index, batch in enumerate(batches):
        path = RAW / f"batch_{index:03d}.json"
        identifiers = [f"DOI:{row['doi']}" for row in batch]
        if path.exists():
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if envelope.get("input_ids") != identifiers:
                raise DiscoveryError(f"checkpoint input drift: {path.name}")
            continue
        records = _post(identifiers, api_key)
        _atomic_json(path, {"input_ids": identifiers, "records": records})
        time.sleep(1)

    resolved: dict[str, dict[str, Any]] = {}
    matched = 0
    for index, batch in enumerate(batches):
        envelope = json.loads((RAW / f"batch_{index:03d}.json").read_text(encoding="utf-8"))
        if len(envelope["records"]) != len(batch):
            raise DiscoveryError("checkpoint cardinality mismatch")
        for row, record in zip(batch, envelope["records"]):
            location = _public_oa_pdf(record)
            resolved[row["citation_family_id"]] = location
            matched += location is not None

    rows = []
    for row in population:
        location = resolved.get(row["citation_family_id"])
        rows.append({
            "citation_family_id": row["citation_family_id"],
            "doi": row.get("doi") or "",
            "candidate_locations": [location] if location else [],
            "disposition": "explicit_open_pdf_found" if location else "no_explicit_open_pdf_found",
        })
    output = FINAL / "location_candidates.jsonl"
    _atomic_jsonl(output, rows)
    raw_hashes = {path.name: sha256(path) for path in sorted(RAW.glob("batch_*.json"))}
    manifest = {
        "status": "d14_s2_oa_location_discovery_complete",
        "pipeline_version": VERSION,
        "population_count": len(population),
        "doi_query_count": len(doi_rows),
        "no_doi_count": len(population) - len(doi_rows),
        "batch_count": len(batches),
        "explicit_open_pdf_count": matched,
        "unresolved_count": len(population) - matched,
        "population_sha256": hashlib.sha256("\n".join(row["citation_family_id"] for row in population).encode()).hexdigest(),
        "locations_sha256": sha256(output),
        "raw_hashes": raw_hashes,
        "credential_handling": "Optional Semantic Scholar API key read from the environment only; never printed or persisted.",
        "security_boundary": "Public scholarly metadata only; no PDF download, Git/history, private systems, paywall bypass, or secret output.",
    }
    path = FINAL / "discovery_manifest.json"
    _atomic_json(path, manifest)
    (FINAL / "discovery_manifest.json.sha256").write_text(f"{sha256(path)}  discovery_manifest.json\n", encoding="ascii")
    return manifest


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "discovery_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _read_jsonl(FINAL / "location_candidates.jsonl")
    if len(rows) != manifest["population_count"] or len({row["citation_family_id"] for row in rows}) != len(rows):
        raise DiscoveryError("discovery population mismatch")
    if sha256(FINAL / "location_candidates.jsonl") != manifest["locations_sha256"]:
        raise DiscoveryError("discovery location checksum mismatch")
    if {path.name: sha256(path) for path in sorted(RAW.glob("batch_*.json"))} != manifest["raw_hashes"]:
        raise DiscoveryError("discovery raw checksum mismatch")
    if (FINAL / "discovery_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise DiscoveryError("discovery manifest sidecar mismatch")
    if sum(bool(row["candidate_locations"]) for row in rows) != manifest["explicit_open_pdf_count"]:
        raise DiscoveryError("discovery count mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args()
    print(json.dumps(run() if args.command == "run" else verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
