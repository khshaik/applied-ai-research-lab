"""Source-grounded D12 appraisal for the lexicographic first half.

This is deliberately local-only. It reads the checksum-bound D11 packet and
static page text; it does not open PDFs, use the network, inspect Git, or read
environment variables. Scores are conservative text-evidence checks under the
frozen protocol's Section 13 forms and are intended for independent audit.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
LEDGER = BASE / "d11/screening/final/fulltext_eligibility_decisions.jsonl"
PACKET_DIR = BASE / "d11/screening"
OUT = BASE / "d12/appraisal_part_a.jsonl"


FORMS = {
    "quantitative_mixed": [
        ("QM1", "clear research question and contribution", [r"research question", r"we (?:investigate|study|evaluate|examine)", r"our contribution"]),
        ("QM2", "context, participants/tasks, and sampling described", [r"participants?", r"respondents?", r"recruit(?:ed|ing|ment)", r"\bn\s*=\s*\d+", r"sample(?:d| size| of)", r"dataset", r"repositories", r"tasks?"] ),
        ("QM3", "AI tool/model/version and exposure described", [r"gpt-?4", r"gpt-?3\.5", r"chatgpt", r"github copilot", r"large language model", r"model version", r"temperature"]),
        ("QM4", "constructs and measures operationalized with validity evidence", [r"measure(?:d|ment)", r"operationali[sz]", r"metric", r"validity", r"questionnaire", r"instrument"]),
        ("QM5", "design addresses bias/confounding and comparator where needed", [r"control group", r"baseline", r"randomi[sz]", r"counterbalanc", r"confound", r"matched", r"comparison group"]),
        ("QM6", "analysis matches design and repeated/nested structure", [r"regression", r"statistical", r"mixed.effects", r"anova", r"wilcoxon", r"mann.whitney", r"confidence interval", r"hypothesis test"]),
        ("QM7", "uncertainty/effect sizes and negative/null outcomes reported", [r"confidence interval", r"effect size", r"p\s*[<=>]", r"not significant", r"no significant", r"null result", r"standard deviation"]),
        ("QM8", "data/code/materials or replication detail available", [r"replication package", r"source code", r"data (?:are|is) available", r"artifact", r"github\.com", r"supplementary material", r"reproduc"]),
        ("QM9", "limitations and validity threats discussed", [r"threats? to validity", r"limitations?", r"external validity", r"internal validity"]),
        ("QM10", "funding/conflicts/relationships and modeled-versus-observed transparency", [r"conflict(?:s)? of interest", r"competing interest", r"funding", r"acknowledg", r"observed", r"simulat", r"synthetic"]),
    ],
    "qualitative": [
        ("QL1", "research purpose and context clear", [r"research question", r"purpose of this study", r"we (?:investigate|explore|study)", r"context"]),
        ("QL2", "sampling and participant roles justified", [r"participants?", r"sampling", r"recruited", r"developer roles?", r"interviewees?"]),
        ("QL3", "data collection transparent", [r"semi.structured interview", r"interview protocol", r"focus group", r"data collection", r"recorded", r"transcri"]),
        ("QL4", "analytic procedure systematic and traceable", [r"thematic analysis", r"grounded theory", r"open coding", r"axial coding", r"codebook", r"qualitative analysis"]),
        ("QL5", "researcher reflexivity or bias addressed", [r"reflexiv", r"researcher bias", r"positionality", r"observer bias", r"interpretive bias"]),
        ("QL6", "evidence supports themes and claims", [r"representative quote", r"participants? (?:said|reported|described)", r"theme", r"quotation", r"coded excerpts?"]),
        ("QL7", "triangulation or member/peer checks", [r"triangulat", r"member check", r"peer debrief", r"inter.rater", r"two (?:authors|researchers|coders)"]),
        ("QL8", "negative cases and limitations considered", [r"negative case", r"deviant case", r"limitations?", r"threats? to validity", r"contradict"]),
        ("QL9", "transferability boundaries stated", [r"transferab", r"generaliz", r"external validity", r"limited to", r"context.specific"]),
        ("QL10", "materials availability and conflicts disclosed", [r"data (?:are|is) available", r"replication package", r"supplementary", r"conflict(?:s)? of interest", r"competing interest", r"funding", r"artifact"]),
    ],
    "secondary_review": [
        ("SR1", "protocol or explicit method", [r"review protocol", r"systematic literature review", r"systematic mapping", r"prisma", r"review method"]),
        ("SR2", "multiple appropriate databases", [r"scopus", r"web of science", r"ieee xplore", r"acm digital library", r"digital libraries", r"databases"]),
        ("SR3", "reproducible full search strings and dates", [r"search string", r"search quer", r"search terms", r"search date", r"searched (?:in|on|between)"]),
        ("SR4", "duplicate screening or reliability procedure", [r"two reviewers", r"independent(?:ly)? screen", r"inter.rater", r"cohen.s kappa", r"disagreement", r"second reviewer"]),
        ("SR5", "clear inclusion and exclusion criteria", [r"inclusion criteria", r"exclusion criteria", r"eligibility criteria", r"included studies"]),
        ("SR6", "study quality or risk appraisal", [r"quality assessment", r"quality appraisal", r"risk of bias", r"critical appraisal"]),
        ("SR7", "study overlap and versions handled", [r"deduplicat", r"duplicate studies", r"study overlap", r"publication version", r"snowball"]),
        ("SR8", "extraction and synthesis method appropriate", [r"data extraction", r"thematic synthesis", r"meta.analysis", r"narrative synthesis", r"data synthesis", r"coding scheme"]),
        ("SR9", "evidence strength and heterogeneity addressed", [r"heterogeneity", r"evidence strength", r"certainty of evidence", r"quality of evidence", r"sensitivity analysis"]),
        ("SR10", "artifacts, limitations, and update date reported", [r"replication package", r"supplementary material", r"limitations?", r"updated? (?:to|on|through)", r"search date", r"artifact"]),
    ],
    "conceptual_framework": [
        ("CF1", "problem and boundary conditions clear", [r"problem statement", r"scope", r"boundary conditions?", r"we address", r"challenge"]),
        ("CF2", "grounded in relevant prior theory or evidence", [r"prior work", r"related work", r"literature", r"theor", r"empirical evidence"]),
        ("CF3", "constructs distinct and operationally definable", [r"we define", r"defined as", r"construct", r"dimension", r"component", r"taxonomy"]),
        ("CF4", "causal or mechanistic reasoning explicit", [r"mechanism", r"causal", r"leads to", r"results in", r"feedback loop", r"process model"]),
        ("CF5", "compared with close alternatives", [r"compared (?:with|to)", r"alternative", r"existing framework", r"baseline", r"related approaches"]),
        ("CF6", "evaluation or falsifiable propositions provided", [r"research proposition", r"hypothes", r"evaluat", r"case study", r"experiment", r"validation"]),
        ("CF7", "implementation cost and failure modes addressed", [r"implementation cost", r"trade.off", r"failure mode", r"risk", r"overhead", r"limitation"]),
        ("CF8", "evidence separated from assumption", [r"we assume", r"assumption", r"conceptual", r"hypothesized", r"future validation", r"empirical"]),
        ("CF9", "limitations and generalizability discussed", [r"limitations?", r"generaliz", r"boundary", r"future work", r"threats? to validity"]),
        ("CF10", "conflicts/commercial relationships and artifacts disclosed", [r"conflict(?:s)? of interest", r"competing interest", r"funding", r"trademark", r"artifact", r"github\.com", r"source code"]),
    ],
    "grey_aacods": [
        ("AA1", "Authority", [r"authors?", r"affiliation", r"organization", r"institution", r"biograph"]),
        ("AA2", "Accuracy", [r"method", r"sample", r"data", r"analysis", r"reference"]),
        ("AA3", "Coverage", [r"scope", r"population", r"dataset", r"participants?", r"case stud"]),
        ("AA4", "Objectivity", [r"limitations?", r"conflict", r"funding", r"sponsor", r"trade.off"]),
        ("AA5", "Date", [r"20(?:1[0-9]|2[0-9])", r"version", r"updated", r"published"]),
        ("AA6", "Significance", [r"implication", r"contribution", r"impact", r"recommend", r"finding"]),
    ],
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def body_pages(raw_pages: list[dict]) -> list[dict]:
    pages = []
    for p in raw_pages:
        text = p.get("text", "")
        if re.match(r"^\s*(?:references|bibliography)\b", text[:160], re.I):
            break
        pages.append({"page": int(p["page"]), "text": text})
    return pages or [{"page": int(p["page"]), "text": p.get("text", "")} for p in raw_pages]


def count_hits(pages: list[dict], patterns: list[str]) -> list[tuple[int, str, int]]:
    hits = []
    for p in pages:
        low = p["text"].lower()
        for pattern in patterns:
            n = len(re.findall(pattern, low, re.I))
            if n:
                hits.append((p["page"], pattern, n))
    return hits


def classify(title: str, pages: list[dict], stratum: str) -> tuple[str, str, str]:
    if stratum in {"grey", "practitioner", "grey_practitioner"}:
        return "grey_aacods", "practitioner_or_grey_report", "conceptual"
    lead = (title + "\n" + "\n".join(p["text"] for p in pages[:5])).lower()
    # Do not mistake an ordinary "Literature review"/"Related work" section for
    # a secondary-study design. Require the title or an explicit review-method
    # declaration in the paper's opening pages.
    secondary = (
        re.search(r"systematic (?:literature )?(?:review|mapping)|mapping study|scoping review|\b(?:a |an )?(?:comprehensive )?(?:survey|review) of\b", title.lower())
        or re.search(r"we (?:conduct|conducted|perform|performed|undertook) (?:a |an )?(?:systematic|scoping|mapping) (?:literature )?(?:review|study)|this systematic (?:literature )?review", lead)
    )
    qualitative = re.search(r"semi.structured interviews?|focus groups?|thematic analysis|grounded theory|qualitative study|interview study", lead)
    empirical = re.search(r"controlled experiment|randomi[sz]ed|participants?|dataset|repositories|case stud(?:y|ies)|survey(?:ed)?|empirical stud|we evaluat|we conduct", lead)
    conceptual = re.search(r"conceptual|position paper|vision paper|perspective|roadmap|manifesto|white paper|reference architecture|framework|taxonomy|challenges", lead)
    if secondary:
        return "secondary_review", "systematic_or_structured_secondary_review", "conceptual"
    if re.search(r"\b(?:vision|position|conceptual|perspective|manifesto|white) paper\b", lead[:5000]):
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    if qualitative:
        return "qualitative", "qualitative_interview_or_observational_study", "self-reported"
    if re.search(r"\b(?:comparison|comparative|experiment|evaluation|case study|empirical)\b", title.lower()):
        return "quantitative_mixed", "empirical_quantitative_or_mixed_study", "observed"
    if conceptual and not empirical:
        return "conceptual_framework", "conceptual_or_framework_paper", "conceptual"
    if re.search(r"survey(?:ed)?|questionnaire|self.report", lead) and not re.search(r"experiment|repository|mining|telemetry|log data", lead):
        return "quantitative_mixed", "survey_or_mixed_method_study", "self-reported"
    if re.search(r"simulation|synthetic|benchmark|modeled|modelled", lead) and not re.search(r"participants?|interview|survey", lead):
        return "quantitative_mixed", "modeled_or_benchmark_evaluation", "modeled"
    return "quantitative_mixed", "empirical_quantitative_or_mixed_study", "observed"


def score_criterion(pages: list[dict], cid: str, label: str, patterns: list[str]) -> dict:
    hits = count_hits(pages, patterns)
    if not hits:
        first = pages[0]["page"] if pages else 1
        last = pages[-1]["page"] if pages else first
        return {
            "criterion_id": cid,
            "criterion": label,
            "score": 0,
            "source_locator": f"page {first}",
            "justification": f"No clear evidence for this criterion was identified in the complete page-{first}-to-{last} extracted text; page {first} anchors the inspected report.",
        }
    by_page = Counter(page for page, _, n in hits for _ in range(n))
    page = by_page.most_common(1)[0][0]
    distinct = len({pat for _, pat, _ in hits})
    total = sum(n for _, _, n in hits)
    score = 2 if distinct >= 2 and total >= 3 else 1
    strength = "clear, repeated indicators" if score == 2 else "partial or single-indicator evidence"
    return {
        "criterion_id": cid,
        "criterion": label,
        "score": score,
        "source_locator": f"page {page}",
        "justification": f"{strength} for {label} on page {page} ({distinct} distinct indicator type(s), {total} occurrence(s) in the inspected body text).",
    }


def appraise(meta: dict, ordinal: int) -> dict:
    text_path = ROOT / meta["extracted_text_path"]
    if sha256(text_path) != meta["extracted_text_sha256"]:
        raise ValueError(f"source checksum mismatch: {meta['family_id']}")
    extracted = json.loads(text_path.read_text(encoding="utf-8"))
    pages = body_pages(extracted["pages"])
    form, design_type, nature = classify(meta.get("title", ""), pages, meta.get("evidence_stratum_candidate", ""))
    criteria = [score_criterion(pages, *criterion) for criterion in FORMS[form]]
    points = sum(c["score"] for c in criteria)
    applicable = 2 * len(criteria)
    percent = round(100 * points / applicable, 1)

    # A critical flaw is reserved for the three predefined fatal conditions.
    # Lack of open materials alone is not treated as fatal.
    scores = {c["criterion_id"]: c["score"] for c in criteria}
    flaw = None
    if form == "quantitative_mixed" and scores["QM2"] == 0 and scores["QM4"] == 0 and scores["QM6"] == 0:
        flaw = "no inspectable data provenance"
    elif form == "qualitative" and scores["QL2"] == 0 and scores["QL3"] == 0 and scores["QL4"] == 0:
        flaw = "no inspectable data provenance"
    elif form == "secondary_review" and scores["SR1"] == 0 and scores["SR3"] == 0 and scores["SR5"] == 0:
        flaw = "unverifiable primary claim"
    elif form == "conceptual_framework" and scores["CF2"] == 0 and scores["CF3"] == 0 and scores["CF6"] == 0:
        flaw = "unverifiable primary claim"
    critical = flaw is not None
    band = "low_contextual" if critical or percent < 50 else ("moderate" if percent < 75 else "high")
    return {
        "family_id": meta["family_id"],
        "record_id": meta["record_id"],
        "appraiser_agent_id": "d12-appraiser-a-v1",
        "review_context_id": f"d12-appraiser-a-{ordinal:04d}",
        "source_text_sha256": meta["extracted_text_sha256"],
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
        "overall_notes": "Protocol Section 13 quality weighting only; D11 eligibility is unchanged. Technical-quality evidence is not treated as validation of cognitive load.",
        "security_attestation": "Local checksum-bound extracted text only; no network, Git/history, environment/secrets, credentials, package installation, PDF execution, embedded action, script, link, or attachment was accessed.",
    }


def validate(rows: list[dict], expected_ids: list[str]) -> None:
    if len(rows) != 285 or [r["family_id"] for r in rows] != expected_ids:
        raise ValueError("partition population/order mismatch")
    if len({r["review_context_id"] for r in rows}) != 285:
        raise ValueError("review contexts are not unique")
    for row in rows:
        expected_n = 6 if row["appraisal_form"] == "grey_aacods" else 10
        if len(row["criteria"]) != expected_n:
            raise ValueError(f"criterion count: {row['family_id']}")
        if any(c["score"] not in {0, 1, 2} or not re.fullmatch(r"page \d+", c["source_locator"]) for c in row["criteria"]):
            raise ValueError(f"invalid score/locator: {row['family_id']}")
        points = sum(c["score"] for c in row["criteria"])
        if points != row["points_awarded"] or row["applicable_points"] != 2 * expected_n:
            raise ValueError(f"arithmetic: {row['family_id']}")
        pct = round(100 * points / row["applicable_points"], 1)
        if pct != row["percent"]:
            raise ValueError(f"percentage: {row['family_id']}")
        expected_band = "low_contextual" if row["critical_flaw"] or pct < 50 else ("moderate" if pct < 75 else "high")
        if row["evidence_band"] != expected_band:
            raise ValueError(f"band: {row['family_id']}")


def main() -> None:
    final = read_jsonl(LEDGER)
    ids = sorted(r["family_id"] for r in final if r.get("final_status") == "included_full_text")[:285]
    wanted = set(ids)
    meta = {}
    for packet in sorted(PACKET_DIR.glob("fulltext_packet_*.jsonl")):
        for row in read_jsonl(packet):
            if row["family_id"] in wanted:
                meta[row["family_id"]] = row
    if set(meta) != wanted:
        raise ValueError(f"missing packet metadata: {sorted(wanted - set(meta))}")
    rows = [appraise(meta[fid], i) for i, fid in enumerate(ids, 1)]
    validate(rows, ids)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    validate(read_jsonl(OUT), ids)
    print(json.dumps({
        "rows": len(rows),
        "forms": Counter(r["appraisal_form"] for r in rows),
        "bands": Counter(r["evidence_band"] for r in rows),
        "critical_flaws": Counter(r["critical_flaw_basis"] for r in rows if r["critical_flaw"]),
        "output_sha256": sha256(OUT),
    }, default=dict, sort_keys=True))


if __name__ == "__main__":
    main()
