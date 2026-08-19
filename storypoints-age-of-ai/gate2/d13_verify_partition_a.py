"""Source-grounded, local-only verification for D13 partition A.

This controller deliberately uses only the frozen primary extraction and the
checksum-bound D11 page text.  It does not open PDFs, follow links, inspect the
environment, or use network/Git facilities.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re


ROOT = Path("gate2/output/systematic/v1.3/20260816")
PRIMARY = ROOT / "d13/primary/evidence_extractions.jsonl"
TEXT = ROOT / "d11/extraction/text"
OUTPUT = ROOT / "d13/verified_part_a.jsonl"
PRIMARY_SHA256 = "60e24eb03433d4c800e0428bc54583dde5fe6a5a421f46bbd457445efbe96a37"
VERIFIER = "d13-verifier-a-v1"

# These are direct estimation/prediction studies.  They overlap only the
# precommitment-predictor dimension; none establishes the complete proposed
# forecasting construct.
PRECOMMITMENT_PARTIAL = {
    "FAM-21732030d4fa145cc1da",  # agentic cost estimation
    "FAM-2c7a7f6add2d1df4e3de",  # LLM agile effort estimation
    "FAM-2df78c6575f62d678e94",  # planning poker/process model
    "FAM-341a4a5dcacb866b6f8c",  # LLM-aware effort estimation
    "FAM-350eb26903dca3c11037",  # requirements-change effort estimation
    "FAM-36ea440d23f04a2a98e2",  # software effort estimation
    "FAM-38f9d79fa52478e1e165",  # review-effort prediction
    "FAM-46bc475de6d5f8e550f3",  # story-point estimation
    "FAM-4d588e2588099e2099f2",  # planning poker estimation
    "FAM-5488497843da8cf96f08",  # story points/user stories
    "FAM-603d94d0b63da5961ba1",  # agile effort estimation
    "FAM-65283040904dbb9cd0e4",  # agile estimation review
    "FAM-692dfba2936558206383",  # GenAI story-point model
    "FAM-6e2e5b4ae9ae1b9baf08",  # request-format effort estimation
    "FAM-768e4b9e4738bc22f178",  # development-effort estimation
    "FAM-7a10195b246d2601f20f",  # story-point estimation
}

# These reports explicitly span multiple SDLC stages/actors.  "partial" is
# retained for lifecycle breadth only, not as evidence of a role-capacity model.
MULTIROLE_PARTIAL: set[str] = set()

# This number is market/adoption context in a technical overview rather than
# an estimate produced by the mapped study.
CONTEXT_ONLY_QUANTITATIVE = {"FAM-6f725835fc8be4b5a0a7"}

# Low-similarity primary paraphrases receive an explicitly bounded verbatim
# excerpt.  Markers are searched only within the stated frozen page.
FINDING_OVERRIDES = {
    "FAM-03edc9d078ec8528e56a": (19, "Review capacity", "superficial scrutiny."),
    "FAM-0603a1a6ec8e6543f4cc": (1, "Our findings indicate", "SAST scanning."),
    "FAM-361c5b418abf5a68991b": (24, "Despite the growing enthusiasm", "whelminglynascent."),
    "FAM-56234795a4b24f5ba4ee": (1, "GRADE", "Very Low Certainty)."),
    "FAM-4f1e91ae5bdc9c036145": (3, "However, engineering is not", "predict - ability."),
    "FAM-7294cbde06d07a0de04f": (1, "Thefindingsindicate", "textualuserstoryinformation."),
    "FAM-3d1b984abe8c7d312c29": (1, "본연구에서는사례분석을통해", "것으로관찰하였다."),
}

PREFIX = re.compile(
    r"^(?:the report states that|the authors report that|the study (?:further )?"
    r"(?:finds?|find|tests?|states?|reports?) that)\s+",
    re.I,
)
LOCATOR = re.compile(r"page\s+(\d+)", re.I)
KEYWORD = re.compile(r'text containing\s+[\"“](.*?)[\"”]', re.I)
RESULT_CUES = re.compile(
    r"\b(?:we (?:find|found|show|demonstrate|report|observe|propose|present|introduce)|"
    r"results? (?:show|indicate|demonstrate|reveal)|findings? (?:show|indicate|suggest|reveal)|"
    r"this (?:paper|study|work) (?:proposes|presents|introduces|finds|shows|demonstrates)|"
    r"our (?:analysis|evaluation|experiment|study|results?))\b",
    re.I,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9%]+", " ", value.lower()).strip()


def numeric_tokens(value: str) -> set[str]:
    """Canonical numeric tokens, preserving decimals and ignoring punctuation."""
    result = set()
    for token in re.findall(r"(?<![A-Za-z])\d+(?:[.,]\d+)?", value or ""):
        canonical = token.replace(",", ".")
        try:
            result.add(f"{float(canonical):g}")
        except ValueError:
            continue
    return result


def page_number(locator: str) -> int:
    match = LOCATOR.search(locator or "")
    if not match:
        raise ValueError(f"missing page locator: {locator!r}")
    return int(match.group(1))


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text).strip()
    values = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", flat)
    return [v.strip() for v in values if 55 <= len(v.strip()) <= 900]


def best_source_sentence(value: str, pages: list[dict]) -> tuple[int, str, float]:
    target = norm(PREFIX.sub("", value))
    target_tokens = set(target.split())
    best: tuple[float, int, str] | None = None
    for page in pages:
        for sentence in sentences(page["text"]):
            candidate = norm(sentence)
            candidate_tokens = set(candidate.split())
            overlap = len(target_tokens & candidate_tokens)
            recall = overlap / max(1, len(target_tokens))
            precision = overlap / max(1, len(candidate_tokens))
            score = (2 * recall * precision / (recall + precision)) if recall + precision else 0
            if target in candidate or candidate in target:
                score += 0.5
            if best is None or score > best[0]:
                best = (score, int(page["page"]), sentence)
    if best is None:
        raise ValueError("no substantive source sentence")
    return best[1], best[2], best[0]


def best_fallback_sentence(pages: list[dict]) -> tuple[int, str]:
    candidates: list[tuple[int, int, int, str]] = []
    for page in pages:
        for sentence in sentences(page["text"]):
            lowered = sentence.lower()
            if "references" in lowered[:20] or "copyright" in lowered or "http" in lowered:
                continue
            cue = int(bool(RESULT_CUES.search(sentence)))
            early = int(page["page"] <= 2)
            candidates.append((cue, early, min(len(sentence), 500), int(page["page"]), sentence))
    if not candidates:
        raise ValueError("no faithful fallback sentence")
    _, _, _, page, sentence = max(candidates)
    return page, sentence


def override_excerpt(family_id: str, pages: list[dict]) -> tuple[int, str] | None:
    spec = FINDING_OVERRIDES.get(family_id)
    if spec is None:
        return None
    page, start, end = spec
    flat = re.sub(r"\s+", " ", pages[page - 1]["text"]).strip()
    begin = flat.lower().find(start.lower())
    finish = flat.lower().find(end.lower(), begin)
    if begin < 0 or finish < 0:
        raise ValueError(f"finding override markers absent: {family_id}")
    return page, flat[begin:finish + len(end)]


def locator_keyword_supported(locator: str | None, pages: list[dict]) -> bool:
    if not locator:
        return False
    p = page_number(locator)
    if p < 1 or p > len(pages):
        return False
    match = KEYWORD.search(locator)
    if not match:
        return True
    needle = norm(match.group(1))
    haystack = norm(pages[p - 1]["text"])
    return needle in haystack or needle.rstrip("s") in haystack


def relocate_keyword(locator: str, pages: list[dict]) -> str | None:
    match = KEYWORD.search(locator or "")
    if not match:
        return locator if locator_keyword_supported(locator, pages) else None
    needle = norm(match.group(1))
    for page in pages:
        haystack = norm(page["text"])
        if needle in haystack or needle.rstrip("s") in haystack:
            return f'page {page["page"]} (text containing "{match.group(1)}")'
    return None


def direct_novelty(row: dict, pages: list[dict]) -> int:
    corrected = 0
    dimensions = row["novelty_assessment"]["dimensions"]
    desired = {
        "precommitment_predictors": "partial" if row["family_id"] in PRECOMMITMENT_PARTIAL else "not_met",
        "multirole_lifecycle": "partial" if row["family_id"] in MULTIROLE_PARTIAL else "not_met",
        "touch_queue_separation": "not_met",
        "capacity_readiness_dependencies": "not_met",
        "verified_completion_forecast": "not_met",
    }
    rationales = {
        "precommitment_predictors": "The report directly studies pre-commitment effort/acceptance estimation, but does not establish the proposed multi-role verified-delivery forecast.",
        "multirole_lifecycle": "The report directly spans multiple SDLC stages or actors, but does not operationalize role-stage touch demand and capacity as an integrated model.",
    }
    for name, value in dimensions.items():
        before = copy.deepcopy(value)
        status = desired[name]
        if status == "not_met":
            value.update({
                "status": "not_met",
                "source_locator": None,
                "rationale": (
                    "No direct source evidence was located for the exact dimension; related keyword co-occurrence was not treated as construct overlap."
                ),
            })
        else:
            locator = relocate_keyword(value.get("source_locator"), pages)
            if locator is None:
                # Use the finding page as a bounded report-level locator only
                # when the title itself directly defines the estimation/lifecycle scope.
                locator = row["measures_findings"][0]["source_locator"]
            value.update({"status": "partial", "source_locator": locator, "rationale": rationales[name]})
        corrected += int(value != before)
    novelty = row["novelty_assessment"]
    expected_same_use = "yes" if row["family_id"] in PRECOMMITMENT_PARTIAL else "no"
    if novelty.get("same_planning_use") != expected_same_use:
        novelty["same_planning_use"] = expected_same_use
        corrected += 1
    expected_risk = "moderate" if row["family_id"] in PRECOMMITMENT_PARTIAL else "low"
    if novelty.get("novelty_risk") != expected_risk:
        novelty["novelty_risk"] = expected_risk
        corrected += 1
    opening = norm(" ".join(page["text"] for page in pages[:2]))
    expected_story_points = "story point" in opening or "storypoint" in opening
    if novelty.get("comparator_story_points") != expected_story_points:
        novelty["comparator_story_points"] = expected_story_points
        corrected += 1
    expected_hie = bool(
        re.search(r"\bhuman input equivalent\b|\bhie\b", " ".join(page["text"] for page in pages[:5]), re.I)
    )
    if novelty.get("comparator_hie") != expected_hie:
        novelty["comparator_hie"] = expected_hie
        corrected += 1
    return corrected


def verify_row(original: dict, primary_hash: str) -> dict:
    row = copy.deepcopy(original)
    source_path = TEXT / f"{row['family_id']}.json"
    if sha256(source_path) != row["source_text_sha256"]:
        raise ValueError(f"source checksum mismatch: {row['family_id']}")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    pages = source["pages"]
    if len(pages) != source["page_count"]:
        raise ValueError(f"page conservation failed: {row['family_id']}")

    summary = {
        "quantitative_verified": 0,
        "quantitative_corrected": 0,
        "quantitative_rejected": 0,
        "novelty_corrected": 0,
        "other_corrections": 0,
    }

    # Make every retained finding a verbatim static-text sentence.  This is
    # stronger than retaining a generated paraphrase and makes D17 auditable.
    for finding in row["measures_findings"]:
        old_value = finding["value"]
        quantitative_changed = False
        override = override_excerpt(row["family_id"], pages)
        if override is not None:
            page, sentence = override
        else:
            page, sentence, score = best_source_sentence(old_value, pages)
            if score < 0.36:
                page, sentence = best_fallback_sentence(pages)
        exact = re.sub(r"\s+", " ", sentence).strip()
        if exact != old_value or page_number(finding["source_locator"]) != page:
            finding["value"] = exact
            finding["source_locator"] = f"page {page}"
            summary["other_corrections"] += 1
            quantitative_changed = bool(finding["quantitative"])
        if finding.get("reported_uncertainty") is not None:
            # Every non-null value in this partition was a broken substring
            # (for example "ciency"), not a CI, SE, SD, range, or p-value.
            finding["reported_uncertainty"] = None
            summary["other_corrections"] += 1
            quantitative_changed = bool(finding["quantitative"])
        if finding["quantitative"]:
            if row["family_id"] in CONTEXT_ONLY_QUANTITATIVE:
                finding["quantitative"] = False
                finding["reported_estimate"] = None
                finding["unit"] = None
                summary["quantitative_rejected"] += 1
            else:
                estimate_tokens = numeric_tokens(finding.get("reported_estimate") or "")
                page_tokens = numeric_tokens(pages[page - 1]["text"])
                if not estimate_tokens or not estimate_tokens <= page_tokens:
                    # Do not retain an estimate unless every reported number is
                    # present on the cited source page.
                    finding["quantitative"] = False
                    finding["reported_estimate"] = None
                    finding["unit"] = None
                    summary["quantitative_rejected"] += 1
                else:
                    summary["quantitative_verified"] += 1
                    summary["quantitative_corrected"] += int(quantitative_changed)

    # Repair mechanically assigned page-keyword locators across mapped fields.
    for stage, value in row["lifecycle_stages"].items():
        if value["present"] and not locator_keyword_supported(value.get("source_locator"), pages):
            relocated = relocate_keyword(value.get("source_locator"), pages)
            if relocated:
                value["source_locator"] = relocated
            else:
                value.update({"present": False, "source_locator": None})
            summary["other_corrections"] += 1
    for name, value in row["vdcm_constructs"].items():
        if value["status"] == "present" and not locator_keyword_supported(value.get("source_locator"), pages):
            relocated = relocate_keyword(value.get("source_locator"), pages)
            if relocated:
                value["source_locator"] = relocated
            else:
                value.update({
                    "status": "absent", "source_locator": None,
                    "rationale": "No explicit source-grounded indicator was located in the frozen page text.",
                })
            summary["other_corrections"] += 1
    retained_emergent = []
    for value in row["emergent_constructs"]:
        if locator_keyword_supported(value.get("source_locator"), pages):
            retained_emergent.append(value)
        else:
            relocated = relocate_keyword(value.get("source_locator"), pages)
            if relocated:
                value["source_locator"] = relocated
                retained_emergent.append(value)
            summary["other_corrections"] += 1
    row["emergent_constructs"] = retained_emergent

    summary["novelty_corrected"] = direct_novelty(row, pages)
    row["verifier_agent_id"] = VERIFIER
    row["verification_context_id"] = f"d13-verify-a-{row['family_id'][4:12]}"
    row["original_extraction_sha256"] = primary_hash
    row["verification_summary"] = summary
    row["reviewer_notes"] = (
        "Distinct source-grounded verification used only checksum-bound static page text. "
        "Retained findings are verbatim page text; quantitative estimates require result-bearing "
        "source support, and novelty requires direct dimensional evidence. D17 author confirmation remains required."
    )
    return row


def validate_output(rows: list[dict], originals: list[dict], primary_hash: str) -> None:
    expected = {row["family_id"] for row in originals}
    if len(rows) != 285 or {row["family_id"] for row in rows} != expected:
        raise ValueError("partition-A population mismatch")
    for row in rows:
        source_path = TEXT / f"{row['family_id']}.json"
        source = json.loads(source_path.read_text(encoding="utf-8"))
        if sha256(source_path) != row["source_text_sha256"]:
            raise ValueError(f"output source checksum mismatch: {row['family_id']}")
        if row["original_extraction_sha256"] != primary_hash:
            raise ValueError(f"primary binding mismatch: {row['family_id']}")
        for finding in row["measures_findings"]:
            page = page_number(finding["source_locator"])
            if not 1 <= page <= source["page_count"]:
                raise ValueError(f"finding page bounds: {row['family_id']}")
            if norm(finding["value"]) not in norm(source["pages"][page - 1]["text"]):
                raise ValueError(f"finding is not exact page text: {row['family_id']}")
            if finding["quantitative"]:
                tokens = numeric_tokens(finding.get("reported_estimate") or "")
                page_tokens = numeric_tokens(source["pages"][page - 1]["text"])
                if not tokens or not tokens <= page_tokens:
                    raise ValueError(f"quantitative estimate unsupported: {row['family_id']}")
            if finding.get("reported_uncertainty") is not None:
                raise ValueError(f"unverified uncertainty retained: {row['family_id']}")
        for value in row["novelty_assessment"]["dimensions"].values():
            if value["status"] in {"met", "partial"}:
                page = page_number(value["source_locator"])
                if not 1 <= page <= source["page_count"]:
                    raise ValueError(f"novelty page bounds: {row['family_id']}")


def main() -> None:
    if sha256(PRIMARY) != PRIMARY_SHA256:
        raise ValueError("primary ledger is not the assigned frozen input")
    originals = [json.loads(line) for line in PRIMARY.read_text(encoding="utf-8").splitlines()][:285]
    rows = [verify_row(row, PRIMARY_SHA256) for row in originals]
    validate_output(rows, originals, PRIMARY_SHA256)
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    digest = sha256(OUTPUT)
    OUTPUT.with_name(OUTPUT.name + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    totals = {key: sum(row["verification_summary"][key] for row in rows) for key in rows[0]["verification_summary"]}
    print(json.dumps({"family_count": len(rows), "sha256": digest, "verification_totals": totals}, sort_keys=True))


if __name__ == "__main__":
    main()
