"""Publish bibliographic metadata supplement for D14 extraction packets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_candidate_consolidation import FINAL as CANDIDATES
from gate2.d14_extraction_packet import PACKET, verify as verify_packet


FINAL = OUTPUT / "evidence_extraction/metadata_supplement"
VERSION = "d14-extraction-metadata/1.0.0"


def _stream(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8"); decoder = json.JSONDecoder(strict=False); rows = []; offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace(): offset += 1
        if offset >= len(text): break
        row, offset = decoder.raw_decode(text, offset); rows.append(row)
    return rows


def run() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError(f"immutable D14 extraction metadata exists: {FINAL}")
    manifest = verify_packet(); wanted = set()
    for partition in manifest["partitions"]:
        wanted.update(row["family_id"] for row in _stream(Path(partition["path"])))
    candidates = {row["citation_family_id"]: row for row in _stream(CANDIDATES / "candidate_families.jsonl")}
    if not wanted <= set(candidates): raise ValueError("D14 extraction metadata family missing")
    rows = []
    for family_id in sorted(wanted):
        row = candidates[family_id]
        rows.append({"family_id": family_id, "title": row["title"], "authors": row["authors"], "publication_year": row["publication_year"],
                     "venue": row["venue"], "doi": row["doi"], "arxiv_id": row["arxiv_id"], "url": row["url"], "sources": row["sources"]})
    if len(rows) != 212: raise ValueError("D14 extraction metadata count mismatch")
    FINAL.mkdir(parents=True); output = FINAL / "bibliographic_metadata.jsonl"
    output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    result = {"status": "d14_extraction_metadata_complete", "pipeline_version": VERSION, "protocol_version": "1.3", "family_count": len(rows),
              "candidate_families_sha256": sha256(CANDIDATES / "candidate_families.jsonl"), "packet_manifest_sha256": sha256(PACKET / "packet_manifest.json"),
              "metadata_sha256": sha256(output)}
    path = FINAL / "manifest.json"; path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (FINAL / "manifest.json.sha256").write_text(f"{sha256(path)}  manifest.json\n", encoding="ascii"); return result


def verify() -> dict[str, Any]:
    path = FINAL / "manifest.json"; result = json.loads(path.read_text(encoding="utf-8"))
    if sha256(FINAL / "bibliographic_metadata.jsonl") != result["metadata_sha256"] or sha256(PACKET / "packet_manifest.json") != result["packet_manifest_sha256"]:
        raise ValueError("D14 extraction metadata checksum mismatch")
    if len(_stream(FINAL / "bibliographic_metadata.jsonl")) != 212: raise ValueError("D14 extraction metadata conservation failure")
    if (FINAL / "manifest.json.sha256").read_text().split()[0] != sha256(path): raise ValueError("D14 extraction metadata sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("run", "verify")); args = parser.parse_args()
    print(json.dumps(run() if args.command == "run" else verify(), sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
