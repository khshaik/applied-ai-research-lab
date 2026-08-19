"""Generate C08 bounded S1/S2 developmental query-control appraisals."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from gate2.query_appraisal import appraise, deterministic_sample_positions

ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "gate2/output/development/query_appraisals"
CASES = {
    "S1": {
        "source":"semantic_scholar", "version":"0.3", "query_id":"S2-S1I3",
        "registry":ROOT / "research/studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3.json",
        "export":ROOT / "gate2/output/development/semantic_scholar/S2-S1I3-20260816-full1",
        "relevant":{0,3,18,82,92,119,120,137,138,187,231,285,323,324,326,328},
        "uncertain":{7,261,288},
    },
    "S2": {
        "source":"openalex", "version":"0.2", "query_id":"OA-S2I2",
        "registry":ROOT / "research/studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.2.json",
        "export":ROOT / "gate2/output/development/openalex/OA-S2I2-20260816-full1",
        "relevant":{2,3,6,7,40,47,54,75,79,89,108,112,121,122,129,136,146,172,175,176,181,186,187,191,218,220,221,222,243,245,247,248,249,250,252,253,254,255},
        "uncertain":{0,1,4,5,113,177},
    },
}

def _reason(decision: str, title: str, family: str) -> str:
    value = title.casefold()
    if decision == "uncertain":
        return "Potentially within the bounded integrative construct, but exported metadata is insufficient for a substantive query-control judgment."
    if decision == "likely_relevant":
        if family == "S1":
            if "productiv" in value or "high-skilled work" in value:
                return "Substantively measures or synthesizes AI-associated developer productivity or work redistribution."
            if "review" in value:
                return "Substantively addresses human/AI code-review effort, behavior, quality, or oversight."
            if "effort" in value or "story point" in value:
                return "Substantively addresses AI-era software effort estimation or its comparator target."
            return "Substantively addresses human work, validation, or developer experience under AI assistance."
        if any(term in value for term in ("delivery", "devops", "ci/cd", "pipeline", "release")):
            return "Substantively addresses AI-assisted software-delivery flow, lifecycle automation, or assurance transitions."
        if any(term in value for term in ("verification", "validation", "gate", "compliance", "security", "requirement")):
            return "Substantively addresses lifecycle verification, validation, readiness, compliance, or evidence gates."
        return "Substantively addresses people/process effects across the AI-assisted software lifecycle."
    if any(term in value for term in ("education", "student", "programming education")):
        return "Education-focused record outside the professional bounded integrative scope."
    if any(term in value for term in ("benchmark", "generation", "tooling", "model", "compiler", "summarization")):
        return "Technical AI/tool performance without substantive human-work redistribution or lifecycle-readiness analysis."
    return "Metadata does not substantively bridge the prespecified human-effort or lifecycle-readiness constructs."

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def generate() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for family, case in CASES.items():
        registry = json.loads(case["registry"].read_text(encoding="utf-8"))
        with (case["export"] / "records.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        positions, seed = deterministic_sample_positions(len(rows), case["source"], family, case["version"])
        assert case["relevant"].isdisjoint(case["uncertain"])
        assert (case["relevant"] | case["uncertain"]).issubset(set(positions))
        decisions=[]
        for position in positions:
            decision=("likely_relevant" if position in case["relevant"] else "uncertain" if position in case["uncertain"] else "likely_irrelevant")
            decisions.append({"source_id":rows[position]["source_id"],"decision":decision,"reason":_reason(decision,rows[position]["title"],family)})
        artifact={"status":"development_query_control_decisions","interpretation_boundary":"Metadata-level query appraisal only; not screening, eligibility, or PRISMA evidence.","source":case["source"],"query_id":case["query_id"],"family_id":family,"query_version":case["version"],"sampling_seed_sha256":seed,"sample_positions_zero_based":positions,"ordered_sample_source_ids":[rows[p]["source_id"] for p in positions],"decisions":decisions}
        result=appraise(case["export"],registry,decisions)
        for suffix,payload in (("decisions",artifact),("appraisal",result)):
            path=OUTPUT / f"{case['query_id']}-20260816-query-{suffix}-v1.json"
            path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
            digest=_sha(path)
            path.with_suffix(".json.sha256").write_text(f"{digest}  {path.name}\n",encoding="utf-8")
            (OUTPUT / f"{case['query_id']}-20260816-query-{suffix}-v1.sha256").write_text(f"{digest}  {path.name}\n",encoding="utf-8")

if __name__ == "__main__": generate()
