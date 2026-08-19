"""Close D14 under the approved prospective resource cap."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_extraction_finalize import FINAL as MAIN_EXTRACTION, verify as verify_main_extraction
from gate2.d14_recovery_extraction import FINAL as RECOVERY_EXTRACTION, validate as validate_recovery_extraction
from gate2.d14_s2_final_retry import FINAL as FINAL_RETRY, verify as verify_final_retry


FINAL = OUTPUT / "final"
DECISION = Path("research/studies/vdcm/evidence-map/D14_RESOURCE_CAP_DECISION.md")
RECOVERY_LEDGER = RECOVERY_EXTRACTION / "extraction.jsonl"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def close() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError("immutable D14 closure exists")
    decision_text = DECISION.read_text(encoding="utf-8")
    if "[x] Approved by accountable author on 2026-08-19" not in decision_text:
        raise ValueError("D14 resource cap lacks accountable-author approval")
    main = verify_main_extraction(); retry = verify_final_retry()
    recovery = validate_recovery_extraction(RECOVERY_LEDGER, "d14-recovery-extractor-a")
    verification = json.loads((RECOVERY_EXTRACTION / "verification_report.json").read_text(encoding="utf-8"))
    if verification["status"] != "pass" or verification["primary_extraction_sha256"] != recovery["sha256"]:
        raise ValueError("D14 recovery verification mismatch")
    rows=[]
    for source, path in (("citation_round_1", MAIN_EXTRACTION / "final_evidence_extraction.jsonl"),
                         ("citation_recovery_supplement", RECOVERY_LEDGER)):
        for row in _read(path):
            rows.append({"family_id":row["family_id"],"record_id":row["record_id"],"citation_source":source,
                         "bibliographic_status":row["bibliographic_status"],"appraisal_form":row["appraisal_form"],
                         "evidence_band":row["evidence_band"],"finding_count":len(row["measures_findings"]),
                         "quantitative_finding_count":sum(bool(f["quantitative"]) for f in row["measures_findings"]),
                         "novelty_assessment":row["novelty_assessment"],"source_text_sha256":row["source_text_sha256"]})
    if len(rows)!=221 or len({r["family_id"] for r in rows})!=221: raise ValueError("D14 included-family conservation failure")
    FINAL.mkdir(parents=True); ledger=FINAL/"d14_included_evidence_families.jsonl"
    ledger.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in sorted(rows,key=lambda r:r["family_id"])),encoding="utf-8")
    novelty=Counter(v["status"] for r in rows for v in r["novelty_assessment"]["dimensions"].values())
    duplicate_lines=[r["family_id"] for r in rows if all(v["status"]=="met" for v in r["novelty_assessment"]["dimensions"].values()) and r["novelty_assessment"]["same_planning_use"]=="yes"]
    manifest={"status":"d14_closed_under_approved_resource_cap","protocol_version":"1.3","included_family_count":221,
              "citation_round_1_included":212,"recovery_supplement_included":9,"finding_count":sum(r["finding_count"] for r in rows),
              "quantitative_finding_count":sum(r["quantitative_finding_count"] for r in rows),"evidence_band_counts":dict(Counter(r["evidence_band"] for r in rows)),
              "novelty_dimension_counts":dict(novelty),"substantively_duplicative_family_ids":duplicate_lines,
              "persistent_api_failure_count":retry["resolution_counts"].get("unresolved_api_failure",0),
              "resource_cap_decision_sha256":sha256(DECISION),"main_extraction_manifest_sha256":sha256(MAIN_EXTRACTION/"final_extraction_manifest.json"),
              "recovery_extraction_sha256":recovery["sha256"],"recovery_verification_sha256":sha256(RECOVERY_EXTRACTION/"verification_report.json"),
              "ledger_sha256":sha256(ledger),"bounded_novelty_wording":"No substantively duplicative framework was identified within the predeclared open scholarly indexes, repositories, and citation networks searched through the stated cutoff date and reported resource cap.",
              "limitations":["Recursive citation chasing from 221 newly included D14 families was not executed under the approved prospective cap.","Five Semantic Scholar seed resolutions remained API failures after bounded retries.","Seven source no-matches and unavailable lawful full texts may conceal relevant evidence.","Subscription databases were inaccessible and were not represented as searched."],
              "security_boundary":"Closure uses local checksum-bound ledgers only; no network, Git/history, secrets, installs, PDF execution, or private systems."}
    path=FINAL/"d14_final_manifest.json"; path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); (FINAL/"d14_final_manifest.json.sha256").write_text(f"{sha256(path)}  d14_final_manifest.json\n",encoding="ascii")
    return manifest


def verify() -> dict[str, Any]:
    path=FINAL/"d14_final_manifest.json"; m=json.loads(path.read_text()); rows=_read(FINAL/"d14_included_evidence_families.jsonl")
    if len(rows)!=m["included_family_count"] or sha256(FINAL/"d14_included_evidence_families.jsonl")!=m["ledger_sha256"]: raise ValueError("D14 final ledger mismatch")
    if sha256(DECISION)!=m["resource_cap_decision_sha256"] or (FINAL/"d14_final_manifest.json.sha256").read_text().split()[0]!=sha256(path): raise ValueError("D14 closure approval/checksum mismatch")
    if m["substantively_duplicative_family_ids"]: raise ValueError("D14 novelty stop rule triggered")
    return m


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("close","verify")); args=parser.parse_args(); result=close() if args.command=="close" else verify(); print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
