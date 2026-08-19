"""Generate exact C07/S8 v0.6 developmental appraisals."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from gate2.query_appraisal import appraise, deterministic_sample_positions

ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "research/studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6.json"
OUTPUT = ROOT / "gate2/output/development/query_appraisals"
CASES = {
    "openalex": ("OA-S8R6", ROOT / "gate2/output/development/openalex/OA-S8R6-20260816-full1"),
    "semantic_scholar": ("S2-S8R6", ROOT / "gate2/output/development/semantic_scholar/S2-S8R6-20260816-full1"),
}

# Manual metadata-level adjudication under the strict S8 rule.  Every sample
# position not listed as relevant or uncertain is explicitly ineligible for
# query-control relevance; the generator proves exhaustive position coverage.
RELEVANT = {
    "openalex": {0,4,98,132,177,231,322,389,404,433,452,484,521,543,544,545,
                  548,550,551,565,612,619,625,650,665,678,769,891,905,938,943,
                  980,981,1059,1069,1088,1093,1094,1095},
    "semantic_scholar": {6,8,9,10,92,213,233,300,392,518,590,600,735,784,785,
                          788,789,793},
}
UNCERTAIN = {
    "openalex": {267,275,316,407,725,1011,1083,1092,1096},
    "semantic_scholar": {3,4,203},
}


def _reason(decision: str, title: str) -> str:
    value = title.casefold()
    if decision == "uncertain":
        return "Title is plausibly connected to a prespecified S8 construct, but exported metadata is insufficient for a substantive query-control judgment."
    if decision == "likely_relevant":
        if "story point" in value or "effort estim" in value or "functional size" in value or "planning poker" in value:
            return "Substantively addresses software effort estimation, relative sizing, estimate validity, or a conventional comparator."
        if "productiv" in value or "work life" in value or "breaks and code quality" in value:
            return "Substantively measures, defines, or analyzes developer productivity, interruptions, work patterns, or productivity-quality trade-offs."
        if "code review" in value or "reviewer" in value or "review comments" in value:
            return "Substantively analyzes human modern-code-review effort, communication, outcomes, practices, or knowledge transfer."
        if "kanban" in value or "dora" in value or "delivery" in value or "agile" in value or "scrum" in value:
            return "Substantively addresses software-team flow, delivery performance, agile process, dependency, or capacity interpretation."
        return "Substantively addresses a prespecified foundational software-work measurement or process comparator."
    if any(term in value for term in ("llm", "copilot", "agentic", "ai-driven", "artificial intelligence", "genai")):
        return "GenAI-specific technical or impact evidence belongs to another evidence family and is not an S8 foundational comparator record."
    if any(term in value for term in ("machine learning", "neural", "prediction", "recommendation", "automating", "automatic")):
        return "Technical automation or prediction record without substantive human-work, measurement-validity, or delivery-flow analysis."
    if any(term in value for term in ("student", "teaching", "course", "tutor", "education")):
        return "Education-focused record outside the foundational professional software-work comparison scope."
    if any(term in value for term in ("gpu", "mpi", "processor", "compiler", "performance tuning", "dataflow", "database", "numerical", "radar")):
        return "System or computational-performance work without a substantive developer-work, estimation, review, or delivery-flow construct."
    return "Metadata does not substantively address estimation validity, developer-productivity measurement, human review work, workload measurement, or software-delivery flow."


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for source, (query_id, export) in CASES.items():
        with (export / "records.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        positions, seed = deterministic_sample_positions(len(rows), source, "S8", "0.6")
        if not RELEVANT[source].isdisjoint(UNCERTAIN[source]):
            raise RuntimeError(f"{source} relevant and uncertain positions overlap")
        if not (RELEVANT[source] | UNCERTAIN[source]).issubset(set(positions)):
            raise RuntimeError(f"{source} judgment position is outside deterministic sample")
        decisions = []
        for position in positions:
            decision = ("likely_relevant" if position in RELEVANT[source] else
                        "uncertain" if position in UNCERTAIN[source] else "likely_irrelevant")
            decisions.append({"source_id": rows[position]["source_id"], "decision": decision,
                              "reason": _reason(decision, rows[position]["title"])})
        artifact = {
            "status":"development_query_control_decisions",
            "interpretation_boundary":"Metadata-level deterministic query appraisal only; not systematic screening, eligibility, or PRISMA evidence.",
            "source":source,"query_id":query_id,"family_id":"S8","query_version":"0.6",
            "sampling_seed_sha256":seed,"sample_positions_zero_based":positions,
            "ordered_sample_source_ids":[rows[position]["source_id"] for position in positions],
            "strict_rule":"Likely relevant only when metadata substantively addresses software estimation validity, developer-productivity measurement, human code-review work, workload measurement boundaries, or software delivery flow foundations; generic tool/system performance and technical automation alone are insufficient.",
            "decisions":decisions,
        }
        result = appraise(export, registry, decisions)
        for suffix, payload in (("decisions", artifact), ("appraisal", result)):
            path = OUTPUT / f"{query_id}-20260816-query-{suffix}-v1.json"
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            path.with_suffix(".json.sha256").write_text(f"{_sha(path)}  {path.name}\n", encoding="utf-8")


if __name__ == "__main__":
    generate()
