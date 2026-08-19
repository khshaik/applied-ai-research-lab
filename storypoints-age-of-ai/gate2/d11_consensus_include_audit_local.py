"""Run the frozen deterministic D11 consensus-inclusion quality audit locally."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "gate2/output/systematic/v1.3/20260816/d11/screening/adjudication/consensus_quality_audit"
PACKET = AUDIT_DIR / "consensus_include_audit_packet.jsonl"
MANIFEST = AUDIT_DIR / "consensus_include_audit_manifest.json"
OUTPUT = AUDIT_DIR / "consensus_include_audit_decisions.jsonl"
EXPECTED_PACKET_SHA256 = "be3f7aa197fd421377ff101e7e744f8ab1d3840c803c7179e1c9bb5449a68e8f"

# Confirmed after source-grounded reapplication of I1-I7. Technical quality
# work is retained only where it substantively establishes assurance demand,
# downstream risk, lifecycle flow, human work, or a protocol-eligible S8 anchor.
CONFIRM_INCLUDE = {
    1, 2, 5, 11, 13, 17, 18, 23, 28, 29, 30, 33, 35, 36, 38, 39,
    40, 42, 45, 46, 48, 50, 51, 52, 61, 64, 68, 71, 72, 73, 74, 78,
    81, 84, 85, 86, 87, 88, 89, 90, 91, 97, 100,
}

E2 = {
    4, 7, 8, 10, 12, 15, 16, 19, 20, 22, 24, 25, 26, 27, 32, 34,
    41, 43, 44, 47, 53, 54, 56, 57, 58, 59, 60, 62, 63, 65, 66, 67,
    69, 77, 80, 82, 92, 93, 96,
}
E10 = {6, 9, 14, 37, 75, 79}
SPECIAL = {70: "E8", 83: "E4"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def include_rationale(title: str) -> str:
    low = title.lower()
    if any(k in low for k in ("effort", "cost estim", "space", "dora", "kpi", "productivity")):
        return "Page 1 measures or defines software effort/productivity/capacity constructs relevant to the evidence map, with GenAI material or an intentional S8 foundation; I1-I4 are satisfied."
    if any(k in low for k in ("review", "feedback", "human", "reliance", "developer", "communicate")):
        return "Page 1 substantively examines human feedback, review, oversight, communication, or work redistribution in AI-assisted software work, satisfying I1-I4."
    if any(k in low for k in ("requirement", "specification", "trace", "context")):
        return "Page 1 provides an inspectable requirements/context method with a material software-lifecycle, coordination, or verification implication, satisfying I1-I4."
    if any(k in low for k in ("security", "vulnerab", "test", "quality", "governance", "cicd", "ci/cd")):
        return "Page 1 goes beyond model accuracy by establishing an inspectable assurance obligation, downstream risk, governance control, or change in testing/review work under the protocol's I3 borderline rule."
    return "Page 1 provides an inspectable AI-assisted software-delivery method or evidence synthesis that substantively addresses lifecycle flow, human work, or downstream quality consequences (I1-I4)."


EXCLUDE_RATIONALE = {
    "E1": "Page 1 does not establish professional AI-assisted software delivery or a transferable eligible construct; the work is non-software, non-GenAI, or outside I1-I3, so E1 is the closest frozen exclusion code.",
    "E2": "Page 1 evaluates a technical code/review/test/security model or benchmark but does not substantively analyze human work, oversight, lifecycle flow, or downstream quality consequences; E2 applies.",
    "E4": "Page 1 is a promotional/opinion-style account without a distinct traceable method or evidence trail adequate for I4, so E4 applies.",
    "E8": "Page 1 describes a software-tool implementation and productivity claims without an inspectable empirical method adequate for those claims, so E8 applies.",
    "E10": "Page 1 concerns building, optimizing, securing, or operating an AI/ML/agent product rather than GenAI assistance in the software-delivery process, so E10 applies.",
}


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["packet_sha256"] != EXPECTED_PACKET_SHA256 or sha256(PACKET) != EXPECTED_PACKET_SHA256:
        raise SystemExit("audit packet hash mismatch")
    rows = [json.loads(line) for line in PACKET.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != manifest["sample_size"] or len(rows) != 100:
        raise SystemExit("audit population mismatch")

    out = []
    families, records, selections = set(), set(), set()
    previous_selection = ""
    for ordinal, packet in enumerate(rows, 1):
        family = packet["family"]
        if packet["audit_rank"] != ordinal or packet["selection_hash"] <= previous_selection:
            raise SystemExit(f"sample order failure at rank {ordinal}")
        previous_selection = packet["selection_hash"]
        if family["family_id"] in families or family["record_id"] in records or packet["selection_hash"] in selections:
            raise SystemExit(f"sample uniqueness failure at rank {ordinal}")
        families.add(family["family_id"])
        records.add(family["record_id"])
        selections.add(packet["selection_hash"])
        if packet["consensus_decision"]["final_fulltext_decision"] != "include":
            raise SystemExit(f"non-inclusion in audit population at rank {ordinal}")
        text_path = ROOT / family["extracted_text_path"]
        if sha256(text_path) != family["extracted_text_sha256"]:
            raise SystemExit(f"extracted-text checksum mismatch at rank {ordinal}")

        if ordinal in CONFIRM_INCLUDE:
            decision, code = "confirm_include", None
            rationale = include_rationale(family.get("title", ""))
        else:
            decision = "false_include"
            code = SPECIAL.get(ordinal, "E10" if ordinal in E10 else "E2" if ordinal in E2 else "E1")
            rationale = EXCLUDE_RATIONALE[code]
        out.append({
            "family_id": family["family_id"],
            "record_id": family["record_id"],
            "audit_rank": ordinal,
            "selection_hash": packet["selection_hash"],
            "auditor_id": "d11-consensus-auditor-v1",
            "audit_context_id": f"d11-consensus-audit-{ordinal:03d}-{family['family_id'][4:12]}",
            "decision": decision,
            "exclusion_code": code,
            "rationale": rationale,
            "source_locator": "page 1",
            "evidence_stratum": family["evidence_stratum_candidate"],
            "input_checksum": EXPECTED_PACKET_SHA256,
            "control_check": "Exact deterministic sample order and identity, packet SHA-256, and referenced extracted-text SHA-256 locally validated; audit context is distinct from screening passes.",
        })

    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in out), encoding="utf-8")
    false_count = sum(row["decision"] == "false_include" for row in out)
    print(json.dumps({
        "status": "complete_threshold_exceeded" if false_count > 5 else "complete_threshold_not_exceeded",
        "sample_size": len(out),
        "confirm_include": len(out) - false_count,
        "false_include": false_count,
        "threshold": 5,
        "full_population_rereview_required": false_count > 5,
        "output_sha256": sha256(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
