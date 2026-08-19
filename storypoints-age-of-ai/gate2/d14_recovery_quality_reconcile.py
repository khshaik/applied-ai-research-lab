"""Prepare and validate separate adjudication of recovery quality appraisals."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d12_appraisal_partition_b_local import FORMS
from gate2.d14_recovery_quality import FINAL as SOURCE, verify_packet as verify_source_packet, validate_appraisal


FINAL = SOURCE / "adjudication"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError("immutable recovery quality adjudication exists")
    manifest = verify_source_packet(); a_path = SOURCE / "appraisal_pass_a.jsonl"; b_path = SOURCE / "appraisal_pass_b.jsonl"
    valid_a = validate_appraisal(a_path, "pass-a", "d14-recovery-quality-agent-a")
    valid_b = validate_appraisal(b_path, "pass-b", "d14-recovery-quality-agent-b")
    source = {r["family_id"]: r for r in _read(Path(manifest["packet_path"]))}; a = {r["family_id"]: r for r in _read(a_path)}; b = {r["family_id"]: r for r in _read(b_path)}
    rows = [{"family": source[fid], "pass_a": a[fid], "pass_b": b[fid]} for fid in sorted(source)]
    FINAL.mkdir(parents=True)
    packet = FINAL / "adjudication_packet.jsonl"; packet.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    result = {"status": "prepared_for_separate_recovery_quality_adjudication", "protocol_version": "1.3", "family_count": 9,
              "pass_a": valid_a, "pass_b": valid_b, "packet_sha256": sha256(packet),
              "instruction": "Recompute each criterion from source text; do not average or mechanically select either prior score."}
    path = FINAL / "manifest.json"; path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (FINAL / "manifest.json.sha256").write_text(f"{sha256(path)}  manifest.json\n", encoding="ascii"); return result


def verify_packet() -> dict[str, Any]:
    path = FINAL / "manifest.json"; manifest = json.loads(path.read_text()); rows = _read(FINAL / "adjudication_packet.jsonl")
    if len(rows) != 9 or len({r["family"]["family_id"] for r in rows}) != 9 or sha256(FINAL / "adjudication_packet.jsonl") != manifest["packet_sha256"]:
        raise ValueError("recovery quality adjudication packet mismatch")
    if (FINAL / "manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("recovery quality adjudication manifest mismatch")
    return manifest


def validate(path: Path) -> dict[str, Any]:
    manifest = verify_packet(); packet = {r["family"]["family_id"]: r["family"] for r in _read(FINAL / "adjudication_packet.jsonl")}; rows = _read(path); seen=set(); contexts=set()
    for row in rows:
        fid=row.get("family_id"); context=row.get("adjudication_context_id")
        if fid not in packet or fid in seen or not context or context in contexts:
            raise ValueError("recovery quality adjudication identity mismatch")
        seen.add(fid); contexts.add(context)
        if row.get("record_id") != fid or row.get("source_text_sha256") != packet[fid]["source_text_sha256"] or row.get("input_checksum") != manifest["packet_sha256"]:
            raise ValueError("recovery quality adjudication binding mismatch")
        if row.get("adjudicator_type") != "ai_agent" or row.get("adjudicator_id") != "d14-recovery-quality-adjudicator-v1" or row.get("prior_synthesis_visible") is not False:
            raise ValueError("recovery quality adjudicator provenance mismatch")
        form=row.get("appraisal_form"); criteria=row.get("criteria")
        if form not in FORMS or [x.get("criterion_id") for x in criteria or []] != [x[0] for x in FORMS[form]]:
            raise ValueError("recovery quality adjudication form mismatch")
        for item in criteria:
            locator=str(item.get("source_locator", ""))
            if item.get("score") not in {0,1,2} or not item.get("justification") or not locator.startswith("page ") or not locator[5:].isdigit() or not 1 <= int(locator[5:]) <= packet[fid]["page_count"]:
                raise ValueError("recovery quality adjudication criterion invalid")
        points=sum(x["score"] for x in criteria); critical=row.get("critical_flaw") is True
        band="low_contextual" if critical or points<10 else "moderate" if points<15 else "high"
        if row.get("applicable_points") != 20 or row.get("points_awarded") != points or row.get("percent") != points*5.0 or row.get("evidence_band") != band:
            raise ValueError("recovery quality adjudication arithmetic mismatch")
        if critical and not row.get("critical_flaw_basis"):
            raise ValueError("recovery quality critical flaw unsupported")
        if row.get("evidence_nature") not in {"observed","self-reported","modeled","conceptual"} or len(row.get("security_attestation", "")) < 30:
            raise ValueError("recovery quality adjudication evidence/security invalid")
    if seen != set(packet): raise ValueError("recovery quality adjudication incomplete")
    sidecar=path.with_suffix(path.suffix+".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path): raise ValueError("recovery quality adjudication sidecar mismatch")
    return {"status":"valid_complete_recovery_quality_adjudication","family_count":9,"forms":dict(Counter(r["appraisal_form"] for r in rows)),"bands":dict(Counter(r["evidence_band"] for r in rows)),"sha256":sha256(path)}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("prepare","verify-packet","validate")); parser.add_argument("path",nargs="?",type=Path); args=parser.parse_args()
    result=prepare() if args.command=="prepare" else verify_packet() if args.command=="verify-packet" else validate(args.path)
    print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
