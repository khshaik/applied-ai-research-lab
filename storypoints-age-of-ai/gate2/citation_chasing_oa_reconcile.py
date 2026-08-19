"""D14 append-only OpenAlex reconciliation for locally identified seed records."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

from gate2.citation_chasing import (
    OUTPUT, ROUND1, SYSTEMATIC, CitationChasingError, _chunks, _normalized_record,
    _paged_filter, _request_json, normalized_title, sha256, verify_round1,
)
from gate2.citation_chasing_s2 import FINAL as S2_FINAL, verify as verify_s2


FINAL = OUTPUT / "round1_openalex_local_id_reconciliation"
WORK = OUTPUT / ".round1_oa_local_id_work"
FALLBACK = S2_FINAL / "fallback_seed_resolution.jsonl"
OCCURRENCES = SYSTEMATIC / "d06/normalized_occurrences.csv"
VERSION = "d14-oa-local-id-reconciliation/1.0.0"
CUTOFF = "2026-08-16"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    # JSON strings can contain Unicode line/paragraph separators. JSONL records
    # are separated only by the physical LF byte emitted by our writers.
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line]


def _local_bindings() -> list[dict[str, Any]]:
    unresolved = [r for r in _read_jsonl(FALLBACK) if r.get("status") == "unresolved"]
    if len(unresolved) != 2:
        raise CitationChasingError("expected exactly two confirmed Semantic Scholar no-match seeds")
    with OCCURRENCES.open(encoding="utf-8", newline="") as handle:
        occurrences = list(csv.DictReader(handle))
    bindings: list[dict[str, Any]] = []
    for seed in unresolved:
        matches = [r for r in occurrences if r.get("source") == "OpenAlex" and r.get("normalized_title") == normalized_title(seed["title"])]
        ids = sorted({r.get("source_id") for r in matches if (r.get("source_id") or "").startswith("https://openalex.org/W")})
        if len(ids) != 1:
            raise CitationChasingError(f"local OpenAlex binding is not unique for {seed['family_id']}")
        bindings.append({
            "family_id": seed["family_id"], "record_id": seed["record_id"], "title": seed["title"],
            "year": seed.get("year"), "openalex_id": ids[0],
            "match_basis": "frozen_d06_exact_normalized_title_unique_openalex_occurrence",
        })
    return sorted(bindings, key=lambda r: r["family_id"])


def run() -> dict[str, Any]:
    if FINAL.exists():
        raise CitationChasingError("immutable D14 local-ID reconciliation exists")
    verify_round1(); verify_s2()
    api_key = os.environ.get("OPENALEX_API_KEY", "")
    if not api_key:
        raise CitationChasingError("OPENALEX_API_KEY is not configured")
    bindings = _local_bindings()
    WORK.mkdir(parents=True, exist_ok=True)
    raw = WORK / "raw"; raw.mkdir(exist_ok=True)
    seeds: list[dict[str, Any]] = []
    for binding in bindings:
        short_id = binding["openalex_id"].rsplit("/", 1)[-1]
        path = raw / f"{binding['family_id']}_seed.json"
        record = json.loads(path.read_text(encoding="utf-8")) if path.exists() else _request_json(f"/works/{short_id}", {}, api_key)
        if normalized_title(record.get("title") or record.get("display_name") or "") != normalized_title(binding["title"]):
            raise CitationChasingError(f"OpenAlex endpoint title mismatch for {binding['family_id']}")
        if binding.get("year") and record.get("publication_year") and int(binding["year"]) != int(record["publication_year"]):
            raise CitationChasingError(f"OpenAlex endpoint year mismatch for {binding['family_id']}")
        if not path.exists():
            path.write_text(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        seeds.append({**binding, "referenced_works": record.get("referenced_works") or [], "cited_by_count": int(record.get("cited_by_count") or 0), "raw_sha256": sha256(path)})

    related: dict[str, dict[str, Any]] = {}
    backward_ids = sorted({wid for seed in seeds for wid in seed["referenced_works"]})
    for index, batch in enumerate(_chunks(backward_ids, 50)):
        rows = _paged_filter(f"openalex_id:{'|'.join(w.rsplit('/',1)[-1] for w in batch)}", api_key, raw, f"backward_{index:04d}")
        for row in rows:
            if row.get("id"): related[row["id"]] = row
    seed_ids = {s["openalex_id"]: s["family_id"] for s in seeds}
    cached_forward = raw / "forward_page_0000.json"
    if cached_forward.exists():
        cached_payload = json.loads(cached_forward.read_text(encoding="utf-8"))
        cached_meta = cached_payload.get("meta") or {}
        if cached_meta.get("next_cursor"):
            raise CitationChasingError("incomplete cached forward pagination requires an explicit controlled resume")
        forward = cached_payload.get("results") or []
    else:
        forward = _paged_filter(
            f"cites:{'|'.join(x.rsplit('/',1)[-1] for x in sorted(seed_ids))},to_publication_date:{CUTOFF}",
            api_key, raw, "forward",
        )
    for row in forward:
        if row.get("id"): related[row["id"]] = row

    relationships: list[dict[str, Any]] = []
    available = set(related)
    for seed in seeds:
        for wid in seed["referenced_works"]:
            relationships.append({"seed_family_id":seed["family_id"],"seed_openalex_id":seed["openalex_id"],"direction":"backward","related_openalex_id":wid,"metadata_retrieved":wid in available})
    for row in forward:
        for cited in set(row.get("referenced_works") or []).intersection(seed_ids):
            relationships.append({"seed_family_id":seed_ids[cited],"seed_openalex_id":cited,"direction":"forward","related_openalex_id":row["id"],"metadata_retrieved":True})

    with (SYSTEMATIC / "d06/canonical_records.csv").open(encoding="utf-8", newline="") as handle:
        existing = list(csv.DictReader(handle))
    existing_dois = {(r.get("doi") or "").lower() for r in existing if r.get("doi")}
    existing_titles = {r.get("normalized_title") or normalized_title(r.get("title") or "") for r in existing}
    prior = _read_jsonl(ROUND1 / "all_citation_candidates.jsonl")
    prior_dois = {r.get("doi") for r in prior if r.get("doi")}; prior_titles = {r.get("normalized_title") for r in prior}
    normalized = [_normalized_record(r) for _, r in sorted(related.items())]
    new_rows=[]
    for row in normalized:
        basis = "existing_doi" if row["doi"] and row["doi"] in existing_dois else "existing_title" if row["normalized_title"] in existing_titles else "round1_doi" if row["doi"] and row["doi"] in prior_dois else "round1_title" if row["normalized_title"] in prior_titles else None
        row["duplicate_basis"] = basis
        if basis is None: new_rows.append(row)

    bindings_path=WORK/"local_bindings.jsonl"; candidates_path=WORK/"new_deduplicated_candidates.jsonl"; rel_path=WORK/"citation_relationships.jsonl"
    bindings_path.write_text("".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in seeds),encoding="utf-8")
    candidates_path.write_text("".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in new_rows),encoding="utf-8")
    rel_path.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in relationships),encoding="utf-8")
    manifest={
        "status":"d14_openalex_local_id_reconciliation_complete","protocol_version":"1.3","pipeline_version":VERSION,
        "resolved_seed_count":len(seeds),"backward_edge_count":sum(r["direction"]=="backward" for r in relationships),
        "forward_edge_count":sum(r["direction"]=="forward" for r in relationships),"unique_related_count":len(normalized),
        "new_deduplicated_candidate_count":len(new_rows),"local_bindings_sha256":sha256(bindings_path),
        "relationships_sha256":sha256(rel_path),"new_candidates_sha256":sha256(candidates_path),
        "cutoff_date":CUTOFF,"credential_handling":"OPENALEX_API_KEY read from environment only; never printed or persisted.",
        "security_boundary":"Public scholarly metadata only; no Git, PDFs, credential files, installs, private systems, or access-control bypass.",
    }
    mp=WORK/"reconciliation_manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (WORK/"reconciliation_manifest.json.sha256").write_text(f"{sha256(mp)}  reconciliation_manifest.json\n",encoding="utf-8")
    WORK.replace(FINAL); return manifest


def verify() -> dict[str, Any]:
    mp=FINAL/"reconciliation_manifest.json"; m=json.loads(mp.read_text())
    for name,key in (("local_bindings.jsonl","local_bindings_sha256"),("citation_relationships.jsonl","relationships_sha256"),("new_deduplicated_candidates.jsonl","new_candidates_sha256")):
        if sha256(FINAL/name)!=m[key]: raise CitationChasingError(f"reconciliation hash mismatch: {name}")
    if len(_read_jsonl(FINAL/"local_bindings.jsonl"))!=2: raise CitationChasingError("two-seed reconciliation conservation failed")
    if (FINAL/"reconciliation_manifest.json.sha256").read_text().split()[0]!=sha256(mp): raise CitationChasingError("reconciliation sidecar mismatch")
    return m


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("command",choices=("run","verify")); a=p.parse_args()
    print(json.dumps(run() if a.command=="run" else verify(),sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
