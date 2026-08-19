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
| Numbered research design and protocol record | [Research-design index](research-design/README.md) |
| Research questions and positioning | [Scientific manuscript](papers/thinkai-2026/manuscript/manuscript_working_draft.md) and [VDCM study dossier](studies/vdcm/README.md) |
| Evidence-map method and results | [Evidence-map workspace](studies/vdcm/evidence-map/README.md) and [evidence preservation map](docs/traceability/evidence-preservation-map.md) |
| Framework constructs and boundaries | [Protocol workspace](studies/vdcm/protocol/README.md) |
| Simulation mechanisms and comparators | [Simulation workspace](studies/vdcm/simulation/README.md) and [developmental results](papers/thinkai-2026/results/README.md) |
| Material claim verification | [Claim-verification ledger](papers/thinkai-2026/manuscript/claim_verification_ledger.md) and [D17 approval](studies/vdcm/integrity/releases/D17_ACCOUNTABLE_AUTHOR_CONFIRMATION_2026-08-19.json) |
| End-to-end operating model | [Workflow guide](communications/verified-delivery-capacity/END_TO_END_WORKFLOW.md) and [communication dossier](communications/verified-delivery-capacity/README.md) |
| Technology boundaries | [Key technologies and libraries](#key-technologies-and-libraries) and [interpretation boundary](#interpretation-and-responsible-use-boundary) |
| Reproduction and integrity | [Quick verification](#quick-verification), [reproducibility map](#reproducibility-map), and [repository verifier](scripts/verify_repository.py) |

## End-to-end verified delivery workflow

![Verified Delivery Capacity end-to-end workflow](communications/verified-delivery-capacity/assets/06-end-to-end-verified-delivery-workflow.png)

The diagram is a conceptual communication artifact, not an empirical result. See the [workflow guide](communications/verified-delivery-capacity/END_TO_END_WORKFLOW.md) for definitions, operating steps, and guardrails.

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
├── studies/vdcm/                 # Study dossier, protocols, evidence map, integrity boundaries
├── papers/thinkai-2026/          # Venue requirements, manuscript, figures, results, release gates
├── communications/               # Platform-neutral narratives and conceptual visuals
├── docs/                         # Governance, status, repository conventions, traceability
├── scripts/                      # Repository-level verification
├── gate2/                        # Import-stable open-evidence tooling and systematic artifacts
├── evidence_review/              # Screening, adjudication, appraisal, and extraction controls
├── simulation/                   # DES, comparators, development outputs, and pre-lock controls
├── tests/                        # Integrated regression and hard-stop tests
├── artifacts/workbooks/          # Workbook inventory and compatibility notes
├── PROJECT_TODO.md               # Controlling completion sequence
├── CITATION.cff
└── LICENSE
```

The root Python packages and numbered protocol files are intentionally retained during the research freeze cycle. Moving them would invalidate paths embedded in manifests, checksums, tests, and preregistration records. [Repository layout governance](docs/repository-layout.md) defines the staged migration policy.

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

- [VDCM study dossier](studies/vdcm/README.md)
- [Protocol and construct definitions](studies/vdcm/protocol/README.md)
- [Evidence-map workspace](studies/vdcm/evidence-map/README.md)
- [Simulation workspace](studies/vdcm/simulation/README.md)
- [Integrity and release boundary](studies/vdcm/integrity/README.md)

### Paper and results

- [THINKAI 2026 submission workspace](papers/thinkai-2026/README.md)
- [Scientific manuscript source](papers/thinkai-2026/manuscript/manuscript_working_draft.md)
- [Claim-verification ledger](papers/thinkai-2026/manuscript/claim_verification_ledger.md)
- [Anonymous-review package](papers/thinkai-2026/manuscript/initial-submission/README.md)
- [Developmental simulation results](papers/thinkai-2026/results/README.md)

### Governance and communication

- [Research governance](docs/research-governance.md)
- [Evidence preservation map](docs/traceability/evidence-preservation-map.md)
- [Research status and release path](docs/traceability/research-status-and-release-path.md)
- [Communication package](communications/verified-delivery-capacity/README.md)
- [Current completion checklist](PROJECT_TODO.md)

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
python3 communications/verified-delivery-capacity/scripts/build_workflow.py
```

## Reproducibility map

| What to reproduce or inspect | Primary artifact |
|---|---|
| Repository structure and safety boundaries | [`scripts/verify_repository.py`](scripts/verify_repository.py) |
| Integrated test suite | [`simulation/test_runner.py`](simulation/test_runner.py) and [`tests/`](tests/) |
| Evidence-map protocol and traceability | [`studies/vdcm/evidence-map/`](studies/vdcm/evidence-map/) and [`gate2/`](gate2/) |
| Screening and adjudication controls | [`evidence_review/`](evidence_review/) |
| Developmental simulation | [`simulation/`](simulation/) |
| Declared simulation results | [`papers/thinkai-2026/results/`](papers/thinkai-2026/results/) |
| Claim-to-evidence boundary | [`claim_verification_ledger.md`](papers/thinkai-2026/manuscript/claim_verification_ledger.md) |
| Anonymous manuscript and visual QA | [`initial-submission/`](papers/thinkai-2026/manuscript/initial-submission/) |
| Communication workflow and checksum manifest | [`communications/verified-delivery-capacity/`](communications/verified-delivery-capacity/) |

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
[public release policy](docs/public-release-policy.md).

AI systems assisted with query engineering, record processing, code generation, testing, adversarial audit, visual generation, and drafting. The accountable human author retains responsibility for methods, source verification, claims, authorship, ethics, and submitted content. See the [AI-assistance disclosure](papers/thinkai-2026/declarations/AI_ASSISTANCE_DISCLOSURE.md).
