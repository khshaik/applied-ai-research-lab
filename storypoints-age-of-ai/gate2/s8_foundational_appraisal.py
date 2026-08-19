"""Generate the deterministic C07/S8 developmental query appraisals.

The decisions below are metadata-level query-control judgments, not systematic
screening or eligibility decisions.  They are deliberately source-position
bound so a changed export, ordering, or sample cannot silently reuse them.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from gate2.query_appraisal import appraise, deterministic_sample_positions


ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.4.json"
OUTPUT = ROOT / "gate2/output/development/query_appraisals"
CASES = {
    "openalex": (
        "OA-S8R4",
        ROOT / "gate2/output/development/openalex/OA-S8R4-20260816-full1",
    ),
    "semantic_scholar": (
        "S2-S8R4",
        ROOT / "gate2/output/development/semantic_scholar/S2-S8R4-20260816-full1",
    ),
}

# Every deterministic sample position has an explicit metadata-level judgment.
# Relevance requires substantive coverage of estimation validity, developer-
# productivity measurement, human review work, workload measurement, or
# software delivery flow.  Generic tool performance and technical automation
# without a human/measurement/flow construct are excluded at query-control time.
DECISIONS = {
    "openalex": {
        0:("likely_relevant","Directly proposes software-developer productivity and performance metrics across delivery stages."),
        1:("likely_irrelevant","Generic AI-impact overview; metadata does not establish a foundational measurement, review-work, estimation-validity, or flow contribution."),
        2:("likely_irrelevant","Duplicate-version generic AI-impact overview outside the strict S8 foundational comparator boundary."),
        3:("likely_irrelevant","Automated story-point prediction benchmark; does not analyze relative-estimate validity or human planning work."),
        4:("likely_relevant","Practitioner study of infrastructure-complexity pain points and developer-productivity consequences."),
        5:("likely_irrelevant","Training-program material, not a scholarly validity or measurement study."),
        6:("likely_irrelevant","Duplicate training-program record without a foundational empirical construct contribution."),
        7:("likely_irrelevant","Autonomous API framework; productivity is motivational rather than measured or analyzed."),
        8:("likely_irrelevant","Duplicate autonomous API framework with only motivational productivity language."),
        9:("likely_irrelevant","LLM-code reliability study belongs to GenAI quality evidence, not the S8 foundational comparison stratum."),
        72:("likely_relevant","Enterprise platform-engineering framework substantively addresses software-delivery complexity and developer flow."),
        78:("likely_irrelevant","AI terminal-tool implementation without foundational workload, estimation, review, or flow measurement."),
        79:("likely_irrelevant","Refactoring-tool implementation; no substantive human-work or productivity-measurement analysis in metadata."),
        162:("likely_relevant","Explicit measurement framework for AI-tool effects on developer productivity and therefore a comparator-metrics record."),
        176:("likely_irrelevant","Generic AI/cloud web-development discussion with no strict S8 construct or measurement contribution."),
        186:("uncertain","Socio-technical serverless-adoption title is plausibly relevant to developer work, but the exported record lacks an abstract."),
        209:("likely_irrelevant","AI-generated-code accuracy study is GenAI primary evidence rather than foundational S8 comparison evidence."),
        212:("likely_irrelevant","Code-comment generator implementation; no human effort or productivity construct is analyzed."),
        301:("likely_irrelevant","API-management technical overview uses productivity language without a strict foundational comparison construct."),
        311:("likely_relevant","Taxonomy of human code-review feedback informs the activity and evidence content of modern review."),
        359:("likely_irrelevant","AI platform-engineering proposal is lifecycle/GenAI evidence, not a foundational comparator study."),
        367:("likely_irrelevant","Android security-policy workflow optimization lacks a general estimation, workload, review-cognition, or productivity measure."),
        389:("likely_relevant","Modern-code-review roadmap explicitly treats manual review as cognitively demanding and resource intensive."),
        402:("likely_relevant","Replication evaluates reliability and accuracy of agile story-point estimation methods."),
        407:("likely_relevant","Empirical analysis of useful code-review comments captures human communication in modern review."),
        438:("likely_relevant","Directly examines Fibonacci/planning-poker estimation practice and claimed accuracy."),
        442:("likely_irrelevant","Copilot review is GenAI evidence and does not serve as a foundational S8 comparator record."),
        461:("likely_relevant","Registered study links interruptions, forgetting, and code quality in software-development work."),
        506:("likely_irrelevant","Quantum-computing language/tool paper invokes productivity only as a design motivation."),
        511:("likely_irrelevant","Automated story-point classification does not test human-estimate validity or work burden."),
        567:("likely_irrelevant","Generic microservices/DevOps architecture discussion without a measurement or queue/flow analysis."),
        627:("likely_relevant","Models merged versus abandoned review changes and explicitly recognizes review effort and iterations."),
        642:("likely_relevant","Empirical code-smell work links software comprehension and developer productivity to change prediction."),
        651:("likely_relevant","Studies interaction between pull-request review and CI, directly informing review and delivery-flow coupling."),
        674:("likely_relevant","Proposes Story Point factors to reduce subjectivity and experience dependence, directly bearing on estimate validity."),
        731:("likely_irrelevant","Numerical-solver performance study is unrelated to developer productivity or delivery flow."),
        750:("likely_irrelevant","Programming-language design cites productivity as motivation but does not measure developer work."),
        759:("likely_irrelevant","HPC performance tuning concerns computational performance, not developer workload or delivery flow."),
        830:("likely_irrelevant","MPI library chapter has no metadata-level connection to the strict S8 constructs."),
        853:("likely_relevant","Foundational software-effort prediction model provides a conventional estimation comparator."),
        855:("likely_irrelevant","Embedded-component reuse paper does not substantively address the S8 constructs in metadata."),
        856:("likely_relevant","Empirically compares client/vendor perceptions of software-development productivity factors."),
        857:("likely_irrelevant","Radar-processor implementation is outside software-work measurement and estimation validity."),
        858:("likely_irrelevant","Embedded-system processor testing is technical system testing, not human workload or delivery planning."),
        859:("likely_irrelevant","Build-tool proposal lacks an empirical productivity, workload, review, or flow measure."),
        860:("uncertain","Project-management book may contain delivery comparison evidence, but exported metadata is insufficient to judge."),
        861:("likely_relevant","Systems-development acceptance model explicitly concerns low developer productivity and software quality."),
        862:("likely_relevant","Field study measures how reusable frameworks affect developer productivity and estimation."),
        863:("likely_relevant","Critiques methods used to measure CASE-tool productivity and reports inconclusive gains."),
        864:("uncertain","CASE implementation study is plausibly relevant to productivity adoption, but the exported metadata lacks substantive details."),
    },
    "semantic_scholar": {
        0:("likely_irrelevant","Dataflow-compilation architecture is outside the strict S8 human-work and estimation boundary."),
        1:("likely_irrelevant","Code-LLM Trojan study is GenAI security evidence, not foundational comparison evidence."),
        2:("likely_irrelevant","Software-product-line transformation paper does not address S8 constructs in metadata."),
        3:("uncertain","Software-process innovation adoption may bear on productivity, but no abstract is available for a substantive judgment."),
        4:("likely_irrelevant","Processor architecture record has no metadata-level S8 construct contribution."),
        5:("likely_relevant","Empirically characterizes differing developer perceptions of productivity."),
        6:("likely_relevant","Evaluates self-monitoring and goal-setting interventions for software-developer productivity."),
        7:("likely_relevant","Directly compares effort-estimate accuracy from function points and Story Points."),
        8:("likely_irrelevant","Embedded-component reuse is outside the strict S8 boundary in the available metadata."),
        9:("likely_relevant","Empirically studies programming-language fragmentation and developer productivity."),
        25:("likely_irrelevant","LLM-tool benchmark is GenAI primary evidence, not foundational comparator evidence."),
        112:("likely_irrelevant","Automated story-point reasoning model does not test human estimate validity or burden."),
        123:("likely_irrelevant","Object-relational transformation component method is unrelated to the S8 constructs."),
        127:("likely_irrelevant","Memory-attribution tooling does not analyze developer workload, productivity measurement, or estimation."),
        174:("likely_relevant","Measures code-transfer succession and developer productivity in software projects."),
        178:("likely_irrelevant","Syntax-highlighting method invokes productivity but does not measure developer work."),
        207:("likely_irrelevant","AI code-review assistant belongs to GenAI review evidence rather than foundational S8 evidence."),
        249:("likely_irrelevant","GPU-library implementation is outside software-work measurement and planning."),
        250:("likely_relevant","Compares developer and manager perceptions of function points and source lines as productivity measures."),
        257:("likely_irrelevant","GenAI productivity meta-analysis belongs to the primary/secondary GenAI evidence strata, not S8."),
        261:("likely_irrelevant","HPC performance-portability repository concerns application performance rather than developer productivity."),
        324:("likely_relevant","Implements a GitLab-based dashboard explicitly intended to measure team developer productivity."),
        332:("likely_irrelevant","Large-scale LLM code-generation method is GenAI technical evidence, not S8."),
        348:("likely_irrelevant","Source-code search infrastructure does not substantively analyze the S8 constructs."),
        391:("likely_relevant","Empirically examines gender differences in software-developer productivity across countries."),
        393:("likely_relevant","Studies how human modern code review affects software-design degradation."),
        399:("likely_irrelevant","Automatic review ordering is technical automation without a substantive human-work measure in metadata."),
        422:("likely_irrelevant","Software-engineering education study is outside the main foundational software-work scope."),
        444:("likely_irrelevant","Database optimization research is unrelated to S8 constructs."),
        474:("likely_irrelevant","Sensor-network development environment is a technical tool paper without S8 measurement evidence."),
        482:("likely_irrelevant","Graph-query performance prediction concerns system performance, not developer productivity."),
        492:("likely_irrelevant","Micro-frontend architecture paper lacks a human productivity, estimation, review, or flow measure."),
        508:("likely_irrelevant","Copilot evidence review belongs to the GenAI evidence strata, not the foundational comparator stratum."),
        519:("likely_irrelevant","Parallel-computing model is outside developer-work measurement."),
        536:("likely_irrelevant","Instruction-set simulator generation is technical performance work, not S8."),
        545:("likely_irrelevant","GPU solver porting evaluates computational performance rather than developer work."),
        567:("likely_irrelevant","Reverse-engineering Copilot endpoint is a tool implementation without an S8 construct analysis."),
        577:("likely_relevant","Empirically identifies which problems human modern code reviews fix."),
        594:("likely_irrelevant","Agentic formal verification is GenAI technical evidence and outside foundational S8."),
        607:("likely_relevant","Canonical NASA-TLX retrospective multidimensional workload reference."),
        608:("likely_irrelevant","Android security-policy workflow paper lacks a general workload or productivity measure."),
        609:("likely_irrelevant","Generic programming-model record provides no metadata-level S8 contribution."),
        610:("likely_irrelevant","Arabic code-summarization evaluation is GenAI technical evidence, not S8."),
        611:("likely_irrelevant","OpenACC compiler-extension experience is outside S8 constructs."),
        612:("likely_relevant","Empirically examines how developers and managers define and trade productivity against quality."),
        613:("likely_relevant","Extends planning poker for effort estimation and explicitly considers developer productivity."),
        614:("likely_irrelevant","DSL acceleration evaluates application performance; productivity is only motivational."),
        615:("likely_irrelevant","Automated story-point prediction does not examine human estimate validity or burden."),
        616:("likely_irrelevant","Enterprise AI-productivity evaluation belongs to GenAI evidence rather than foundational S8."),
        617:("likely_relevant","Proposes a comprehensive measurement approach for software-developer productivity and teamwork."),
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for source, (query_id, export) in CASES.items():
        with (export / "records.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        positions, seed = deterministic_sample_positions(len(rows), source, "S8", "0.4")
        if set(positions) != set(DECISIONS[source]) or len(positions) != len(DECISIONS[source]):
            raise RuntimeError(f"{source} decision positions do not match deterministic sample")
        ordered_ids = [rows[position]["source_id"] for position in positions]
        decisions = [
            {"source_id": rows[position]["source_id"], "decision": DECISIONS[source][position][0],
             "reason": DECISIONS[source][position][1]}
            for position in positions
        ]
        artifact = {
            "status": "development_query_control_decisions",
            "interpretation_boundary": "Metadata-level deterministic query appraisal only; not systematic screening, eligibility, or PRISMA evidence.",
            "source": source,
            "query_id": query_id,
            "family_id": "S8",
            "query_version": "0.4",
            "sampling_seed_sha256": seed,
            "sample_positions_zero_based": positions,
            "ordered_sample_source_ids": ordered_ids,
            "strict_rule": "Likely relevant only when metadata substantively addresses software estimation validity, developer-productivity measurement, human code-review work, workload measurement boundaries, or software delivery flow/queue foundations; generic tool/system performance and technical automation alone are insufficient.",
            "decisions": decisions,
        }
        result = appraise(export, registry, decisions)
        stem = f"{query_id}-20260816-query"
        decision_path = OUTPUT / f"{stem}-decisions-v1.json"
        result_path = OUTPUT / f"{stem}-appraisal-v1.json"
        for path, payload in ((decision_path, artifact), (result_path, result)):
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            path.with_suffix(".json.sha256").write_text(f"{_sha(path)}  {path.name}\n", encoding="utf-8")


if __name__ == "__main__":
    generate()
