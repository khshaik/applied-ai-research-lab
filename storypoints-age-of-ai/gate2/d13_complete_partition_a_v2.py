"""Independent D13 completeness remediation for verified partition A.

Reads only the verified baseline and checksum-bound static text. It does not
inspect the original extractor implementation, open PDFs, or access networks.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "gate2/output/systematic/v1.3/20260816"
BASELINE = BASE / "d13/verified_part_a.jsonl"
PRIMARY = BASE / "d13/primary/evidence_extractions.jsonl"
PACKETS = BASE / "d11/screening"
OUTPUT = BASE / "d13/verified_part_a_v2.jsonl"
VERIFIER = "d13-completeness-verifier-v1"


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


def body_pages(source: dict) -> dict[int, str]:
    result = {}
    for item in source["pages"]:
        text = clean(item.get("text", ""))
        marker = re.search(r"(?i)(?:^|\s)(references|bibliography)\s*(?:\[?1\]?|$)", text)
        if marker:
            text = text[:marker.start()].strip()
        if text: result[int(item["page"])] = text
        if marker: break
    return result or {int(p["page"]): clean(p.get("text", "")) for p in source["pages"]}


def sentences(pages: dict[int, str]):
    for page, text in pages.items():
        for raw in re.split(r"(?<=[.!?])\s+|\n+", text):
            value = clean(raw)
            if 35 <= len(value) <= 1400:
                yield page, value


CATEGORIES = (
    ("human_effort_time_workload", r"cognitive|mental workload|human effort|manual effort|review effort|time spent|task time|completion time|productiv|efficien|developer experience|attention|oversight"),
    ("review_testing_security_quality", r"code review|pull request|test(?:ing| case| coverage)|quality|correctness|defect|bug|vulnerab|security|compliance|maintainab|reliab"),
    ("delivery_flow", r"delivery|cycle time|lead time|deployment|release|throughput|sprint|velocity|queue|waiting time|handoff|flow"),
    ("readiness_gates", r"readiness|quality gate|acceptance criteria|verification|validation|evidence gate|definition of done"),
    ("estimation_comparator", r"story point|effort estimat|forecast|planning accuracy|baseline|control group|human-only|without (?:AI|copilot)|comparison"),
    ("limitations", r"limitation|threats? to validity|generaliz|future work|small sample|selection bias|self-report|cannot conclude|does not establish"),
)

OWNED_RESULT = re.compile(
    r"(?i)\bwe (?:find|found|show|showed|observe|observed|report|reported|identify|identified|demonstrate|demonstrated|propose|present|introduce)\b|"
    r"\bour (?:results?|findings?|analysis|evaluation) (?:find|found|show|shows|showed|indicate|indicates|suggest|suggests|reveal|reveals|confirm|confirms|demonstrate|demonstrates)\b|"
    r"\bthis (?:study|paper|analysis|evaluation|experiment|survey) (?:finds?|found|shows?|showed|reveals?|revealed|identifies?|identified|demonstrates?|reports?|proposes?|presents?)\b"
)
SYNTHESIS_RESULT = re.compile(r"(?i)\b(?:our|this) (?:review|mapping study|systematic review|synthesis)\b.*\b(?:find|found|identify|identified|reveal|shows?|conclude|categor)")
PROPOSAL_RESULT = re.compile(r"(?i)\bwe (?:propose|present|introduce|develop|design)\b.*\b(?:framework|model|method|approach|tool|system|metric|taxonomy)")
BACKGROUND = re.compile(r"(?i)according to|previous (?:study|studies|research)|prior (?:study|studies|research)|industry report|market survey|has been reported|researchers found|et al\.|\[[0-9, -]+\]")
BIBLIO = re.compile(r"(?i)copyright|isbn|issn|doi:|arxiv:|proceedings|volume\s+\d|issue\s+\d|page no\.?|received \d|accepted \d|corresponding author|publisher|\bemail:")
PROCEDURAL = re.compile(r"(?i)remainder of (?:this|the) paper|paper is organi[sz]ed|following section|section \d.{0,100}(?:present|describe|report)|structure of (?:this|the) paper")
SAMPLE_STATEMENT = re.compile(r"(?i)\bwe (?:surveyed|interviewed|observed|analy[sz]ed|evaluated|recruited)\b.{0,180}\b\d{1,7}\s+(?:participants?|respondents?|developers?|programmers?|professionals?|students?|tasks?|projects?|repositories|pull requests?|teams?|studies|papers|interviews?)\b|\b(?:our|the) sample (?:consists?|comprised?|included|contains?)\b.{0,120}\b\d{1,7}\b|\bn\s*=\s*\d{1,7}\b")


def category(sentence: str) -> str | None:
    if re.search(dict(CATEGORIES)["limitations"], sentence, re.I):
        return "limitations"
    for name, pattern in CATEGORIES:
        if name == "limitations": continue
        if re.search(pattern, sentence, re.I): return name
    return None


def result_owned(sentence: str) -> bool:
    return bool(OWNED_RESULT.search(sentence) or SYNTHESIS_RESULT.search(sentence) or PROPOSAL_RESULT.search(sentence) or SAMPLE_STATEMENT.search(sentence)) and not bool(PROCEDURAL.search(sentence))


def numeric_measure(sentence: str, owned: bool) -> tuple[bool, str | None, str | None]:
    """Return only study-result/sample/work/effect numbers, never identifiers."""
    if not owned or BIBLIO.search(sentence): return False, None, None
    # Background figures remain qualitative context even if numerical.
    if BACKGROUND.search(sentence) and not re.search(r"(?i)\bour (?:results?|study|analysis|sample)\b|\bwe (?:find|found|evaluate|evaluated|measure|measured)\b", sentence):
        return False, None, None
    tokens = []
    for pattern in (
        r"\bn\s*=\s*\d{1,7}\b",
        r"(?<![\w.])[-+~≈]?(?:\d{1,3}(?:\.\d+)?\s*%|\d{1,3}(?:\.\d+)?\s+percent\b)",
        r"\bp\s*[<=>]\s*0?\.\d+\b",
        r"\b(?:95\s*%\s*)?(?:CI|confidence interval)\s*[:=]?\s*[^.;]{1,90}",
        r"\b\d+(?:\.\d+)?\s*(?:seconds?|minutes?|hours?|days?|weeks?|months?|sprints?)\b",
        r"\b\d{1,7}\s+(?:participants?|respondents?|developers?|programmers?|professionals?|students?|tasks?|projects?|repositories|pull requests?|code reviews?|teams?|studies|papers|interviews?)\b",
        r"\b(?:accuracy|precision|recall|F1|score|rate|coverage|effect size|odds ratio|mean|median)\s*(?:of|=|:)\s*-?\d+(?:\.\d+)?\b",
    ):
        tokens.extend(m.group(0).strip() for m in re.finditer(pattern, sentence, re.I))
    # Dataset partitioning and parameter weights are not findings.
    if re.search(r"(?i)(?:data ?set|corpus).{0,100}(?:split|training data|validation data|testing data)|(?:risk|factor|criterion|dimension).{0,80}\bweight\b", sentence):
        return False, None, None
    unique = list(dict.fromkeys(tokens))
    market_context = re.compile(r"(?i)labor[- ]market|jobs? sampled|market impact|workforce statistic")
    unique = [token for token in unique if not any(
        market_context.search(sentence[max(0, match.start()-100):min(len(sentence), match.end()+100)])
        for match in re.finditer(re.escape(token), sentence, re.I)
    )]
    if not unique: return False, None, None
    uncertainty = next((x for x in unique if re.search(r"(?i)confidence interval|\bCI\b", x)), None)
    estimates = [x for x in unique if x != uncertainty]
    return bool(estimates), "; ".join(estimates) if estimates else None, uncertainty if estimates else None


def direction(sentence: str) -> str:
    pos = re.search(r"(?i)improv|increase|higher|faster|better|outperform|gain|reduc(?:e|ed|tion) (?:time|effort|defect|error|risk)", sentence)
    neg = re.search(r"(?i)decrease|lower|slower|worse|degrad|more (?:defect|error|vulnerab)|risk increased", sentence)
    if pos and neg: return "mixed"
    if pos: return "positive"
    if neg: return "negative"
    if re.search(r"(?i)no significant|no difference|did not|null result", sentence): return "null"
    return "mixed"


def wordset(value: str) -> set[str]:
    return {x for x in re.findall(r"[a-z]{3,}", value.lower()) if x not in {"this", "that", "with", "from", "have", "were", "their", "study", "paper", "results"}}


def duplicate(a: str, b: str) -> bool:
    aa, bb = wordset(a), wordset(b)
    if not aa or not bb: return False
    overlap = len(aa & bb) / min(len(aa), len(bb))
    nums_a, nums_b = set(re.findall(r"\d+(?:\.\d+)?", a)), set(re.findall(r"\d+(?:\.\d+)?", b))
    return overlap >= .62 or (bool(nums_a) and nums_a == nums_b and overlap >= .40)


def baseline_supported(finding: dict, pages: dict[int, str]) -> bool:
    try: page = int(finding["source_locator"].split()[1])
    except Exception: return False
    text, value = pages.get(page, ""), clean(str(finding.get("value") or ""))
    if not value or value.lower() not in text.lower(): return False
    if BIBLIO.search(value): return False
    # Keep quantitative study results, owned findings/syntheses/proposals, and
    # explicit limitations. Drop generic background/speculation.
    principal_result = finding.get("field_name") == "principal_reported_finding" and bool(re.search(r"(?i)findings? (?:show|indicate|reveal|suggest|confirm)|results? (?:show|indicate|reveal|suggest)|analysis (?:shows|indicates|reveals|suggests)", value))
    return bool(finding.get("quantitative") or result_owned(value) or principal_result or category(value) == "limitations")


def candidates(pages: dict[int, str]) -> list[tuple[int, int, str, str]]:
    result = []
    for page, sentence in sentences(pages):
        cat = category(sentence)
        if not cat or BIBLIO.search(sentence) or PROCEDURAL.search(sentence): continue
        if re.search(r"(?i)labor[- ]market|jobs? sampled|market impact|workforce statistic", sentence): continue
        owned = result_owned(sentence)
        is_limitation = cat == "limitations" and bool(re.search(r"(?i)\bour (?:study|analysis|sample|findings|results)|\bthis study|\bwe (?:acknowledge|cannot|could not|did not|were unable|limit)|threats? to validity|study limitations", sentence))
        if not (owned or is_limitation): continue
        score = 10 + (3 if owned else 0) + (2 if page == 1 else 0)
        score += 2 if re.search(r"\d", sentence) else 0
        score += 2 if re.search(r"(?i)result|finding|conclu|demonstrat", sentence) else 0
        if BACKGROUND.search(sentence): score -= 4
        result.append((score, page, sentence, cat))
    return sorted(result, key=lambda x: (-x[0], x[1], x[2]))


def make_finding(sentence: str, page: int, cat: str, data_nature: str) -> dict:
    owned = result_owned(sentence)
    quant, estimate, uncertainty = numeric_measure(sentence, owned)
    unit = None
    if estimate:
        if "%" in estimate or "percent" in estimate.lower(): unit = "%"
        elif re.search(r"(?i)seconds?|minutes?|hours?|days?|weeks?|months?|sprints?", estimate): unit = "reported time"
        elif re.search(r"(?i)participants?|respondents?|developers?|tasks?|projects?|repositories|pull requests?|teams?|studies|papers|interviews?", estimate): unit = "reported sample/count"
    return {
        "finding_id": "", "field_name": cat, "value": sentence, "unit": unit,
        "data_nature": data_nature, "direction": direction(sentence),
        "source_locator": f"page {page}", "quantitative": quant,
        "reported_estimate": estimate, "reported_uncertainty": uncertainty,
        "limitations": "Completeness extraction retains the directly located study statement; interpretation remains bounded by the appraised design, evidence band, and any separately extracted limitation.",
    }


def process(row: dict, pages: dict[int, str], primary_hash: str, index: int) -> dict:
    baseline = row["measures_findings"]
    nature_value = row["context_method"].get("data_nature", "conceptual")
    if isinstance(nature_value, dict): nature_value = nature_value.get("value")
    data_nature = nature_value or "conceptual"
    retained = [json.loads(json.dumps(f)) for f in baseline if baseline_supported(f, pages)]
    for finding in retained:
        if not finding.get("quantitative"):
            finding["reported_estimate"] = None
            finding["reported_uncertainty"] = None
    used_categories = {category(f["value"]) for f in retained}
    additions = []
    pool = candidates(pages)
    # First maximize domain coverage, then fill remaining slots by evidence score.
    for prefer_new_category in (True, False):
        for _, page, sentence, cat in pool:
            if len(retained) + len(additions) >= 5: break
            if prefer_new_category and cat in used_categories: continue
            if cat == "limitations" and cat in used_categories: continue
            if any(duplicate(sentence, f["value"]) for f in retained + additions): continue
            additions.append(make_finding(sentence, page, cat, data_nature))
            used_categories.add(cat)
        if len(retained) + len(additions) >= 5: break
    final = (retained + additions)[:5]
    if not final:
        # Faithful fallback: exact first topic-relevant body sentence.
        for page, sentence in sentences(pages):
            cat = category(sentence)
            if cat and not BIBLIO.search(sentence) and not PROCEDURAL.search(sentence):
                final = [make_finding(sentence, page, cat, data_nature)]
                break
    if not final: raise ValueError(f"no faithful finding: {row['family_id']}")
    for n, finding in enumerate(final, 1): finding["finding_id"] = f"F{n}"
    old_quant = sum(bool(f["quantitative"]) for f in baseline)
    retained_baseline = len(retained)
    added = max(0, len(final) - retained_baseline)
    quant_added = sum(bool(f["quantitative"]) for f in final[retained_baseline:])
    row["measures_findings"] = final
    row["extractor_agent_id"] = row["extractor_agent_id"]  # preserve extraction provenance
    row["verifier_agent_id"] = VERIFIER
    row["verification_context_id"] = f"d13-complete-a-{index:04d}-{row['source_text_sha256'][:12]}"
    row["original_extraction_sha256"] = primary_hash
    row["verification_summary"] = {
        "quantitative_verified": sum(bool(f["quantitative"]) for f in final),
        "quantitative_corrected": quant_added,
        "quantitative_rejected": max(0, old_quant - sum(bool(f["quantitative"]) for f in retained)),
        "novelty_corrected": 0,
        "other_corrections": len(baseline) - retained_baseline,
    }
    row["completeness_review"] = {
        "baseline_finding_count": len(baseline),
        "retained_baseline_findings": retained_baseline,
        "new_findings_added": added,
        "quantitative_new_findings_added": quant_added,
    }
    row["reviewer_notes"] = (
        "Independent completeness review used only checksum-bound static body text. "
        "Findings are exact located report statements; quantitative coding is limited to owned study samples, "
        "work/time, effect, quality/performance, or uncertainty measures. Background statistics are not coded as outcomes."
    )
    return row


def validate(rows: list[dict], baseline: list[dict], packet_by_family: dict, primary_hash: str) -> None:
    if len(rows) != 285 or [r["family_id"] for r in rows] != [r["family_id"] for r in baseline]:
        raise ValueError("partition-A population/order changed")
    if len({r["verification_context_id"] for r in rows}) != 285: raise ValueError("verification contexts not unique")
    for row, old in zip(rows, baseline):
        if row["verifier_agent_id"] != VERIFIER or row["original_extraction_sha256"] != primary_hash:
            raise ValueError("verification provenance invalid")
        source_path = ROOT / packet_by_family[row["family_id"]]["extracted_text_path"]
        if sha256(source_path) != row["source_text_sha256"]: raise ValueError("source checksum mismatch")
        source = json.loads(source_path.read_text(encoding="utf-8")); page_count = int(source["page_count"])
        page_text = {int(p["page"]): clean(p.get("text", "")) for p in source["pages"]}
        if not 1 <= len(row["measures_findings"]) <= 5: raise ValueError("finding count invalid")
        for finding in row["measures_findings"]:
            page = int(finding["source_locator"].split()[1])
            if not 1 <= page <= page_count or clean(finding["value"]).lower() not in page_text[page].lower():
                raise ValueError(f"finding source support invalid: {row['family_id']}/{finding['finding_id']}")
            if finding["quantitative"]:
                if not finding["reported_estimate"]: raise ValueError("quantitative estimate missing")
                for token in re.findall(r"\d+(?:\.\d+)?", finding["reported_estimate"]):
                    if token not in page_text[page]: raise ValueError(f"numeric token unsupported: {row['family_id']}/{token}")
            elif finding.get("reported_estimate") is not None or finding.get("reported_uncertainty") is not None:
                raise ValueError("nonquantitative estimate/uncertainty retained")
        expected = row["completeness_review"]
        if expected["baseline_finding_count"] != len(old["measures_findings"]): raise ValueError("baseline count mismatch")
        if expected["retained_baseline_findings"] + expected["new_findings_added"] != len(row["measures_findings"]):
            raise ValueError("completeness count reconciliation failed")


def main() -> None:
    baseline = read_jsonl(BASELINE); primary_hash = sha256(PRIMARY)
    packet_by_family = {}
    for path in sorted(PACKETS.glob("fulltext_packet_*.jsonl")):
        for packet in read_jsonl(path): packet_by_family[packet["family_id"]] = packet
    rows = []
    for index, original in enumerate(baseline, 1):
        row = json.loads(json.dumps(original))
        source_path = ROOT / packet_by_family[row["family_id"]]["extracted_text_path"]
        if sha256(source_path) != row["source_text_sha256"]: raise ValueError(f"input source hash mismatch: {row['family_id']}")
        pages = body_pages(json.loads(source_path.read_text(encoding="utf-8")))
        rows.append(process(row, pages, primary_hash, index))
    validate(rows, baseline, packet_by_family, primary_hash)
    OUTPUT.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    digest = sha256(OUTPUT)
    OUTPUT.with_name(OUTPUT.name + ".sha256").write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    totals = Counter()
    for row in rows: totals.update(row["completeness_review"])
    prior_one_pattern = all(len(r["measures_findings"]) == 1 for r in baseline)
    materially_omitted = sum(r["completeness_review"]["new_findings_added"] for r in rows) > 0
    print(json.dumps({"status": "complete", "families": len(rows), "sha256": digest, "prior_exactly_one_pattern": prior_one_pattern, "materially_omitted_findings": materially_omitted, **dict(totals)}, sort_keys=True))


if __name__ == "__main__": main()
