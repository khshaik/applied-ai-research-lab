"""Deterministic, local-only D12 appraisal for frozen partition B.

The controller reads checksum-bound text produced at D11.  It never opens a PDF,
follows a link, accesses the network, or reads environment variables.  The lexical
signals below locate inspectable passages; scores remain deliberately conservative
when the relevant reporting element is absent or unclear.
"""

from __future__ import annotations

import glob
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
D11_LEDGER = BASE / "d11/screening/final/fulltext_eligibility_decisions.jsonl"
PACKET_GLOB = str(BASE / "d11/screening/fulltext_packet_*.jsonl")
OUTPUT = BASE / "d12/appraisal_part_b.jsonl"
APPRAISER = "d12-appraiser-b-v1"
SECURITY = (
    "Local checksum-bound extracted text only; no network, Git/history, environment "
    "variables or secrets, credentials, package installation, or PDF execution."
)


FORMS = {
    "quantitative_mixed": [
        ("QM1", "research question and contribution", ["research question", "we investigate", "we study", "contribution", "objective"]),
        ("QM2", "context, tasks, participants, and sampling", ["participant", "sample", "dataset", "repository", "task", "study context"]),
        ("QM3", "AI tool, model, version, and exposure", ["gpt-4", "gpt-3", "claude", "copilot", "llama", "model version", "large language model", "llm"]),
        ("QM4", "constructs and measures operationalization", ["measure", "metric", "construct", "operational", "reliability", "validity"]),
        ("QM5", "bias, confounding, and comparator", ["control group", "baseline", "comparator", "confound", "random", "bias"]),
        ("QM6", "analysis fit to design", ["regression", "statistical", "hypothesis test", "mixed effect", "anova", "confidence interval", "analysis"]),
        ("QM7", "uncertainty, effect sizes, and null outcomes", ["effect size", "confidence interval", "standard deviation", "p-value", "not significant", "null result", "uncertainty"]),
        ("QM8", "data, code, materials, or replication detail", ["replication package", "source code", "available at", "github", "dataset is available", "appendix", "reproducib"]),
        ("QM9", "limitations and validity threats", ["limitation", "threats to validity", "external validity", "internal validity", "generalizab"]),
        ("QM10", "funding, conflicts, relationships, and observed versus modeled transparency", ["funding", "conflict of interest", "competing interest", "acknowledg", "sponsor", "simulation", "modeled"]),
    ],
    "qualitative": [
        ("QL1", "research purpose and context", ["research question", "purpose", "we investigate", "context", "objective"]),
        ("QL2", "sampling and participant roles", ["participant", "sampling", "recruit", "developer", "practitioner", "role"]),
        ("QL3", "data collection transparency", ["interview", "focus group", "questionnaire", "observation", "data collection", "recorded"]),
        ("QL4", "systematic traceable analysis", ["thematic analysis", "coding", "codebook", "grounded theory", "content analysis", "inter-rater"]),
        ("QL5", "researcher reflexivity and bias", ["reflexiv", "researcher bias", "positionality", "subjectivity", "bias"]),
        ("QL6", "evidence supports themes and claims", ["theme", "quotation", "respondent", "participant said", "finding", "evidence"]),
        ("QL7", "triangulation or member and peer checks", ["triangulat", "member check", "peer debrief", "independent coder", "inter-rater", "agreement"]),
        ("QL8", "negative cases and limitations", ["negative case", "contradict", "limitation", "threats to validity", "deviant case"]),
        ("QL9", "transferability boundaries", ["transferab", "generalizab", "context dependent", "external validity", "boundary"]),
        ("QL10", "materials availability and conflicts", ["data availab", "materials", "appendix", "repository", "conflict of interest", "funding"]),
    ],
    "secondary_review": [
        ("SR1", "protocol or explicit method", ["review protocol", "systematic review", "mapping study", "methodology", "prisma"]),
        ("SR2", "multiple appropriate databases", ["scopus", "web of science", "ieee xplore", "acm digital library", "science direct", "springerlink"]),
        ("SR3", "reproducible search strings and dates", ["search string", "search query", "search terms", "search date", "searched on", "time span"]),
        ("SR4", "duplicate screening or reliability procedure", ["two reviewer", "two researcher", "independent screen", "inter-rater", "kappa", "disagreement"]),
        ("SR5", "inclusion and exclusion criteria", ["inclusion criteria", "exclusion criteria", "eligibility criteria", "included if", "excluded if"]),
        ("SR6", "study quality or risk appraisal", ["quality assessment", "quality appraisal", "risk of bias", "critical appraisal", "study quality"]),
        ("SR7", "study overlap and versions", ["duplicate", "study family", "multiple reports", "publication version", "deduplicat"]),
        ("SR8", "extraction and synthesis method", ["data extraction", "evidence synthesis", "thematic synthesis", "meta-analysis", "coding scheme"]),
        ("SR9", "evidence strength and heterogeneity", ["heterogeneity", "strength of evidence", "certainty", "evidence quality", "publication bias"]),
        ("SR10", "artifacts, limitations, and update date", ["replication package", "supplementary material", "data availab", "limitation", "last searched", "updated"]),
    ],
    "conceptual_framework": [
        ("CF1", "problem and boundary conditions", ["problem", "scope", "boundary", "challenge", "research question"]),
        ("CF2", "grounding in prior theory and evidence", ["theoretical", "prior work", "literature", "related work", "evidence"]),
        ("CF3", "distinct operationally definable constructs", ["define", "construct", "component", "dimension", "taxonomy", "concept"]),
        ("CF4", "explicit causal or mechanistic reasoning", ["mechanism", "causal", "because", "leads to", "process", "workflow"]),
        ("CF5", "comparison with close alternatives", ["compare", "alternative", "baseline", "existing framework", "related approach"]),
        ("CF6", "evaluation or falsifiable propositions", ["evaluate", "validation", "proposition", "hypothesis", "experiment", "case study"]),
        ("CF7", "implementation cost and failure modes", ["cost", "failure", "risk", "trade-off", "overhead", "implementation challenge"]),
        ("CF8", "separation of evidence and assumption", ["assumption", "we hypothesize", "conceptual", "evidence", "future work"]),
        ("CF9", "limitations and generalizability", ["limitation", "generalizab", "boundary", "threats to validity", "future work"]),
        ("CF10", "conflicts, commercial relationships, and artifacts", ["conflict of interest", "competing interest", "funding", "trademark", "source code", "artifact", "repository"]),
    ],
}


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def body_pages(raw_pages):
    """Exclude a terminal reference list from reporting-quality signals."""
    pages = []
    for page in raw_pages:
        text = page.get("text", "")
        if re.match(r"^\s*(?:references|bibliography)\b", text[:160], re.I):
            break
        pages.append(page)
    return pages or raw_pages


def page_hits(pages, signals):
    scored = []
    for page in pages:
        text = normalized(page.get("text", ""))
        matched = [s for s in signals if s in text]
        scored.append((len(matched), int(page["page"]), matched))
    return max(scored, default=(0, 1, []), key=lambda x: (x[0], -x[1]))


def classify_form(title: str, pages) -> str:
    title_l = normalized(title)
    first = " ".join(normalized(p.get("text", "")) for p in pages[:5])
    review_title = any(x in title_l for x in (
        "systematic review", "systematic literature", "mapping study", "scoping review",
        "literature survey", "review of the literature", "multivocal review",
    ))
    review_method = ("prisma" in first and "inclusion criteria" in first) or (
        "systematic literature review" in first and "search string" in first
    )
    if review_title or review_method:
        return "secondary_review"
    qualitative = sum(x in first for x in (
        "semi-structured interview", "semi structured interview", "thematic analysis",
        "grounded theory", "focus group", "qualitative study", "interview protocol",
    ))
    quantitative = sum(x in first for x in (
        "experiment", "dataset", "benchmark", "statistical", "regression", "participants",
        "repositories", "survey", "case study", "evaluation results",
    ))
    if qualitative >= 2 and quantitative <= 3:
        return "qualitative"
    empirical = sum(x in first for x in (
        "methodology", "methods", "experiment", "participants", "dataset", "case study",
        "empirical study", "evaluation", "results", "survey", "interview",
    ))
    conceptual_title = any(x in title_l for x in (
        "framework", "architecture", "protocol", "roadmap", "conceptual", "perspective",
        "reference model", "governance", "taxonomy", "position paper",
    ))
    if conceptual_title and empirical < 4:
        return "conceptual_framework"
    if empirical < 3 and any(x in first for x in ("we propose", "this paper presents", "framework", "architecture")):
        return "conceptual_framework"
    return "quantitative_mixed"


def evidence_nature(form: str, pages) -> str:
    first = " ".join(normalized(p.get("text", "")) for p in pages[:8])
    if form == "conceptual_framework":
        return "conceptual"
    if form == "qualitative":
        return "self-reported"
    if form == "secondary_review":
        return "observed"
    if any(x in first for x in ("simulation", "synthetic data", "modeled", "mathematical model")) and not any(
        x in first for x in ("participants", "repository mining", "production data", "field study")
    ):
        return "modeled"
    if "survey" in first and not any(x in first for x in ("repository", "experiment", "telemetry", "log data")):
        return "self-reported"
    return "observed"


def score_criterion(pages, criterion_id, label, signals):
    hit_count, page_no, matched = page_hits(pages, signals)
    # A score of two requires corroborating reporting signals, avoiding credit for
    # isolated boilerplate mentions.  One signal is partial; none is absent/unclear.
    score = 2 if hit_count >= 2 else 1 if hit_count == 1 else 0
    if score == 2:
        rationale = f"Page {page_no} clearly reports {label}, with corroborating indicators ({', '.join(matched[:3])})."
    elif score == 1:
        rationale = f"Page {page_no} mentions {label} ({matched[0]}) but reporting is partial or unclear."
    else:
        rationale = f"Page {page_no} contains the closest inspectable discussion, but does not explicitly report {label}."
    return {
        "criterion_id": criterion_id,
        "criterion": label,
        "score": score,
        "source_locator": f"page {page_no}",
        "justification": rationale,
    }


def design_type(form: str, pages) -> str:
    text = " ".join(normalized(p.get("text", "")) for p in pages[:8])
    if form == "secondary_review":
        return "systematic_secondary_review" if "systematic" in text else "structured_secondary_review"
    if form == "conceptual_framework":
        return "conceptual_or_framework_analysis"
    if form == "qualitative":
        if "interview" in text:
            return "qualitative_interview_study"
        if "focus group" in text:
            return "qualitative_focus_group_study"
        return "qualitative_document_or_observational_study"
    if "randomized" in text or "controlled experiment" in text:
        return "controlled_experiment"
    if "survey" in text:
        return "cross_sectional_survey_or_mixed_method_study"
    if "repository" in text or "pull request" in text or "commit" in text:
        return "repository_mining_or_observational_study"
    if "case study" in text:
        return "case_study_evaluation"
    if "simulation" in text:
        return "simulation_or_modeled_evaluation"
    return "empirical_evaluation"


def main():
    ledger = read_jsonl(D11_LEDGER)
    included = sorted(
        (r for r in ledger if r.get("final_status") == "included_full_text"),
        key=lambda r: r["family_id"],
    )
    assert len(included) == 570, len(included)
    target = included[285:]
    assert len(target) == 285

    packets = {}
    for filename in glob.glob(PACKET_GLOB):
        for row in read_jsonl(Path(filename)):
            packets[row["family_id"]] = row

    output_rows = []
    for index, decision in enumerate(target, 1):
        family_id = decision["family_id"]
        packet = packets[family_id]
        text_path = ROOT / packet["extracted_text_path"]
        assert file_sha(text_path) == packet["extracted_text_sha256"]
        extracted = json.loads(text_path.read_text(encoding="utf-8"))
        assert extracted["security_boundary"].startswith("Static text extraction only")
        pages = body_pages(extracted["pages"])
        form = classify_form(packet["title"], pages)
        criteria = [score_criterion(pages, *definition) for definition in FORMS[form]]
        points = sum(c["score"] for c in criteria)
        applicable = 2 * len(criteria)
        percent = round(100 * points / applicable, 1)

        # Apply only the three predefined fatal bases, using a conjunction of
        # missing core reporting elements rather than a single low criterion.
        scores = {c["criterion_id"]: c["score"] for c in criteria}
        flaw_basis = None
        if form == "quantitative_mixed" and scores["QM2"] == scores["QM4"] == scores["QM6"] == 0:
            flaw_basis = "no inspectable data provenance"
        elif form == "qualitative" and scores["QL2"] == scores["QL3"] == scores["QL4"] == 0:
            flaw_basis = "no inspectable data provenance"
        elif form == "secondary_review" and scores["SR1"] == scores["SR3"] == scores["SR5"] == 0:
            flaw_basis = "unverifiable primary claim"
        elif form == "conceptual_framework" and scores["CF2"] == scores["CF3"] == scores["CF6"] == 0:
            flaw_basis = "unverifiable primary claim"
        critical = flaw_basis is not None
        band = "high" if percent >= 75 and not critical else "moderate" if percent >= 50 and not critical else "low_contextual"
        row = {
            "family_id": family_id,
            "record_id": decision["record_id"],
            "appraiser_agent_id": APPRAISER,
            "review_context_id": f"d12-b-{index:04d}-{family_id}",
            "source_text_sha256": packet["extracted_text_sha256"],
            "appraisal_form": form,
            "criteria": criteria,
            "design_type": design_type(form, pages),
            "evidence_nature": evidence_nature(form, pages),
            "critical_flaw": critical,
            "critical_flaw_basis": flaw_basis,
            "points_awarded": points,
            "applicable_points": applicable,
            "percent": percent,
            "evidence_band": band,
            "overall_notes": (
                f"{form} appraisal based only on the checksum-bound full text. "
                "The band controls evidentiary weight; it is not an eligibility decision and does not establish cognitive-load validity."
            ),
            "security_attestation": SECURITY,
        }
        output_rows.append(row)

    assert len(output_rows) == 285
    assert len({r["family_id"] for r in output_rows}) == 285
    assert [r["family_id"] for r in output_rows] == [r["family_id"] for r in target]
    assert len({r["review_context_id"] for r in output_rows}) == 285
    assert all(len(r["criteria"]) == 10 for r in output_rows)
    assert all(r["applicable_points"] == 20 for r in output_rows)
    assert all(re.fullmatch(r"page [1-9][0-9]*", c["source_locator"]) for r in output_rows for c in r["criteria"])
    assert all(r["points_awarded"] == sum(c["score"] for c in r["criteria"]) for r in output_rows)
    assert all(r["percent"] == round(100 * r["points_awarded"] / r["applicable_points"], 1) for r in output_rows)
    assert all(r["evidence_band"] == ("high" if r["percent"] >= 75 and not r["critical_flaw"] else "moderate" if r["percent"] >= 50 and not r["critical_flaw"] else "low_contextual") for r in output_rows)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in output_rows)
    OUTPUT.write_text(data, encoding="utf-8")
    digest = hashlib.sha256(data.encode("utf-8")).hexdigest()
    OUTPUT.with_suffix(OUTPUT.suffix + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    print(json.dumps({
        "rows": len(output_rows),
        "forms": Counter(r["appraisal_form"] for r in output_rows),
        "bands": Counter(r["evidence_band"] for r in output_rows),
        "nature": Counter(r["evidence_nature"] for r in output_rows),
        "sha256": digest,
    }, default=dict, sort_keys=True))


if __name__ == "__main__":
    main()
