"""Append-only merge of D14 v2 and Semantic Scholar explicit OA locations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_locations_v2 import FINAL as V2, verify as verify_v2
from gate2.d14_s2_fulltext_discovery import FINAL as S2, verify as verify_s2

FINAL = OUTPUT / "fulltext" / "locations_v3"
VERSION = "d14-fulltext-locations-v3/1.0.0"


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
        raise ValueError("immutable D14 location-v3 artifact exists")
    verify_v2(); verify_s2()
    base = _read(V2 / "location_candidates.jsonl")
    supplement = {row["citation_family_id"]: row for row in _read(S2 / "location_candidates.jsonl")}
    if len(base) != 1017 or len(supplement) != 582:
        raise ValueError("D14 location-v3 input population drift")
    additions = 0; rows = []
    for row in base:
        merged = list(row["candidate_locations"])
        extra = supplement.get(row["citation_family_id"], {}).get("candidate_locations", [])
        existing_urls = {item["url"] for item in merged}
        for item in extra:
            if item["url"] not in existing_urls:
                merged.append(item); existing_urls.add(item["url"]); additions += 1
        rows.append({**row, "candidate_locations": merged})
    if additions != 226:
        raise ValueError(f"D14 location-v3 expected 226 additions, observed {additions}")
    output = FINAL / "location_candidates.jsonl"
    _atomic_jsonl(output, rows)
    manifest = {
        "status": "d14_lawful_location_v3_complete",
        "pipeline_version": VERSION,
        "family_count": len(rows),
        "v2_location_family_count": sum(bool(row["candidate_locations"]) for row in base),
        "s2_added_family_count": additions,
        "location_family_count": sum(bool(row["candidate_locations"]) for row in rows),
        "no_location_family_count": sum(not row["candidate_locations"] for row in rows),
        "v2_manifest_sha256": sha256(V2 / "locations_manifest.json"),
        "s2_manifest_sha256": sha256(S2 / "discovery_manifest.json"),
        "locations_sha256": sha256(output),
        "security_boundary": "Metadata-only append; explicit OA HTTPS routes only; no PDF access, Git/history, secrets, private systems, or paywall bypass.",
    }
    path = FINAL / "locations_manifest.json"
    _atomic_json(path, manifest)
    (FINAL / "locations_manifest.json.sha256").write_text(f"{sha256(path)}  locations_manifest.json\n", encoding="ascii")
    return manifest


def verify() -> dict[str, Any]:
    path = FINAL / "locations_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    rows = _read(FINAL / "location_candidates.jsonl")
    if len(rows) != 1017 or len({row["citation_family_id"] for row in rows}) != 1017:
        raise ValueError("D14 location-v3 population mismatch")
    if sha256(FINAL / "location_candidates.jsonl") != manifest["locations_sha256"]:
        raise ValueError("D14 location-v3 checksum mismatch")
    if sum(bool(row["candidate_locations"]) for row in rows) != manifest["location_family_count"]:
        raise ValueError("D14 location-v3 count mismatch")
    if (FINAL / "locations_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("D14 location-v3 sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("build", "verify")); args = parser.parse_args()
    print(json.dumps(build() if args.command == "build" else verify(), sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
