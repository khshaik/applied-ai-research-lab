"""Deterministic D14 citation-candidate normalization and conservative deduplication."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from gate2.citation_chasing import OUTPUT, normalized_title, sha256, verify_round1
from gate2.citation_chasing_s2 import FINAL as S2_FINAL, verify as verify_s2


FINAL = OUTPUT / "candidate_consolidation"
OA = OUTPUT / "round1_openalex/new_deduplicated_candidates.jsonl"
S2 = S2_FINAL / "new_deduplicated_candidates.jsonl"
VERSION = "d14-candidate-consolidation/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line]


def _norm_author(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).split())


def _arxiv_from_doi(doi: str) -> str:
    prefix = "10.48550/arxiv."
    return doi[len(prefix):] if (doi or "").lower().startswith(prefix) else ""


def _occurrences() -> list[dict[str, Any]]:
    rows=[]
    for source,path in (("OpenAlex",OA),("Semantic Scholar",S2)):
        for index,row in enumerate(_read(path)):
            authors=row.get("authors") or []
            first=_norm_author(authors[0] if isinstance(authors,list) and authors else "")
            doi=(row.get("doi") or "").lower().removeprefix("https://doi.org/")
            arxiv=(row.get("arxiv_id") or _arxiv_from_doi(doi)).lower()
            title=row.get("normalized_title") or normalized_title(row.get("title") or "")
            stable=row.get("openalex_id") or row.get("s2_id")
            if not stable or not title: raise ValueError("candidate lacks stable source ID or title")
            occurrence_id="CIT-"+hashlib.sha256(f"{source}|{stable}".encode()).hexdigest()[:20]
            rows.append({**row,"citation_occurrence_id":occurrence_id,"discovery_source":source,"source_record_id":stable,
                         "doi":doi,"arxiv_id":arxiv,"normalized_title":title,"normalized_first_author":first,
                         "source_row_index":index})
    return sorted(rows,key=lambda r:r["citation_occurrence_id"])


def consolidate() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError("immutable D14 candidate consolidation exists")
    verify_round1(); verify_s2()
    rows=_occurrences(); parent=list(range(len(rows)))
    def find(x:int)->int:
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a:int,b:int)->None:
        a,b=find(a),find(b)
        if a!=b: parent[max(a,b)]=min(a,b)
    indexes:dict[tuple[str,str],int]={}
    for i,row in enumerate(rows):
        keys=[]
        if row["doi"]: keys.append(("doi",row["doi"]))
        if row["arxiv_id"]: keys.append(("arxiv",row["arxiv_id"]))
        if row["normalized_first_author"] and row.get("publication_year"):
            keys.append(("title_author_year",f"{row['normalized_title']}|{row['normalized_first_author']}|{row['publication_year']}"))
        for key in keys:
            if key in indexes: union(i,indexes[key])
            else: indexes[key]=i
    groups:dict[int,list[dict[str,Any]]]={}
    for i,row in enumerate(rows): groups.setdefault(find(i),[]).append(row)
    families=[]; occurrence_rows=[]
    for members in groups.values():
        members=sorted(members,key=lambda r:r["citation_occurrence_id"])
        family_id="CITFAM-"+hashlib.sha256("|".join(r["citation_occurrence_id"] for r in members).encode()).hexdigest()[:20]
        representative=max(members,key=lambda r:(bool(r.get("doi")),len(r.get("abstract") or ""),r["discovery_source"]=="OpenAlex",r["citation_occurrence_id"]))
        families.append({
            "citation_family_id":family_id,"occurrence_count":len(members),
            "occurrence_ids":[r["citation_occurrence_id"] for r in members],
            "sources":sorted({r["discovery_source"] for r in members}),"title":representative.get("title") or "",
            "normalized_title":representative["normalized_title"],"doi":representative["doi"],"arxiv_id":representative["arxiv_id"],
            "publication_year":representative.get("publication_year"),"authors":representative.get("authors") or [],
            "abstract":representative.get("abstract") or "","venue":representative.get("venue"),"url":representative.get("url"),
            "cited_by_count":max(int(r.get("cited_by_count") or 0) for r in members),
            "dedup_basis":"exact_identifier_or_title_first_author_year",
            "screening_status":"pending_frozen_title_abstract_workflow",
        })
        for row in members: occurrence_rows.append({"citation_occurrence_id":row["citation_occurrence_id"],"citation_family_id":family_id,"discovery_source":row["discovery_source"],"source_record_id":row["source_record_id"],"source_row_index":row["source_row_index"]})
    families.sort(key=lambda r:r["citation_family_id"]); occurrence_rows.sort(key=lambda r:r["citation_occurrence_id"])
    FINAL.mkdir(parents=True)
    fp=FINAL/"candidate_families.jsonl"; op=FINAL/"candidate_occurrences.jsonl"
    fp.write_text("".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in families),encoding="utf-8")
    op.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in occurrence_rows),encoding="utf-8")
    manifest={"status":"d14_candidates_consolidated","pipeline_version":VERSION,"protocol_version":"1.3",
              "input_occurrence_count":len(rows),"candidate_family_count":len(families),"duplicate_occurrence_count":len(rows)-len(families),
              "openalex_input_sha256":sha256(OA),"semantic_scholar_input_sha256":sha256(S2),
              "families_sha256":sha256(fp),"occurrences_sha256":sha256(op),
              "deduplication_rule":"exact DOI OR exact arXiv ID OR exact normalized title + normalized first author + publication year; no fuzzy merge",
              "interpretation_boundary":"Candidate families are not eligible studies, PRISMA inclusions, or novelty evidence."}
    mp=FINAL/"consolidation_manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (FINAL/"consolidation_manifest.json.sha256").write_text(f"{sha256(mp)}  consolidation_manifest.json\n",encoding="utf-8")
    return manifest


def verify()->dict[str,Any]:
    mp=FINAL/"consolidation_manifest.json"; m=json.loads(mp.read_text())
    if sha256(OA)!=m["openalex_input_sha256"] or sha256(S2)!=m["semantic_scholar_input_sha256"]: raise ValueError("candidate input drift")
    if sha256(FINAL/"candidate_families.jsonl")!=m["families_sha256"] or sha256(FINAL/"candidate_occurrences.jsonl")!=m["occurrences_sha256"]: raise ValueError("candidate output hash mismatch")
    fam=_read(FINAL/"candidate_families.jsonl"); occ=_read(FINAL/"candidate_occurrences.jsonl")
    if len(fam)!=m["candidate_family_count"] or len(occ)!=m["input_occurrence_count"]: raise ValueError("candidate count mismatch")
    if len({r["citation_family_id"] for r in fam})!=len(fam) or len({r["citation_occurrence_id"] for r in occ})!=len(occ): raise ValueError("candidate identifier collision")
    if set(r["citation_family_id"] for r in occ)!=set(r["citation_family_id"] for r in fam): raise ValueError("orphan candidate family")
    if (FINAL/"consolidation_manifest.json.sha256").read_text().split()[0]!=sha256(mp): raise ValueError("candidate manifest sidecar mismatch")
    return m


def main()->int:
    p=argparse.ArgumentParser();p.add_argument("command",choices=("run","verify"));a=p.parse_args()
    print(json.dumps(consolidate() if a.command=="run" else verify(),sort_keys=True));return 0


if __name__=="__main__":raise SystemExit(main())
