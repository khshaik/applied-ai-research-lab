"""Resolve D12 appraisal disputes from checksum-bound static text.

This adjudicator recomputes every disputed appraisal from the frozen Section 13
form.  The primary and cross-audit rows identify the contested judgments and
candidate locators; their scores are not averaged and neither has precedence.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate2.d12_appraise_part_a_local import FORMS, body_pages
from gate2.d12_cross_audit_b_local import ADEQUATE


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816/d12/reconciliation"
PACKET = BASE / "appraisal_disputes.jsonl"
OUTPUT = BASE / "adjudicated_appraisals.jsonl"
AGENT_ID = "d12-quality-adjudicator-v1"
ALLOWED_BASES = {
    "none",
    "no_inspectable_data_provenance",
    "fatal_design_outcome_mismatch",
    "unverifiable_primary_claim",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean_pages(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pages = body_pages(raw)
    cleaned = []
    for page in pages:
        text = page.get("text", "")
        cutoff = re.search(r"\n\s*(?:references|bibliography)\s*\n", text, re.I)
        cleaned.append({"page": int(page["page"]), "text": text[: cutoff.start()] if cutoff else text})
    return cleaned


def _declared_design(title: str, pages: list[dict[str, Any]], stratum: str) -> tuple[str, str, str]:
    """Select one frozen form from explicit design declarations, not prior scores."""
    if stratum in {"grey", "practitioner", "grey_practitioner"}:
        return "grey_aacods", "practitioner_or_grey_report", "conceptual"
    title_l = title.lower()
    opening = "\n".join(p["text"] for p in pages[:6]).lower()
    lead = title_l + "\n" + opening
    secondary = bool(
        re.search(r"systematic (?:literature )?(?:review|mapping)|scoping review|mapping study", title_l)
        or re.search(r"\b(?:survey|review) of\b", title_l)
        or re.search(
            r"we (?:conduct|conducted|perform|performed|undertook) (?:a |an )?"
            r"(?:systematic|scoping|mapping) (?:literature )?(?:review|study)", opening
        )
    )
    qual = bool(re.search(r"semi.?structured interviews?|focus groups?|thematic analysis|grounded theory|qualitative stud", lead))
    quantitative = bool(re.search(
        r"experiment|randomi[sz]|telemetry|repository mining|dataset|statistical|regression|anova|"
        r"wilcoxon|mann.?whitney|quantitative|jira|sonarqube|performance metric", lead
    ))
    conceptual = bool(re.search(
        r"\b(?:conceptual|position|vision|perspective|manifesto|white) paper\b|"
        r"reference architecture|conceptual framework", lead
    ))
    evaluated = bool(re.search(r"we evaluat|evaluation|case stud|experiment|participants?|dataset", lead))
    if secondary:
        return "secondary_review", "systematic_or_structured_secondary_review", "conceptual"
    if qual and not quantitative:
        return "qualitative", "qualitative_interview_or_observational_study", "self_reported"
    if conceptual and not evaluated:
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    if qual and quantitative:
        return "quantitative_mixed", "mixed_method_empirical_evaluation", "mixed"
    if re.search(r"simulation|synthetic|benchmark|modeled|modelled", lead) and not re.search(r"participants?|survey|interview", lead):
        return "quantitative_mixed", "modeled_or_benchmark_evaluation", "modeled"
    if re.search(r"survey|questionnaire|self.?report", lead) and not quantitative:
        return "quantitative_mixed", "survey_evaluation", "self_reported"
    if conceptual and not quantitative:
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    return "quantitative_mixed", "empirical_quantitative_or_mixed_evaluation", "observed"


def _resolved_design(packet_row: dict[str, Any], pages: list[dict[str, Any]]) -> tuple[str, str, str]:
    """Preserve an undisputed form; independently resolve the 104 form disputes."""
    primary = packet_row["primary_appraisal"]["appraisal_form"]
    audit = packet_row["cross_audit_appraisal"]["appraisal_form"]
    family = packet_row["family"]
    title = family.get("title", "")
    lead = (title + "\n" + "\n".join(page["text"] for page in pages[:6])).lower()
    if primary == audit:
        form = primary
        if form == "grey_aacods":
            return form, "practitioner_or_grey_report", "conceptual"
        if form == "secondary_review":
            return form, "systematic_or_structured_secondary_review", "conceptual"
        if form == "qualitative":
            return form, "qualitative_interview_or_observational_study", "self_reported"
        if form == "conceptual_framework":
            return form, "conceptual_or_framework_paper", "conceptual"
        qualitative = bool(re.search(r"interviews?|survey|questionnaire|self.?report", lead))
        observed = bool(re.search(r"telemetry|repository|dataset|experiment|benchmark|performance metric", lead))
        nature = "mixed" if qualitative and observed else ("self_reported" if qualitative else ("modeled" if re.search(r"simulation|synthetic|modeled|modelled", lead) else "observed"))
        return form, "empirical_quantitative_or_mixed_evaluation", nature

    title_l = title.lower()
    if family.get("evidence_stratum_candidate") in {"grey", "practitioner", "grey_practitioner"}:
        return "grey_aacods", "practitioner_or_grey_report", "conceptual"
    if re.search(r"systematic (?:literature )?(?:review|map(?:ping)?|analysis)|scoping review|(?:systematic )?map(?:ping)? study|meta.analysis|rapid review|\ba review\b|\b(?:survey|review) (?:of|on)\b|literature review|comprehensive review", title_l):
        return "secondary_review", "systematic_or_structured_secondary_review", "conceptual"
    if re.search(r"interview|perceptions?|opinions?|experiences?|early adopters|developer.s perspective|qualitative|conversations?|engagement", title_l) or (
        re.search(r"semi.?structured interviews?|thematic analysis|grounded theory", lead)
        and not re.search(r"quantitative telemetry|mixed.method|design science", lead)
    ):
        return "qualitative", "qualitative_interview_or_observational_study", "self_reported"
    empirical_title = bool(re.search(r"empirical|evaluat|quantif|case stud|experiment|measurement|assessment|impact", title_l))
    conceptual_title = bool(re.search(
        r"framework|architecture|proposal|governance|position|perspective|opportunities|pitfalls|"
        r"considerations|rethinking|future of|control plane|formalizing|workflow-centric|reference model", title_l
    ))
    if conceptual_title and not empirical_title:
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    return _declared_design(title, pages, family.get("evidence_stratum_candidate", ""))


def _locators(row: dict[str, Any]) -> set[int]:
    pages: set[int] = set()
    for item in row.get("criteria_scores", row.get("criteria", [])):
        value = str(item.get("source_locator", item.get("page_locator", "")))
        match = re.search(r"(?:page|p\.)\s*(\d+)", value, re.I)
        if match:
            pages.add(int(match.group(1)))
    return pages


def _hits(text: str, patterns: list[str]) -> list[re.Match[str]]:
    hits: list[re.Match[str]] = []
    for pattern in patterns:
        hits.extend(re.finditer(pattern, text, re.I))
    return hits


def _snippet(text: str, start: int) -> str:
    left, right = max(0, start - 120), min(len(text), start + 260)
    words = re.sub(r"\s+", " ", text[left:right]).strip().split()
    return " ".join(words[:24]).replace('"', "'")


def _score_criterion(
    pages: list[dict[str, Any]], criterion: tuple[str, str, list[str]], candidate_pages: set[int]
) -> dict[str, Any]:
    cid, label, base_patterns = criterion
    best: tuple[int, int, int, int, str, str] | None = None
    # The score is rederived from criterion-specific co-located evidence.
    # Prior locators only break equal-evidence ties so they cannot determine a score.
    for page in pages:
        text = page["text"]
        bases = _hits(text, base_patterns)
        adequate_match: re.Match[str] | None = None
        adequate = False
        for conjunction in ADEQUATE[cid]:
            groups = [_hits(text, [pattern]) for pattern in conjunction]
            if all(groups):
                positions = [group[0].start() for group in groups]
                if max(positions) - min(positions) <= 700:
                    adequate = True
                    adequate_match = groups[0][0]
                    break
        score = 2 if adequate else (1 if bases else 0)
        evidence_count = len(bases)
        tie = 1 if int(page["page"]) in candidate_pages else 0
        anchor = adequate_match or (bases[0] if bases else None)
        candidate = (score, evidence_count, tie, -int(page["page"]), text, _snippet(text, anchor.start()) if anchor else "")
        if best is None or candidate[:4] > best[:4]:
            best = candidate
    assert best is not None
    score, _, _, neg_page, _, snippet = best
    page_num = -neg_page
    if score == 2:
        justification = f"Page {page_num} contains co-located, criterion-specific evidence: \"{snippet}\""
    elif score == 1:
        justification = f"Page {page_num} contains partial evidence but not all adequacy elements: \"{snippet}\""
    else:
        first, last = pages[0]["page"], pages[-1]["page"]
        page_num = first
        justification = f"Pages {first}-{last} were searched; no criterion-specific evidence was located."
    return {
        "criterion_id": cid,
        "criterion": label,
        "score": score,
        "source_locator": f"page {page_num}",
        "justification": justification,
    }


def _critical(form: str, scores: dict[str, int], body: str) -> str:
    provenance = bool(re.search(r"method(?:ology)?|dataset|sample|participants?|experiment|evaluation|case stud", body, re.I))
    if form == "quantitative_mixed" and scores["QM2"] == scores["QM4"] == scores["QM6"] == 0 and not provenance:
        return "no_inspectable_data_provenance"
    if form == "qualitative" and scores["QL2"] == scores["QL3"] == scores["QL4"] == 0 and not provenance:
        return "no_inspectable_data_provenance"
    if form == "secondary_review" and scores["SR1"] == scores["SR3"] == scores["SR5"] == 0:
        return "unverifiable_primary_claim"
    if form == "conceptual_framework" and scores["CF2"] == scores["CF3"] == scores["CF6"] == 0:
        return "unverifiable_primary_claim"
    return "none"


def adjudicate(packet_row: dict[str, Any], ordinal: int) -> dict[str, Any]:
    family = packet_row["family"]
    source = ROOT / family["extracted_text_path"]
    source_hash = sha256(source)
    if source_hash != family["extracted_text_sha256"]:
        raise ValueError(f"source checksum mismatch: {family['family_id']}")
    extracted = json.loads(source.read_text(encoding="utf-8"))
    pages = clean_pages(extracted["pages"])
    page_numbers = {p["page"] for p in pages}
    prior_candidates = (_locators(packet_row["primary_appraisal"]) | _locators(packet_row["cross_audit_appraisal"])) & page_numbers
    form, design_type, nature = _resolved_design(packet_row, pages)
    criteria = [_score_criterion(pages, item, prior_candidates) for item in FORMS[form]]
    points = sum(item["score"] for item in criteria)
    applicable = 2 * len(criteria)
    percent = round(100 * points / applicable, 1)
    scores = {item["criterion_id"]: item["score"] for item in criteria}
    basis = _critical(form, scores, "\n".join(p["text"] for p in pages))
    critical = basis != "none"
    band = "low_contextual" if critical or percent < 50 else ("moderate" if percent < 75 else "high")
    primary = packet_row["primary_appraisal"]
    audit = packet_row["cross_audit_appraisal"]
    return {
        "family_id": family["family_id"],
        "record_id": family["record_id"],
        "adjudicator_agent_id": AGENT_ID,
        "review_context_id": f"d12-quality-adjudication-{ordinal:04d}-{source_hash[:12]}",
        "source_text_sha256": source_hash,
        "evidence_stratum": family.get("evidence_stratum_candidate", ""),
        "appraisal_form": form,
        "design_type": design_type,
        "data_nature": nature,
        "criteria_scores": criteria,
        "points_awarded": points,
        "applicable_points": applicable,
        "percent_score": percent,
        "critical_flaw": critical,
        "critical_flaw_basis": basis,
        "evidence_band": band,
        "dispute_reasons": list(packet_row.get("dispute_reasons", [])),
        "compared_source_locators": {
            "primary_pages": sorted(_locators(primary)),
            "cross_audit_pages": sorted(_locators(audit)),
        },
        "resolution_rationale": (
            f"Recomputed from the frozen Section 13 {form} form and checksum-bound full text after comparing "
            f"the primary ({primary['appraisal_form']}, {primary['points_awarded']}/{primary['applicable_points']}) "
            f"and cross-audit ({audit['appraisal_form']}, {audit['points_awarded']}/{audit['applicable_points']}) "
            f"forms, locators, and stated reasons. No averaging, vote, or technical-quality-to-cognitive-load inference was used."
        ),
        "overall_notes": "Quality controls evidentiary weight only and does not alter D11 eligibility.",
        "security_attestation": {
            "local_only": True,
            "network_used": False,
            "git_or_history_inspected": False,
            "environment_or_secrets_inspected": False,
            "credentials_accessed": False,
            "packages_installed": False,
            "pdf_executed": False,
            "source_scope": "D12 dispute packet and checksum-bound static D11 extracted text only",
        },
    }


def validate(rows: list[dict[str, Any]], packet_rows: list[dict[str, Any]]) -> None:
    expected = [row["family"]["family_id"] for row in packet_rows]
    if len(rows) != 567 or [row.get("family_id") for row in rows] != expected or len(set(expected)) != 567:
        raise ValueError("D12 adjudication population/order mismatch")
    if len({row["review_context_id"] for row in rows}) != 567:
        raise ValueError("D12 adjudication contexts are not unique")
    for row, packet_row in zip(rows, packet_rows):
        family = packet_row["family"]
        if row["record_id"] != family["record_id"] or row["adjudicator_agent_id"] != AGENT_ID:
            raise ValueError(f"identity mismatch: {row['family_id']}")
        source = ROOT / family["extracted_text_path"]
        if row["source_text_sha256"] != sha256(source) or row["source_text_sha256"] != family["extracted_text_sha256"]:
            raise ValueError(f"source hash mismatch: {row['family_id']}")
        extracted = json.loads(source.read_text(encoding="utf-8"))
        page_numbers = {int(page["page"]) for page in extracted["pages"]}
        form = row["appraisal_form"]
        criteria = row["criteria_scores"]
        if form not in FORMS or len(criteria) != len(FORMS[form]):
            raise ValueError(f"form/criterion count mismatch: {row['family_id']}")
        expected_ids = [item[0] for item in FORMS[form]]
        if [item["criterion_id"] for item in criteria] != expected_ids:
            raise ValueError(f"criterion identity mismatch: {row['family_id']}")
        for item in criteria:
            match = re.fullmatch(r"page (\d+)", item["source_locator"])
            if item["score"] not in {0, 1, 2} or not item["justification"] or not match or int(match.group(1)) not in page_numbers:
                raise ValueError(f"invalid criterion evidence: {row['family_id']}/{item['criterion_id']}")
        points = sum(item["score"] for item in criteria)
        applicable = 2 * len(criteria)
        percent = round(100 * points / applicable, 1)
        if (row["points_awarded"], row["applicable_points"], row["percent_score"]) != (points, applicable, percent):
            raise ValueError(f"arithmetic mismatch: {row['family_id']}")
        basis = row["critical_flaw_basis"]
        if basis not in ALLOWED_BASES or row["critical_flaw"] != (basis != "none"):
            raise ValueError(f"critical flaw mismatch: {row['family_id']}")
        band = "low_contextual" if row["critical_flaw"] or percent < 50 else ("moderate" if percent < 75 else "high")
        if row["evidence_band"] != band:
            raise ValueError(f"band mismatch: {row['family_id']}")
        security = row["security_attestation"]
        if not security["local_only"] or any(security[key] for key in (
            "network_used", "git_or_history_inspected", "environment_or_secrets_inspected",
            "credentials_accessed", "packages_installed", "pdf_executed",
        )):
            raise ValueError(f"security attestation invalid: {row['family_id']}")


def main() -> None:
    packets = read_jsonl(PACKET)
    if len(packets) != 567:
        raise ValueError("frozen dispute packet does not contain 567 rows")
    rows = [adjudicate(packet, ordinal) for ordinal, packet in enumerate(packets, 1)]
    validate(rows, packets)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    validate(read_jsonl(OUTPUT), packets)
    digest = sha256(OUTPUT)
    OUTPUT.with_name(OUTPUT.name + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(rows),
        "forms": dict(sorted(Counter(row["appraisal_form"] for row in rows).items())),
        "bands": dict(sorted(Counter(row["evidence_band"] for row in rows).items())),
        "critical_flaws": dict(sorted(Counter(row["critical_flaw_basis"] for row in rows if row["critical_flaw"]).items())),
        "sha256": digest,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
