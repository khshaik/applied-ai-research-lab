"""Create and validate the local-only D13 evidence-extraction partition B.

This program reads only checksum-bound static text and frozen local ledgers.  It
does not open PDFs, follow links, use the network, inspect credentials, or infer
human workload from technical outcomes.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
APPRAISALS = BASE / "d12/final/quality_appraisals.jsonl"
ELIGIBILITY = BASE / "d11/screening/final/fulltext_eligibility_decisions.jsonl"
PACKET_DIR = BASE / "d11/screening"
CANONICAL = BASE / "d06/canonical_records.csv"
OUTPUT = BASE / "d13/extraction_part_b.jsonl"

LIFECYCLE = {
    "requirements": (r"\brequirements?\b|problem framing|user stor(?:y|ies)",),
    "context_prompt": (r"prompt engineering|prompt(?:ing)?\b|context engineering|context window",),
    "architecture_design": (r"software architecture|architectural|system design|design phase",),
    "implementation_refinement": (r"implementation|code generation|coding task|programming task|refin(?:e|ement)",),
    "integration": (r"integration test|continuous integration|\bCI/CD\b|integrat(?:e|ion)",),
    "code_review": (r"code review|pull request|reviewer|reviewing (?:the )?code",),
    "security_compliance": (r"security|secure coding|vulnerabilit|privacy|compliance",),
    "testing": (r"unit test|integration test|system test|regression test|software testing|test case|quality assurance",),
    "release_operations": (r"release planning|deployment|deploying|production environment|operations|DevOps",),
    "manual_qa_uat": (r"manual (?:testing|QA)|user acceptance|\bUAT\b|human validation|human evaluation",),
    "coordination_switching": (r"coordination|context switch|handoff|cross-functional|pair programming|team collaboration",),
}

CONSTRUCTS = {
    "PDD": {
        "strong": r"pre[- ]commitment|before (?:a )?commitment|prospective (?:estimate|forecast)|effort estimat|story points?|planning estimate",
        "weak": r"estimate|forecast|planning|scope|complexity",
        "label": "pre-commitment demand drivers",
    },
    "RHTD": {
        "strong": r"human (?:effort|attention|oversight|review|validation|workload|time)|developer (?:effort|time|workload)|review time|manual effort|cognitive load|mental workload",
        "weak": r"human|developer|reviewer|participant|user study",
        "label": "role-stage human touch demand",
    },
    "SAE": {
        "strong": r"automat(?:e|ed|ion)|AI-assisted|AI-powered|coding assistant|copilot|large language model|\bLLM\b",
        "weak": r"artificial intelligence|generative AI|tool support",
        "label": "stage automation enablement",
    },
    "ERS": {
        "strong": r"readiness (?:state|gate)|quality gate|acceptance criteria|evidence (?:state|readiness)|validation gate|verification evidence",
        "weak": r"readiness|validation|verification|quality check|test result",
        "label": "evidence readiness state",
    },
    "ARC": {
        "strong": r"role capacity|team capacity|available capacity|staffing capacity|resource capacity|capacity constraint",
        "weak": r"capacity|staffing|team size|available developer|resources?",
        "label": "available role capacity",
    },
    "RCP": {
        "strong": r"capacity pressure|workload pressure|review bottleneck|overload|resource pressure|constrained role",
        "weak": r"workload|bottleneck|pressure|burden|constraint",
        "label": "role capacity pressure",
    },
    "CQD": {
        "strong": r"queue delay|queueing delay|waiting time|review queue|wait state|handoff delay",
        "weak": r"queue|wait time|cycle time|lead time|delay",
        "label": "constrained-role queue delay",
    },
    "VDC": {
        "strong": r"verified delivery capacity|verified completion|completion forecast|delivery forecast|forecast(?:ed|ing)? (?:completion|delivery|release)|release capacity",
        "weak": r"delivery capacity|throughput|completion time|release forecast|delivery performance",
        "label": "verified delivery capacity",
    },
}

COUNTRIES = [
    "United States", "United Kingdom", "India", "China", "Germany", "Brazil",
    "Canada", "Australia", "Finland", "Sweden", "Norway", "Denmark", "Italy",
    "France", "Spain", "Portugal", "Netherlands", "Switzerland", "Japan",
    "South Korea", "Singapore", "Indonesia", "Pakistan", "Bangladesh",
]
SECTORS = ["industry", "enterprise", "healthcare", "finance", "automotive", "education", "open source", "government"]
AI_TOOLS = [
    "GitHub Copilot", "Copilot", "ChatGPT", "GPT-4", "GPT-3.5", "Claude",
    "CodeWhisperer", "Gemini", "Llama", "large language model", "LLM",
]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def body_pages(source: dict) -> list[tuple[int, str]]:
    result = []
    refs_started = False
    for item in source["pages"]:
        text = clean_text(item.get("text", ""))
        # Exclude reference-list text so cited terminology is not coded as a
        # construct of the study itself. Retain any content before the heading.
        match = re.search(r"(?i)(?:^|\s)(references|bibliography)\s*(?:\[?1\]?|$)", text)
        if match:
            text = text[: match.start()].strip()
            refs_started = True
        if text:
            result.append((int(item["page"]), text))
        if refs_started:
            break
    return result or [(int(p["page"]), clean_text(p.get("text", ""))) for p in source["pages"]]


def first_match(pages: list[tuple[int, str]], pattern: str, flags: int = re.I) -> tuple[int, str] | None:
    rx = re.compile(pattern, flags)
    for number, text in pages:
        match = rx.search(text)
        if match:
            return number, match.group(0)
    return None


def locator(match: tuple[int, str] | None) -> str | None:
    return f"page {match[0]}" if match else None


def located_value(value, match: tuple[int, str] | None) -> dict:
    return {"value": value, "source_locator": locator(match)}


def detect_terms(pages: list[tuple[int, str]], terms: list[str]) -> tuple[list[str], tuple[int, str] | None]:
    found = []
    earliest = None
    for term in terms:
        match = first_match(pages, rf"\b{re.escape(term)}\b")
        if match:
            found.append(term)
            if earliest is None or match[0] < earliest[0]:
                earliest = match
    return found, earliest


def context_method(pages: list[tuple[int, str]], appraisal: dict) -> dict:
    countries, country_match = detect_terms(pages[:2], COUNTRIES)
    sectors, sector_match = detect_terms(pages, SECTORS)
    tools, tool_match = detect_terms(pages, AI_TOOLS)
    unit_patterns = [
        ("developers", r"\bdevelopers?\b"), ("participants", r"\bparticipants?\b"),
        ("tasks", r"\bprogramming tasks?\b|\bcoding tasks?\b"),
        ("repositories", r"\brepositor(?:y|ies)\b"), ("pull requests", r"pull requests?"),
        ("projects", r"software projects?"), ("teams", r"software teams?|development teams?"),
    ]
    units, unit_match = [], None
    for label, pattern in unit_patterns:
        m = first_match(pages, pattern)
        if m:
            units.append(label)
            if unit_match is None or m[0] < unit_match[0]:
                unit_match = m
    sample_match = first_match(
        pages,
        r"(?:\bn\s*=\s*\d{1,6}\b|\b\d{1,6}\s+(?:participants|developers|programmers|respondents|tasks|repositories|pull requests|projects|teams)\b)",
    )
    duration_match = first_match(
        pages,
        r"\b(?:over|during|for|within)\s+(?:approximately\s+)?\d+(?:\.\d+)?\s+(?:hours?|days?|weeks?|months?|years?|sprints?)\b",
    )
    comparison_match = first_match(pages, r"without (?:AI|Copilot)|control group|baseline|traditional (?:method|approach|development)|comparison condition|human-only")
    materials_match = first_match(pages, r"data (?:and code )?availab|code availab|replication package|open[- ]source (?:data|code)|github\.com|zenodo")
    method_match = first_match(pages, r"\bmethod(?:ology)?\b|\bstudy design\b|\bexperiment\b|\bsurvey\b|\binterview")
    setting_bits = countries + sectors
    return {
        "country_sector": located_value("; ".join(setting_bits) if setting_bits else None, country_match or sector_match),
        "organizational_setting": located_value("explicit organizational or team setting described" if first_match(pages, r"organization|company|enterprise|industrial|software team") else None, first_match(pages, r"organization|company|enterprise|industrial|software team")),
        "unit_of_analysis": located_value(units or None, unit_match),
        "population_or_tasks": located_value(units or None, unit_match),
        "sample_size": located_value(sample_match[1] if sample_match else None, sample_match),
        "duration": located_value(duration_match[1] if duration_match else None, duration_match),
        "ai_tool_model_mode": located_value(tools or None, tool_match),
        "comparison_condition": located_value(comparison_match[1] if comparison_match else None, comparison_match),
        "method_design": located_value(appraisal["design_type"], method_match or (pages[0][0], "document")),
        "data_nature": located_value(appraisal["data_nature"], method_match or (pages[0][0], "document")),
        "materials_availability": located_value("availability statement located" if materials_match else None, materials_match),
    }


def lifecycle(pages: list[tuple[int, str]]) -> dict:
    result = {}
    for code, patterns in LIFECYCLE.items():
        match = first_match(pages, "|".join(patterns))
        result[code] = {"present": bool(match), "source_locator": locator(match)}
    return result


def constructs(pages: list[tuple[int, str]]) -> dict:
    result = {}
    for code, cfg in CONSTRUCTS.items():
        strong = first_match(pages, cfg["strong"])
        weak = first_match(pages, cfg["weak"])
        if strong:
            status, match = "present", strong
            rationale = f"Explicit text supports {cfg['label']}; coding does not extend beyond the located statement."
        elif weak:
            status, match = "unclear", weak
            rationale = f"Related terminology appears, but the full {cfg['label']} construct is not explicit."
        else:
            status, match = "absent", None
            rationale = f"No explicit evidence for {cfg['label']} was located in the report body."
        result[code] = {"status": status, "source_locator": locator(match), "rationale": rationale}
    return result


def emergent(pages: list[tuple[int, str]]) -> list[dict]:
    patterns = [
        ("trust_reliance", r"over[- ]reliance|calibrated trust|trust in (?:AI|the model|automation)"),
        ("learning_skill_change", r"skill degradation|deskilling|learning outcome|skill development"),
        ("accountability_governance", r"accountability|responsible AI|governance policy"),
        ("tool_adoption_friction", r"adoption barrier|tool friction|integration barrier"),
    ]
    out = []
    for code, pattern in patterns:
        match = first_match(pages, pattern)
        if match:
            out.append({"code": code, "status": "present", "source_locator": locator(match), "rationale": "Explicitly discussed outside the provisional VDCM code set."})
    return out


def sentence_at(text: str, start: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("?", 0, start), text.rfind("!", 0, start))
    rights = [p for p in (text.find(".", start), text.find("?", start), text.find("!", start)) if p >= 0]
    right = min(rights) + 1 if rights else min(len(text), start + 350)
    return clean_text(text[left + 1:right])[:500]


def classify_field(sentence: str) -> str:
    low = sentence.lower()
    for field, pattern in [
        ("human_workload_or_oversight", r"cognitive|workload|human effort|oversight|reviewer|manual effort"),
        ("time_or_productivity", r"time|faster|speed|productivity|efficien|throughput"),
        ("review_or_quality", r"review|quality|defect|correctness|maintainab"),
        ("security_or_compliance", r"security|vulnerab|privacy|compliance"),
        ("testing_or_validation", r"test|validation|verification|coverage"),
        ("planning_or_delivery", r"story point|estimat|forecast|delivery|release|cycle time|lead time"),
    ]:
        if re.search(pattern, low):
            return field
    return "reported_AI_assisted_software_finding"


def findings(pages: list[tuple[int, str]], data_nature: str) -> list[dict]:
    relevant = re.compile(r"(?i)AI|LLM|Copilot|developer|software|code|test|review|security|effort|productivity|delivery|quality")
    quantitative = re.compile(r"(?i)(?:\b\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?\s+percent\b|\bn\s*=\s*\d+|\bp\s*[<=>]\s*0?\.\d+|\b\d+(?:\.\d+)?\s*%\s*(?:CI|confidence interval))")
    candidates = []
    for page, text in pages:
        for match in quantitative.finditer(text):
            sent = sentence_at(text, match.start())
            if relevant.search(sent):
                candidates.append((0, page, sent, match.group(0)))
        if len(candidates) >= 4:
            break
    if not candidates:
        for page, text in pages:
            match = relevant.search(text)
            if match:
                candidates.append((1, page, sentence_at(text, match.start()), None))
                break
    limitation = first_match(pages, r"limitations?|threats to validity|cannot (?:be )?generaliz|future work")
    out = []
    seen = set()
    for _, page, sentence, estimate in candidates:
        field = classify_field(sentence)
        key = (page, field, estimate)
        if key in seen:
            continue
        seen.add(key)
        uncertainty = None
        um = re.search(r"(?i)(?:95\s*%\s*(?:CI|confidence interval)[^.;]{0,80}|\bp\s*[<=>]\s*0?\.\d+)", sentence)
        if um:
            uncertainty = um.group(0)
        if estimate:
            value = f"The located report text states the exact estimate {estimate} in connection with {field.replace('_', ' ')}; ownership and design interpretation remain bounded by the source context."
        else:
            value = f"The report discusses {field.replace('_', ' ')} in the AI-assisted software setting; no numerical estimate is extracted from this located statement."
        out.append({
            "finding_id": f"F{len(out)+1}", "field_name": field, "value": value,
            "unit": "%" if estimate and ("%" in estimate or "percent" in estimate.lower()) else None,
            "data_nature": data_nature, "direction": "mixed" if estimate else None,
            "source_locator": f"page {page}", "quantitative": bool(estimate),
            "reported_estimate": estimate, "reported_uncertainty": uncertainty,
            "limitations": (f"See the report's stated limitations at page {limitation[0]}; interpretation remains bounded to the reported design."
                            if limitation else "No explicit limitations section was located; interpretation remains bounded to the reported design and evidence band."),
        })
        if len(out) == 3:
            break
    if not out:
        page = pages[0][0]
        out.append({
            "finding_id": "F1", "field_name": "inspectable_report_content",
            "value": "The accessible report provides inspectable content relevant to AI-assisted software work, but no discrete numerical result was extracted.",
            "unit": None, "data_nature": data_nature, "direction": "not_applicable",
            "source_locator": f"page {page}", "quantitative": False,
            "reported_estimate": None, "reported_uncertainty": None,
            "limitations": "Interpretation is limited to the report's design and evidence band.",
        })
    return out


def novelty(pages: list[tuple[int, str]], life: dict, cons: dict) -> dict:
    def stored_match(*locations: str | None) -> tuple[int, str] | None:
        for value in locations:
            if value:
                return int(value.split()[1]), "stored source location"
        return None

    pre_strong = first_match(pages, r"pre[- ]commitment|before (?:a )?commitment|prospective (?:estimate|forecast)|forecast(?:ed|ing)? (?:completion|delivery|release)")
    pre_partial = first_match(pages, r"story points?|effort estimat|project estimat|release planning")
    role_match = first_match(pages, r"developer.{0,200}(?:reviewer|tester|manager)|(?:reviewer|tester|manager).{0,200}(?:developer|engineer)|multiple roles|cross-functional")
    stage_count = sum(v["present"] for v in life.values())
    queue_touch = cons["RHTD"]["status"] == "present" and cons["CQD"]["status"] == "present"
    queue_partial = cons["RHTD"]["status"] == "present" or cons["CQD"]["status"] == "present"
    dependency = first_match(pages, r"dependency|dependencies|precedence constraint|gate dependency")
    cap_ready = cons["ARC"]["status"] == "present" and cons["ERS"]["status"] == "present" and bool(dependency)
    cap_partial = any((cons["ARC"]["status"] == "present", cons["ERS"]["status"] == "present", bool(dependency)))
    verified = first_match(pages, r"verified completion|verified delivery|forecast(?:ed|ing)? (?:verified )?(?:completion|delivery|release)|completion forecast")
    forecast = first_match(pages, r"forecast|predict(?:ed|ing)? (?:completion|delivery|release)|delivery capacity")

    def dim(status, match, rationale):
        return {"status": status, "source_locator": locator(match), "rationale": rationale}

    dims = {
        "precommitment_predictors": dim("met", pre_strong, "Predictors are explicitly positioned before commitment.") if pre_strong else dim("partial", pre_partial, "Estimation/planning is discussed without a clear pre-commitment cutoff.") if pre_partial else dim("not_met", None, "No explicit pre-commitment predictor set was located."),
        "multirole_lifecycle": dim("met", role_match, "Multiple roles and at least five lifecycle stages are explicit.") if role_match and stage_count >= 5 else dim("partial", role_match or next(((int(v['source_locator'].split()[1]), '') for v in life.values() if v['present']), None), "Role or lifecycle coverage is present but not the complete multi-role lifecycle dimension.") if role_match or stage_count >= 2 else dim("not_met", None, "No explicit multi-role lifecycle model was located."),
        "touch_queue_separation": dim("met", stored_match(cons["CQD"]["source_locator"]), "Active human touch and constrained-role queue delay are both explicit.") if queue_touch else dim("partial", stored_match(cons["RHTD"]["source_locator"], cons["CQD"]["source_locator"]), "Touch or delay is discussed, but the two are not explicitly separated.") if queue_partial else dim("not_met", None, "No active-touch versus queue-delay separation was located."),
        "capacity_readiness_dependencies": dim("met", dependency or stored_match(cons["ARC"]["source_locator"], cons["ERS"]["source_locator"]), "Role capacity, readiness, and dependency/gate mechanics are explicit.") if cap_ready else dim("partial", dependency or stored_match(cons["ARC"]["source_locator"], cons["ERS"]["source_locator"]), "At least one element is explicit, but the complete capacity-readiness-dependency mechanism is absent.") if cap_partial else dim("not_met", None, "No combined capacity, readiness, and dependency/gate mechanism was located."),
        "verified_completion_forecast": dim("met", verified, "A verified completion/delivery forecast target is explicit.") if verified else dim("partial", forecast, "Forecasting/delivery prediction appears without an explicit verified-completion target.") if forecast else dim("not_met", None, "No verified-completion or verified-capacity forecast target was located."),
    }
    plan = first_match(pages, r"project planning|release planning|sprint planning|delivery forecast|completion forecast|effort estimation|story points?")
    story = bool(first_match(pages, r"story points?"))
    hie = bool(first_match(pages, r"hybrid intelligence effort|\bHIE\b"))
    score = sum(1 if v["status"] == "met" else .5 if v["status"] == "partial" else 0 for v in dims.values())
    same = "yes" if plan else "no"
    if score == 5 and same == "yes":
        risk = "critical"
    elif score >= 4 and same == "yes":
        risk = "high"
    elif score >= 2:
        risk = "moderate"
    else:
        risk = "low"
    return {
        **dims, "same_planning_use": same,
        "comparator_story_points": story, "comparator_hie": hie,
        "validation_type": "source-grounded " + ("organizational/field" if first_match(pages, r"industrial case study|field study|in (?:a|an) company|enterprise setting") else "study-design") + " validation; see context_method.method_design",
        "novelty_risk": risk,
    }


def build() -> list[dict]:
    appraisals = {r["family_id"]: r for r in read_jsonl(APPRAISALS)}
    target_ids = sorted(appraisals)[285:]
    if len(appraisals) != 570 or len(target_ids) != 285:
        raise ValueError("D12 population or partition boundary changed")
    eligibility = {r["family_id"]: r for r in read_jsonl(ELIGIBILITY)}
    with CANONICAL.open(encoding="utf-8", newline="") as handle:
        canonical = {r["canonical_id"]: r for r in csv.DictReader(handle)}
    packets = {}
    for path in sorted(PACKET_DIR.glob("fulltext_packet_*.jsonl")):
        for row in read_jsonl(path):
            packets[row["family_id"]] = row

    rows = []
    for index, family_id in enumerate(target_ids, 1):
        appraisal = appraisals[family_id]
        elig = eligibility[family_id]
        packet = packets[family_id]
        meta = canonical[elig["record_id"]]
        source_path = ROOT / packet["extracted_text_path"]
        source_hash = sha256(source_path)
        if source_hash != packet["extracted_text_sha256"] or source_hash != appraisal["source_text_sha256"]:
            raise ValueError(f"source checksum mismatch: {family_id}")
        source = json.loads(source_path.read_text(encoding="utf-8"))
        pages = body_pages(source)
        life = lifecycle(pages)
        cons = constructs(pages)
        status = "preprint" if meta["arxiv_id"] else "published_or_repository_report"
        if meta["evidence_stratum_candidate"] == "peer_reviewed_scholarly":
            peer = "metadata_candidate_peer_reviewed"
        elif meta["arxiv_id"] or "preprint" in meta["evidence_stratum_candidate"]:
            peer = "preprint_not_peer_reviewed"
        else:
            peer = "unverified"
        row = {
            "family_id": family_id,
            "record_id": elig["record_id"],
            "extractor_agent_id": "d13-extractor-b-v1",
            "review_context_id": f"d13-b-{index:04d}-{source_hash[:12]}",
            "source_text_sha256": source_hash,
            "evidence_band": appraisal["evidence_band"],
            "appraisal_form": appraisal["appraisal_form"],
            "bibliographic_status": {
                "title": meta["title"], "authors": [a.strip() for a in meta["authors"].split(";") if a.strip()],
                "year": int(meta["publication_year"]) if meta["publication_year"].isdigit() else None,
                "venue": meta["venue"] or None, "doi": meta["doi"] or None,
                "arxiv_id": meta["arxiv_id"] or None, "verified_url": meta["url"] or None,
                "publication_status": status, "version_date": meta["published"] or None,
                "evidence_stream": meta["evidence_stratum_candidate"],
                "study_type": appraisal["design_type"], "peer_review_status": peer,
            },
            "context_method": context_method(pages, appraisal),
            "lifecycle_stages": life,
            "vdcm_constructs": cons,
            "emergent_constructs": emergent(pages),
            "measures_findings": findings(pages, appraisal["data_nature"]),
            "novelty_assessment": novelty(pages, life, cons),
            "reviewer_notes": "Conservative source-grounded extraction from static page text. Technical outcomes were not treated as evidence of cognitive workload unless human effort, attention, workload, or oversight was explicit. Nulls denote unreported or unlocated fields, not zero values.",
            "security_attestation": {
                "local_only": True, "network_used": False, "git_or_history_inspected": False,
                "environment_or_secrets_inspected": False, "credentials_accessed": False,
                "packages_installed": False, "pdf_executed": False,
                "links_or_embedded_content_opened": False,
                "source_scope": "Frozen protocol section 14, D11 packet metadata/checksum-bound static page text, D11 final eligibility, D12 final appraisal, and D06 bibliographic metadata only.",
            },
        }
        rows.append(row)
    return rows


def validate(rows: list[dict]) -> None:
    required = {"family_id", "record_id", "extractor_agent_id", "review_context_id", "source_text_sha256", "evidence_band", "appraisal_form", "bibliographic_status", "context_method", "lifecycle_stages", "vdcm_constructs", "emergent_constructs", "measures_findings", "novelty_assessment", "reviewer_notes", "security_attestation"}
    life_keys = set(LIFECYCLE)
    construct_keys = set(CONSTRUCTS)
    novelty_keys = {"precommitment_predictors", "multirole_lifecycle", "touch_queue_separation", "capacity_readiness_dependencies", "verified_completion_forecast"}
    target = sorted(r["family_id"] for r in read_jsonl(APPRAISALS))[285:]
    packet_by_family = {}
    for packet_path in sorted(PACKET_DIR.glob("fulltext_packet_*.jsonl")):
        for packet_row in read_jsonl(packet_path):
            packet_by_family[packet_row["family_id"]] = packet_row
    if len(rows) != 285 or [r["family_id"] for r in rows] != target:
        raise ValueError("partition population/order invalid")
    if len({r["review_context_id"] for r in rows}) != 285:
        raise ValueError("review contexts not unique")
    for row in rows:
        fid = row["family_id"]
        if set(row) != required or row["extractor_agent_id"] != "d13-extractor-b-v1":
            raise ValueError(f"top-level schema invalid: {fid}")
        if set(row["lifecycle_stages"]) != life_keys or set(row["vdcm_constructs"]) != construct_keys:
            raise ValueError(f"coverage schema invalid: {fid}")
        novelty_row = row["novelty_assessment"]
        if set(novelty_row) != novelty_keys | {"same_planning_use", "comparator_story_points", "comparator_hie", "validation_type", "novelty_risk"}:
            raise ValueError(f"novelty dimensions invalid: {fid}")
        if row["evidence_band"] not in {"high", "moderate", "low_contextual"}:
            raise ValueError(f"evidence band invalid: {fid}")
        if row["appraisal_form"] not in {"quantitative_mixed", "qualitative", "secondary_review", "conceptual_framework"}:
            raise ValueError(f"appraisal form invalid: {fid}")
        source_path = ROOT / packet_by_family[fid]["extracted_text_path"]
        source_doc = json.loads(source_path.read_text(encoding="utf-8"))
        page_count = source_doc["page_count"]
        page_text = {int(page["page"]): clean_text(page.get("text", "")) for page in source_doc["pages"]}
        locators = []
        locators += [v["source_locator"] for v in row["lifecycle_stages"].values()]
        locators += [v["source_locator"] for v in row["vdcm_constructs"].values()]
        locators += [row["novelty_assessment"][key]["source_locator"] for key in novelty_keys]
        locators += [v["source_locator"] for v in row["measures_findings"]]
        if not row["measures_findings"]:
            raise ValueError(f"no finding: {fid}")
        for value in row["lifecycle_stages"].values():
            if value["present"] and not value["source_locator"]:
                raise ValueError(f"present lifecycle missing locator: {fid}")
        for code, value in row["vdcm_constructs"].items():
            if value["status"] not in {"present", "absent", "unclear"} or (value["status"] != "absent" and not value["source_locator"]):
                raise ValueError(f"construct invalid: {fid}/{code}")
        for code in novelty_keys:
            value = row["novelty_assessment"][code]
            if value["status"] not in {"met", "partial", "not_met", "unclear"} or (value["status"] in {"met", "partial", "unclear"} and not value["source_locator"]):
                raise ValueError(f"novelty invalid: {fid}/{code}")
        for loc in filter(None, locators):
            m = re.fullmatch(r"page (\d+)", loc)
            if not m or not 1 <= int(m.group(1)) <= page_count:
                raise ValueError(f"locator out of bounds: {fid}/{loc}")
        for finding in row["measures_findings"]:
            if finding["data_nature"] not in {"observed", "self_reported", "modeled", "conceptual", "mixed"}:
                raise ValueError(f"finding data nature invalid: {fid}")
            if finding["direction"] not in {"positive", "negative", "mixed", None, "not_applicable"}:
                raise ValueError(f"finding direction invalid: {fid}")
            finding_page = int(finding["source_locator"].split()[1])
            if finding["quantitative"] != bool(finding["reported_estimate"]):
                raise ValueError(f"finding estimate flag invalid: {fid}/{finding['finding_id']}")
            if finding["reported_estimate"] and finding["reported_estimate"].lower() not in page_text[finding_page].lower():
                raise ValueError(f"reported estimate not found at locator: {fid}/{finding['finding_id']}")
            if finding["reported_uncertainty"] and finding["reported_uncertainty"].lower() not in page_text[finding_page].lower():
                raise ValueError(f"reported uncertainty not found at locator: {fid}/{finding['finding_id']}")
        if novelty_row["same_planning_use"] not in {"yes", "no", "unclear"} or novelty_row["novelty_risk"] not in {"low", "moderate", "high", "critical"}:
            raise ValueError(f"novelty summary invalid: {fid}")
        if sha256(source_path) != row["source_text_sha256"]:
            raise ValueError(f"source hash revalidation failed: {fid}")


def main() -> None:
    rows = build()
    validate(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    temp = OUTPUT.with_suffix(".jsonl.tmp")
    temp.write_text(payload, encoding="utf-8")
    temp.replace(OUTPUT)
    digest = sha256(OUTPUT)
    OUTPUT.with_suffix(OUTPUT.suffix + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    print(json.dumps({"status": "valid_complete", "rows": len(rows), "sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
