# Verified Delivery Capacity Research

**Beyond Story Points in AI-Assisted Delivery: an open evidence map, design-science framework, and developmental simulation for role-constrained human capacity.**

<p align="center">AI-assisted software engineering · Role-constrained delivery · Evidence readiness · Queue-aware planning</p>

<p align="center">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white">
  <img alt="JSON" src="https://img.shields.io/badge/Data-JSON-292929?logo=json&logoColor=white">
  <img alt="CSV" src="https://img.shields.io/badge/Data-CSV-217346">
  <img alt="YAML" src="https://img.shields.io/badge/Config-YAML-CB171E?logo=yaml&logoColor=white">
  <img alt="pytest" src="https://img.shields.io/badge/Testing-pytest-0A9EDC?logo=pytest&logoColor=white">
  <img alt="SHA-256" src="https://img.shields.io/badge/Integrity-SHA--256-E67E22">
  <img alt="Microsoft Excel" src="https://img.shields.io/badge/Review-Excel-217346?logo=microsoftexcel&logoColor=white">
  <img alt="Microsoft Word" src="https://img.shields.io/badge/Manuscript-Word-2B579A?logo=microsoftword&logoColor=white">
  <img alt="PDF" src="https://img.shields.io/badge/Publication-PDF-B30B00?logo=adobeacrobatreader&logoColor=white">
</p>

<p align="center">
  <a href="#the-research-problem"><strong>Problem</strong></a> ·
  <a href="#research-project-dossier"><strong>Dossier</strong></a> ·
  <a href="#method-overview"><strong>Method</strong></a> ·
  <a href="#key-findings"><strong>Results</strong></a> ·
  <a href="#end-to-end-verified-delivery-workflow"><strong>Workflow</strong></a> ·
  <a href="#key-technologies-and-libraries"><strong>Libraries</strong></a> ·
  <a href="#reproducibility-map"><strong>Reproducibility</strong></a> ·
  <a href="#navigate-the-research"><strong>Artifacts</strong></a>
</p>

This repository develops the **Verified Delivery Capacity Model (VDCM)** and its proposed elicitation artifact, the **Role–Stage Demand and Readiness Instrument (RSDRI)**. The work asks whether pre-commitment role-stage demand, effective capacity, queues, dependencies, and evidence readiness can make cross-functional delivery constraints more visible than a single work-item estimate.

> **Double-blind review notice:** keep this repository private while the THINKAI 2026 submission is under review. Repository metadata, workbooks, declarations, and identified-author material may reveal authorship.

## Author

Shaik Khaja Nayab Rasool.

---

## Research project dossier

### Project identity

**Beyond Story Points in AI-Assisted Delivery**  
*An evidence map and simulation framework for forecasting role-constrained, evidence-ready software delivery.*

| Item | Description |
|---|---|
| Research area | AI-assisted software engineering, Agile estimation, human oversight, quality assurance, delivery flow, and operations research |
| Study type | Open evidence map, design-science artifact, and developmental discrete-event simulation |
| Primary artifact | Verified Delivery Capacity Model (VDCM) with the proposed Role–Stage Demand and Readiness Instrument (RSDRI) |
| Unit of planning | A work item represented as role-by-lifecycle-stage service demand, capacity exposure, dependencies, readiness obligations, and rework risk |
| Forecast target | Verified completion probability and expected evidence-ready items per horizon, with bottleneck and delay decomposition |
| Evidence scope | 791 included study families, 2,343 exact-locator findings, and 769 quantitative findings under the Open Evidence Route |
| Evaluation scope | 11 developmental synthetic scenarios with 24 replications each; no organizational participant data |
| Current conclusion | A falsifiable planning representation with mixed synthetic results; no deployable comparator was uniformly best |
| Publication framing | Framework-development and conditional mechanism-evidence paper; Route A organizational validation remains future work |

### Dossier coverage at a glance

| Research-project requirement | Where it is documented |
|---|---|
| Numbered research design and protocol record | [Research-design index](research/design/README.md) |
| Research questions and positioning | [Scientific manuscript](papers/thinkai-2026/manuscript/manuscript_working_draft.md) and [VDCM study dossier](research/studies/vdcm/README.md) |
| Evidence-map method and results | [Evidence-map workspace](research/studies/vdcm/evidence-map/README.md) and [evidence preservation map](docs/traceability/evidence-preservation-map.md) |
| Framework constructs and boundaries | [Protocol workspace](research/studies/vdcm/protocol/README.md) |
| Simulation mechanisms and comparators | [Simulation workspace](research/studies/vdcm/simulation/README.md) and [developmental results](papers/thinkai-2026/results/README.md) |
| Material claim verification | [Claim-verification ledger](papers/thinkai-2026/manuscript/claim_verification_ledger.md) and [D17 approval](research/studies/vdcm/integrity/releases/D17_ACCOUNTABLE_AUTHOR_CONFIRMATION_2026-08-19.json) |
| End-to-end operating model | [Workflow guide](docs/communications/verified-delivery-capacity/END_TO_END_WORKFLOW.md) and [communication dossier](docs/communications/verified-delivery-capacity/README.md) |
| Technology boundaries | [Key technologies and libraries](#key-technologies-and-libraries) and [interpretation boundary](#interpretation-and-responsible-use-boundary) |
| Reproduction and integrity | [Quick verification](#quick-verification), [reproducibility map](#reproducibility-map), and [repository verifier](scripts/verify_repository.py) |

## End-to-end verified delivery workflow

![Verified Delivery Capacity end-to-end workflow](docs/communications/verified-delivery-capacity/assets/06-end-to-end-verified-delivery-workflow.png)

The diagram is a conceptual communication artifact, not an empirical result. See the [workflow guide](docs/communications/verified-delivery-capacity/END_TO_END_WORKFLOW.md) for definitions, operating steps, and guardrails.

The operating model progresses through three controlled phases:

1. **Frame and forecast:** define the work item, freeze the `t0` information set, profile pre-commitment demand drivers, and forecast active service by role and stage.
2. **Flow and verify:** load effective role capacity, model queues and dependencies, and evaluate whether required evidence is present, current, traceable, and independently checkable.
3. **Commit and learn:** apply explicit gate semantics, forecast verified completion, then compare prediction with outcomes in a later calibration wave without leaking execution data into the original forecast.

## The research problem

AI assistance can shorten some implementation activities without proportionally shortening end-to-end delivery. Requirements clarification, architecture, integration, review, security, testing, release, and acceptance still consume finite specialist capacity. If implementation accelerates faster than those functions, the constraint moves downstream and work accumulates in queues.

VDCM reframes the planning question:

> Can the required roles produce and verify the evidence needed for the planned portfolio by the commitment deadline?

The proposed representation separates active human service from queue delay, dependency blocking, and calendar pauses. It forecasts verified completion against explicit evidence obligations rather than treating code generation or task completion as delivery completion.

## Current scientific status

| Area | Status |
|---|---|
| Research contribution | Prospective multi-role capacity-and-flow representation; not a first human-attention model or universal Story Point replacement |
| Evidence review | Open Evidence Route protocol v1.3 frozen; D05–D17 complete |
| Evidence synthesis | 791 included study families; 2,343 exact-locator findings; 769 quantitative findings |
| Novelty boundary | No family met all five declared overlap dimensions for the same planning use within the bounded search |
| Material claims | CL-001 through CL-010 confirmed by the accountable author on 2026-08-19 |
| Simulation | 11 developmental scenarios × 24 replications; mechanisms and comparators implemented |
| Comparative result | No deployable comparator was uniformly best; simpler models won in several declared worlds |
| Empirical validation | Route A future work requiring genuine practitioners and organizational data |
| Manuscript | Anonymous full-paper release candidate generated and visually inspected; final venue/authorship release gates remain |
| Verification | Integrated tests, artifact checks, and manuscript-boundary checks run through `make verify` |

Developmental search records are not PRISMA inclusions. Synthetic simulation results do not validate human cognition, organizational usefulness, causal AI effects, or return on investment.

## Contributions

1. **A bounded open evidence map** separating peer-reviewed studies, preprints, secondary research, practitioner evidence, and foundational references.
2. **A prospective planning representation** covering pre-commitment demand drivers, role-stage human touch demand, effective capacity, evidence readiness, dependencies, queues, and bounded rework.
3. **A reproducible developmental simulation** comparing Story Points, an HIE-compatible baseline, simple role load, the proposed model, and a diagnostic oracle.
4. **A falsifiable validation agenda** for later shadow-mode, multi-team evaluation with temporal and team/project holdouts.
5. **Explicit failure and simplification rules** for cases where added detail is unstable, burdensome, or no better than a simpler baseline.

## Method overview

VDCM links planning-time evidence, service demand, resource constraints, and delivery outcomes without collapsing them into one score:

```text
work item + risk tier + frozen t0 evidence
        ↓
pre-commitment demand-driver profile
        ↓
role × lifecycle-stage human touch-demand distribution
        + effective role capacity and existing queue
        + dependency graph and calendar availability
        + evidence-readiness state and bounded rework
        ↓
queue-aware delivery simulation / forecast
        ↓
verified completion probability + items per horizon
        + constrained role-stage + touch/wait/block decomposition
        ↓
later outcome reconciliation and Route A recalibration
```

The proposed construct families are:

| Construct | Operational meaning | Explicit exclusion |
|---|---|---|
| Pre-commitment Demand Drivers (PDD) | Intent uncertainty, propagation exposure, context deficit, assurance obligation, and coordination topology known at `t0` | Not realized prompt counts, churn, comments, or failures |
| Role–Stage Human Touch Demand (RHTD) | Forecast P50/P80 active service hours for role `r` at stage `s` | Not psychological workload or individual productivity |
| Available Role Capacity (ARC) | Schedulable role-pool hours after declared allocations, calendars, and blackouts | Not nominal headcount or continuous availability |
| Evidence Readiness State (ERS) | Presence, currency, traceability, and independent checkability of required evidence at a named gate/time | Evidence existence is not evidence correctness |
| Role Capacity Pressure (RCP) | Forecast demand divided by available capacity for each role/horizon | Role ratios are not summed into a universal score |
| Constrained-role Queue Delay (CQD) | Elapsed non-service time awaiting a required role, decision, or evidence | Kept separate from active touch time |
| Verified Delivery Capacity (VDC) | Distribution of evidence-ready items per horizon and per-item completion probability | Not code volume, velocity, or a causal productivity claim |

## Key findings

- The systematic stream began with 5,879 record occurrences and the first citation round with 6,097 candidate occurrences.
- After screening, lawful full-text assessment, appraisal, extraction, bounded citation chasing, and reconciliation, the evidence map contains 791 included study families.
- The evidence base is broad but uneven: implementation/refinement is heavily represented, while manual QA/UAT has substantially less mapped coverage.
- No mapped family satisfied all five novelty dimensions for the same pre-commitment planning use.
- Across 11 developmental synthetic scenarios, the proposed and HIE-compatible models each had the lowest descriptive Brier score in four, simple role load in two, and Story Points in one.
- Mixed results are intentional evidence about boundaries: added structure must earn its elicitation cost.

The maximum defensible novelty statement is:

> No substantively duplicative framework was identified within the predeclared open scholarly indexes, repositories, and citation networks searched through the stated cutoff date and approved resource cap.

This is not an exhaustive-literature claim.

## Repository layout

```text
.
├── research/
│   ├── design/                  # Numbered concept, protocol, framework, and simulation records
│   └── studies/vdcm/            # Study dossier, evidence map, and integrity boundaries
├── papers/thinkai-2026/         # Venue requirements, manuscript, figures, results, release gates
├── docs/
│   ├── communications/          # Platform-neutral narratives and conceptual visuals
│   ├── governance/              # Research and public-release governance
│   ├── repository/              # Repository organization
│   ├── status/                  # Roadmap and controlling completion checklist
│   └── traceability/            # Evidence preservation and relocation records
├── scripts/                      # Repository-level verification
├── gate2/                        # Import-stable open-evidence tooling and systematic artifacts
├── evidence_review/              # Screening, adjudication, appraisal, and extraction controls
├── simulation/                   # DES, comparators, development outputs, and pre-lock controls
├── tests/                        # Integrated regression and hard-stop tests
├── artifacts/
│   ├── workbooks/               # Research workbooks
│   └── reference-images/        # Conference/reference imagery
├── CITATION.cff
└── LICENSE
```

The executable Python packages remain at the root for stable imports. Numbered
research records, study navigation, documentation, communication material,
workbooks, and reference imagery are segregated under their canonical folders.
[Repository layout governance](docs/repository/repository-layout.md) defines the
checksum-preserving migration policy.

## Key technologies and libraries

The repository deliberately separates deterministic research logic from optional retrieval, document, and visualization tooling.

| Layer | Technology or library | Role in this project |
|---|---|---|
| Core runtime | Python 3.9+ standard library | Simulation events, comparators, checksums, schemas, ledgers, deterministic sampling, reconciliation, and most verification logic |
| Configuration | JSON and optional PyYAML | Machine-readable protocols, schemas, simulation worlds, registries, and YAML-compatible configuration loading |
| Testing | `pytest` and `unittest` | Integrated regression, adversarial, hard-stop, determinism, reconciliation, and contract tests |
| Public evidence retrieval | `urllib.request` and `requests` | Bounded calls to declared open scholarly sources and lawful full-text locations |
| PDF safety and extraction | project-local `pypdf`; legacy static extraction through `PyPDF2` | Remove interactive actions, create action-free derivatives, and extract static text without executing document content |
| Analysis and figures | NumPy and Matplotlib | Developmental summaries, uncertainty calculations, and manuscript figures |
| Communication visual | Pillow plus repository-owned SVG generation | Deterministic PNG/SVG rendering of the conceptual VDCM workflow |
| Manuscript generation | `python-docx`, Microsoft Word, and PDF rendering tools | Build, format, render, and visually inspect submission artifacts |
| Human review ledger | Microsoft Excel workbook | Gate/status review, parameter tracking, and accountable human-in-the-loop checkpoints |
| Integrity | SHA-256 via `hashlib` | Bind protocols, source artifacts, outputs, manuscripts, approval records, and communication visuals |

### Technology boundaries

- The simulation engine does not require a model API or production organizational system.
- Public scholarly APIs were used only under the frozen evidence-map protocol; communication and README generation are local-only.
- PDF processing is static and fail-closed: malformed or action-bearing files that cannot be safely sanitized remain excluded.
- Optional libraries support retrieval, rendering, or publication; they do not convert synthetic results into empirical validation.
- Production seed values and real organizational data are not included in this repository.

## Navigate the research

### Scientific study

- [VDCM study dossier](research/studies/vdcm/README.md)
- [Protocol and construct definitions](research/studies/vdcm/protocol/README.md)
- [Evidence-map workspace](research/studies/vdcm/evidence-map/README.md)
- [Simulation workspace](research/studies/vdcm/simulation/README.md)
- [Integrity and release boundary](research/studies/vdcm/integrity/README.md)

### Paper and results

- [THINKAI 2026 submission workspace](papers/thinkai-2026/README.md)
- [Scientific manuscript source](papers/thinkai-2026/manuscript/manuscript_working_draft.md)
- [Claim-verification ledger](papers/thinkai-2026/manuscript/claim_verification_ledger.md)
- [Anonymous-review package](papers/thinkai-2026/manuscript/initial-submission/README.md)
- [Developmental simulation results](papers/thinkai-2026/results/README.md)

### Governance and communication

- [Research governance](docs/governance/research-governance.md)
- [Evidence preservation map](docs/traceability/evidence-preservation-map.md)
- [Research status and release path](docs/traceability/research-status-and-release-path.md)
- [Communication package](docs/communications/verified-delivery-capacity/README.md)
- [Current completion checklist](docs/status/PROJECT_TODO.md)

## Quick verification

Python 3.11 or later is recommended.

```bash
python3 -m simulation.test_runner --quiet
python3 scripts/verify_repository.py
```

Or run the integrated verification target:

```bash
make verify
```

In the complete local archive, this runs all tests and source-body integrity
checks. In the GitHub-ready export, the presence of
`PUBLIC_RELEASE_MANIFEST.json` selects the redistribution-safe test subset and
verifies the release manifest, secrets boundary, GitHub file-size limit, and
manuscript. The excluded source-body checks remain documented in
`PUBLIC_RELEASE_EXCLUSIONS.json`.

Rebuild the conceptual workflow without network or external-system access:

```bash
python3 docs/communications/verified-delivery-capacity/scripts/build_workflow.py
```

## Reproducibility map

| What to reproduce or inspect | Primary artifact |
|---|---|
| Repository structure and safety boundaries | [`scripts/verify_repository.py`](scripts/verify_repository.py) |
| Integrated test suite | [`simulation/test_runner.py`](simulation/test_runner.py) and [`tests/`](tests/) |
| Evidence-map protocol and traceability | [`research/studies/vdcm/evidence-map/`](research/studies/vdcm/evidence-map/) and [`gate2/`](gate2/) |
| Screening and adjudication controls | [`evidence_review/`](evidence_review/) |
| Developmental simulation | [`simulation/`](simulation/) |
| Declared simulation results | [`papers/thinkai-2026/results/`](papers/thinkai-2026/results/) |
| Claim-to-evidence boundary | [`claim_verification_ledger.md`](papers/thinkai-2026/manuscript/claim_verification_ledger.md) |
| Anonymous manuscript and visual QA | [`initial-submission/`](papers/thinkai-2026/manuscript/initial-submission/) |
| Communication workflow and checksum manifest | [`docs/communications/verified-delivery-capacity/`](docs/communications/verified-delivery-capacity/) |

### Reproducibility expectations

- Verification should fail closed when a required file, checksum, frozen count, transition, or claim boundary is inconsistent.
- Developmental outputs remain explicitly separated from locked production evaluation.
- Search, screening, appraisal, extraction, and citation-chasing records retain source IDs, timestamps, locators, decisions, and hashes.
- Frozen artifacts are superseded through versioned records; they are not silently overwritten.
- Negative, null, and comparator-favorable results remain reportable outcomes.
- A successful local test run establishes artifact consistency, not organizational validity.

## Interpretation and responsible-use boundary

- Human touch demand is active work time, not psychological workload or a measure of individual capability.
- Queue delay remains separate from active service.
- Story Points and HIE-compatible estimates remain meaningful comparators, not strawman baselines.
- VDCM must not be used for individual surveillance, ranking, compensation, or automated denial of professional judgment.
- Security, compliance, release, and acceptance decisions remain accountable human responsibilities.
- Route B establishes conditional synthetic mechanism behavior only; Route A is required for organizational validation.

## Reuse, citation, and disclosure

Repository-owned code and data are licensed under the [MIT License](LICENSE) unless a file states otherwise. Referenced publications and retrieved full texts remain subject to their respective rights. Citation metadata are provided in [CITATION.cff](CITATION.cff).

The GitHub-ready export intentionally excludes third-party PDF bodies, bulk
extracted full text, credentials, sealed values, session transcripts, and local
environments. It preserves their reproducibility trail through source metadata,
lawful-location records, hashes, exact locators, and derived evidence. See the
[public release policy](docs/governance/public-release-policy.md).

AI systems assisted with query engineering, record processing, code generation, testing, adversarial audit, visual generation, and drafting. The accountable human author retains responsibility for methods, source verification, claims, authorship, ethics, and submitted content. See the [AI-assistance disclosure](papers/thinkai-2026/declarations/AI_ASSISTANCE_DISCLOSURE.md).

---

## Professor's at-a-glance research review

This section is a decision-oriented synopsis of the research record. It does not replace the protocol, manuscript, evidence ledgers, or result files linked above.

### Research logic in one view

| Element | At-a-glance assessment |
|---|---|
| Observed problem | AI assistance may accelerate implementation while requirements, architecture, review, security, testing, release, and acceptance remain constrained by finite specialist capacity and evidence obligations. A single relative estimate does not show where those constraints or queues occur. |
| Research gap | The bounded open search found adjacent estimation, human-in-the-loop, lifecycle-gate, cost, and delivery-flow approaches, but no study family covered all five predeclared overlap dimensions for the same prospective planning use. This is a bounded novelty result, not proof that no prior framework exists. |
| Central research question | Can a pre-commitment role-by-stage representation of demand, effective capacity, queues, dependencies, and evidence readiness make verified-delivery constraints more inspectable than a single work-item estimate? |
| Artifact proposed | VDCM, supported by RSDRI, represents each work item through demand drivers, role-stage service distributions, capacity exposure, queue and dependency states, evidence obligations, and bounded rework. |
| Analysis performed | A targeted open evidence map, design-science construct development, and a developmental discrete-event simulation with explicit comparators, reproducibility controls, and failure conditions. |
| Main outcome | The framework is coherent and falsifiable enough for prospective evaluation, but the synthetic comparisons are mixed: no deployable comparator was uniformly best and simpler approaches won several scenarios. |
| Present claim level | Conditional mechanism evidence and a field-validation agenda. The project does not yet establish organizational prediction, causal benefit, return on investment, or superiority to Story Points. |
| Practical implication | Use VDCM first as a shadow-mode diagnostic where specialist bottlenecks, assurance gates, or cross-functional queues matter; retain a simpler model where added detail does not improve decisions enough to justify its cost. |

### Research questions and hypothesis status

The current manuscript is organized around four questions:

1. **Evidence:** how accessible scholarly and practitioner evidence characterizes redistribution of human work, review, assurance, coordination, and estimation in AI-assisted delivery.
2. **Artifact:** which pre-commitment constructs and state variables are required to represent role-constrained, evidence-ready delivery without confusing time, capacity, and psychological workload.
3. **Mechanisms:** when role-stage demand, queues, dependencies, readiness, and rework change verified-completion forecasts relative to simpler comparators in declared synthetic conditions.
4. **Boundaries:** when the additional detail adds no material value, becomes unstable, or creates unjustified estimation overhead.

No confirmatory human-subject hypothesis has been tested in this repository. The original candidate hypotheses were refined into seven preregisterable **future empirical propositions**: incremental touch-demand validity, bottleneck and queue validity, completion calibration, readiness-risk association, AI-related work redistribution, role-specific overload validity, and transportability. Their precise comparator and leakage-control rules are recorded in [Gate 3 future empirical propositions](research/design/03_future_empirical_propositions.md). Consequently, “supported” or “rejected” should not yet be assigned to those propositions.

### What was analyzed and what the results mean

| Analysis layer | Evidence produced | Defensible interpretation |
|---|---|---|
| Open evidence map | 5,879 systematic-search occurrences and 6,097 first-round citation candidates were processed into 791 included study families, 2,343 exact-locator findings, and 769 quantitative findings. | The problem has a substantial but uneven adjacent evidence base. Manual QA/UAT and prospective estimation are relatively sparse in the mapped corpus. Frequencies describe coverage, not effect magnitude or direction. |
| Novelty/overlap assessment | Across 3,955 family-by-dimension judgments, no family met all five overlap dimensions for the same planning use. | The combined planning representation appears non-duplicative within the declared open-source search boundary. It is not an exhaustive global novelty claim. |
| Developmental simulation | Eleven synthetic scenarios, 24 replications each, compared Story Points, HIE-compatible forecasting, simple role load, the proposed model, and a non-deployable oracle. | Role constraints, queues, readiness, dependencies, and rework can change forecasts inside the model, but scenario construction and illustrative parameters prevent real-world inference. |
| Comparative behavior | Proposed and HIE-compatible models each had the lowest descriptive Brier score in four scenarios, simple role load in two, and Story Points in one. | There is no general winner. The result supports conditional use and explicit simplification rules, not a universal replacement claim. |
| Mechanism ablation and reproducibility | Queue, readiness, dependency, and multi-role removals were executed; current-code runs and declared artifacts reproduced deterministically. | The mechanisms are executable and auditable. The ablation deltas are not isolated causal effects, and readiness was non-binding in the illustrative ablation worlds. |

For exact counts, appraisal bands, and bounded conclusions, see the [D16 evidence synthesis](gate2/output/systematic/v1.3/20260816/d16_v2/D16_EVIDENCE_SYNTHESIS.md). For scenario-level scores and uncertainty, see the [developmental results](papers/thinkai-2026/results/README.md).

### Outcome and contribution assessment

The research has produced a **testable planning representation**, not a validated organizational instrument. Its strongest current contributions are:

- separating active human service from queue delay, dependency blocking, and calendar time;
- locating demand and capacity at the role-by-lifecycle-stage level rather than hiding them in one scalar;
- making evidence readiness an explicit condition of verified completion;
- comparing against credible simpler baselines and preserving comparator-favorable results;
- defining conditions under which the framework should be simplified or rejected; and
- providing an auditable path from evidence-map records through constructs, simulation, results, and manuscript claims.

The principal scientific value is therefore representational and methodological: VDCM makes a cross-functional capacity hypothesis measurable and falsifiable. The principal practical value is diagnostic: it may reveal *which* role-stage or missing evidence threatens a commitment, rather than only indicating that an item is “large.”

### Where the framework is most and least useful

| More plausible use | Prefer current or simpler practice when |
|---|---|
| Work requires scarce security, architecture, QA, operations, or acceptance capacity. | Team composition, work mix, and assurance obligations are stable and historical throughput already calibrates well. |
| AI acceleration creates uneven arrival rates across lifecycle stages. | A simple role-load ratio predicts completion and bottlenecks just as well. |
| Risk-tier evidence gates determine whether work is genuinely releasable or acceptable. | Evidence readiness is not a binding differentiator for the workflow. |
| Dependencies, queues, handoffs, or calendar availability dominate elapsed time. | Role-stage inputs cannot be rated consistently or maintained at reasonable cost. |
| Leaders need an explainable bottleneck and delay decomposition before commitment. | Forecast conclusions reverse under small, plausible input changes. |

VDCM should complement portfolio, value, and outcome methods; it does not estimate customer value, financial return, or individual performance.

### Suggested integration and use

Adoption should be incremental and reversible:

1. **Choose a narrow pilot.** Select one workflow and risk tier with a known specialist constraint; do not begin with an organization-wide rollout.
2. **Define the decision contract.** Record the planning horizon, terminal definition of verified completion, required evidence, accountable role pools, and gate semantics.
3. **Freeze the information boundary.** Archive predictors available at commitment time (`t0`) so later execution data cannot leak into the forecast.
4. **Run beside current planning.** Retain normal Story Points and add a simple role-load baseline; record VDCM/RSDRI independently without changing commitments.
5. **Integrate minimum operational data.** Use work-item metadata, role-pool calendars, current queues, dependencies, gate/evidence identifiers, and later workflow outcomes. Preserve active service, waiting, blocking, and rework as separate fields.
6. **Evaluate incremental value.** Compare calibration, proper scoring rules, bottleneck identification, decision usefulness, rating reliability, and elicitation burden at the same cutoff.
7. **Scale, simplify, or stop.** Expand only when the added information is stable and decision-relevant; reduce to simple role load or existing practice when it is not.

Potential technical integrations include issue trackers for frozen work-item attributes and dependencies, source-control and CI/CD systems for traceable evidence identifiers, test/security/release systems for gate evidence, and workforce calendars for role-pool availability. These integrations should collect the minimum data required at work-item or role-pool level, preserve access controls and retention rules, and exclude individual surveillance metrics. The repository provides the model and research machinery, not a production connector or automated commitment engine.

### Core assumptions requiring field validation

- Pre-commitment demand drivers can be defined and rated with acceptable inter-rater reliability.
- Active service demand can be estimated or sampled separately from waiting, blocking, and calendar pauses.
- Role pools and lifecycle stages are meaningful enough for the participating organization to map consistently.
- Effective capacity, existing queues, dependencies, and evidence obligations are observable at the chosen planning horizon.
- Evidence states can be defined as present, current, traceable, and independently checkable without equating existence with correctness.
- Declared queue, dependency, gate, and bounded-rework mechanisms approximate the pilot workflow sufficiently for the intended decision.
- Historical Story Points are treated within their team-specific context rather than pooled as universal units.
- The benefit of better forecasts or bottleneck visibility can be compared fairly with measurement and maintenance overhead.
- Calibration may drift as tools, policies, team composition, codebases, and automation maturity change.

### Shortcomings and threats to validity

- **Evidence coverage:** the map is constrained to accessible open indexes, lawful full texts, English-access rules, a stated cutoff, and an approved resource cap; six major subscription sources were unavailable as authenticated systematic-search sources.
- **Review independence:** isolated AI-assisted screening agents and adjudication improve procedural separation but are not equivalent to independent human systematic-review teams and may share model-lineage bias.
- **Construct maturity:** VDCM/RSDRI has not completed expert content validation, inter-rater reliability testing, usability evaluation, or organizational calibration.
- **Parameter provenance:** current simulation inputs are illustrative rather than estimates derived from compatible organizational observations.
- **External and causal validity:** synthetic runs do not establish real productivity, quality, fairness, causal AI effects, or return on investment.
- **Model-world circularity:** a model may perform well in worlds shaped by compatible assumptions; diverse and misspecified scenarios reduce but cannot eliminate this risk.
- **Simplified mechanics:** the minimum simulation excludes or simplifies some real delivery features, including richer routing, parallel service, and organizational heterogeneity.
- **Temporal validity:** fast-changing AI tools, policies, and practices make version reporting, temporal holdouts, drift monitoring, and recalibration necessary.
- **Measurement effects:** added elicitation can create burden, gaming, or Goodhart effects and could distort behavior if used for targets or individual assessment.

### Recommendations based on the present evidence

1. Present VDCM as a **candidate planning aid and research artifact**, not a proven replacement for Story Points.
2. Preserve the mixed result prominently; comparator-favorable and null outcomes are central evidence about the framework's boundary conditions.
3. Begin any organizational use in prospective shadow mode with current practice and a simple role-load comparator retained.
4. Make calibration, bottleneck accuracy, reliability, usefulness, privacy, and elicitation cost explicit adoption criteria.
5. Use distributions and sensitivity analysis instead of collapsing role demands into a universal score or deterministic commitment.
6. Keep accountable humans responsible for security, compliance, release, and acceptance decisions.
7. Reject or simplify the framework if ratings are unreliable, readiness adds no information, small perturbations reverse decisions, or overhead approaches benefit.

### Future research scope and completion criteria

The next scientific phase is Route A organizational validation:

1. conduct expert and practitioner review of construct definitions, behavioral anchors, and risk-scaled evidence gates;
2. assess inter-rater reliability, measurement burden, privacy risk, and usability before prediction claims;
3. preregister a prospective shadow-mode study with a complete `t0` snapshot and identical outcomes, folds, and time windows for all comparators;
4. collect low-burden multi-role touch observations, queue and block timestamps, readiness states, completion, rework, UAT rejection, and prespecified quality outcomes;
5. test the seven future propositions with temporal and leave-team/project-out validation, proper scoring rules, measurement-error audits, and cluster-aware uncertainty;
6. test transportability and calibration drift across team, domain, risk tier, AI mode, tool version, and automation maturity;
7. quantify whether forecast and decision improvements justify elicitation and maintenance cost; and
8. only after predictive and usability validity, evaluate decision impact through a randomized or stepped-wedge rollout where feasible.

Progression from research artifact to operational use should require all of the following: reproducible measurement, acceptable rater agreement, no material leakage, improvement over the strongest simple comparator on prespecified outcomes, stable conclusions under plausible sensitivity tests, acceptable burden and privacy safeguards, and evidence that the resulting information changes decisions constructively. Failure on these criteria is a result and should lead to revision, simplification, or rejection.

### Quick reading path by purpose

| Reader need | Start here |
|---|---|
| Scientific argument, research questions, results, and limitations | [Working manuscript](papers/thinkai-2026/manuscript/manuscript_working_draft.md) |
| Exact framework constructs, outputs, boundaries, and falsification conditions | [Framework specification](research/design/03_framework_specification.md) |
| Evidence-map population, coverage, appraisal, and novelty boundary | [D16 evidence synthesis](gate2/output/systematic/v1.3/20260816/d16_v2/D16_EVIDENCE_SYNTHESIS.md) |
| Scenario-level developmental outcomes | [Developmental results](papers/thinkai-2026/results/README.md) |
| Future empirical hypotheses/propositions and evaluation rules | [Future empirical propositions](research/design/03_future_empirical_propositions.md) |
| Practical pilot workflow and guardrails | [End-to-end workflow](docs/communications/verified-delivery-capacity/END_TO_END_WORKFLOW.md) |
| Current maturity, release state, and remaining work | [Status and roadmap](docs/status/status-and-roadmap.md) |