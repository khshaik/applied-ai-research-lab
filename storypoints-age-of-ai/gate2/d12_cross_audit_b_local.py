"""Blinded, contextual D12 cross-audit of lexicographic partition B.

Only the frozen D11 ledger, D11 screening packets, and checksum-bound static
page text are inputs. Primary appraisal outputs are never opened. Each score is
based on criterion-specific combinations in the surrounding source passage,
not a document-level keyword count.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from d12_appraise_part_a_local import FORMS, body_pages, read_jsonl, sha256


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
LEDGER = BASE / "d11/screening/final/fulltext_eligibility_decisions.jsonl"
PACKETS = BASE / "d11/screening"
OUT = BASE / "d12/audit_part_b_by_a.jsonl"


# A score of 2 requires at least one criterion-specific conjunction in the
# same page passage. A base indicator without such substantiation scores at
# most 1. This avoids upgrading a passing mention in background prose.
ADEQUATE: dict[str, list[list[str]]] = {
    "QM1": [[r"research questions?", r"contribution"], [r"\brq\s*[1-9]", r"we (?:investigate|evaluate|examine)"], [r"objective", r"we (?:conduct|present|report)"]],
    "QM2": [[r"(?:participants?|respondents?|developers?)", r"\bn\s*=\s*\d+|\b\d+\s+(?:participants?|respondents?|developers?)"], [r"sampling|recruit", r"participants?|respondents?|developers?"]],
    "QM3": [[r"gpt-?4|gpt-?3\.5|claude|github copilot|gemini", r"we (?:use|used|configure|configured)|temperature|prompt|exposure|experimental condition"], [r"large language model", r"model version|temperature|prompt design|experimental condition"]],
    "QM4": [[r"operationali[sz]|defined as", r"measure(?:d|ment)|metric|construct"], [r"questionnaire|instrument|scale", r"reliab|validat|cronbach"]],
    "QM5": [[r"control group|comparison group|baseline", r"randomi[sz]|matched|counterbalanc|within.subject|between.subject"], [r"confound|bias", r"control(?:led|ling)?|adjust(?:ed|ment)?"]],
    "QM6": [[r"regression|anova|wilcoxon|mann.whitney|mixed.effects", r"repeated measures|nested|distribution|normality|non.parametric|cluster"], [r"statistical analysis", r"confidence interval|effect size|p.value"]],
    "QM7": [[r"confidence interval|effect size|odds ratio|cohen.s d", r"not significant|significant|p\s*[<=>]|null"], [r"negative result|null result|no significant", r"confidence interval|effect size|standard deviation"]],
    "QM8": [[r"replication package|data (?:are|is) available|code (?:are|is) available", r"https?://|github|zenodo|doi"], [r"artifact|supplementary material", r"available|repository|appendix"]],
    "QM9": [[r"threats? to validity|limitations?", r"internal validity|external validity|construct validity|generaliz|selection bias"]],
    "QM10": [[r"funding|conflict(?:s)? of interest|competing interest", r"observed|simulat|modeled|modelled|synthetic|experiment"], [r"funded by|no conflict|no competing", r"data|study|analysis"]],
    "QL1": [[r"research questions?|purpose of this study", r"context|setting|developers?|organization"]],
    "QL2": [[r"sampling|recruit", r"participants?|interviewees?|developers?|roles?"], [r"participants?|interviewees?", r"\bn\s*=\s*\d+|\b\d+\s+(?:participants?|interviewees?|developers?)"]],
    "QL3": [[r"semi.structured interviews?|focus groups?|observations?", r"recorded|transcri|protocol|duration|data collection"]],
    "QL4": [[r"thematic analysis|grounded theory|open coding|axial coding", r"codebook|coder|iteration|saturation|analytic"]],
    "QL5": [[r"reflexiv|positionality|researcher bias", r"mitigat|address|discuss|role"]],
    "QL6": [[r"themes?", r"participants? (?:said|reported|described)|representative quote|quotation"], [r"coded excerpts?", r"finding|theme|claim"]],
    "QL7": [[r"triangulat|member check|peer debrief", r"participant|researcher|coder"], [r"two (?:authors|researchers|coders)|independent cod", r"agreement|resolve|discussion"]],
    "QL8": [[r"negative case|deviant case|contradict", r"theme|finding|analysis"], [r"limitations?|threats? to validity", r"sampling|bias|generaliz"]],
    "QL9": [[r"transferab|generaliz|external validity", r"context|setting|population|limited"]],
    "QL10": [[r"data (?:are|is) available|replication package|artifact", r"repository|https?://|supplementary"], [r"conflict(?:s)? of interest|competing interest|funding", r"disclos|none|supported"]],
    "SR1": [[r"systematic literature review|systematic mapping|scoping review", r"protocol|prisma|guideline|method"]],
    "SR2": [[r"scopus|web of science|ieee xplore|acm digital library", r"scopus|web of science|ieee xplore|acm digital library|springer|science direct"]],
    "SR3": [[r"search string|search quer", r"search date|searched (?:in|on|between|through)|\b20\d\d\b"]],
    "SR4": [[r"two reviewers|independent(?:ly)? screen|second reviewer", r"agreement|disagreement|kappa|resolve"]],
    "SR5": [[r"inclusion criteria", r"exclusion criteria"], [r"eligibility criteria", r"included|excluded"]],
    "SR6": [[r"quality assessment|quality appraisal|risk of bias|critical appraisal", r"checklist|score|criteria|tool"]],
    "SR7": [[r"deduplicat|duplicate studies|study overlap|publication version", r"remove|merge|retain|screen"]],
    "SR8": [[r"data extraction", r"synthesis|coding|themes?|meta.analysis"], [r"narrative synthesis|thematic synthesis|meta.analysis", r"studies|findings|evidence"]],
    "SR9": [[r"heterogeneity|evidence strength|certainty of evidence|quality of evidence", r"address|assess|rate|sensitivity"]],
    "SR10": [[r"limitations?", r"search date|updated? (?:to|on|through)|artifact|replication package|supplementary"]],
    "CF1": [[r"problem statement|we address|challenge", r"scope|boundary|context|condition"]],
    "CF2": [[r"prior work|related work|literature|theor", r"evidence|studies|research|framework"]],
    "CF3": [[r"we define|defined as|construct", r"dimension|component|relationship|operational"]],
    "CF4": [[r"mechanism|causal|feedback loop|process model", r"leads to|results in|because|therefore|relationship"]],
    "CF5": [[r"compared (?:with|to)|alternative|existing framework|related approaches", r"difference|whereas|unlike|baseline|advantage"]],
    "CF6": [[r"proposition|hypothes|falsif", r"evaluat|test|validat|future study"], [r"case study|experiment|evaluation", r"result|finding|validation"]],
    "CF7": [[r"implementation cost|overhead|trade.off|failure mode|risk", r"mitigat|limitation|cost|failure|adoption"]],
    "CF8": [[r"we assume|assumption|conceptual|hypothesized", r"evidence|empirical|validation|future work"]],
    "CF9": [[r"limitations?|generaliz|boundary", r"future work|context|scope|validity"]],
    "CF10": [[r"conflict(?:s)? of interest|competing interest|funding", r"artifact|github|source code|commercial|trademark"], [r"artifact|source code", r"available|repository|https?://"]],
    "AA1": [[r"authors?|affiliation|organization|institution", r"role|expert|research|professional"]],
    "AA2": [[r"method|sample|data", r"analysis|reference|validation|source"]],
    "AA3": [[r"scope|population|dataset|participants?|case stud", r"include|cover|range|context"]],
    "AA4": [[r"limitations?|conflict|funding|sponsor|trade.off", r"disclos|bias|risk|interest"]],
    "AA5": [[r"20(?:1[0-9]|2[0-9])", r"version|updated|published|date"]],
    "AA6": [[r"implication|contribution|impact|recommend|finding", r"practice|organization|developer|delivery"]],
}


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def body_with_refs_removed(raw_pages: list[dict]) -> list[dict]:
    # Reuse the conservative reference cutoff, then remove obvious reference-
    # list tails within a page so citations do not satisfy appraisal criteria.
    pages = body_pages(raw_pages)
    cleaned = []
    for p in pages:
        text = p["text"]
        m = re.search(r"\n\s*(?:REFERENCES|BIBLIOGRAPHY)\s*\n", text, re.I)
        cleaned.append({"page": p["page"], "text": text[: m.start()] if m else text})
    return cleaned


def classify_cross(title: str, pages: list[dict], stratum: str) -> tuple[str, str, str]:
    """Classify design without treating phrases such as 'review of code' as reviews."""
    if stratum in {"grey", "practitioner", "grey_practitioner"}:
        return "grey_aacods", "practitioner_or_grey_report", "conceptual"
    title_low = title.lower()
    lead = (title + "\n" + "\n".join(p["text"] for p in pages[:5])).lower()
    secondary = (
        re.search(r"systematic (?:literature )?(?:review|mapping)|mapping study|scoping review", title_low)
        or re.search(r"^(?:a |an )?(?:comprehensive )?(?:survey|review) of\b", title_low)
        or re.search(r"we (?:conduct|conducted|perform|performed|undertook) (?:a |an )?(?:systematic|scoping|mapping) (?:literature )?(?:review|study)|this systematic (?:literature )?review", lead)
    )
    qualitative = (
        re.search(r"qualitative|interview", title_low)
        or re.search(r"we (?:conduct|conducted|perform|performed) (?:\d+ |a |an )?(?:semi.structured )?interviews?|participants? (?:were )?interviewed|our thematic analysis|we used grounded theory", lead)
    )
    empirical = re.search(r"controlled experiment|randomi[sz]ed|participants?|dataset|repositories|case stud(?:y|ies)|survey(?:ed)?|empirical stud|we evaluat|we conduct", lead)
    conceptual = re.search(r"conceptual|position paper|vision paper|perspective|roadmap|manifesto|white paper|reference architecture|framework|taxonomy|challenges", lead)
    if secondary:
        return "secondary_review", "systematic_or_structured_secondary_review", "conceptual"
    if re.search(r"\b(?:vision|position|conceptual|perspective|manifesto|white) paper\b", lead[:5000]):
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    if qualitative:
        return "qualitative", "qualitative_interview_or_observational_study", "self-reported"
    if re.search(r"\b(?:comparison|comparative|experiment|evaluation|case study|empirical)\b", title_low):
        return "quantitative_mixed", "empirical_quantitative_or_mixed_study", "observed"
    if conceptual and not empirical:
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    if re.search(r"survey(?:ed)?|questionnaire|self.report", lead) and not re.search(r"experiment|repository|mining|telemetry|log data", lead):
        return "quantitative_mixed", "survey_or_mixed_method_study", "self-reported"
    if re.search(r"simulation|synthetic|benchmark|modeled|modelled", lead) and not re.search(r"participants?|interview|survey", lead):
        return "quantitative_mixed", "modeled_or_benchmark_evaluation", "modeled"
    return "quantitative_mixed", "empirical_quantitative_or_mixed_study", "observed"


def page_matches(text: str, patterns: list[str]) -> list[re.Match]:
    found = []
    for pattern in patterns:
        found.extend(re.finditer(pattern, text, re.I))
    return found


def criterion_base_patterns(cid: str, patterns: list[str]) -> list[str]:
    adjusted = list(patterns)
    if cid in {"QM1", "QL1"}:
        adjusted.extend([r"(?:this|the) (?:paper|study) (?:proposes|presents|develops|reports|examines|reinvents)", r"aim of this (?:paper|study)", r"objective of this (?:paper|study)"])
    if cid == "QM8":
        # Merely calling a result "reproducible" is not materials or
        # replication detail; require an actual artifact/availability signal.
        adjusted = [p for p in adjusted if p != r"reproduc"]
    return adjusted


def excerpt(text: str, match: re.Match | None) -> str:
    if not text:
        return "[no extractable text on the anchor page]"
    start = max(0, (match.start() if match else 0) - 100)
    end = min(len(text), (match.end() if match else 0) + 180)
    words = normalize(text[start:end]).split()
    if len(words) > 22:
        words = words[:22]
    return " ".join(words).replace('"', "'")


def contextual_score(pages: list[dict], criterion: tuple[str, str, list[str]]) -> dict:
    cid, label, base_patterns = criterion
    base_patterns = criterion_base_patterns(cid, base_patterns)
    best = None
    for p in pages:
        text = p["text"]
        base = page_matches(text, base_patterns)
        if not base:
            continue
        adequate = False
        adequate_match = None
        for conjunction in ADEQUATE[cid]:
            conjunct_matches = [page_matches(text, [pat]) for pat in conjunction]
            if all(conjunct_matches):
                # Require conjunction evidence to be reasonably local within
                # a page, not disconnected occurrences in unrelated sections.
                positions = [matches[0].start() for matches in conjunct_matches]
                if max(positions) - min(positions) <= 600:
                    adequate = True
                    adequate_match = conjunct_matches[0][0]
                    break
        candidate = (2 if adequate else 1, len(base), p["page"], adequate_match or base[0], text)
        if best is None or candidate[:2] > best[:2]:
            best = candidate
    if best is None:
        anchor = pages[0] if pages else {"page": 1, "text": ""}
        last = pages[-1]["page"] if pages else anchor["page"]
        return {
            "criterion_id": cid,
            "criterion": label,
            "score": 0,
            "source_locator": f"page {anchor['page']}",
            "justification": f"Complete pages {anchor['page']}-{last} were searched; no passage substantively addressing {label} was located. Page {anchor['page']} is the document anchor.",
        }
    score, _, page, match, text = best
    strength = "substantively satisfies" if score == 2 else "partially addresses"
    return {
        "criterion_id": cid,
        "criterion": label,
        "score": score,
        "source_locator": f"page {page}",
        "justification": f"Page {page} {strength} the criterion in context: \"{excerpt(text, match)}\"",
    }


def appraise(meta: dict, ordinal: int) -> dict:
    source = ROOT / meta["extracted_text_path"]
    source_hash = sha256(source)
    if source_hash != meta["extracted_text_sha256"]:
        raise ValueError(f"source checksum mismatch: {meta['family_id']}")
    extracted = json.loads(source.read_text(encoding="utf-8"))
    pages = body_with_refs_removed(extracted["pages"])
    body_text = "\n".join(p["text"] for p in pages).lower()
    form, design_type, nature = classify_cross(meta.get("title", ""), pages, meta.get("evidence_stratum_candidate", ""))
    criteria = [contextual_score(pages, item) for item in FORMS[form]]
    points = sum(c["score"] for c in criteria)
    applicable = 2 * len(criteria)
    percent = round(100 * points / applicable, 1)
    scores = {c["criterion_id"]: c["score"] for c in criteria}
    flaw = None
    provenance_signal = re.search(r"method(?:ology)?|case stud(?:y|ies)|case materials?|dataset|participants?|sample|experiment|evaluation", body_text)
    if form == "quantitative_mixed" and scores["QM2"] == scores["QM4"] == scores["QM6"] == 0 and not provenance_signal:
        flaw = "no inspectable data provenance"
    elif form == "qualitative" and scores["QL2"] == scores["QL3"] == scores["QL4"] == 0 and not provenance_signal:
        flaw = "no inspectable data provenance"
    elif form == "secondary_review" and scores["SR1"] == scores["SR3"] == scores["SR5"] == 0:
        flaw = "unverifiable primary claim"
    elif form == "conceptual_framework" and scores["CF2"] == scores["CF3"] == scores["CF6"] == 0:
        flaw = "unverifiable primary claim"
    critical = flaw is not None
    band = "low_contextual" if critical or percent < 50 else ("moderate" if percent < 75 else "high")
    return {
        "family_id": meta["family_id"],
        "record_id": meta["record_id"],
        "appraiser_agent_id": "d12-cross-auditor-a-v1",
        "review_context_id": f"d12-cross-auditor-a-{ordinal:04d}",
        "source_text_sha256": source_hash,
        "appraisal_form": form,
        "design_type": design_type,
        "evidence_nature": nature,
        "criteria": criteria,
        "points_awarded": points,
        "applicable_points": applicable,
        "percent": percent,
        "critical_flaw": critical,
        "critical_flaw_basis": flaw,
        "evidence_band": band,
        "overall_notes": "Independent blinded cross-audit under frozen Section 13. Quality controls evidentiary weight only; technical quality is not cognitive-load validation.",
        "security_attestation": "Local D11 ledger, packet metadata, and checksum-bound static extracted text only; no primary-B appraisal, merged appraisal, network, Git/history, environment/secrets, credentials, package installation, PDF execution, or embedded content was accessed.",
    }


def validate(rows: list[dict], expected: list[str], meta: dict[str, dict]) -> None:
    if len(rows) != 285 or [r["family_id"] for r in rows] != expected:
        raise ValueError("partition B population/order mismatch")
    if len({r["review_context_id"] for r in rows}) != 285:
        raise ValueError("review contexts are not unique")
    for row in rows:
        if row["appraiser_agent_id"] != "d12-cross-auditor-a-v1":
            raise ValueError("wrong appraiser identity")
        source = ROOT / meta[row["family_id"]]["extracted_text_path"]
        raw = source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["source_text_sha256"]:
            raise ValueError(f"hash mismatch: {row['family_id']}")
        page_numbers = {int(p["page"]) for p in json.loads(raw)["pages"]}
        expected_n = 6 if row["appraisal_form"] == "grey_aacods" else 10
        if len(row["criteria"]) != expected_n:
            raise ValueError(f"criterion count: {row['family_id']}")
        for c in row["criteria"]:
            if c["score"] not in {0, 1, 2}:
                raise ValueError(f"score: {row['family_id']}")
            match = re.fullmatch(r"page (\d+)", c["source_locator"])
            if not match or int(match.group(1)) not in page_numbers:
                raise ValueError(f"locator: {row['family_id']}")
        points = sum(c["score"] for c in row["criteria"])
        if points != row["points_awarded"] or row["applicable_points"] != expected_n * 2:
            raise ValueError(f"arithmetic: {row['family_id']}")
        pct = round(100 * points / row["applicable_points"], 1)
        expected_band = "low_contextual" if row["critical_flaw"] or pct < 50 else ("moderate" if pct < 75 else "high")
        if pct != row["percent"] or expected_band != row["evidence_band"]:
            raise ValueError(f"percentage/band: {row['family_id']}")
        if row["critical_flaw_basis"] not in {None, "no inspectable data provenance", "fatal design-outcome mismatch", "unverifiable primary claim"}:
            raise ValueError(f"critical flaw: {row['family_id']}")


def main() -> None:
    included = sorted(r["family_id"] for r in read_jsonl(LEDGER) if r.get("final_status") == "included_full_text")
    expected = included[285:]
    if len(included) != 570 or len(expected) != 285:
        raise ValueError("D11 included population is not the frozen 570/285 split")
    wanted = set(expected)
    meta = {}
    for packet in sorted(PACKETS.glob("fulltext_packet_*.jsonl")):
        for row in read_jsonl(packet):
            if row["family_id"] in wanted:
                meta[row["family_id"]] = row
    if set(meta) != wanted:
        raise ValueError(f"missing packet metadata: {sorted(wanted - set(meta))}")
    rows = [appraise(meta[fid], i) for i, fid in enumerate(expected, 1)]
    validate(rows, expected, meta)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    validate(read_jsonl(OUT), expected, meta)
    print(json.dumps({
        "rows": len(rows),
        "forms": dict(Counter(r["appraisal_form"] for r in rows)),
        "bands": dict(Counter(r["evidence_band"] for r in rows)),
        "natures": dict(Counter(r["evidence_nature"] for r in rows)),
        "critical_flaws": dict(Counter(r["critical_flaw_basis"] for r in rows if r["critical_flaw"])),
        "sha256": sha256(OUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
