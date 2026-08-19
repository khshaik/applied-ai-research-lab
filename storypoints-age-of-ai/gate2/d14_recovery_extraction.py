"""Freeze recovery quality and prepare/validate its evidence extraction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any, Optional

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_new_candidate_consolidation import FINAL as CANDIDATES, verify as verify_candidates
from gate2.d14_recovery_quality import FINAL as QUALITY, verify_packet as verify_quality_packet
from gate2.d14_recovery_quality_reconcile import FINAL as ADJ, validate as validate_quality


FINAL = OUTPUT / "newly_resolved_extraction_v2"
PACKET = FINAL / "packet"
SCHEMA = Path("gate2/d14_extraction_schema.json")
QUALITY_LEDGER = ADJ / "adjudicated_quality.jsonl"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def prepare() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError("immutable recovery extraction exists")
    quality = validate_quality(QUALITY_LEDGER); qpacket = verify_quality_packet(); verify_candidates()
    source = {r["family_id"]: r for r in _read(Path(qpacket["packet_path"]))}; qrows = {r["family_id"]: r for r in _read(QUALITY_LEDGER)}
    candidates = {r["citation_family_id"]: r for r in _read(CANDIDATES / "new_unique_candidates.jsonl")}
    rows=[]
    for fid in sorted(qrows):
        q=qrows[fid]; s=source[fid]; c=candidates[fid]
        rows.append({**s, "quality_appraisal_sha256": sha256(QUALITY_LEDGER), "appraisal_form": q["appraisal_form"], "evidence_band": q["evidence_band"],
                     "bibliographic_status": {"title": c["title"], "authors": c.get("authors") or [], "year": c.get("publication_year"), "venue": c.get("venue"),
                                              "doi": c.get("doi"), "arxiv_id": c.get("arxiv_id"), "verified_url": c.get("url"),
                                              "publication_status": "preprint" if c.get("arxiv_id") else "published", "version_date": None,
                                              "evidence_stream": "citation_chasing", "study_type": q["design_type"],
                                              "peer_review_status": "not_verified"}})
    PACKET.mkdir(parents=True); path=PACKET/"extraction_packet.jsonl"; path.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    manifest={"status":"d14_recovery_extraction_packet_complete","protocol_version":"1.3","family_count":9,"packet_path":str(path),"packet_sha256":sha256(path),
              "quality":quality,"quality_ledger_sha256":sha256(QUALITY_LEDGER),"schema_sha256":sha256(SCHEMA),
              "security_boundary":"Checksum-bound action-free static text only; no network, Git/history, secrets, installs, or PDF execution."}
    mp=PACKET/"manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); (PACKET/"manifest.json.sha256").write_text(f"{sha256(mp)}  manifest.json\n",encoding="ascii")
    return manifest


def verify_packet() -> dict[str, Any]:
    mp=PACKET/"manifest.json"; m=json.loads(mp.read_text()); rows=_read(Path(m["packet_path"]))
    if len(rows)!=9 or len({r["family_id"] for r in rows})!=9 or sha256(Path(m["packet_path"]))!=m["packet_sha256"]: raise ValueError("recovery extraction packet mismatch")
    for r in rows:
        if sha256(Path(r["source_text_path"]))!=r["source_text_sha256"]: raise ValueError("recovery extraction source drift")
    if (PACKET/"manifest.json.sha256").read_text().split()[0]!=sha256(mp): raise ValueError("recovery extraction manifest mismatch")
    return m


def _page(locator: Any) -> Optional[int]:
    if isinstance(locator,dict): return locator.get("page")
    m=re.search(r"\bpage\s+(\d+)\b",str(locator),re.I); return int(m.group(1)) if m else None


def validate(path: Path, extractor_id: str) -> dict[str, Any]:
    manifest=verify_packet(); schema=json.loads(SCHEMA.read_text()); expected={r["family_id"]:r for r in _read(Path(manifest["packet_path"]))}; rows=_read(path); seen=set(); contexts=set()
    for row in rows:
        fid=row.get("family_id"); context=row.get("review_context_id")
        if fid not in expected or fid in seen or not context or context in contexts: raise ValueError("recovery extraction identity mismatch")
        seen.add(fid); contexts.add(context)
        if set(schema["top_level_required"])-set(row) or row.get("record_id")!=fid or row.get("source_text_sha256")!=expected[fid]["source_text_sha256"] or row.get("quality_appraisal_sha256")!=manifest["quality_ledger_sha256"] or row.get("extractor_agent_id")!=extractor_id: raise ValueError("recovery extraction schema/binding mismatch")
        if any(row["security_attestation"].get(k) is not False for k in schema["security_required_false"]): raise ValueError("recovery extraction security mismatch")
        pages={p["page"]:p["text"] for p in json.loads(Path(expected[fid]["source_text_path"]).read_text())["pages"]}; ids=set()
        if not 1<=len(row["measures_findings"])<=5: raise ValueError("recovery extraction finding count invalid")
        for f in row["measures_findings"]:
            n=_page(f.get("source_locator")); value=f.get("value","")
            if f.get("finding_id") in ids or n not in pages or "".join(value.split()) not in "".join(pages[n].split()): raise ValueError("recovery extraction finding support mismatch")
            ids.add(f["finding_id"])
            if f.get("field_name") not in schema["finding_field_name_enum"] or f.get("data_nature") not in schema["data_nature_enum"] or f.get("direction") not in schema["finding_direction_enum"]: raise ValueError("recovery extraction finding enum mismatch")
            if f.get("quantitative") and not f.get("reported_estimate"): raise ValueError("recovery quantitative estimate missing")
        novelty=row["novelty_assessment"]
        if set(novelty["dimensions"])!=set(schema["novelty_dimension_keys"]) or any(x["status"] not in schema["novelty_status_enum"] for x in novelty["dimensions"].values()) or novelty["same_planning_use"] not in schema["same_planning_use_enum"] or novelty["novelty_risk"] not in schema["novelty_risk_enum"]: raise ValueError("recovery novelty schema mismatch")
    if seen!=set(expected): raise ValueError("recovery extraction incomplete")
    sidecar=path.with_suffix(path.suffix+".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0]!=sha256(path): raise ValueError("recovery extraction checksum mismatch")
    return {"status":"valid_complete_recovery_extraction","family_count":9,"finding_count":sum(len(r["measures_findings"]) for r in rows),"sha256":sha256(path)}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("prepare","verify-packet","validate")); parser.add_argument("path",nargs="?",type=Path); parser.add_argument("extractor_id",nargs="?"); args=parser.parse_args()
    result=prepare() if args.command=="prepare" else verify_packet() if args.command=="verify-packet" else validate(args.path,args.extractor_id)
    print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
