"""Conservatively consolidate candidates from newly resolved D14 seeds."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from gate2.citation_chasing import OUTPUT, normalized_title, sha256
from gate2.d14_s2_newly_resolved_relationships import FINAL as SOURCE, verify as verify_source


BASE = OUTPUT.parent
EXISTING = OUTPUT / "candidate_consolidation/candidate_families.jsonl"
D06 = BASE / "d06/canonical_records.csv"
FINAL = OUTPUT / "newly_resolved_candidate_consolidation_v2"
VERSION = "d14-new-candidate-consolidation/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    # One frozen round-1 record contains a literal newline within a JSON string.
    # Decode the append-only object stream without rewriting that source artifact.
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder(strict=False)
    rows: list[dict[str, Any]] = []
    offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset >= len(text):
            break
        row, offset = decoder.raw_decode(text, offset)
        rows.append(row)
    return rows


def _author(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    elif isinstance(value, str) and ";" in value:
        value = value.split(";", 1)[0]
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).split())


def _keys(row: dict[str, Any]) -> list[tuple[str, str]]:
    doi = (row.get("doi") or "").lower().removeprefix("https://doi.org/")
    arxiv = (row.get("arxiv_id") or "").lower()
    title = row.get("normalized_title") or normalized_title(row.get("title") or "")
    author = row.get("normalized_first_author") or _author(row.get("authors"))
    year = str(row.get("publication_year") or "")
    keys = []
    if doi:
        keys.append(("doi", doi))
    if arxiv:
        keys.append(("arxiv", arxiv))
    if title and author and year:
        keys.append(("title_author_year", f"{title}|{author}|{year}"))
    return keys


def run() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 new-candidate consolidation exists: {FINAL}")
    verify_source()
    existing_rows = _read(EXISTING)
    with D06.open(encoding="utf-8", newline="") as handle:
        d06_rows = list(csv.DictReader(handle))
    index: dict[tuple[str, str], tuple[str, str]] = {}
    for source_name, rows, id_field in (("d06", d06_rows, "canonical_id"), ("d14_round1", existing_rows, "citation_family_id")):
        for row in rows:
            for key in _keys(row):
                index.setdefault(key, (source_name, row[id_field]))

    candidates = _read(SOURCE / "candidates.jsonl")
    if len(candidates) != 54:
        raise ValueError("D14 newly resolved candidate population drift")
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    seen_new: dict[tuple[str, str], str] = {}
    for row in sorted(candidates, key=lambda value: value["s2_id"]):
        keys = _keys(row)
        matches = sorted({index[key] for key in keys if key in index})
        new_matches = sorted({seen_new[key] for key in keys if key in seen_new})
        if matches or new_matches:
            duplicates.append({
                "s2_id": row["s2_id"],
                "title": row["title"],
                "matched_existing": [{"source": source, "record_id": record_id} for source, record_id in matches],
                "matched_new_family_ids": new_matches,
                "dedup_basis": "exact DOI OR exact arXiv ID OR exact normalized title + first author + publication year",
            })
            continue
        family_id = "CITFAM-" + hashlib.sha256(f"newly-resolved-v2|{row['s2_id']}".encode()).hexdigest()[:20]
        normalized = {
            "citation_family_id": family_id,
            "occurrence_count": 1,
            "sources": ["Semantic Scholar"],
            "source_record_id": row["s2_id"],
            "title": row["title"],
            "normalized_title": row.get("normalized_title") or normalized_title(row["title"]),
            "doi": (row.get("doi") or "").lower(),
            "arxiv_id": (row.get("arxiv_id") or "").lower(),
            "publication_year": row.get("publication_year"),
            "authors": row.get("authors") or [],
            "abstract": row.get("abstract") or "",
            "venue": row.get("venue"),
            "url": row.get("url"),
            "cited_by_count": int(row.get("cited_by_count") or 0),
            "dedup_basis": "no exact match in frozen D06 or D14 round-1 candidate corpus",
            "screening_status": "pending_frozen_title_abstract_workflow",
        }
        unique.append(normalized)
        for key in keys:
            seen_new[key] = family_id

    FINAL.mkdir(parents=True)
    unique_path = FINAL / "new_unique_candidates.jsonl"
    duplicate_path = FINAL / "duplicate_candidates.jsonl"
    unique_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in unique), encoding="utf-8")
    duplicate_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in duplicates), encoding="utf-8")
    manifest = {
        "status": "d14_newly_resolved_candidates_consolidated",
        "pipeline_version": VERSION,
        "protocol_version": "1.3",
        "input_candidate_count": len(candidates),
        "new_unique_candidate_count": len(unique),
        "duplicate_candidate_count": len(duplicates),
        "source_manifest_sha256": sha256(SOURCE / "manifest.json"),
        "d06_canonical_sha256": sha256(D06),
        "existing_d14_families_sha256": sha256(EXISTING),
        "new_unique_candidates_sha256": sha256(unique_path),
        "duplicate_candidates_sha256": sha256(duplicate_path),
        "deduplication_rule": "exact DOI OR exact arXiv ID OR exact normalized title + normalized first author + publication year; no fuzzy merge",
        "interpretation_boundary": "New candidate records are not eligible studies, evidence, or novelty findings until frozen screening and lawful full-text assessment.",
    }
    manifest_path = FINAL / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (FINAL / "manifest.json.sha256").write_text(f"{sha256(manifest_path)}  manifest.json\n", encoding="ascii")
    return manifest


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for path, field in ((SOURCE / "manifest.json", "source_manifest_sha256"), (D06, "d06_canonical_sha256"), (EXISTING, "existing_d14_families_sha256"), (FINAL / "new_unique_candidates.jsonl", "new_unique_candidates_sha256"), (FINAL / "duplicate_candidates.jsonl", "duplicate_candidates_sha256")):
        if sha256(path) != manifest[field]:
            raise ValueError(f"D14 new-candidate checksum mismatch: {path.name}")
    if len(_read(FINAL / "new_unique_candidates.jsonl")) != manifest["new_unique_candidate_count"]:
        raise ValueError("D14 new unique-candidate count mismatch")
    if len(_read(FINAL / "duplicate_candidates.jsonl")) != manifest["duplicate_candidate_count"]:
        raise ValueError("D14 duplicate-candidate count mismatch")
    if manifest["new_unique_candidate_count"] + manifest["duplicate_candidate_count"] != manifest["input_candidate_count"]:
        raise ValueError("D14 new-candidate conservation failure")
    if (FINAL / "manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 new-candidate manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args()
    print(json.dumps(run() if args.command == "run" else verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
