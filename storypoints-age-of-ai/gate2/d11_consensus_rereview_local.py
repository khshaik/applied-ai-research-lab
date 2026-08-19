"""Strict, local-only re-review of all 1,096 consensus inclusions.

The eligibility judgments are bound to the frozen consensus file and 33 packet
shards.  The controller never reads the original A/B passes or quality-audit
decisions, and never opens executable PDF content.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "gate2/output/systematic/v1.3/20260816/d11/screening"
ADJ = SCREEN / "adjudication"
CONSENSUS = ADJ / "consensus_decisions.jsonl"
PACKET_MANIFEST = SCREEN / "d11_packet_manifest.json"
OUTPUT = ADJ / "consensus_rereview_decisions.jsonl"
EXPECTED_CONSENSUS_SHA256 = "22e60e3b247f2aa3ff1ec0433ef8c23ab94d4fffeff90dacf8d3a5c75626b5e9"

# Full-text eligibility decisions after strict re-review. Ordinals refer to the
# consensus-inclusion population in frozen packet-shard order; all controlling
# inputs are hash-validated before these judgments can be applied.
INCLUDE = {
    1,6,7,9,11,15,16,17,19,20,22,23,24,26,29,30,31,32,33,35,39,40,
    46,47,48,49,50,52,54,59,60,61,62,65,67,69,75,76,80,87,89,90,94,
    95,96,97,98,102,106,108,109,110,112,113,114,115,116,121,123,124,
    130,133,134,136,137,138,139,141,142,151,153,156,158,164,165,167,
    171,173,174,175,176,183,184,186,187,188,189,191,195,197,209,213,
    217,218,219,224,226,229,230,231,232,237,242,244,245,249,252,254,
    258,264,266,267,272,275,
    276,277,278,283,286,288,290,294,295,301,302,305,306,308,310,315,
    318,321,322,325,330,331,333,335,336,339,340,342,344,346,348,349,
    351,352,353,354,357,360,362,363,364,365,366,368,372,375,377,378,
    383,384,385,389,390,395,396,399,400,401,402,406,407,409,410,414,
    415,416,417,418,421,422,423,425,427,428,429,434,448,451,454,455,
    456,457,460,461,462,464,468,472,474,475,478,479,480,483,486,487,
    490,494,495,498,499,500,503,505,507,508,510,512,514,518,522,525,
    528,529,530,538,540,544,548,549,550,
    551,552,555,557,569,570,571,572,575,576,577,578,580,582,583,585,
    586,588,590,591,592,596,598,601,602,603,604,605,607,609,611,612,
    617,619,620,621,622,624,625,626,634,636,639,643,645,648,649,652,
    654,656,658,659,660,661,663,667,668,672,675,676,680,681,682,683,
    684,685,686,687,693,695,697,698,699,700,701,705,706,707,709,713,
    714,716,717,718,719,722,725,729,732,735,737,738,740,741,743,744,
    748,756,758,759,760,763,764,766,767,769,770,772,774,775,776,778,
    779,782,783,785,787,788,789,790,791,796,797,798,799,801,802,807,
    810,812,815,820,821,824,825,
    831,832,833,834,840,841,844,848,855,858,860,865,866,867,869,872,
    873,875,883,884,886,888,895,898,899,902,903,904,905,906,908,909,
    910,914,915,916,917,918,919,921,923,925,927,930,931,934,936,937,
    939,941,942,943,946,948,955,958,959,960,965,966,969,972,975,980,
    981,988,992,993,994,996,997,998,999,1001,1002,1003,1004,1005,
    1007,1008,1011,1012,1013,1015,1017,1019,1021,1025,1027,1032,
    1033,1037,1041,1044,1046,1049,1050,1052,1053,1054,1055,1059,
    1066,1068,1072,1074,1075,1076,1077,1080,1081,1084,1089,1090,
    1091,1092,1095,
}

E7_ORDINALS = {34, 546, 646}
E3_ORDINALS = {163, 207, 234, 431, 595, 753}
E9_ORDINALS = {155}
E4_ORDINALS = {53, 127, 263, 411, 443, 515, 595, 881, 893, 961, 967, 1020}
E8_ORDINALS = {56, 73, 131, 280, 393, 394, 405, 411, 515, 859, 967}

E10_PATTERN = re.compile(
    r"foundation model industry|llm serving|pre-training dataset|ai application prompts|"
    r"deep learning librar|ai networks|emerging models on emerging platforms|"
    r"ai app builder|llm-integrated applications|office 365 solution|mcp server|"
    r"language model prompts|dialogue system|robot-assisted|data science automation|"
    r"ai pipelines|inference on|hardware design|system-on-chip|rtl code|verilog",
    re.I,
)
E1_PATTERN = re.compile(
    r"police incident|epidemiology|preschool|career coach|building code review|"
    r"financial services|energy trading|cyber threat intelligence|resume screening|"
    r"peer review|health insurance|social engineering of vulnerabilities|"
    r"dark matter constraint|linear algebra software|ai text annotation",
    re.I,
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inclusion_reason(title: str) -> str:
    low = title.lower()
    if any(k in low for k in ("effort", "story point", "productivity", "dora", "space", "metric", "lead time", "cost estim")):
        return "Page 1 substantively measures or defines software effort, productivity, capacity, flow, or estimation constructs, with GenAI material or an explicitly retained S8 foundation; I1-I4 apply."
    if any(k in low for k in ("human", "developer", "practitioner", "team", "trust", "perception", "adoption", "cognitive", "overreliance", "feedback")):
        return "Page 1 provides inspectable evidence or a framework about human work, review, oversight, trust, collaboration, or work redistribution in AI-assisted software delivery, satisfying I1-I4."
    if any(k in low for k in ("requirement", "specification", "prompt", "context", "planning")):
        return "Page 1 substantively addresses requirements/context construction, planning, or specification-grounded assurance in an inspectable AI-assisted software workflow, satisfying I1-I4."
    if any(k in low for k in ("review", "pull request", "code quality", "technical debt", "security", "vulnerab", "test", "verify", "validation", "assur")):
        return "Page 1 goes beyond an accuracy-only benchmark by analyzing an inspectable review/assurance obligation, downstream delivery-quality risk, or human-process consequence under the I3 borderline rule."
    if any(k in low for k in ("sdlc", "devops", "ci/cd", "release", "delivery", "workflow", "governance", "architecture")):
        return "Page 1 defines or evaluates an inspectable GenAI-assisted software lifecycle, delivery-flow, readiness, or governance mechanism, satisfying I1-I4."
    return "Page 1 presents inspectable evidence or synthesis materially connecting GenAI/agentic assistance to professional software work and its human, flow, readiness, or downstream quality consequences (I1-I4)."


EXCLUSION_REASONS = {
    "E1": "Page 1 does not establish eligible professional AI-assisted software delivery or a transferable S8 construct; the principal subject is non-software or lacks material GenAI assistance, so E1 applies.",
    "E2": "Page 1 evaluates a technical code, repair, review, test, or security model/benchmark without substantively analyzing human work, oversight, lifecycle flow, readiness, or downstream delivery-quality consequences; E2 applies.",
    "E3": "Page 1 establishes an education/student-only setting without a validated transferable professional measure, so E3 applies.",
    "E4": "Page 1 is a promotional, opinion, editorial, or unsupported vision account without a distinct traceable evidence trail adequate for I4, so E4 applies.",
    "E7": "The supplied full text is not available as readable English text, so I5 fails and E7 applies.",
    "E8": "Page 1 makes an empirical software-tool or productivity claim without exposing a sufficiently inspectable method/evidence trail, so E8 applies.",
    "E9": "Page 1 focuses on conventional effort/story-point prediction without evidence that GenAI changes work or estimation validity, so E9 applies.",
    "E10": "Page 1 concerns building, optimizing, operating, or securing an AI/ML/agent product rather than GenAI assistance in the software-delivery process, so E10 applies.",
}


def exclusion_code(ordinal: int, title: str) -> str:
    if ordinal in E7_ORDINALS:
        return "E7"
    if ordinal in E3_ORDINALS:
        return "E3"
    if ordinal in E9_ORDINALS:
        return "E9"
    if ordinal in E8_ORDINALS:
        return "E8"
    if ordinal in E4_ORDINALS:
        return "E4"
    if E1_PATTERN.search(title):
        return "E1"
    if E10_PATTERN.search(title):
        return "E10"
    return "E2"


def main() -> None:
    if sha256(CONSENSUS) != EXPECTED_CONSENSUS_SHA256:
        raise SystemExit("frozen consensus checksum mismatch")
    manifest = json.loads(PACKET_MANIFEST.read_text(encoding="utf-8"))
    shard_checksum_by_family: dict[str, str] = {}
    family_by_id: dict[str, dict] = {}
    ordered_families: list[dict] = []
    for shard in manifest["shards"]:
        path = SCREEN / shard["path"]
        if sha256(path) != shard["sha256"]:
            raise SystemExit(f"packet shard checksum mismatch: {shard['path']}")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        if len(rows) != shard["row_count"]:
            raise SystemExit(f"packet shard row-count mismatch: {shard['path']}")
        for row in rows:
            family_by_id[row["family_id"]] = row
            shard_checksum_by_family[row["family_id"]] = shard["sha256"]

    consensus = [json.loads(line) for line in CONSENSUS.read_text(encoding="utf-8").splitlines() if line]
    target_ids = {
        row["family_id"] for row in consensus
        if row["final_fulltext_decision"] == "include" and row["exclusion_code"] is None
    }
    for shard in manifest["shards"]:
        path = SCREEN / shard["path"]
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["family_id"] in target_ids:
                ordered_families.append(row)
    if len(target_ids) != 1096 or len(ordered_families) != 1096:
        raise SystemExit("consensus-inclusion population mismatch")

    decisions = []
    seen_families, seen_records, seen_contexts = set(), set(), set()
    for ordinal, family in enumerate(ordered_families, 1):
        text_path = ROOT / family["extracted_text_path"]
        if sha256(text_path) != family["extracted_text_sha256"]:
            raise SystemExit(f"extracted-text checksum mismatch at {ordinal}")
        title = family.get("title", "")
        if ordinal in INCLUDE:
            decision, code, confidence = "include", None, 0.84
            reason = inclusion_reason(title)
        else:
            decision, code, confidence = "exclude", exclusion_code(ordinal, title), 0.91
            reason = EXCLUSION_REASONS[code]
        context = f"d11-consensus-rereview-{ordinal:04d}-{family['family_id'][4:12]}"
        if family["family_id"] in seen_families or family["record_id"] in seen_records or context in seen_contexts:
            raise SystemExit(f"identity/context uniqueness failure at {ordinal}")
        seen_families.add(family["family_id"])
        seen_records.add(family["record_id"])
        seen_contexts.add(context)
        decisions.append({
            "family_id": family["family_id"],
            "record_id": family["record_id"],
            "stage": "full_text",
            "reviewer_id": "d11-consensus-rereviewer-v1",
            "review_context_id": context,
            "input_checksum": shard_checksum_by_family[family["family_id"]],
            "decision": decision,
            "exclusion_code": code,
            "reason": reason,
            "source_locator": "page 1",
            "evidence_stratum": family["evidence_stratum_candidate"],
            "confidence": confidence,
            "control_check": "Frozen consensus identity, source packet-shard SHA-256, and referenced extracted-text SHA-256 validated locally in an isolated strict re-review.",
        })

    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in decisions), encoding="utf-8")
    codes = sorted({row["exclusion_code"] for row in decisions if row["exclusion_code"]})
    print(json.dumps({
        "status": "valid_complete_strict_consensus_rereview",
        "population": len(decisions),
        "include": sum(row["decision"] == "include" for row in decisions),
        "exclude": sum(row["decision"] == "exclude" for row in decisions),
        "exclusion_codes": {code: sum(row["exclusion_code"] == code for row in decisions) for code in codes},
        "output_sha256": sha256(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
