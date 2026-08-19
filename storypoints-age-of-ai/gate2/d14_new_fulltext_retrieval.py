"""Retrieve lawful PDFs for 11 newly screened D14 candidates using archived routes."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
import gate2.d14_secure_fulltext as secure
from gate2.d14_new_screening_finalize import FINAL as SCREENING, verify as verify_screening
from gate2.d14_new_candidate_consolidation import FINAL as CANDIDATES, verify as verify_candidates
from gate2.d14_s2_newly_resolved_relationships import FINAL as RELATIONSHIPS, verify as verify_relationships


FINAL = OUTPUT / "newly_resolved_fulltext_v2"
ROUTES = FINAL / "routes"
RESULTS = FINAL / "results"
PDFS = FINAL / "pdf"
QUARANTINE = FINAL / "quarantine"
VERSION = "d14-new-fulltext-retrieval/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_routes() -> dict[str, Any]:
    if ROUTES.exists(): raise ValueError(f"immutable D14 new full-text routes exist: {ROUTES}")
    verify_screening(); verify_candidates(); verify_relationships()
    included = {row["family_id"] for row in _read(SCREENING / "final_screening_ledger.jsonl") if row["final_title_abstract_decision"] == "include"}
    candidates = {row["citation_family_id"]: row for row in _read(CANDIDATES / "new_unique_candidates.jsonl")}
    source_to_family = {candidates[fid]["source_record_id"]: fid for fid in included}
    found: dict[str, dict[str, Any]] = {}
    response_hashes = {}
    for path in sorted((RELATIONSHIPS / "responses").glob("*.json")):
        response_hashes[path.name] = sha256(path); envelope = json.loads(path.read_text(encoding="utf-8"))
        for edge in envelope.get("data", []):
            for key in ("citedPaper", "citingPaper"):
                node = edge.get(key) or {}; paper_id = node.get("paperId"); route = node.get("openAccessPdf") or {}
                if paper_id in source_to_family:
                    url = route.get("url") or ""
                    basis = "archived_semantic_scholar_openAccessPdf"
                    if not url:
                        match = re.search(r"https://arxiv\.org/abs/([0-9.]+)", route.get("disclaimer") or "")
                        if match:
                            url = f"https://arxiv.org/pdf/{match.group(1)}"
                            basis = "archived_semantic_scholar_arxiv_disclaimer"
                        elif route.get("status") != "CLOSED" and candidates[source_to_family[paper_id]].get("doi"):
                            url = "https://doi.org/" + candidates[source_to_family[paper_id]]["doi"]
                            basis = "archived_semantic_scholar_doi_disclaimer"
                    if url and not url.startswith("https://"): raise ValueError("non-HTTPS archived open PDF route")
                    found[paper_id] = {"url": url, "basis": basis, "status": route.get("status"), "license": route.get("license")}
    if set(found) != set(source_to_family): raise ValueError("archived metadata missing for an included candidate")
    rows = []
    for source_id, family_id in sorted(source_to_family.items(), key=lambda item: item[1]):
        location = found[source_id]
        candidates_list = ([{"url": location["url"], "basis": location["basis"], "license": location["license"], "oa_status": location["status"]}] if location["url"] else [])
        rows.append({"citation_family_id": family_id, "title": candidates[family_id]["title"], "source_record_id": source_id,
                     "candidate_locations": candidates_list})
    ROUTES.mkdir(parents=True); path = ROUTES / "location_candidates.jsonl"
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    manifest = {"status": "d14_new_fulltext_routes_complete", "pipeline_version": VERSION, "protocol_version": "1.3", "family_count": len(rows),
                "screening_manifest_sha256": sha256(SCREENING / "final_screening_manifest.json"), "relationship_manifest_sha256": sha256(RELATIONSHIPS / "manifest.json"),
                "response_hashes": response_hashes, "routes_sha256": sha256(path),
                "security_boundary": "Routes extracted from archived public Semantic Scholar metadata; no network, secrets, Git/history, or private systems."}
    mp = ROUTES / "manifest.json"; mp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROUTES / "manifest.json.sha256").write_text(f"{sha256(mp)}  manifest.json\n", encoding="ascii"); return manifest


def verify_routes() -> dict[str, Any]:
    path = ROUTES / "manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8"))
    if sha256(ROUTES / "location_candidates.jsonl") != manifest["routes_sha256"] or len(_read(ROUTES / "location_candidates.jsonl")) != 11:
        raise ValueError("D14 new full-text route ledger mismatch")
    if (ROUTES / "manifest.json.sha256").read_text().split()[0] != sha256(path): raise ValueError("D14 new route sidecar mismatch")
    return manifest


def fetch() -> dict[str, Any]:
    verify_routes(); RESULTS.mkdir(parents=True, exist_ok=True)
    secure.RESULTS = RESULTS; secure.PDFS = PDFS; secure.QUARANTINE = QUARANTINE
    rows = _read(ROUTES / "location_candidates.jsonl")
    for row in rows:
        result_path = RESULTS / f"{row['citation_family_id']}.json"
        if result_path.exists(): continue
        if row["candidate_locations"]:
            secure._fetch_row(row)
        else:
            secure._atomic_json(result_path, {"citation_family_id": row["citation_family_id"], "status": "no_lawful_pdf_route", "attempts": [], "pdf_path": None, "pdf_sha256": None, "bytes": 0,
                                                    "security_attestation": "Archived metadata exposed no lawful public PDF route; no network request was made."})
    results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(RESULTS.glob("*.json"))]
    manifest = {"status": "d14_new_fulltext_retrieval_complete", "pipeline_version": VERSION, "family_count": 11,
                "result_counts": dict(Counter(row["status"] for row in results)), "result_hashes": {p.name: sha256(p) for p in sorted(RESULTS.glob("*.json"))},
                "routes_manifest_sha256": sha256(ROUTES / "manifest.json"),
                "security_boundary": "Public HTTPS only; public-IP validation, bounded redirects/size, PDF signature and active-content quarantine; no authentication, paywall bypass, secrets, Git/history, or PDF execution."}
    path = FINAL / "retrieval_manifest.json"; path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (FINAL / "retrieval_manifest.json.sha256").write_text(f"{sha256(path)}  retrieval_manifest.json\n", encoding="ascii"); return manifest


def verify_retrieval() -> dict[str, Any]:
    path = FINAL / "retrieval_manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8")); files = sorted(RESULTS.glob("*.json"))
    if len(files) != 11 or {p.name: sha256(p) for p in files} != manifest["result_hashes"]: raise ValueError("D14 new retrieval result mismatch")
    for p in files:
        row = json.loads(p.read_text()); pdf = row.get("pdf_path")
        if row["status"] == "retrieved_static_pdf" and (not Path(pdf).exists() or sha256(Path(pdf)) != row["pdf_sha256"] or secure.active_indicators(Path(pdf).read_bytes())):
            raise ValueError("D14 new retrieved PDF integrity failure")
    if (FINAL / "retrieval_manifest.json.sha256").read_text().split()[0] != sha256(path): raise ValueError("D14 new retrieval sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("build-routes", "verify-routes", "fetch", "verify-retrieval")); args = parser.parse_args()
    result = build_routes() if args.command == "build-routes" else verify_routes() if args.command == "verify-routes" else fetch() if args.command == "fetch" else verify_retrieval()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
