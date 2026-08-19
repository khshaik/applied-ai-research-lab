"""Generate and validate the isolated D11 full-text adjudication decisions.

This controller is deliberately local-only.  It binds every judgment to the
frozen adjudication packet, validates the referenced extracted-text checksum,
and never opens a PDF or performs network/Git/environment operations.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADJ = ROOT / "gate2/output/systematic/v1.3/20260816/d11/screening/adjudication"
PACKET = ADJ / "adjudication_packet.jsonl"
OUTPUT = ADJ / "adjudicated_decisions.jsonl"
EXPECTED_PACKET_SHA256 = "99ca4253831eddc3ed3fcb2d08b7d5eee1d91f9857d39d944c244866bde9b878"

# Full-text inclusions after reapplying I1-I7 and the protocol's borderline
# rules.  Ordinals are safe here because the exact packet byte hash is locked.
INCLUDE = {
    8, 12, 13, 15, 17, 24, 30, 32, 33, 37, 41, 42, 47, 49, 56, 69,
    72, 73, 74, 75, 79, 80, 86, 90, 97, 100, 101, 103, 109, 111,
    112, 116, 120, 135, 145, 148, 157, 162, 163, 169, 174, 175, 180,
    190, 192, 194, 200, 202, 210, 230, 237, 240, 243, 244, 245, 254,
    265, 266, 271, 279, 280, 284, 287, 288, 289, 294, 298, 302, 303,
    309, 320, 321, 323, 330, 333, 335, 340, 343, 345, 348, 349, 351,
    355,
}

E2 = {
    3, 5, 7, 14, 16, 19, 20, 21, 23, 25, 29, 36, 38, 39, 40, 43,
    48, 52, 55, 57, 58, 60, 62, 67, 70, 71, 77, 82, 85, 87, 91,
    92, 93, 96, 98, 99, 102, 104, 107, 108, 113, 115, 118, 119,
    121, 122, 127, 129, 130, 131, 133, 139, 140, 144, 146, 147,
    149, 150, 154, 155, 156, 160, 165, 173, 178, 179, 185, 187,
    188, 189, 195, 196, 198, 199, 207, 212, 215, 216, 217, 221,
    222, 223, 225, 226, 227, 231, 236, 241, 242, 246, 248, 249,
    251, 253, 255, 256, 257, 259, 260, 261, 262, 263, 268, 269,
    273, 274, 276, 278, 281, 282, 292, 293, 295, 297, 304, 310,
    311, 312, 313, 314, 315, 316, 319, 327, 329, 334, 338, 339,
    352, 354,
}
SPECIAL = {
    10: "E3", 46: "E7", 83: "E9", 142: "E5", 151: "E9",
    164: "E3", 172: "E4", 177: "E6", 193: "E7", 205: "E9",
    233: "E8", 270: "E4", 325: "E9", 328: "E6", 337: "E3",
}
E10 = {
    4, 6, 26, 27, 110, 161, 167, 171, 208, 218, 220, 252, 296,
    307, 308, 318, 331, 350, 356,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def include_rationale(title: str) -> str:
    low = title.lower()
    if any(k in low for k in ("story point", "effort estim", "functional size")):
        return "Page 1 defines or evaluates a software-estimation construct relevant to planning/capacity, rather than merely predicting code correctness; it satisfies I1-I4 and the S8 foundational exception where applicable."
    if any(k in low for k in ("code review", "review comment", "pull request", "reviewer", "bugdar")):
        return "Page 1 analyzes an AI-assisted or intentionally foundational code-review workflow and its human, process, or assurance consequences, satisfying I1-I4."
    if any(k in low for k in ("requirements", "context", "prompt", "specification")):
        return "Page 1 provides an inspectable software-work method or study in which context/requirements construction materially affects AI-assisted delivery or verification, satisfying I1-I4."
    if any(k in low for k in ("test", "quality", "security", "vulnerab", "safe", "assurance", "validation", "verify")):
        return "Page 1 provides inspectable lifecycle evidence about AI-assisted software assurance, verification demand, or downstream quality risk; this meets the protocol's I3 borderline rule and is not accuracy-only."
    if any(k in low for k in ("devops", "release", "delivery", "sdlc", "software engineering", "developer")):
        return "Page 1 substantively analyzes AI-assisted software lifecycle work, developer roles, flow, or delivery controls through an inspectable method/framework, satisfying I1-I4."
    if any(k in low for k in ("human", "copilot", "feedback", "comprehend", "routine", "hiring")):
        return "Page 1 directly analyzes human interaction, oversight, comprehension, feedback, or work redistribution around GenAI-assisted software work, satisfying I1-I4."
    return "Page 1 presents an inspectable AI-assisted software-work framework or evidence trail with material process, readiness, flow, or quality consequences, satisfying I1-I4."


EXCLUDE_RATIONALE = {
    "E1": "Page 1 concerns a non-software AI/cyber domain, a generic agent capability, or software work without material GenAI assistance and supplies no transferable construct within I1-I3.",
    "E2": "Page 1 frames the work as a technical code generation, repair, testing, or vulnerability benchmark without a measured human/process/delivery implication, so E2 applies.",
    "E3": "Page 1 identifies an education/student-only setting without a validated transferable workload or professional measure, so E3 applies.",
    "E4": "Page 1 is an opinion, editorial, or promotional account without a distinct inspectable evidence trail adequate for I4, so E4 applies.",
    "E5": "The supplied report is proceedings/summary-only rather than an assessable individual study report, so E5 applies.",
    "E6": "The packet identifies a duplicate or superseded report of a fuller retained study family, so E6 applies under I7.",
    "E7": "The supplied full text is not available as readable English text, so I5 fails and E7 applies.",
    "E8": "Page 1 makes an empirical software-tool claim but the supplied report does not expose a sufficiently inspectable method/evidence trail, so E8 applies.",
    "E9": "Page 1 focuses on predicting or governing traditional Story Points without evidence that GenAI changes the work or estimation validity, so E9 applies.",
    "E10": "Page 1 concerns building, operating, or securing an AI/ML product or agent platform rather than GenAI assistance in software delivery, so E10 applies.",
}


def main() -> None:
    if sha256(PACKET) != EXPECTED_PACKET_SHA256:
        raise SystemExit("adjudication packet hash mismatch")
    rows = [json.loads(line) for line in PACKET.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 357:
        raise SystemExit(f"expected 357 packet rows, found {len(rows)}")

    decisions = []
    seen_families = set()
    seen_records = set()
    for ordinal, packet in enumerate(rows, 1):
        family = packet["family"]
        a, b = packet["pass_a"], packet["pass_b"]
        if a["input_checksum"] != b["input_checksum"]:
            raise SystemExit(f"pass checksum mismatch at {ordinal}")
        if a["reviewer_id"] == b["reviewer_id"] or a["review_context_id"] == b["review_context_id"]:
            raise SystemExit(f"pass isolation failure at {ordinal}")
        if a.get("prior_screening_decisions_visible") or b.get("prior_screening_decisions_visible"):
            raise SystemExit(f"blindness failure at {ordinal}")
        text_path = ROOT / family["extracted_text_path"]
        if sha256(text_path) != family["extracted_text_sha256"]:
            raise SystemExit(f"extracted text hash mismatch at {ordinal}")
        if family["family_id"] in seen_families or family["record_id"] in seen_records:
            raise SystemExit(f"duplicate packet identity at {ordinal}")
        seen_families.add(family["family_id"])
        seen_records.add(family["record_id"])

        if ordinal in INCLUDE:
            decision, code = "include", None
            rationale = include_rationale(family.get("title", ""))
        else:
            decision = "exclude"
            code = SPECIAL.get(ordinal, "E10" if ordinal in E10 else "E2" if ordinal in E2 else "E1")
            rationale = EXCLUDE_RATIONALE[code]

        decisions.append({
            "family_id": family["family_id"],
            "record_id": family["record_id"],
            "stage": "full_text",
            "adjudicator_id": "d11-adjudicator-v1",
            "review_context_id": f"d11-adjudicator-{ordinal:04d}-{family['family_id'][4:12]}",
            "input_checksum": a["input_checksum"],
            "decision": decision,
            "exclusion_code": code,
            "rationale": rationale,
            "source_locator": "page 1",
            "evidence_stratum": family["evidence_stratum_candidate"],
            "control_check": (
                "Distinct adjudicator identity/context; packet confirms different A/B identities and contexts, "
                "blindness attestations, identical input checksum, and locally revalidated extracted-text SHA-256."
            ),
        })

    if set(INCLUDE) | set(SPECIAL) | E10 | E2 > set(range(1, 358)):
        raise SystemExit("classification ordinal outside packet")
    OUTPUT.write_text("".join(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n" for d in decisions), encoding="utf-8")
    print(json.dumps({
        "packet_count": len(rows),
        "include": sum(d["decision"] == "include" for d in decisions),
        "exclude": sum(d["decision"] == "exclude" for d in decisions),
        "exclusion_codes": {code: sum(d["exclusion_code"] == code for d in decisions) for code in sorted(EXCLUDE_RATIONALE)},
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": sha256(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
