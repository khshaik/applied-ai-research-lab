"""Append-only merge of frozen and live-discovered D14 lawful locations."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gate2.citation_chasing import CitationChasingError, sha256
from gate2.d14_fulltext_discovery import FINAL as DISCOVERY, verify as verify_discovery
from gate2.d14_fulltext_locations import FINAL as BASE, verify as verify_base

FINAL = BASE.parent / "locations_v2"
VERSION = "d14-fulltext-locations/2.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line]


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise CitationChasingError("immutable D14 location-v2 artifact exists")
    base_manifest = verify_base()
    discovery_manifest = verify_discovery()
    base = _read(BASE / "location_candidates.jsonl")
    discovered = {r["citation_family_id"]: r for r in _read(DISCOVERY / "location_discoveries.jsonl")}
    rows = []
    for item in base:
        locations = list(item["candidate_locations"])
        supplement = discovered.get(item["citation_family_id"], {})
        seen = {loc["url"] for loc in locations}
        for location in supplement.get("candidate_locations") or []:
            if location["url"] not in seen:
                seen.add(location["url"])
                locations.append(location)
        rows.append({
            "citation_family_id": item["citation_family_id"],
            "title": item["title"],
            "candidate_locations": locations,
            "location_status": "candidate_identified" if locations else "lawful_location_discovery_pending",
        })
    if len(rows) != 1017 or len({r["citation_family_id"] for r in rows}) != len(rows):
        raise CitationChasingError("location-v2 family conservation failed")
    FINAL.mkdir(parents=True)
    ledger = FINAL / "location_candidates.jsonl"
    ledger.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    counts = Counter(r["location_status"] for r in rows)
    basis = Counter(loc["basis"] for r in rows for loc in r["candidate_locations"])
    manifest = {
        "status": "d14_combined_location_resolution_complete",
        "pipeline_version": VERSION,
        "protocol_version": "1.3",
        "family_count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "location_basis_counts": dict(sorted(basis.items())),
        "base_manifest_sha256": sha256(BASE / "locations_manifest.json"),
        "discovery_manifest_sha256": sha256(DISCOVERY / "discovery_manifest.json"),
        "locations_sha256": sha256(ledger),
        "security_boundary": "Append-only local reconciliation of checksum-verified lawful location metadata; no network or PDF access.",
    }
    manifest_path = FINAL / "locations_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (FINAL / "locations_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  locations_manifest.json\n", encoding="utf-8")
    return manifest


def verify() -> dict[str, Any]:
    verify_base()
    verify_discovery()
    manifest_path = FINAL / "locations_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _read(FINAL / "location_candidates.jsonl")
    if len(rows) != manifest["family_count"] or len({r["citation_family_id"] for r in rows}) != len(rows):
        raise CitationChasingError("location-v2 population mismatch")
    if sha256(FINAL / "location_candidates.jsonl") != manifest["locations_sha256"]:
        raise CitationChasingError("location-v2 ledger checksum mismatch")
    if sha256(BASE / "locations_manifest.json") != manifest["base_manifest_sha256"] or sha256(DISCOVERY / "discovery_manifest.json") != manifest["discovery_manifest_sha256"]:
        raise CitationChasingError("location-v2 upstream binding mismatch")
    if (FINAL / "locations_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise CitationChasingError("location-v2 manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
