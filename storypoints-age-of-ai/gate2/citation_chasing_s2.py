"""D14 Semantic Scholar fallback for OpenAlex-unresolved seeds only."""
from __future__ import annotations

import argparse
import csv
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

from gate2.citation_chasing import OUTPUT, RESOLUTION, ROUND1, SYSTEMATIC, normalized_title, sha256, verify_resolution, verify_round1


FINAL = OUTPUT / "round1_semantic_scholar_fallback"
WORK = OUTPUT / ".round1_s2_work"
BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,externalIds,title,abstract,year,authors,venue,url,citationCount,referenceCount"
VERSION = "d14-s2-fallback/1.0.0"


class S2Error(RuntimeError): pass


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line]


def _get(path: str, params: dict[str, str], api_key: str) -> dict[str, Any]:
    url = f"{BASE}{path}?{urlencode(params)}"; headers = {"User-Agent": "VDCM-evidence-map/1.0"}
    if api_key: headers["x-api-key"] = api_key
    request = Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response: return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404: return {"_not_found": True}
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise S2Error(f"Semantic Scholar HTTP {exc.code} for redacted path={path}") from None
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            try:
                server_delay = float(retry_after) if retry_after is not None else 0.0
            except ValueError:
                server_delay = 0.0
            time.sleep(min(max(server_delay, float(2 ** attempt)), 60.0))
        except (URLError, TimeoutError) as exc:
            if attempt == 2: raise S2Error(f"Semantic Scholar transport failure: {type(exc).__name__}") from None
            time.sleep(min(2 ** attempt, 12))
    raise S2Error("unreachable request state")


def _match_title(seed: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    wanted = normalized_title(seed["title"])
    exact = [row for row in rows if normalized_title(row.get("title") or "") == wanted]
    return exact[0] if exact else None


def _resolve(seed: dict[str, Any], api_key: str) -> dict[str, Any]:
    identifiers = []
    if seed.get("doi"): identifiers.append("DOI:" + seed["doi"])
    if seed.get("arxiv_id"): identifiers.append("ARXIV:" + seed["arxiv_id"])
    for identifier in identifiers:
        payload = _get("/paper/" + quote(identifier, safe=":"), {"fields": FIELDS}, api_key)
        if payload.get("paperId"): return {**seed, "status": "resolved", "match_basis": identifier.split(":", 1)[0].lower(), "s2_record": payload}
    payload = _get("/paper/search", {"query": seed["title"], "limit": "5", "fields": FIELDS}, api_key)
    matched = _match_title(seed, payload.get("data") or [])
    return {**seed, "status": "resolved" if matched else "unresolved", "match_basis": "exact_normalized_title" if matched else "unresolved", "s2_record": matched}


def _relations(paper_id: str, kind: str, api_key: str) -> list[dict[str, Any]]:
    offset = 0; results = []
    while True:
        payload = _get(f"/paper/{quote(paper_id, safe='')}/{kind}", {"fields": FIELDS, "limit": "1000", "offset": str(offset)}, api_key)
        data = payload.get("data") or []; results.extend(data)
        if not data or offset + len(data) >= int(payload.get("total") or len(results)): break
        offset += len(data); time.sleep(0.4 if api_key else 1.1)
    return results


def _normalize(record: dict[str, Any]) -> dict[str, Any]:
    external = record.get("externalIds") or {}
    return {"s2_id": record.get("paperId"), "doi": (external.get("DOI") or "").lower(), "arxiv_id": external.get("ArXiv"),
            "title": record.get("title") or "", "normalized_title": normalized_title(record.get("title") or ""),
            "publication_year": record.get("year"), "authors": [row.get("name") for row in record.get("authors") or [] if row.get("name")],
            "venue": record.get("venue"), "url": record.get("url"), "abstract": record.get("abstract") or "",
            "cited_by_count": int(record.get("citationCount") or 0)}


def run() -> dict[str, Any]:
    if FINAL.exists(): raise S2Error("immutable D14 Semantic Scholar fallback exists")
    verify_resolution(); oa = verify_round1(); api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    unresolved = [row for row in _read(RESOLUTION / "seed_resolution.jsonl") if row["status"] == "unresolved"]
    if len(unresolved) != 58: raise S2Error("D14 fallback population changed")
    records_dir = WORK / "seed_records"; relation_dir = WORK / "relations"; records_dir.mkdir(parents=True, exist_ok=True); relation_dir.mkdir(exist_ok=True)
    resolutions = []
    for seed in unresolved:
        path = records_dir / f"{seed['family_id']}.json"
        if path.exists(): result = json.loads(path.read_text(encoding="utf-8"))
        else:
            try: result = _resolve(seed, api_key)
            except S2Error: result = {**seed, "status": "unresolved_api_failure", "match_basis": "api_failure", "s2_record": None}
            tmp = path.with_suffix(".tmp"); tmp.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"); tmp.replace(path)
            time.sleep(0.4 if api_key else 1.1)
        resolutions.append(result)
    related: dict[str, dict[str, Any]] = {}; relationships = []
    for seed in resolutions:
        record = seed.get("s2_record") or {}; paper_id = record.get("paperId")
        if not paper_id: continue
        for kind, direction, node_key in (("references", "backward", "citedPaper"), ("citations", "forward", "citingPaper")):
            path = relation_dir / f"{seed['family_id']}_{direction}.json"
            if path.exists(): data = json.loads(path.read_text(encoding="utf-8"))
            else:
                try: data = _relations(paper_id, kind, api_key)
                except S2Error: data = []
                tmp = path.with_suffix(".tmp"); tmp.write_text(json.dumps(data, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"); tmp.replace(path)
                time.sleep(0.4 if api_key else 1.1)
            for edge in data:
                node = edge.get(node_key) or {}; rid = node.get("paperId")
                if not rid: continue
                related[rid] = node; relationships.append({"seed_family_id": seed["family_id"], "seed_s2_id": paper_id, "direction": direction, "related_s2_id": rid})
    with (SYSTEMATIC / "d06/canonical_records.csv").open(encoding="utf-8", newline="") as handle: existing = list(csv.DictReader(handle))
    existing_dois = {(row.get("doi") or "").lower() for row in existing if row.get("doi")}; existing_titles = {row["normalized_title"] for row in existing}
    oa_rows = _read(ROUND1 / "all_citation_candidates.jsonl"); oa_dois = {row["doi"] for row in oa_rows if row["doi"]}; oa_titles = {row["normalized_title"] for row in oa_rows}
    normalized = [_normalize(row) for _, row in sorted(related.items())]; new_rows = []
    for row in normalized:
        basis = "existing_doi" if row["doi"] in existing_dois else "existing_title" if row["normalized_title"] in existing_titles else "openalex_doi" if row["doi"] in oa_dois and row["doi"] else "openalex_title" if row["normalized_title"] in oa_titles else None
        row["duplicate_basis"] = basis
        if basis is None: new_rows.append(row)
    resolution_path = WORK / "fallback_seed_resolution.jsonl"; resolution_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in resolutions), encoding="utf-8")
    relation_path = WORK / "fallback_relationships.jsonl"; relation_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in relationships), encoding="utf-8")
    new_path = WORK / "new_deduplicated_candidates.jsonl"; new_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in new_rows), encoding="utf-8")
    result = {"status":"d14_s2_fallback_round1_complete","protocol_version":"1.3","pipeline_version":VERSION,"seed_count":58,
              "resolved_count":sum(row["status"]=="resolved" for row in resolutions),"unresolved_count":sum(row["status"]!="resolved" for row in resolutions),
              "relationship_count":len(relationships),"unique_related_count":len(normalized),"new_deduplicated_candidate_count":len(new_rows),
              "seed_resolution_sha256":sha256(resolution_path),"relationships_sha256":sha256(relation_path),"new_candidates_sha256":sha256(new_path),
              "credential_handling":"Optional SEMANTIC_SCHOLAR_API_KEY read from environment header only; never printed or persisted.",
              "interpretation_boundary":"Fallback citation candidates are not eligible studies or PRISMA inclusions."}
    manifest = WORK / "fallback_manifest.json"; manifest.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",encoding="utf-8"); (WORK/"fallback_manifest.json.sha256").write_text(f"{sha256(manifest)}  fallback_manifest.json\n",encoding="utf-8")
    WORK.replace(FINAL); return result


def verify() -> dict[str, Any]:
    path=FINAL/"fallback_manifest.json"; result=json.loads(path.read_text(encoding="utf-8"))
    for name,field in (("fallback_seed_resolution.jsonl","seed_resolution_sha256"),("fallback_relationships.jsonl","relationships_sha256"),("new_deduplicated_candidates.jsonl","new_candidates_sha256")):
        if sha256(FINAL/name)!=result[field]: raise S2Error(f"D14 S2 hash mismatch: {name}")
    if len(_read(FINAL/"fallback_seed_resolution.jsonl"))!=58: raise S2Error("D14 S2 seed conservation failed")
    if (FINAL/"fallback_manifest.json.sha256").read_text().split()[0]!=sha256(path): raise S2Error("D14 S2 manifest sidecar mismatch")
    return result


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("run","verify")); args=parser.parse_args(); print(json.dumps(run() if args.command=="run" else verify(),sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
