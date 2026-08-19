"""Secure, resumable D14 scholarly citation-chasing controls.

Only public bibliographic identifiers/titles are transmitted. API credentials
are read from the environment, excluded from artifacts, and redacted from
exceptions. This module never opens PDFs or follows document links.
"""
from __future__ import annotations

import argparse
import csv
from difflib import SequenceMatcher
import hashlib
import json
import os
from pathlib import Path
import re
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SYSTEMATIC = ROOT / "gate2/output/systematic/v1.3/20260816"
D13 = SYSTEMATIC / "d13/final"
OUTPUT = SYSTEMATIC / "d14"
RESOLUTION = OUTPUT / "resolution"
ROUND1 = OUTPUT / "round1_openalex"
WORK = OUTPUT / ".resolution_work"
VERSION = "d14-citation-chasing/1.0.0"
OPENALEX = "https://api.openalex.org"
CREATED_AT = "2026-08-18T02:00:00Z"
MAX_ATTEMPTS = 4


class CitationChasingError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_title(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).split())


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    # JSON strings may lawfully contain Unicode line/paragraph separators when
    # ensure_ascii=False. splitlines() treats those code points as record
    # boundaries; JSONL is delimited only by the physical LF byte we write.
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line]


def seed_rows() -> list[dict[str, Any]]:
    matrix = _read_jsonl(D13 / "evidence_matrix.jsonl")
    if len(matrix) != 570 or len({row["family_id"] for row in matrix}) != 570:
        raise CitationChasingError("D14 seed population must be exactly 570 D13 families")
    seeds = []
    for row in sorted(matrix, key=lambda item: item["family_id"]):
        biblio = row["bibliographic_status"]
        seeds.append({
            "family_id": row["family_id"], "record_id": row["record_id"],
            "title": biblio.get("title") or "", "doi": (biblio.get("doi") or "").lower(),
            "arxiv_id": biblio.get("arxiv_id") or "", "year": biblio.get("year"),
            "source_text_sha256": row["source_text_sha256"],
        })
    return seeds


def choose_title_match(seed: dict[str, Any], results: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, float]:
    wanted = normalized_title(seed["title"])
    exact = [row for row in results if normalized_title(row.get("title") or row.get("display_name") or "") == wanted]
    if exact:
        return exact[0], "exact_normalized_title", 1.0
    scored = []
    for row in results:
        candidate = normalized_title(row.get("title") or row.get("display_name") or "")
        score = SequenceMatcher(None, wanted, candidate).ratio() if wanted and candidate else 0.0
        year = row.get("publication_year")
        if seed.get("year") and year and abs(int(seed["year"]) - int(year)) > 1:
            score -= 0.1
        scored.append((score, row))
    if scored:
        score, row = max(scored, key=lambda item: item[0])
        if score >= 0.94:
            return row, "high_similarity_title_year", score
    return None, "unresolved", max((item[0] for item in scored), default=0.0)


def _request_json(path: str, params: dict[str, str], api_key: str) -> dict[str, Any]:
    safe_params = dict(params)
    request_params = dict(params); request_params["api_key"] = api_key
    url = f"{OPENALEX}{path}?{urlencode(request_params)}"
    request = Request(url, headers={"User-Agent": "VDCM-evidence-map/1.0 (citation metadata only)"})
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == MAX_ATTEMPTS - 1:
                raise CitationChasingError(f"OpenAlex HTTP {exc.code} for redacted request path={path} params={safe_params}") from None
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            try:
                server_delay = float(retry_after) if retry_after is not None else 0.0
            except ValueError:
                server_delay = 0.0
            time.sleep(min(max(server_delay, float(2 ** attempt)), 60.0))
        except (URLError, TimeoutError) as exc:
            if attempt == MAX_ATTEMPTS - 1:
                raise CitationChasingError(f"OpenAlex transport failure for redacted request path={path}: {type(exc).__name__}") from None
            time.sleep(min(2 ** attempt, 8))
    raise CitationChasingError("unreachable request state")


def _resolve(seed: dict[str, Any], api_key: str) -> dict[str, Any]:
    record = None; basis = ""; score = 0.0; query_kind = ""
    doi = seed.get("doi") or ""
    if doi:
        try:
            record = _request_json(f"/works/{quote('https://doi.org/' + doi, safe='')}", {}, api_key)
            basis, score, query_kind = "exact_doi_endpoint", 1.0, "doi"
        except CitationChasingError:
            record = None
    if record is None:
        try:
            payload = _request_json("/works", {"search": seed["title"], "per-page": "5"}, api_key)
        except CitationChasingError:
            # A few punctuation-heavy titles are rejected by the public search
            # endpoint. Retry once with a bounded normalized-title query; if the
            # source still rejects it, retain an explicit unresolved seed rather
            # than aborting or silently changing identity criteria.
            try:
                payload = _request_json("/works", {"search": normalized_title(seed["title"])[:180], "per-page": "5"}, api_key)
                query_kind = "normalized_title_fallback"
            except CitationChasingError:
                payload = {"results": []}; query_kind = "title_rejected"
        record, basis, score = choose_title_match(seed, payload.get("results", []))
        if not query_kind: query_kind = "title"
    if record is None:
        return {**seed, "status": "unresolved", "match_basis": basis, "match_score": score,
                "query_kind": query_kind, "openalex_id": None, "cited_by_count": None,
                "referenced_work_count": None, "referenced_works": []}
    return {
        **seed, "status": "resolved", "match_basis": basis, "match_score": score,
        "query_kind": query_kind, "openalex_id": record.get("id"),
        "resolved_title": record.get("title") or record.get("display_name"),
        "resolved_doi": record.get("doi"), "publication_year": record.get("publication_year"),
        "cited_by_count": int(record.get("cited_by_count") or 0),
        "referenced_work_count": len(record.get("referenced_works") or []),
        "referenced_works": record.get("referenced_works") or [],
        "openalex_record": record,
    }


def resolve_seeds() -> dict[str, Any]:
    if RESOLUTION.exists():
        raise CitationChasingError("immutable D14 resolution already exists")
    api_key = os.environ.get("OPENALEX_API_KEY", "")
    if not api_key:
        raise CitationChasingError("OPENALEX_API_KEY is not configured")
    seeds = seed_rows(); WORK.mkdir(parents=True, exist_ok=True)
    results_dir = WORK / "records"; results_dir.mkdir(exist_ok=True)
    for index, seed in enumerate(seeds, 1):
        path = results_dir / f"{seed['family_id']}.json"
        if path.exists():
            current = json.loads(path.read_text(encoding="utf-8"))
            if current.get("family_id") != seed["family_id"] or current.get("source_text_sha256") != seed["source_text_sha256"]:
                raise CitationChasingError(f"D14 checkpoint mismatch: {seed['family_id']}")
            continue
        result = _resolve(seed, api_key)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(path)
        if index % 25 == 0:
            time.sleep(0.25)
    rows = [json.loads((results_dir / f"{seed['family_id']}.json").read_text(encoding="utf-8")) for seed in seeds]
    resolved = [row for row in rows if row["status"] == "resolved"]
    ledger = WORK / "seed_resolution.jsonl"
    ledger.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    manifest = {
        "status": "d14_seed_resolution_complete", "protocol_version": "1.3",
        "pipeline_version": VERSION, "created_at_utc": CREATED_AT,
        "provider": "OpenAlex", "seed_count": len(rows), "resolved_count": len(resolved),
        "unresolved_count": len(rows) - len(resolved),
        "total_reported_forward_citations": sum(row["cited_by_count"] for row in resolved),
        "total_backward_reference_edges": sum(row["referenced_work_count"] for row in resolved),
        "unique_backward_work_ids": len({work for row in resolved for work in row["referenced_works"]}),
        "ledger_sha256": sha256(ledger),
        "credential_handling": "OPENALEX_API_KEY read from environment only; not logged, printed, or persisted.",
        "security_boundary": "Public bibliographic metadata only; no PDFs, private content, Git operations, links, package installs, or access-control bypass.",
        "interpretation_boundary": "Resolution and citation-edge counts are not screened studies, PRISMA inclusions, or novelty evidence.",
    }
    manifest_path = WORK / "resolution_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (WORK / "resolution_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  resolution_manifest.json\n", encoding="utf-8")
    OUTPUT.mkdir(parents=True, exist_ok=True); WORK.replace(RESOLUTION)
    return manifest


def verify_resolution() -> dict[str, Any]:
    path = RESOLUTION / "resolution_manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8"))
    ledger = RESOLUTION / "seed_resolution.jsonl"; rows = _read_jsonl(ledger)
    if sha256(ledger) != manifest["ledger_sha256"] or len(rows) != manifest["seed_count"]:
        raise CitationChasingError("D14 resolution ledger mismatch")
    if len({row["family_id"] for row in rows}) != len(rows) or len(rows) != 570:
        raise CitationChasingError("D14 resolution population mismatch")
    if sum(row["status"] == "resolved" for row in rows) != manifest["resolved_count"]:
        raise CitationChasingError("D14 resolution counts mismatch")
    if (RESOLUTION / "resolution_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise CitationChasingError("D14 resolution manifest sidecar mismatch")
    return manifest


def _chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def _abstract(record: dict[str, Any]) -> str:
    inverted = record.get("abstract_inverted_index") or {}
    pairs = [(position, word) for word, positions in inverted.items() for position in positions]
    return " ".join(word for _, word in sorted(pairs))


def _normalized_record(record: dict[str, Any]) -> dict[str, Any]:
    authors = []
    for authorship in record.get("authorships") or []:
        name = (authorship.get("author") or {}).get("display_name")
        if name: authors.append(name)
    location = record.get("primary_location") or {}
    source = location.get("source") or {}
    return {
        "openalex_id": record.get("id"), "doi": (record.get("doi") or "").replace("https://doi.org/", "").lower(),
        "title": record.get("title") or record.get("display_name") or "",
        "normalized_title": normalized_title(record.get("title") or record.get("display_name") or ""),
        "publication_year": record.get("publication_year"), "publication_date": record.get("publication_date"),
        "record_type": record.get("type"), "authors": authors,
        "venue": source.get("display_name"), "url": location.get("landing_page_url"),
        "abstract": _abstract(record), "cited_by_count": int(record.get("cited_by_count") or 0),
        "referenced_works": record.get("referenced_works") or [],
    }


def _existing_indexes() -> tuple[set[str], set[str]]:
    path = SYSTEMATIC / "d06/canonical_records.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    dois = {(row.get("doi") or "").lower() for row in rows if row.get("doi")}
    titles = {row.get("normalized_title") or normalized_title(row.get("title") or "") for row in rows}
    return dois, titles


def _paged_filter(filter_value: str, api_key: str, raw_dir: Path, stem: str) -> list[dict[str, Any]]:
    cursor = "*"; page = 0; results: list[dict[str, Any]] = []
    while cursor:
        payload = _request_json("/works", {
            "filter": filter_value, "per-page": "200", "cursor": cursor,
            "select": "id,doi,title,display_name,publication_year,publication_date,type,authorships,primary_location,abstract_inverted_index,referenced_works,cited_by_count",
        }, api_key)
        raw_path = raw_dir / f"{stem}_page_{page:04d}.json"
        raw_path.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        batch = payload.get("results") or []; results.extend(batch)
        next_cursor = (payload.get("meta") or {}).get("next_cursor")
        if not batch or not next_cursor or next_cursor == cursor: break
        cursor = next_cursor; page += 1
        time.sleep(0.12)
    return results


def fetch_round1() -> dict[str, Any]:
    if ROUND1.exists(): raise CitationChasingError("immutable D14 OpenAlex round 1 exists")
    resolution = verify_resolution(); api_key = os.environ.get("OPENALEX_API_KEY", "")
    if not api_key: raise CitationChasingError("OPENALEX_API_KEY is not configured")
    seed_rows_resolved = [row for row in _read_jsonl(RESOLUTION / "seed_resolution.jsonl") if row["status"] == "resolved"]
    work = OUTPUT / ".round1_openalex_work"; raw_backward = work / "raw_backward"; raw_forward = work / "raw_forward"
    raw_backward.mkdir(parents=True, exist_ok=True); raw_forward.mkdir(parents=True, exist_ok=True)
    seed_by_openalex = {row["openalex_id"]: row["family_id"] for row in seed_rows_resolved}
    backward_ids = sorted({work_id for row in seed_rows_resolved for work_id in row["referenced_works"]})
    records: dict[str, dict[str, Any]] = {}
    for index, batch in enumerate(_chunks(backward_ids, 50)):
        marker = raw_backward / f"batch_{index:04d}.complete.json"
        if marker.exists():
            payload_rows = json.loads(marker.read_text(encoding="utf-8"))["records"]
        else:
            payload_rows = _paged_filter(f"openalex_id:{'|'.join(x.rsplit('/', 1)[-1] for x in batch)}", api_key, raw_backward, f"batch_{index:04d}")
            temporary = marker.with_suffix(".tmp")
            temporary.write_text(json.dumps({"ids": batch, "records": payload_rows}, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"); temporary.replace(marker)
        for record in payload_rows:
            if record.get("id"): records[record["id"]] = record
    forward_records: dict[str, dict[str, Any]] = {}
    for index, batch in enumerate(_chunks(sorted(seed_by_openalex), 20)):
        marker = raw_forward / f"batch_{index:04d}.complete.json"
        if marker.exists(): payload_rows = json.loads(marker.read_text(encoding="utf-8"))["records"]
        else:
            ids = "|".join(x.rsplit("/", 1)[-1] for x in batch)
            payload_rows = _paged_filter(f"cites:{ids},to_publication_date:2026-08-16", api_key, raw_forward, f"batch_{index:04d}")
            temporary = marker.with_suffix(".tmp")
            temporary.write_text(json.dumps({"seed_ids": batch, "records": payload_rows}, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"); temporary.replace(marker)
        for record in payload_rows:
            if record.get("id"): forward_records[record["id"]] = record
    records.update(forward_records)
    relationships = []
    available = set(records)
    for seed in seed_rows_resolved:
        for work_id in seed["referenced_works"]:
            relationships.append({"seed_family_id": seed["family_id"], "seed_openalex_id": seed["openalex_id"],
                                  "direction": "backward", "related_openalex_id": work_id,
                                  "metadata_retrieved": work_id in available})
    seed_ids = set(seed_by_openalex)
    for record in forward_records.values():
        for cited_seed in seed_ids.intersection(record.get("referenced_works") or []):
            relationships.append({"seed_family_id": seed_by_openalex[cited_seed], "seed_openalex_id": cited_seed,
                                  "direction": "forward", "related_openalex_id": record["id"],
                                  "metadata_retrieved": True})
    normalized = [_normalized_record(record) for _, record in sorted(records.items())]
    existing_dois, existing_titles = _existing_indexes(); new_rows = []
    for row in normalized:
        basis = "doi" if row["doi"] and row["doi"] in existing_dois else "normalized_title" if row["normalized_title"] in existing_titles else None
        row["existing_corpus_match"] = basis is not None; row["existing_match_basis"] = basis
        if basis is None: new_rows.append(row)
    candidates_path = work / "all_citation_candidates.jsonl"
    candidates_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in normalized), encoding="utf-8")
    new_path = work / "new_deduplicated_candidates.jsonl"
    new_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in new_rows), encoding="utf-8")
    relationships_path = work / "citation_relationships.jsonl"
    relationships_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in relationships), encoding="utf-8")
    manifest = {
        "status": "d14_openalex_round1_retrieved_deduplicated", "protocol_version": "1.3",
        "pipeline_version": VERSION, "created_at_utc": CREATED_AT,
        "resolved_seed_count": len(seed_rows_resolved), "unresolved_seed_count": resolution["unresolved_count"],
        "backward_edge_count": sum(row["direction"] == "backward" for row in relationships),
        "backward_metadata_missing_count": sum(row["direction"] == "backward" and not row["metadata_retrieved"] for row in relationships),
        "forward_edge_count": sum(row["direction"] == "forward" for row in relationships),
        "unique_candidate_count": len(normalized),
        "existing_corpus_candidate_count": len(normalized) - len(new_rows), "new_deduplicated_candidate_count": len(new_rows),
        "all_candidates_sha256": sha256(candidates_path), "new_candidates_sha256": sha256(new_path),
        "relationships_sha256": sha256(relationships_path),
        "credential_handling": "OPENALEX_API_KEY read from environment only; not logged, printed, or persisted.",
        "interpretation_boundary": "Citation candidates are not eligible studies or PRISMA inclusions; all new records require the frozen screening workflow.",
    }
    manifest_path = work / "round1_manifest.json"; manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (work / "round1_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  round1_manifest.json\n", encoding="utf-8")
    work.replace(ROUND1); return manifest


def verify_round1() -> dict[str, Any]:
    path = ROUND1 / "round1_manifest.json"; result = json.loads(path.read_text(encoding="utf-8"))
    checks = [("all_citation_candidates.jsonl", "all_candidates_sha256"), ("new_deduplicated_candidates.jsonl", "new_candidates_sha256"), ("citation_relationships.jsonl", "relationships_sha256")]
    for name, field in checks:
        if sha256(ROUND1 / name) != result[field]: raise CitationChasingError(f"D14 round1 hash mismatch: {name}")
    all_rows = _read_jsonl(ROUND1 / "all_citation_candidates.jsonl"); new_rows = _read_jsonl(ROUND1 / "new_deduplicated_candidates.jsonl")
    if len(all_rows) != result["unique_candidate_count"] or len(new_rows) != result["new_deduplicated_candidate_count"]:
        raise CitationChasingError("D14 round1 count mismatch")
    if len({row["openalex_id"] for row in all_rows}) != len(all_rows): raise CitationChasingError("D14 round1 duplicate OpenAlex IDs")
    if (ROUND1 / "round1_manifest.json.sha256").read_text().split()[0] != sha256(path): raise CitationChasingError("D14 round1 sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("resolve-seeds", "verify-resolution", "fetch-round1", "verify-round1")); args = parser.parse_args()
    result = resolve_seeds() if args.command == "resolve-seeds" else verify_resolution() if args.command == "verify-resolution" else fetch_round1() if args.command == "fetch-round1" else verify_round1()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
