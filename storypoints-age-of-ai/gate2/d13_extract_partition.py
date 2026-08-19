"""Generate a conservative, source-grounded D13 extraction partition.

This local-only utility reads the frozen D11 page text, D11 packet metadata,
and D12 quality ledger.  It deliberately records absence/uncertainty rather
than inferring human workload from technical outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
D12 = BASE / "d12/final/quality_appraisals.jsonl"
D11_PACKETS = BASE / "d11/screening"
TEXT_DIR = BASE / "d11/extraction/text"
D08_PACKETS = BASE / "d08"

LIFECYCLE = {
    "requirements": ("requirement", "problem framing", "user stor"),
    "context_prompt": ("prompt", "context window", "prompt engineering", "retrieval augmented"),
    "architecture_design": ("architecture", "software design", "design decision"),
    "implementation_refinement": ("implementation", "code generation", "programming", "debugg"),
    "integration": ("integration", "merge", "continuous integration"),
    "code_review": ("code review", "pull request", "reviewer"),
    "security_compliance": ("security", "vulnerabil", "compliance", "privacy", "secure code"),
    "testing": ("unit test", "software test", "test case", "regression test", "quality assurance"),
    "release_operations": ("software deployment", "continuous deployment", "production deployment", "software release", "release engineering", "devops", "production operations"),
    "manual_qa_uat": ("manual testing", "user acceptance testing", "manual qa"),
    "coordination_switching": ("coordination", "context switch", "collaboration", "communication"),
}

CONSTRUCTS = {
    "PDD": ("effort estimation", "story point", "pre-commit", "task complexity", "planning poker"),
    "RHTD": ("human effort", "human oversight", "manual effort", "developer effort", "review effort", "cognitive load", "mental workload"),
    "SAE": ("automation", "ai-assisted", "copilot", "large language model", "generative ai", "agentic"),
    "ERS": ("readiness", "test coverage", "validation evidence", "verification", "quality gate", "acceptance criteria"),
    "ARC": ("team capacity", "available capacity", "staffing", "resource availability"),
    "RCP": ("workload", "capacity pressure", "overload", "burnout", "cognitive load", "mental demand"),
    "CQD": ("queue", "waiting time", "bottleneck", "review delay", "cycle time"),
    "VDC": ("delivery capacity", "throughput", "lead time", "deployment frequency", "release frequency", "completed work"),
}

ROLE_TERMS = ("developer", "reviewer", "tester", "architect", "manager", "product owner", "security engineer", "team")
RESULT_TERMS = ("result", "found", "show", "demonstrat", "report", "indicat", "observ", "improv", "reduc", "increas", "effect")


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def metadata_map():
    result = {}
    for path in sorted(D08_PACKETS.glob("screening_packet_*.jsonl")):
        for row in read_jsonl(path):
            member = next((m for m in row.get("member_reports", []) if m.get("canonical_id") == row.get("record_id")), None)
            if member is None and row.get("member_reports"):
                member = row["member_reports"][0]
            result[row["family_id"]] = {**row, "member": member or {}}
    return result


def d11_map():
    result = {}
    for path in sorted(D11_PACKETS.glob("fulltext_packet_*.jsonl")):
        for row in read_jsonl(path):
            result[row["family_id"]] = row
    return result


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def page_hit(pages, terms):
    for page in pages:
        low = page.get("text", "").lower()
        for term in terms:
            if re.search(r"(?<![a-z0-9])" + re.escape(term) + r"[a-z]*?(?![a-z0-9])", low):
                return page["page"], term
    return None, None


def locator(page, term=None):
    if page is None:
        return None
    return f'page {page}' + (f' (text containing "{term}")' if term else "")


def sentences(text):
    clean = norm(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", clean) if 35 <= len(s.strip()) <= 600]


def select_finding(meta, pages):
    abstract = meta.get("member", {}).get("abstract") or ""
    candidates = sentences(abstract)
    selected = None
    for sentence in reversed(candidates):
        if any(term in sentence.lower() for term in RESULT_TERMS):
            selected = sentence
            break
    selected = selected or (candidates[-1] if candidates else None)
    page = None
    if selected:
        needle_words = [w.lower() for w in re.findall(r"[A-Za-z]{5,}", selected)[:8]]
        for p in pages:
            low = p.get("text", "").lower()
            if sum(w in low for w in needle_words) >= min(4, len(needle_words)):
                page = p["page"]
                break
    fallback_scope = False
    if selected is None:
        # Prefer an explicit results-bearing sentence in the report body. Limit
        # the scan to the main body to reduce reference-list false positives.
        for p in pages[: max(1, int(len(pages) * 0.8))]:
            for sentence in sentences(p.get("text", "")):
                if any(term in sentence.lower() for term in RESULT_TERMS):
                    selected, page = sentence, p["page"]
                    break
            if selected:
                break
    if selected is None:
        title = meta.get("member", {}).get("title") or "Untitled study"
        selected = f"The report's stated subject is {title}. No results-bearing sentence was identified by this conservative pass."
        page = 1
        fallback_scope = True
    # A bounded faithful rendering. It makes no causal or workload inference.
    selected = norm(selected)
    if len(selected) > 420:
        selected = selected[:417].rsplit(" ", 1)[0] + "..."
    if re.match(r"^we\b", selected, re.I):
        value = re.sub(r"^we\b", "The study", selected, flags=re.I)
    elif re.match(r"^our (results|findings)\b", selected, re.I):
        value = "The authors report that " + re.sub(r"^our (results|findings)\s*", "", selected, flags=re.I).lstrip(" ,:")
    else:
        value = "The report states that " + selected[0].lower() + selected[1:]
    quant = bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:%|percent\b|hours?\b|minutes?\b|days?\b|participants?\b|teams?\b|projects?\b|repositories?\b|pull requests?\b|prs?\b)", selected, re.I))
    estimates = re.findall(r"(?:~|≈)?\d+(?:\.\d+)?\s*(?:%|percent\b|hours?\b|minutes?\b|days?\b)", selected, re.I)
    participant = re.search(r"\b(?:study|sample)\s+with\s+(\d+)\s+participants?\b", selected, re.I)
    if participant:
        estimates.append(f"sample size n={participant.group(1)}")
    for metric, number in re.findall(r"\b(?:Mean\s+)?(SUS|NASA-TLX)\s*=\s*(\d+(?:\.\d+)?)", selected, re.I):
        estimates.append(f"mean {metric.upper()}={number}")
    uncertainty = re.findall(
        r"(?:\b(?:95%\s*)?CI\b|\bconfidence interval\b|\bp\s*[<=>]|\b(?:SD|SE)\s*=)\s*[^,;.]{0,45}",
        selected,
        re.I,
    )
    low = selected.lower()
    if any(k in low for k in ("increase", "improv", "faster", "gain", "higher", "benefit")) and any(k in low for k in ("decrease", "reduc", "slower", "lower", "risk", "error")):
        direction = "mixed"
    elif any(k in low for k in ("increase", "improv", "faster", "gain", "higher", "benefit", "reduc", "decrease")):
        direction = "positive"
    elif any(k in low for k in ("worse", "harm", "risk", "error", "lower quality", "slower")):
        direction = "negative"
    else:
        direction = None
    if fallback_scope:
        anchor = norm(meta.get("member", {}).get("title") or "Untitled study").replace('"', "'")
        exact_locator = "page 1"
    else:
        anchor = norm(" ".join(selected.split()[:10])).replace('"', "'")
        exact_locator = f"page {page or 1}"
    return {
        "finding_id": "F1",
        "field_name": "study_scope_no_result_identified" if fallback_scope else "principal_reported_finding",
        "value": value,
        "unit": None,
        "data_nature": None,  # supplied from appraisal below
        "direction": direction,
        "source_locator": exact_locator,
        "quantitative": quant,
        "reported_estimate": "; ".join(estimates) if estimates else None,
        "reported_uncertainty": "; ".join(uncertainty) if uncertainty else None,
        "limitations": "Single conservatively selected study-level finding; D17 author verification is required before citation or outcome-bearing use.",
    }


def context_method(appraisal, meta, pages):
    full = " ".join(p.get("text", "") for p in pages)
    low = full.lower()
    sample_match = re.search(r"\b(?:n\s*=\s*)?(\d{1,6})\s+(participants?|developers?|programmers?|teams?|projects?|repositories?|pull requests?|prs?|tasks?|responses?)\b", full, re.I)
    duration_match = re.search(r"\b(?:over|during|for)\s+(\d+(?:\.\d+)?\s+(?:hours?|days?|weeks?|months?|years?))\b", full, re.I)
    tool_terms = [x for x in ("GitHub Copilot", "ChatGPT", "GPT-4", "GPT-3.5", "Claude", "Gemini", "Code Llama", "Large Language Model") if x.lower() in low]
    availability = "reported" if any(x in low for x in ("github.com", "replication package", "dataset is available", "source code is available")) else "not_identified"
    sample_page, _ = page_hit(pages, (sample_match.group(0),)) if sample_match else (None, None)
    duration_page, _ = page_hit(pages, (duration_match.group(0),)) if duration_match else (None, None)
    ai_page, ai_term = page_hit(pages, tuple(tool_terms)) if tool_terms else (None, None)
    if "open source" in low or "github repositor" in low:
        setting = "open_source_software"
    elif any(x in low for x in ("industrial case study", "industry partner", "software company", "professional developer")):
        setting = "industry_or_professional"
    elif any(x in low for x in ("controlled experiment", "laboratory experiment", "lab study")):
        setting = "controlled_or_laboratory"
    else:
        setting = None
    return {
        "country_sector": None,
        "organizational_setting": setting,
        "unit_of_analysis": sample_match.group(2).lower() if sample_match else None,
        "participants_teams_tasks_projects_repositories_prs": norm(sample_match.group(0)) if sample_match else None,
        "sample_size": int(sample_match.group(1)) if sample_match else None,
        "duration": duration_match.group(1) if duration_match else None,
        "ai_tool_model_mode": tool_terms or None,
        "comparison_condition": "present" if any(x in low for x in ("control group", "baseline", "compared with", "comparison condition", "without copilot", "without ai")) else None,
        "method_design": appraisal.get("design_type"),
        "data_nature": appraisal.get("data_nature", "conceptual"),
        "data_code_materials_availability": availability,
        "source_locators": {
            "sample": locator(sample_page) if sample_page else None,
            "duration": locator(duration_page) if duration_page else None,
            "ai_tool_model_mode": locator(ai_page, ai_term) if ai_page else None,
        },
    }


def extract_row(appraisal, meta, packet):
    family = appraisal["family_id"]
    text_path = ROOT / packet["extracted_text_path"]
    if sha256(text_path) != packet["extracted_text_sha256"]:
        raise ValueError(f"source hash mismatch: {family}")
    text_doc = json.loads(text_path.read_text(encoding="utf-8"))
    pages = text_doc["pages"]
    full_low = " ".join(p.get("text", "") for p in pages).lower()
    lifecycle = {}
    for code, terms in LIFECYCLE.items():
        page, term = page_hit(pages, terms)
        lifecycle[code] = {"present": page is not None, "source_locator": locator(page, term)}
    constructs = {}
    for code, terms in CONSTRUCTS.items():
        page, term = page_hit(pages, terms)
        if page is None:
            constructs[code] = {"status": "absent", "source_locator": None, "rationale": f"No explicit {code} indicator was identified in the static page text."}
        else:
            constructs[code] = {"status": "present", "source_locator": locator(page, term), "rationale": f"The text explicitly addresses an indicator mapped to {code}; mapping does not establish framework equivalence."}
    finding = select_finding(meta, pages)
    dn = appraisal.get("data_nature") or "conceptual"
    finding["data_nature"] = dn if dn in {"observed", "self_reported", "modeled", "conceptual", "mixed"} else "mixed"
    roles = sum(term in full_low for term in ROLE_TERMS)
    stages = sum(v["present"] for v in lifecycle.values())
    def dim(status, page=None, term=None, rationale=""):
        return {"status": status, "source_locator": locator(page, term), "rationale": rationale}
    pdd_page, pdd_term = page_hit(pages, CONSTRUCTS["PDD"])
    q_page, q_term = page_hit(pages, CONSTRUCTS["CQD"])
    cap_page, cap_term = page_hit(pages, CONSTRUCTS["ARC"] + CONSTRUCTS["RCP"])
    ready_page, ready_term = page_hit(pages, CONSTRUCTS["ERS"])
    forecast_page, forecast_term = page_hit(pages, ("forecast", "predict", "estimat"))
    verified = ready_page is not None
    novelty = {
        "dimensions": {
            "precommitment_predictors": dim("partial" if pdd_page else "not_met", pdd_page, pdd_term, "An estimation/demand-driver signal is present, but full prospective pre-commitment use is not inferred." if pdd_page else "No explicit pre-commitment predictor was located."),
            "multirole_lifecycle": dim("partial" if roles >= 2 and stages >= 2 else "not_met", *page_hit(pages, ROLE_TERMS) if roles >= 2 and stages >= 2 else (None, None), rationale="Multiple role and lifecycle signals occur, but an integrated multi-role lifecycle model is not inferred." if roles >= 2 and stages >= 2 else "No explicit integrated multi-role lifecycle model was located."),
            "touch_queue_separation": dim("partial" if constructs["RHTD"]["status"] == "present" and q_page else "not_met", q_page if constructs["RHTD"]["status"] == "present" else None, q_term if constructs["RHTD"]["status"] == "present" else None, "Human-demand and queue signals co-occur, without proof they are modeled separately." if constructs["RHTD"]["status"] == "present" and q_page else "No explicit separation of human touch demand from queue delay was located."),
            "capacity_readiness_dependencies": dim("partial" if cap_page and ready_page else "not_met", cap_page if ready_page else None, cap_term if ready_page else None, "Capacity and readiness signals co-occur; explicit dependency modeling is not established." if cap_page and ready_page else "No combined capacity-readiness-dependency model was located."),
            "verified_completion_forecast": dim("partial" if forecast_page and verified else "not_met", forecast_page if verified else None, forecast_term if verified else None, "Forecast/estimation and verification signals co-occur, but verified-completion forecasting is not established." if forecast_page and verified else "No explicit forecast of verified completion was located."),
        },
        "same_planning_use": "unclear" if pdd_page else "no",
        "comparator_story_points": "story point" in full_low,
        "comparator_hie": bool(re.search(r"\bhie\b|human input effort", full_low)),
        "validation_type": appraisal.get("design_type") or "unclear",
        "novelty_risk": "low",
    }
    partial_count = sum(v["status"] in {"met", "partial"} for v in novelty["dimensions"].values())
    # Keyword co-occurrence can flag overlap for author review but cannot by
    # itself establish a critical/direct duplicate.
    novelty["novelty_risk"] = "high" if partial_count >= 4 else "moderate" if partial_count >= 2 else "low"
    member = meta.get("member", {})
    publication_status = "preprint" if member.get("record_type") == "posted-content" or "arxiv" in (member.get("venue") or "").lower() else "published"
    context = context_method(appraisal, meta, pages)
    emergent = []
    for label, terms in {
        "trust_and_reliance": ("trust", "over-reliance", "reliance"),
        "developer_experience": ("developer experience", "satisfaction", "usability"),
        "error_propagation": ("error propagation", "hallucination"),
        "skill_change": ("skill", "learning", "expertise"),
    }.items():
        page, term = page_hit(pages, terms)
        if page:
            emergent.append({"construct": label, "source_locator": locator(page, term), "rationale": "Explicit textual signal retained outside the a priori VDCM code set."})
    return {
        "family_id": family,
        "record_id": packet["record_id"],
        "extractor_agent_id": "d13-extractor-a-v1",
        "review_context_id": f"d13-extractor-a-{family[4:12]}",
        "source_text_sha256": packet["extracted_text_sha256"],
        "evidence_band": appraisal["evidence_band"],
        "appraisal_form": appraisal["appraisal_form"],
        "bibliographic_status": {
            "title": member.get("title"), "authors": member.get("authors"),
            "year": int((member.get("published") or "0000")[:4]) if (member.get("published") or "")[:4].isdigit() else None,
            "venue": member.get("venue"), "doi": member.get("doi") or None,
            "arxiv_id": member.get("arxiv_id") or None, "verified_url": member.get("url") or None,
            "publication_status": publication_status, "version_date": member.get("published") or None,
            "evidence_stream": meta.get("evidence_stratum_candidate"),
            "study_type": appraisal.get("design_type"),
            "peer_review_status": "not_peer_reviewed_or_unclear" if publication_status == "preprint" else "peer_reviewed_or_published_venue",
        },
        "context_method": context,
        "lifecycle_stages": lifecycle,
        "vdcm_constructs": constructs,
        "emergent_constructs": emergent,
        "measures_findings": [finding],
        "novelty_assessment": novelty,
        "reviewer_notes": "Conservative automated source-grounded extraction for evidence mapping; quantities and human cognitive workload were not inferred from technical outcomes. Material claims require D17 author verification.",
        "security_attestation": {"local_only": True, "network_used": False, "git_or_history_inspected": False, "environment_or_secrets_inspected": False, "credentials_accessed": False, "packages_installed": False, "pdf_executed": False, "links_or_embedded_content_opened": False, "source_scope": "Frozen D11 checksum-bound static page text, D11/D08 metadata, and D12 final appraisal only"},
    }


def validate(rows, expected, d12_by_family, packet_by_family):
    if len(rows) != expected or len({r["family_id"] for r in rows}) != expected:
        raise ValueError("population mismatch")
    required = {"family_id","record_id","extractor_agent_id","review_context_id","source_text_sha256","evidence_band","appraisal_form","bibliographic_status","context_method","lifecycle_stages","vdcm_constructs","emergent_constructs","measures_findings","novelty_assessment","reviewer_notes","security_attestation"}
    life_keys = set(LIFECYCLE); construct_keys = set(CONSTRUCTS)
    dim_keys = {"precommitment_predictors","multirole_lifecycle","touch_queue_separation","capacity_readiness_dependencies","verified_completion_forecast"}
    for row in rows:
        if set(row) != required: raise ValueError(f"top-level schema: {row['family_id']}")
        fam=row["family_id"]; app=d12_by_family[fam]; packet=packet_by_family[fam]
        if row["source_text_sha256"] != packet["extracted_text_sha256"]: raise ValueError(f"hash: {fam}")
        if row["evidence_band"] != app["evidence_band"] or row["appraisal_form"] != app["appraisal_form"]: raise ValueError(f"appraisal: {fam}")
        if set(row["lifecycle_stages"]) != life_keys or set(row["vdcm_constructs"]) != construct_keys: raise ValueError(f"construct schema: {fam}")
        if set(row["novelty_assessment"]["dimensions"]) != dim_keys: raise ValueError(f"novelty dimensions: {fam}")
        if not row["measures_findings"]: raise ValueError(f"finding missing: {fam}")
        max_page=packet["page_count"]
        for finding in row["measures_findings"]:
            match=re.search(r"page (\d+)", finding["source_locator"] or "")
            if not match or int(match.group(1)) > max_page: raise ValueError(f"finding locator: {fam}")
            if finding["data_nature"] not in {"observed","self_reported","modeled","conceptual","mixed"}: raise ValueError(f"data nature: {fam}")
            if finding["direction"] not in {"positive","negative","mixed",None,"not_applicable"}: raise ValueError(f"direction: {fam}")


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--part",choices=("a","b"),required=True); parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    appraisals=sorted(read_jsonl(D12),key=lambda r:r["family_id"])
    selected=appraisals[:285] if args.part=="a" else appraisals[285:]
    metas=metadata_map(); packets=d11_map(); d12_by={r["family_id"]:r for r in appraisals}
    rows=[extract_row(a,metas[a["family_id"]],packets[a["family_id"]]) for a in selected]
    validate(rows,len(selected),d12_by,packets)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    payload="".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in rows)
    args.output.write_text(payload,encoding="utf-8")
    digest=sha256(args.output)
    args.output.with_suffix(args.output.suffix+".sha256").write_text(f"{digest}  {args.output.name}\n",encoding="utf-8")
    print(json.dumps({"part":args.part,"rows":len(rows),"sha256":digest,"bands":{b:sum(r['evidence_band']==b for r in rows) for b in ('high','moderate','low_contextual')},"novelty_risk":{b:sum(r['novelty_assessment']['novelty_risk']==b for r in rows) for b in ('low','moderate','high','critical')}},indent=2))


if __name__ == "__main__":
    main()
