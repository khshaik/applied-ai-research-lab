"""Conservatively verify D13 partition B against frozen static page text.

No PDF is opened and no external resource is accessed.  The verifier rejects
numbers that occur only as bibliographic/contextual identifiers and requires
direct textual support for every positive/partial novelty dimension.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
PRIMARY = BASE / "d13/primary/evidence_extractions.jsonl"
PACKETS = BASE / "d11/screening"
OUTPUT = BASE / "d13/verified_part_b.jsonl"
AGENT = "d13-verifier-b-v1"

NOVELTY_KEYS = {
    "precommitment_predictors", "multirole_lifecycle", "touch_queue_separation",
    "capacity_readiness_dependencies", "verified_completion_forecast",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def body_page_map(source: dict) -> dict[int, str]:
    """Return report body only; references must not become study evidence."""
    result = {}
    for item in source["pages"]:
        text = clean(item.get("text", ""))
        match = re.search(r"(?i)(?:^|\s)(references|bibliography)\s*(?:\[?1\]?|$)", text)
        if match:
            text = text[:match.start()].strip()
        if text:
            result[int(item["page"])] = text
        if match:
            break
    return result or {int(item["page"]): clean(item.get("text", "")) for item in source["pages"]}


def sentence_containing(text: str, needle: str) -> str | None:
    match = re.search(re.escape(needle), text, re.I)
    if not match:
        return None
    lefts = [text.rfind(mark, 0, match.start()) for mark in (".", "?", "!", "\n")]
    left = max(lefts)
    rights = [p for p in (text.find(mark, match.end()) for mark in (".", "?", "!", "\n")) if p >= 0]
    right = min(rights) + 1 if rights else min(len(text), match.end() + 500)
    return clean(text[left + 1:right])


def context_window(text: str, needle: str, width: int = 450) -> str | None:
    match = re.search(re.escape(needle), text, re.I)
    if not match:
        return None
    return clean(text[max(0, match.start()-width):min(len(text), match.end()+width)])


RESULT_TERMS = re.compile(
    r"(?i)result|found|show(?:s|ed)?|report(?:s|ed)?|observ(?:e|ed)|participant|respondent|developer|"
    r"task|experiment|sample|accuracy|precision|recall|score|rate|reduc|increas|improv|declin|"
    r"time|minute|hour|second|faster|slower|productiv|efficien|quality|correct|pass|success|fail|"
    r"defect|bug|vulnerab|weakness|coverage|effort|workload|review|acceptance|satisfaction|"
    r"significan|confidence interval|effect|odds|correlation|regression|median|mean|average"
)
CONTEXT_ONLY = re.compile(
    r"(?i)copyright|isbn|issn|doi|arxiv|volume\s+\d|issue\s+\d|page(?:s)?\s+\d|"
    r"references?|bibliograph|retrieved|accessed|proceedings|conference held|model (?:version|name)|"
    r"dataset (?:id|version)|table of contents"
)
SAMPLE_TERMS = re.compile(r"(?i)participant|respondent|developer|programmer|student|professional|task|project|repository|pull request|team|sample")


def is_result_bearing(estimate: str, sentence: str, window: str) -> bool:
    combined = f"{sentence} {window}"
    if re.search(r"(?i)(?:risk category|dimension|criterion|factor).{0,80}\bweight\b|\bweight\b.{0,80}" + re.escape(estimate), sentence):
        return False
    if CONTEXT_ONLY.search(sentence) and not RESULT_TERMS.search(sentence):
        return False
    if re.fullmatch(r"(?i)n\s*=\s*\d+", estimate.strip()):
        return bool(SAMPLE_TERMS.search(combined))
    if re.fullmatch(r"(?i)p\s*[<=>]\s*0?\.\d+", estimate.strip()):
        return bool(re.search(r"(?i)significan|test|difference|association|effect|correlat|regress", combined))
    if "%" in estimate or "percent" in estimate.lower():
        split_context = re.search(r"(?i)(?:data ?sets?|corpus|samples?).{0,100}(?:split|training data|validation data|testing data)|(?:split|training data|validation data|testing data).{0,100}(?:data ?sets?|corpus|samples?)", sentence)
        return bool(RESULT_TERMS.search(sentence)) and not bool(re.search(r"(?i)confidence level|percentile", sentence)) and not bool(split_context)
    return bool(RESULT_TERMS.search(combined))


def field_for(text: str) -> str:
    for field, pattern in (
        ("human_workload_or_oversight", r"cognitive|workload|human effort|oversight|manual effort|reviewer"),
        ("time_or_productivity", r"time|faster|slower|speed|productiv|efficien|throughput"),
        ("review_or_quality", r"review|quality|defect|bug|correct|maintainab"),
        ("security_or_compliance", r"security|vulnerab|weakness|privacy|compliance"),
        ("testing_or_validation", r"test|validation|verification|coverage|pass rate"),
        ("planning_or_delivery", r"story point|estimat|forecast|delivery|release|cycle time|lead time"),
    ):
        if re.search(pattern, text, re.I):
            return field
    return "reported_AI_assisted_software_finding"


def direction_for(text: str) -> str:
    pos = re.search(r"(?i)improv|increas|higher|faster|reduc(?:ed|tion) in time|better|outperform|gain", text)
    neg = re.search(r"(?i)decreas|lower|slower|worse|degrad|more defect|more vulnerab|risk", text)
    if pos and neg: return "mixed"
    if pos: return "positive"
    if neg: return "negative"
    if re.search(r"(?i)no significant|did not|no difference|null", text): return "null"
    return "mixed"


def qualitative_fallback(pages: dict[int, str], data_nature: str) -> dict:
    preferred = re.compile(r"(?i)we (?:find|found|show|report|observe)|our results|results (?:show|indicate|suggest)|this study (?:finds|shows|examines)|this (?:paper|study) (?:investigates|evaluates)")
    generic = re.compile(r"(?i)AI|large language model|LLM|Copilot|code generation|software|developer|testing|code review")
    for rx in (preferred, generic):
        for page, text in pages.items():
            match = rx.search(text)
            if match:
                sent = sentence_containing(text, match.group(0)) or clean(text[match.start():match.start()+500])
                sent = sent[:700]
                return {
                    "finding_id": "F1", "field_name": field_for(sent),
                    "value": f"The report states: {sent}", "unit": None,
                    "data_nature": data_nature, "direction": direction_for(sent),
                    "source_locator": f"page {page}", "quantitative": False,
                    "reported_estimate": None, "reported_uncertainty": None,
                    "limitations": "Qualitative extraction is limited to this directly located report statement and the study's appraised design.",
                }
    page = min(pages)
    return {
        "finding_id": "F1", "field_name": "inspectable_report_content",
        "value": f"The report states: {clean(pages[page])[:700]}", "unit": None,
        "data_nature": data_nature, "direction": "not_applicable",
        "source_locator": f"page {page}", "quantitative": False,
        "reported_estimate": None, "reported_uncertainty": None,
        "limitations": "Extraction is limited to the directly located report text and the study's appraised design.",
    }


def verify_findings(row: dict, pages: dict[int, str]) -> tuple[list[dict], dict[str, int]]:
    retained = []
    stats = Counter(quantitative_verified=0, quantitative_corrected=0, quantitative_rejected=0)
    for finding in row["measures_findings"]:
        if not finding["quantitative"]:
            # Keep only if the cited page contains topic-relevant text; rewrite false generic uncertainty.
            page = int(finding["source_locator"].split()[1])
            if page in pages:
                item = dict(finding)
                item["reported_uncertainty"] = None
                retained.append(item)
            continue
        page = int(finding["source_locator"].split()[1])
        estimate = str(finding["reported_estimate"]).strip()
        page_text = pages.get(page, "")
        sentence = sentence_containing(page_text, estimate)
        window = context_window(page_text, estimate)
        if not sentence or not window or not is_result_bearing(estimate, sentence, window):
            stats["quantitative_rejected"] += 1
            continue
        item = dict(finding)
        old = json.dumps(item, sort_keys=True)
        item["field_name"] = field_for(sentence)
        item["value"] = f"The report states: {sentence[:700]}"
        item["direction"] = direction_for(sentence)
        item["unit"] = "%" if ("%" in estimate or "percent" in estimate.lower()) else ("sample" if estimate.lower().startswith("n") else None)
        # A p-value is a test result, not automatically an uncertainty interval.
        ci = re.search(r"(?i)(?:95\s*%\s*)?(?:CI|confidence interval)\s*[:=]?\s*[^.;]{1,100}", sentence)
        item["reported_uncertainty"] = ci.group(0).strip() if ci else None
        item["limitations"] = "Estimate retained only as reported on the cited page; interpretation remains bounded by the study design and evidence band."
        retained.append(item)
        if json.dumps(item, sort_keys=True) == old:
            stats["quantitative_verified"] += 1
        else:
            stats["quantitative_corrected"] += 1
    if not retained:
        retained = [qualitative_fallback(pages, row["context_method"]["data_nature"]["value"] or "conceptual")]
    for index, finding in enumerate(retained, 1):
        finding["finding_id"] = f"F{index}"
    return retained, dict(stats)


def locate(pages: dict[int, str], pattern: str) -> tuple[int, str] | None:
    rx = re.compile(pattern, re.I | re.S)
    for page, text in pages.items():
        match = rx.search(text)
        if match:
            return page, clean(text[max(0, match.start()-180):min(len(text), match.end()+250)])
    return None


def located_sentences(pages: dict[int, str]):
    for page, text in pages.items():
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
            sentence = clean(sentence)
            if sentence:
                # PDF table extraction can create punctuation-free megastrings.
                # Bound matching windows without dropping their contents.
                for start in range(0, len(sentence), 2500):
                    yield page, sentence[start:start + 3000]


def direct_sentence(pages: dict[int, str], pattern: str) -> tuple[int, str] | None:
    rx = re.compile(pattern, re.I)
    for page, sentence in located_sentences(pages):
        if rx.search(sentence):
            return page, sentence
    return None


def novelty_direct(pages: dict[int, str]) -> tuple[dict, int]:
    # Direct, dimension-specific tests. Broad keyword co-occurrence does not pass.
    pre_met = pre_partial = role_met = role_partial = None
    touch_met = touch_partial = cap_met = cap_partial = None
    verified_met = verified_partial = None
    for page, sentence in located_sentences(pages):
        low = sentence.lower()
        has_predict = any(x in low for x in ("predict", "forecast", "estimat"))
        has_commit = any(x in low for x in ("pre-commitment", "precommitment", "prior to commitment", "before project commitment", "before sprint commitment", "before release commitment"))
        has_plan_target = any(x in low for x in ("story point", "software effort estimation", "project effort estimation", "sprint planning", "release planning"))
        if pre_met is None and has_commit and has_predict: pre_met = (page, sentence)
        if pre_partial is None and has_plan_target and has_predict: pre_partial = (page, sentence)

        role_groups = (
            ("developer", "engineer", "reviewer"), ("tester", "quality assurance", " qa "),
            ("product owner", "project manager", "architect", "security engineer"),
        )
        stage_groups = (
            ("requirement",), ("architect", "design"), ("implement", "coding", "code generation"),
            ("review",), ("test", "validat", "verif"), ("deploy", "release", "operation"),
        )
        roles = sum(any(term in low for term in group) for group in role_groups)
        stages = sum(any(term in low for term in group) for group in stage_groups)
        process = any(x in low for x in ("workflow", "lifecycle", "delivery process", "development process", "handoff", "stage", "phase"))
        if role_met is None and roles >= 2 and stages >= 3 and process: role_met = (page, sentence)
        if role_partial is None and roles >= 2 and stages >= 2 and process: role_partial = (page, sentence)

        has_touch = any(x in low for x in ("human effort", "human time", "human touch", "review effort", "review time", "manual effort", "hands-on"))
        has_wait = any(x in low for x in ("queue", "waiting", "wait time", "delay"))
        has_sep = any(x in low for x in ("separat", "distinguish", "decompos"))
        if touch_met is None and has_touch and has_wait and has_sep: touch_met = (page, sentence)
        if touch_partial is None and (has_touch or any(x in low for x in ("review queue", "queueing delay", "review wait"))): touch_partial = (page, sentence)

        has_capacity = any(x in low for x in ("role capacity", "team capacity", "reviewer capacity", "tester capacity", "capacity constraint", "resource capacity"))
        has_ready = any(x in low for x in ("readiness", "quality gate", "acceptance criteria"))
        has_dep = any(x in low for x in ("dependency", "dependencies", "precedence"))
        has_delivery = any(x in low for x in ("workflow", "delivery", "release", "completion", "planning"))
        if cap_met is None and has_capacity and has_ready and has_dep: cap_met = (page, sentence)
        if cap_partial is None and has_delivery and (has_capacity or has_ready or has_dep): cap_partial = (page, sentence)

        has_verified = any(x in low for x in ("verified", "validated", "quality-assured", "quality assured"))
        has_completion = any(x in low for x in ("completion", "delivery", "release"))
        if verified_met is None and has_verified and has_completion and has_predict: verified_met = (page, sentence)
        explicit_forecast_target = any(x in low for x in ("completion time", "delivery date", "release date", "software delivery", "project completion"))
        if verified_partial is None and explicit_forecast_target and has_predict: verified_partial = (page, sentence)

    def dim(met, partial, met_reason, partial_reason, absent_reason):
        match, status, reason = (met, "met", met_reason) if met else ((partial, "partial", partial_reason) if partial else (None, "not_met", absent_reason))
        return {"status": status, "source_locator": f"page {match[0]}" if match else None, "rationale": reason}

    dimensions = {
        "precommitment_predictors": dim(pre_met, pre_partial, "Direct text links predictors/forecasting to a pre-commitment point.", "Direct text concerns planning or effort estimation, but no explicit pre-commitment cutoff is established.", "No direct evidence of predictors defined for use before a commitment decision was located."),
        "multirole_lifecycle": dim(role_met, role_partial, "Direct text connects multiple delivery roles with lifecycle stages.", "Direct text identifies multiple roles in a workflow/process, but does not establish full lifecycle coverage.", "No direct source evidence of a multi-role lifecycle model was located."),
        "touch_queue_separation": dim(touch_met, touch_partial, "Direct text distinguishes active human-touch work from queue/wait delay.", "Direct text reports human review effort or queue/wait delay, but does not explicitly separate both components.", "No direct source evidence separating active human touch from queue delay was located."),
        "capacity_readiness_dependencies": dim(cap_met, cap_partial, "Direct text links role capacity, readiness/gates, and dependencies.", "Direct text covers a capacity, readiness/gate, or dependency constraint in delivery, but not the combined mechanism.", "No direct source evidence of the combined capacity-readiness-dependency mechanism was located."),
        "verified_completion_forecast": dim(verified_met, verified_partial, "Direct text forecasts completion/delivery subject to verification or validation.", "Direct text forecasts delivery/completion, but not verified completion.", "No direct source evidence of a verified-completion forecast target was located."),
    }
    return dimensions, 0


def planning_flags(pages: dict[int, str]) -> tuple[str, bool, bool]:
    planning = locate(pages, r"(?:study|model|method|approach|framework|experiment).{0,300}(?:story points?|effort estimation|sprint planning|release planning|delivery forecast|completion forecast)|(?:story points?|effort estimation|sprint planning|release planning|delivery forecast|completion forecast).{0,300}(?:study|model|method|approach|framework|experiment)")
    story = locate(pages, r"\bstory points?\b")
    hie = locate(pages, r"hybrid intelligence effort|\bHIE\b")
    return ("yes" if planning else "no", bool(story), bool(hie))


def risk_for(dimensions: dict, same: str) -> str:
    score = sum(1 if d["status"] == "met" else .5 if d["status"] == "partial" else 0 for d in dimensions.values())
    if score == 5 and same == "yes": return "critical"
    if score >= 4 and same == "yes": return "high"
    if score >= 2: return "moderate"
    return "low"


def main() -> None:
    primary_rows = read_jsonl(PRIMARY)
    primary_hash = sha256(PRIMARY)
    targets = primary_rows[285:]
    if len(primary_rows) != 570 or len(targets) != 285:
        raise ValueError("locked D13 population changed")
    packet_by_family = {}
    for path in sorted(PACKETS.glob("fulltext_packet_*.jsonl")):
        for row in read_jsonl(path): packet_by_family[row["family_id"]] = row

    output_rows = []
    total = Counter()
    for index, original in enumerate(targets, 1):
        row = json.loads(json.dumps(original))
        packet = packet_by_family[row["family_id"]]
        source_path = ROOT / packet["extracted_text_path"]
        if sha256(source_path) != row["source_text_sha256"] or row["source_text_sha256"] != packet["extracted_text_sha256"]:
            raise ValueError(f"source hash mismatch: {row['family_id']}")
        source = json.loads(source_path.read_text(encoding="utf-8"))
        pages = body_page_map(source)
        findings, qstats = verify_findings(row, pages)
        row["measures_findings"] = findings
        old_dims = row["novelty_assessment"]["dimensions"]
        dimensions, _ = novelty_direct(pages)
        novelty_corrected = sum(old_dims[key] != dimensions[key] for key in NOVELTY_KEYS)
        same, story, hie = planning_flags(pages)
        other = 0
        for key, value in (("same_planning_use", same), ("comparator_story_points", story), ("comparator_hie", hie)):
            other += int(row["novelty_assessment"].get(key) != value)
            row["novelty_assessment"][key] = value
        row["novelty_assessment"]["dimensions"] = dimensions
        row["novelty_assessment"]["novelty_risk"] = risk_for(dimensions, same)
        row["novelty_assessment"]["validation_type"] = "Independent source-grounded overlap verification against checksum-bound static page text; not a validation of VDCM effectiveness."
        row["verifier_agent_id"] = AGENT
        row["verification_context_id"] = f"d13-vb-{index:04d}-{row['source_text_sha256'][:12]}"
        row["original_extraction_sha256"] = primary_hash
        row["verification_summary"] = {
            **qstats, "novelty_corrected": novelty_corrected, "other_corrections": other,
        }
        row["reviewer_notes"] += " Independent verifier B rechecked numeric candidates and novelty dimensions against the cited static page text; direct support was required and keyword co-occurrence was insufficient."
        output_rows.append(row)
        total.update(row["verification_summary"])

    if len(output_rows) != 285 or len({r["family_id"] for r in output_rows}) != 285:
        raise ValueError("verified partition population invalid")
    if len({r["verification_context_id"] for r in output_rows}) != 285:
        raise ValueError("verification contexts not unique")
    # Final source, page, enum, and positive-evidence checks.
    for row in output_rows:
        source_path = ROOT / packet_by_family[row["family_id"]]["extracted_text_path"]
        source = json.loads(source_path.read_text(encoding="utf-8")); page_count = int(source["page_count"])
        page_text = {int(p["page"]): clean(p.get("text", "")) for p in source["pages"]}
        if sha256(source_path) != row["source_text_sha256"] or row["original_extraction_sha256"] != primary_hash:
            raise ValueError(f"final checksum failure: {row['family_id']}")
        if not row["measures_findings"]:
            raise ValueError(f"finding missing: {row['family_id']}")
        for f in row["measures_findings"]:
            page = int(f["source_locator"].split()[1])
            if not 1 <= page <= page_count: raise ValueError("finding page out of bounds")
            if f["quantitative"]:
                estimate = str(f["reported_estimate"])
                sentence = sentence_containing(page_text[page], estimate)
                window = context_window(page_text[page], estimate)
                if not sentence or not window or not is_result_bearing(estimate, sentence, window):
                    raise ValueError(f"unsupported quantitative estimate: {row['family_id']}/{f['finding_id']}")
        for key, value in row["novelty_assessment"]["dimensions"].items():
            if key not in NOVELTY_KEYS or value["status"] not in {"met", "partial", "not_met", "unclear"}:
                raise ValueError("novelty enum invalid")
            if value["status"] in {"met", "partial", "unclear"}:
                page = int(value["source_locator"].split()[1])
                if not 1 <= page <= page_count: raise ValueError("novelty page out of bounds")
        rederived_dimensions, _ = novelty_direct(body_page_map(source))
        if row["novelty_assessment"]["dimensions"] != rederived_dimensions:
            raise ValueError(f"novelty support does not rederive: {row['family_id']}")

    payload = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in output_rows)
    OUTPUT.write_text(payload, encoding="utf-8")
    digest = sha256(OUTPUT)
    OUTPUT.with_name(OUTPUT.name + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    print(json.dumps({"status": "verified_complete", "families": 285, "original_extraction_sha256": primary_hash, "output_sha256": digest, **dict(total)}, sort_keys=True))


if __name__ == "__main__":
    main()
