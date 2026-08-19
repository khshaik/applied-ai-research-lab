# Gate 2 Systematic Mapping Review Protocol

**Protocol version:** 1.3  
**Reconciliation date:** 16 August 2026  
**Working project:** Role-constrained verified delivery capacity in AI-assisted software development  
**Status:** `prefreeze_reconciled_awaiting_D03_approval`. Minimum-route amendment 0.1 is approved; all 18 developmental source-family controls are reconciled; D03 freeze approval remains pending. Searches executed before freeze are developmental/scoping searches only.

## 1. Gate 2 decision

This protocol defines how the literature will be identified, screened, appraised, extracted, and synthesized to position and constrain VDCM/RSDRI. It is informed by the [Kitchenham and Charters software-engineering review guidance](https://homepages.dcc.ufmg.br/~figueiredo/disciplinas/papers/guidelines-kitchenham.pdf), [PRISMA 2020](https://www.prisma-statement.org/prisma-2020), and the [PRISMA-P protocol checklist](https://www.prisma-statement.org/protocols).

The proposed review is a **targeted, access-constrained, AI-assisted open evidence map, with a separate multivocal evidence stream**, not a meta-analysis or exhaustive systematic review. The evidence is too heterogeneous in interventions, tasks, tools, outcomes, and units of analysis to justify pooling effect sizes at protocol stage. The open-index route was approved on 15 August 2026 because institutional authentication for the six subscription sources listed in Section 7.2 is unavailable. Minimum-route amendment 0.1 was approved on 16 August 2026. Neither approval freezes the protocol nor converts a developmental result into a systematic-corpus result.

## 2. Material novelty finding from pilot searches

Gate 1's broad novelty position must be narrowed. Three close research clusters are already present.

### 2.1 LLM-aware effort estimation

Alaswad et al. introduced **Hybrid Intelligence Effort (HIE)** and compared Story Points with interaction- and oversight-derived indicators in a controlled study involving 22 developers, 110 tasks, and three LLMs. The study finds that Story Points retain partial explanatory value but omit important interaction and oversight factors. It expressly excludes downstream testing automation, CI, regression pipelines, release management, and longitudinal feature evolution: [Hybrid intelligence effort for software effort estimation in LLM assisted development](https://link.springer.com/article/10.1007/s10791-026-10331-6).

The same research line has a conceptual paper that identifies LLM reasoning complexity, context completeness, code-transformation impact, iterative reasoning cycles, and human oversight effort as core dimensions: [Toward LLM-aware software effort estimation](https://doi.org/10.3389/frai.2026.1772418).

### 2.2 Lifecycle verification and readiness frameworks

Agile V combines requirements, design, implementation, testing, compliance, and human approval gates, although its feasibility evidence is based on a small author-run case: [Agile V](https://arxiv.org/abs/2602.20684). Other 2026 work proposes agentic review workflows and production-verification harnesses.

### 2.3 Team-level delivery orchestration

A retrospective study of three modernization programs reports delivery across analysis, planning, implementation, and validation, but mixes observed outcomes with modeled staffing/effort scenarios: [Orchestrating Human-AI Software Delivery](https://arxiv.org/abs/2603.20028).

### 2.4 Required repositioning

The paper must not claim to be:

- the first to argue that Story Points are incomplete under LLM assistance;
- the first to model prompt/refinement/validation effort;
- the first AI-augmented Agile framework with human gates; or
- the first lifecycle-oriented human–AI delivery model.

The potentially defensible contribution is a design-science resource-and-flow
framework that forecasts pre-commitment role-stage human touch demand, separates
touch from queue delay, and couples evidence readiness, role capacity,
dependencies, and gate transitions to verified-completion forecasts. The current
paper supports this specification with a targeted open evidence map and
developmental simulation scenarios. Human and organizational validation remains
future Route A work. This is a contribution boundary to test through the frozen
review, not a final novelty claim.

## 3. Review objectives

1. Map how human effort, attention, cognitive workload, oversight, verification, and coordination are conceptualized in AI-assisted software work.
2. Identify instruments and observable indicators used to measure those constructs.
3. Compare traditional Agile estimation, LLM-aware effort models, developer-productivity frameworks, lifecycle metrics, and readiness/gating frameworks.
4. Determine which lifecycle stages, roles, outcomes, and organizational contexts are underrepresented.
5. Identify studies that directly duplicate or materially constrain the VDCM/RSDRI contribution.
6. Produce a verified evidence base for Gate 3 construct selection and operational anchors.

## 4. Literature-review questions

**LRQ1 — Work redistribution.** What empirical evidence shows how generative-AI assistance redistributes human work across requirements, design, context construction, implementation, review, security, testing, release, operations, and UAT?

**LRQ2 — Constructs and measures.** How are human effort, attention, mental workload, oversight, verification, rework, coordination, and readiness defined and measured?

**LRQ3 — Estimation and planning.** Which estimation or forecasting approaches have been proposed or evaluated for AI-assisted software development, and what outcomes do they explain or predict relative to Story Points, hours, functional size, or other baselines?

**LRQ4 — Delivery and quality.** Which flow, productivity, quality, risk, and acceptance outcomes are measured, and what factors moderate those outcomes?

**LRQ5 — Gates and controls.** Which readiness, human-approval, verification, security, test, release, or acceptance gates are proposed, and what evidence supports their effectiveness and implementation cost?

**LRQ6 — Novelty boundary.** Which publications overlap VDCM/RSDRI in unit of analysis, lifecycle coverage, constructs, intended users, prediction target, and empirical design, and what contribution—if any—remains unaddressed?

## 5. Review design and evidence streams

### 5.1 Stream A: scholarly evidence

Purpose: support scientific claims, theory, method selection, construct definition, and novelty.

Eligible forms:

- peer-reviewed journal articles;
- peer-reviewed conference papers and book chapters;
- registered reports;
- systematic/scoping/mapping reviews;
- preprints with a transparent empirical or review method, retained as a separately labelled status because 2025–2026 evidence is moving faster than publication cycles.

### 5.2 Stream B: practitioner and organizational evidence

Purpose: identify current terminology, operational metrics, implementation practices, and industry-reported problems that may not yet be represented in scholarly literature.

Eligible forms:

- official research reports with a stated method;
- technical reports and independently inspectable organizational case studies;
- standards and official measurement frameworks;
- practitioner articles only when they add a distinct operational construct or traceable observation.

Practitioner evidence will not be combined with peer-reviewed evidence as if it has equal evidentiary weight.

### 5.3 Method/reference set

Review-reporting guidance, measurement instruments, standards, and foundational pre-2019 theories are stored separately. They support the protocol or construct interpretation but are not counted as GenAI primary studies.

### 5.4 Mutually exclusive evidence destinations

Each retained report receives exactly one reporting destination before synthesis:

| Destination | Definition | Synthesis treatment |
|---|---|---|
| Scholarly primary—peer reviewed | Empirical or conceptual primary report with verified peer-review status | Main scholarly map; status shown explicitly |
| Scholarly primary—preprint | Primary report not yet verified as peer reviewed | Separate preprint stratum; never counted again if consolidated with a peer-reviewed version |
| Scholarly secondary | Review, mapping, or evidence-synthesis report | Secondary-study stratum and citation-chasing seed |
| Practitioner/grey | Eligible Stream B report | Separate multivocal synthesis and AACODS-inspired appraisal |
| Method/reference | Guidance, instrument, standard, or foundational theory used only for method/interpretation | Not counted as a GenAI primary study |

Study-family consolidation links versions without erasing report provenance. Counts must identify whether they refer to reports or consolidated study families.

## 6. Scope

### 6.1 Population and context

Professional or realistically simulated software-engineering work performed by individuals, teams, or organizations using generative-AI/LLM coding assistants or agents.

Education studies are excluded from the main synthesis unless they directly validate a transferable cognitive-workload or human–AI interaction measure. Such studies may be retained as indirect evidence and labelled accordingly.

### 6.2 Phenomena of interest

- AI-related work redistribution;
- prompt/context construction and refinement;
- human oversight, validation, comprehension, and review;
- cognitive load, mental workload, attention, and context switching;
- effort estimation, Story Points, sprint planning, capacity, and forecasting;
- requirements, architecture, integration, security, QA, UAT, release, and operational readiness;
- rework, technical debt, defects, stability, flow, and delivery outcomes;
- human-approval and readiness gates.

### 6.3 Time boundaries

- **Primary GenAI search:** 1 January 2019 through the final search date.
- **Pre-2019 foundational search:** no lower date limit, but only for Story Points/Agile estimation, cognitive-load measurement, code-review cognition, software-delivery metrics, and research methods identified through targeted searches or snowballing.
- **Mandatory refresh:** within seven days before manuscript submission because the 2026 literature is changing rapidly.

### 6.4 Language

English full text. Non-English records with an English abstract are logged but excluded unless a reliable, documented full-text translation is available to the review team.

## 7. Information sources

### 7.1 Executable open scholarly source set

Every declared source-family pair in the approved matrix below will be translated,
syntax-validated, completely exported, and archived separately. Sources omitted
from a family are deliberately out of scope, not unreported search failures.

| Family | Mandatory discovery sources |
|---|---|
| S1 | Semantic Scholar Academic Graph |
| S2 | OpenAlex |
| S3 | OpenAlex; Semantic Scholar Academic Graph |
| S4/S5R | OpenAlex; Semantic Scholar Academic Graph; arXiv |
| S5T | OpenAlex; arXiv |
| S5S | OpenAlex; arXiv |
| S6 | OpenAlex; arXiv |
| S7 | OpenAlex; Semantic Scholar Academic Graph; arXiv |
| S8 | OpenAlex; Semantic Scholar Academic Graph |

OpenAlex, Semantic Scholar, and arXiv are complementary, not interchangeable.
Crossref is used only for DOI and bibliographic verification of candidate or
included records; it is not a broad discovery source and non-retrieval cannot
support an absence claim. arXiv status does not establish peer review, and
retrieval from an open index does not establish that every publisher record is
represented. Google Scholar may be used only as a logged supplementary
discovery and lawful-version-locating method because ranked results and exposed
counts are not sufficiently stable to serve as the sole systematic source.

### 7.2 Access-constrained subscription sources

The following sources were assessed as unavailable on **15 August 2026** because the project has no institutional authentication/authorization and cannot supply it:

| Source | Access status | Recorded reason | Protocol treatment |
|---|---|---|---|
| Scopus | `blocked_authentication` | No authorized institutional session is available | Not searched; report as a coverage limitation |
| Web of Science Core Collection | `blocked_authentication` | No authorized institutional session is available | Not searched; report as a coverage limitation |
| IEEE Xplore | `blocked_authentication` | Required authenticated/export access is unavailable | Not searched as a database; individual lawful records may be verified separately |
| ACM Digital Library | `blocked_authentication` | Required authenticated/export access is unavailable | Not searched as a database; individual lawful records may be verified separately |
| SpringerLink | `blocked_authentication` | Required authenticated/export access is unavailable | Not searched systematically; individual lawful records may be verified separately |
| ScienceDirect | `blocked_authentication` | Required authenticated/export access is unavailable | Not searched systematically; individual lawful records may be verified separately |

The open sources are a **non-equivalent supplement**, not a coverage-equivalent replacement for these platforms. No result from OpenAlex, Semantic Scholar, Crossref, arXiv, Google Scholar, a publisher page, or general web search may be relabelled as a search of an inaccessible source. If access later becomes available, adding a source requires a logged protocol deviation and prospective query validation before its records enter the corpus.

Accordingly, the final coverage description must remain `access_constrained`. The review must not claim comprehensive database coverage, exhaustive retrieval, or that all relevant literature was searched.

### 7.3 Grey/practitioner sources

- DORA/Google Cloud research publications and published survey questions;
- NASA workload-measurement resources;
- official developer-platform research from GitHub, Microsoft Research, Google Research, GitLab, and comparable organizations;
- Sahaj and other practitioner sources that contain identifiable methods, cases, or operational proposals;
- standards bodies or official framework owners where relevant.

### 7.4 Citation chasing and lawful version discovery

- backward-reference searching from every included secondary review and every included or high-overlap seed study;
- forward-citation searching through OpenAlex and Semantic Scholar for HIE, LLM-aware estimation, SPACE, Copilot productivity experiments, cognitive-load/code-review research, lifecycle orchestration studies, and every newly included study;
- DOI and bibliographic reconciliation through Crossref;
- author/title searching for updated peer-reviewed, accepted-manuscript, or repository versions of included preprints and otherwise inaccessible reports.

Each citation-chasing round must record the seed study-family IDs, direction, source, date, records inspected, records newly identified, and deduplication outcome. Continue through at least one complete backward and forward round for all included studies; stop when a complete round adds no new eligible study family, or apply and report a prospectively approved resource cap. Records identified by citation chasing enter the same screening, appraisal, study-family, and author-confirmation workflow as database records.

Full text may be obtained only from a lawful open publisher page, repository, author manuscript, preprint server, or access legitimately held by an accountable author. The review will not bypass authentication, paywalls, technical controls, or licence restrictions. If no lawful English full text can be obtained, record `retrieval_unavailable`, the routes attempted, and the date, then exclude under I5 rather than infer content from an abstract or AI summary.

## 8. Search concepts

### 8.1 Concept blocks

**A — AI assistance**

```text
("generative AI" OR GenAI OR "large language model*" OR LLM* OR
 "AI coding assistant*" OR "AI programming assistant*" OR
 "AI-assisted coding" OR "AI-assisted software" OR
 "AI-augmented software" OR "agentic coding" OR "coding agent*" OR
 "GitHub Copilot" OR Cursor OR CodeWhisperer OR "Claude Code")
```

**B — Software-work context**

```text
("software engineering" OR "software development" OR "software delivery" OR
 SDLC OR programmer* OR developer* OR "agile team*" OR Scrum OR DevOps)
```

**C — Human work and estimation**

```text
(effort OR estimat* OR forecast* OR "story point*" OR capacity OR
 "human attention" OR "cognitive load" OR "mental workload" OR
 oversight OR supervis* OR verification OR validation OR review OR rework OR
 "context engineering" OR "prompt engineering" OR coordination OR
 "context switch*")
```

**D — Lifecycle, readiness, and outcomes**

```text
(requirement* OR architect* OR design OR integration OR security OR testing OR QA OR
 "user acceptance" OR UAT OR release OR deploy* OR operation* OR maintenance OR
 readiness OR gate* OR productivity OR "cycle time" OR "lead time" OR throughput OR
 quality OR defect* OR "technical debt" OR stability OR incident*)
```

### 8.2 Search families

Searches will use multiple focused families rather than one excessively broad query.

| ID | Purpose | Canonical Boolean structure |
|---|---|---|
| S1 | Human effort/attention redistribution | A AND B AND C |
| S2 | Lifecycle validation/readiness | A AND B AND D AND (oversight OR verification OR validation OR readiness OR gate*) |
| S3 | Story Points and estimation shift | ("story point*" OR "agile effort estimation" OR "software effort estimation") AND A |
| S4 | Cognitive review burden | A AND ("code review" OR "pull request") AND ("cognitive load" OR workload OR attention OR effort OR verification) |
| S5R | Human review burden | A AND ("code review" OR "pull request") AND (human OR oversight OR workload OR attention OR effort OR verification) |
| S5T | Human testing/QA burden | A AND ("software testing" OR "test generation" OR "unit testing" OR "integration testing" OR "quality assurance") AND (human OR oversight OR verification OR validation OR effort) |
| S5S | Human security-assurance burden | A AND ("software security" OR "secure coding" OR vulnerability OR "security review") AND (human OR oversight OR verification OR validation OR review) |
| S6 | Full-lifecycle/team delivery | A AND (team OR organization* OR enterprise) AND (SDLC OR "software delivery") AND (flow OR capacity OR orchestrat* OR coordination OR readiness) |
| S7 | Exact novelty terms | ("hybrid intelligence effort" OR "LLM-aware effort estimation" OR "verified delivery" OR "delivery attention" OR "human attention demand") |
| S8 | Foundational comparison | ("story point*" OR "agile effort estimation" OR "developer productivity" OR "code review") AND (validity OR accuracy OR cognitive OR workload OR performance) |

S5 is an umbrella assurance family and is operationally complete only when its
three prespecified subfamilies S5R, S5T, and S5S have each been handled. The
required operational set is therefore S1, S2, S3, S4, S5R, S5T, S5S, S6, S7,
and S8. The machine-readable term registry and deterministic expansion control
are `gate2/search_control_template.json` and `gate2/search_control.py`.

## 9. Source translations

The full literal query accepted by the platform, filters, platform, search
fields, date, and hit count must be copied to the Search Log at execution for
each declared source-family pair in Section 7.1.
Symbolic strings such as `A_TERMS`, `B_TERMS`, and `C_TERMS` are prohibited in
an execution log. Canonical families must first be expanded by
`gate2.search_control.render_families`, then translated and syntax-validated in
the target interface or API. The appendix contains tested arXiv pilots and a
limited set of candidate translations. A missing translation for a declared
source-family pair is a pending method-control item. No source-family Cartesian
product is required beyond the approved Section 7.1 matrix.

### 9.1 OpenAlex

Translate each family into documented Works search/filter parameters. Preserve the exact request URL or parameter object, API documentation date, cursor or pagination state, mailto/API-key mode if used, response files, result count reported by the service, and complete-export checksum. Search semantics and rate-limit handling must be validated before freeze.

### 9.2 Semantic Scholar Academic Graph

Translate each family into documented paper bulk-search parameters. Preserve the exact request parameters, requested fields, pagination token/offset, API documentation date, response files, result count when supplied, and complete-export checksum. If API-key limits affect reproducibility, record the limit and retry policy; do not silently truncate.

### 9.3 Crossref REST API

For each candidate or included DOI, preserve the exact verification request,
response metadata, access time, and verification outcome. Batch title/author
lookups used to resolve a missing DOI must be labelled metadata resolution, not
systematic discovery. Crossref is DOI/deposit metadata infrastructure rather
than a disciplinary discovery index; it has no mandatory family translation,
does not contribute PRISMA identification counts, and its non-retrieval cannot
support an absence claim.

### 9.4 Inaccessible-source candidate translations

The following legacy candidate translations are retained only for auditability or future use if lawful access becomes available. They are not part of the approved executable open-source set and must not generate implied search coverage.

#### Scopus

Wrap each fully expanded canonical family in `TITLE-ABS-KEY(...)`, then add
`PUBYEAR > 2018` and `LIMIT-TO(LANGUAGE,"English")` for S1–S7. Run S8 without
the 2019 lower bound when retrieving foundational evidence. Run every required
family separately; do not rely on one combined Scopus query.

#### Web of Science

Wrap each fully expanded canonical family in `TS=(...)`. Apply document types
Article, Proceedings Paper, or Review, English language, and the 2019–search
date window for S1–S7. Apply the foundational time rule to S8. Record the exact
query text displayed by Web of Science after parsing.

#### IEEE Xplore

Translate every term of each expanded family into explicit `"All Metadata"`
clauses. Apply publication-year and content-type filters in the interface and
record them. A partially translated family is `translation_draft`, not an
executable or completed search.

#### ACM Digital Library

Translate every term of each expanded family into explicit Abstract and Title
clauses. If the interface rejects a long query, split it into prespecified,
logged subqueries whose union represents the family; record every accepted
query independently and deduplicate only after export preservation.

#### SpringerLink and ScienceDirect

Use title/abstract/keyword searches where supported. Run every required family,
including S8 and all three S5 subfamilies, separately and record filters.
Because platform search semantics can differ from bibliographic databases,
results from these sources are deduplicated by DOI/title rather than assumed
unique. A publisher interface fallback remains a distinct source and never
inherits the coverage claim of Scopus or Web of Science.

### 9.5 arXiv

Example S3:

```text
all:("story points" OR "software effort estimation")
AND all:("large language model" OR "generative AI" OR "AI-assisted")
```

Search cs.SE, cs.HC, cs.AI, and relevant information-systems categories. Record version number and update date; replace a preprint with its peer-reviewed version when the content is materially equivalent.

### 9.6 Google Scholar supplementary discovery

Use exact phrases and short combinations because long Boolean expressions are unreliable. Examine at most the first 200 results per query, sorted by relevance, plus a date-sorted pass for 2025–2026. Record the query and screening depth, not only the approximate hit count.

## 10. Search validation

Before final execution, the search must retrieve the following sentinel papers where the database indexes them:

1. Alaswad et al., HIE (2026)
2. Alaswad et al., LLM-aware effort framework (2026)
3. Peng et al., Copilot productivity experiment (2023)
4. Becker et al., experienced open-source developer RCT (2025)
5. Mohamed et al., LLM-assistant productivity systematic review (2026)
6. Gonçalves et al., cognitive load and code review (2022)
7. Pasuksmit et al., Story Point changes (2022)
8. Zhong et al., human-centric to agentic code review (2026)
9. Armesto and Kolb, lifecycle field study (2026)
10. Koch and Wellbrock, Agile V (2026)

If a database-specific query misses a sentinel paper known to be indexed there, revise that database translation and document the change before freezing the final search.

For the arXiv developmental translations, AX-S5R must diagnose recall of `2606.26505` and AX-S6R must diagnose recall of `2603.20028`. Match arXiv base identifiers without version suffixes. Passing a sentinel check is necessary but not sufficient: it does not replace complete pagination, eligibility screening, or precision appraisal.

## 11. Eligibility criteria

### 11.1 Inclusion criteria

Include a record in the scholarly primary corpus when all applicable conditions hold:

- **I1:** addresses professional or realistically simulated software engineering/development/delivery;
- **I2:** includes generative AI, an LLM assistant, or an agentic coding system as a material part of the work;
- **I3:** measures, models, or substantively analyzes human effort/attention/oversight, estimation/planning, lifecycle readiness, flow, or quality consequences;
- **I4:** provides an inspectable method, framework definition, dataset, or evidence trail;
- **I5:** full text is available in English;
- **I6:** published in the date window, or intentionally retained as foundational evidence;
- **I7:** is the most complete accessible version of the study.

Secondary reviews are included in a separate secondary-study stratum. Practitioner evidence must satisfy the Stream B requirements and is not placed in the scholarly primary corpus.

### 11.2 Exclusion criteria

- **E1:** AI for a non-software domain with no transferable software-engineering construct;
- **E2:** model benchmark focused only on code-generation accuracy with no human/process/delivery implication;
- **E3:** education-only study with no validated transferable measure or professional relevance;
- **E4:** opinion, marketing page, or news report with no distinct traceable evidence or construct;
- **E5:** abstract/poster/slides only, unless they are the only record of a clearly relevant ongoing study and are labelled “awaiting evidence”;
- **E6:** duplicate or earlier version superseded by a fuller record;
- **E7:** non-English full text without reliable translation;
- **E8:** no transparent method for a claimed empirical result;
- **E9:** focuses only on using an LLM to predict traditional Story Points and offers no evidence about AI changing work or estimation validity; such studies may be retained in a background-only category when useful for comparison;
- **E10:** study concerns building AI/ML products generally but not AI assistance in the software-delivery process.

### 11.3 Borderline rules

- Requirements, architecture, testing, review, security, or operations studies are included if they measure human work or provide lifecycle evidence relevant to VDCM/RSDRI.
- AI-generated-code quality studies without participants may be included when they provide evidence about assurance obligation, evidence readiness, verification demand, rework, or downstream risk; they cannot validate human workload.
- DORA and comparable large industry research enters Stream B unless published as a peer-reviewed study.
- A preprint and journal/conference version are treated as one study family; material differences are documented.

## 12. Screening procedure

### 12.1 Deduplication

Deduplicate in this order:

1. DOI;
2. arXiv identifier/related DOI;
3. normalized title plus first author and year;
4. manual study-family review for preprint/conference/journal variants.

Retain the most complete version and preserve links to related versions.

### 12.2 Screening stages

1. automated and manual deduplication;
2. title/abstract screening;
3. full-text eligibility screening;
4. study-family consolidation;
5. quality appraisal;
6. data extraction;
7. backward/forward citation chasing with the same criteria and stopping rule in Section 7.4;
8. final update search.

### 12.3 Reviewers and disagreements

Because additional human reviewers are unavailable during Gate 2, the review will use a disclosed **agent-assisted evidence-mapping mode**:

1. two independently prompted AI reviewer agents screen each calibration record and each full text against the frozen criteria;
2. each agent records its identifier, model/version when available, prompt/protocol version, decision, reason, confidence, and cited source location;
3. the coordinating agent adjudicates disagreements by checking the source text and records a reasoned final research decision;
4. all inclusions, novelty-threatening exclusions, disputed quality scores, and extracted quantitative claims receive an additional source-grounded audit;
5. the authors retain accountability for the review and must verify every included source, citation, quotation, and outcome-bearing extraction before submission.

This is not described as human double screening. Agreement statistics measure reproducibility between agent review passes, not inter-human reliability. AI agents are methodological aids and cannot be authors, ethics approvers, or publication-accountability substitutes.

### 12.4 Calibration

Before full screening, the two agents screen the same 30–50 records in isolated review passes. Target Cohen's kappa of at least 0.70 after resolving rule ambiguity. Record raw agreement as well. These are diagnostics of agent-pass consistency, not evidence of human-review reliability and not substitutes for source-grounded adjudication.

### 12.5 Exclusion reporting

Every full-text exclusion receives one primary reason from E1–E10. PRISMA counts are generated from the logs only after the final search; no pilot-search count may be presented as a systematic-review result.

## 13. Quality appraisal

Quality is assessed after full-text inclusion. A low score does not automatically remove a relevant paper; it controls evidentiary weight. A record with no inspectable method or unverifiable empirical claims may be excluded under E8.

Each criterion is scored 0 (absent/serious concern), 1 (partial/unclear), or 2 (clear/adequate), with “N/A” only where the form explicitly permits it. Report percentage of applicable points.

### 13.1 Empirical quantitative/mixed-method studies

1. clear research question and contribution;
2. context, participants/tasks, and sampling described;
3. AI tool/model/version and exposure described;
4. constructs and measures operationalized with validity evidence;
5. design addresses bias/confounding and includes an appropriate comparator where needed;
6. analysis matches design, distributions, nesting, and repeated measures;
7. uncertainty/effect sizes and negative/null outcomes reported;
8. data/code/materials or sufficient replication detail available;
9. limitations and validity threats discussed;
10. funding, conflicts, author–framework relationship, and modeled-versus-observed values transparent.

### 13.2 Qualitative studies

1. research purpose and context clear;
2. sampling and participant roles justified;
3. data collection transparent;
4. analytic procedure systematic and traceable;
5. researcher reflexivity/bias addressed;
6. evidence supports themes/claims;
7. triangulation or member/peer checks where appropriate;
8. negative cases and limitations considered;
9. transferability boundaries stated;
10. data/material availability and conflicts disclosed.

### 13.3 Secondary reviews

1. protocol or explicit method;
2. multiple appropriate databases;
3. reproducible full search strings and dates;
4. duplicate screening or stated reliability procedure;
5. clear inclusion/exclusion criteria;
6. study quality/risk appraisal;
7. study overlap/versions handled;
8. extraction and synthesis method appropriate;
9. evidence strength and heterogeneity addressed;
10. artifacts, limitations, and update date reported.

### 13.4 Conceptual/framework papers

1. problem and boundary conditions clear;
2. grounding in relevant prior theory/evidence;
3. constructs are distinct and operationally definable;
4. causal/mechanistic reasoning is explicit;
5. framework is compared with close alternatives;
6. evaluation or falsifiable propositions are provided;
7. implementation cost and failure modes addressed;
8. evidence versus assumption is separated;
9. limitations/generalizability discussed;
10. conflicts, trademark/commercial relationship, and artifacts disclosed.

### 13.5 Grey/practitioner evidence — AACODS-inspired

Score Authority, Accuracy, Coverage, Objectivity, Date, and Significance from 0–2 each. Record sample/method, sponsor/vendor interest, raw-data availability, and whether claims can be traced to primary evidence.

### 13.6 Evidence-weight bands

- **High:** at least 75% of applicable points and no critical flaw;
- **Moderate:** 50–74%;
- **Low/contextual:** below 50%, or important limitations that prevent strong inference.

No mathematical weighting of findings will be presented as certainty. The bands guide narrative language and sensitivity checks.

## 14. Data-extraction model

The evidence matrix records:

### 14.1 Bibliographic and status fields

- record ID and study-family ID;
- title, authors, year, venue;
- DOI/arXiv ID and verified URL;
- publication status and version date;
- evidence stream and study type;
- peer-review status.

### 14.2 Context and method

- country/sector and organizational setting;
- unit of analysis;
- participants, teams, tasks, projects, repositories, or PRs;
- sample size and duration;
- AI tool/model/mode and comparison condition;
- method/design;
- observed versus self-reported versus modeled data;
- availability of data/code/materials.

### 14.3 Lifecycle and construct coverage

- requirements/problem framing;
- context/prompt construction;
- architecture/design;
- implementation/refinement;
- integration;
- human/AI code review;
- security/privacy/compliance;
- unit/integration/system/regression testing;
- release/deployment/operations;
- manual QA and UAT;
- coordination/context switching.

Map each study to the candidate VDCM/RSDRI constructs—pre-commitment demand
drivers (PDD), role-stage human touch demand (RHTD), stage automation enablement
(SAE), evidence readiness state (ERS), available role capacity (ARC), role
capacity pressure (RCP), constrained-role queue delay (CQD), and verified
delivery capacity (VDC). Retain an “emergent construct” field so the proposed
framework cannot force evidence into predetermined categories.

### 14.4 Measures and findings

- baseline estimator or comparator;
- prospective or retrospective estimate;
- human touch time and elapsed time;
- perceived workload instrument;
- prompt/refinement/validation indicators;
- flow and delivery metrics;
- review and quality metrics;
- quality/readiness gates;
- effect direction, effect size/uncertainty, and key finding;
- moderators and boundary conditions;
- limitations and reviewer notes.

### 14.5 Novelty-adjudication fields

- direct overlap with VDCM/RSDRI claim;
- pre-commitment estimation present?;
- multi-role capacity present?;
- full lifecycle through release/UAT present?;
- readiness evidence present?;
- compared against organizational Story Points?;
- out-of-sample prediction/calibration present?;
- organizational or simulated validation present?;
- remaining distinction and novelty risk (low/moderate/high/critical).

## 15. Synthesis and reporting plan

### 15.0 Evidence-map and PRISMA boundary

PRISMA 2020 will be used to report transparent identification, deduplication, screening, retrieval, and inclusion flow. It is a reporting structure, not a certificate of exhaustive coverage. The synthesis is an access-constrained systematic evidence map: it characterizes the records found through the predeclared open sources and other logged methods, but it does not estimate the total universe of relevant research. Counts must remain separated by peer-reviewed scholarly reports, preprints, secondary studies, and practitioner/grey evidence, and report counts must not be conflated with consolidated study-family counts.

### 15.1 Descriptive mapping

Report counts by year, publication status, method, unit of analysis, lifecycle stage, AI mode, role, construct, measure, and evidence-weight band.

### 15.2 Thematic synthesis

Use inductive/deductive coding to identify:

- work shifted away from or toward humans;
- attention/oversight mechanisms;
- bottlenecks and moderators;
- measurement approaches;
- readiness/gate patterns;
- adoption cost and unintended effects;
- evidence gaps.

The deductive VDCM/RSDRI code set is provisional; new categories must be permitted.

### 15.3 Quantitative synthesis

- tabulate effect estimates and uncertainty when available;
- do not pool heterogeneous time-saving percentages from unrelated tasks;
- consider meta-analysis only if at least five sufficiently comparable independent studies use compatible outcomes, interventions, and designs;
- avoid vote counting based only on statistically significant positive/negative findings;
- separate self-reported productivity, observed task time, modeled effort, delivery-system performance, and quality outcomes.

### 15.4 Framework comparison

Construct a comparison matrix across Story Points, HIE/LLM-aware estimation,
SPACE, DORA, Agile V, code-review frameworks, delivery-orchestration studies,
and VDCM/RSDRI. Compare purpose, unit, timing, constructs, lifecycle scope,
outcomes, validation, organizational burden, and individual-measurement risk.

### 15.5 Novelty stop rule

Stop or materially pivot the paper if one study family or coherent framework
line already integrates all five indispensable dimensions below and targets
the same planning use:

1. predictors fixed at the pre-commitment cutoff;
2. multi-role demand across lifecycle stages through acceptance/release;
3. active human touch separated from constrained-role queue delay;
4. explicit role capacity, evidence readiness, and dependency/gate mechanics;
5. a verified-completion or verified-capacity forecast target.

Comparison with Story Points/HIE, simulation, out-of-sample prediction, or
organizational field validation strengthens the overlap assessment but is not a
mechanical substitute for the five indispensable dimensions. Adjudication is at
the study-family/framework-line level and must record a qualitative rationale.
Substantial overlap requires the paper to be framed as replication, integration,
or extension rather than as a first framework.

## 16. Bias and validity controls

- freeze protocol before systematic search counts are used;
- retain null/negative evidence and contradictory productivity studies;
- label peer-reviewed, preprint, and practitioner evidence distinctly;
- record model/tool version and study date because capability changes are a major source of temporal heterogeneity;
- record author/vendor conflicts and separate modeled from observed results;
- avoid deriving the framework only from papers that support the starting thesis;
- include literature showing Story Points retain partial value;
- audit extraction against full text, not abstracts or AI summaries;
- conduct a submission-date update search;
- publish the protocol, evidence matrix, search log, and exclusion reasons when permitted.

### 16.1 Defensible novelty language

The review must not state “no prior research exists,” “all relevant literature was searched,” or any equivalent universal absence/completeness claim. Subject to completion of the frozen workflow, the maximum permitted novelty statement is:

> No substantively duplicative framework was identified within the predeclared open scholarly indexes, repositories, and citation networks searched through the stated cutoff date.

Any such statement must name the cutoff date and remain qualified by the inaccessible subscription sources, open-index coverage differences, English-full-text rule, and lawful-access constraints. If the novelty stop rule in Section 15.5 is triggered, that finding overrides this wording and requires the stated pivot.

## 17. AI-assisted review safeguards

AI agents may format search strings, detect likely duplicates, screen records, suggest codes, extract candidate fields, and independently critique decisions under Section 12.3. The following controls are mandatory:

- no systematic search begins until the authors approve the protocol and executable queries;
- every decision and extraction must be traceable to an inspectable source location;
- no agent may invent a missing full text, sample size, effect, quotation, or bibliographic field;
- disagreements and low-confidence decisions require source-grounded adjudication;
- copyrighted full texts and confidential material must remain within systems approved for that content;
- the authors must verify every source and outcome-bearing claim before submission and retain responsibility for appraisal and synthesis;
- substantive AI use, including agent screening, must be disclosed in the manuscript in accordance with the applicable conference and Springer Nature policies;
- agents cannot be listed as authors and cannot provide ethics, conflict-of-interest, or publication approval.

### 17.1 Executable evidence-governance record

The normative workbook-independent record is the versioned Gate 2 review bundle
defined by `evidence_review/schemas/review_bundle.schema.json`. Cross-record
hard stops and PRISMA reconciliation are implemented by
`evidence_review/workflow.py`; the blank starting point is
`evidence_review/templates/review_bundle.template.json`.

The executable record distinguishes agent screening, coordinating-agent
adjudication, study-family consolidation, agent extraction/verification, and
accountable-author confirmation. A source or outcome-bearing extraction is not
publication-ready merely because two agents agree. Before citation, an
accountable author must open the cited report, check the recorded locator, and
record `confirmed`; a pending or rejected confirmation is a hard stop in final
mode. The author record also affirms whether that exact locator supports the
extracted claim. PRISMA totals are derived from record-level events and cannot
be supplied as hand-entered totals; final mode validates each record's terminal
transition path as well as aggregate conservation. The predeclared executable
open-source/search-family coverage matrix must be complete, and every
inaccessible subscription source must carry the dated access record defined in
Section 7.2. Pilot-only searches cannot
contribute records to the systematic corpus.

## 18. Pilot-search log

The web searches performed on 13 August 2026 were **scoping searches**, not the systematic database execution. They identified sentinel papers and overlap clusters but do not supply PRISMA counts.

| Pilot family | Purpose | Result used |
|---|---|---|
| AI coding + cognitive load + Story Points | Initial duplication scan | Identified HIE, oversight/overload, agentic review, and productivity studies |
| Verification tax + human attention | Terminology collision scan | Found extensive practitioner usage; terms are not novel |
| AI-assisted effort estimation | Direct framework overlap | Confirmed conceptual and empirical HIE papers |
| Full-lifecycle AI delivery | Lifecycle overlap | Found Agile V and modernization field study |
| Readiness gates + verified delivery | Gate-framework overlap | Found academic and practitioner readiness/verification frameworks |
| Review methods | Protocol design | Confirmed PRISMA 2020, PRISMA-P, and Kitchenham guidance |

## 19. Protocol deviations

After approval, every deviation must record:

- date;
- original rule;
- revised rule;
- reason;
- affected records;
- whether the change was made before or after reviewing outcome-bearing results;
- approving author or protocol owner.

### 19.1 Freeze criteria for the Open Evidence Route

The protocol remains `prefreeze_reconciled_awaiting_D03_approval` until all of the following are satisfied:

1. minimum-route amendment 0.1 remains archived as approved, and the protocol
   owner separately approves the final v1.3 freeze package;
2. literal, source-accepted translations exist for every declared
   source-family pair in Section 7.1; Crossref has a tested metadata-verification
   procedure rather than family queries;
3. sentinel, pagination, rate-limit/retry, deduplication, export, and checksum
   controls have passed for each declared discovery pair;
4. the six inaccessible sources have dated, reasoned access records and non-substitution treatment;
5. the two isolated agent prompts, calibration set, adjudication rules, author-confirmation responsibility, and disclosure language are versioned and hashed;
6. peer-reviewed, preprint, secondary-study, and practitioner/grey strata have mutually exclusive record destinations;
7. the evidence-map/PRISMA boundary and prohibited claims are embedded in the manuscript-generation prompt and reporting templates;
8. protocol, query registry, control record, schema, templates, and approval record are archived with immutable checksums.

Protocol approval and search execution are separate events. No pilot count, developmental arXiv export, or query-engineering record enters the systematic corpus unless rerun after freeze under the approved query and logged as eligible.

## 20. Gate 2 recommendation

Use the minimum-route provisional title:

> **Beyond Story Points in AI-Assisted Delivery: An Evidence Map and Simulation Framework for Role-Constrained Human Capacity**

Treat HIE as the closest task-level effort predecessor. Position VDCM/RSDRI as
a design-science resource-and-flow integration whose distinctive target is
pre-commitment role-stage demand, queues, readiness, capacity, and verified
completion. Do not describe the current paper as a prospective multi-team
study; that empirical validation is future Route A work.

## 21. Gate 2 approval checklist

Author/protocol-owner approval is required for:

1. targeted access-constrained open evidence map using the non-Cartesian
   OpenAlex, Semantic Scholar, and arXiv matrix in Section 7.1, Crossref
   metadata verification, and a separate multivocal stream;
2. LRQ1–LRQ6;
3. primary date window and foundational-evidence rule;
4. executable open sources, inaccessible-source limitations, and search families;
5. inclusion/exclusion criteria;
6. disclosed two-agent screening, adjudication, and mandatory author-verification procedure;
7. quality-appraisal instruments and evidence bands;
8. extraction fields and synthesis plan;
9. novelty stop rule;
10. repositioning from “new Story Point replacement” to a design-science
    verified-delivery-capacity integration with developmental simulation and
    future Route A validation.

B05 approved amendment 0.1 on 16 August 2026. All 18 declared source-family
controls and the prefreeze package are now reconciled. This checklist must be
approved again at D03 before any protocol artifact is marked frozen.
